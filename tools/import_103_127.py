# -*- coding: utf-8 -*-
"""把《第一百零三至一百二十七课·续编合稿》拆成课页数据。

源件：_in/文稿/三字经·第一百零三至一百二十七课·续编合稿.md（213,772 字节，25 课）
产出：tools/lessons_87_111.json（书内课次 87–111，合稿课次 103–127）

原则：
  1. 正文照原文搬，只做渲染所需的分段与标记（**加粗 → <b>、去掉聊天尾巴）；
  2. 图位一律留空，落成 figure.ph 虚线框，不出图；
  3. 只改三处确定的错字与口径：108 课「羂光」→「韬光」；105 课文末旧口径
     「二阳敷化、一阴归藏」→ 三才「阳启、枢济、阴藏」；109 课起「（完整链条见附录）」
     这个指向书外附录的括号删去（书里没有该附录）。
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_in', '文稿', '三字经·第一百零三至一百二十七课·续编合稿.md')
OUT = os.path.join(ROOT, 'tools', 'lessons_87_111.json')

CN = '〇一二三四五六七八九'
_BOOK_OFFSET = 16  # 书 86 = 合稿 101+102，故合稿 103 → 书 87


def cn_strokes(n):
    if n < 10:
        return CN[n] + '画'
    if n < 20:
        return '十' + (CN[n % 10] if n % 10 else '') + '画'
    return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '') + '画'


def bold(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = s.replace('**', '')
    s = s.replace('`', '')
    return s.strip()


def strip_chat(lines):
    """去掉撰写会话的尾巴与交付提示，这些不是书稿内容。"""
    out = []
    pats = (
        '文稿先行交付', '文稿审阅定稿后', '本课定稿完成', '是否开启下一课', '是否接续下一课',
        '是否直接开启', '本课不出图', '阴阳定位已按你的指正修正', '这个版本可以直接替换原稿',
    )
    for s in lines:
        t = s.strip()
        if not t:
            continue
        if t in ('---', '***', '___'):
            continue
        if any(t.startswith(p) for p in pats):
            continue
        if t.startswith('（完整链条见附录）'):
            continue
        out.append(s)
    return out


def split_sentences(text):
    """按句号、分号外的句读切句，保留句末标点；只用于核心字段的分段。"""
    parts = re.split(r'(?<=。)', text)
    return [p.strip() for p in parts if p.strip()]


def parse_grid(block):
    right = re.search(r'右列：(.+?)\n', block, re.S)
    left = re.search(r'左列：(.+?)\n', block, re.S)
    if not right or not left:
        raise ValueError('田字格解析失败')
    cols = []
    for m in (right, left):
        raw = m.group(1).strip()
        chars = []
        pinyin = ''
        strokes = []
        pm = re.search(r'（(.+?)）', raw)
        if pm:
            pinyin = pm.group(1).strip()
        sm = re.search(r'笔画：(.+?)$', raw)
        if sm:
            strokes = [int(x) for x in re.findall(r'\d+', sm.group(1))]
        body = raw.split('（')[0]
        chars = [c.strip() for c in re.split(r'·|\|', body.replace('*', '')) if c.strip()]
        words = [[p, c, cn_strokes(s)] for p, c, s in zip(pinyin.split(), chars, strokes)]
        if len(words) != 3:
            raise ValueError('田字格列不为三字：%r -> %r' % (body, words))
        cols.append(words)
    return cols


def parse_lesson(no_cn_int, title, block):
    no_short = title.split()[0]          # 第一百零三课
    line = title[len(no_short):].strip()  # 自羲农，至黄帝
    line_plain = line
    secs = {}
    # 按二级标题切段
    cur = None
    for s in block.split('\n'):
        m = re.match(r'^##(?!#)\s*(.+)$', s.strip())
        if m:
            cur = m.group(1).strip()
            secs[cur] = []
            continue
        if s.strip().startswith('# ') or s.strip().startswith('#\t'):
            continue
        if cur is not None:
            secs[cur].append(s)

    grid_key = next(k for k in secs if k.startswith('田字格'))
    core_key = next(k for k in secs if k.startswith('核心字'))
    read_key = next(k for k in secs if k.startswith('少儿共读'))
    card_key = next(k for k in secs if k.startswith('双卡'))
    take_key = next(k for k in secs if k.startswith('成长'))
    tip_key = next(k for k in secs if k.startswith('家长栏'))
    adult_key = next(k for k in secs if k.startswith('成人研学'))

    cols = parse_grid('\n'.join(secs[grid_key]))

    # 核心字小课堂：一条要点 + 一段「对比」引文
    core_lines = strip_chat(secs[core_key])
    lead_text, quote_paras = '', []
    for s in core_lines:
        t = s.strip()
        if t.startswith('- '):
            t = t[2:]
            t = re.sub(r'^<b>.*?</b>：', '', bold(t)) if bold(t).startswith('<b>') else t
            lead_text = bold(t)
        elif t.startswith('> '):
            quote_paras.append(bold(t[2:]))
        elif t:
            quote_paras.append(bold(t))

    # 少儿共读：图位之前是共读段，图位之后是「落到心上理解」
    read_lines, kid_tail, tail_on = [], [], False
    for x in secs[read_key]:
        t = x.strip()
        if not t or '图一' in t or '图二' in t:
            continue
        if t.startswith('落到心上'):
            tail_on = True
            continue
        (kid_tail if tail_on else read_lines).append(bold(t))

    # 双卡对照
    rows = []
    for x in secs[card_key]:
        t = x.strip()
        if not t or t.startswith('|') is False:
            continue
        if re.match(r'\|[\s\-:|]+\|', t):
            continue
        cells = [bold(c.strip()) for c in t.strip('|').split('|')]
        if len(cells) == 2:
            rows.append(cells)

    takes = [bold(x.strip()[2:]) for x in secs[take_key] if x.strip().startswith('- ')]

    tips, practice = [], ''
    for x in secs[tip_key]:
        t = x.strip()
        if not t or t in ('---', '***', '___'):
            continue
        if t.startswith('> '):
            practice = bold(t[2:])
            continue
        m = re.match(r'\d+\.\s*(.+?)[：:](.*)$', t)
        if m:
            label, text = m.group(1).strip(), m.group(2).strip()
            idx = len(tips)
            mark = '一二三四五六七八九'[idx] if idx < 9 else str(idx + 1)
            tips.append(('<b>%s、%s。</b>%s' % (mark, label, bold(text))) if text else '<b>%s、%s。</b>' % (mark, label))
        else:
            tips.append(bold(t))

    # 成人研学五节
    adult_lines = [x.rstrip() for x in secs[adult_key]]
    adult_secs = []
    cur = None
    for x in adult_lines:
        t = x.strip()
        if t.startswith('### '):
            title_txt = re.sub(r'^###\s*[一二三四五]\s*', '', t).strip()
            cur = [t.split()[1], ['@@TITLE@@' + title_txt]]
            adult_secs.append(cur)
            continue
        if cur is None:
            continue
        if not t:
            continue
        if t.startswith('#### '):
            cur[1].append('@@SUB@@' + re.sub(r'^####\s*', '', t).strip())
            continue
        if t.startswith('> '):
            cur[1].append('@@QUOTE@@' + bold(t[2:]))
            continue
        if t.startswith('- '):
            cur[1].append(bold(t[2:]))
            continue
        m = re.match(r'\d+\.\s*', t)
        if m and cur[0] == '五':
            cur[1].append('@@NUM@@' + t)
            continue
        cur[1].append(bold(t))

    # 存疑：从第五节里抽出编号问题
    doubt = []
    if adult_secs and adult_secs[-1][0] == '五':
        for p in adult_secs[-1][1]:
            if p.startswith('@@NUM@@'):
                doubt.append(re.sub(r'@@NUM@@\d+\.\s*', '', p))
        adult_secs = adult_secs[:-1] if not doubt else adult_secs
        if not doubt:
            # 只有「下一课接续」这类转场句，不再作为存疑
            adult_secs = [s for s in adult_secs if s[0] != '五']

    fav = re.sub(r'<.+?>', '', line)[0]
    pinyin_line = '　'.join(' '.join(w[0] for w in col) for col in cols)
    ph_first, ph_second = cols[0][0][1], cols[1][0][1]

    lead_text_sents = split_sentences(lead_text)
    n = no_cn_int - _BOOK_OFFSET
    no_cn_spaced = ' '.join(no_short)
    return dict(
        n=str(n), no_cn=no_cn_spaced, no_short=no_short,
        runhead='%s · %s' % (no_short, re.split('，', line)[0]),
        fav=fav, line=line, line_plain=line_plain,
        pinyin=pinyin_line,
        h2=line, meta=line + ' ｜ 少儿页＋成人页',
        grid_split=[['① 先读右列', cols[0], '② 再读左列', cols[1],
                     '古法竖排：<b>自右而左，自上而下</b>。先读右列「%s」，再读左列「%s」。'
                     % (''.join(w[1] for w in cols[0]), ''.join(w[1] for w in cols[1]))]],
        readnote='', note='', note2='',
        kid=[['lead', lead_text_sents[0]]] + [['p', q] for q in lead_text_sents[1:]] + [['p', q] for q in quote_paras]
            + [['p', q] for q in read_lines]
            + [['ph', '图一 · 待补'], ['ph', '图二 · 待补']]
            + [['p', '落到心上理解']] + [['p', q] for q in kid_tail],
        cards=[(('俗 见' if j == 0 else '正 解'), '其 %s' % '一二三四五六'[i], r[j])
               for i, r in enumerate(rows) for j in (0, 1)],
        takes=takes,
        tips=[('' if i == 0 else '6', t) for i, t in enumerate(tips)] + ([('12', practice)] if practice else []),
        adult=adult_secs,
        doubt=doubt,
    )


CHAT_TAIL = ('文稿审阅定稿后', '文稿先行交付', '本课定稿完成', '是否开启下一课',
             '是否接续下一课', '阴阳定位已按你的指正修正')


def _clean(t):
    t = t.replace('（完整链条见附录）', '')
    # 二十五课都顶着同一句「承接上一课存疑：」，去壳留问，免得翻页像复印
    t = re.sub(r'^承接上一课存疑：', '', t)
    if t.strip() in ('---', '***', '___'):
        return ''
    if any(t.strip().startswith(x) for x in CHAT_TAIL):
        return ''
    return t


def scrub(lessons):
    for d in lessons:
        d['kid'] = [[k, _clean(v)] for k, v in d['kid']]
        d['kid'] = [b for b in d['kid'] if b[1]]
        d['tips'] = [[m, c] for m, c in
                     (('' if i == 0 else m, _clean(t)) for i, (m, t) in enumerate(d['tips'])) if c]
        d['takes'] = [t for t in d['takes'] if _clean(t)]
        d['adult'] = [(n, [x for x in (_clean(p) for p in ps) if x])
                      for n, ps in d['adult'] if n != '五']
        d['doubt'] = [x for x in (_clean(p) for p in d['doubt']) if x]
    return lessons


def main():
    text = open(SRC, encoding='utf-8').read()
    # 去掉段首总说明：从第一个「# 第一百零三课」开始
    starts = [m.start() for m in re.finditer(r'^#\s*第[一二三四五六七八九十百零〇]+课', text, re.M)]
    if len(starts) != 25:
        raise SystemExit('课数不是 25：%d' % len(starts))
    blocks = [text[a:b] for a, b in zip(starts, starts[1:] + [len(text)])]

    lessons = []
    for k, blk in enumerate(blocks):
        first, _, rest = blk.partition('\n')
        title = first.lstrip('# ').strip()
        lessons.append(parse_lesson(103 + k, title, rest))

    fix = {'羂光': '韬光'}
    raw = json.dumps(lessons, ensure_ascii=False, indent=1)
    for a, b in fix.items():
        raw = raw.replace(a, b)
    # 105 课旧口径（二阳一阴）与 104 定稿的三才模型冲突，换成正稿说法
    raw = raw.replace('三皇是“二阳敷化、一阴归藏”', '三皇是「阳启、枢济、阴藏」')
    lessons = scrub(json.loads(raw))
    json.dump({'lessons': lessons}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('OK %d 课 → %s' % (len(lessons), os.path.relpath(OUT, ROOT)))
    for d in lessons:
        print('%s → 书 %s ｜ %s ｜lead %d ｜段落 %d ｜图位 %d ｜卡 %d ｜启示 %d ｜家长 %d ｜成人 %d ｜存疑 %d'
              % (d['no_short'], d['n'], d['line'], len(d['kid'][0][1]),
                 len([x for x in d['kid'] if x[0] == 'p']),
                 len([x for x in d['kid'] if x[0] == 'ph']),
                 len(d['cards']), len(d['takes']), len(d['tips']), len(d['adult']), len(d['doubt'])))


if __name__ == '__main__':
    main()
