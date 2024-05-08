# -*- coding: utf-8 -*-

"""検索結果のhtml文作成に関する関数"""

from utils import calculate_achiever_rate, calculate_deviation, validate_score

from data import Column


# 結果の表の仕様
# 動画・楽曲名・難易度・レベル・作曲者・プレイ人数・クリアマーク(PLAYED~PUC)・スコアグレード(B~998)・平均スコア・VF帯ごとの平均スコア (~アルジェント~インペリアル2)、スキルレベルごとの平均スコア(~雷電~後光暴龍天)の順で表示
# 動画・楽曲名・難易度は必ず表示
# 楽曲名をクリックすると楽曲ごとの偏差値計算ページ(ss_musicページ)に飛ぶ
# クリアマーク・スコアグレードに関してはpercent_flag=Trueの場合は達成率 (達成人数÷プレイ人数×100)表示, Falseの場合は人数表示
# 達成率表示の場合、達成率を計算する関数を使って達成率を計算し、0%は灰色文字, 0.10%以下は赤太文字, 0.10~1.00%以下は赤文字(細字), 1.00%以上は黒文字で表示
# 色はCSSで指定する. 0%はachiever_rate_zero, 0.01%以下はachiever_rate_very_rare, 1.00%以上はachiever_rate_rareのクラスを使用
def create_results_header(
    select_keys, is_percent=True, is_count_display=False, is_ranking=False
) -> str:
    """
    検索結果テーブルのヘッダーを作成

    Args:
        select_keys (list): 表示する列のリスト
        is_percent (bool, optional): 達成率を表示するかどうか
        is_count_display (bool, optional): プレイ人数を表示するかどうか
        is_ranking (bool, optional): "Ranking"ならホームのランキングテーブルのヘッダを生成

    Returns:
        str: 作成されたヘッダーのHTMLコード
    """
    header = ""
    # ランキングのときのみRankを表示
    if is_ranking:
        header += "<tr>\n<th class='con' id='rank'>RANK</th>\n"
    header += "<th class='con' id='0'>動画</th>\n"
    for index, key in enumerate(select_keys):
        header_name = Column.column_info[key]
        # クリアマークとスコアグレードの場合は表記を明示
        if key in Column.score_grade + Column.clear_mark:
            if is_percent:
                header_name += " (%)"
            else:
                header_name += " (人)"
        # HTMLヘッダーに列名を追加
        # プレイ人数を表示しない場合は除外
        if key == "count" and not is_count_display:
            continue
        header += f"<th class='con' id='{index+1}'>{header_name}</th>\n"
    header += "</tr>\n"
    return header


def _create_table_data(class_name, data, is_music=False) -> str:
    """
    テーブルの個々のセルデータのHTMLコードを作成

    Args:
        class_name (str): class属性につける名前
        data (str): テーブルデータ
        is_music (bool, optional): データが楽曲名の場合はTrue. デフォルトはNone.

    Returns:
        str: テーブルデータのHTMLコード
    """
    if is_music:
        # 楽曲名の場合は動画へのリンクとss_musicへのリンクを追加
        video_link = (
            '<a href="https://www.youtube.com/results?search_query='
            + str(data)
            + '+sdvx"><img src="https://zodiac-18.github.io/cs_exp01/jikken/img/yt_icon.png" alt="動画" width="24" height="16" border="0"></a>'
        )
        data_link = (
            '<a href="/?ss_music=' + str(data) + '" class="data">' + str(data) + "</a>"
        )
        return f'<td class="video">{video_link}</td><td class="{class_name}">{data_link}</td>'
    else:
        return f'<td class="{class_name}">{data}</td>'


def create_results_table(
    cur,
    sql,
    values,
    select_keys,
    is_percent=True,
    is_count_display=False,
    is_ranking=False,
) -> tuple:
    """
    指定されたSQLクエリに基づいて結果テーブルを作成

    Args:
        cur (sqlite3.Cursor): データベースのカーソル
        sql (str): SQLクエリ
        values (tuple or list): SQLクエリのプレースホルダに対応する値
        select_keys (list): 表示する列のリスト
        is_percent (bool, optional): 達成率を表示するかどうか.
        is_count_display (bool, optional): プレイ人数を表示するかどうか.
        is_ranking (bool, optional): ホームのランキングテーブルであるかどうか.

    Returns:
        tuple (str, str): 生成されたテーブルのヘッダと本文
    """
    # ヘッダを生成
    header = create_results_header(
        select_keys, is_percent, is_count_display, is_ranking
    )

    # テーブルの本文を生成
    results_table = ""
    # valuesがタプルではない場合はタプルに変換
    if not isinstance(values, tuple):
        values = tuple(values)
    for data_number, search_result in enumerate(cur.execute(sql, values)):
        results_table += "<tr>\n"
        # 達成率を計算するためのプレイ人数のインデックス取得
        count_index = select_keys.index("count")
        # ランキングのときのみRankを表示
        if is_ranking:
            results_table += '<td class="rank">' + str(data_number + 1) + "</td>\n"
        for key_number, key in enumerate(select_keys):
            if key == "music_title":
                music_title = search_result[key_number]
                results_table += _create_table_data(
                    "music_title", music_title, is_music=True
                )
            # 難易度名の色指定のために別枠でclassを追加
            elif key == "difficulty_name":
                difficulty_name = search_result[key_number]
                results_table += _create_table_data(
                    f"difficulty_{difficulty_name}", difficulty_name
                )
            # クリアマークとスコアグレードは人数または達成者率を計算して表示
            elif key in Column.clear_mark + Column.score_grade:
                # ％表示
                if is_percent:
                    data, css_class = calculate_achiever_rate(
                        int(search_result[key_number]),
                        int(search_result[count_index]),
                    )
                # 人数表示
                else:
                    data, css_class = search_result[key_number], key
                results_table += _create_table_data(css_class, data)
            else:
                # プレイ人数を表示するかどうかを判定
                if key == "count" and not is_count_display:
                    continue
                data = search_result[key_number]
                results_table += _create_table_data(key, data)
        results_table += "</tr>\n"
    return header, results_table


def create_deviation_score_results(ss_score, sd_score, avg_score):
    """
    偏差値計算の結果を表示するページを作成

    Args:
        ss_score (int): プレイヤーのスコア
        sd_score (int): データベース上の標準偏差
        avg_score (int): データベース上の平均スコア

    Returns:
        str: 偏差値計算結果のHTMLコード
    """
    # スコアが正しいかどうかを確認
    is_valid, error_message = validate_score(ss_score, sd_score)
    if is_valid:
        deviation_score = calculate_deviation(ss_score, avg_score, sd_score)
        return f"<h3>偏差値は{deviation_score}です。</h3>\n"
    else:
        return error_message
