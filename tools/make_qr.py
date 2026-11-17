# -*- coding: utf-8 -*-
"""生成短链二维码与群发卡片：docs/qr-apk.png、docs/qr-card.png。"""
import os
import segno
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
URL = 'https://q1z2q3-debug.github.io/daokedao-sanzijing/dl/'
INK = (47, 42, 36)
OCHRE = (162, 80, 59)
PAPER = (251, 247, 236)

SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'


def font(path, size):
    for p in (path, '/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=0)
    return ImageFont.load_default()


def qr_png(path, scale=16):
    q = segno.make(URL, error='m')
    q.save(path, scale=scale, border=3, dark=INK, light=PAPER)
    return q


def card(path, qr_path):
    W, H = 1080, 1440
    im = Image.new('RGB', (W, H), (239, 231, 216))
    d = ImageDraw.Draw(im)
    # 纸面
    d.rectangle([56, 56, W - 56, H - 56], fill=PAPER, outline=(224, 213, 189))
    d.rectangle([70, 70, W - 70, H - 70], outline=(162, 80, 59, 90))
    # 顶部赭条
    d.rectangle([56, 56, W - 56, 96], fill=OCHRE)
    t = font(SERIF, 30)
    d.text((W // 2, 78), '润 泽 说  ·  少 儿 启 蒙 国 学', font=t, fill=PAPER, anchor='mm')

    d.text((W // 2, 210), '三 字 经', font=font(SERIF, 76), fill=INK, anchor='mm')
    d.text((W // 2, 280), '安卓离线阅读版 · v3.2', font=font(SANS, 28), fill=(123, 110, 92), anchor='mm')
    d.text((W // 2, 322), '201 课 · 402 图 · 一课两页', font=font(SANS, 26), fill=(123, 110, 92), anchor='mm')

    qr = Image.open(qr_path).convert('RGB')
    qs = 620
    qr = qr.resize((qs, qs), Image.LANCZOS)
    im.paste(qr, ((W - qs) // 2, 400))
    d.rectangle([(W - qs) // 2 - 14, 386, (W + qs) // 2 + 14, 400 + qs + 14], outline=(224, 213, 189))

    d.text((W // 2, 1105), '扫码即下 · 手机浏览器打开更稳', font=font(SANS, 30), fill=OCHRE, anchor='mm')
    d.text((W // 2, 1160), '22.3 MB ｜ Android 5.0+ ｜ 全离线 无权限 免费', font=font(SANS, 24), fill=(123, 110, 92), anchor='mm')
    d.text((W // 2, 1218), 'q1z2q3-debug.github.io/daokedao-sanzijing/dl/', font=font(SANS, 20), fill=(138, 128, 116), anchor='mm')

    d.line([(200, 1280), (W - 200, 1280)], fill=(224, 213, 189))
    d.text((W // 2, 1330), '一句一故事　一图一世界', font=font(SERIF, 26), fill=(107, 97, 82), anchor='mm')
    im.save(path, quality=92)


if __name__ == '__main__':
    qp = os.path.join(DOCS, 'qr-apk.png')
    q = qr_png(qp)
    card(os.path.join(DOCS, 'qr-card.png'), qp)
    print('qr', URL, os.path.getsize(qp) // 1024, 'KB; card', os.path.getsize(os.path.join(DOCS, 'qr-card.png')) // 1024, 'KB')
