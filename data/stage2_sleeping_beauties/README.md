# 段階2 埋もれた研究の予測実験 元データ(Claude側、2026-11-10 取得)

- cand_pos_a.json、cand_pos_b.json、cand_neg.json: OpenAlex から取得した候補論文
- rows.jsonl: 分析に使った行(特徴量つき)
- topics.json: トピックごとの年別件数
- pilot.json、pilot.py: 予備調査
- oa.py、topics.py、main.py: 取得スクリプト(環境変数 OPENALEX_API_KEY が必要)
- analyze.py: 分析。result.json を出力
- run1.log、run2.log: 実行記録

既知の限界: OpenAlex のトピック分類は2026年10月更新の分類器によるもので、分類体系そのものが後年の引用関係から作られている。時点漏洩は解消できていない。取得日以降は OpenAlex 側のデータが変わるため、同じスクリプトを再実行しても同一のデータにはならない。再現はこの保存データに対して analyze.py を実行して行う。
