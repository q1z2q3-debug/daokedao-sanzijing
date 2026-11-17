# -*- coding: utf-8 -*-
"""把 docs/book.html 出成单文件轻量版：图缩到 900px WebP 内嵌（约 30 MB）。"""
import base64, io, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')


def main():
    s = open(os.path.join(DOCS, 'book.html'), encoding='utf-8').read()
    cache = {}

    import re
    def repl(m):
        f = m.group(1)
        if f in cache:
            return 'src="%s"' % cache[f]
        im = Image.open(os.path.join(DOCS, 'assets', f)).convert('RGB')
        if im.width > 900:
            im = im.resize((900, int(im.height * 900 / im.width)), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, 'WEBP', quality=67, method=6)
        cache[f] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
        return 'src="%s"' % cache[f]

    out = re.sub(r'src="assets/([^"]+)"', repl, s)
    p = os.path.join(ROOT, '三字经·二百零一课·合览（单文件·轻量）.html')
    open(p, 'w', encoding='utf-8').write(out)
    print('%s  %.1f MB  imgs %d' % (os.path.basename(p), os.path.getsize(p) / 1048576, len(cache)))


if __name__ == '__main__':
    main()
