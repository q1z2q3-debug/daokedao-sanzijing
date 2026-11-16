"""71–86 文案校订：合并两段骨架留下的重复。
规则：
1) 少儿「落到心上理解」若有两条「承接上一课存疑」，第二条改为「另有一问」；
2) 家长栏把同名小标题的上、下两段并成一条，重排一–四，末尾保留承接条；
3) 双卡四张并成两张（俗见／正解 各含上下两段）；
4) 成人页「命题考辨」里同名小节（对照当下现代语境、般若范式互参等）并成一节，重排（1）–（n）；
5) 成人页「和前面课程的张力」里重复的次第链条只留最全一条，同名「呼应『…』」并成一句；
6) 图注按实修正（只改字，不动图）。
"""
import copy, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import lessons_71_86 as L

CN = '一二三四五六七八九十'
ALT_FIX = {
    '课七十一·一笔点卷.jpg': ('案侧三名女童围看，蒙师执笔在长卷上轻点', '一笔点下去，卷上落一点红。'),
    '课七十二·书阶两级.jpg': ('书册在两级木案上摊开，童子踏着书阶向上', '案分数级，书搁在级上。'),
    '课七十九·三张素卡.jpg': ('男孩双手举着两张素卡，桌面另放一张', '三张素卡，一张一张翻开。'),
    '课八十五·架前平视.jpg': ('矮架上并排立着一列书，男孩站在架前平视', '架上的书并排，孩子在架前平视。'),
}


NEWFIG = {
    '79': [('课七十九·88·三环气韵相扣.jpg',
            '古法长案上三组环形气韵首尾相扣：山势、大地、周流回环',
            '三环相扣，三易同归。'),
           ('课七十九·87·三册轮流翻开.jpg',
            '书桌三本素面无字小册并放，孩子轮流翻开又合上',
            '三册轮着翻，三种角度。')],
    '80': [('课八十·89·六组简牍平列共览.jpg',
            '长案上六组形制略异的无字简牍分组平列',
            '六组简牍，各依其体。'),
           ('课八十·90·捧厚册家长陪读.jpg',
            '孩子捧一本较厚的素面书，家长在旁平坐陪读',
            '厚厚一册，七十篇。')],
    '81': [('课八十一·91·三类诗卷讽咏.jpg',
            '长案上三类无字诗卷舒展，师长手中册页为空白纸面',
            '风、雅、颂，三类诗卷。'),
           ('课八十一·92·伴声韵反复涵咏.jpg',
            '孩子伴着舒缓声韵反复念一段，家人静听',
            '一段一段，低声涵咏。')],
    '82': [('课八十二·93·诗卷渐淡编年简展开.jpg',
            '无字诗卷渐淡收起，一侧编年素简徐徐展开',
            '诗卷收起，编年展开。'),
           ('课八十二·94·安静记下两件小事.jpg',
            '孩子在一张无字卡片上安静记下两件小事',
            '两件小事，记在心里。')],
    '83': [('课八十三·96·三册注本并列同展一卷.jpg',
            '三册无字注本并列，同展一卷无字素简',
            '三册并列，同展一卷。'),
           ('课八十三·96·三人对照同一张空白卡纸.jpg',
            '三个孩子各执一册素面书，对照同一张空白卡纸',
            '三人各一册，同一张纸。')],
    '84': [('课八十四·97·经卷归位诸子散简展开.jpg',
            '六束无字经卷归位案右，案左诸子散简依次展开',
            '经卷归位，子书展开。'),
           ('课八十四·98·只留三枚无字卡片.jpg',
            '孩子把要点写成无字小卡片，只留三枚',
            '只留三张，其余收起。')],
    '85': [('课八十五·99·五册形制各异并置.jpg',
            '长案上五册形制各异的无字册同案并置',
            '五册并置，形制各异。'),
           ('课八十五·100·窗边静坐一册摊开.jpg',
            '孩子与长辈窗边静坐，一册无字书摊开',
            '窗边一册，慢慢摊开。')],
    '86': [('课八十六·101·经子归位编年长卷展开.jpg',
            '经卷与子册收拢归位，长案另侧展开编年长卷',
            '经子归位，长卷展开。'),
           ('课八十六·102·沿空白长页从右看到左.jpg',
            '孩子两只手沿一条无字长页自右端向左端移动',
            '从右看到左，看清终始。')],
}


def polish_kid(d):
    blocks = copy.deepcopy(d['kid'])
    if d['n'] in NEWFIG:
        figs = iter(NEWFIG[d['n']])
        for i, b in enumerate(blocks):
            if b[0] == 'fig':
                fn, alt, cap = next(figs)
                blocks[i] = ('fig', fn, alt, cap)
    seen = 0
    for i, b in enumerate(blocks):
        if b[0] == 'p' and '承接上一课存疑' in b[1]:
            seen += 1
            if seen >= 2:
                blocks[i] = ('p', b[1].replace('承接上一课存疑', '另有一问', 1))
    for i, b in enumerate(blocks):
        if b[0] == 'fig':
            fn = b[1]
            if fn in ALT_FIX:
                blocks[i] = ('fig', fn, ALT_FIX[fn][0], ALT_FIX[fn][1])
    return blocks


TITLE_RE = re.compile(r'<b>(?:[一二三四五六七八九十]+、)?(.+?)</b>')


def polish_tips(d):
    tips = [list(t) for t in d['tips']]
    groups = []          # [(title, [bodys], style)]
    tail = []
    for (style, txt) in tips:
        m = TITLE_RE.search(txt)
        if not m:
            tail.append((style, txt))
            continue
        title = m.group(1).rstrip('。')
        body = txt[m.end():].strip()
        for g in groups:
            if g[0] == title:
                g[1].append(body)
                if style and not g[1][-1].startswith(style):
                    pass
                break
        else:
            groups.append([title, [body], style])
    out = []
    for i, g in enumerate(groups):
        style = g[2] if g[2] else (g[1] and '')
        joined = ''.join(g[1])
        num = CN[i]
        out.append((style, '<b>%s、%s。</b>%s' % (num, g[0].rstrip('。'), joined)))
    out.extend(tail)
    return out


def polish_cards(d):
    cards = d['cards']
    half = len(cards) // 2
    if half != 2:
        return copy.deepcopy(cards)
    out = []
    for k in range(2):
        lab_cn = cards[k][0]
        sub = cards[k][1].replace('上段', '').replace('下段', '').strip(' ·')
        body = cards[k][2]
        body2 = cards[k + 2][2]
        out.append((lab_cn, '这 一 课 的 读 法', body + '；' + body2))
    return out


BLOCK_RE = re.compile(r'<b>（(\d)）(.+?)</b>')


def polish_adult(d):
    out = []
    for (num, paras) in d['adult']:
        paras = copy.deepcopy(paras)
        if paras and '命题考辨' in paras[0]:
            paras = merge_blocks(paras)
        elif paras and '和前面课程的张力' in paras[0]:
            paras = merge_chain(paras)
        else:
            paras = merge_bullets(paras)
        out.append((num, paras))
    return out


def merge_blocks(paras):
    out = []
    blocks = []          # [(key, title, [lines])]
    head = []
    for p in paras:
        m = BLOCK_RE.search(p)
        if m:
            title = m.group(2)
            key = '般若' if ('般若' in title or '互参' in title) else title
            blocks.append([key, title, []])
        elif blocks:
            blocks[-1][2].append(p)
        else:
            head.append(p)
    merged = []
    for (key, title, lines) in blocks:
        for m in merged:
            if m[0] == key:
                m[2].extend(lines)
                break
        else:
            merged.append([key, title, list(lines)])
    res = head[:]
    for i, (key, title, lines) in enumerate(merged):
        show = '般若范式互参' if key == '般若' else title
        res.append('<b>（%d）%s</b>' % (i + 1, show))
        if key == '般若':
            res.extend(combine_prajan(lines))
        else:
            res.extend(dedupe_labels(lines))
    return res


def merge_bullets(paras):
    """同书／同题的「·」条目并成一条；重复的「全句释义」分标上句、下句。"""
    out = []
    said = 0
    groups = []
    order = []
    for p in paras:
        if p.startswith('·'):
            label = p[1:].strip()
            key = label.split('：', 1)[0]
            body = label.split('：', 1)[1] if '：' in label else label
            for g in groups:
                if g[0] == key:
                    g[1].append(body)
                    break
            else:
                groups.append([key, [body]])
                order.append(('grp', len(groups) - 1))
        else:
            if p == '全句释义：' or p.startswith('全句释义：'):
                said += 1
                if said == 1:
                    p = p.replace('全句释义：', '上句释义：', 1)
                elif said == 2:
                    p = p.replace('全句释义：', '下句释义：', 1)
            order.append(('raw', p))
    for kind, v in order:
        if kind == 'raw':
            out.append(v)
        else:
            key, bodies = groups[v]
            joined = bodies[0]
            for b in bodies[1:]:
                joined += b
            out.append('· %s：%s' % (key, joined))
    return out


def dedupe_labels(lines):
    seen = set()
    out = []
    for x in lines:
        if x.endswith('：') and len(x) <= 30:
            if x in seen:
                continue
            seen.add(x)
        out.append(x)
    return out


BOOK_RE = re.compile(r'《[^》]+》')


def combine_prajan(lines):
    """把两段的般若互参并成一节：引言在前，联动／呼应各并一句，延伸义理按经名并条。"""
    lead, link, echo, quotes = [], [], [], []
    mode = 'lead'
    for x in lines:
        if x.startswith('联动'):
            mode = 'link'
            link.append(x)
        elif x.startswith('呼应'):
            mode = 'echo'
            echo.append(x)
        elif x.endswith('延伸义理：'):
            mode = 'quote'
        elif mode == 'quote':
            if x.startswith('《'):
                quotes.append(x)
            else:
                lead.append(x)
        elif mode == 'lead':
            lead.append(x)
        elif mode == 'link':
            link.append(x)
        elif mode == 'echo':
            echo.append(x)
    out = list(lead)
    if link:
        out.append(merge_prefix(link))
    if echo:
        out.append(merge_prefix(echo))
    if quotes:
        out.append('延伸义理：')
        out.extend(merge_books(quotes))
    return out


def merge_prefix(lines):
    """同一冒号前缀的多条，并成一条：前缀：文1；文2。"""
    key, _, body = lines[0].partition('：')
    rest = []
    for x in lines[1:]:
        _, _, b = x.partition('：')
        rest.append(b)
    joined = body.strip()
    for b in rest:
        joined += b.strip()
    return '%s：%s' % (key, joined)


def merge_books(quotes):
    order, by = [], {}
    for q in quotes:
        m = BOOK_RE.search(q)
        k = m.group(0) if m else '他'
        body = q[m.end():].lstrip('：').strip() if m else q
        if k not in by:
            by[k] = [body]
            order.append(k)
        else:
            by[k].append(body)
    out = []
    for k in order:
        b = by[k][0]
        for more in by[k][1:]:
            b += more.strip()
        out.append('%s%s' % (k, b if b.startswith('：') else '：' + b))
    return out


def merge_chain(paras):
    chain = []
    groups = []      # [(key, [bodies])]
    order = []       # ('chain',) / ('grp', idx)
    for p in paras:
        if p.startswith('次第链条'):
            if 'chain' not in order:
                order.append('chain')
            chain.append(p)
        elif p.startswith('呼应'):
            key, _, body = p.partition('：')
            for i, g in enumerate(groups):
                if g[0] == key:
                    g[1].append(body)
                    break
            else:
                groups.append([key, [body]])
                order.append(('grp', len(groups) - 1))
        else:
            order.append(('raw', p))
    res = []
    for item in order:
        if item == 'chain':
            if not chain:
                continue
            steps = []
            for c in chain:
                body = c.split('：', 1)[1] if '：' in c else c
                body = body.replace('（完整链条见附录）', '')
                for st in body.split('→'):
                    st = st.strip()
                    if st and st not in steps and st != '……':
                        steps.append(st)
            res.append('次第链条：……→ %s' % ' → '.join(steps))
        elif item[0] == 'grp':
            key, bodies = groups[item[1]]
            res.append('%s：%s' % (key, ''.join(bodies)))
        else:
            res.append(item[1])
    return res


def polish(d):
    d = copy.deepcopy(d)
    d['kid'] = polish_kid(d)
    d['tips'] = polish_tips(d)
    d['cards'] = polish_cards(d)
    d['adult'] = polish_adult(d)
    return d


def all_lessons():
    return [polish(x) for x in L.LESSONS]


if __name__ == '__main__':
    for d in all_lessons():
        print(d['n'], 'tips', len(d['tips']), 'cards', len(d['cards']),
              'adult2', len(d['adult'][1][1]), 'adult4', len(d['adult'][3][1]))
