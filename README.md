# 作れたのに作られなかった物はどれだけあるか ― 公開用一式(2026-11-19)

ある個人の研究の問いを、AI(Anthropic の Claude)が対話しながら調べた記録の公開用一式です。2026年11月10〜19日に作業しました。
本文は `report/` にあります。まずそちらを読んでください。同じ報告は、読みやすいページでも読めます: https://claude.ai/artifact/MqaXg6yjtpxkHnhSnPWtvS (リンクが共有されていない間は開けません)

## 中身
| フォルダ | 内容 |
|---|---|
| `report/` | 公開用の報告(この一式の本体。単独で読める) |
| `records/` | 作業の記録。手順と予想(protocol)、結果(results)を番号順に並べたもの(01〜20)。予想は結果より前に書き、ハッシュ値を記録した |
| `records/blind_recode/` | 独立の判定者(別の AI)に渡した資料と、その回答 |
| `code/field_calc/` | 基板設計の数字を試した電磁界の計算(2次元の有限差分、3次元の簡単な見積もり) |
| `code/field_calc_independent/` | 同じ問題を、別の作業者が別の方法(モーメント法など)で解いた計算 |
| `code/potter/` | Potter の公開データから、遅れの表を作り直すスクリプト |
| `data/stage2_sleeping_beauties/` | 「埋もれた研究の予測」の元データ(OpenAlex 由来)と分析 |
| `data/untried_ideas/` | 論文の「まだ試されていない」「応用できるかもしれない」の候補一覧(書誌情報のみ)と引用数 |

## 再現のしかた
- 遅れの表: Potter のリポジトリ(https://github.com/briancpotter/inventiondating)から `inventions_full_analysis.docx` を取得し、`python3 -I code/potter/rebuild_potter_gaps.py inventions_full_analysis.docx gaps.csv` を実行する。2026-11-17に取得した版では、報告で使った170行と完全に一致した。
- 電磁界の計算: Python 3、numpy、scipy。`code/field_calc/validate.py`(既知の式との照合)、`run17.py`、`run17b.py`、`run17c.py`、`peec3d.py`。
- 埋もれた研究の予測: `data/stage2_sleeping_beauties/` で `python3 analyze.py` を実行する。取得用のスクリプトは OpenAlex の API キー(環境変数 OPENALEX_API_KEY)が要る。取得し直すと OpenAlex 側のデータが変わっているため、同じ結果にはならない。

## 注意
- 査読を受けた論文ではありません。判定はほぼすべて AI によるもので、独立の確認も別の AI によるものです。
- 歴史の年代は、Potter のデータ(AI による推定)に頼っています。
- 基板の計算は2次元の準静的な近似で、実測ではありません。**実際の機器の設計や安全の判断に使わないでください。**
- `records/` の記録のうち5点(01、05、14、17、19)は、個人名を「依頼者」に置き換えました。そのため、`records/SHA256SUMS_original.txt` にある元のハッシュ値とは一致しません。違いは、この置き換えだけです。
- `records/SHA256SUMS_original.txt` には、この一式に入れていないファイルの値も含まれます。
- 記録の中には、作業した環境のファイルの場所(パス)が出てきます。この一式の中の場所とは違います。

## ライセンス
- 文書と、こちらで作ったデータ: CC BY 4.0(LICENSE-docs.txt)
- コード: MIT(LICENSE-code.txt)
- 第三者のデータ(OpenAlex 由来、CC0)は、それぞれの条件に従います。Potter のデータは、この一式に含めていません(`EXCLUDED.md`)。
