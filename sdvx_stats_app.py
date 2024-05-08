# -*- coding: utf-8 -*-

"""SDVXのスコアデータベースを扱うWebアプリケーション"""

# CGIモジュールをインポート
import cgi
import cgitb
import os

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
import sys
from wsgiref import simple_server

import pandas as pd

from column import Column
from modules import (
    create_deviation_score_results,
    create_results_table,
    make_sql_from_form,
)
from utils import create_placeholder, load_html, print_sql

cgitb.enable()


class SdvxStatsApp:
    """SDVXのスコアデータベースを扱うWebアプリケーション"""

    def __init__(self, dbname="sdvx_stats.db", csv_file="sdvx_stats.csv"):
        self.dbname = dbname  # DB名
        self.csv_file = csv_file  # CSVファイル名
        self.select_keys = []  # 表示する項目管理
        self.is_count_display = False  # プレイ人数を表示するかどうかのフラグ
        self.is_percent = False  # 達成者を%表示するかどうかのフラグ

        self.init_db()  # データベースの初期化

    def init_db(self) -> None:
        """データベースの初期化"""
        if not os.path.exists(self.dbname):
            csv_f = pd.read_csv(self.csv_file, header=None, sep=",")
            rows = [list(csv_f.iloc[i]) for i in range(1, len(csv_f))]
            con = sqlite3.connect(self.dbname)
            cur = con.cursor()
            # SQLテーブルの作成
            columns = ", ".join(col for col in Column.column_info.keys())
            cur.execute(f"CREATE TABLE IF NOT EXISTS sdvx_stats ({columns})")
            cur.executemany(
                f"INSERT INTO sdvx_stats ({columns}) VALUES ({create_placeholder(columns.split(','))})",
                rows,
            )
            con.commit()
            cur.close()
            con.close()

    def handle_home(self) -> str:
        """
        トップページのHTMLページを生成する

        Returns:
            str: トップページのHTMLページ
        """
        # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）
        # HTML(入力フォーム部分)
        response = load_html("home.html")

        con = sqlite3.connect(self.dbname)
        cur = con.cursor()
        con.text_factory = str

        # 送信するページデータの辞書
        page_data = {"results_header": "", "results": ""}

        # トップページに載せる平均スコアランキング
        # レベル18以上のMXM相当の楽曲の中で平均スコアが低い順に10曲のデータを表示 (トップ10に入りうる楽曲)
        # 楽曲名, 難易度, レベル, 作曲者, プレイ人数, 全体の平均スコア, インペリアル1の平均スコア, 後光暴龍天の平均スコアを表示
        self.select_keys = [
            "music_title",
            "difficulty_name",
            "level",
            "artist",
            "count",
            "avg_score",
            "avg_vf_10_i",
            "avg_skill_12_h",
        ]
        # 18~20のレベルかつMXM相当の楽曲を対象にする
        ranking_display_levels = ["18", "19", "20"]
        ranking_display_difficulties = Column.difficulties[3:]
        ranking_display_values = ranking_display_difficulties + ranking_display_levels

        # TODO: make_sqlを使ってSQL文を生成したい
        sql = (
            f"SELECT {', '.join(self.select_keys)} FROM sdvx_stats "
            + f"WHERE difficulty_name IN ({create_placeholder(ranking_display_difficulties)}) "
            + f"AND level IN ({create_placeholder(ranking_display_levels)}) "
            + "ORDER BY avg_score ASC LIMIT 0, 10"
        )

        # 生成したSQL文を表示
        print_sql(sql, ranking_display_values)

        # SQL文の検索結果からHTML文を作成
        page_data["results_header"], page_data["results"] = create_results_table(
            cur,
            sql,
            ranking_display_values,
            self.select_keys,
            self.is_percent,
            self.is_count_display,
            is_ranking=True,
        )

        # 結果部分のHTML出力
        for key, value in page_data.items():
            response = response.replace("{% " + key + " %}", value)

        # カーソルと接続を閉じる
        cur.close()
        con.close()
        return response

    def handle_about(self) -> str:
        """
        AboutのHTMLページを生成する

        Returns:
            str: AboutのHTMLページ
        """
        response = load_html("about.html")
        return response

    def handle_result(self, form) -> str:
        """
        検索結果のHTMLページを生成する

        Args:
            form (dict): 検索条件・表示項目を含むフォームデータ

        Returns:
            str: 検索結果のHTMLページ
        """
        response = load_html("result.html")
        con = sqlite3.connect(self.dbname)
        cur = con.cursor()
        con.text_factory = str

        # HTMLに追加するHTML文
        page_data = {"results_header": "", "results": ""}

        # 検索フォームの内容からSQL文を生成
        sql, sql_values, self.select_keys, self.is_percent, self.is_count_display = (
            make_sql_from_form(form, Column.filter_info, Column.display_info)
        )

        # 生成したSQL文を表示
        print_sql(sql, sql_values)

        # SQL文の検索結果からHTML文を作成
        page_data["results_header"], page_data["results"] = create_results_table(
            cur,
            sql,
            sql_values,
            self.select_keys,
            self.is_percent,
            self.is_count_display,
        )

        # 結果部分のHTML出力
        for key, value in page_data.items():
            response = response.replace("{% " + key + " %}", value)

        # カーソルと接続を閉じる
        cur.close()
        con.close()
        return response

    def handle_calculate(self, form) -> str:
        """
        偏差値計算のHTMLページを生成する

        Args:
            form (dict): 検索条件・表示項目を含むフォームデータ

        Returns:
            str: 検索結果のHTMLページ
        """
        response = load_html("ss.html")
        con = sqlite3.connect(self.dbname)
        cur = con.cursor()
        con.text_factory = str
        # ss_results: 偏差値計算結果
        # data_info: 「"楽曲名”の統計データ」という文字列 (データがある場合)
        # results_header: 統計テーブルヘッダ
        # results_table: 統計テーブルデータ
        page_data = {
            "ss_results": "<h3>検索結果が見つかりませんでした。</h3>\n",
            "data_info": "",
            "results_header": "",
            "results_table": "",
        }
        # 偏差値計算の対象となる楽曲名を取得
        music_title = form.getvalue("ss_music")
        # 楽曲名をHTML文に追加
        page_data["music_title"] = f"'{music_title}'"

        if "submit" not in form:
            page_data["ss_results"] = "<h3>スコアを入力してください。</h3>\n"
        else:
            # 偏差値計算を行う難易度 (0=NOVICE, 1=ADVANCED, 2=EXHAUST, 3=MAXIMUM相当)
            search_difficulty = form.getvalue("ss_difficulty").split(",")
            # 偏差値計算を行うスコア
            ss_score = form.getvalue("ss_score")
            # すべての列を表示
            self.select_keys = Column.display_info
            # TODO: make_sqlを使ってSQL文を生成したい
            # 偏差値計算のためのSQL文
            sql = (
                "SELECT * FROM sdvx_stats "
                + f"WHERE music_title=? AND difficulty_name IN ({create_placeholder(search_difficulty)})"
            )
            sql_values = [music_title] + search_difficulty

            print_sql(sql, sql_values)

            # 偏差値計算のためのデータを取得
            search_result = cur.execute(sql, sql_values).fetchone()
            if search_result:
                # 平均スコアと標準偏差を取得
                avg_score = search_result[self.select_keys.index("avg_score")]
                sd_score = search_result[self.select_keys.index("sd_score")]
                # 偏差値の計算結果と統計データのHTML文を生成
                page_data["ss_results"] = create_deviation_score_results(
                    ss_score, sd_score, avg_score
                )
                page_data["data_info"] = f"<h4>'{music_title}'の統計データ</h4>\n"
                page_data["results_header"], page_data["results_table"] = (
                    create_results_table(
                        cur,
                        sql,
                        sql_values,
                        self.select_keys,
                        is_percent=True,
                        is_count_display=True,
                    )
                )
        for key, value in page_data.items():
            response = response.replace("{% " + key + " %}", value)
        # カーソルと接続を閉じる
        cur.close()
        con.close()
        return response

    def application(self, environ, start_response) -> list:
        """
        Webアプリケーションのエントリーポイント

        Args:
            environ (dict): WSGI環境変数の辞書オブジェクト
            start_response (callable): レスポンスヘッダーを設定するための関数

        Returns:
            list: レスポンスボディのリスト
        """
        # フォームデータを取得
        form = cgi.FieldStorage(environ=environ, keep_blank_values=True)
        if "ss_music" in form:
            response = self.handle_calculate(form)
        elif "submit" in form:
            response = self.handle_result(form)
        elif "about" in form:
            response = self.handle_about()
        else:
            response = self.handle_home()

        response = response.encode("utf-8")

        # レスポンス
        start_response(
            "200 OK",
            [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(response))),
            ],
        )
        return [response]


# リファレンスWEBサーバを起動
# ファイルを直接実行する（python3 sql.py）と，
# リファレンスWEBサーバが起動し，http://localhost:8080 にアクセスすると
# このサンプルの動作が確認できる．
# コマンドライン引数にポート番号を指定（python3 sql.py ポート番号）した場合は，
# http://localhost:ポート番号 にアクセスする．

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    sdvx_app = SdvxStatsApp(dbname="sdvx_stats.db", csv_file="sdvx_stats.csv")
    server = simple_server.make_server("", port, sdvx_app.application)
    server.serve_forever()
