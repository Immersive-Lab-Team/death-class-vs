# DEATH CLASS LP

廃校で目覚める、1泊2日のデスゲーム。
A案 SURVIVOR / B案 DRAMA の VS 投票キャンペーン LP。

- IMMERSIVE LAB × NASU UTOPIA
- 投票期間：2026年5月2日 〜 5月31日
- ホスティング：Netlify（https://dead-class-lp.netlify.app/）

## 構成
- `index.html` — LP本体（CSS / JS インライン）
- `kv/` — 主要キービジュアル（Hero / コンセプト / A案 / B案）
- `venue/` — 会場（NASU UTOPIA 公式提供）写真

## 投票連携
LP内の `VOTE_CONFIG` で以下3つを指定：
- `FORM_RED` / `FORM_BLUE`：Google Form プリフィルURL
- `COUNT_API`：Google Apps Script Web App（集計エンドポイント）

GAS の元コードは `~/work/immersive-lab/dead_class/setup_form.gs`。
