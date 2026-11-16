# -*- coding: utf-8 -*-
"""把《三字经·补编·二十一课》文稿导入为 patch 课程数据。

支持两种标记：
  @AT n       插入到旧第 n 课之后
  @REPLACE n  替换旧第 n 课正文（课次不动）

田字格只写「右列／左列」各三字与拼音（12 字课写四行），笔画由新华字典数据补算。
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import import_103_127 as I

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_in', '文稿', '三字经·补编·二十一课（v3.2 校勘）.md')
OUT = os.path.join(ROOT, 'tools', 'lessons_patch_201.json')
WORD = '/tmp/word.json'

CN = '〇一二三四五六七八九'
def cn_num(n):
    if n < 10: return CN[n]
    if n < 20: return '十' + (CN[n % 10] if n % 10 else '')
    if n < 100: return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')
    h, r = divmod(n, 100)
    head = CN[h] + '百'
    if not r: return head
    if r < 10: return head + '零' + CN[r]
    if r < 20: return head + '一' + cn_num(r)
    return head + cn_num(r)

def strokes_map():
    data = json.load(open(WORD, encoding='utf-8'))
    m = {}
    for d in data:
        s = str(d.get('strokes', '')).strip()
        if not s: continue
        try: m.setdefault(d['word'], int(s))
        except ValueError: pass
    return m

def cn_strokes(k):
    return cn_num(k) + '画'

GRID_COLS = re.compile(r'^(右列|左列)：(.*)$')

def read_cols(block):
    """取田字格节的列定义，返回 [(侧, 拼音list, 字list)]。"""
    sec = re.search(r'##\s*田字格[^\n]*\n(.+?)(?=\n##\s)', block, re.S)
    if not sec:
        raise ValueError('缺田字格节')
    cols = []
    for ln in sec.group(1).split('\n'):
        m = GRID_COLS.match(ln.strip())
        if not m: continue
        body, py = m.group(2), ''
        pm = re.search(r'（(.+?)）', body)
        if pm: py = pm.group(1).strip()
        chars = [c.strip() for c in re.split(r'·', body.split('（')[0]) if c.strip()]
        pys = py.split()
        if len(chars) != 3 or len(pys) != 3:
            raise ValueError('列不为三字或拼音不齐：%r' % ln)
        cols.append((m.group(1), pys, chars))
    if len(cols) not in (2, 4):
        raise ValueError('列数应为 2 或 4，实为 %d' % len(cols))
    return cols

def cells(col, sm):
    side, pys, chars = col
    out = []
    for p, c in zip(pys, chars):
        if c not in sm:
            raise ValueError('缺笔画：%s' % c)
        out.append([p, c, cn_strokes(sm[c])])
    return out

def grid_blocks(cols, sm):
    """2 列 → 一块；4 列 → 两块。"""
    def txt(cs): return ''.join(x[1] for x in cs)
    b = []
    for i in range(0, len(cols), 2):
        r, l = cols[i], cols[i + 1]
        cr, cl = cells(r, sm), cells(l, sm)
        if i == 0:
            rn = ('古法竖排：<b>自右而左，自上而下</b>。%s先读右列「%s」，再读左列「%s」。'
                  % ('上段' if len(cols) == 4 else '', txt(cr), txt(cl)))
            tag = ('① 先读右列', cr, '② 再读左列', cl, rn)
        else:
            rn = '下段续读：先读右列「%s」，再读左列「%s」。' % (txt(cr), txt(cl))
            tag = ('③ 续读右列', cr, '④ 再读左列', cl, rn)
        b.append(list(tag))
    return b

def main():
    text = open(SRC, encoding='utf-8').read()
    sm = strokes_map()
    heads = [(m.start(), m.group(0)) for m in re.finditer(r'^#\s*(补|改)[^\n]*', text, re.M)]
    if len(heads) != 21:
        raise SystemExit('课数不是 21：%d' % len(heads))
    lessons = []
    for k, (pos, head) in enumerate(heads):
        nxt = heads[k + 1][0] if k + 1 < len(heads) else len(text)
        block = text[pos:nxt]
        first, _, body = block.partition('\n')
        m = re.match(r'^#\s*(补|改)\S+\s*@(AT|REPLACE)\s*(\d+)\s*(.*)$', first.strip())
        if not m:
            raise ValueError('标题不合式：%r' % first)
        mode, anchor, line = ('insert' if m.group(2) == 'AT' else 'replace'), int(m.group(3)), m.group(4).strip()
        cols = read_cols(block)
        # 让 parse_lesson 能跑：把田字格临时压成两列
        fake = re.sub(r'##\s*田字格[^\n]*\n(.+?)(?=\n##\s)',
                      lambda mm: '## 田字格（古法竖排）\n右列：%s\n左列：%s\n\n'
                      % (' · '.join(cols[0][2]) + '（' + ' '.join(cols[0][1]) + '）｜笔画：' +
                         '、'.join(str(sm[c]) for c in cols[0][2]),
                         ' · '.join(cols[1][2]) + '（' + ' '.join(cols[1][1]) + '）｜笔画：' +
                         '、'.join(str(sm[c]) for c in cols[1][2])),
                      block, count=1, flags=re.S)
        title = '第%s课 %s' % (cn_num(anchor), line)
        d = I.parse_lesson(anchor + 16, title, fake.partition('\n')[2])
        d['grid_split'] = grid_blocks(cols, sm)
        d['pinyin'] = '　'.join(' '.join(c[1]) for c in cols)
        d['anchor'] = anchor
        d['mode'] = mode
        d.pop('n', None); d.pop('no_cn', None); d.pop('no_short', None); d.pop('runhead', None)
        lessons.append(d)
    json.dump({'lessons': lessons}, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('写出', len(lessons), '课 →', OUT)
    for d in lessons:
        print(' ', d['mode'], d['anchor'], d['line'], len(d['kid']), len(d['cards']))

if __name__ == '__main__':
    main()
