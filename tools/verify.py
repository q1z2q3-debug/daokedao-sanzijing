# -*- coding: utf-8 -*-
"""合册与站点一致性校验（CI 与本地共用，零第三方依赖）。

用法：
  python3 tools/verify.py            # 校验 docs/book.html 与 docs/ 站点
  python3 tools/verify.py --quiet    # 只在失败时输出

校验项：
  1 课页数 N、成人页 N、插图＋占位框 2N（新段图位留空，虚线框计位）
  2 base64 图 2N−占位框 张且互不重复
  3 页码 2..2N+1 连续
  4 根目录存在同内容的「N 课合览」，且其页数同为 N
  5 docs/lessonNN.html 齐备，每份恰含 1 少儿页 + 1 成人页 + 2 图
  6 docs/index.html 列出 N 条「读 单 课」，链接全部可达
  7 入口页版本号能在 CHANGELOG 中找到
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')

fails = []
notes = []


def check(cond, msg):
    if cond:
        return True
    fails.append(msg)
    return False


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    book_path = os.path.join(DOCS, 'book.html')
    if not os.path.exists(book_path):
        print('FAIL: docs/book.html 不存在')
        return 1
    book = open(book_path, encoding='utf-8').read()
    page_re = r'<div class="page(?: long)?"(?: id="k\d+")?>'
    n = len(re.findall(page_re, book))
    check(n > 0, '课页数为 0')
    check(book.count('class="page cover"') == 1, '封面页数不为 1')
    check(book.count('<div class="adult">') == n, '成人页数 %d ≠ 课页数 %d' % (book.count('<div class="adult">'), n))

    figures = book.count('<figure>')
    ph = book.count('<figure class="ph">')
    check(figures + ph == 2 * n, '插图＋占位框 %d ≠ 2N(%d)' % (figures + ph, 2 * n))

    imgs = re.findall(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)', book)
    refs = re.findall(r'src="assets/([^"]+)"', book)
    if imgs:
        uniq = len({hashlib.md5(x.encode()).hexdigest() for x in imgs})
        check(len(imgs) == 2 * n - ph, 'base64 图 %d ≠ 2N−占位(%d)' % (len(imgs), 2 * n - ph))
        check(uniq == len(imgs), 'base64 图有重复：%d 张仅 %d 种' % (len(imgs), uniq))
    else:
        check(len(refs) == 2 * n - ph, '外置图引用 %d ≠ 2N−占位(%d)' % (len(refs), 2 * n - ph))
        missing = [x for x in refs if not os.path.exists(os.path.join(DOCS, 'assets', x))]
        check(not missing, '外置图缺文件：%s' % ', '.join(sorted(set(missing))[:5]))

    folios = [int(x) for x in re.findall(r'— (\d+) —', book)]
    check(folios == list(range(2, 2 * n + 2)), '页码序列不连续（首 %s 尾 %s 共 %d 个）'
          % (folios[:2], folios[-2:], len(folios)))

    book_md5 = md5(book_path)
    twins = []
    for name in os.listdir(ROOT):
        if '合览' in name and name.endswith('.html') and '单文件' not in name:
            p = os.path.join(ROOT, name)
            txt = open(p, encoding='utf-8').read()
            norm = txt.replace('src="docs/assets/', 'src="assets/')
            if md5(p) == book_md5 or norm == book:
                twins.append((name, len(re.findall(page_re, txt))))
    check(bool(twins), '根目录没有与 docs/book.html 同内容的合览')
    for name, pages in twins:
        check(pages == n, '合览 %s 页数 %d ≠ %d' % (name, pages, n))
    if twins:
        notes.append('合览同源：%s' % twins[0][0])

    for i in range(1, n + 1):
        p = os.path.join(DOCS, 'lesson%02d.html' % i)
        if not os.path.exists(p):
            fails.append('缺少 docs/lesson%02d.html' % i)
            continue
        s = open(p, encoding='utf-8').read()
        if (len(re.findall(page_re, s)) != 1 or s.count('<div class="adult">') != 1
                or (s.count('<figure>') + s.count('<figure class="ph">') != 2
                    and len(re.findall(r'<figure>', s)) + len(re.findall(r'<figure class="ph">', s)) != 2)):
            fails.append('docs/lesson%02d.html 结构异常（页 %d／成人 %d／图 %d＋占位 %d）'
                         % (i, len(re.findall(page_re, s)), s.count('<div class="adult">'),
                            s.count('<figure>'), s.count('<figure class="ph">')))

    index_path = os.path.join(DOCS, 'index.html')
    check(os.path.exists(index_path), '缺少 docs/index.html')
    if os.path.exists(index_path):
        idx = open(index_path, encoding='utf-8').read()
        links = re.findall(r'href="(lesson\d+\.html)"', idx)
        check(len(links) == n, '入口列 %d 课 ≠ %d' % (len(links), n))
        missing = [l for l in links if not os.path.exists(os.path.join(DOCS, l))]
        check(not missing, '入口存在死链：%s' % ', '.join(missing))
        m = re.search(r'v(\d+\.\d+(?:\.\d+)?)', idx)
        if not m:
            fails.append('入口页缺少版本号')
        else:
            ver = m.group(1)
            cl = open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
            check(('v' + ver) in cl, '入口版本 v%s 未记入 CHANGELOG' % ver)
            notes.append('站点版本 v%s' % ver)

    if ph:
        notes.append('图位待补 %d 处' % ph)
    notes.append('课页 %d ／ 插图 %d ／ 页码 2–%d ／ %.2f MB' % (n, figures, 2 * n + 1, len(book.encode()) / 1048576))
    quiet = '--quiet' in sys.argv
    if fails:
        print('FAIL (共 %d 项)' % len(fails))
        for msg in fails:
            print('  - %s' % msg)
        return 1
    if not quiet:
        print('OK  %s' % '；'.join(notes))
    return 0


if __name__ == '__main__':
    sys.exit(main())
