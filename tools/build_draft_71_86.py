# -*- coding: utf-8 -*-
"""71–86 文案校订稿（图暂空）单文件 HTML。
读 tools/lessons_71_86 → polish_71_86 校订 → 图位换成占位框 → 拼双页。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
import polish_71_86 as P

OUT = os.path.join(B.ROOT, '三字经·第七十一至八十六课·文案校订稿.html')


def ph_tag(fname, alt, cap):
    return ('<figure class="figempty">\n'
            '      <div class="ph">图暂空<span class="f">%s</span></div>\n'
            '      <figcaption>%s</figcaption>\n'
            '    </figure>' % (fname.replace('.jpg', ''), cap))


PH_CSS = """
.figempty .ph{margin:14px 0 0;border:1px dashed #D8CBB2;background:#FBF7EC;color:#9A8C77;
  font-size:13px;letter-spacing:.12em;padding:64px 0;text-align:center;border-radius:2px}
.figempty .ph .f{display:block;margin-top:8px;font-size:11px;color:#B4A88F;letter-spacing:.04em}
"""

NOTE = """<div class="page">
  <div class="runhead"><span>润泽少儿启蒙国学 · 三字经</span><span class="c">文案校订稿</span></div>
  <div class="lesson-no">校 订 说 明</div>
  <h1>第七十一至八十六课　文案校订</h1>
  <div class="sub">图位暂空，先看文；确认后再并回正本</div>
  <div class="kid" style="margin-top:34px">
    <p class="lead">这一稿只动文字，不动版面骨架，图位留空，等你看完文再决定图。</p>
    <p><b>一、少儿页。</b>原来每课是两段并成，两段各带一句「承接上一课存疑」。现只保留前一句，后一句改作「另有一问」，不致同一句话在同一页里重复两遍。</p>
    <p><b>二、家长栏。</b>原为九条：一至四、五至八，四个小标题各出现两次（勘俗见、现代对照、常变主线、教与学二分）。现按同名标题并作四条，末尾承接条不动。</p>
    <p><b>三、双卡。</b>原四张（俗见上段／正解上段／俗见下段／正解下段），并为两张：俗见、正解各收上下两段的说法。</p>
    <p><b>四、成人页。</b>「命题考辨」原六小节，其中「对照当下现代语境」「般若范式互参」各两遍；现同名并节，重排为（1）至（4）（第八十六课两段节数不等，并为五节）。「和前面课程的张力」里重复的次第链条并成一条，同名「呼应」并成一句。</p>
    <p><b>五、图注。</b>按实改了四处字（课七十一、七十二、七十九、八十五），图本身未动。课八十六三只手、课七十二五踩书、课三十五绿块、课四十六两张，仍等你发话再重出。</p>
  </div>
  <div class="folio">— 1 —</div>
</div>
"""


def main():
    build_css = B.read_css() + B.EXTRA_CSS + PH_CSS
    lessons = P.all_lessons()
    pages = [NOTE]
    for i, d in enumerate(lessons):
        B.img_tag = ph_tag
        folio = 2 * int(d['n'])
        pages.append(B.kid_page(d, folio))
        pages.append(B.adult_page(d, folio + 1))
    html = B.head('三字经·第七十一至八十六课·文案校订稿', '经', build_css) + ''.join(pages) + B.TAIL
    open(OUT, 'w', encoding='utf-8').write(html)
    print('written', OUT, len(html))


if __name__ == '__main__':
    main()
