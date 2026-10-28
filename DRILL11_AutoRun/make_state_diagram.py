# Boy 상태 다이어그램(state_diagram.png) 생성 스크립트 - 실행: python make_state_diagram.py
import math
import os

from PIL import Image, ImageDraw, ImageFont

S = 2  # 2배로 그린 뒤 줄여서 계단 현상을 없앤다
W, H = 1400, 900
FONT_PATH = 'C:/Windows/Fonts/malgunbd.ttf'
FONT_PATH_REGULAR = 'C:/Windows/Fonts/malgun.ttf'

BG = (255, 255, 255)
LINE = (60, 60, 70)
STATE_FILL = (232, 240, 254)
STATE_LINE = (66, 103, 178)
NEW_FILL = (255, 236, 220)
NEW_LINE = (220, 100, 30)
LABEL = (30, 30, 30)

img = Image.new('RGB', (W * S, H * S), BG)
d = ImageDraw.Draw(img)
title_font = ImageFont.truetype(FONT_PATH, 30 * S)
name_font = ImageFont.truetype(FONT_PATH, 26 * S)
desc_font = ImageFont.truetype(FONT_PATH_REGULAR, 15 * S)
label_font = ImageFont.truetype(FONT_PATH, 17 * S)

BOX_W, BOX_H = 230, 110
# 상태 이름: (중심 x, 중심 y, 설명, 새로 추가된 상태인지)
states = {
    'IDLE': (600, 260, '제자리 대기\n5초 타이머', False),
    'SLEEP': (170, 260, '누워서 잠자기', False),
    'RUN': (1110, 260, '방향키 방향으로 이동\n속도 10', False),
    'AUTORUN': (600, 700, '자동 무적 런 (속도 x2, 크기 x2)\n화면 끝에서 자동 방향 전환\n5초 타이머', True),
}


def p(x, y):
    return x * S, y * S


def box(name):
    x, y, _, _ = states[name]
    w = BOX_W + (90 if name == 'AUTORUN' else 0)
    h = BOX_H + (24 if name == 'AUTORUN' else 0)
    return x - w / 2, y - h / 2, x + w / 2, y + h / 2


def draw_state(name):
    x, y, desc, is_new = states[name]
    l, t, r, b = box(name)
    d.rounded_rectangle([p(l, t), p(r, b)], radius=22 * S,
                        fill=NEW_FILL if is_new else STATE_FILL,
                        outline=NEW_LINE if is_new else STATE_LINE, width=4 * S)
    d.text(p(x, t + 28), name, font=name_font, fill=LABEL, anchor='mm')
    d.multiline_text(p(x, (t + 50 + b) / 2), desc, font=desc_font, fill=LABEL, anchor='mm', align='center', spacing=3 * S)


def arrow_head(x1, y1, x2, y2, color=LINE):
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 16
    pts = [(x2, y2),
           (x2 - size * math.cos(ang - 0.4), y2 - size * math.sin(ang - 0.4)),
           (x2 - size * math.cos(ang + 0.4), y2 - size * math.sin(ang + 0.4))]
    d.polygon([p(*q) for q in pts], fill=color)


def arrow(points, label, label_pos, color=LINE):
    d.line([p(*q) for q in points], fill=color, width=3 * S, joint='curve')
    arrow_head(*points[-2], *points[-1], color=color)
    lx, ly = label_pos
    tb = d.textbbox(p(lx, ly), label, font=label_font, anchor='mm')
    d.rectangle([tb[0] - 6 * S, tb[1] - 4 * S, tb[2] + 6 * S, tb[3] + 4 * S], fill=BG)
    d.text(p(lx, ly), label, font=label_font, fill=color, anchor='mm')


d.text(p(W / 2, 40), 'Boy 상태 다이어그램 (DRILL11 - AutoRun)', font=title_font, fill=LABEL, anchor='mm')

# 시작 상태
d.ellipse([p(588, 143), p(612, 167)], fill=LINE)
arrow([(600, 167), (600, box('IDLE')[1])], '', (0, 0))

i_l, i_t, i_r, i_b = box('IDLE')
s_l, s_t, s_r, s_b = box('SLEEP')
r_l, r_t, r_r, r_b = box('RUN')
a_l, a_t, a_r, a_b = box('AUTORUN')

# IDLE <-> SLEEP
arrow([(i_l, 235), (s_r, 235)], 'TIME_OUT (5초)', (385, 210))
arrow([(s_r, 290), (i_l, 290)], 'SPACE down', (385, 315))

# IDLE <-> RUN
arrow([(i_r, 235), (r_l, 235)], '← / → down', (855, 210))
arrow([(r_l, 290), (i_r, 290)], '← / → up (모든 방향키 뗌)', (855, 315))

# SLEEP -> RUN (위로 돌아감)
arrow([(170, s_t), (170, 100), (1110, 100), (1110, r_t)], '← / → down', (300, 100))

# IDLE <-> AUTORUN (새로 추가된 전이)
arrow([(560, i_b), (560, a_t)], "'a' down", (490, 475), color=NEW_LINE)
arrow([(640, a_t), (640, i_b)], 'TIME_OUT (5초)', (730, 475), color=NEW_LINE)

# AUTORUN -> RUN
arrow([(a_r, 700), (1110, 700), (1110, r_b)], '← / → down (무적 런 취소)', (930, 675), color=NEW_LINE)

for n in states:
    draw_state(n)

# 범례
d.rounded_rectangle([p(40, 820), p(70, 845)], radius=6 * S, fill=NEW_FILL, outline=NEW_LINE, width=3 * S)
d.text(p(80, 832), '새로 추가한 상태 / 전이', font=desc_font, fill=LABEL, anchor='lm')

# 저장소 루트(이 스크립트의 상위 폴더)에 저장한다
img.resize((W, H), Image.LANCZOS).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'state_diagram.png'))
