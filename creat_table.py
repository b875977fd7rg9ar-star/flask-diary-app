import sqlite3

dbname = 'diary.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

# users テーブルを追加（存在しない場合だけ作成）
cur.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("users テーブルを作成しました")