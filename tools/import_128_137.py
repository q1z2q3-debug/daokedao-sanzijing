# -*- coding: utf-8 -*-
"""把《第一百二十八至一百三十七课·续编合稿》拆成课页数据。

源件：_in/文稿/三字经·第一百二十八至一百三十七课·续编合稿.md（10 课）
产出：tools/lessons_112_121.json（书内课次 112–121，合稿课次 128–137）

原则与 import_103_127 全同：正文照原文搬，只做渲染所需的分段与标记；
图位一律留空，落成 figure.ph 虚线框，不出图。
解析函数直接从 import_103_127 借用，不另起一套，免得两处口径走偏。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from import_103_127 import parse_lesson, scrub   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_in', '文稿', '三字经·第一百二十八至一百三十七课·续编合稿.md')
OUT = os.path.join(ROOT, 'tools', 'lessons_112_121.json')

FIRST = 128       # 合稿首课
COUNT = 10
OFFSET = 16       # 书 86 ＝ 合稿 101+102，故合稿 128 → 书 112


def main():
    text = open(SRC, encoding='utf-8').read()
    starts = [m.start() for m in re.finditer(r'^#\s*第[一二三四五六七八九十百零〇]+课', text, re.M)]
    if len(starts) != COUNT:
        raise SystemExit('课数不是 %d：%d' % (COUNT, len(starts)))
    blocks = [text[a:b] for a, b in zip(starts, starts[1:] + [len(text)])]

    lessons = []
    for k, blk in enumerate(blocks):
        first, _, rest = blk.partition('\n')
        title = first.lstrip('# ').strip()
        lessons.append(parse_lesson(FIRST + k, title, rest))

    raw = json.dumps(lessons, ensure_ascii=False, indent=1)
    # 与 103–127 同一批口径修订，防止旧说法回潮
    raw = raw.replace('羂光', '韬光')
    raw = raw.replace('三皇是“二阳敷化、一阴归藏”', '三皇是「阳启、枢济、阴藏」')
    raw = raw.replace('（完整链条见附录）', '')
    lessons = scrub(json.loads(raw))

    json.dump({'lessons': lessons}, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('OK %d 课 → %s' % (len(lessons), os.path.relpath(OUT, ROOT)))
    for d in lessons:
        print('%s → 书 %s ｜ %s ｜lead %d ｜段落 %d ｜图位 %d ｜卡 %d ｜启示 %d ｜家长 %d ｜成人 %s ｜存疑 %d'
              % (d['no_short'], d['n'], d['line'], len(d['kid'][0][1]),
                 len([x for x in d['kid'] if x[0] == 'p']),
                 len([x for x in d['kid'] if x[0] == 'ph']),
                 len(d['cards']), len(d['takes']), len(d['tips']),
                 [s[0] for s in d['adult']], len(d['doubt'])))


if __name__ == '__main__':
    main()
