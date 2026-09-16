#!/usr/bin/env python3
"""
Gera o mapa mental de Orientação a Objetos em Python no estilo "hand-drawn"
usado como referência (sketch de Concorrência vs. Paralelismo da Enatielly):
caixas com cantos arredondados levemente rotacionadas, fonte de caligrafia,
conectores tracejados/pontilhados com seta aberta, elipses "Ideal para:",
anotações sublinhadas e legenda de cores no canto inferior esquerdo.

Cada uma das quatro caixas de categoria carrega também uma citação de página
do livro Learning Python (Lutz & Ascher, 6a ed.) -- ancorando o mapa em
mecanismos/trechos concretos do livro, não só em rótulos genéricos -- no
mesmo espírito do mapa mental dos 4 pilares (build_pillars.py).

Fontes embutidas como base64 (@font-face) a partir dos pacotes @fontsource,
porque o sandbox não tem acesso de rede a fonts.googleapis.com.

NOTA: este script é mantido aqui como referência/transparência de como o PNG
final (../mapa_mental_poo.png) foi gerado. Para rodá-lo de novo é preciso
antes gerar um "/tmp/fonts_pkg/fonts.css" com as fontes Caveat, Patrick Hand
e Space Mono em base64 (via `npm install @fontsource/caveat
@fontsource/patrick-hand @fontsource/space-mono` e concatenando os arquivos
"latin" + "latin-ext" de cada peso usado) — esse CSS não foi incluído aqui
por tamanho. O HTML já renderizado (oop_mindmap_sketch.html) está incluído
e pode ser aberto/printado diretamente.
"""

W = 1700
MIDX = W / 2  # 850

BLUE = "#2f6fed"
GREEN = "#2f9e52"
INK = "#262220"
PAPER = "#fffdf6"
CREAM = "#fdf3c9"
RED = "#d6402d"
MUTED = "#6b6255"

FONT_DISPLAY = "'CaveatLocal', cursive"
FONT_BODY = "'PatrickHandLocal', cursive"
FONT_CODE = "'SpaceMonoLocal', monospace"

# ---------------------------------------------------------------- layout math
# As caixas de categoria cresceram pra caber uma citação de página embaixo do
# título; as constantes abaixo derivam a altura total do canvas a partir
# dessas caixas maiores, em vez de um H fixo — assim nada se sobrepõe.
CAT_Y1 = 800            # topo da linha A de caixas de categoria
ROWA_H = 124            # título (2 linhas) + citação (até 2 linhas)
ROWB_GAP = 38           # vão entre a linha A e a linha B
CAT_Y2 = CAT_Y1 + ROWA_H + ROWB_GAP
ROWB_H = 124
APP_GAP = 40            # vão entre a linha B e o cluster "onde apliquei"
APP_Y = CAT_Y2 + ROWB_H + APP_GAP + 40
LEG_Y = APP_Y + 172
H = LEG_Y + 268

svg_parts = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rot(cx, cy, deg):
    return f' transform="rotate({deg} {cx} {cy})"' if deg else ""


def box(x, y, w, h, stroke, fill=PAPER, rx=16, sw=2.4, dash=None, deg=0):
    cx, cy = x + w / 2, y + h / 2
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    svg_parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"'
        f'{dash_attr}{rot(cx, cy, deg)}/>'
    )


def ellipse(cx, cy, rx_, ry_, stroke, fill=PAPER, dash="6 5", sw=2.2):
    svg_parts.append(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx_}" ry="{ry_}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}" stroke-dasharray="{dash}"/>'
    )


def text(x, y, s, size=20, color=INK, font=FONT_BODY, anchor="start", weight="400"):
    svg_parts.append(
        f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
        f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'
    )


def multiline(x, y, lines, size=19, color=INK, font=FONT_BODY, anchor="middle",
              weight="400", leading=1.28):
    dy0 = -(len(lines) - 1) * size * leading / 2
    for i, ln in enumerate(lines):
        text(x, y + dy0 + i * size * leading, ln, size=size, color=color, font=font,
             anchor=anchor, weight=weight)


def underline(x, y, s, size=17, color=INK, font=FONT_BODY, anchor="start"):
    text(x, y, s, size=size, color=color, font=font, anchor=anchor)
    approx_w = len(s) * size * 0.46
    x0 = {"start": x, "middle": x - approx_w / 2, "end": x - approx_w}[anchor]
    svg_parts.append(
        f'<line x1="{x0:.1f}" y1="{y + 5}" x2="{x0 + approx_w:.1f}" y2="{y + 5}" '
        f'stroke="{color}" stroke-width="1.5" stroke-linecap="round"/>'
    )


def bullets(x, y, lines, size=17, color=INK, anchor="start", gap=26):
    for i, ln in enumerate(lines):
        text(x, y + i * gap, ln, size=size, color=color, font=FONT_BODY, anchor=anchor)


ARROW_ID = 0


def _marker(color):
    global ARROW_ID
    ARROW_ID += 1
    mid = f"arrow{ARROW_ID}"
    svg_parts.append(
        f'<marker id="{mid}" viewBox="0 0 12 12" refX="10" refY="6" '
        f'markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
        f'<path d="M1,1 L10,6 L1,11" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round"/></marker>'
    )
    return mid


def line(x1, y1, x2, y2, color=INK, sw=2.2, dash=None, arrow=True, curve=None):
    mid = _marker(color) if arrow else None
    marker_attr = f' marker-end="url(#{mid})"' if arrow else ""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    if curve:
        cx1, cy1, cx2, cy2 = curve
        d = f"M {x1} {y1} C {cx1} {cy1}, {cx2} {cy2}, {x2} {y2}"
        svg_parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'
            f'{dash_attr}{marker_attr}/>'
        )
    else:
        svg_parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}"{dash_attr}{marker_attr}/>'
        )


# ================================================================ background
svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')
for gy in range(70, H, 50):
    svg_parts.append(
        f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="#000000" '
        f'stroke-opacity="0.02" stroke-width="1"/>'
    )

# ================================================================ row 1: outcomes
LX, RX = 330, MIDX + 520  # centers of left/right columns
box(LX - 280, 30, 560, 82, BLUE, rx=20, deg=-0.5)
multiline(LX, 62, ["Molde reaproveitável: comportamento"], size=18.5, color=BLUE)
multiline(LX, 86, ["definido em um só lugar"], size=18.5, color=BLUE)

box(RX - 280, 30, 560, 82, GREEN, rx=20, deg=0.5)
multiline(RX, 62, ["Mesma chamada, várias implementações"], size=18.5, color=GREEN)
multiline(RX, 86, ["diferentes por trás"], size=18.5, color=GREEN)

# ================================================================ row 2: ideal-para ellipses
ellipse(LX, 210, 165, 52, BLUE)
multiline(LX, 200, ["Ideal para:"], size=16.5, color=BLUE, weight="700")
multiline(LX, 224, ["modelar entidades do domínio"], size=15.5, color=BLUE)

ellipse(RX, 210, 165, 52, GREEN)
multiline(RX, 200, ["Ideal para:"], size=16.5, color=GREEN, weight="700")
multiline(RX, 224, ["interfaces flexíveis / plugáveis"], size=15.5, color=GREEN)

line(LX, 158, LX, 118, BLUE, sw=2)
line(RX, 158, RX, 118, GREEN, sw=2)

# underlined annotations, below each ellipse
underline(LX, 292, "Válido em qualquer linguagem OO", size=16.5, color=BLUE, anchor="middle")
underline(RX, 292, "Sintaxe e idiomas específicos do Python", size=16.5, color=GREEN, anchor="middle")

# ================================================================ row 3: title
text(MIDX, 372, "Vs.", size=30, color=INK, font=FONT_DISPLAY, anchor="middle", weight="700")
text(MIDX - 55, 372, "Fundamentos de POO", size=37, color=BLUE, font=FONT_DISPLAY,
     anchor="end", weight="700")
text(MIDX + 55, 372, "Peculiaridades em Python", size=37, color=GREEN, font=FONT_DISPLAY,
     anchor="start", weight="700")


# ================================================================ hub
box(MIDX - 105, 432, 210, 56, INK, fill=CREAM, rx=14)
text(MIDX, 466, "Em Python", size=23, color=INK, font=FONT_DISPLAY, anchor="middle", weight="700")

box(MIDX - 205, 502, 410, 98, INK, fill=CREAM, rx=16)
multiline(MIDX, 536, ["Tudo é objeto —"], size=21, color=INK, font=FONT_DISPLAY, weight="700")
multiline(MIDX, 564, ["até classes e funções!"], size=21, color=INK, font=FONT_DISPLAY, weight="700")
text(MIDX, 588, "type(obj) revela a classe por trás", size=14, color=MUTED, font=FONT_CODE,
     anchor="middle")

line(MIDX, 432, MIDX, 412, INK, sw=2)

line(MIDX - 205, 530, LX + 60, 540, BLUE, sw=2.2, dash="7 6",
     curve=(MIDX - 340, 530, LX + 220, 535))
line(MIDX + 205, 530, RX - 60, 540, GREEN, sw=2.2, dash="7 6",
     curve=(MIDX + 340, 530, RX - 220, 535))

# ================================================================ Y split below hub
line(MIDX - 40, 620, MIDX - 150, 668, INK, sw=2.2)
line(MIDX + 40, 620, MIDX + 150, 668, INK, sw=2.2)
text(MIDX - 150, 700, "Herança clássica", size=18, color=INK, font=FONT_BODY,
     anchor="middle", weight="700")
text(MIDX - 150, 722, "(“is-a”)", size=15.5, color=MUTED, font=FONT_BODY, anchor="middle")
text(MIDX + 150, 700, "Duck typing", size=18, color=INK, font=FONT_BODY,
     anchor="middle", weight="700")
text(MIDX + 150, 722, "(“comporta-se como”)", size=15.5, color=MUTED, font=FONT_BODY,
     anchor="middle")

multiline(MIDX, 756,
          ["Na dúvida entre herança e composição: composição favorece baixo",
           "acoplamento e facilita testes — bom critério pra guardar."],
          size=16, color=MUTED)

# ================================================================ category boxes — row A
box(MIDX - 480, CAT_Y1, 330, ROWA_H, BLUE, rx=18, deg=-0.4)
multiline(MIDX - 315, CAT_Y1 + 34, ["Encapsulamento"], size=19, color=BLUE, font=FONT_DISPLAY, weight="700")
multiline(MIDX - 315, CAT_Y1 + 62, ["& Abstração"], size=19, color=BLUE, font=FONT_DISPLAY, weight="700")
text(MIDX - 315, CAT_Y1 + 86, "Encapsulamento: cap. 28 (p. 684)", size=11.5, color=BLUE,
     font=FONT_CODE, anchor="middle", weight="600")
text(MIDX - 315, CAT_Y1 + 103, "Abstração: caps. 26 / 29 (p. 651, 722)", size=11.5, color=BLUE,
     font=FONT_CODE, anchor="middle", weight="600")

bullets(30, CAT_Y1 - 5, [
    "Atributos _protegido / __privado",
    "@property com validação",
    "Classe abstrata (ABC)",
    "+ @abstractmethod",
], color=BLUE, size=17, gap=26)
line(430, CAT_Y1 + 8, MIDX - 485, CAT_Y1 + 20, BLUE, sw=2, dash="4 5",
     curve=(620, CAT_Y1, 780, CAT_Y1 + 10))

box(MIDX + 150, CAT_Y1, 330, ROWA_H, GREEN, rx=18, deg=0.4)
multiline(MIDX + 315, CAT_Y1 + 34, ["Dunder Methods"], size=19, color=GREEN, font=FONT_DISPLAY, weight="700")
multiline(MIDX + 315, CAT_Y1 + 62, ["(Protocolos)"], size=19, color=GREEN, font=FONT_DISPLAY, weight="700")
text(MIDX + 315, CAT_Y1 + 86, "Learning Python, cap. 30 (p. 739)", size=11.5, color=GREEN,
     font=FONT_CODE, anchor="middle", weight="600")
text(MIDX + 315, CAT_Y1 + 103, "“Operator Overloading”", size=11.5, color=GREEN,
     font=FONT_CODE, anchor="middle", weight="600")

bullets(MIDX + 500, CAT_Y1 - 5, [
    "__repr__, __eq__",
    "__len__, __iter__",
    "Integra com built-ins:",
    "len(), for, ==",
], color=GREEN, size=17, gap=26)
line(MIDX + 480, CAT_Y1 + 20, MIDX + 495, CAT_Y1 + 12, GREEN, sw=2, dash="4 5")

# ================================================================ category boxes — row B
box(MIDX - 480, CAT_Y2, 330, ROWB_H, BLUE, rx=18, deg=0.4)
multiline(MIDX - 315, CAT_Y2 + 36, ["Herança &"], size=19, color=BLUE, font=FONT_DISPLAY, weight="700")
multiline(MIDX - 315, CAT_Y2 + 64, ["Polimorfismo"], size=19, color=BLUE, font=FONT_DISPLAY, weight="700")
text(MIDX - 315, CAT_Y2 + 87, "Herança: cap. 29 (p. 718)", size=11.5, color=BLUE,
     font=FONT_CODE, anchor="middle", weight="600")
text(MIDX - 315, CAT_Y2 + 104, "Polimorfismo: cap. 31 (p. 780)", size=11.5, color=BLUE,
     font=FONT_CODE, anchor="middle", weight="600")

bullets(30, CAT_Y2 - 8, [
    "Reuso de código (super())",
    "Relação Is-a",
    "MRO — Method Resolution Order",
    "Mesma interface, N formas",
], color=BLUE, size=17, gap=26)
line(430, CAT_Y2 + 8, MIDX - 485, CAT_Y2 + 25, BLUE, sw=2, dash="4 5",
     curve=(620, CAT_Y2, 780, CAT_Y2 + 15))


box(MIDX + 150, CAT_Y2, 330, ROWB_H, GREEN, rx=18, deg=-0.4)
multiline(MIDX + 315, CAT_Y2 + 36, ["Decorators &"], size=19, color=GREEN, font=FONT_DISPLAY, weight="700")
multiline(MIDX + 315, CAT_Y2 + 64, ["Composição"], size=19, color=GREEN, font=FONT_DISPLAY, weight="700")
text(MIDX + 315, CAT_Y2 + 87, "Learning Python, cap. 32 (p. 834, 837)", size=11.5, color=GREEN,
     font=FONT_CODE, anchor="middle", weight="600")
text(MIDX + 315, CAT_Y2 + 104, "composição: cap. 28 (p. 695)", size=11.5, color=GREEN,
     font=FONT_CODE, anchor="middle", weight="600")

# accents no vão entre as duas caixas da linha B: herança forte = alto
# acoplamento (vermelho), composição = baixo acoplamento (verde) — mesmas
# cores da legenda, apontando cada uma para a caixa que ela qualifica.
GAP_CX = MIDX  # 850, centro do vão entre as duas colunas
line(GAP_CX + 55, CAT_Y2 + 30, MIDX - 150 + 8, CAT_Y2 + 30, RED, sw=3)
text(GAP_CX, CAT_Y2 + 14, "alto acoplamento", size=14.5, color=RED, font=FONT_BODY, anchor="middle")

line(GAP_CX - 55, CAT_Y2 + 68, MIDX + 150 - 8, CAT_Y2 + 68, GREEN, sw=3)
text(GAP_CX, CAT_Y2 + 88, "baixo acoplamento", size=14.5, color=GREEN, font=FONT_BODY, anchor="middle")

bullets(MIDX + 500, CAT_Y2 - 8, [
    "@classmethod / @staticmethod",
    "@dataclass",
    "Composição > Herança (Has-a)",
    'Ex.: PreProcessador “tem um”',
    "ColumnTransformer",
], color=GREEN, size=17, gap=25)
line(MIDX + 480, CAT_Y2 + 25, MIDX + 495, CAT_Y2 + 15, GREEN, sw=2, dash="4 5")

# ================================================================ applied-in-my-case cluster
ellipse(MIDX, APP_Y, 175, 50, INK, fill=CREAM, dash="5 4")
multiline(MIDX, APP_Y - 8, ["Onde apliquei"], size=16.5, color=INK, weight="700")
multiline(MIDX, APP_Y + 15, ["neste case"], size=15.5, color=INK)

box(MIDX - 175, APP_Y + 62, 350, 82, BLUE, rx=16)
multiline(MIDX, APP_Y + 92, ["Caso 1 — Monitoramento"], size=16, color=BLUE, weight="700")
multiline(MIDX, APP_Y + 116, ["Oceanográfico (POO pura)"], size=16, color=BLUE)
line(MIDX, APP_Y + 50, MIDX, APP_Y + 62, BLUE, sw=2, dash="4 4")

# ================================================================ legend
text(40, LEG_Y, "Legenda:", size=17.5, color=INK, font=FONT_BODY, weight="700")
line(40, LEG_Y + 34, 105, LEG_Y + 34, GREEN, sw=3.6, arrow=True)
text(118, LEG_Y + 40, "Baixo acoplamento (composição)", size=16.5, color=INK, font=FONT_BODY)
line(40, LEG_Y + 68, 105, LEG_Y + 68, RED, sw=3.6, arrow=True)
text(118, LEG_Y + 74, "Alto acoplamento (herança forte / rígida)", size=16.5, color=INK, font=FONT_BODY)

# mecanismo concreto por trás de "Herança clássica" (row do Y-split lá em
# cima): toda busca de atributo em Python — a peça que efetivamente une as
# quatro categorias acima — passa por object.attribute subindo a árvore de
# classes. Citado aqui embaixo, perto da legenda, pra não brigar por espaço
# com o Y-split.
text(40, LEG_Y + 112, "Por trás de toda herança/busca de método: uma expressão —",
     size=15, color=MUTED, font=FONT_BODY)
text(40, LEG_Y + 136, "object.attribute sobe a árvore de classes até achar o atributo",
     size=13.5, color=INK, font=FONT_CODE, weight="600")
text(40, LEG_Y + 158, "(Learning Python, cap. 26, “OOP: The Big Picture”, p. 651)",
     size=13, color=MUTED, font=FONT_CODE)

# adendo: numa passagem específica (cap. 31, p. 779) o próprio livro resume a
# POO em Python em só 3 ideias — sem abstração como item separado. Não muda
# o enquadramento de 4 pilares usado neste estudo (convenção didática mais
# comum), mas é uma nuance que vale registrar aqui também.
text(40, LEG_Y + 194, "Adendo: em cap. 31, “Python and OOP” (p. 779), o livro resume a POO em",
     size=15, color=MUTED, font=FONT_BODY)
text(40, LEG_Y + 216, "Python em 3 ideias — herança, polimorfismo, encapsulamento —, sem abstração",
     size=13.5, color=INK, font=FONT_CODE, weight="600")
text(40, LEG_Y + 236, "como item à parte; aqui uso o enquadramento didático de 4 pilares.",
     size=13.5, color=INK, font=FONT_CODE, weight="600")

text(W - 40, H - 24, "Enatielly Goes — estudo de POO em Python", size=13.5, color="#9a9184",
     font=FONT_BODY, anchor="end")

svg_body = "\n".join(svg_parts)

with open("/tmp/fonts_pkg/fonts.css", "r", encoding="utf-8") as f:
    fonts_css = f.read()

html = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Mapa mental — Orientação a Objetos em Python</title>
<style>
{fonts_css}
html,body {{ margin:0; padding:0; background:{PAPER}; }}
#stage {{ width:{W}px; height:{H}px; }}
svg {{ display:block; }}
</style>
</head>
<body>
<div id="stage">
<svg id="mindmap" width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Mapa mental de Orientação a Objetos em Python, comparando fundamentos universais de POO com peculiaridades específicas do Python, com citações de página do livro Learning Python em cada categoria, no estilo desenhado à mão.">
{svg_body}
</svg>
</div>
</body>
</html>
"""

with open("/tmp/oop_repo/assets/mindmap_source/oop_mindmap_sketch.html", "w", encoding="utf-8") as f:
    f.write(html)

print("done", W, H)
