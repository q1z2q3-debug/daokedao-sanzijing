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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
BASE = os.path.join(ROOT, '三字经·样书·五课合览.html')

PH_CSS = """
figure.ph .phbox{width:100%;aspect-ratio:4/3;border:1px dashed #D6C9AE;background:#FBF7EC;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px}
figure.ph .phbox .k{font-family:"Noto Sans SC",sans-serif;font-size:11px;letter-spacing:.28em;color:#BCAF93}
figure.ph .phbox .f{font-family:"Noto Serif SC",serif;font-size:15px;color:#8C7F63;letter-spacing:.12em}
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


def head_pages(count=5):
    """取第 1–5 课原页：优先现有 docs/book.html（已经过编辑定稿），退回五课合览。

    页内注释保留，页间批次注释与空行剥掉。
    """
    src = os.path.join(DOCS, 'book.html')
    text = open(src if os.path.exists(src) else BASE, encoding='utf-8').read()
    starts = [m.start() for m in re.finditer(r'<div class="page">', text)]
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
    body = cover_for(lessons) + '\n' + head + ''.join(
        '\n\n<!-- 第 %s 课 -->\n%s' % (d['n'], pages[d['n']]) for d in lessons)
    body = re.sub(r'\n{3,}(?=<!-- 第 \d+ 课 -->)', '\n\n', body)
    return B.head('三字经·%s课合览（样书 %s）' % (cn_num(len(lessons) + 5), meta_from_changelog()[0]), '三', css) + body + B.TAIL


def main():
    lessons = load_lessons()
    css = B.read_css() + PH_CSS
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
