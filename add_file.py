def write_file():
    import sqlite3
    import datetime
    while True:
        happen = input('今日は何を習った？>>')
        if happen == '':
            print('入力してください!')
        else: 
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            conn = sqlite3.connect('diary.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO diary (name) VALUES (?)", (now + ' | ' + happen,))
            conn.commit()
            conn.close()
            print("保存しました！")
            break