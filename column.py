# -*- coding: utf-8 -*-

"""データベースのカラム情報"""


class Column:
    """
    データベースのカラム情報を定義するクラス
    """

    column_info = {
        "music_title": "楽曲名",
        "difficulty_name": "難易度",
        "level": "レベル",
        "artist": "作曲者",
        "count": "プレイ人数",
        # クリアランプ (PLAYED, COMP, EX_COMP, UC, PUC)
        "played": "PLAYED",
        "comp": "COMP",
        "ex_comp": "EX_COMP",
        "uc": "UC",
        "per": "PUC",
        # スコアグレード (B, A, A+, AA, AA+, AAA, AAA+, S, 995, 998)
        "grade_B": "B",
        "grade_A": "A",
        "grade_Ap": "A+",
        "grade_AA": "AA",
        "grade_AAp": "AA+",
        "grade_AAA": "AAA",
        "grade_AAAp": "AAA+",
        "grade_S": "S",
        "grade_995": "995",
        "grade_998": "998",
        # 平均スコア・標準偏差
        "avg_score": "平均スコア",
        "sd_score": "標準偏差",
        # スキルレベルごとの平均スコア (～雷電, 魔騎士, 剛力羅, 或帝滅斗, 無枠暴龍天, 金枠暴龍天, 後光暴龍天)
        "avg_skill_u8": "～雷電",
        "avg_skill_9": "魔騎士",
        "avg_skill_10": "剛力羅",
        "avg_skill_11": "或帝滅斗",
        "avg_skill_12_n": "無枠暴龍天",
        "avg_skill_12_g": "金枠暴龍天",
        "avg_skill_12_h": "後光暴龍天",
        # VF帯ごとの平均スコア (～アルジェント, エルドラ1, 2, エルドラ3, 4, クリムゾン1, クリムゾン2, クリムゾン3, クリムゾン4, インペリアル1, インペリアル2)
        "avg_vf_u7": "～アルジェント",
        "avg_vf_8_i_ii": "エルドラ1, 2",
        "avg_vf_8_iii_iv": "エルドラ3, 4",
        "avg_vf_9_i": "クリムゾン1",
        "avg_vf_9_ii": "クリムゾン2",
        "avg_vf_9_iii": "クリムゾン3",
        "avg_vf_9_iv": "クリムゾン4",
        "avg_vf_10_i": "インペリアル1",
        "avg_vf_10_ii": "インペリアル2",
    }

    # リスト定義
    filter_info = [
        "level_filter",
        "difficulty",
        "music_title_filter",
        "artist_filter",
    ]

    display_info = [
        "music_title",
        "difficulty_name",
        "level",
        "artist",
        "count",
        # クリアマークの達成人数・割合
        "played",
        "comp",
        "ex_comp",
        "uc",
        "per",
        # スコアグレードの達成人数・割合
        "grade_B",
        "grade_A",
        "grade_Ap",
        "grade_AA",
        "grade_AAp",
        "grade_AAA",
        "grade_AAAp",
        "grade_S",
        "grade_995",
        "grade_998",
        # 平均スコア（全体）
        "avg_score",
        "sd_score",
        # スキルレベルごとの平均スコア
        "avg_skill_u8",
        "avg_skill_9",
        "avg_skill_10",
        "avg_skill_11",
        "avg_skill_12_n",
        "avg_skill_12_g",
        "avg_skill_12_h",
        # VF帯ごとの平均スコア
        "avg_vf_u7",
        "avg_vf_8_i_ii",
        "avg_vf_8_iii_iv",
        "avg_vf_9_i",
        "avg_vf_9_ii",
        "avg_vf_9_iii",
        "avg_vf_9_iv",
        "avg_vf_10_i",
        "avg_vf_10_ii",
    ]

    difficulties = [
        "NOVICE",
        "ADVANCED",
        "EXHAUST",
        "MAXIMUM",
        "INFINITE",
        "GRAVITY",
        "HEAVENLY",
        "VIVID",
        "EXCEED",
    ]

    clear_mark = ["played", "comp", "ex_comp", "uc", "per"]

    score_grade = [
        "grade_B",
        "grade_A",
        "grade_Ap",
        "grade_AA",
        "grade_AAp",
        "grade_AAA",
        "grade_AAAp",
        "grade_S",
        "grade_995",
        "grade_998",
    ]
