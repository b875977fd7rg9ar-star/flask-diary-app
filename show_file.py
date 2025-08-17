def show_diary():
    import sqlite3
    conn = sqlite3.connect('diary.db')
    cur = conn.cursor()
    cur.execute('SELECT * from diary')
    rows = cur.fetchall() 
    for row in rows:
        print(f"{row[1]}｜{row[0]}")
    input("メニューに戻るにはEnterを押してください!")
