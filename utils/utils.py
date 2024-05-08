# -*- coding: utf-8 -*-

"""ユーティリティ関数"""


def load_html(filename) -> str:
    """
    ファイル名からHTMLを読み込む

    Args:
        filename (str): HTMLファイル名

    Returns:
        str: 読み込んだHTML
    """
    with open(filename, "r", encoding="utf-8") as file:
        html = file.read()
    return html


def create_placeholder(key) -> str:
    """
    SQL文作成のためのプレースホルダを生成

    Args:
        key (list): プレースホルダを設置するキー

    Returns:
        str: プレースホルダの文字列
    """
    return ",".join(["?" for _ in range(len(key))])


def calculate_deviation(score, avg_score, sd_score) -> float:
    """
    偏差値を計算する

    Args:
        score (str): スコア
        avg_score (str): 平均スコア
        sd_score (str): 標準偏差

    Returns:
        float: 偏差値
    """

    # 偏差値計算
    deviation_value = round((int(score) - int(avg_score)) / int(sd_score) * 10 + 50, 3)
    return deviation_value


def _validate_ss_score(ss_score) -> tuple:
    """
    偏差値計算に用いるスコアのバリデーションを行う

    Args:
        ss_score (str): formから得られた偏差値計算用スコア

    Returns:
        tuple (bool, str): バリデーションの結果とエラーメッセージ
    """
    try:
        ss_score = int(ss_score)
        if ss_score < 0 or ss_score > 10000000:
            return (
                False,
                "<h3>スコアは0～10,000,000の範囲で入力してください。</h3>\n",
            )
        else:
            return True, ""
    except ValueError:
        return False, "<h3>スコアは数値で入力してください。</h3>\n"


def _validate_sd_score(sd_score) -> tuple:
    """
    偏差値計算に用いる標準偏差のバリデーションを行う
    Args:
        sd_score (str): データベースから得られた標準偏差

    Returns:
        tuple: バリデーションの結果とエラーメッセージ
    """
    sd_score = int(sd_score)
    if sd_score == 0:
        return False, "<h3>スコアデータがないため計算できません。</h3>\n"
    else:
        return True, ""


# ss_scoreとsd_scoreのバリデーションを行う
def validate_score(ss_score, sd_score):
    """
    スコアのバリデーションを行う

    Args:
        ss_score (str): スコア
        sd_score (str): 標準偏差

    Returns:
        tuple: バリデーションの結果とエラーメッセージ
    """
    # スコアが正しいかどうかを確認
    is_valid, error_message = _validate_ss_score(ss_score)
    if not is_valid:
        return False, error_message
    # 標準偏差が正しいかどうかを確認
    is_valid, error_message = _validate_sd_score(sd_score)
    if not is_valid:
        return False, error_message
    return True, ""


def calculate_achiever_rate(achiever_count, total_count) -> tuple:
    """
    達成数と総数に基づいて達成率とcss色分け用のクラスを返す

    Args:
        achiever_count (int): 達成者数
        total_count (int): 総数

    Returns:
        tuple (float, str): 達成率と色分け用のクラス
    """
    # 達成者率の計算
    if total_count == 0:
        achiever_rate = 0.0
    else:
        achiever_rate = round(achiever_count / total_count * 100, 3)
    # 達成者率ごとに色分け用のクラスを返す
    if achiever_rate == 0:
        achiever_class = "achiever_rate_zero"
    elif achiever_rate <= 0.10:
        achiever_class = "achiever_rate_very_rare"
    elif achiever_rate <= 1.00:
        achiever_class = "achiever_rate_rare"
    else:
        achiever_class = "achiever_rate_common"
    return achiever_rate, achiever_class


def print_sql(sql, values) -> None:
    """
    実行したSQL文とプレースホルダに対応する値を表示

    Args:
        sql (str): 実行したSQL文
        values (list): プレースホルダに対応する値
    """
    print(f"\n実行したSQL文\n {sql}\n")
    print("プレースホルダ\n" + str(values) + "\n")
