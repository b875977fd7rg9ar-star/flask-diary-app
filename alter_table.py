import sqlite3

conn = sqlite3.connect("diary.db")
cur = conn.cursor()

cur.execute("ALTER TABLE diary ADD COLUMN user_id INTEGER;")

conn.commit()
conn.close()

print("user_idカラムを追加しました！")

