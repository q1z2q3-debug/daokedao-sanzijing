# -*- coding: utf-8 -*-
"""第七十一至八十六课：文稿合稿（第七十一至一百零二课）两课合为一课。

正文来自 _in/文稿/三字经·第七十一至一百零二课·文稿合稿.md，经 tools/import_71_102.py
搬成 lessons_71_86.json；本模块只做分段、编号与泄字清理，不再增写句子。
图仍是本册已入库的两张（原图不重出），图注沿用按实旧注。
"""
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAW = json.load(open(os.path.join(_HERE, 'lessons_71_86.json'), encoding='utf-8'))['lessons']

_SUB_KEY = None


def _clean_kid(kid):
    out, seen_label = [], False
    for b in kid:
        if b[0] == 'p':
            t = b[1].strip()
            if not t:
                continue
            if t == '落到心上理解：':
                if seen_label:
                    continue
                seen_label = True
                out.append(('p', '落到心上理解'))
                continue
            out.append(('p', t))
        else:
            out.append(b)
    # 两处「落到心上理解」只留一次标签
    fixed, once = [], False
    for b in out:
        if b[0] == 'p' and b[1] == '落到心上理解':
            if once:
                continue
            once = True
        fixed.append(b)
    return fixed


def _clean_adult(adult):
    out = []
    for num, paras in adult:
        secs, sub_i = [], 0
        for p in paras:
            if p.startswith('@@TITLE@@'):
                t = p.replace('@@TITLE@@', '')
                if num == '五':
                    continue
                if not secs:
                    secs.append('<b class="sec">%s</b>' % t)
                continue
            if p.startswith('@@SUB@@'):
                sub_i += 1
                t = re.sub(r'（\d+）', '（%d）' % sub_i, p.replace('@@SUB@@', ''))
                secs.append('<b>%s</b>' % t)
                continue
            if p.startswith('@@QUOTE@@'):
                secs.append(p.replace('@@QUOTE@@', ''))
                continue
            if p.startswith('@@NUM@@'):
                if num == '五':
                    continue
                secs.append(re.sub(r'^\d+\.\s*', '', p.replace('@@NUM@@', '')))
                continue
            secs.append(p)
        out.append((num, secs))
    return out


def _clean_doubt(doubt):
    out, k = [], 0
    for x in doubt:
        t = x.replace('@@TITLE@@', '').replace('@@NUM@@', '').strip()
        t = re.sub(r'^\d+\.\s*', '', t)
        if not t or t in ('存疑',):
            continue
        k += 1
        out.append('%d. %s' % (k, t))
    return out


def _note(d):
    parts = [x for x in d['note'].split('　') if x.strip()]
    return (parts[0] if parts else '', parts[1] if len(parts) > 1 else '')


LESSONS = []
for d in _RAW:
    LESSONS.append(dict(
        n=d['n'], no_cn=d['no_cn'], no_short=d['no_short'], runhead=d['runhead'],
        fav=d['fav'], line=d['line'], line_plain=d['line_plain'], pinyin_line=d['pinyin'],
        grid_split=d['grid'], readnote='', note=_note(d)[0], note2=_note(d)[1],
        kid=_clean_kid(d['kid']), cards=d['cards'], takeaways=d['takes'],
        tip_title='给 爸 爸 妈 妈 的 一 句 话 · 这 一 课 讲 什 么，慢 慢 说 给 孩 子 听',
        tips=[(('' if i == 0 else '6'), t) for i, t in enumerate(d['tips'])],
        h2=d['h2'], meta=d['meta'], adult=_clean_adult(d['adult']),
        doubt=_clean_doubt(d['doubt']),
    ))
