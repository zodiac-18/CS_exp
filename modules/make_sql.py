# -*- coding: utf-8 -*-

"""SQLの作成に関する関数"""

from utils import create_placeholder

from data import Column


def make_sql_from_form(form, filter, display) -> tuple:
    """
    検索フォームから受け取った検索条件・表示項目からSQL文を生成

    Args:
        form (dict): 検索条件・表示項目を含むフォームデータ
        filter (list): 検索条件に用いるhtml内のnameリスト
        display (list): 表示項目に用いるhtml内のnameリスト

    Returns:
        tuple (str, list, list, bool, bool):
        SQL文, プレースホルダに対応する値, 表示項目, 達成人数の割合表示フラグ, プレイ人数表示フラグ
    """
    # 1. SELECT句の作成
    # formatフラグを取得
    # 0 (False): 人数表示, 1 (True): 達成率表示
    is_percent = bool(int(form.getvalue("format")))
    # 表示する項目を取得して記憶
    select_keys = [name for name in display if form.getvalue(name)]
    is_count_display = "count" in select_keys
    # 表示する列がない場合は全ての列を表示する
    if not select_keys:
        columns = "*"
        select_keys = Column.display_info
    else:
        # プレイ人数, 難易度, 楽曲名は必ず検索する (プレイ人数は指定がなければ表示しない)
        # TODO: プレイ人数周りの処理の冗長性を解消したい
        required_columns = ["count", "difficulty_name", "music_title"]
        for col in required_columns:
            if col not in select_keys:
                select_keys.insert(0, col)
        columns = ", ".join(select_keys)

    # 2. WHERE句の作成
    conditions = []
    # プレースホルダに対応する値を格納 (SQLインジェクション対策)
    values = []
    for name in filter:
        value = form.getlist(name)
        if value:
            if name == "level_filter":
                level_values = [f"{int(v)}" for v in value]
                conditions.append(f"level IN ({create_placeholder(level_values)})")
                values.extend(level_values)
            elif name == "difficulty":
                difficulty_values = [f"{Column.difficulties[int(v)]}" for v in value]
                conditions.append(
                    f"difficulty_name IN ({create_placeholder(difficulty_values)})"
                )
                values.extend(difficulty_values)
            elif name == "music_title_filter" and value != [""]:
                conditions.append("music_title LIKE ?")
                values.append(f"%{value[0]}%")
            elif name == "artist_filter" and value != [""]:
                conditions.append("artist LIKE ?")
                values.append(f"%{value[0]}%")

    where_clause = " AND ".join(conditions)

    if where_clause:
        where_clause = f"WHERE {where_clause}"
    sql = f"SELECT {columns} FROM sdvx_stats {where_clause}"

    return sql, values, select_keys, is_percent, is_count_display
