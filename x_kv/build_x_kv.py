"""DEATH CLASS X投稿用キービジュアル生成
LP の FV と同じ構成（背景体育館KV + ダークグラデ + 明朝/Cinzel テキスト）を、
X 投稿用に焼き込んだ静止画として書き出す。

縦長フォーマット（4:5・9:16）では DEATH / CLASS を2行に分けて配置。
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "kv" / "hero_main_split.png"
OUT_DIR = ROOT / "x_kv"
OUT_DIR.mkdir(exist_ok=True)

CINZEL = "/tmp/Cinzel.ttf"
JP_BOLD = "/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/05e0acee5c6c187e563c708cb4e4dcac431f7f1a.asset/AssetData/ToppanBunkyuMidashiMinchoStdN-ExtraBold.otf"
JP_REG  = "/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/c23c376fbb89978a2a0827cb91beae9d94448499.asset/AssetData/ToppanBunkyuMinchoPr6N-Regular.otf"

if not os.path.exists(JP_BOLD):
    JP_BOLD = "/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/acac607170ecaf9d5b40c9f86a6568dc1c0be035.asset/AssetData/YuMincho.ttc"
if not os.path.exists(JP_REG):
    JP_REG = JP_BOLD


def crop_to_aspect(im: Image.Image, w: int, h: int) -> Image.Image:
    src_aspect = im.width / im.height
    tgt_aspect = w / h
    if src_aspect > tgt_aspect:
        new_w = int(im.height * tgt_aspect)
        x = (im.width - new_w) // 2
        im = im.crop((x, 0, x + new_w, im.height))
    else:
        new_h = int(im.width / tgt_aspect)
        y = (im.height - new_h) // 2
        im = im.crop((0, y, im.width, y + new_h))
    return im.resize((w, h), Image.LANCZOS)


def gradient_overlay(w: int, h: int) -> Image.Image:
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(h):
        ratio = y / h
        if ratio < 0.30:
            t = ratio / 0.30
            alpha = int(140 * (1 - t) + 60 * t)
        elif ratio < 0.70:
            t = (ratio - 0.30) / 0.40
            alpha = int(60 * (1 - t) + 75 * t)
        else:
            t = (ratio - 0.70) / 0.30
            alpha = int(75 * (1 - t) + 215 * t)
        od.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    return overlay


_meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def text_metrics(text: str, font: ImageFont.FreeTypeFont, ls_px: int):
    widths = []
    for ch in text:
        bb = _meas.textbbox((0, 0), ch, font=font)
        widths.append(bb[2] - bb[0])
    total = sum(widths) + ls_px * max(0, len(text) - 1)
    return total, widths


def fit_font(text: str, font_path: str, max_width: int, max_size: int, ls_ratio: float = 0.0):
    size = max_size
    while size >= 14:
        font = ImageFont.truetype(font_path, size)
        ls_px = int(size * ls_ratio)
        total, _ = text_metrics(text, font, ls_px)
        if total <= max_width:
            return font, ls_px
        size -= 2
    return ImageFont.truetype(font_path, 14), 0


def draw_centered(draw, text, font, y, fill, w, ls_px=0):
    if ls_px == 0:
        bb = draw.textbbox((0, 0), text, font=font)
        tw = bb[2] - bb[0]
        draw.text(((w - tw) // 2, y), text, fill=fill, font=font)
        return
    total, widths = text_metrics(text, font, ls_px)
    x = (w - total) // 2
    for ch, cw in zip(text, widths):
        draw.text((x, y), ch, fill=fill, font=font)
        x += cw + ls_px


def render(name: str, w: int, h: int, two_line_title: bool = None):
    if two_line_title is None:
        # 縦長 (h > w * 1.05) は2行タイトル
        two_line_title = h > w * 1.05

    src = Image.open(SRC).convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    # タイトル：縦長は2行 (DEATH / CLASS)、横長は1行
    if two_line_title:
        title_lines = ["DEATH", "CLASS"]
        cap_title = int(h * 0.14)
        title_max_w = int(w * 0.72)
    else:
        title_lines = ["DEATH CLASS"]
        cap_title = int(h * 0.13)
        title_max_w = int(w * 0.78)

    longest = max(title_lines, key=len)
    title_font, title_ls = fit_font(longest, CINZEL, title_max_w, cap_title, ls_ratio=0.06)

    cap_tag   = int(h * 0.022)
    cap_sub   = int(h * 0.030)
    cap_q     = int(h * 0.052)
    cap_meta  = int(h * 0.024)

    tag_font,   tag_ls = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.80), cap_tag, ls_ratio=0.30)
    sub_font,  _ = fit_font("廃校で目覚める、1泊2日のデスゲーム。", JP_REG, int(w * 0.86), cap_sub, ls_ratio=0.0)
    q_font,    _ = fit_font("どちらの DEATH CLASS で目覚めたい？", JP_BOLD, int(w * 0.92), cap_q, ls_ratio=0.0)
    meta_font, _ = fit_font("投票期間：2026年5月2日 〜 5月31日", JP_REG, int(w * 0.78), cap_meta, ls_ratio=0.0)

    # 縦位置
    if two_line_title:
        y_tag         = int(h * 0.20)
        y_title_start = int(h * 0.26)
        y_sub         = int(h * 0.62)
        y_q           = int(h * 0.71)
        y_meta        = int(h * 0.88)
    else:
        y_tag         = int(h * 0.30)
        y_title_start = int(h * 0.36)
        y_sub         = int(h * 0.57)
        y_q           = int(h * 0.65)
        y_meta        = int(h * 0.86)

    title_line_h = int(title_font.size * 1.0)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, y_tag,
                  (255, 255, 255, 220), w, ls_px=tag_ls)

    for i, line in enumerate(title_lines):
        draw_centered(draw, line, title_font, y_title_start + i * title_line_h,
                      (255, 255, 255, 255), w, ls_px=title_ls)

    draw_centered(draw, "廃校で目覚める、1泊2日のデスゲーム。", sub_font, y_sub,
                  (240, 240, 240, 240), w)
    draw_centered(draw, "どちらの DEATH CLASS で目覚めたい？", q_font, y_q,
                  (255, 255, 255, 255), w)
    draw_centered(draw, "投票期間：2026年5月2日 〜 5月31日", meta_font, y_meta,
                  (220, 220, 220, 220), w)

    out = OUT_DIR / f"x_kv_{name}.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out} ({w}×{h}) {'2-line title' if two_line_title else '1-line title'}")


if __name__ == "__main__":
    render("16x9", 1200, 675)   # X 標準
    render("1x1",  1080, 1080)  # SNS 汎用
    render("4x5",  1080, 1350)  # 縦長・タイムライン占有大
    render("9x16",  720, 1280)  # ストーリーズ
