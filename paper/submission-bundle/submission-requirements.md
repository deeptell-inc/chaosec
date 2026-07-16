---
asset: submission-requirements
version: 1.0.0
生成元入力: S12 本投稿バンドル作成（venue: PRX Quantum）
依存工程: S10, S12
生成日: 2026-07-10
---

# submission-requirements — PRX Quantum 投稿要件 × 成果物 1対1照合

Venue: **PRX Quantum** (APS). Source of requirements: APS PRX Quantum author
information + PRX-family common rules (Popular Summary, REVTeX, declarations).

| # | 要件 | 状態 | 成果物 / 備考 |
|---|---|---|---|
| 1 | REVTeX 4.2 ソース（`prxquantum` クラス） | ✓ | `main.tex`（`[aps,prxquantum,twocolumn]`） |
| 2 | アブストラクト（本文冒頭） | ✓ | `main.tex` abstract（Nature式7要素） |
| 3 | **Popular Summary（非専門家向け ≤250語）** | ✓ | `popular_summary.md`（239語） |
| 4 | 図（本文が参照する全図を同梱・解決可能） | ✓ | `figures/`（8点 PNG、`\graphicspath{{figures/}}`） |
| 5 | 参照文献（BibTeX） | ✓ | `refs.bib`（34件、未定義引用0） |
| 6 | 補足資料（Supplemental Material） | ✓ | `supplement.tex`（8節・図3・表1） |
| 7 | カバーレター（推奨査読者含む） | ✓ | `cover_letter.{tex,pdf}`（3段落appeal＋査読者8名） |
| 8 | Competing interests 宣言 | ✓ | `DECLARATIONS.md`（no competing interests） |
| 9 | Data & code availability 宣言 | ✓ | `main.tex` §Data and code availability ＋ `DECLARATIONS.md` |
| 10 | 事実検証（数値・主張） | ✓ | S17 通過（`../factcheck-report.md`, `../claims-ledger.md`） |
| 11 | コンパイル健全性（本文・補足が単独で通る） | ✓ | バンドル内 `pdflatex` で main 5p・supplement 3p、エラー0 |

## 投稿前に著者が埋める項目（未確定）
- [ ] Funding / acknowledgments（`main.tex` の該当コメント、`DECLARATIONS.md`）
- [ ] Author contributions の最終文言（`DECLARATIONS.md`）
- [x] Zenodo DOI 予約済 **10.5281/zenodo.21336840**（production draft id 21336840、
      `main.tex` data availability・`DECLARATIONS.md` に記載済）。※レコードは未公開（draft）。
      公開時: `zenodo-deposit --config submission.json --production --publish`（不可逆）
- [ ] 推奨査読者の所属メールアドレス（`cover_letter.tex`）
- [ ] 長さガイド（初回投稿は任意形式可。プロダクション時に図を個別ファイル提出）

## DoD（S12）
- 形式要件を全項目1対1確認 ✓（未確定は「著者記入」に明示分離）
- バンドル内ファイル一式が揃う ✓
- 引用整合（本文引用 ⇔ refs.bib ⇔ claims-ledger）取れている ✓
- S17 通過済 ✓
→ **S12 バンドルは投稿可能状態。実投稿は承認ゲート（ユーザー承認後）。**
