#!/usr/bin/env python3
import csv, json, os

OCH = "/workspace/research/80_AI作業場/knowledge/literature/daily-feed/ochiai"
INDEX = "/workspace/research/80_AI作業場/knowledge/literature/daily-feed/index.csv"
GD = "2026-10-20"

data = {
"42844276": {
 "what": "右上腹部(RUQ)超音波の読影を支援するマルチタスク視覚言語エージェント(VLM)を開発し、外部機関で検証した研究。16所見の分類・診断レポート生成・手術意思決定支援(胆嚢摘出術の要否予測)を単一システムで行う。",
 "compared_to_prior": "超音波読影は操作者依存で時間感受性が高い。従来のAIは単一タスクが中心で、複数タスクを統合したVLMとして報告した点が新しい。",
 "key_technique": "フレーム単位の視覚理解とレポートに基づく言語推論を統合したマルチタスクVLM。16所見分類・レポート生成・手術意思決定支援を1つのシステムで実行。",
 "target": "単一の三次学術医療センターの9,189例・594,099画像で学習。2独立機関(1,704例・90,616画像、108例・3,240画像)で評価。",
 "verification_method": "内部・外部コホートでAUROCを算出。生成レポートは放射線科医による盲検評価で専門医作成レポートと判別困難かを検証。胆嚢摘出術予測は生成レポートと臨床データから実施。",
 "technical_metrics": "16所見分類のマクロAUROC 内部0.820・University of Colorado 0.794・Stanford 0.775、内部マイクロAUROC 0.865。",
 "clinical_metrics": "胆嚢摘出術の要否予測(生成レポート+臨床データ)。感度・特異度等の詳細は抄録に記載なし。",
 "discussion_limitations": "前向きな臨床使用での性能・ワークフロー影響・一般化は未検証(抄録の範囲では限界の詳細記載なし)。",
 "summary_ja": "右上腹部超音波(RUQ)の読影を支援するマルチタスク視覚言語エージェント(VLM)の開発・外部検証研究。16所見の分類・診断レポート生成・手術意思決定支援(胆嚢摘出術の要否予測)を単一モデルで行う。内部・2外部機関でAUROC 0.775〜0.820、生成レポートは専門医作成と判別困難。救急・肝胆膵の超音波読影のばらつきと時間依存性を緩和する可能性を示す。",
 "study_design": "role=model_development; model=VLM; validation=external_multi_institution",
},
"42881307": {
 "what": "市販AIソフトによる手術動画の自動区間化(auto-segmentation)が、術式レビュー・評価の効率をどこまで改善するかを、標準化された移植肝バックテーブル準備(25工程)で検証した研究。",
 "compared_to_prior": "手術動画のauto-segmentationは研究段階のものが多いが、市販プラットフォームの自動編集機能を実際の技能評価ワークフローで比較した点が新しい。",
 "key_technique": "GoProのAI auto-edit機能による手術動画の自動区間化。手動編集動画・生動画と比較して、工程捕捉率と評価一致を評価。",
 "target": "バックテーブル準備の手術動画5本(うち2本をAI自動区間化)。独立した移植外科医1名が評価。",
 "verification_method": "25工程の捕捉率と、修正Likert尺度(0〜3)による技術評価を、生動画・手動編集・AI自動区間化で比較。",
 "technical_metrics": "AI自動区間化は手動編集比96倍・生動画比16倍速く閲覧・評価可能。工程捕捉率87%(平均19.5/25)。技術評価はAI 2.14±0.99、生/手動2.58±0.71、評価一致率82.9%。",
 "clinical_metrics": "該当なし(技能評価の前処理効率が主要評価)。",
 "discussion_limitations": "高度に標準化された術式(移植肝バックテーブル)での検証であり、他術式への一般化は要検討。評価者は1名。",
 "summary_ja": "市販AIソフト(GoPro auto-edit)による手術動画の自動セグメンテーションが、熟練外科医による術式レビュー・評価をどれだけ効率化できるかを検証。移植肝のバックテーブル準備(25工程)を対象に、自動区間化は手動編集比96倍・生動画比16倍速く閲覧でき、工程捕捉率87%・評価一致率82.9%。標準化された術式での技能評価前処理の省力化に有用だが、他術式への一般化は未検証。",
 "study_design": "role=method_evaluation; model=commercial_auto_segmentation; validation=single_rater_pilot",
},
"42879739": {
 "what": "消化器内視鏡外科のリアルタイムAI意思決定支援(CLASSICA-OR)のインターフェース・解釈・ワークフロー統合について、外科医の要件を質的に明らかにした研究。",
 "compared_to_prior": "リアルタイムAIは技術的性能の報告が中心で、術者がどう提示・統合を望むかというユーザー中心設計の質的知見は乏しい。",
 "key_technique": "CLASSICA-OR(リアルタイム内視鏡癌characterization×AI)を高忠実度の手術シミュレーション環境で術者に試用させ、半構造化インタビューをテーマ分析。",
 "target": "低侵襲消化器外科を専門とする外科医18名。",
 "verification_method": "NVivo支援の質的テーマ分析(定性的)。定量的なAI性能評価は行わない。",
 "technical_metrics": "該当なし(質的研究。リアルタイム灌流ベースの病変characterizationの課題を言及)。",
 "clinical_metrics": "該当なし(術者の要件抽出が目的)。",
 "discussion_limitations": "シミュレーション環境・事前録画画像でのfirst impressionsであり、実際の術中ワークフローや臨床アウトカムは未検証。",
 "summary_ja": "消化器内視鏡外科のリアルタイムAI意思決定支援(CLASSICA-OR)について、術者が求めるインターフェース・解釈・ワークフロー統合の要件を質的に調査。18名の低侵襲消化器外科医が高忠実度シミュレーション環境で試用し、認知負荷の最小化・術者の自律性保持・不確実性の明示・シームレスな統合を優先事項として挙げた。単純な二値出力と詳細な数値表示の好みが分かれ、適応可能な表示設計の必要性が示唆された。",
 "study_design": "role=qualitative_user_study; model=none; validation=none",
},
"42855513": {
 "what": "腹腔鏡の直接光学トロッカー挿入(DOTI)時に腹壁層を識別する深層学習セマンティックセグメンテーションの実現可能性を検討した単施設パイロット研究。",
 "compared_to_prior": "DOTI初期穿刺は空間的見当識障害のリスクが高いが、腹壁層を術中に識別するAIの報告はほぼない。extra-abdominal組織層の識別を検討した点が新しい。",
 "key_technique": "DeepLabV3+(ResNet-50バックボーン)による腹直筋・腹直筋鞘・腹膜+背景の3クラス画素単位セグメンテーション。5分割交差検証。",
 "target": "DOTI 10手技から抽出した951フレーム(3解剖クラス+背景に画素単位注釈)。",
 "verification_method": "5分割交差検証でmIoU・mDice・precision・recall・F1を評価。混同行列で組織クラス間の誤分類を解析。",
 "technical_metrics": "平均IoU 0.794(95%CI 0.785–0.802)、平均Dice 0.883(0.878–0.889)。クラス別Diceは腹直筋0.923・腹直筋鞘0.903・腹膜0.824。組織クラス間の直接混同は0.0–0.3%で大半の誤りは組織-背景境界。",
 "clinical_metrics": "該当なし(技術的実現可能性の検証)。",
 "discussion_limitations": "単施設・小規模コホートのため一般化可能性に限界。臨床応用には多施設・前向き研究が必要。",
 "summary_ja": "腹腔鏡の初回トロッカー直接光学挿入(DOTI)時の空間的見当識障害リスクに対し、腹壁層を識別する深層学習セマンティックセグメンテーションを提案。10手技・951フレームを腹直筋・腹直筋鞘・腹膜の3クラスに画素単位で注釈し、DeepLabV3+(ResNet-50)を5分割交差検証で学習。平均IoU 0.794・平均Dice 0.883(腹膜Dice 0.824)。単施設・小規模だが、AI支援による手術アクセスガイダンスの実現可能性を示す。",
 "study_design": "role=method_development; model=DeepLabV3+_ResNet50; validation=5fold_cv",
},
"42849513": {
 "what": "FDAが認可したAI/機械学習医療機器のうち外科応用のものを体系的に解析し、臨床応用・AI技術・エビデンス品質・規制経路を特徴づけた研究。",
 "compared_to_prior": "外科AIの規制ランドスケープとエビデンス基盤を、FDA認可機器の全数スクリーニングで定量化した点が新しい。",
 "key_technique": "FDA認可AI/ML機器を体系的にスクリーニングし、記述的・診断的・予測的・処方的フレームワークで分類。predicate networkを評価しpredicate creepリスクを判定。",
 "target": "2025年7月までのFDA認可AI/ML医療機器のうち外科応用314件(全体の25.1%)。",
 "verification_method": "体系的スクリーニングとRによる記述統計。各機器の臨床応用・AI技術・エビデンス品質・規制経路を抽出。",
 "technical_metrics": "画像ベース機器が中心。領域は一般外科24.8%・整形18.2%・脳神経17.2%・心臓10.8%。記述的50.6%・診断的40.4%・予測的1.3%・処方的7.6%。510(k)が95.2%、predicate creep高リスク37.5%。前向き高品質エビデンスは5.1%。",
 "clinical_metrics": "該当なし(規制・エビデンス基盤の解析)。",
 "discussion_limitations": "予測的・介入的役割への拡大に伴い、エビデンス透明性と機器等価性評価の強化が必要。",
 "summary_ja": "FDAが認可したAI/機械学習医療機器のうち外科応用(314件、25.1%)を体系的に解析。大半は画像ベースの記述的(50.6%)・診断的(40.4%)機器で、予測的(1.3%)・処方的(7.6%)は少ない。臨床検証は後ろ向き・ベンチが中心で前向き高品質エビデンスは5.1%のみ、510(k)が95.2%を占め37.5%にpredicate creepの高リスク。外科AIの規制・エビデンス基盤の課題を示す。",
 "study_design": "role=regulatory_landscape; model=none; validation=systematic_screening",
},
}

for pm, d in data.items():
    rec = {"pmid": pm}
    for k in ["what","compared_to_prior","key_technique","target","verification_method",
              "technical_metrics","clinical_metrics","discussion_limitations","summary_ja","study_design"]:
        rec[k] = d[k]
    rec["source"] = "abstract_only"
    rec["generated_date"] = GD
    with open(os.path.join(OCH, pm + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print("ochiai written", pm)

# reflect into index.csv columns + S rank
with open(INDEX, encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; rows = list(rd)
srank = {"42879739": "S:消化器内視鏡外科のリアルタイムAI意思決定支援の術者要件を質的に抽出。口田さんの術中リアルタイムAIアラート研究の設計・実装に直結する。"}
for r in rows:
    if r["pmid"] in data:
        d = data[r["pmid"]]
        r["summary_ja"] = d["summary_ja"]
        r["study_design"] = d["study_design"]
        r["technical_metrics"] = d["technical_metrics"]
        r["clinical_metrics"] = d["clinical_metrics"]
        if r["pmid"] in srank:
            r["s_rank"] = srank[r["pmid"]]
with open(INDEX, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print("index.csv updated for ochiai", len(data))
