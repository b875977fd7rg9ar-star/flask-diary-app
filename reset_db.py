import sqlite3

# データベースに接続（なければ作られる）
conn = sqlite3.connect('diary.db')
cur = conn.cursor()

# 既存のテーブルを削除（ある場合）
cur.execute("DROP TABLE IF EXISTS diary")

# Flask用の構成で作り直し
cur.execute("""
CREATE TABLE diary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT
)
""")

conn.commit()
conn.close()

print("データベースをリセットし、Flask用に再構築しました。")