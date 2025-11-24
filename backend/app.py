from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

from backend.assignment_detail_service import get_assignment_detail

# Add parent directory to path for utils import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger, log_startup, log_success, log_error, log_warning, log_info
from utils.logger import setup_logger, log_startup, log_success, log_error, log_warning, log_info
from backend.assignment_detail_service import get_assignment_detail
from backend.db_services import (
    get_courses as db_get_courses,
    add_course as db_add_course,
    update_course as db_update_course,
    delete_course as db_delete_course,
    get_assignments as db_get_assignments,
    add_assignment as db_add_assignment,
    update_assignment as db_update_assignment,
    delete_assignment as db_delete_assignment,
    get_user_assignments as db_get_user_assignments,
)
try:
    # Add backend directory to path for chat_support import
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    from chat_support import chat_with_ai_teacher, clear_ai_conversation, get_ai_system_status
    CHAT_SUPPORT_AVAILABLE = True
except ImportError as e:
    log_warning(f"Chat support not available: {e}")
    CHAT_SUPPORT_AVAILABLE = False

# Load environment variables from both .env and env.yaml
load_dotenv()

# Also load from YAML file
try:
    from utils import load_env_from_yaml
    load_env_from_yaml()
    print("✅ Loaded environment variables from env.yaml")
except Exception as e:
    print(f"⚠️  Could not load env.yaml: {e}")

# Setup logger
logger = setup_logger("LearningApp")

# Import chatbot prompt utilities
try:
    from utils.chatbot_prompt import get_system_prompt, get_user_prompt_template
    CHATBOT_PROMPT_AVAILABLE = True
except ImportError as e:
    log_warning(f"Chatbot prompt utilities not available: {e}")
    CHATBOT_PROMPT_AVAILABLE = False

# Import Ollama for local LLM
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    log_warning("Ollama is not installed. Please install it: pip install ollama")

# Chatbot session storage (in-memory, stores conversation history per session)
chatbot_sessions = {}  # Format: {session_id: [{"role": "user", "content": "message"}, {"role": "assistant", "content": "response"}, ...]}

# Ensure Flask uses the correct templates folder (absolute path)
TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
app = Flask(__name__, template_folder=TEMPLATES_PATH)

# Check required environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    log_error("SECRET_KEY environment variable is not set. Please check your .env file.")
    raise ValueError("SECRET_KEY environment variable is not set. Please check your .env file.")

MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    log_error("MONGO_URI environment variable is not set. Please check your .env file.")
    raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")

# Set Flask secret key
app.secret_key = SECRET_KEY
log_success("Flask secret key configured")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db_name = os.getenv('DB_NAME', 'learning')
    db = client[db_name]
    users_collection = db.users
    courses_collection = db.courses
    assignments_collection = db.assignments
    reports_collection = db.reports
    game_scores_collection = db.game_scores
    log_success(f"Connected to MongoDB database: {db_name}")
except Exception as e:
    log_error(f"Failed to connect to MongoDB: {e}")
    raise

def get_courses(filters=None):
    """Wrapper around db_services.get_courses using global collection."""
    try:
        return db_get_courses(courses_collection, filters)
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return []


def add_course(course_data):
    """Wrapper around db_services.add_course using global collection."""
    try:
        return db_add_course(courses_collection, course_data)
    except Exception as e:
        logger.error(f"Error adding course: {e}")
        return None


def update_course(course_id, course_data):
    """Wrapper around db_services.update_course using global collection."""
    try:
        return db_update_course(courses_collection, course_id, course_data)
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return False


def delete_course(course_id):
    """Wrapper around db_services.delete_course using global collection."""
    try:
        return db_delete_course(courses_collection, course_id)
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        return False


def get_assignments(filters=None):
    """Wrapper around db_services.get_assignments using global collection."""
    try:
        return db_get_assignments(assignments_collection, filters)
    except Exception as e:
        logger.error(f"Error getting assignments: {e}")
        return []


def add_assignment(assignment_data):
    """Wrapper around db_services.add_assignment using global collection."""
    try:
        return db_add_assignment(assignments_collection, assignment_data)
    except Exception as e:
        logger.error(f"Error adding assignment: {e}")
        return None


def update_assignment(assignment_id, assignment_data):
    """Wrapper around db_services.update_assignment using global collection."""
    try:
        return db_update_assignment(assignments_collection, assignment_id, assignment_data)
    except Exception as e:
        logger.error(f"Error updating assignment: {e}")
        return False


def delete_assignment(assignment_id):
    """Wrapper around db_services.delete_assignment using global collection."""
    try:
        return db_delete_assignment(assignments_collection, assignment_id)
    except Exception as e:
        logger.error(f"Error deleting assignment: {e}")
        return False


def get_user_assignments(user_email):
    """Wrapper around db_services.get_user_assignments using global collection."""
    try:
        return db_get_user_assignments(assignments_collection, user_email)
    except Exception as e:
        logger.error(f"Error getting user assignments: {e}")
        return []

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    # Check if it's a valid Indian phone number (10 digits)
    return len(phone_digits) == 10 and phone_digits.isdigit()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@app.route('/')
def index():
    """Serve the main webpage"""
    try:
        # Check if user is logged in, if so redirect to dashboard
        if 'user_id' in session:
            logger.info(f"User {session.get('username', 'Unknown')} is logged in, redirecting to dashboard")
            return redirect('/dashboard')
        
        logger.info("Serving main webpage")
        return render_template('landing.html')
    except Exception as e:
        logger.error(f"Error serving main webpage: {e}")
        return "Error loading webpage.", 500

@app.route('/styles.css')
def styles():
    """Serve the CSS file"""
    try:
        # Get the correct path to the CSS file
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(current_dir, '..', 'webpage', 'styles.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        return css_content, 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        logger.error(f"CSS file not found at: {css_path}")
        return "CSS file not found.", 404

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # No content response

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    try:
        # Get the correct path to the JavaScript file
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, '..', 'webpage', 'script.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        logger.info("Serving JavaScript file")
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        logger.error(f"JavaScript file not found at: {js_path}")
        return "JavaScript file not found.", 404

@app.route('/static/js/<path:filename>')
def static_js(filename):
    """Serve static JavaScript files"""
    try:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, '..', 'static', 'js', filename)
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        logger.info(f"Serving static JavaScript file: {filename}")
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        logger.error(f"Static JavaScript file not found: {filename}")
        return "JavaScript file not found.", 404


@app.route('/login-page', methods=['GET', 'POST'])
def login_page():
    """Serve the login page and handle login form"""
    try:
        if request.method == 'POST':
            # Handle login form submission
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Please fill in all fields', 'error')
                return render_template('login.html')
            
            # Find user in database by email
            user = users_collection.find_one({'email': email})
            
            if user:
                logger.info(f"User found: {email}")
                password_match = check_password_hash(user['password'], password)
                logger.info(f"Password match: {password_match}")
                
                if password_match:
                    session['user_id'] = str(user['_id'])
                    session['email'] = user['email']
                    session['phone'] = user.get('phone', '')
                    session['username'] = user.get('username', user['email'])
                    session['profile'] = user.get('profile', {})
                    flash('🎉 Login successful! Welcome back!', 'success')
                    logger.info(f"✅ User {email} logged in successfully, redirecting to dashboard")
                    return redirect('/dashboard')
                else:
                    flash('❌ Invalid password. Please check your password and try again.', 'error')
                    logger.warning(f"Password mismatch for user: {email}")
                    return render_template('login.html')
            else:
                flash('❌ User not found. Please check your email or sign up for a new account.', 'error')
                logger.warning(f"User not found: {email}")
                return render_template('login.html')
        else:
            logger.info("Serving login page")
            return render_template('login.html')
    except Exception as e:
        logger.error(f"Error serving login page: {e}")
        return "Error loading login page.", 500

@app.route('/signup-page', methods=['GET', 'POST'])
def signup_page():
    """Serve the signup page and handle signup form"""
    try:
        if request.method == 'POST':
            # Handle signup form submission
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            logger.info(f"Signup attempt for email: {email}, phone: {phone}")
            
            # Validation
            if not all([email, phone, password, confirm_password]):
                flash('Please fill in all fields', 'error')
                logger.warning("Signup failed: Missing fields")
                return render_template('signup.html')
            
            if not validate_email(email):
                flash('❌ Please enter a valid email address (e.g., user@example.com)', 'error')
                logger.warning(f"Signup failed: Invalid email: {email}")
                return render_template('signup.html')
            
            if not validate_phone(phone):
                flash('❌ Please enter a valid 10-digit phone number (e.g., 9876543210)', 'error')
                logger.warning(f"Signup failed: Invalid phone: {phone}")
                return render_template('signup.html')
            
            if password != confirm_password:
                flash('❌ Passwords do not match. Please make sure both password fields are identical.', 'error')
                logger.warning(f"Signup failed: Password mismatch for email: {email}")
                return render_template('signup.html')
            
            is_valid_password, password_error = validate_password(password)
            if not is_valid_password:
                flash(f'❌ {password_error}', 'error')
                logger.warning(f"Signup failed: {password_error} for email: {email}")
                return render_template('signup.html')
            
            # Check if user already exists
            existing_user = users_collection.find_one({
                '$or': [
                    {'email': email},
                    {'phone': phone}
                ]
            })
            
            if existing_user:
                if existing_user['email'] == email:
                    flash('❌ This email is already registered. Please use a different email or try logging in.', 'error')
                else:
                    flash('❌ This phone number is already registered. Please use a different phone number.', 'error')
                logger.warning(f"Signup failed: User already exists - email: {email}, phone: {phone}")
                return render_template('signup.html')
            
            # Create new user
            try:
                hashed_password = generate_password_hash(password)
                logger.info(f"Creating user: {email}")

                # Generate username from email
                username = email.split('@')[0]
                
                # Create user data
                user_data = {
                    'email': email,
                    'phone': phone,
                    'password': hashed_password,
                    'username': username,
                    'profile': {
                        'name': '',
                        'bio': '',
                        'location': '',
                        'interests': []
                    },
                    'created_at': datetime.utcnow(),
                    'last_login': None
                }
                
                # Insert user into database
                result = users_collection.insert_one(user_data)
                
                if result.inserted_id:
                    # Set session data
                    session['user_id'] = str(result.inserted_id)
                    session['email'] = email
                    session['phone'] = phone
                    session['username'] = username
                    session['profile'] = user_data['profile']
                    flash('🎉 Account created successfully! Please complete your profile.', 'success')
                    logger.info(f"✅ New user registered successfully: {email} ({phone})")
                    return redirect('/profile-setup')
                else:
                    flash('❌ Failed to create account. Please try again.', 'error')
                    logger.error(f"❌ Failed to create account for: {email}")
                    return render_template('signup.html')
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Signup error for {email}: {error_msg}")
                
                if "E11000" in error_msg:
                    flash('❌ Account already exists with this information. Please try logging in instead.', 'error')
                else:
                    flash('❌ An error occurred while creating your account. Please try again.', 'error')
                
                return render_template('signup.html')
        else:
            logger.info("Serving signup page")
            return render_template('signup.html')
    except Exception as e:
        logger.error(f"Error serving signup page: {e}")
        return "Error loading signup page.", 500

@app.route('/about')
def about_page():
    """Serve the about us page"""
    try:
        logger.info("Serving about page")
        return render_template('about.html')
    except Exception as e:
        logger.error(f"Error serving about page: {e}")
        return "Error loading about page.", 500

@app.route('/profile-setup')
def profile_setup():
    """Serve the profile setup page"""
    try:
        logger.info(f"Profile setup accessed. Session: {dict(session)}")
        
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to profile setup - redirecting to login")
            flash('Please login to access profile setup', 'error')
            return redirect('/login-page')
        
        logger.info(f"Profile setup page served successfully")
        return render_template('profile_setup.html')
        
    except Exception as e:
        logger.error(f"Error serving profile setup page: {e}")
        return f"Error loading profile setup page: {e}", 500

@app.route('/complete-profile', methods=['POST'])
def complete_profile():
    """Handle profile completion form submission"""
    try:
        if 'user_id' not in session:
            flash('Please login to complete your profile', 'error')
            return redirect('/login-page')
        
        # Get form data
        name = request.form.get('name')
        location = request.form.get('location')
        bio = request.form.get('bio')
        
        logger.info(f"Profile completion for user: {session.get('email')}")
        
        # Validate required fields
        if not name or not location:
            flash('❌ Please fill in your name and farm location', 'error')
            return redirect('/profile-setup')
        
        # Update user profile in database
        user_id = session['user_id']
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'profile.name': name,
                    'profile.location': location,
                    'profile.bio': bio or '',
                    'profile_completed': True
                }
            }
        )
        
        # Update session
        session['profile'] = {
            'name': name,
            'location': location,
            'bio': bio or ''
        }
        
        # Add JavaScript to store user data in sessionStorage
        flash('🎉 Profile completed successfully! Welcome to LearningApp!', 'success')
        logger.info(f"✅ Profile completed for user: {session.get('email')}")
        
        # Redirect to dashboard with user data
        response = redirect('/dashboard')
        return response
        
    except Exception as e:
        logger.error(f"Error completing profile: {e}")
        flash('❌ An error occurred. Please try again.', 'error')
        return redirect('/profile-setup')

@app.route('/dashboard')
def dashboard():
    """Serve the learning dashboard"""
    try:
        logger.info(f"Dashboard accessed. Session: {dict(session)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to dashboard - redirecting to login")
            flash('Please login to access the dashboard', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Get user's courses and assignments
        user_courses = get_courses({'instructor': user_name})
        user_assignments = get_user_assignments(user_email)

        # Calculate adaptive stats based on assignments
        ratings = [a.get('rating') for a in user_assignments if a.get('rating') is not None]
        average_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

        completed_assignments = [a for a in user_assignments if a.get('status') == 'completed']
        total_assignments = len(user_assignments) or 1  # avoid divide by zero
        progress_percent = int((len(completed_assignments) / total_assignments) * 100)

        # -------- Global leaderboards for games (tic‑tac‑toe, crossword, word search) --------
        tictactoe_leaderboard = []
        crossword_leaderboard = []
        wordsearch_leaderboard = []
        try:
            def build_game_leaderboard(game_type):
                pipeline = [
                    {"$match": {"game_type": game_type}},
                    {
                        "$group": {
                            "_id": "$student_email",
                            "total_score": {"$sum": "$score"},
                            "games": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total_score": -1}},
                    {"$limit": 5},
                ]
                rows = []
                for doc in game_scores_collection.aggregate(pipeline):
                    email = doc.get("_id") or ""
                    # name stored on score document (fallback to users collection)
                    sample = game_scores_collection.find_one({"student_email": email, "game_type": game_type}) or {}
                    name = sample.get("student_name")
                    if not name:
                        user_doc = users_collection.find_one({"email": email}) or {}
                        name = user_doc.get("username") or user_doc.get("name") or email.split("@")[0]
                    rows.append({
                        "email": email,
                        "name": name,
                        "total_score": float(doc.get("total_score", 0)),
                        "games": int(doc.get("games", 0)),
                    })
                return rows

            tictactoe_leaderboard = build_game_leaderboard("tictactoe")
            crossword_leaderboard = build_game_leaderboard("crossword")
            wordsearch_leaderboard = build_game_leaderboard("wordsearch")
        except Exception as e:
            logger.error(f"Error building game leaderboards: {e}")

        logger.info(f"Serving dashboard for user: {user_name}")
        return render_template(
            'dashboard.html',
            user_email=user_email,
            user_phone=user_phone,
            user_name=user_name,
            user_location=user_location,
            user_bio=user_bio,
            user_courses=user_courses,
            user_assignments=user_assignments,
            average_rating=average_rating,
            progress_percent=progress_percent,
            tictactoe_leaderboard=tictactoe_leaderboard,
            crossword_leaderboard=crossword_leaderboard,
            wordsearch_leaderboard=wordsearch_leaderboard,
        )
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return "Error loading dashboard.", 500

@app.route('/courses')
def courses_page():
    """Courses management page"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to courses page - redirecting to login")
            flash('Please login to access the courses page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Get user's own courses
        user_courses = get_courses({'instructor': user_name})

        # Build per-course progress stats for this user based on assignments
        user_assignments = get_user_assignments(user_email)
        course_progress = {}
        for a in user_assignments:
            course_title = a.get('course')
            if not course_title:
                continue
            stats = course_progress.setdefault(course_title, {
                'total': 0,
                'completed': 0,
                'scores': [],
            })
            stats['total'] += 1
            if a.get('status') == 'completed' and a.get('score') is not None:
                stats['completed'] += 1
                stats['scores'].append(float(a.get('score', 0)))

        for title, stats in course_progress.items():
            scores = stats.get('scores') or []
            stats['avg_score'] = round(sum(scores) / len(scores), 1) if scores else 0.0
            # simple percentage progress: completed / total
            total = max(stats['total'], 1)
            stats['progress_percent'] = int((stats['completed'] / total) * 100)
        
        logger.info(f"Serving courses page for user: {user_name}")
        return render_template(
            'courses.html', 
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio,
            user_courses=user_courses,
            course_progress=course_progress,
        )
    except Exception as e:
        logger.error(f"Error serving courses page: {e}")
        return "Error loading courses page.", 500

@app.route('/assignments')
def assignments_page():
    """Assignments page"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to assignments page - redirecting to login")
            flash('Please login to access the assignments page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Optional filters from query params
        filters = {}
        status = request.args.get('status')
        course = request.args.get('course')
        if status:
            filters['status'] = status
        if course:
            filters['course'] = course
        
        is_admin_flag = session.get('is_admin', False)

        # Students should only see their own assignments.
        # Admins have a separate admin page for managing all assignments.
        if is_admin_flag:
            assignments = get_assignments(filters if filters else None)
        else:
            # Start from user-specific assignments and apply simple in-memory filters.
            assignments = get_user_assignments(user_email)
            if status:
                assignments = [a for a in assignments if a.get('status') == status]
            if course:
                assignments = [a for a in assignments if a.get('course') == course]
        
        logger.info(f"Serving assignments page for user: {user_name}")
        return render_template(
            'assignments.html',
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio,
            assignments=assignments,
            is_admin=is_admin_flag,
        )
    except Exception as e:
        logger.error(f"Error serving assignments page: {e}")
        return "Error loading assignments page.", 500

@app.route('/learn')
def learn_page():
    """Learning materials page"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to learn page - redirecting to login")
            flash('Please login to access the learn page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Get courses from database with filters
        filters = {}
        category = request.args.get('category')
        level = request.args.get('level')
        instructor = request.args.get('instructor')
        
        if category:
            filters['category'] = category
        if level:
            filters['level'] = level
        if instructor:
            filters['instructor'] = instructor
        
        courses = get_courses(filters)
        
        logger.info(f"Serving learn page for user: {user_name}")
        return render_template('learn.html', 
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio,
                             courses=courses)
    except Exception as e:
        logger.error(f"Error serving learn page: {e}")
        return "Error loading learn page.", 500

@app.route('/test-booking')
def test_booking():
    """Test route to check if booking page works"""
    return "Booking page test - this should work!"

@app.route('/debug-session')
def debug_session():
    """Debug route to check session data"""
    return f"Session data: {dict(session)}"

# Courses API Routes
@app.route('/api/courses', methods=['GET'])
def api_get_courses():
    """Get all courses"""
    try:
        courses = get_courses()
        return jsonify({"success": True, "courses": courses})
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/courses', methods=['POST'])
def api_add_course():
    """Add a new course"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'category', 'description', 'level']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        user_name = session.get('profile', {}).get('name', user_email.split('@')[0])
        
        # Create course data
        course_data = {
            'title': data['title'],
            'category': data['category'],
            'description': data['description'],
            'level': data['level'],
            'duration': data.get('duration', ''),
            'instructor': user_name,
            'instructor_email': user_email,
            'enrolled_students': 0,
            'rating': 0,
            'created_at': datetime.utcnow()
        }
        
        # Add to database
        course_id = add_course(course_data)
        
        if course_id:
            course_data['_id'] = course_id
            return jsonify({"success": True, "course": course_data})
        else:
            return jsonify({"success": False, "error": "Failed to add course"}), 500
            
    except Exception as e:
        logger.error(f"Error adding course: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/courses/generate', methods=['POST'])
def api_generate_course():
    """
    Use the local LLM (Ollama) to generate a course automatically.
    The client provides a subject and (optionally) a level; the LLM
    returns a title, description, level, duration and outline.
    """
    try:
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Please install it to enable AI course generation.",
            }), 503

        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        subject = (data.get('subject') or '').strip()
        level = (data.get('level') or '').strip()

        if not subject:
            return jsonify({"success": False, "error": "Subject is required"}), 400

        user_email = session.get('email', 'anonymous@example.com')
        user_name = session.get('profile', {}).get('name', user_email.split('@')[0])

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        system_prompt = (
            "You are an expert curriculum designer for a school/college learning app.\n"
            "Generate ONE well-structured course for the given subject.\n"
            "Respond ONLY with valid JSON, no extra text.\n"
            "JSON keys: title (string), description (string), level (string), "
            "duration (string, like '4 weeks' or '10 lessons'), outline (list of short topic strings).\n"
        )

        user_prompt_parts = [f"Subject: {subject}"]
        if level:
            user_prompt_parts.append(f"Target learner level: {level}")
        user_prompt_parts.append(
            "Course should be practical, engaging, and suitable for MCQ and assignment-based practice."
        )
        user_prompt = "\n".join(user_prompt_parts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for course generation: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to generate course using the LLM",
            }), 500

        import json

        try:
            generated = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning(f"Course LLM did not return strict JSON, raw: {raw_content[:200]}...")
            # Simple fallback structure
            generated = {
                "title": f"{subject} Fundamentals",
                "description": f"Auto-generated {subject} course.",
                "level": level or "beginner",
                "duration": "4 weeks",
                "outline": [],
            }

        title = generated.get("title") or f"{subject} Course"
        description = generated.get("description") or f"Learn {subject} step by step."
        gen_level = generated.get("level") or (level or "beginner")
        duration = generated.get("duration") or "Self-paced"
        outline = generated.get("outline") or []

        # Build course data using the same structure as manual creation
        course_data = {
            'title': title,
            'category': subject,
            'description': description,
            'level': gen_level,
            'duration': duration,
            'instructor': user_name,
            'instructor_email': user_email,
            'enrolled_students': 0,
            'rating': 0,
            'created_at': datetime.utcnow(),
            'outline': outline,
        }

        course_id = add_course(course_data)
        if course_id:
            course_data['_id'] = course_id
            return jsonify({"success": True, "course": course_data})
        else:
            return jsonify({"success": False, "error": "Failed to save generated course"}), 500
    except Exception as e:
        logger.error(f"Error generating course with LLM: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/courses/<course_id>', methods=['PUT'])
def api_update_course(course_id):
    """Update a course"""
    try:
        data = request.get_json()
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the instructor
        from bson import ObjectId
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            return jsonify({"success": False, "error": "Course not found"}), 404
        
        if course.get('instructor_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to edit this course"}), 403
        
        # Update data
        update_data = {
            'title': data.get('title', course['title']),
            'category': data.get('category', course['category']),
            'description': data.get('description', course['description']),
            'level': data.get('level', course['level']),
            'duration': data.get('duration', course.get('duration', '')),
            'updated_at': datetime.utcnow()
        }
        
        success = update_course(course_id, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Course updated successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to update course"}), 500
            
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/courses/<course_id>', methods=['DELETE'])
def api_delete_course(course_id):
    """Delete a course"""
    try:
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the instructor
        from bson import ObjectId
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            return jsonify({"success": False, "error": "Course not found"}), 404
        
        if course.get('instructor_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to delete this course"}), 403
        
        success = delete_course(course_id)
        
        if success:
            return jsonify({"success": True, "message": "Course deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete course"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Assignments API Routes
@app.route('/api/assignments', methods=['GET'])
def api_get_assignments():
    """Get all assignments with optional filters"""
    try:
        # Get query parameters for filtering
        course = request.args.get('course')
        status = request.args.get('status')
        due_date = request.args.get('due_date')
        
        filters = {}
        if course:
            filters['course'] = course
        if status:
            filters['status'] = status
        if due_date:
            filters['due_date'] = due_date
        
        assignments = get_assignments(filters)
        return jsonify({"success": True, "assignments": assignments})
    except Exception as e:
        logger.error(f"Error getting assignments: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/assignments', methods=['POST'])
def api_add_assignment():
    """Add a new assignment"""
    try:
        data = request.get_json()
        logger.info(f"Received assignment data: {data}")
        
        # Validate required fields
        required_fields = ['title', 'course', 'description', 'due_date']
        for field in required_fields:
            if field not in data or not data[field]:
                logger.error(f"Missing required field: {field}")
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        user_name = session.get('profile', {}).get('name', user_email.split('@')[0])
        
        # Create assignment data
        assignment_data = {
            'title': data['title'],
            'course': data['course'],
            'description': data['description'],
            'due_date': data['due_date'],
            'points': int(data.get('points', 100)),
            'status': data.get('status', 'pending'),
            'instructor_name': user_name,
            'instructor_email': user_email,
            'student_email': data.get('student_email', ''),
            'difficulty_level': int(data.get('difficulty_level', 1)),
            # Fields used later for grading / adaptive learning
            'question': data.get('question', data['description']),
            'expected_answer': data.get('expected_answer', ''),
            'score': None,
            'rating': None,
            'feedback': '',
            'created_at': datetime.utcnow()
        }
        
        # Add to database
        assignment_id = add_assignment(assignment_data)
        
        if assignment_id:
            assignment_data['_id'] = assignment_id
            return jsonify({"success": True, "assignment": assignment_data})
        else:
            return jsonify({"success": False, "error": "Failed to add assignment"}), 500
            
    except Exception as e:
        logger.error(f"Error adding assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/assignments/<assignment_id>', methods=['PUT'])
def api_update_assignment(assignment_id):
    """Update an assignment"""
    try:
        data = request.get_json()
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the instructor
        from bson import ObjectId
        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404
        
        if assignment.get('instructor_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to edit this assignment"}), 403
        
        # Update data
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'course' in data:
            update_data['course'] = data['course']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'due_date' in data:
            update_data['due_date'] = data['due_date']
        if 'points' in data:
            update_data['points'] = int(data['points'])
        if 'status' in data:
            update_data['status'] = data['status']
        if 'difficulty_level' in data:
            update_data['difficulty_level'] = int(data['difficulty_level'])
        if 'question' in data:
            update_data['question'] = data['question']
        if 'expected_answer' in data:
            update_data['expected_answer'] = data['expected_answer']
        
        update_data['updated_at'] = datetime.utcnow()
        
        success = update_assignment(assignment_id, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Assignment updated successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to update assignment"}), 500
            
    except Exception as e:
        logger.error(f"Error updating assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/assignments/<assignment_id>', methods=['DELETE'])
def api_delete_assignment(assignment_id):
    """Delete an assignment"""
    try:
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the instructor
        from bson import ObjectId
        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404
        
        if assignment.get('instructor_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to delete this assignment"}), 403
        
        success = delete_assignment(assignment_id)
        
        if success:
            return jsonify({"success": True, "message": "Assignment deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete assignment"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/generate', methods=['POST'])
def api_generate_assignment():
    """
    Use the local LLM (Ollama) to generate an assignment question for a course.
    This endpoint only generates the content; the caller is responsible for
    saving it via /api/assignments.
    """
    try:
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Please install it to enable AI assignment generation."
            }), 503

        data = request.get_json() or {}
        course_title = data.get('course') or data.get('course_title')
        topic = data.get('topic') or data.get('title')
        difficulty_level = int(data.get('difficulty_level', 1))

        if not course_title:
            return jsonify({"success": False, "error": "Course title is required"}), 400

        # Try to load course details to give more context to the model
        course = courses_collection.find_one({"title": course_title})
        course_description = course.get('description', '') if course else ''
        course_level = course.get('level', '') if course else ''

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        # Build a very constrained prompt so we can parse JSON safely
        system_prompt = (
            "You are an expert teacher creating high‑quality assignments.\n"
            "Generate ONE assignment question for the given course and topic.\n"
            "Respond ONLY with valid JSON, no extra text.\n"
            "JSON keys: title, question, sample_answer, points, difficulty_level.\n"
            "difficulty_level is an integer from 1 (easy) to 5 (hard)."
        )

        user_prompt_parts = [
            f"Course title: {course_title}",
        ]
        if course_description:
            user_prompt_parts.append(f"Course description: {course_description}")
        if course_level:
            user_prompt_parts.append(f"Course level: {course_level}")
        if topic:
            user_prompt_parts.append(f"Assignment topic: {topic}")
        user_prompt_parts.append(f"Target difficulty_level: {difficulty_level}")

        user_prompt = "\n".join(user_prompt_parts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for assignment generation: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to generate assignment using the LLM",
            }), 500

        import json

        generated = {}
        try:
            # Try to parse as JSON directly
            generated = json.loads(raw_content)
        except json.JSONDecodeError:
            # Fallback: wrap the whole content as a question
            logger.warning(f"LLM did not return strict JSON, using fallback. Raw: {raw_content[:200]}...")
            generated = {
                "title": topic or f"{course_title} assignment (AI generated)",
                "question": raw_content,
                "sample_answer": "",
                "points": 100,
                "difficulty_level": difficulty_level,
            }

        # Normalise fields and defaults
        title = generated.get("title") or (topic or f"{course_title} assignment")
        question = generated.get("question") or generated.get("prompt") or ""
        sample_answer = generated.get("sample_answer") or ""
        points = int(generated.get("points") or 100)
        difficulty = int(generated.get("difficulty_level") or difficulty_level)

        return jsonify({
            "success": True,
            "generated": {
                "title": title,
                "question": question,
                "sample_answer": sample_answer,
                "points": points,
                "difficulty_level": difficulty,
            },
        })
    except Exception as e:
        logger.error(f"Error generating assignment with LLM: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/<assignment_id>/detail', methods=['GET'])
def api_get_assignment_detail(assignment_id):
    """
    Get full details for an assignment so the UI can show:
    - For MCQ quizzes: each question, which options were correct/incorrect, and the user's answers
    - For normal assignments: question/description, user's answer, marks, rating and feedback
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from bson import ObjectId

        user_email = session.get("email", "anonymous@example.com")
        is_admin = session.get("is_admin", False)

        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        # Only admin or the owner student can view the assignment detail
        if not is_admin and assignment.get("student_email") != user_email:
            return jsonify({"success": False, "error": "Not authorized to view this assignment"}), 403

        detail = get_assignment_detail(assignments_collection, assignment_id)
        if detail is None:
            return jsonify({"success": False, "error": "Assignment not found"}), 404
        return jsonify({"success": True, "assignment": detail})
    except Exception as e:
        logger.error(f"Error getting assignment detail: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/games/flashcards', methods=['POST'])
def api_generate_flashcards():
    """
    Generate short Q/A flashcards for a given subject and level using the LLM.
    Used by the Study Games page (Learn tab).
    """
    try:
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Flashcard game is unavailable.",
            }), 503

        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        subject = (data.get('subject') or '').strip()
        level = (data.get('level') or '').strip() or "beginner"

        if not subject:
            return jsonify({"success": False, "error": "Subject is required"}), 400

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        system_prompt = (
            "You are a friendly teacher creating short study puzzles.\n"
            "Each puzzle is a single-question riddle, word problem or conceptual check.\n"
            "Return ONLY valid JSON (no explanation text), representing a list of puzzles.\n"
            "Each item must have: question (string) and answer (string).\n"
            "Keep questions simple but slightly challenging. 1 short line for the question, 1–3 sentences for the answer."
        )

        user_prompt = (
            f"Create 6 study puzzles for subject: {subject}.\n"
            f"Learner level: {level}.\n"
            "Mix different concepts. Some can be numeric problems, some definition puzzles, some 'which concept am I' riddles.\n"
            "Format as a JSON array, e.g.\n"
            '[{\"question\": \"...\", \"answer\": \"...\"}, ...]'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for flashcards: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to generate flashcards using the AI tutor.",
            }), 500

        import json

        try:
            parsed = json.loads(raw_content)
            if isinstance(parsed, dict) and "flashcards" in parsed:
                cards = parsed.get("flashcards") or []
            elif isinstance(parsed, list):
                cards = parsed
            else:
                cards = []
        except json.JSONDecodeError:
            logger.warning(f"Flashcard JSON parse failed, raw: {raw_content[:200]}...")
            cards = []

        flashcards = []
        for c in cards:
            q = (c.get("question") or "").strip()
            a = (c.get("answer") or "").strip()
            if q and a:
                flashcards.append({"question": q, "answer": a})

        if not flashcards:
            # Simple fallback if parsing failed or model misbehaved
            flashcards = [
                {
                    "question": f"What is one key concept in {subject}?",
                    "answer": f"This depends on your syllabus, but an important idea in {subject} is often introduced at the {level} level.",
                }
            ]

        return jsonify({"success": True, "flashcards": flashcards}), 200
    except Exception as e:
        logger.error(f"Error in flashcard game endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/games/crossword', methods=['POST'])
def api_generate_crossword():
    """
    Generate simple crossword-style entries (word + clue) for a subject/level.
    The frontend renders these as rows of boxes similar to a crossword.
    """
    try:
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Crossword game is unavailable.",
            }), 503

        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        subject = (data.get('subject') or '').strip()
        level = (data.get('level') or '').strip() or "beginner"

        if not subject:
            return jsonify({"success": False, "error": "Subject is required"}), 400

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        system_prompt = (
            "You are a teacher creating a small crossword puzzle.\n"
            "Return ONLY valid JSON (no explanation text).\n"
            "JSON format: {\"entries\": [{\"clue\": \"...\", \"answer\": \"WORD\"}, ...]}\n"
            "Rules for each answer:\n"
            "- One single word, only A-Z letters, no spaces, no hyphens.\n"
            "- 3 to 10 letters long.\n"
        )

        user_prompt = (
            f"Create 6 crossword entries for subject: {subject}.\n"
            f"Learner level: {level}.\n"
            "Clues should be short and simple.\n"
            "Answers must follow the rules and be related to the subject."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for crossword: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to generate crossword using the AI tutor.",
            }), 500

        import json

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            # Try to salvage JSON array/object from within the text
            logger.warning(f"Crossword JSON parse failed, raw: {raw_content[:200]}...")
            first_brace = raw_content.find('{')
            last_brace = raw_content.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                try:
                    trimmed = raw_content[first_brace:last_brace + 1]
                    parsed = json.loads(trimmed)
                    logger.info("Recovered crossword JSON after trimming surrounding text.")
                except json.JSONDecodeError:
                    return jsonify({
                        "success": False,
                        "error": "AI did not return valid JSON for crossword. Please try again.",
                    }), 500
            else:
                return jsonify({
                    "success": False,
                    "error": "AI did not return valid JSON for crossword. Please try again.",
                }), 500

        entries_raw = []
        if isinstance(parsed, dict) and "entries" in parsed:
            entries_raw = parsed.get("entries") or []
        elif isinstance(parsed, list):
            entries_raw = parsed

        entries = []
        for e in entries_raw:
            clue = (e.get("clue") or "").strip()
            answer = (e.get("answer") or "").strip().upper()
            if not clue or not answer:
                continue
            # Keep only letters, remove other characters and spaces
            import re
            answer_clean = re.sub(r'[^A-Z]', '', answer)
            if len(answer_clean) < 3 or len(answer_clean) > 10:
                continue
            entries.append({
                "clue": clue,
                "answer": answer_clean,
            })
            if len(entries) == 6:
                break

        if not entries:
            return jsonify({
                "success": False,
                "error": "Failed to generate valid crossword entries. Please try again.",
            }), 500

        return jsonify({"success": True, "entries": entries}), 200
    except Exception as e:
        logger.error(f"Error in crossword game endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/games/crossword/score', methods=['POST'])
def api_record_crossword_score():
    """Record crossword score for leaderboard."""
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        correct = int(data.get("correct") or 0)
        total = int(data.get("total") or 0)
        seconds = int(data.get("seconds") or 0)
        if seconds < 1:
            seconds = 1

        user_email = session.get('email', 'anonymous@example.com')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])

        # Time-based score: more correct words and less time -> higher score
        # Example: score = correct * (120 / seconds), capped to avoid extreme values
        from math import inf
        time_factor = 120.0 / float(seconds)
        if time_factor < 0.5:
            time_factor = 0.5
        if time_factor > 3.0:
            time_factor = 3.0
        score_value = float(correct) * time_factor

        game_scores_collection.insert_one({
            "game_type": "crossword",
            "student_email": user_email,
            "student_name": user_name,
            "score": score_value,
            "max_score": total,
            "words_correct": correct,
            "time_seconds": seconds,
            "created_at": datetime.utcnow(),
        })

        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"Error recording crossword score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/games/wordsearch', methods=['POST'])
def api_generate_wordsearch():
    """
    Generate a list of subject-related words for the word search game.
    Frontend will arrange them in a grid.
    """
    try:
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Word search game is unavailable.",
            }), 503

        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        subject = (data.get('subject') or '').strip()
        level = (data.get('level') or '').strip() or "beginner"

        if not subject:
            return jsonify({"success": False, "error": "Subject is required"}), 400

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        system_prompt = (
            "You are helping to create a word search puzzle for students.\n"
            "Return ONLY valid JSON with this format:\n"
            "{\"words\": [\"WORD1\", \"WORD2\", ...]}\n"
            "Rules:\n"
            "- Each word: single word, only A-Z letters, no spaces.\n"
            "- Length 3–10 letters.\n"
        )

        user_prompt = (
            f"Create 8 distinct words related to subject: {subject} for {level} learners.\n"
            "Mix concepts (objects, processes, people, places) that students can find in a word search."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 256,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for wordsearch: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to generate word search words using the AI tutor.",
            }), 500

        import json, re

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning(f"Wordsearch JSON parse failed, raw: {raw_content[:200]}...")
            first_brace = raw_content.find('{')
            last_brace = raw_content.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                try:
                    trimmed = raw_content[first_brace:last_brace + 1]
                    parsed = json.loads(trimmed)
                    logger.info("Recovered wordsearch JSON after trimming surrounding text.")
                except json.JSONDecodeError:
                    return jsonify({
                        "success": False,
                        "error": "AI did not return valid JSON for word search. Please try again.",
                    }), 500
            else:
                return jsonify({
                    "success": False,
                    "error": "AI did not return valid JSON for word search. Please try again.",
                }), 500

        words_raw = []
        if isinstance(parsed, dict) and "words" in parsed:
            words_raw = parsed.get("words") or []
        elif isinstance(parsed, list):
            words_raw = parsed

        words: list[str] = []
        for w in words_raw:
            word = str(w).strip().upper()
            word = re.sub(r'[^A-Z]', '', word)
            if len(word) < 3 or len(word) > 10:
                continue
            if word not in words:
                words.append(word)
            if len(words) == 8:
                break

        if not words:
            return jsonify({
                "success": False,
                "error": "Failed to generate valid words for word search. Please try again.",
            }), 500

        return jsonify({"success": True, "words": words}), 200
    except Exception as e:
        logger.error(f"Error in wordsearch game endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/games/wordsearch/score', methods=['POST'])
def api_record_wordsearch_score():
    """Record word search score for leaderboard."""
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        found = int(data.get("found") or 0)
        total = int(data.get("total") or 0)
        seconds = int(data.get("seconds") or 0)
        if seconds < 1:
            seconds = 1

        user_email = session.get('email', 'anonymous@example.com')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])

        # Time-based score: more found words and less time -> higher score
        time_factor = 120.0 / float(seconds)
        if time_factor < 0.5:
            time_factor = 0.5
        if time_factor > 3.0:
            time_factor = 3.0
        score_value = float(found) * time_factor

        game_scores_collection.insert_one({
            "game_type": "wordsearch",
            "student_email": user_email,
            "student_name": user_name,
            "score": score_value,
            "max_score": total,
            "words_found": found,
            "time_seconds": seconds,
            "created_at": datetime.utcnow(),
        })

        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"Error recording wordsearch score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/games/tictactoe/score', methods=['POST'])
def api_record_tictactoe_score():
    """Record tic tac toe score for leaderboard."""
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json() or {}
        result = (data.get("result") or "").strip().lower()

        # Simple scoring: win = 3, draw = 1, loss = 0
        score_map = {"win": 3, "draw": 1, "loss": 0}
        score = score_map.get(result, 0)

        user_email = session.get('email', 'anonymous@example.com')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])

        game_scores_collection.insert_one({
            "game_type": "tictactoe",
            "student_email": user_email,
            "student_name": user_name,
            "score": float(score),
            "max_score": 3.0,
            "result": result,
            "created_at": datetime.utcnow(),
        })

        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"Error recording tictactoe score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/<assignment_id>/report', methods=['POST'])
def api_report_assignment(assignment_id):
    """
    Allow a student to report a problem with an assignment (any type).
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from bson import ObjectId

        data = request.get_json() or {}
        reason = (data.get('reason') or '').strip()

        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        report_doc = {
            "type": "assignment",
            "assignment_id": str(assignment["_id"]),
            "course": assignment.get("course", ""),
            "title": assignment.get("title", ""),
            "student_email": session.get("email", "anonymous@example.com"),
            "student_name": session.get("profile", {}).get("name", session.get("username", "")),
            "reason": reason or "Student reported an issue with this assignment.",
            "status": "open",
            "created_at": datetime.utcnow(),
        }
        result = reports_collection.insert_one(report_doc)

        return jsonify({"success": True, "report_id": str(result.inserted_id)})
    except Exception as e:
        logger.error(f"Error reporting assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/<assignment_id>/questions/<int:question_index>/report', methods=['POST'])
def api_report_assignment_question(assignment_id, question_index):
    """
    Allow a student to report a specific question in an MCQ quiz assignment.
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from bson import ObjectId

        data = request.get_json() or {}
        reason = (data.get('reason') or '').strip()

        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        if assignment.get("assignment_type") != "quiz_mcq":
            return jsonify({"success": False, "error": "This assignment is not an MCQ quiz"}), 400

        questions = assignment.get("question_set") or []
        if question_index < 0 or question_index >= len(questions):
            return jsonify({"success": False, "error": "Question index out of range"}), 400

        q = questions[question_index]
        results = assignment.get("results") or []
        user_answer = None
        is_correct = None
        explanation = ""
        if 0 <= question_index < len(results):
            r = results[question_index]
            user_answer = r.get("user_answer")
            is_correct = r.get("is_correct")
            explanation = r.get("explanation", "")

        report_doc = {
            "type": "question",
            "assignment_id": str(assignment["_id"]),
            "question_index": question_index,
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct_index": q.get("correct_index", 0),
            "student_email": session.get("email", "anonymous@example.com"),
            "student_name": session.get("profile", {}).get("name", session.get("username", "")),
            "student_answer": user_answer,
            "is_correct": is_correct,
            "explanation": explanation,
            "reason": reason or "Student reported an issue with this MCQ question.",
            "status": "open",
            "created_at": datetime.utcnow(),
        }
        result = reports_collection.insert_one(report_doc)

        return jsonify({"success": True, "report_id": str(result.inserted_id)})
    except Exception as e:
        logger.error(f"Error reporting assignment question: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ----------------------------- ADMIN SUPPORT -----------------------------
from functools import wraps


def is_admin():
    return session.get("is_admin", False)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_admin():
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return wrapper


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """
    Simple admin login using fixed credentials:
    username: rohit
    password: baniya
    """
    try:
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')

            if username == 'rohit' and password == 'baniya':
                session['is_admin'] = True
                flash('Admin login successful.', 'success')
                return redirect('/admin')
            else:
                flash('Invalid admin credentials.', 'error')

        return render_template('admin_login.html')
    except Exception as e:
        logger.error(f"Error in admin_login: {e}")
        return "Error loading admin login page.", 500


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Admin logged out.', 'success')
    return redirect('/admin-login')


@app.route('/admin')
@admin_required
def admin_dashboard():
    """
    Admin dashboard showing all students, assignments, and reports.
    """
    try:
        # Users
        users = list(users_collection.find({}, {'password': 0}).sort('created_at', -1))
        for u in users:
            u['_id'] = str(u['_id'])

        # Assignments
        assignments = list(assignments_collection.find().sort('created_at', -1))
        for a in assignments:
            a['_id'] = str(a['_id'])

        # Reports
        reports = list(reports_collection.find().sort('created_at', -1))
        for r in reports:
            r['_id'] = str(r['_id'])

        return render_template(
            'admin.html',
            users=users,
            assignments=assignments,
            reports=reports,
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}")
        return "Error loading admin dashboard.", 500


@app.route('/admin/users/<user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    try:
        from bson import ObjectId
        users_collection.delete_one({'_id': ObjectId(user_id)})
        flash('User deleted successfully.', 'success')
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        flash('Failed to delete user.', 'error')
    return redirect('/admin')


@app.route('/admin/assignments/<assignment_id>/delete', methods=['POST'])
@admin_required
def admin_delete_assignment(assignment_id):
    try:
        from bson import ObjectId
        assignments_collection.delete_one({'_id': ObjectId(assignment_id)})
        flash('Assignment deleted successfully.', 'success')
    except Exception as e:
        logger.error(f"Error deleting assignment {assignment_id}: {e}")
        flash('Failed to delete assignment.', 'error')
    return redirect('/admin')


@app.route('/admin/assignments/<assignment_id>/update-marks', methods=['POST'])
@admin_required
def admin_update_assignment_marks(assignment_id):
    """
    Allow admin to manually adjust marks and rating for an assignment.
    """
    try:
        from bson import ObjectId

        score_raw = request.form.get('score')
        rating_raw = request.form.get('rating')
        updates = {}
        if score_raw is not None and score_raw != '':
            try:
                updates['score'] = float(score_raw)
            except ValueError:
                pass
        if rating_raw is not None and rating_raw != '':
            try:
                updates['rating'] = float(rating_raw)
            except ValueError:
                pass

        if updates:
            updates['updated_at'] = datetime.utcnow()
            assignments_collection.update_one(
                {'_id': ObjectId(assignment_id)},
                {'$set': updates},
            )
            flash('Assignment marks updated.', 'success')
        else:
            flash('No valid marks provided to update.', 'warning')
    except Exception as e:
        logger.error(f"Error updating marks for assignment {assignment_id}: {e}")
        flash('Failed to update assignment marks.', 'error')
    return redirect('/admin')


@app.route('/admin/assignments/<assignment_id>/review', methods=['GET', 'POST'])
@admin_required
def admin_review_assignment(assignment_id):
    """
    Interactive review page for a quiz assignment.
    Admin can mark each MCQ question as correct/incorrect and we
    recompute the total score and rating.
    """
    try:
        from bson import ObjectId

        assignment = assignments_collection.find_one({'_id': ObjectId(assignment_id)})
        if not assignment:
            flash('Assignment not found.', 'error')
            return redirect('/admin')

        if request.method == 'POST':
            # Only meaningful for MCQ quizzes with results
            if assignment.get('assignment_type') == 'quiz_mcq':
                results = assignment.get('results') or []
                if results:
                    # Update is_correct per checkbox
                    for idx, r in enumerate(results):
                        field = f"q_correct_{idx}"
                        r['is_correct'] = field in request.form

                    # Recompute score and rating
                    correct_count = sum(1 for r in results if r.get('is_correct'))
                    num_questions = len(results) or 1
                    new_score = float(correct_count)
                    new_rating = (new_score / float(num_questions)) * 5.0
                    if new_rating > 5:
                        new_rating = 5.0
                    if new_rating < 0:
                        new_rating = 0.0

                    assignments_collection.update_one(
                        {'_id': assignment['_id']},
                        {
                            '$set': {
                                'score': new_score,
                                'rating': new_rating,
                                'results': results,
                                'updated_at': datetime.utcnow(),
                            }
                        },
                    )
                    flash('Question marks updated and score recalculated.', 'success')

            return redirect(f'/admin/assignments/{assignment_id}/review')

        # GET: render page
        results = assignment.get('results') or []
        # Convert ObjectId to string for template
        assignment['_id'] = str(assignment['_id'])
        return render_template(
            'admin_assignment_review.html',
            assignment=assignment,
            results=results,
        )
    except Exception as e:
        logger.error(f"Error reviewing assignment {assignment_id}: {e}")
        flash('Failed to load assignment review page.', 'error')
        return redirect('/admin')


@app.route('/admin/reports/<report_id>/resolve', methods=['POST'])
@admin_required
def admin_resolve_report(report_id):
    """
    Mark a report as resolved. Optionally adjust assignment marks.
    - For assignment-level reports: admin can manually set new score/rating.
    - For question-level reports on MCQ quizzes: if no manual score is provided,
      the reported question is automatically treated as correct and the quiz
      score/rating are recomputed.
    """
    try:
        from bson import ObjectId

        report = reports_collection.find_one({'_id': ObjectId(report_id)})
        if not report:
            flash('Report not found.', 'error')
            return redirect('/admin')

        assignment_id = report.get('assignment_id')
        if not assignment_id:
            flash('Report has no assignment id.', 'error')
            return redirect('/admin')

        assignment = assignments_collection.find_one({'_id': ObjectId(assignment_id)})
        if not assignment:
            flash('Related assignment not found.', 'error')
            return redirect('/admin')

        score_raw = request.form.get('score')
        rating_raw = request.form.get('rating')

        manual_updates: dict = {}
        if score_raw:
            try:
                manual_updates['score'] = float(score_raw)
            except ValueError:
                pass
        if rating_raw:
            try:
                manual_updates['rating'] = float(rating_raw)
            except ValueError:
                pass

        # If admin provided explicit marks, just apply them.
        if manual_updates:
            manual_updates['updated_at'] = datetime.utcnow()
            assignments_collection.update_one(
                {'_id': assignment['_id']},
                {'$set': manual_updates},
            )
        else:
            # For MCQ question reports, auto grant credit for that question and recompute score/rating.
            if (
                report.get('type') == 'question'
                and assignment.get('assignment_type') == 'quiz_mcq'
            ):
                question_index = report.get('question_index')
                results = assignment.get('results') or []
                if (
                    isinstance(question_index, int)
                    and 0 <= question_index < len(results)
                ):
                    # Mark this question as correct
                    results[question_index]['is_correct'] = True
                    # Recompute total correct answers
                    correct_count = sum(
                        1 for r in results if r.get('is_correct')
                    )
                    num_questions = len(results) or 1
                    new_score = float(correct_count)
                    new_rating = (new_score / float(num_questions)) * 5.0
                    if new_rating > 5:
                        new_rating = 5.0
                    if new_rating < 0:
                        new_rating = 0.0

                    assignments_collection.update_one(
                        {'_id': assignment['_id']},
                        {
                            '$set': {
                                'score': new_score,
                                'rating': new_rating,
                                'results': results,
                                'updated_at': datetime.utcnow(),
                            }
                        },
                    )

        # Finally, mark report as resolved
        reports_collection.update_one(
            {'_id': ObjectId(report_id)},
            {
                '$set': {
                    'status': 'resolved',
                    'resolved_at': datetime.utcnow(),
                }
            },
        )

        flash('Report has been marked as resolved.', 'success')
    except Exception as e:
        logger.error(f"Error resolving report {report_id}: {e}")
        flash('Failed to resolve report.', 'error')
    return redirect('/admin')


@app.route('/api/assignments/<assignment_id>/submit', methods=['POST'])
def api_submit_assignment(assignment_id):
    """
    Submit a student's answer for an assignment.
    Uses the local LLM to grade the answer, assign marks and a 0‑5 rating,
    and (optionally) updates course rating and difficulty level.
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Please install it to enable AI grading.",
            }), 503

        from bson import ObjectId

        data = request.get_json() or {}
        student_answer = (data.get('answer') or '').strip()
        generate_next = bool(data.get('generate_next', True))

        if not student_answer:
            return jsonify({"success": False, "error": "Answer is required"}), 400

        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        # Bind assignment to this student if not already set
        student_email = session.get('email', 'anonymous@example.com')
        if not assignment.get('student_email'):
            assignments_collection.update_one(
                {"_id": assignment["_id"]},
                {"$set": {"student_email": student_email}},
            )
            assignment['student_email'] = student_email

        max_points = int(assignment.get('points', 100))
        difficulty_level = int(assignment.get('difficulty_level', 1))
        question_text = assignment.get('question') or assignment.get('description') or ''
        expected_answer = assignment.get('expected_answer', '')
        course_title = assignment.get('course', '')

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        system_prompt = (
            "You are a strict but fair teacher grading a student's assignment.\n"
            "Given the question, the expected answer (if provided), and the student's answer,\n"
            "you must grade the answer and respond ONLY with valid JSON.\n"
            "JSON keys: score (0‑{max_points}), rating (0‑5, float), feedback (string), next_difficulty_level (int 1‑5).\n"
            "Do not include any explanation outside the JSON."
        ).format(max_points=max_points)

        user_prompt_parts = [
            f"Question: {question_text}",
        ]
        if expected_answer:
            user_prompt_parts.append(f"Expected answer (for reference): {expected_answer}")
        user_prompt_parts.append(f"Max points: {max_points}")
        user_prompt_parts.append(f"Current difficulty_level: {difficulty_level}")
        user_prompt_parts.append(f"Student's answer: {student_answer}")

        user_prompt = "\n".join(user_prompt_parts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.3,  # lower temperature for more deterministic grading
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for grading: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to grade assignment using the LLM",
            }), 500

        import json

        try:
            grading = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning(f"Grading JSON parse failed, raw: {raw_content[:200]}...")
            # Very simple heuristic fallback: full marks if non‑empty answer
            grading = {
                "score": max_points if len(student_answer) > 20 else max_points // 2,
                "rating": 5.0 if len(student_answer) > 20 else 3.0,
                "feedback": "Automatic fallback grading applied due to parsing error.",
                "next_difficulty_level": difficulty_level + 1,
            }

        score = float(grading.get("score", 0))
        # Clamp score into valid range
        if score < 0:
            score = 0
        if score > max_points:
            score = max_points

        rating = float(grading.get("rating", 0))
        if rating < 0:
            rating = 0
        if rating > 5:
            rating = 5

        feedback = grading.get("feedback", "")
        next_difficulty_level = int(grading.get("next_difficulty_level", difficulty_level))
        if next_difficulty_level < 1:
            next_difficulty_level = 1
        if next_difficulty_level > 5:
            next_difficulty_level = 5

        # Update the assignment with grading results
        update_doc = {
            "student_answer": student_answer,
            "score": score,
            "rating": rating,
            "feedback": feedback,
            "status": "completed",
            "difficulty_level": difficulty_level,
            "completed_at": datetime.utcnow(),
        }
        assignments_collection.update_one({"_id": assignment["_id"]}, {"$set": update_doc})

        # Recalculate course-level rating based on all graded assignments for this course
        if course_title:
            try:
                pipeline = [
                    {"$match": {"course": course_title, "rating": {"$ne": None}}},
                    {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}},
                ]
                agg = list(assignments_collection.aggregate(pipeline))
                if agg:
                    avg_rating = float(agg[0]["avg_rating"])
                    courses_collection.update_one(
                        {"title": course_title},
                        {"$set": {"rating": avg_rating}},
                    )
            except Exception as e:
                logger.warning(f"Failed to update course rating for {course_title}: {e}")

        result = {
            "assignment_id": assignment_id,
            "score": score,
            "max_points": max_points,
            "rating": rating,
            "feedback": feedback,
            "difficulty_level": difficulty_level,
            "next_difficulty_level": next_difficulty_level,
        }

        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Error submitting assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/quiz/start', methods=['POST'])
def api_start_quiz_assignment():
    """
    Start a 10-question MCQ quiz for a given subject (course).
    - Chooses the level automatically based on how many quiz assignments the
      student has already completed for that course (level = completed + 1).
    - Uses the local LLM to generate 10 MCQ questions.
    - Stores the quiz (including correct answers) as an assignment document.
    - Returns the questions WITHOUT correct answers to the frontend.
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Please install it to enable AI MCQ generation.",
            }), 503

        data = request.get_json() or {}
        course_title = data.get('course') or data.get('course_title')

        if not course_title:
            return jsonify({"success": False, "error": "Course title is required"}), 400

        user_email = session.get('email', 'anonymous@example.com')

        # Determine current level for this user & course based on completed quizzes
        completed_count = assignments_collection.count_documents({
            "course": course_title,
            "student_email": user_email,
            "assignment_type": "quiz_mcq",
            "status": "completed",
        })
        level = int(completed_count) + 1

        # Try to load course details to give more context to the model
        course = courses_collection.find_one({"title": course_title})
        course_description = course.get('description', '') if course else ''
        course_level = course.get('level', '') if course else ''

        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')

        system_prompt = (
            "You are an expert teacher creating multiple-choice quizzes.\n"
            "Generate EXACTLY 10 MCQ questions for the given course and level.\n"
            "Each question must have 4 options.\n"
            "Respond ONLY with valid JSON, no extra text.\n"
            'JSON format:\n'
            '{\n'
            '  \"level\": <int>,\n'
            '  \"questions\": [\n'
            '    {\"question\": \"...\", \"options\": [\"opt1\", \"opt2\", \"opt3\", \"opt4\"], \"correct_index\": 0},\n'
            '    ... 10 items total ...\n'
            '  ]\n'
            '}\n'
        )

        user_prompt_parts = [
            f"Course title: {course_title}",
            f"Target quiz level: {level}",
            "The questions should be suitable for this level.",
        ]
        if course_description:
            user_prompt_parts.append(f"Course description: {course_description}")
        if course_level:
            user_prompt_parts.append(f"Course difficulty: {course_level}")

        user_prompt = "\n".join(user_prompt_parts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 1024,
                },
            )
            raw_content = response["message"]["content"].strip()
        except Exception as ollama_error:
            logger.error(f"Error calling Ollama for MCQ quiz generation: {ollama_error}")
            return jsonify({
                "success": False,
                "error": "Failed to generate MCQ quiz using the LLM",
            }), 500

        import json

        try:
            quiz_data = json.loads(raw_content)
        except json.JSONDecodeError:
            # Try to recover when the model wraps JSON with extra text
            logger.warning(f"MCQ quiz JSON parse failed, raw: {raw_content[:200]}...")
            first_brace = raw_content.find('{')
            last_brace = raw_content.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                try:
                    trimmed = raw_content[first_brace:last_brace + 1]
                    quiz_data = json.loads(trimmed)
                    logger.info("Recovered MCQ quiz JSON after trimming surrounding text.")
                except json.JSONDecodeError:
                    logger.error("MCQ quiz JSON recovery attempt failed.")
                    return jsonify({
                        "success": False,
                        "error": "LLM did not return valid JSON for the quiz. Please try again.",
                    }), 500
            else:
                return jsonify({
                    "success": False,
                    "error": "LLM did not return valid JSON for the quiz. Please try again.",
                }), 500

        questions = quiz_data.get("questions") or []
        # Ensure we have exactly 10 questions and each has required fields
        cleaned_questions = []
        for q in questions:
            text = (q.get("question") or "").strip()
            opts = q.get("options") or []
            if not text or len(opts) < 2:
                continue
            # normalise to 4 options when possible
            opts = opts[:4]
            correct_index = q.get("correct_index", 0)
            try:
                correct_index = int(correct_index)
            except (TypeError, ValueError):
                correct_index = 0
            if correct_index < 0 or correct_index >= len(opts):
                correct_index = 0
            cleaned_questions.append({
                "question": text,
                "options": opts,
                "correct_index": correct_index,
            })
            if len(cleaned_questions) == 10:
                break

        if not cleaned_questions:
            return jsonify({
                "success": False,
                "error": "Failed to extract valid MCQ questions from the LLM response.",
            }), 500

        num_questions = len(cleaned_questions)
        max_points = num_questions * 1  # 1 mark per correct question

        assignment_doc = {
            "title": f"{course_title} - Level {level} MCQ Quiz",
            "course": course_title,
            "description": f"AI-generated level {level} MCQ quiz for {course_title}",
            "due_date": None,
            "points": max_points,
            "status": "pending",
            "instructor_name": "",
            "instructor_email": "",
            "student_email": user_email,
            "assignment_type": "quiz_mcq",
            "difficulty_level": level,
            "question_set": cleaned_questions,
            "score": None,
            "rating": None,
            "feedback": "",
            "created_at": datetime.utcnow(),
        }

        result = assignments_collection.insert_one(assignment_doc)
        assignment_id = str(result.inserted_id)

        # Return questions WITHOUT correct answers to the frontend
        public_questions = [
            {
                "index": idx,
                "question": q["question"],
                "options": q["options"],
            }
            for idx, q in enumerate(cleaned_questions)
        ]

        return jsonify({
            "success": True,
            "assignment_id": assignment_id,
            "course": course_title,
            "level": level,
            "max_points": max_points,
            "num_questions": num_questions,
            "questions": public_questions,
        })
    except Exception as e:
        logger.error(f"Error starting MCQ quiz assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/quiz/<assignment_id>', methods=['GET'])
def api_get_quiz_assignment(assignment_id):
    """
    Get an existing MCQ quiz assignment's questions (without correct answers).
    Used when the user clicks 'Attempt & Get Marks' on a pending quiz.
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from bson import ObjectId

        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        if assignment.get("assignment_type") != "quiz_mcq":
            return jsonify({"success": False, "error": "This assignment is not an MCQ quiz"}), 400

        questions = assignment.get("question_set") or []
        public_questions = [
            {
                "index": idx,
                "question": q.get("question", ""),
                "options": q.get("options", []),
            }
            for idx, q in enumerate(questions)
        ]

        return jsonify({
            "success": True,
            "assignment_id": assignment_id,
            "course": assignment.get("course", ""),
            "level": int(assignment.get("difficulty_level", 1)),
            "num_questions": len(public_questions),
            "questions": public_questions,
        })
    except Exception as e:
        logger.error(f"Error getting MCQ quiz assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/assignments/quiz/<assignment_id>/submit', methods=['POST'])
def api_submit_quiz_assignment(assignment_id):
    """
    Submit answers for a 10-question MCQ quiz assignment.
    - Compares answers against stored correct_index for each question.
    - Computes score and rating (0-5) without calling the LLM.
    - Marks the assignment as completed and allows the next level to unlock.
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from bson import ObjectId

        data = request.get_json() or {}
        answers = data.get('answers', [])

        assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        if assignment.get("assignment_type") != "quiz_mcq":
            return jsonify({"success": False, "error": "This assignment is not an MCQ quiz"}), 400

        questions = assignment.get("question_set") or []
        if not questions:
            return jsonify({"success": False, "error": "Quiz has no questions stored"}), 500

        num_questions = len(questions)
        max_points = int(assignment.get("points", num_questions))

        # Score the quiz
        correct_count = 0
        detailed_results = []
        for idx, q in enumerate(questions):
            correct_index = int(q.get("correct_index", 0))
            user_answer = None
            if idx < len(answers):
                try:
                    user_answer = int(answers[idx])
                except (TypeError, ValueError):
                    user_answer = None
            is_correct = user_answer is not None and user_answer == correct_index
            if is_correct:
                correct_count += 1
            detailed_results.append({
                "question": q.get("question", ""),
                "options": q.get("options", []),
                "correct_index": correct_index,
                "user_answer": user_answer,
                "is_correct": is_correct,
            })

        score = float(correct_count)  # 1 mark per correct answer
        # Map score proportion to rating 0-5
        rating = 0.0
        if num_questions > 0:
            rating = (score / float(num_questions)) * 5.0
        if rating < 0:
            rating = 0.0
        if rating > 5:
            rating = 5.0

        level = int(assignment.get("difficulty_level", 1))
        feedback = f"You answered {correct_count} out of {num_questions} questions correctly."

        # Optional: generate per-question explanations for incorrect answers using LLM
        # This is best-effort only; if Ollama is not available, we skip detailed reasons.
        if OLLAMA_AVAILABLE:
            try:
                model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')
                for r in detailed_results:
                    # Build a short explanation only for incorrect answers
                    if not r.get("is_correct", False) and r.get("user_answer") is not None and r.get("user_answer") >= 0:
                        q_text = r.get("question", "")
                        options = r.get("options", [])
                        ca_idx = int(r.get("correct_index", 0))
                        ua_idx = int(r.get("user_answer", -1))

                        def idx_to_label(i: int) -> str:
                            try:
                                return chr(ord("A") + i)
                            except Exception:
                                return "?"

                        ca_label = idx_to_label(ca_idx)
                        ua_label = idx_to_label(ua_idx)
                        ca_text = options[ca_idx] if 0 <= ca_idx < len(options) else ""
                        ua_text = options[ua_idx] if 0 <= ua_idx < len(options) else ""

                        # Build options text block like "A) ..., B) ..., ..."
                        opts_str_parts = []
                        for i, opt in enumerate(options):
                            label = idx_to_label(i)
                            opts_str_parts.append(f"{label}) {opt}")
                        opts_str = "\n".join(opts_str_parts)

                        system_prompt = (
                            "You are a math and reasoning teacher.\n"
                            "Given a multiple-choice question, the options, the student's chosen answer "
                            "and the correct answer, explain briefly WHY the student's answer is wrong and "
                            "WHY the correct answer is right.\n"
                            "Use very simple language, 1-3 short sentences, and do NOT repeat the full question."
                        )

                        user_prompt = (
                            f"Question: {q_text}\n"
                            f"Options:\n{opts_str}\n\n"
                            f"Student chose: {ua_label}) {ua_text}\n"
                            f"Correct answer: {ca_label}) {ca_text}\n\n"
                            "Explain the mistake and the correct reasoning."
                        )

                        try:
                            response = ollama.chat(
                                model=model_name,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt},
                                ],
                                options={
                                    "temperature": 0.4,
                                    "top_p": 0.9,
                                    "num_predict": 256,
                                },
                            )
                            explanation = response["message"]["content"].strip()
                        except Exception as explain_error:
                            logger.warning(f"Ollama explanation error for quiz question: {explain_error}")
                            explanation = "This answer is not correct. Review the concept and try again."

                        r["explanation"] = explanation
                    else:
                        # For correct answers, a simple confirmation is enough
                        r["explanation"] = "Your answer is correct."
            except Exception as e:
                logger.warning(f"Failed to generate detailed MCQ explanations: {e}")
                # Fallback generic explanation text
                for r in detailed_results:
                    if r.get("is_correct", False):
                        r["explanation"] = "Your answer is correct."
                    else:
                        r["explanation"] = "This answer is incorrect. Please review this concept."
        else:
            # No LLM available – provide simple generic messages
            for r in detailed_results:
                if r.get("is_correct", False):
                    r["explanation"] = "Your answer is correct."
                else:
                    r["explanation"] = "This answer is incorrect. Please check the correct option and try again."

        update_doc = {
            "score": score,
            "rating": rating,
            "feedback": feedback,
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results": detailed_results,
        }
        assignments_collection.update_one({"_id": assignment["_id"]}, {"$set": update_doc})

        # (MCQ quiz scores are not used in game leaderboard; only stored on assignments)

        result = {
            "assignment_id": assignment_id,
            "course": assignment.get("course", ""),
            "level": level,
            "score": score,
            "max_points": max_points,
            "rating": rating,
            "correct_count": correct_count,
            "num_questions": num_questions,
            "feedback": feedback,
        }

        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Error submitting MCQ quiz assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test-booking-simple')
def test_booking_simple():
    """Simple test route for booking page without auth"""
    return "Booking page test - accessible without auth"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect('/login-page')
        
        # Find user in database by email
        user = users_collection.find_one({'email': email})
        
        if user:
            logger.info(f"User found: {email}")
            logger.info(f"Stored password hash: {user['password'][:20]}...")
            logger.info(f"Provided password: {password}")
            
            password_match = check_password_hash(user['password'], password)
            logger.info(f"Password match: {password_match}")
            
            if password_match:
                session['user_id'] = str(user['_id'])
                session['email'] = user['email']
                session['phone'] = user.get('phone', '')
                session['username'] = user.get('username', user['email'])
                session['profile'] = user.get('profile', {})
                flash('🎉 Login successful! Welcome back!', 'success')
                logger.info(f"✅ User {email} logged in successfully, redirecting to dashboard")
                logger.info(f"Session data: {dict(session)}")
                # Use direct URL redirect to dashboard
                return redirect('/dashboard')
            else:
                flash('❌ Invalid password. Please check your password and try again.', 'error')
                logger.warning(f"Password mismatch for user: {email}")
                return redirect('/login-page')
        else:
            flash('❌ User not found. Please check your email or sign up for a new account.', 'error')
            logger.warning(f"User not found: {email}")
            return redirect('/login-page')
    
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    logger.info(f"Signup attempt for email: {email}, phone: {phone}")
    
    # Validation
    if not all([email, phone, password, confirm_password]):
        flash('Please fill in all fields', 'error')
        logger.warning("Signup failed: Missing fields")
        return redirect('/signup-page')
    
    if not validate_email(email):
        flash('❌ Please enter a valid email address (e.g., user@example.com)', 'error')
        logger.warning(f"Signup failed: Invalid email: {email}")
        return redirect('/signup-page')
    
    if not validate_phone(phone):
        flash('❌ Please enter a valid 10-digit phone number (e.g., 9876543210)', 'error')
        logger.warning(f"Signup failed: Invalid phone: {phone}")
        return redirect('/signup-page')
    
    if password != confirm_password:
        flash('❌ Passwords do not match. Please make sure both password fields are identical.', 'error')
        logger.warning(f"Signup failed: Password mismatch for email: {email}")
        return redirect('/signup-page')
    
    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        flash(f'❌ {password_error}', 'error')
        logger.warning(f"Signup failed: {password_error} for email: {email}")
        return redirect('/signup-page')
    
    # Check if user already exists
    existing_user = users_collection.find_one({
        '$or': [
            {'email': email},
            {'phone': phone}
        ]
    })
    
    if existing_user:
        if existing_user['email'] == email:
            flash('❌ This email is already registered. Please use a different email or try logging in.', 'error')
        else:
            flash('❌ This phone number is already registered. Please use a different phone number.', 'error')
        logger.warning(f"Signup failed: User already exists - email: {email}, phone: {phone}")
        return redirect('/signup-page')
    
    # Create new user
    try:
        hashed_password = generate_password_hash(password)
        logger.info(f"Creating user: {email}")
        logger.info(f"Hashed password: {hashed_password[:20]}...")
        
        # Generate a unique username if email is already taken as username
        username = email
        counter = 1
        while users_collection.find_one({'username': username}):
            username = f"{email}_{counter}"
            counter += 1
        
        user_data = {
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'username': username,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True,
            'profile': {
                'name': '',
                'location': '',
                'bio': ''
            }
        }
        
        result = users_collection.insert_one(user_data)
        if result.inserted_id:
            # Store user info in session for profile completion
            session['user_id'] = str(result.inserted_id)
            session['email'] = email
            session['phone'] = phone
            session['username'] = username
            session['profile'] = user_data['profile']
            flash('🎉 Account created successfully! Please complete your profile.', 'success')
            logger.info(f"✅ New user registered successfully: {email} ({phone})")
            return redirect('/profile-setup')
        else:
            flash('❌ Failed to create account. Please try again.', 'error')
            logger.error(f"❌ Failed to create account for: {email}")
            return redirect('/signup-page')
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Signup error for {email}: {error_msg}")
        
        # Handle specific MongoDB errors
        if "E11000" in error_msg and "email" in error_msg:
            flash('❌ This email is already registered. Please use a different email or try logging in.', 'error')
        elif "E11000" in error_msg and "phone" in error_msg:
            flash('❌ This phone number is already registered. Please use a different phone number.', 'error')
        elif "E11000" in error_msg and "username" in error_msg:
            flash('❌ This email is already registered as a username. Please try logging in instead.', 'error')
        elif "E11000" in error_msg:
            flash('❌ Account already exists with this information. Please try logging in instead.', 'error')
        else:
            flash('❌ An error occurred while creating your account. Please try again.', 'error')
        
        return redirect('/signup-page')


@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    logger.info(f"User {username} is logging out")
    
    # Clear the session
    session.clear()
    
    # Flash success message
    flash('👋 You have been successfully logged out!', 'success')
    
    logger.info(f"✅ User {username} logged out successfully")
    return redirect(url_for('index'))

@app.route('/api/users')
def api_users():
    """API endpoint to get all users (for testing)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = list(users_collection.find({}, {'password': 0}))
    for user in users:
        user['_id'] = str(user['_id'])
        if user.get('created_at'):
            user['created_at'] = user['created_at'].isoformat()
        if user.get('last_login'):
            user['last_login'] = user['last_login'].isoformat()
    
    return jsonify(users)

# ============================================================================
# AI CHAT SUPPORT ROUTES
# ============================================================================

@app.route('/chat', methods=['GET'])
def chat_page():
    """Serve the AI chat page"""
    try:
        if not CHAT_SUPPORT_AVAILABLE:
            flash('AI Chat support is not available. Please check the setup.', 'error')
            return redirect('/')
        
        if 'user_id' not in session:
            flash('Please login to access AI chat support', 'warning')
            return redirect('/login-page')
        
        log_info("Serving AI chat page")
        return render_template('chat.html')
    except Exception as e:
        log_error(f"Error serving chat page: {e}")
        return "Error loading chat page.", 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for AI chat"""
    try:
        if not CHAT_SUPPORT_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'AI Chat support is not available'
            }), 503
        
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        user_id = session['user_id']
        log_info(f"AI chat request from user {user_id}: {question[:50]}...")
        
        # Get AI response
        result = chat_with_ai_teacher(user_id, question)
        
        if result['success']:
            log_info(f"AI response generated successfully for user {user_id}")
            return jsonify(result)
        else:
            log_warning(f"AI chat failed for user {user_id}: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
            
    except Exception as e:
        log_error(f"Error in AI chat API: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def api_clear_chat():
    """API endpoint to clear chat history"""
    try:
        if not CHAT_SUPPORT_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'AI Chat support is not available'
            }), 503
        
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        success = clear_ai_conversation(user_id)
        
        if success:
            log_info(f"Chat history cleared for user {user_id}")
            return jsonify({'success': True, 'message': 'Chat history cleared'})
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear chat history'
            }), 500
            
    except Exception as e:
        log_error(f"Error clearing chat history: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/chat/status', methods=['GET'])
def api_chat_status():
    """API endpoint to get AI system status"""
    try:
        if not CHAT_SUPPORT_AVAILABLE:
            return jsonify({
                'ollama_connected': False,
                'current_model': 'Not available',
                'available_models': [],
                'active_conversations': 0,
                'total_messages': 0,
                'error': 'Chat support not available'
            })
        
        status = get_ai_system_status()
        return jsonify(status)
    except Exception as e:
        log_error(f"Error getting AI system status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get system status'
        }), 500

# ============================================================================
# CHATBOT API ROUTES
# ============================================================================

def detect_language(text):
    """
    Detects the language of the user's message.
    Returns: 'en' (English), 'hi' (Hindi), or 'hinglish' (Hinglish)
    """
    if not text:
        return 'en'  # Default to English
    
    # Check for Devanagari script (Hindi characters)
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    has_hindi = bool(devanagari_pattern.search(text))
    
    # Check for English characters (letters)
    english_pattern = re.compile(r'[a-zA-Z]')
    has_english = bool(english_pattern.search(text))
    
    # Determine language
    if has_hindi and has_english:
        return 'hinglish'
    elif has_hindi:
        return 'hi'
    else:
        return 'en'  # Default to English if no Hindi detected

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """Chatbot endpoint using local LLM with chain-of-thought reasoning"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', None)
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        # Create new session if session_id is not provided
        if not session_id:
            session_id = f"chat_{uuid.uuid4().hex[:16]}"
            logger.info(f"Created new chat session: {session_id}")
        
        # Initialize session if it doesn't exist
        if session_id not in chatbot_sessions:
            chatbot_sessions[session_id] = []
            logger.info(f"Initialized new session storage for: {session_id}")
        
        # Get conversation history from session storage
        session_history = chatbot_sessions[session_id]
        
        # Use provided history if available, otherwise use session history
        if not history and session_history:
            # Convert session history to the format expected by LLM
            history = []
            for msg in session_history[-10:]:  # Last 10 messages
                if msg.get('role') == 'user':
                    history.append({'user': msg.get('content', ''), 'assistant': ''})
                elif msg.get('role') == 'assistant':
                    if history and history[-1].get('user'):
                        history[-1]['assistant'] = msg.get('content', '')
                    else:
                        history.append({'user': '', 'assistant': msg.get('content', '')})
        
        # Check if Ollama is available
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Please install it: pip install ollama",
                "response": "I'm sorry, the AI assistant is not available. Please install Ollama to enable AI features."
            }), 503
        
        # Detect language BEFORE processing with LLM
        detected_lang = detect_language(user_message)
        logger.info(f"Detected language for message '{user_message[:50]}...': {detected_lang}")
        
        # Get system prompt with language-specific instructions
        if CHATBOT_PROMPT_AVAILABLE:
            system_prompt = get_system_prompt(detected_lang)
            user_prompt_template = get_user_prompt_template()
        else:
            # Fallback prompt if chatbot_prompt module is not available
            system_prompt = "You are a Learning Assistant for a student learning platform. Help students with courses, assignments, and learning questions."
            user_prompt_template = "{user_message}"
        
        # Build conversation messages for Ollama (using session history)
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation history from session storage
        if session_history:
            # Convert session history to Ollama message format
            for msg in session_history[-10:]:  # Last 10 messages for context
                if msg.get('role') in ['user', 'assistant']:
                    messages.append({
                        'role': msg['role'],
                        'content': msg.get('content', '')
                    })
        
        # Add current user message with chain-of-thought instruction
        messages.append({
            'role': 'user',
            'content': user_prompt_template.format(user_message=user_message)
        })
        
        # Get model name from environment or use default
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        try:
            # Call Ollama with chain-of-thought reasoning and full conversation history
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 2000,
                    'repeat_penalty': 1.2
                }
            )
            
            bot_response = response['message']['content'].strip()
            
            # Store conversation in session history
            chatbot_sessions[session_id].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.utcnow().isoformat()
            })
            chatbot_sessions[session_id].append({
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Limit session history to last 50 messages to prevent memory issues
            if len(chatbot_sessions[session_id]) > 50:
                chatbot_sessions[session_id] = chatbot_sessions[session_id][-50:]
            
            logger.info(f"Chatbot response generated successfully for session: {session_id}")
            return jsonify({
                "success": True,
                "response": bot_response,
                "session_id": session_id
            })
            
        except Exception as ollama_error:
            logger.error(f"Ollama error: {ollama_error}")
            
            # Check if Ollama service is running
            if "connection" in str(ollama_error).lower() or "refused" in str(ollama_error).lower():
                return jsonify({
                    "success": False,
                    "error": "Ollama service is not running",
                    "response": "I'm sorry, the AI service is not running. Please make sure Ollama is installed and running."
                }), 503
            
            # Fallback response
            return jsonify({
                "success": False,
                "error": str(ollama_error),
                "response": "I'm having trouble processing your request right now. Please try again in a moment."
            }), 500
            
    except Exception as e:
        logger.error(f"Chatbot API error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I'm sorry, I encountered an error. Please try again."
        }), 500

if __name__ == '__main__':
    # Show startup banner
    log_startup()
    
    # Create indexes for better performance
    try:
        # Drop old username index if it exists
        try:
            users_collection.drop_index("username_1")
            log_info("Dropped old username index")
        except Exception as e:
            log_info(f"Username index drop result: {e}")
        
        # Clean up existing users with null usernames
        try:
            result = users_collection.update_many(
                {"username": None},
                {"$set": {"username": "$email"}}
            )
            if result.modified_count > 0:
                log_info(f"Updated {result.modified_count} users with null usernames")
        except Exception as e:
            log_warning(f"Error updating null usernames: {e}")
        
        # Create new indexes
        users_collection.create_index("email", unique=True)
        users_collection.create_index("phone", unique=True)
        # Create username index with sparse option to allow null values
        users_collection.create_index("username", unique=True, sparse=True)
        log_success("Database indexes created successfully")
    except Exception as e:
        log_warning(f"Index creation warning: {e}")
    

    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    log_info(f"Starting Learning App server on {host}:{port}")
    log_info(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
    log_success("🎓 Learning App is ready! Press Ctrl+C to stop.")
    
    try:
        app.run(debug=debug_mode, host=host, port=port)
    except KeyboardInterrupt:
        log_info("Shutting down Learning App...")
        log_success("👋 Learning App stopped successfully!")
    except Exception as e:
        log_error(f"Learning App crashed: {e}")
        sys.exit(1)
