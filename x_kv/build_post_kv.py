"""DEATH CLASS X投稿用 専用キービジュアル生成
4本のX投稿それぞれに合わせた焼き込み画像を生成する：
  1. announcement_16x9.png  — 初回告知（hero_main_split 背景）
  2. a_pitch_4x5.png        — A推し派閥煽り（赤体育館背景）
  3. b_pitch_4x5.png        — B推し派閥煽り（青体育館背景）
  4. last_call_4x5.png      — 締切間近（hero_main_split 背景）
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


def gradient_overlay(w, h, accent_alpha_top=0):
    """ダークグラデ。accent_alpha_top で上部に薄い色乗せもオプション可能"""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(h):
        ratio = y / h
        if ratio < 0.30:
            t = ratio / 0.30
            alpha = int(155 * (1 - t) + 70 * t)
        elif ratio < 0.70:
            t = (ratio - 0.30) / 0.40
            alpha = int(70 * (1 - t) + 90 * t)
        else:
            t = (ratio - 0.70) / 0.30
            alpha = int(90 * (1 - t) + 225 * t)
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
    """中央に水平アンダーラインを引く"""
    line_w = int(w * half_width)
    x1 = (w - line_w) // 2
    x2 = x1 + line_w
    draw.rectangle([(x1, y), (x2, y + height)], fill=color)


# ============================================================
# 1. 初回告知（16:9・両色 KV 背景）
# ============================================================
def render_announcement():
    w, h = 1200, 675
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    tag_font,   tag_ls   = fit_font("IMMERSIVE LAB  ×  NASU UTOPIA", CINZEL, int(w * 0.80), int(h * 0.025), ls_ratio=0.30)
    title_font, title_ls = fit_font("DEATH CLASS", CINZEL, int(w * 0.78), int(h * 0.14), ls_ratio=0.06)
    sub_font,  _ = fit_font("廃校で目覚める、1泊2日のデスゲーム。", JP_REG, int(w * 0.86), int(h * 0.034), ls_ratio=0.0)
    body_font, _ = fit_font("ただし開校されるのは、片方だけ。", JP_BOLD, int(w * 0.92), int(h * 0.054), ls_ratio=0.0)
    meta_font, _ = fit_font("投票期間：2026年5月2日 〜 5月31日", JP_REG, int(w * 0.78), int(h * 0.026), ls_ratio=0.0)

    draw_centered(draw, "IMMERSIVE LAB  ×  NASU UTOPIA", tag_font, int(h * 0.27),
                  (255, 255, 255, 220), w, ls_px=tag_ls)
    draw_centered(draw, "DEATH CLASS", title_font, int(h * 0.33),
                  (255, 255, 255, 255), w, ls_px=title_ls)
    draw_centered(draw, "廃校で目覚める、1泊2日のデスゲーム。", sub_font, int(h * 0.55),
                  (240, 240, 240, 240), w)
    draw_centered(draw, "ただし開校されるのは、片方だけ。", body_font, int(h * 0.64),
                  (255, 255, 255, 255), w)
    draw_centered(draw, "投票期間：2026年5月2日 〜 5月31日", meta_font, int(h * 0.86),
                  (220, 220, 220, 220), w)

    out = OUT / "announcement_16x9.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 2. A推し派閥煽り（4:5・赤体育館 KV 背景）
# ============================================================
def render_a_pitch():
    w, h = 1080, 1350
    src = Image.open(KV / "hero_a_v3_red_gym.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    RED = (200, 16, 46, 255)
    WHITE = (255, 255, 255, 255)

    tag_font, tag_ls = fit_font("VOTE  FOR  A", CINZEL, int(w * 0.5), int(h * 0.025), ls_ratio=0.40)
    title_font, title_ls = fit_font("DEATH", CINZEL, int(w * 0.7), int(h * 0.13), ls_ratio=0.08)
    accent_font, _ = fit_font("A案 / サバイバルゲーム", JP_BOLD, int(w * 0.86), int(h * 0.038), ls_ratio=0.0)
    big_font, _ = fit_font("勝ち残れ。", JP_BOLD, int(w * 0.86), int(h * 0.085), ls_ratio=0.0)
    body_font, _ = fit_font("知力・体力・判断力で、最後の一人へ。", JP_REG, int(w * 0.90), int(h * 0.030), ls_ratio=0.0)
    meta_font, _ = fit_font("投票期間：〜 2026年5月31日", JP_REG, int(w * 0.78), int(h * 0.022), ls_ratio=0.0)

    draw_centered(draw, "VOTE  FOR  A", tag_font, int(h * 0.18), RED, w, ls_px=tag_ls)

    title_line_h = int(title_font.size * 1.0)
    draw_centered(draw, "DEATH", title_font, int(h * 0.23),
                  WHITE, w, ls_px=title_ls)
    draw_centered(draw, "CLASS", title_font, int(h * 0.23) + title_line_h,
                  WHITE, w, ls_px=title_ls)

    draw_centered(draw, "A案 / サバイバルゲーム", accent_font, int(h * 0.51),
                  RED, w)
    draw_centered(draw, "勝ち残れ。", big_font, int(h * 0.58),
                  WHITE, w)
    draw_centered(draw, "知力・体力・判断力で、最後の一人へ。", body_font, int(h * 0.71),
                  (240, 240, 240, 240), w)
    draw_underline(draw, int(h * 0.79), w, RED, half_width=0.18, height=3)
    draw_centered(draw, "投票期間：〜 2026年5月31日", meta_font, int(h * 0.88),
                  (220, 220, 220, 220), w)

    out = OUT / "a_pitch_4x5.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 3. B推し派閥煽り（4:5・青体育館 KV 背景）
# ============================================================
def render_b_pitch():
    w, h = 1080, 1350
    src = Image.open(KV / "hero_b_v5_blue_gym.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    BLUE = (29, 58, 138, 255)
    LIGHT_BLUE = (140, 165, 230, 255)
    WHITE = (255, 255, 255, 255)

    tag_font, tag_ls = fit_font("VOTE  FOR  B", CINZEL, int(w * 0.5), int(h * 0.025), ls_ratio=0.40)
    title_font, title_ls = fit_font("DEATH", CINZEL, int(w * 0.7), int(h * 0.13), ls_ratio=0.08)
    accent_font, _ = fit_font("B案 / 物語没入体験", JP_BOLD, int(w * 0.86), int(h * 0.038), ls_ratio=0.0)
    big_font, _ = fit_font("演じきれ。", JP_BOLD, int(w * 0.86), int(h * 0.085), ls_ratio=0.0)
    body_font, _ = fit_font("あなたは、誰を助けますか。", JP_REG, int(w * 0.90), int(h * 0.034), ls_ratio=0.0)
    meta_font, _ = fit_font("投票期間：〜 2026年5月31日", JP_REG, int(w * 0.78), int(h * 0.022), ls_ratio=0.0)

    draw_centered(draw, "VOTE  FOR  B", tag_font, int(h * 0.18), LIGHT_BLUE, w, ls_px=tag_ls)

    title_line_h = int(title_font.size * 1.0)
    draw_centered(draw, "DEATH", title_font, int(h * 0.23),
                  WHITE, w, ls_px=title_ls)
    draw_centered(draw, "CLASS", title_font, int(h * 0.23) + title_line_h,
                  WHITE, w, ls_px=title_ls)

    draw_centered(draw, "B案 / 物語没入体験", accent_font, int(h * 0.51),
                  LIGHT_BLUE, w)
    draw_centered(draw, "演じきれ。", big_font, int(h * 0.58),
                  WHITE, w)
    draw_centered(draw, "あなたは、誰を助けますか。", body_font, int(h * 0.71),
                  (240, 240, 240, 240), w)
    draw_underline(draw, int(h * 0.79), w, LIGHT_BLUE, half_width=0.18, height=3)
    draw_centered(draw, "投票期間：〜 2026年5月31日", meta_font, int(h * 0.88),
                  (220, 220, 220, 220), w)

    out = OUT / "b_pitch_4x5.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


# ============================================================
# 4. ラスト押し（4:5・両色 KV 背景・ラスト訴求）
# ============================================================
def render_last_call():
    w, h = 1080, 1350
    src = Image.open(KV / "hero_main_split.png").convert("RGBA")
    img = crop_to_aspect(src, w, h)
    img = Image.alpha_composite(img, gradient_overlay(w, h))
    draw = ImageDraw.Draw(img)

    RED = (200, 16, 46, 255)
    WHITE = (255, 255, 255, 255)

    tag_font, tag_ls = fit_font("FINAL  DAYS", CINZEL, int(w * 0.55), int(h * 0.028), ls_ratio=0.40)
    title_font, title_ls = fit_font("DEATH", CINZEL, int(w * 0.7), int(h * 0.13), ls_ratio=0.08)
    big_font, _ = fit_font("締切間近。", JP_BOLD, int(w * 0.86), int(h * 0.080), ls_ratio=0.0)
    body_font, _ = fit_font("票数が少ない方は、消える。", JP_BOLD, int(w * 0.90), int(h * 0.040), ls_ratio=0.0)
    body2_font, _ = fit_font("あなたの一票が、片方を生かす。", JP_REG, int(w * 0.90), int(h * 0.030), ls_ratio=0.0)
    date_font, _ = fit_font("5月31日まで", JP_BOLD, int(w * 0.6), int(h * 0.045), ls_ratio=0.0)

    draw_centered(draw, "FINAL  DAYS", tag_font, int(h * 0.18), RED, w, ls_px=tag_ls)

    title_line_h = int(title_font.size * 1.0)
    draw_centered(draw, "DEATH", title_font, int(h * 0.23),
                  WHITE, w, ls_px=title_ls)
    draw_centered(draw, "CLASS", title_font, int(h * 0.23) + title_line_h,
                  WHITE, w, ls_px=title_ls)

    draw_centered(draw, "締切間近。", big_font, int(h * 0.54),
                  WHITE, w)
    draw_centered(draw, "票数が少ない方は、消える。", body_font, int(h * 0.66),
                  (250, 250, 250, 250), w)
    draw_centered(draw, "あなたの一票が、片方を生かす。", body2_font, int(h * 0.72),
                  (230, 230, 230, 230), w)
    draw_underline(draw, int(h * 0.80), w, RED, half_width=0.18, height=3)
    draw_centered(draw, "5月31日まで", date_font, int(h * 0.85),
                  WHITE, w)

    out = OUT / "last_call_4x5.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"saved: {out}")


if __name__ == "__main__":
    render_announcement()
    render_a_pitch()
    render_b_pitch()
    render_last_call()
