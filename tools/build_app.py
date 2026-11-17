# -*- coding: utf-8 -*-
"""把《三字经》201 制合览做成安卓阅读应用的资源（app/assets/app.html）。

源页：docs/book.html（402 页、201 课，含三类读法页与目录页）。
产物：单文件 app.html —— 课页原样保留（含田字格与水墨图），图缩到 900px WebP 内嵌，
外加应用层：目录抽屉、全文检索、上一课／下一课、字号（交给 WebView textZoom）、
夜读、收藏、进度记忆、附录。
"""
import base64, io, json, os, re, sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, 'docs')
OUTDIR = os.path.join(ROOT, 'app', 'assets')
sys.path.insert(0, HERE)
import toc_plan as T

三类切分 = [(0, 3, '立人', '何以为人'), (4, 10, '知世', '何以知世'), (11, 11, '劝学', '如何成人')]


def load_book():
    s = open(os.path.join(DOCS, 'book.html'), encoding='utf-8').read()
    css = re.search(r'<style>([\s\S]*?)</style>', s).group(1)
    pages = re.findall(r'<div class="page(?: [^"]*)?" id="(k\d+|toc|guide)">[\s\S]*?\n</div>\n?(?=<div class="page|<div class="foot)', s)
    return s, css, pages


def page_of(s, key):
    """取 id=key 的整页（以顶层 <div class="page" ... id="key"> 起，到下一个顶层 page 止）。"""
    m = re.search(r'<div class="page(?: [^"]*)?" id="%s">' % key, s)
    if not m:
        return ''
    nxt = re.search(r'\n<div class="page(?: [^"]*)?" id="', s[m.end():])
    end = m.end() + (nxt.start() if nxt else len(s))
    return s[m.start():end]


def toc_meta(s, pages_html):
    meta = []
    for g in T.GROUPS:
        for n in range(g[2], g[3] + 1):
            meta.append({'n': n, 'seg': g[1]})
    return meta


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    s, css, _ = load_book()

    # ---- 图片：assets/p*.jpg → 900px WebP data URI（同一图复用缓存）
    cache = {}

    def repl(m):
        f = m.group(1)
        if f in cache:
            return 'src="%s"' % cache[f]
        p = os.path.join(DOCS, f)
        im = Image.open(p).convert('RGB')
        if im.width > 900:
            im = im.resize((900, int(im.height * 900 / im.width)), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, 'WEBP', quality=67, method=6)
        cache[f] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
        return 'src="%s"' % cache[f]

    lessons = []
    for n in range(1, 202):
        pg = page_of(s, 'k%d' % n)
        if not pg:
            raise SystemExit('缺页 k%d' % n)
        pg = re.sub(r'src="(assets/p[0-9a-f]+\.jpg)"', repl, pg)
        no = re.search(r'<div class="lesson-no">([^<]*)</div>', pg)
        h1 = re.search(r'<h1>([^<]*)</h1>', pg)
        lessons.append({'n': n, 'no': no.group(1).strip() if no else '', 'h1': h1.group(1).strip() if h1 else '', 'html': pg})

    guide = page_of(s, 'guide')

    meta = []
    for g in T.GROUPS:
        for n in range(g[2], g[3] + 1):
            meta.append((n, g[1]))
    类 = {}
    for a, b, nm, key in 三类切分:
        for g in T.GROUPS[a:b + 1]:
            for n in range(g[2], g[3] + 1):
                类[n] = nm

    toc = [[l['n'], l['no'], l['h1'], 类[l['n']], dict(meta)[l['n']]] for l in lessons]
    # 分段（三类 + 十二段）用于抽屉分组
    segs = []
    for a, b, nm, key in 三类切分:
        segs.append({'name': nm, 'key': key, 'a': T.GROUPS[a][2], 'b': T.GROUPS[b][3],
                     'sub': [{'name': g[1], 'a': g[2], 'b': g[3]} for g in T.GROUPS[a:b + 1]]})

    appendix = build_appendix_page()

    app_css = open(os.path.join(HERE, 'app_shell.css'), encoding='utf-8').read()
    app_js = open(os.path.join(HERE, 'app_shell.js'), encoding='utf-8').read()

    body = ('<div class="book-wrap" id="bookWrap">' + ''.join(l['html'] for l in lessons) + guide + appendix + '</div>')

    html = '''<!DOCTYPE html>
<html lang="zh-Hans" class="theme-paper">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>三字经·润泽说</title>
<style>%s</style>
<style>%s</style>
</head>
<body>
<header id="bar">
  <button id="btnToc" aria-label="目录"><span class="ic">☰</span></button>
  <div id="now"><b id="nowNo">第一课</b><span id="nowTi">人之初，性本善</span></div>
  <button id="btnFav" aria-label="收藏"><span class="ic" id="favIc">☆</span></button>
</header>

<main id="stage">%s</main>

<nav id="bar2">
  <button id="prev">‹ 上一课</button>
  <div id="pgn"><span id="pgnNum">1</span><span class="sl">/ 201</span></div>
  <button id="next">下一课 ›</button>
</nav>

<div id="tools">
  <button data-act="smaller">A−</button>
  <button data-act="bigger">A+</button>
  <button data-act="night">夜读</button>
  <button data-act="search">检索</button>
  <button data-act="top">回顶</button>
</div>

<div id="drawer" class="sheet">
  <div class="sh-head"><b>目录</b><span class="hint" id="progHint"></span><button class="close" data-close="drawer">×</button></div>
  <div class="sh-tabs"><button class="on" data-tab="all">全部</button><button data-tab="read">已读</button><button data-tab="fav">收藏</button></div>
  <div class="sh-body" id="tocBody"></div>
</div>

<div id="search" class="sheet">
  <div class="sh-head"><b>检索</b><button class="close" data-close="search">×</button></div>
  <div class="sh-body">
    <input id="q" type="search" placeholder="搜原文、字词、人名、典名　如：中庸／断机杼" autocomplete="off">
    <div id="res" class="res"></div>
  </div>
</div>

<div id="mask"></div>
<script>var TOC=%s; var SEGS=%s;</script>
<script>%s</script>
</body>
</html>
''' % (css, app_css, body, json.dumps(toc, ensure_ascii=False), json.dumps(segs, ensure_ascii=False), app_js)

    p = os.path.join(OUTDIR, 'app.html')
    open(p, 'w', encoding='utf-8').write(html)
    print('app.html', round(os.path.getsize(p) / 1e6, 1), 'MB; imgs', len(cache), '; lessons', len(lessons))


def build_appendix_page():
    import build_appendix as BA
    D = BA.lessons()
    rows = ''.join('<p class="ax-row"><span class="ax-no">%d</span>%s</p>' % (n, BA.full(D[n]['line_plain'])) for n in range(1, 202))
    补 = ''.join('<p class="ax-row"><span class="ax-no">%d</span>%s<span class="ax-pos">%s</span></p>' % (n, l, pos) for n, pos, l in BA.补)
    改 = ''.join('<div class="ax-card"><b>第 %d 课</b><div class="ax-c">%s</div><div class="ax-n">底本：%s<br>%s</div></div>' % (n, D[n]['line_plain'], b, note) for n, b, note in BA.改)
    异 = ''.join('<div class="ax-card"><b>%s</b><div class="ax-n">清版：%s<br>通行本：%s<br>%s</div></div>' % (a1, a2, a3, a4) for a1, a2, a3, a4 in BA.异文)
    return ('''<div class="page ax" id="appendix">
  <div class="runhead"><span>润泽少儿启蒙国学 · 三字经</span><span class="c">附 录</span></div>
  <h1>附录 · 次第链条与经文对照</h1>
  <div class="sub">全书 201 课，页码 2–403。旧稿中被删、被并之句，依作者裁定不入本表。</div>
  <div class="ax-h">附录一 · 次第链条全表</div>
  %s
  <div class="ax-h">附录二 · 甲 补入之课（18）</div>
  %s
  <div class="ax-h">附录二 · 乙 改笔复元（3）</div>
  %s
  <div class="ax-h">附录二 · 丙 异文存此不校（5）</div>
  %s
  <div class="folio">— 附录 —</div>
</div>
''' % (rows, 补, 改, 异))


if __name__ == '__main__':
    main()
