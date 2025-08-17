def delete_diary():
    import sqlite3
    conn = sqlite3.connect('diary.db')
    cur = conn.cursor()
    cur.execute('SELECT * from diary')
    rows = cur.fetchall() 
    for row in rows:
        print(f"{row[1]}｜{row[0]}")
    while True:
        delete_id = input('削除する番号を選択してください!>>')
        cur.execute("SELECT * FROM diary WHERE id = ?", (delete_id,))
        result = cur.fetchone()
        if result is None:
            print("その投稿は存在しません!")
        else:
            cur.execute("DELETE FROM diary WHERE id = ?", (delete_id,))
            conn.commit()
            print("投稿を削除しました!")
            break