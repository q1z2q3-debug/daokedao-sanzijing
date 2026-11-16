# -*- coding: utf-8 -*-
"""按 201 课重排 docs/index.html 的课次列表：保留原有手写提要，改课号与链接，
在插入点补入新补编课的条目，删去 27/28/135 三条。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_201 as P2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'docs', 'index.html')
CN = '〇一二三四五六七八九'
cn = P2.cn_num

data = json.load(open(os.path.join(ROOT, 'tools', 'lessons_patch_201.json'), encoding='utf-8'))['lessons']
ins = {}
for d in data:
    if d['mode'] == 'insert':
        ins.setdefault(d['anchor'], []).append(d)
m = P2.mapping()
html = open(IDX, encoding='utf-8').read()

ul = re.search(r'(<ul class="lessons">)(.*?)(\n    </ul>)', html, re.S)
items = re.findall(r'\n      <li class="lesson">.*?\n      </li>', ul.group(2), re.S)
assert len(items) == 186, len(items)

def new_item(d, no):
    chars = [w[1] for blk in d['grid_split'] for col in (blk[1], blk[3]) for w in col]
    core = ' · '.join(chars)
    return ('\n      <li class="lesson">\n'
            '        <div class="no">%s</div>\n'
            '        <div>\n'
            '          <div class="line">%s。</div>\n'
            '          <div class="meta">核心字：%s　｜　图位待补（prompt 已拟）　｜　成人页：字义与句读、命题考辨、跨典互参</div>\n'
            '        </div>\n'
            '        <a class="st" href="lesson%02d.html">读 单 课</a>\n'
            '      </li>' % (' '.join(list('第%s课' % cn(no))), d['line'].rstrip('。'), core, no))

out = []
seq = 0
for i, it in enumerate(items, 1):
    n = m[i]
    if n is None:
        continue
    seq = n
    it = re.sub(r'<div class="no">[^<]*</div>', '<div class="no">%s</div>' % ' '.join(list('第%s课' % cn(n))), it)
    it = re.sub(r'href="lesson[0-9]*\.html"', 'href="lesson%02d.html"' % n, it)
    out.append(it)
    for d in ins.get(i, []):
        seq += 1
        out.append(new_item(d, seq))
assert seq == 201, seq

html = html[:ul.start(2)] + ''.join(out) + html[ul.end(2):]
html = html.replace('共 186 课', '共 201 课')
html = html.replace('第 1–70 课 · 70 课', '第 1–78 课 · 78 课')
html = html.replace('第 71–139 课 · 69 课', '第 79–154 课 · 76 课')
html = html.replace('第 140–186 课 · 47 课', '第 155–201 课 · 47 课')
html = html.replace('人之初，性本善 → 此十义，人所同', '人之初，性本善 → 若广学，惧其繁')
html = html.replace('凡训蒙，须讲究 → 通古今，若亲目', '凡训蒙，须讲究 → 后汉三，国志四')
html = html.replace('口而诵，心而惟 → 戒之哉，宜勉力', '口而诵，心而惟 → 戒之哉，宜勉力')
html = re.sub(r'v3\.1', 'v3.2', html)
open(IDX, 'w', encoding='utf-8').write(html)
print('index 条目', len(out), '末课', seq)
