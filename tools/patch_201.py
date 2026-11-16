# -*- coding: utf-8 -*-
"""201 课重排：删 3 课、并入 2 课、替 3 课、补 18 课，课次整体重编。

由 build_book.load_lessons() 在成课收集之后调用：
    out = patch_201.apply(out)
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'tools', 'lessons_patch_201.json')
DROP = {27, 28, 135}          # 27/28 并入 26；135 由清段四行取代（内容并入 134 后四课）
W = {26: 26, 80: 80, 136: 136}  # 原文改笔复正，课次不动

CN = '〇一二三四五六七八九'
def cn_num(n):
    if n < 10: return CN[n]
    if n < 20: return '十' + (CN[n % 10] if n % 10 else '')
    if n < 100: return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')
    h, r = divmod(n, 100)
    head = CN[h] + '百'
    if not r: return head
    if r < 10: return head + '零' + CN[r]
    if r < 20: return head + '一' + cn_num(r)
    return head + cn_num(r)


def _adult(secs):
    """小节标记转版式标签（与 lessons_136_186 同制）。"""
    out = []
    for num, paras in secs:
        if num == '五':
            continue
        body, seen = [], False
        for p in paras:
            if p.startswith('@@TITLE@@'):
                t = p.replace('@@TITLE@@', '')
                if not seen:
                    body.append('<b class="sec">%s</b>' % t)
                    seen = True
                continue
            if p.startswith('@@SUB@@'):
                body.append('<b>%s</b>' % p.replace('@@SUB@@', ''))
                continue
            if p.startswith('@@QUOTE@@'):
                body.append(p.replace('@@QUOTE@@', ''))
                continue
            body.append(p)
        out.append((num, body))
    return out


FIGS = json.load(open(os.path.join(ROOT, 'tools', 'figs_patch.json'), encoding='utf-8'))


def _figs(d):
    """改写课沿用原有配图：把 ph 占位换成 fig 块（图随原课走）。"""
    fixed = FIGS.get(str(d['anchor']))
    if not fixed:
        return d['kid']
    ph = [b for b in d['kid'] if b[0] == 'ph']
    if not ph:
        return d['kid']
    out = []
    for b in d['kid']:
        if b[0] == 'ph' and fixed:
            f = fixed.pop(0)
            out.append(('fig', f[0], f[1], f[2]))
        else:
            out.append(b)
    return out


def _wrap(d):
    return dict(
        n=d.get('n', '0'), no_cn=d.get('no_cn', ''), no_short=d.get('no_short', ''), runhead=d.get('runhead', ''),
        fav=d['fav'], line=d['line'], line_plain=d['line_plain'], pinyin_line=d['pinyin'],
        grid_split=d['grid_split'], readnote=d.get('readnote', ''), note=d.get('note', ''),
        note2=d.get('note2', ''),
        kid=_figs(d), cards=d['cards'], takeaways=d['takes'],
        tip_title='给 爸 爸 妈 妈 的 一 句 话 · 这 一 课 讲 什 么，慢 慢 说 给 孩 子 听',
        tips=d['tips'],
        h2=d['h2'], meta=d['meta'], adult=_adult(d['adult']), doubt=d['doubt'],
        anchor=d['anchor'], mode=d['mode'],
    )


def load():
    return [_wrap(d) for d in json.load(open(DATA, encoding='utf-8'))['lessons']]


def apply(out):
    data = load()
    ins, repl = {}, {}
    for d in data:
        if d['mode'] == 'insert':
            ins.setdefault(d['anchor'], []).append(d)
        else:
            repl[d['anchor']] = d
    new = []
    for d in sorted(out, key=lambda x: int(x['n'])):
        n = int(d['n'])
        if n in repl:
            new.append(repl[n])
        elif n in DROP:
            pass
        else:
            new.append(d)
        new.extend(ins.get(n, []))
    # 第 1–5 课为合览原页，不在内容模块内，故模块课次自 6 起编
    for i, d in enumerate(new, 6):
        cn = cn_num(i)
        d['n'] = str(i)
        d['no_short'] = '第%s课' % cn
        d['no_cn'] = ' '.join('第%s课' % cn)
        d['runhead'] = '%s · %s' % (d['no_short'], re.split('，', d['line'])[0])
    return new


def mapping():
    """旧课次 → 新课次（被删者无值），供 toc、prompt、本地库换算。"""
    data = load()
    ins = {}
    for d in data:
        if d['mode'] == 'insert':
            ins.setdefault(d['anchor'], []).append(d['line'])
    m, cur = {}, 0
    for n in range(1, 187):
        if n in DROP:
            m[n] = None
        else:
            cur += 1
            m[n] = cur
        cur += len(ins.get(n, []))
    return m


if __name__ == '__main__':
    m = mapping()
    for n in (26, 40, 60, 80, 93, 118, 134, 136, 137, 186):
        print(n, '→', m[n])
    print('总课数', max(x for x in m.values() if x))
