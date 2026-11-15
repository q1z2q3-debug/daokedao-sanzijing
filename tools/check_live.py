# -*- coding: utf-8 -*-
"""线上站点可达性检查（Actions 定时任务用）。

用法：
  python3 tools/check_live.py            # 检查 index.html / book.html
  python3 tools/check_live.py --all      # 额外检查每课单页

判定：HTTP 200，且 book.html 的 content-length 与仓库内 docs/book.html 字节数一致
（Pages 有部署延迟，默认重试 6 次、每次间隔 30 秒）。
"""
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://q1z2q3-debug.github.io/daokedao-sanzijing/'
RETRY, INTERVAL = 6, 30


def head(url):
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'sanzijing-ci'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, int(r.headers.get('content-length') or 0)


def wait_for(path, expect=None):
    url = BASE + path + '?cb=%d' % int(time.time())
    last = None
    for i in range(RETRY):
        try:
            code, size = head(url)
            last = (code, size)
            if code == 200 and (expect is None or size == expect):
                return True, last
        except Exception as e:  # noqa: BLE001
            last = ('ERR', str(e)[:60])
        if i < RETRY - 1:
            time.sleep(INTERVAL)
            url = BASE + path + '?cb=%d' % int(time.time())
    return False, last


def main():
    book = os.path.join(ROOT, 'docs', 'book.html')
    expect = os.path.getsize(book)
    fails = []
    ok, info = wait_for('index.html')
    print('index.html      ', 'OK' if ok else 'FAIL', info)
    if not ok:
        fails.append('index.html')
    ok, info = wait_for('book.html', expect)
    print('book.html       ', 'OK' if ok else 'FAIL', info, '本地 %d' % expect)
    if not ok:
        fails.append('book.html')

    if '--all' in sys.argv:
        idx = open(os.path.join(ROOT, 'docs', 'index.html'), encoding='utf-8').read()
        lessons = sorted(set(re.findall(r'href="(lesson\d+\.html)"', idx)))
        for name in lessons:
            ok, info = wait_for(name)
            print('%-15s' % name, 'OK' if ok else 'FAIL', info)
            if not ok:
                fails.append(name)

    if fails:
        print('FAIL: %s' % ', '.join(fails))
        return 1
    print('OK 线上与仓库一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
