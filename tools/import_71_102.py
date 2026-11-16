# -*- coding: utf-8 -*-
"""把《第七十一至一百零二课·文稿合稿》导成十六课：相邻两课合为四句一课。

只搬运、不另写：田字格、核心字小课堂、少儿共读、落到心上、双卡、启示、家长栏、
成人五节都按原文成段搬入；图位用本册已入库的两张图（原图不重出），图注沿用按实的旧注。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_in', '文稿', '三字经·第七十一至一百零二课·文稿合稿.md')
OUT = os.path.join(ROOT, 'tools', 'lessons_71_86.json')

CN = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
DIG = dict(zip('〇一二三四五六七八九', range(10)))


def cn2n(text):
    if text.startswith('一百'):
        rest = text[2:]
        if not rest:
            return 100
        if rest.startswith('零'):
            return 100 + DIG[rest[1]]
        return 100 + cn2n(rest)
    if '十' in text:
        a, _, b = text.partition('十')
        return (DIG[a] if a else 1) * 10 + (DIG[b] if b else 0)
    return DIG[text]


def n2cn(n):
    if n < 10:
        return CN[n]
    if n < 20:
        return '十' + (CN[n % 10] if n % 10 else '')
    return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')


def flat(x):
    return re.sub(r'\*\*(.+?)\*\*', r'\1', x.strip())


def split_sections(block):
    secs, cur, body = {}, None, []
    for line in block.split('\n'):
        m = re.match(r'## ([^\n]+)', line)
        if m:
            if cur:
                secs[cur] = body
            cur, body = m.group(1).strip(), []
            continue
        m2 = re.match(r'### ([一二三四五])[ 　]*([^\n]*)', line)
        if m2 and cur:
            body.append('@@SEC@@%s|%s' % (m2.group(1), m2.group(2).strip()))
            continue
        if cur:
            body.append(line)
    if cur:
        secs[cur] = body
    return secs


def take_paras(lines):
    out = []
    for ln in lines:
        t = ln.strip()
        if not t or t.startswith('（图') or t.startswith('---') or t.startswith('@@') or t.startswith('## '):
            continue
        out.append(flat(t))
    return out


def parse_lesson(block):
    lines = block.split('\n')
    title = flat(lines[0]).lstrip('# ').strip()
    m = re.match(r'第?([一二三四五六七八九十百零]+)课[ 　]*([^\n]+)', title)
    no, line = cn2n(m.group(1)), flat(m.group(2))
    secs = split_sections(block)

    grid = {}
    for ln in secs.get('田字格（古法竖排，自右向左，先下右列，先右后左）', []):
        t = ln.strip()
        if t.startswith('右列') or t.startswith('左列'):
            head = t.split('｜')[0]
            chars = re.findall(r'[\u4e00-\u9fa5]', re.sub(r'（.+?）', '', head).replace('右列', '').replace('左列', ''))
            py = re.search(r'（([^）]+)）', t).group(1)
            st = re.search(r'笔画：([\d、]+)', t).group(1).split('、')
            grid['r' if t.startswith('右列') else 'l'] = [
                (p.strip(), c, int(s)) for p, c, s in zip(py.split(), chars, st)]

    cls = []
    for l in secs.get('核心字小课堂', []):
        t = flat(l)
        if t.startswith('- '):
            cls.append(re.sub(r'^[^：]+：', '', re.sub(r'^-\s*', '', t)).strip())

    kid_lines = secs.get('少儿共读', [])
    cut = next((i for i, ln in enumerate(kid_lines) if ln.strip().startswith('落到心上理解')), None)
    kid = take_paras(kid_lines[:cut] if cut is not None else kid_lines)
    mind = take_paras(kid_lines[cut:] if cut is not None else [])
    if mind:
        mind[0] = mind[0].replace('落到心上理解：', '', 1)

    rows = []
    for ln in secs.get('双卡对照', []):
        t = ln.strip()
        if t.startswith('|') and not re.match(r'\|[-: |]+\|', t):
            rows.append([flat(x) for x in t.strip('|').split('|')])

    takes = [flat(re.sub(r'^-\s*', '', l)) for l in secs.get('成长小启示', []) if flat(l).startswith('- ')]

    tips, carry = [], ''
    for ln in secs.get('家长栏：通俗引导', []):
        t = flat(ln)
        if re.match(r'\d+\.', t):
            tips.append(re.sub(r'^\d+\.\s*', '', t))
        elif t.startswith('>') and '选择力' in t:
            carry = t.lstrip('> ').strip()

    adult_key = next((k for k in secs if k.startswith('成人研学')), None)
    adult, cur = {}, None
    for ln in (secs.get(adult_key) or []) if adult_key else []:
        t = ln.strip()
        m2 = re.match(r'@@SEC@@([一二三四五])[|](.*)', t)
        if m2:
            cur = m2.group(1)
            adult[cur] = ['@@TITLE@@' + flat(m2.group(2).strip())]
            continue
        if cur is None or not t:
            continue
        if t.startswith('####'):
            adult[cur].append('@@SUB@@' + flat(t.lstrip('# ')))
        elif t.startswith('>'):
            adult[cur].append('@@QUOTE@@' + flat(t.lstrip('> ')))
        elif re.match(r'\d+\.', t):
            adult[cur].append('@@NUM@@' + flat(t))
        elif t.startswith('- '):
            adult[cur].append('· ' + flat(re.sub(r'^-\s*', '', t)))
        elif t.startswith('---'):
            continue
        else:
            adult[cur].append(flat(t))

    return dict(no=no, line=line, grid=grid, cls=cls, kid=kid, mind=mind,
                rows=rows, takes=takes, tips=tips, carry=carry, adult=adult)


def merge(a, b, imgs):
    line = a['line'] + '。' + b['line'] + '。'
    groups = [''.join(w[0] + ' ' for w in side).strip()
              for side in (a['grid']['r'], a['grid']['l'], b['grid']['r'], b['grid']['l'])]
    pinyin = '　'.join(groups)
    RN_A = ('古法竖排：<b>自右而左，自上而下</b>。上段先读右列「%s」，再读左列「%s」。'
            % (''.join(w[1] for w in a['grid']['r']), ''.join(w[1] for w in a['grid']['l'])))
    RN_B = ('下段续读：先读右列「%s」，再读左列「%s」。'
            % (''.join(w[1] for w in b['grid']['r']), ''.join(w[1] for w in b['grid']['l'])))
    cells = lambda side: [(w[0], w[1], '%s画' % n2cn(w[2])) for w in side]
    grid = [
        ('① 先读右列', cells(a['grid']['r']), '② 再读左列', cells(a['grid']['l']), RN_A),
        ('③ 续读右列', cells(b['grid']['r']), '④ 再读左列', cells(b['grid']['l']), RN_B),
    ]

    def tip_text(items, base):
        out = []
        for i, t in enumerate(items):
            label, _, rest = t.partition('：')
            out.append('<b>%s、%s。</b>%s' % (CN[(base + i) % 10], label, rest))
        return out

    kid = [('lead', a['kid'][0])] + [('p', x) for x in a['kid'][1:]]
    kid.append(('fig', imgs[0][0], imgs[0][1], imgs[0][2]))
    kid += [('p', x) for x in b['kid']]
    kid.append(('fig', imgs[1][0], imgs[1][1], imgs[1][2]))
    if a['mind']:
        kid.append(('p', '落到心上理解：' + a['mind'][0]))
        kid += [('p', x) for x in a['mind'][1:]]
    kid += [('p', x) for x in b['mind']]

    cards = []
    for rows, tag in ((a['rows'], '上 段'), (b['rows'], '下 段')):
        if rows and len(rows[0]) >= 2:
            cards.append(('俗 见', tag + ' · 常 见 的 读 法', rows[0][0]))
            cards.append(('正 解', tag + ' · 这 一 课 的 读 法', rows[0][1]))

    tips_all = tip_text(a['tips'], 1) + tip_text(b['tips'], 5)
    if a['carry']:
        tips_all.append(a['carry'])

    adult = [(k, a['adult'].get(k, []) + b['adult'].get(k, [])) for k in '一二三四五']
    doubt = [x.replace('@@NUM@@', '') for x in a['adult'].get('五', []) + b['adult'].get('五', [])]

    return dict(line=line, pinyin=pinyin, grid=grid, kid=kid, cards=cards,
                takes=a['takes'] + b['takes'], tips=tips_all, adult=adult, doubt=doubt,
                note='　'.join(a['cls'] + b['cls']), note2='',
                no=a['no'])


def main():
    text = open(SRC, encoding='utf-8').read()
    blocks = re.split(r'\n# 第', text)[1:]
    halves = [parse_lesson('# 第' + b) for b in blocks]
    assert [h['no'] for h in halves] == list(range(71, 103)), [h['no'] for h in halves]

    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    old = {}
    for mod in ('lessons_71_74', 'lessons_75_78', 'lessons_79_82', 'lessons_83_86'):
        for d in __import__(mod).LESSONS:
            figs = [b for b in d['kid'] if b[0] == 'fig']
            old[int(d['n'])] = [(f[1], f[2], f[3]) for f in figs]

    out = []
    for i in range(16):
        n = 71 + i
        m = merge(halves[2 * i], halves[2 * i + 1], old[n])
        m.update(n=str(n), no_cn='第 %s 课' % ' '.join(n2cn(n)),
                 no_short='第%s课' % n2cn(n),
                 runhead='第%s课 · %s' % (n2cn(n), halves[2 * i]['line'].split('，')[0]),
                 fav=halves[2 * i]['line'][0],
                 line_plain=m['line'].rstrip('。'), h2=m['line'].rstrip('。'),
                 meta='%s ｜ 少儿页＋成人页' % m['line'].rstrip('。'))
        out.append(m)

    json.dump(dict(lessons=out), open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
    for m in out:
        print(m['n'], len(m['kid']), 'blocks｜', len(m['takes']), '启示｜', len(m['tips']), '家长｜',
              len(m['adult'][0][1]), '成人段｜', len(m['doubt']), '存疑')


if __name__ == '__main__':
    main()
