import sqlite3

# DBに接続
conn = sqlite3.connect("diary.db")
cur = conn.cursor()

# usersテーブルの中身を確認
cur.execute("SELECT * FROM users;")
rows = cur.fetchall()

if rows:
    for row in rows:
        print(row)
else:
    print("usersテーブルにはまだデータがありません。")

conn.close()