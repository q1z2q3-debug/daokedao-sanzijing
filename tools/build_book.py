# -*- coding: utf-8 -*-
"""总装：从内容模块从零重建整本合册（CI 与本地共用）。

结构：封面（按课数、版本、年月生成）＋ 第 1–5 课原页（取自五课合览，不重排）
      ＋ 第 6 课起由 lessons_*.py 逐课渲染。

用法：
  python3 tools/build_book.py            只重建 docs/book.html 与合览，不覆盖单课页
  python3 tools/build_book.py --full     同时重出 docs/lesson06..N.html
  python3 tools/build_book.py --check    只在生成结果与现有 book.html 不一致时报错退出
"""
import glob
import importlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
import toc_plan as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
BASE = os.path.join(ROOT, '三字经·样书·五课合览.html')

PH_CSS = """
figure.ph .phbox{width:100%;aspect-ratio:4/3;border:1px dashed #D6C9AE;background:#FBF7EC;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px}
figure.ph .phbox .k{font-family:"Noto Sans SC",sans-serif;font-size:11px;letter-spacing:.28em;color:#BCAF93}
figure.ph .phbox .f{font-family:"Noto Serif SC",serif;font-size:15px;color:#8C7F63;letter-spacing:.12em}
"""

TOC_CSS = """
.page.toc,.page.toc2{padding:64px 64px 54px}
.toc h1,.toc2 h1{font-size:34px;font-weight:600;letter-spacing:.28em;margin:0 0 10px}
.toc .tl,.toc2 .tl{font-family:"Noto Sans SC",sans-serif;font-size:12.5px;color:var(--muted);line-height:2;letter-spacing:.04em;margin-bottom:26px}
.toc .qbar{display:flex;align-items:center;gap:12px;margin:0 0 22px;flex-wrap:wrap}
.toc .qbar input{flex:1 1 300px;padding:11px 14px;border:1px solid var(--line);background:#FCF8EF;font-family:"Noto Serif SC",serif;font-size:16px;color:var(--ink);outline:none;min-width:0}
.toc .qbar input:focus{border-color:var(--ochre)}
.toc .qbar .hint{font-family:"Noto Sans SC",sans-serif;font-size:11.5px;color:var(--muted);white-space:nowrap;letter-spacing:.06em}
#hits{display:none;margin:0 0 24px;font-family:"Noto Sans SC",sans-serif;font-size:12.5px;line-height:1.9;color:var(--ink2)}
#hits a{display:block;padding:5px 0;border-bottom:1px dashed var(--line);color:var(--ink2);text-decoration:none}
#hits a:hover{color:var(--ochre)}
#hits .none{color:var(--muted)}
.toc .grp{margin-top:20px}
.toc .gh{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--line);padding-bottom:8px}
.toc .gn{font-family:"Noto Sans SC",sans-serif;font-size:11.5px;letter-spacing:.24em;color:var(--ochre)}
.toc .gt{font-family:"Noto Sans SC",sans-serif;font-size:12px;color:var(--muted);letter-spacing:.06em}
.toc .cols{column-count:2;column-gap:38px;margin-top:8px}
.toc a.it{display:flex;align-items:baseline;padding:5px 0;font-size:14px;color:var(--ink);text-decoration:none;break-inside:avoid;line-height:1.7}
.toc a.it:hover .ln{color:var(--ochre)}
.toc .no{font-family:"Noto Sans SC",sans-serif;font-size:10.5px;color:var(--muted);flex:0 0 28px;letter-spacing:.04em}
.toc .ln{flex:0 1 auto}
.toc .dots{flex:1 1 12px;margin:0 6px;border-bottom:1px dotted #D9CDB4;transform:translateY(-3px)}
.toc .pg{font-family:"Noto Sans SC",sans-serif;font-size:11px;color:var(--muted);flex:0 0 28px;text-align:right}
.toc2 .cols{column-count:2;column-gap:36px;margin-top:8px}
.toc2 .it{display:flex;align-items:baseline;padding:5px 0;font-size:13.5px;color:#8C7F63;break-inside:avoid;line-height:1.7}
.toc2 .no{font-family:"Noto Sans SC",sans-serif;font-size:10.5px;color:#BCAF93;flex:0 0 28px}
.toc2 .tag{font-family:"Noto Sans SC",sans-serif;font-size:10px;color:#B7A88B;border:1px solid #E6DBC4;padding:0 4px;margin-left:auto;flex:0 0 auto;letter-spacing:.08em}
.toc .note2,.toc2 .note2{font-family:"Noto Sans SC",sans-serif;font-size:11.5px;color:var(--muted);line-height:2;margin-top:28px;border-top:1px solid var(--line);padding-top:14px}
.go-toc{position:fixed;right:16px;bottom:16px;z-index:9;display:flex;font-family:"Noto Sans SC",sans-serif;font-size:11.5px}
.go-toc a{padding:8px 11px;background:#FBF6E9;border:1px solid #E0D5BD;color:var(--ink2);text-decoration:none;letter-spacing:.14em;box-shadow:0 4px 14px rgba(60,45,30,.10)}
.go-toc a+a{border-left:0}
.go-toc a:hover{color:var(--ochre)}
@media(max-width:760px){.toc,.toc2{padding:40px 22px 34px}.toc .cols,.toc2 .cols{column-count:1}.go-toc{right:8px;bottom:8px}}
"""

SEARCH_JS = r"""
<script>
(function(){
  var q=document.getElementById('q'),hits=document.getElementById('hits'),idx=null;
  if(!q||!hits)return;
  function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function build(){
    idx=[];
    var ps=document.querySelectorAll('.page[id^="k"]');
    for(var i=0;i<ps.length;i++){
      var p=ps[i],n=parseInt(p.id.slice(1),10),t=p.textContent.replace(/\s+/g,' ');
      var nx=p.nextElementSibling;
      if(nx&&nx.classList&&nx.classList.contains('adult')) t+=' '+nx.textContent.replace(/\s+/g,' ');
      idx.push({n:n,t:t,href:'#k'+p.id.slice(1),next:0});
    }
    var nxt=document.querySelectorAll('.toc2 .it');
    for(var j=0;j<nxt.length;j++){
      var it=nxt[j],no=it.querySelector('.no');
      if(!no)continue;
      idx.push({n:parseInt(no.textContent,10),t:it.textContent.replace('待写','').replace(/\s+/g,' '),
                href:'#toc2',next:1});
    }
    idx.sort(function(a,b){return a.n-b.n;});
  }
  function run(){
    var v=q.value.trim();
    if(!v){hits.style.display='none';hits.innerHTML='';return;}
    if(!idx)build();
    var out=[],k;
    for(k=0;k<idx.length&&out.length<16;k++){
      if(idx[k].t.indexOf(v)>-1){
        var pos=idx[k].t.indexOf(v);
        var sn=idx[k].t.slice(Math.max(0,pos-16),pos+v.length+34);
        var lab=idx[k].next?('续 '+idx[k].n+' 课·待写'):('第 '+idx[k].n+' 课');
        var tail=idx[k].next?'　（续编存目）':'';
        out.push('<a href="'+idx[k].href+'">'+lab+'　…'+esc(sn)+'…'+tail+'</a>');
      }
    }
    hits.style.display='block';
    hits.innerHTML=out.length?out.join(''):'<div class="none">没有找到。换个词，或只搜两个字。</div>';
  }
  q.addEventListener('input',run);
  q.addEventListener('keydown',function(e){
    if(e.key==='Enter'){var a=hits.querySelector('a');if(a){location.hash=a.getAttribute('href');}}
  });
})();
</script>
"""

NAV_CSS = """
.page.land{outline:2px solid rgba(162,80,59,.45);outline-offset:1px}
"""

NAV_JS = r"""
<script>
(function(){
  var seq=0;
  function go(id){
    var t=document.getElementById(id);
    if(!t)return;
    var my=++seq, n=0;
    (function step(){
      if(my!==seq)return;
      t.scrollIntoView({block:'start'});
      if(n++>10)return;
      setTimeout(step,160);
    })();
    t.classList.add('land');
    setTimeout(function(){t.classList.remove('land');},1500);
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest?e.target.closest('a[href^="#"]'):null;
    if(!a)return;
    var id=a.getAttribute('href').slice(1);
    if(!id||!document.getElementById(id))return;
    e.preventDefault();
    go(id);
    if(history.replaceState)history.replaceState(null,'','#'+id);
  },false);
  if(location.hash&&location.hash.length>1){
    var id0=location.hash.slice(1);
    if(document.getElementById(id0))setTimeout(function(){go(id0);},60);
  }
})();
</script>
"""
CN = '〇一二三四五六七八九'


def cn_num(n):
    if n < 10:
        return CN[n]
    if n < 20:
        return '十' + (CN[n % 10] if n % 10 else '')
    return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')


def load_lessons():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'tools', 'lessons_*.py'))):
        name = os.path.splitext(os.path.basename(path))[0]
        out.extend(importlib.import_module(name).LESSONS)
    import polish_71_86 as PL
    out = [PL.polish(d) if 71 <= int(d['n']) <= 86 else d for d in out]
    return sorted(out, key=lambda d: int(d['n']))


def meta_from_changelog():
    text = open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
    m = re.search(r'##\s*v(\d+\.\d+(?:\.\d+)?)\s*—\s*(\d{4})-(\d{2})-(\d{2})', text)
    if not m:
        return 'v0.0', '二〇二六年十一月'
    ver, y, mo, _d = m.groups()
    ym = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九', 10: '十', 11: '十一', 12: '十二'}
    return 'v' + ver, ''.join(CN[int(c)] for c in y) + '年' + ym[int(mo)] + '月'


def cover_for(lessons):
    last = lessons[-1]['line_plain']
    m = re.search(r'<h1>([^<，]+)，', open(BASE, encoding='utf-8').read())
    head = m.group(1) if m else lessons[0]['line_plain'].split('，')[0]
    tail = last.split('，')[-1]
    ver, ym = meta_from_changelog()
    n = len(lessons) + 5
    return ('<div class="page cover">\n'
            '  <div class="s">润 泽 少 儿 启 蒙 国 学</div>\n'
            '  <h1>三 字 经</h1>\n'
            '  <div class="t2">一句一故事 · 一图一世界</div>\n'
            '  <div class="line"></div>\n'
            '  <div class="info">第一课至第%s课　·　%s　至　%s<br>亲子共读 4–9 岁　·　每课双页：少儿读本 ／ 成人研学<br>样书　%s　·　%s</div>\n'
            '</div>' % (cn_num(n), head, tail, ver, ym))


def toc_entries(lessons):
    """已成课次：课号、原句、页码（少儿页）。"""
    lines = {}
    for d in lessons:
        lines[int(d['n'])] = d['line_plain']
    lines.update(T.LINES_1_5)
    return [(n, lines[n], 2 * n) for n in sorted(lines)]


def toc_page(lessons):
    rows = toc_entries(lessons)
    by_n = {n: (line, folio) for (n, line, folio) in rows}
    grp = []
    for (no, name, a, b) in T.GROUPS:
        items = []
        for n in range(a, b + 1):
            line, folio = by_n[n]
            items.append('      <a class="it" href="#k%d"><span class="no">%d</span>'
                         '<span class="ln">%s</span><span class="dots"></span>'
                         '<span class="pg">%d</span></a>' % (n, n, line, folio))
        grp.append('    <div class="grp">\n      <div class="gh"><span class="gn">%s</span>'
                   '<span class="gt">%s　第 %d–%d 课</span></div>\n'
                   '      <div class="cols">\n%s\n      </div>\n    </div>'
                   % (no, name, a, b, '\n'.join(items)))
    return ('<div class="page toc" id="toc">\n'
            '  <div class="runhead"><span>润泽少儿启蒙国学 · 三字经</span><span class="c">目 录</span></div>\n'
            '  <h1>目 录</h1>\n'
            '  <div class="tl">八十六课，一课两页。点课号到该课少儿页，成人页在后一页；题下数字为该课少儿页页码。</div>\n'
            '  <div class="qbar"><input id="q" type="search" autocomplete="off" '
            'placeholder="搜原文、字词、人名、典名（含续编存目）　如：中庸／断机杼／项橐" aria-label="查册">'
            '<span class="hint">回车到第一处</span></div>\n'
            '  <div id="hits"></div>\n'
            '%s\n'
            '  <div class="note2">分段只是读法上的分段，课次照旧一贯到底。续编（第八十七课起）另页存目，尚未成课。</div>\n'
            '</div>' % '\n'.join(grp))


def toc_page_next():
    rows = []
    for i, line in enumerate(T.NEXT):
        n = T.NEXT_START + i
        rows.append((n, line))
    grp = []
    for (no, name, a, b) in T.NEXT_GROUPS:
        items = ['      <div class="it"><span class="no">%d</span><span class="ln">%s</span>'
                 '<span class="tag">待写</span></div>' % (n, line)
                 for (n, line) in rows if a <= n <= b]
        grp.append('    <div class="grp">\n      <div class="gh"><span class="gn">%s</span>'
                   '<span class="gt">%s　第 %d–%d 课</span></div>\n'
                   '      <div class="cols">\n%s\n      </div>\n    </div>'
                   % (no, name, a, b, '\n'.join(items)))
    return ('<div class="page toc2" id="toc2">\n'
            '  <div class="runhead"><span>润泽少儿启蒙国学 · 三字经</span><span class="c">续 编 存 目</span></div>\n'
            '  <h1>续 编 存 目</h1>\n'
            '  <div class="tl">「考世系，知终始」之后，三字经还有读史与勤学两大段。全段尚未成课，先按通行本四句一组占位排号，留出位置；成课时以校定底本为定，课次可整体重排。</div>\n'
            '%s\n'
            '  <div class="note2">存目句依通行本录，未校异文；课次为占位，不作准。</div>\n'
            '</div>' % '\n'.join(grp))


def head_pages(count=5):
    """取第 1–5 课原页：优先现有 docs/book.html（已经过编辑定稿），退回五课合览。

    页内注释保留，页间批次注释与空行剥掉。
    """
    src = os.path.join(DOCS, 'book.html')
    text = open(src if os.path.exists(src) else BASE, encoding='utf-8').read()
    starts = [m.start() for m in re.finditer(r'<div class="page"(?: id="k\d+")?>', text)]
    if len(starts) < count:
        raise SystemExit('五课合览中课页不足 %d 个' % count)
    if len(starts) > count:
        ends = starts[1:count + 1]
    else:
        ends = starts[1:count] + [text.rindex('</body>')]
    blocks = []
    for a, b in zip(starts[:count], ends):
        block = text[a:b].rstrip()
        # 只剥页尾的批次/分段注释，保留页内注释
        while block.endswith('-->'):
            block = block[:block.rindex('<!--')].rstrip()
        block = re.sub(r'<div class="page" id="k\d+">', '<div class="page">', block, count=1)
        blocks.append(block)
    return '\n'.join(blocks)


def render_pages(lessons):
    pages = {}
    for d in lessons:
        folio = 2 * int(d['n'])
        pages[d['n']] = B.kid_page(d, folio) + B.adult_page(d, folio + 1)
    return pages


def assemble(lessons, css):
    head = head_pages()
    pages = render_pages(lessons)
    body = cover_for(lessons) + '\n' + toc_page(lessons) + '\n' + toc_page_next() + '\n' + head + ''.join(
        '\n\n<!-- 第 %s 课 -->\n%s' % (d['n'], pages[d['n']]) for d in lessons)
    body = re.sub(r'\n{3,}(?=<!-- 第 \d+ 课 -->)', '\n\n', body)
    # 给每一课少儿页挂锚点 k1..kN（封面与目录页类名不同，不入此列）
    cnt = {'i': 0}

    def _anch(m):
        cnt['i'] += 1
        return '<div class="page" id="k%d">' % cnt['i']

    body = re.sub(r'<div class="page">', _anch, body)
    body += ('\n<div class="go-toc"><a href="#toc">目 录</a><a href="#toc2">续 编</a>'
             '<a href="#k%d">末 课</a></div>\n' % int(lessons[-1]['n'])) + SEARCH_JS + NAV_JS
    return B.head('三字经·%s课合览（样书 %s）' % (cn_num(len(lessons) + 5), meta_from_changelog()[0]), '三', css) + body + B.TAIL


def main():
    lessons = load_lessons()
    css = B.read_css() + PH_CSS + TOC_CSS + NAV_CSS
    html = assemble(lessons, css)
    n = len(lessons)
    total = n + 5
    name = '三字经·样书·%s课合览.html' % cn_num(total)
    out_book = os.path.join(ROOT, name)
    docs_book = os.path.join(DOCS, 'book.html')

    if '--check' in sys.argv:
        cur = open(docs_book, encoding='utf-8').read() if os.path.exists(docs_book) else ''
        if cur == html:
            print('OK 总装结果与 docs/book.html 一致（%d 课，%.2f MB）' % (total, len(html.encode()) / 1048576))
            return 0
        print('DIFF 总装结果与 docs/book.html 不一致（新 %d 字节 / 旧 %d 字节）'
              % (len(html.encode()), len(cur.encode())))
        return 1

    open(out_book, 'w', encoding='utf-8').write(html)
    open(docs_book, 'w', encoding='utf-8').write(html)
    print('%-46s %8.1f MB' % (os.path.relpath(out_book, ROOT), os.path.getsize(out_book) / 1048576))

    if '--full' in sys.argv:
        for d in lessons:
            p = os.path.join(DOCS, 'lesson%02d.html' % int(d['n']))
            open(p, 'w', encoding='utf-8').write(
                B.head('%s　%s——润泽说·少儿启蒙国学读本' % (d['no_short'], d['line_plain']), d['fav'], css)
                + B.kid_page(d, 2 * int(d['n'])) + '\n' + B.adult_page(d, 2 * int(d['n']) + 1) + B.TAIL)
        print('单课页已重出：lesson%02d–lesson%02d' % (int(lessons[0]['n']), int(lessons[-1]['n'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
