# -*- coding: utf-8 -*-
"""附录 · 次第链条与经文对照（201 制）。

输出两份：文稿库 md（`三字经文稿/校勘201/附录·次第链条与经文对照.md`）、
站点页（`docs/appendix.html`）。数据取自 patch 后的 201 课正文与 tools/collation.md。
作者旧稿中被删、被并之句，依作者裁定不入附录。
"""
import os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, 'docs')
LIB = os.path.dirname(ROOT)
MD_OUT = os.path.join(LIB, '三字经文稿', '校勘201', '附录·次第链条与经文对照.md')
sys.path.insert(0, HERE)
import build_book as BB
import toc_plan as T

早年 = '一二三四五'


def lessons():
    d = {int(x['n']): x for x in BB.load_lessons()}
    for i in range(1, 6):
        t = open(os.path.join(DOCS, 'lesson%02d.html' % i), encoding='utf-8').read()
        m = re.search(r'<h1>(.*?)</h1>', t, re.S)
        d[i] = {'n': str(i), 'line_plain': re.sub(r'<[^>]+>', '', m.group(1)).strip()}
    return d


# 校勘记录（与 tools/collation.md 同源，此处只取附录所需字段）
补 = [
    (39, '原书 40 后', '寒燠均，霜露改。右高原，左大海'),
    (60, '原书 60 后', '青赤黄，及黑白。此五色，目所识'),
    (61, '原书 60 后', '酸苦甘，及辛咸。此五味，口所含'),
    (62, '原书 60 后', '膻焦香，及腥朽。此五臭，鼻所嗅'),
    (64, '原书 61 后', '曰平上，曰去入。此四声，宜调协'),
    (74, '原书 70 后', '斩齐衰，大小功。至缌麻，五服终'),
    (75, '原书 70 后', '礼乐射，御书数。古六艺，今不具'),
    (76, '原书 70 后', '惟书学，人共遵。既识字，讲说文'),
    (77, '原书 70 后', '有古文，大小篆。隶草继，不可乱'),
    (78, '原书 70 后', '若广学，惧其繁。但略说，能知原'),
    (102, '原书 93 后', '四百载，迁夏社'),
    (128, '原书 118 后', '梁灭之，国乃改'),
    (145, '原书 134 后', '由康雍，历乾嘉。民安富，治绩夸'),
    (146, '原书 134 后', '道咸间，变乱起。始英法，扰都鄙'),
    (147, '原书 134 后', '同光后，宣统弱。传九帝，满清殁'),
    (148, '原书 134 后', '革命兴，废帝制。立宪法，建民国'),
    (151, '原书 137 后', '史虽繁，读有次。史记一，汉书二'),
    (152, '原书 137 后', '后汉三，国志四。兼证经，参通鉴'),
]
改 = [
    (26, '三纲者，君臣义。父子亲，夫妇顺', '底本十二字一课，与全书体例合；旧稿拆作三课，此复其原'),
    (88, '有典谟，有训诰。有誓命，书之奥', '底本言《书》六体，不著篇数；旧稿「诘」为「诰」之讹，且以篇数系之周公'),
    (149, '古今史，全在兹', '底本作「古今史」；清版作「廿一史」，民國本作「历代事」，数随代增，故不系定数'),
]
异文 = [
    ('第十一、十二课', '十七世', '十六世', '正文从通行本'),
    ('第十七课', '弟于长', '悌于长', '正文从通行本'),
    ('第一百一十八课', '子思笔', '乃孔伋', '正文从通行本'),
    ('第二百零一课', '當講求', '当讲究', '正文从通行本'),
    ('第六十二课', '臊（《素问》）', '膻（童蒙本）', '正文从童蒙本'),
]


def 课次(n):
    return '%d' % n


def full(line):
    line = line.strip()
    return line if line.endswith('。') else line + '。'


def main():
    D = lessons()
    segs = []
    for g in T.GROUPS:
        _, title, a, b = g
        segs.append((title, a, b))

    # ---------- md ----------
    md = ['# 附录 · 次第链条与经文对照', '',
          '> 全书 201 课，页码 2–403。次第链条即各课经文之序；经文对照只列与底本（通行增补本）有出入者，其余各课与底本同文。',
          '> 旧稿中被删、被并之句依作者裁定不入本表。', '']
    md += ['## 附录一 · 次第链条全表（201 课）', '']
    for title, a, b in segs:
        md += ['### %s（第 %d–%d 课）' % (title, a, b), '', '| 课 | 经文 |', '|---|---|']
        for n in range(a, b + 1):
            md.append('| %d | %s |' % (n, full(D[n]['line_plain'])))
        md.append('')
    md += ['## 附录二 · 经文对照表', '',
           '### 甲 补入之课（18）', '',
           '本书原缺、底本有者，按位补入，课次随全书重排。', '',
           '| 课 | 原书位 | 经文 |', '|---|---|---|']
    for n, pos, line in 补:
        md.append('| %d | %s | %s |' % (n, pos, line))
    md += ['', '### 乙 改笔复元（3）', '',
           '底本原句与现文对照；旧稿改笔之文不入本表。', '',
           '| 课 | 现文 | 底本 | 说明 |', '|---|---|---|---|']
    for n, base, note in 改:
        md.append('| %d | %s | %s | %s |' % (n, D[n]['line_plain'], base, note))
    md += ['', '### 丙 异文存此不校（5）', '',
           '两本皆通者存此不校，仅于成人页标出。', '',
           '| 处 | 清版 | 通行本 | 处置 |', '|---|---|---|---|']
    for a1, a2, a3, a4 in 异文:
        md.append('| %s | %s | %s | %s |' % (a1, a2, a3, a4))
    md += ['', '### 丁 校读口径', '',
           '- 底本：通行增补本（古诗文网全文、清华大字本、光明日报 2008 修订本三方合校）。',
           '- 对校本：汉典王应麟清版、汉典民國重定本（章太炎一路）。',
           '- 原则：原版有而本书缺者补；作者改笔而失原貌者复；异文可两存者存此不校，只在成人页标出。',
           '- 判定：全书 402 图位、201 课，补 18、改 3；删并之课不入本附录。', '']
    os.makedirs(os.path.dirname(MD_OUT), exist_ok=True)
    open(MD_OUT, 'w', encoding='utf-8').write('\n'.join(md))

    # ---------- html ----------
    seg_html = []
    for title, a, b in segs:
        rows = ''.join('<li><span class="no">%d</span><span class="ln">%s</span></li>' % (n, html.escape(full(D[n]['line_plain']))) for n in range(a, b + 1))
        seg_html.append('<div class="seg"><h3>%s<span class="rg">第 %d–%d 课</span></h3><ul class="chain">%s</ul></div>' % (html.escape(title), a, b, rows))
    补html = ''.join('<div class="card"><div class="ct">第 %d 课<span class="pos">%s</span></div><div class="cl">%s</div></div>' % (n, html.escape(pos), html.escape(l)) for n, pos, l in 补)
    改html = ''.join('<div class="card"><div class="ct">第 %d 课</div><div class="cl">%s</div><div class="note">底本：%s<br>%s</div></div>' % (n, html.escape(D[n]['line_plain']), html.escape(base), html.escape(note)) for n, base, note in 改)
    异html = ''.join('<div class="card"><div class="ct">%s</div><div class="note">清版：%s<br>通行本：%s<br>%s</div></div>' % (html.escape(a1), html.escape(a2), html.escape(a3), html.escape(a4)) for a1, a2, a3, a4 in 异文)

    page = '''<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>三字经·附录 次第链条与经文对照</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23A2503B'/%3E%3Ctext x='32' y='45' font-size='28' text-anchor='middle' fill='%23F8F3E6' font-family='serif'%3E附%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500&display=swap">
<style>
:root{--paper:#F8F3E6;--paper2:#FCF8EF;--ink:#2F2A24;--ink2:#4A443C;--muted:#8A8074;--line:#DFD4BE;--ochre:#A2503B;--cyan:#6F8A86}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:"Noto Serif SC",serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding:48px 22px 72px}
.head{text-align:center;padding-bottom:26px;border-bottom:1px solid var(--line)}
.kicker{font-family:"Noto Sans SC",sans-serif;font-size:11.5px;letter-spacing:.3em;color:var(--muted)}
h1{font-size:30px;font-weight:600;letter-spacing:.1em;margin:16px 0 10px;line-height:1.4}
.sub{font-family:"Noto Sans SC",sans-serif;font-size:12.5px;color:var(--ink2);line-height:1.9}
.sec{margin-top:42px}
.sec h2{font-family:"Noto Sans SC",sans-serif;font-size:12px;letter-spacing:.26em;color:var(--muted);font-weight:400;padding-bottom:10px;border-bottom:1px solid var(--line)}
.lede{font-family:"Noto Sans SC",sans-serif;font-size:13px;color:var(--ink2);line-height:2;margin-top:14px}
.seg{margin-top:26px}
.seg h3{font-size:17px;font-weight:500;letter-spacing:.08em;border-left:3px solid var(--ochre);padding-left:10px}
.seg h3 .rg{font-family:"Noto Sans SC",sans-serif;font-size:11px;color:var(--muted);letter-spacing:.1em;margin-left:10px}
.chain{list-style:none;margin-top:10px}
.chain li{display:grid;grid-template-columns:34px 1fr;gap:10px;align-items:baseline;padding:7px 2px;border-bottom:1px dashed rgba(223,212,190,.7)}
.chain .no{font-family:"Noto Sans SC",sans-serif;font-size:11px;color:var(--muted);letter-spacing:.06em}
.chain .ln{font-size:16px;letter-spacing:.06em;line-height:1.7}
h2 + .lede{margin-top:10px}
.sub2{font-size:15px;font-weight:500;margin-top:24px;letter-spacing:.08em}
.cards{margin-top:10px}
.card{background:var(--paper2);border:1px solid var(--line);padding:14px 16px;margin-top:10px}
.card .ct{font-family:"Noto Sans SC",sans-serif;font-size:11.5px;color:var(--muted);letter-spacing:.12em}
.card .ct .pos{margin-left:10px;color:var(--cyan)}
.card .cl{font-size:17px;letter-spacing:.05em;margin-top:6px;line-height:1.8}
.card .note{font-family:"Noto Sans SC",sans-serif;font-size:12px;color:var(--muted);line-height:1.95;margin-top:6px}
.rules{font-family:"Noto Sans SC",sans-serif;font-size:12.5px;color:var(--ink2);line-height:2.1;margin-top:12px}
.rules li{margin-left:1.1em}
.foot{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);font-family:"Noto Sans SC",sans-serif;font-size:12px;color:var(--muted)}
.foot a{color:var(--ochre);text-decoration:none;border-bottom:1px solid rgba(162,80,59,.35)}
@media(max-width:480px){h1{font-size:24px}.chain li{grid-template-columns:28px 1fr;padding:6px 0}.chain .ln{font-size:15px}.card .cl{font-size:16px}}
</style>
</head>
<body>
<div class="wrap">
<div class="head">
<div class="kicker">润泽说 · 少儿启蒙国学读本《三字经》</div>
<h1>附录 · 次第链条与经文对照</h1>
<div class="sub">全书 201 课，页码 2–403。链即经文之序；对照只列与底本有出入者。<br>旧稿中被删、被并之句，依作者裁定不入本表。</div>
</div>

<div class="sec"><h2>附录一 · 次第链条全表（201 课）</h2>
<div class="lede">各课经文依序连读，即全书次第。</div>
''' + ''.join(seg_html) + '''
</div>

<div class="sec"><h2>附录二 · 经文对照表</h2>
<div class="lede">底本：通行增补本（古诗文网全文、清华大字本、光明日报 2008 修订本三方合校）。对校本：汉典清版、民國重定本。</div>
<div class="sub2">甲 补入之课（18）</div>
<div class="lede">本书原缺、底本有者，按位补入，课次随全书重排。</div>
<div class="cards">''' + 补html + '''</div>
<div class="sub2">乙 改笔复元（3）</div>
<div class="lede">底本原句与现文对照；旧稿改笔之文不入本表。</div>
<div class="cards">''' + 改html + '''</div>
<div class="sub2">丙 异文存此不校（5）</div>
<div class="lede">两本皆通者存此不校，仅于成人页标出。</div>
<div class="cards">''' + 异html + '''</div>
<div class="sub2">丁 校读口径</div>
<ul class="rules">
<li>原版有而本书缺者补；作者改笔而失原貌者复；异文可两存者存此不校。</li>
<li>全书 201 课、402 图位；补 18 课、复 3 处。删并之课不入本附录。</li>
<li>异文释义只入成人页，少儿页不载，免乱正文。</li>
</ul>
</div>

<div class="foot"><a href="index.html">← 返回目录</a></div>
</div>
</body>
</html>
'''
    open(os.path.join(DOCS, 'appendix.html'), 'w', encoding='utf-8').write(page)
    print('ok', len(md), 'md lines; html', len(page))


if __name__ == '__main__':
    main()
