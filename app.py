from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Flask-Login設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ユーザークラス
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("diary.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(id=row[0], username=row[1], password=row[2])
    return None

# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect("diary.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()

        if row and check_password_hash(row[2], password):
            user = User(id=row[0], username=row[1], password=row[2])
            login_user(user, remember=True)
            flash("ログインしました！", "success")
            return redirect(url_for("home"))
        else:
            flash("ユーザー名またはパスワードが違います。", "danger")

    return render_template("login.html")
# ログアウト
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました。", "info")
    return redirect(url_for("login"))

# 日記一覧（ログイン必須）
@app.route("/")
@login_required
def home():
    conn = sqlite3.connect("diary.db")
    cur = conn.cursor()
    cur.execute("SELECT id, content, date FROM diary WHERE user_id=?", (current_user.id,))
    posts = cur.fetchall()
    conn.close()
    return render_template("home.html", posts=posts)

# 書き込み
@app.route("/write", methods=["GET", "POST"])
@login_required
def write():
    if request.method == "POST":
        content = request.form["diary_entry"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("diary.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO diary (content, date, user_id) VALUES (?, ?, ?)",
            (content, date, current_user.id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("home"))
    return render_template("write.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # パスワード一致チェック
        if password != confirm_password:
            flash("パスワードが一致しません", "danger")
            return redirect("/register")

        # パスワードをハッシュ化
        hashed_password = generate_password_hash(password)

        # DBにユーザー登録
        conn = sqlite3.connect("diary.db")
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("そのユーザー名はすでに使われています", "danger")
            conn.close()
            return redirect("/register")
        conn.close()

        flash("アカウントが作成されました。ログインしてください", "success")
        return redirect("/login")
    else:
        return render_template("register.html")

# 削除
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    conn = sqlite3.connect("diary.db")
    cur = conn.cursor()
    # idとuser_idが一致する投稿だけ削除
    # cur.execute("DELETE FROM diary WHERE id=? AND user_id=?", (id, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

# 編集
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    conn = sqlite3.connect("diary.db")
    cur = conn.cursor()

    if request.method == "POST":
        # 入力内容を受け取って更新
        content = request.form["diary_entry"]
        cur.execute(
            "UPDATE diary SET content=? WHERE id=? AND user_id=?",
            (content, id, current_user.id)
        )
        conn.commit()
        conn.close()
        flash("日記を更新しました！", "success")
        return redirect(url_for("home"))

    # GET時は編集フォームに既存の内容を表示
    cur.execute(
        "SELECT * FROM diary WHERE id=? AND user_id=?",
        (id, current_user.id)
    )
    post = cur.fetchone()
    conn.close()

    if not post:
        flash("その投稿は存在しないか、編集権限がありません。", "danger")
        return redirect(url_for("home"))

    return render_template("edit.html", post=post)

if __name__ == "__main__":
    app.run()