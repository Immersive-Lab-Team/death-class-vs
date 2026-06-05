"""DEATH CLASS 一般販売開始 専用キービジュアル生成
既存 build_post_kv.py のトンマナ（Cinzel + 凸版文久見出し明朝 + ダークグラデ）を踏襲。
  1. onsale_16x9.png  — X単発投稿用（1200x675）
  2. onsale_4x5.png   — フィード縦長補助（1080x1350）
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
KV   = ROOT / "kv"
OUT  = ROOT / "x_kv"
OUT.mkdir(exist_ok=True)

CINZEL  = "/tmp/Cinzel.ttf"
JP_BOLD = "/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/05e0acee5c6c187e563c708cb4e4dcac431f7f1a.asset/AssetData/ToppanBunkyuMidashiMinchoStdN-ExtraBold.otf"
JP_REG  = "/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/c23c376fbb89978a2a0827cb91beae9d94448499.asset/AssetData/ToppanBunkyuMinchoPr6N-Regular.otf"
if not os.path.exists(JP_BOLD):
    JP_BOLD = "/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/acac607170ecaf9d5b40c9f86a6568dc1c0be035.asset/AssetData/YuMincho.ttc"
if not os.path.exists(JP_REG):
    JP_REG = JP_BOLD

GOLD = (197, 165, 114, 255)  # 上品なゴールド（ON SALE アクセント）


def crop_to_aspect(im, w, h):
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


def gradient_overlay(w, h):
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(h):
        ratio = y / h
        if ratio < 0.30:
            t = ratio / 0.30
            alpha = int(165 * (1 - t) + 80 * t)
        elif ratio < 0.66:
            t = (ratio - 0.30) / 0.36
            alpha = int(80 * (1 - t) + 105 * t)
        else:
            t = (ratio - 0.66) / 0.34
            alpha = int(105 * (1 - t) + 235 * t)
        od.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    return overlay


_meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def text_metrics(text, font, ls_px):
    widths = []
    for ch in text:
        bb = _meas.textbbox((0, 0), ch, font=font)
        widths.append(bb[2] - bb[0])
    total = sum(widths) + ls_px * max(0, len(text) - 1)
    return total, widths


def fit_font(text, font_path, max_width, max_size, ls_ratio=0.0):
    size = max_size
    while size >= 12:
        font = ImageFont.truetype(font_path, size)
        ls_px = int(size * ls_ratio)
        total, _ = text_metrics(text, font, ls_px)
        if total <= max_width:
            return font, ls_px
        size -= 2
    return ImageFont.truetype(font_path, 12), 0


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


def draw_underline(draw, y, w, color, half_width=0.3, height=2):
    line_w = int(w * half_width)
    x1 = (w - line_w) // 2
    x2 = x1 + line_w
    draw.rectangle([(x1, y), (x2, y + height)], fill=color)


def draw_pill(draw, cx, y, text, font, fill_text, fill_bg, pad_x, pad_y):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x1 = cx - tw // 2 - pad_x
    x2 = cx + tw // 2 + pad_x
    y1 = y
    y2 = y + th + pad_y * 2
    r = (y2 - y1) // 2
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=r, fill=fill_bg)
    draw.text((cx - tw // 2, y1 + pad_y - bb[1]), text, font=font, fill=fill_text)
    return y2


# ============================================================
# 1. 一般販売開始（16:9）
# ============================================================
def render_onsale_16x9():
    w, h = 1200, 675
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    tag_font,   tag_ls   = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.80), int(h * 0.024), ls_ratio=0.30)
    title_font, title_ls = fit_font("DEATH CLASS", CINZEL, int(w * 0.78), int(h * 0.14), ls_ratio=0.06)
    sub_font,  _ = fit_font("廃校で目覚める、1泊2日のデスゲーム。", JP_REG, int(w * 0.86), int(h * 0.034), ls_ratio=0.0)
    pill_font    = ImageFont.truetype(CINZEL, int(h * 0.040))
    date_font, _ = fit_font("2026年6月8日 19:00　一般販売開始", JP_BOLD, int(w * 0.90), int(h * 0.050), ls_ratio=0.0)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, int(h * 0.20),
                  (255, 255, 255, 220), w, ls_px=tag_ls)
    draw_centered(draw, "DEATH CLASS", title_font, int(h * 0.26),
                  (255, 255, 255, 255), w, ls_px=title_ls)
    draw_centered(draw, "廃校で目覚める、1泊2日のデスゲーム。", sub_font, int(h * 0.49),
                  (238, 238, 238, 238), w)

    draw_pill(draw, w // 2, int(h * 0.62), "TICKETS ON SALE", pill_font,
              (18, 18, 18, 255), GOLD, pad_x=int(w * 0.022), pad_y=int(h * 0.012))
    draw_centered(draw, "2026年6月8日 19:00　一般販売開始", date_font, int(h * 0.78),
                  (255, 255, 255, 255), w)

    out = OUT / "onsale_16x9.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 2. 一般販売開始（4:5）
# ============================================================
def render_onsale_4x5():
    w, h = 1080, 1350
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    tag_font, tag_ls = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.82), int(h * 0.020), ls_ratio=0.26)
    title_font, title_ls = fit_font("DEATH", CINZEL, int(w * 0.70), int(h * 0.13), ls_ratio=0.08)
    sub_font, _ = fit_font("廃校で目覚める、1泊2日のデスゲーム。", JP_REG, int(w * 0.90), int(h * 0.030), ls_ratio=0.0)
    pill_font = ImageFont.truetype(CINZEL, int(h * 0.034))
    date_font, _ = fit_font("2026年6月8日 19:00", JP_BOLD, int(w * 0.80), int(h * 0.052), ls_ratio=0.0)
    label_font, _ = fit_font("一般販売開始", JP_BOLD, int(w * 0.80), int(h * 0.046), ls_ratio=0.10)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, int(h * 0.15),
                  (255, 255, 255, 220), w, ls_px=tag_ls)

    title_line_h = int(title_font.size * 1.0)
    draw_centered(draw, "DEATH", title_font, int(h * 0.20), (255, 255, 255, 255), w, ls_px=title_ls)
    draw_centered(draw, "CLASS", title_font, int(h * 0.20) + title_line_h, (255, 255, 255, 255), w, ls_px=title_ls)

    draw_centered(draw, "廃校で目覚める、1泊2日のデスゲーム。", sub_font, int(h * 0.49),
                  (238, 238, 238, 238), w)

    draw_pill(draw, w // 2, int(h * 0.60), "TICKETS ON SALE", pill_font,
              (18, 18, 18, 255), GOLD, pad_x=int(w * 0.030), pad_y=int(h * 0.010))
    draw_centered(draw, "2026年6月8日 19:00", date_font, int(h * 0.71),
                  (255, 255, 255, 255), w)
    draw_centered(draw, "一般販売開始", label_font, int(h * 0.79),
                  GOLD, w, ls_px=int(int(h * 0.046) * 0.10))
    draw_underline(draw, int(h * 0.87), w, GOLD, half_width=0.18, height=3)

    out = OUT / "onsale_4x5.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 3. 只今より 一般販売開始（16:9・NOW版）
# ============================================================
def render_now_16x9():
    w, h = 1200, 675
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    tag_font,   tag_ls   = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.80), int(h * 0.024), ls_ratio=0.30)
    title_font, title_ls = fit_font("DEATH CLASS", CINZEL, int(w * 0.78), int(h * 0.14), ls_ratio=0.06)
    sub_font,  _ = fit_font("廃校で目覚める、1泊2日のデスゲーム。", JP_REG, int(w * 0.86), int(h * 0.034), ls_ratio=0.0)
    pill_font    = ImageFont.truetype(CINZEL, int(h * 0.040))
    date_font, _ = fit_font("只今より、一般販売開始。", JP_BOLD, int(w * 0.90), int(h * 0.058), ls_ratio=0.04)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, int(h * 0.20),
                  (255, 255, 255, 220), w, ls_px=tag_ls)
    draw_centered(draw, "DEATH CLASS", title_font, int(h * 0.26),
                  (255, 255, 255, 255), w, ls_px=title_ls)
    draw_centered(draw, "廃校で目覚める、1泊2日のデスゲーム。", sub_font, int(h * 0.49),
                  (238, 238, 238, 238), w)

    draw_pill(draw, w // 2, int(h * 0.62), "NOW ON SALE", pill_font,
              (18, 18, 18, 255), GOLD, pad_x=int(w * 0.024), pad_y=int(h * 0.012))
    draw_centered(draw, "只今より、一般販売開始。", date_font, int(h * 0.78),
                  (255, 255, 255, 255), w, ls_px=int(int(h * 0.058) * 0.04))

    out = OUT / "onsale_now_16x9.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 4. 只今より 一般販売開始（4:5・NOW版）
# ============================================================
def render_now_4x5():
    w, h = 1080, 1350
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    tag_font, tag_ls = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.82), int(h * 0.020), ls_ratio=0.26)
    title_font, title_ls = fit_font("DEATH", CINZEL, int(w * 0.70), int(h * 0.13), ls_ratio=0.08)
    sub_font, _ = fit_font("廃校で目覚める、1泊2日のデスゲーム。", JP_REG, int(w * 0.90), int(h * 0.030), ls_ratio=0.0)
    pill_font = ImageFont.truetype(CINZEL, int(h * 0.034))
    big_font, _ = fit_font("只今より", JP_BOLD, int(w * 0.70), int(h * 0.075), ls_ratio=0.06)
    label_font, _ = fit_font("一般販売開始", JP_BOLD, int(w * 0.80), int(h * 0.050), ls_ratio=0.10)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, int(h * 0.15),
                  (255, 255, 255, 220), w, ls_px=tag_ls)

    title_line_h = int(title_font.size * 1.0)
    draw_centered(draw, "DEATH", title_font, int(h * 0.20), (255, 255, 255, 255), w, ls_px=title_ls)
    draw_centered(draw, "CLASS", title_font, int(h * 0.20) + title_line_h, (255, 255, 255, 255), w, ls_px=title_ls)

    draw_centered(draw, "廃校で目覚める、1泊2日のデスゲーム。", sub_font, int(h * 0.49),
                  (238, 238, 238, 238), w)

    draw_pill(draw, w // 2, int(h * 0.60), "NOW ON SALE", pill_font,
              (18, 18, 18, 255), GOLD, pad_x=int(w * 0.030), pad_y=int(h * 0.010))
    draw_centered(draw, "只今より", big_font, int(h * 0.70),
                  (255, 255, 255, 255), w, ls_px=int(int(h * 0.075) * 0.06))
    draw_centered(draw, "一般販売開始", label_font, int(h * 0.79),
                  GOLD, w, ls_px=int(int(h * 0.050) * 0.10))
    draw_underline(draw, int(h * 0.87), w, GOLD, half_width=0.18, height=3)

    out = OUT / "onsale_now_4x5.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 5. 今夏告知 × 一般販売（16:9 / 1600x900・X最適 / メイン）
# ============================================================
def render_summer_16x9():
    w, h = 1600, 900
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    tag_font,  tag_ls   = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.74), int(h * 0.026), ls_ratio=0.32)
    title_font, title_ls = fit_font("DEATH CLASS", CINZEL, int(w * 0.74), int(h * 0.145), ls_ratio=0.07)
    season_font, season_ls = fit_font("2026  SUMMER", CINZEL, int(w * 0.50), int(h * 0.030), ls_ratio=0.40)
    hook_font, _ = fit_font("この夏、廃校が開く。", JP_BOLD, int(w * 0.80), int(h * 0.066), ls_ratio=0.06)
    pill_font    = ImageFont.truetype(CINZEL, int(h * 0.038))
    sale_font, _ = fit_font("只今より、一般販売開始。", JP_REG, int(w * 0.70), int(h * 0.036), ls_ratio=0.04)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, int(h * 0.155),
                  (255, 255, 255, 220), w, ls_px=tag_ls)
    draw_centered(draw, "DEATH CLASS", title_font, int(h * 0.215),
                  (255, 255, 255, 255), w, ls_px=title_ls)
    draw_centered(draw, "2026  SUMMER", season_font, int(h * 0.455),
                  GOLD, w, ls_px=season_ls)
    draw_centered(draw, "この夏、廃校が開く。", hook_font, int(h * 0.525),
                  (255, 255, 255, 255), w, ls_px=int(int(h * 0.066) * 0.06))

    draw_pill(draw, w // 2, int(h * 0.72), "NOW ON SALE", pill_font,
              (18, 18, 18, 255), GOLD, pad_x=int(w * 0.020), pad_y=int(h * 0.011))
    draw_centered(draw, "只今より、一般販売開始。", sale_font, int(h * 0.86),
                  (245, 245, 245, 245), w, ls_px=int(int(h * 0.036) * 0.04))

    out = OUT / "summer_onsale_16x9.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


if __name__ == "__main__":
    render_onsale_16x9()
    render_onsale_4x5()
    render_now_16x9()
    render_now_4x5()
    render_summer_16x9()
