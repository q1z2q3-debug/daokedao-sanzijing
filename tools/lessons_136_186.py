# -*- coding: utf-8 -*-
"""第一百三十六至一百八十六课：接《三字经·第一百五十二至二百零二课·续编合稿》。

合稿一句一课，书内一页一课（书 86＝合稿 101+102，故合稿 152 起＝书 136 起）。
正文来自 tools/lessons_136_186.json（由 tools/import_152_202.py 从 _in/文稿 装配），
本模块只做渲染前的整理：小节标记转成版式标签、家长栏归并、图位标空。
图位一律留空，页上是虚线框，等配图到了再换。
"""
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAW = json.load(open(os.path.join(_HERE, 'lessons_136_186.json'), encoding='utf-8'))['lessons']


def _adult(secs):
    out = []
    for num, paras in secs:
        if num == '五':          # 存疑单列，本段不重复摆一次
            continue
        body, seen_title = [], False
        for p in paras:
            if p.startswith('@@TITLE@@'):
                t = p.replace('@@TITLE@@', '')
                if not seen_title:
                    body.append('<b class="sec">%s</b>' % t)
                    seen_title = True
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


LESSONS = []
for d in _RAW:
    LESSONS.append(dict(
        n=d['n'], no_cn=d['no_cn'], no_short=d['no_short'], runhead=d['runhead'],
        fav=d['fav'], line=d['line'], line_plain=d['line_plain'], pinyin_line=d['pinyin'],
        grid_split=d['grid_split'], readnote=d.get('readnote', ''), note=d.get('note', ''),
        note2=d.get('note2', ''),
        kid=d['kid'], cards=d['cards'], takeaways=d['takes'],
        tip_title='给 爸 爸 妈 妈 的 一 句 话 · 这 一 课 讲 什 么，慢 慢 说 给 孩 子 听',
        tips=d['tips'],
        h2=d['h2'], meta=d['meta'], adult=_adult(d['adult']), doubt=d['doubt'],
    ))
