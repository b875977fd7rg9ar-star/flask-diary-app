from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

import os
import psycopg
from flask import g

def get_conn():
    """リクエストごとに新しいコネクションを返す"""
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL が設定されていません（RenderのEnvironmentで設定してね）")
    if "sslmode=" not in dsn:
        dsn += "?sslmode=require"
    return psycopg.connect(dsn)

with get_conn() as conn, conn.cursor() as cur:
    cur.execute("SELECT ...")
    result = cur.fetchall()

@app.teardown_appcontext
def close_conn(_exc):
    db = g.pop("db", None)
    if db:
        db.close()

def ensure_schema():
    """テーブルが無ければ作る（最初の起動で実行）"""
    with get_conn() as conn, conn.cursor() as cur:
        # users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
              id SERIAL PRIMARY KEY,
              username TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL
            );
        """)
        # diary
        cur.execute("""
            CREATE TABLE IF NOT EXISTS diary (
              id SERIAL PRIMARY KEY,
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              content TEXT NOT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()

# アプリ起動時に一度だけスキーマ確認
with app.app_context():
    ensure_schema()


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
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
    if row:
        return User(id=row[0], username=row[1], password=row[2])
    return None

# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # PostgreSQL からユーザー検索
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
            row = cur.fetchone()

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
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, content, created_at FROM diary WHERE user_id = %s ORDER BY created_at DESC",
            (current_user.id,)
        )
        posts = cur.fetchall()
    return render_template("home.html", posts=posts)

# 書き込み
@app.route("/write", methods=["GET", "POST"])
@login_required
def write():
    if request.method == "POST":
        content = request.form.get("diary_entry", "").strip()
        if content:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO diary (user_id, content) VALUES (%s, %s)",
                    (current_user.id, content)
                )
                conn.commit()
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

        # PostgreSQL にユーザー登録
        with get_conn() as conn, conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed_password)
                )
                conn.commit()
            except psycopg.errors.UniqueViolation:  # UNIQUE制約違反
                conn.rollback()
                flash("そのユーザー名はすでに使われています", "danger")
                return redirect("/register")

        flash("アカウントが作成されました。ログインしてください", "success")
        return redirect("/login")

    return render_template("register.html")

#削除
@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM diary WHERE id = %s AND user_id = %s",
            (id, current_user.id)
        )
        conn.commit()
    return redirect(url_for("home"))

# 編集
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    if request.method == "POST":
        content = request.form.get("diary_entry", "").strip()
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE diary SET content = %s WHERE id = %s AND user_id = %s",
                (content, id, current_user.id)
            )
            conn.commit()
        return redirect(url_for("home"))
    # GET: 既存取得
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, content FROM diary WHERE id = %s AND user_id = %s",
            (id, current_user.id)
        )
        row = cur.fetchone()
    if not row:
        return redirect(url_for("home"))
    return render_template("edit.html", post=row)

if __name__ == "__main__":
    # Render環境では0.0.0.0の指定とportが必要
    import os
    port = int(os.environ.get("PORT", 5000))  # RenderがPORTを環境変数で渡してくれる
    app.run(host="0.0.0.0", port=port, debug=True)