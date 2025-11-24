# Learning App - Student Learning Platform

A comprehensive student learning platform built with Flask, MongoDB and Ollama‑powered AI.
The app combines **assignments**, **AI tutoring**, and **game‑based learning** (Tic Tac Toe, Crossword,
Word Search) with a **global leaderboard** so students can learn and compete together.

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd learning_app
   ```

2. **Create environment file**
   ```bash
   cp env.yaml.template env.yaml
   ```

3. **Configure environment variables**
   Edit `env.yaml` file with your actual values:
   - `MONGO_URI`: Your MongoDB connection string
   - `SECRET_KEY`: Your Flask secret key
   - `LANGCHAIN_API_KEY`: Your LangSmith API key
   - `OLLAMA_BASE_URL`: Your Ollama server URL (default: http://localhost:11434)
   - `OLLAMA_MODEL`: Your preferred Ollama model (default: llama3.2)
   - `SECRET_KEY`: Generate a secure secret key
   - `DB_NAME`: Your database name (default: learning)

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Security Notes

- **Never commit `env.yaml` files** - They contain sensitive information like API keys
- **Use `env.yaml.template`** as a template for required environment variables
- **Generate a strong SECRET_KEY** for production use
- **Keep your MongoDB credentials and API keys secure**
- **The `env.yaml` file is already added to `.gitignore`** to prevent accidental commits

## Project Structure

```
learning_app/
├── backend/                   # Flask backend
│   ├── app.py                 # Main Flask application & routes
│   ├── db_services.py         # MongoDB CRUD helpers for courses/assignments
│   ├── assignment_detail_service.py  # Helper for assignment detail API
│   └── __pycache__/           # Compiled Python files (ignored)
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Base layout (header, nav, chatbot widget)
│   ├── landing.html           # Landing page
│   ├── login.html             # Login page
│   ├── signup.html            # Signup page
│   ├── profile_setup.html     # Profile setup page
│   ├── dashboard.html         # Main learning dashboard + leaderboards
│   ├── assignments.html       # Assignments + MCQ Practice + Tic Tac Toe
│   ├── courses.html           # My Courses + AI course generation
│   ├── learn.html             # Learn with Games (Crossword, Word Search)
│   ├── chat.html              # AI Tutor chat page
│   ├── admin.html             # Admin dashboard (students, assignments, reports)
│   └── admin_login.html       # Admin login page
├── static/                    # Static assetsname to
│   ├── js/
│   │   ├── main.js            # General frontend logic
│   │   └── chatbot.js         # Floating chatbot widget logic
│   └── ...                    # Images / CSS if any
├── utils/
│   ├── chatbot_prompt.py      # System prompts for AI tutor
│   └── logger.py              # Logging utilities
├── webpage/                   # Legacy/static landing assets
│   ├── styles.css
│   └── script.js
├── setup_ollama.py            # Helper script to install/pull Ollama models
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── env.yaml.template          # Sample environment config
├── env.yaml                   # Local environment config (ignored in git)
└── README.md                  # Project documentation (this file)
```

## Features

### 🎓 Core Learning Features
- **User Authentication**: Secure login/signup with email and phone validation.
- **Profile Management**: Complete user profile setup and management.
- **Course Management**:
  - Manual course creation.
  - **AI‑generated courses** via Ollama (subject + level → title, description, outline).
- **Assignment Tracking**:
  - Text assignments graded by the LLM with marks, rating, and feedback.
  - AI‑generated **MCQ quizzes** per subject with automatic scoring and explanations.
- **Learning Dashboard**: Personalized dashboard with assignment stats and **global game leaderboards**.
- **Admin Panel**:
  - View/delete students and assignments.
  - Review reports and manually adjust marks.

### 🧠 AI & LLM Integration
- **Ollama‑powered question generation**:
  - MCQ quizzes (10 questions per level, per subject).
  - Open‑ended assignment grading with rubric‑based JSON output.
  - Explanations for wrong MCQ answers.
- **AI Tutor Chatbot**:
  - `/chat` page + floating widget.
  - Uses carefully crafted prompts (`utils/chatbot_prompt.py`) for safe, language‑aware responses.

### 🎮 Game‑Based Learning (Learn with Games)

The **Learn with Games** tab (`/learn`) contains two AI‑driven study games:

- **Crossword Puzzle**
  - LLM generates subject‑specific words + clues.
  - UI shows 3 Across words with boxes and additional Down clues.
  - Student types answers into boxes and clicks **Complete & Check**.
  - **Time‑based scoring**:
    - App tracks time from generation until completion.
    - Backend scores: `score = correct_words × time_factor`, where `time_factor` rewards faster solves.

- **Word Search**
  - LLM generates a list of subject words.
  - Frontend builds a dynamic 10×10 letter grid and hides the words in horizontal/vertical/diagonal lines.
  - Student selects words directly with the mouse (start cell → end cell).
  - Clicking **Complete** submits:
    - `found_words`, `total_words`, and elapsed time.
  - Backend computes a **time‑weighted score** based on words found and speed.

In addition, after completing any assignment or quiz, students unlock a **Tic Tac Toe** mini‑game (vs. computer)
for a short break. Each round contributes to the Tic Tac Toe leaderboard.

### 🏆 Global Leaderboards

On the **Dashboard** page, a **Game Leaderboards (Global)** section shows the top students for:

- **Tic Tac Toe**  
  - Stored as `game_type = "tictactoe"` in `game_scores`.
  - Scoring per round: **win = 3**, **draw = 1**, **loss = 0**.
  - Leaderboard aggregates total points per student (name only, no email shown).

- **Crossword**  
  - Endpoint `/api/games/crossword/score` records:
    - `correct` words, `total` words, `time_seconds`.
  - Score is time‑weighted: more correct answers and less time → higher score.

- **Word Search**  
  - Endpoint `/api/games/wordsearch/score` records:
    - `words_found`, `total` words, `time_seconds`.
  - Similar time‑weighted scoring encouraging both accuracy and speed.

All game scores are stored in the `game_scores` MongoDB collection and aggregated globally so every user
can see who is leading in each game type.

### 🎯 Key Pages
1. **Landing Page**: Welcome page with features and call-to-action.
2. **Login/Signup**: User authentication with validation.
3. **Profile Setup**: Complete user profile configuration.
4. **Learning Dashboard**: Main application interface with courses, assignments, and leaderboards.
5. **Assignments**:
   - MCQ Practice (LLM‑generated quizzes, level‑based).
   - Text assignments with LLM grading and reporting.
   - Per‑question reporting and admin review tools.
6. **Courses**:
   - My Courses list.
   - AI course generation and quick links to MCQ Practice and AI Tutor.
7. **Learn with Games**: Crossword + Word Search games with timers and scoring.
8. **Chat (AI Tutor)**: Dedicated chat page for subject doubts and study help.
9. **Admin Dashboard**: View/delete students and assignments, resolve reports, adjust marks.

### 🛠️ Technical Features
- **Template System**: Clean separation using Jinja2 templates.
- **Modular JavaScript**: Organized code structure for dashboard, assignments, games, and chatbot.
- **Responsive Design**: Mobile-first layout with CSS Grid and Flexbox.
- **Form Validation**: Client-side and server-side validation.
- **Session Management**: Secure user session handling.
- **Database Integration**:
  - `users`, `courses`, `assignments`, `reports`, `game_scores` collections in MongoDB.
  - Helper functions in `backend/db_services.py` and `backend/assignment_detail_service.py`.

## Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd learning_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   MONGO_URI=your-mongodb-connection-string
   DB_NAME=learning
   FLASK_DEBUG=True
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Code Organization

### Backend (Flask)
- **Modular Routes**: Each page has its own route handler
- **Template Rendering**: Uses Jinja2 for dynamic content
- **Session Management**: Secure user authentication
- **Database Operations**: MongoDB integration for data persistence

### Frontend (HTML/CSS/JS)
- **Template Inheritance**: Base template with page-specific content
- **Modular JavaScript**: Separated concerns for better maintainability
- **Responsive CSS**: Mobile-first design approach
- **Form Validation**: Client-side validation with server-side verification

### Key Improvements Made
1. **Separated HTML Files**: Each page now has its own template.
2. **Organized JavaScript**: Modular structure for assignments, games, chatbot, and admin tools.
3. **Clean Backend**: Large `app.py` refactored to use `db_services.py` and `assignment_detail_service.py`.
4. **AI‑First Features**: Centralized Ollama usage for question generation, grading, explanations, and games.
5. **Game & Leaderboard Layer**: Added `game_scores` storage and dashboard aggregation for multiple games.

## API Endpoints

- `GET /` - Landing page
- `GET /login-page` - Login page
- `POST /login` - User login
- `GET /signup-page` - Signup page
- `POST /signup` - User registration
- `GET /profile-setup` - Profile setup page
- `POST /complete-profile` - Complete user profile
- `GET /dashboard` - Main learning dashboard
- `GET /courses` - Course management page
- `GET /assignments` - Assignment tracking page (text + MCQ + Tic Tac Toe bonus)
- `GET /learn` - Learn with Games (Crossword + Word Search)
- `GET /about` - About us page
- `GET /logout` - User logout
- `POST /api/assignments/quiz/start` - Generate a 10‑question MCQ quiz for a subject/level
- `POST /api/assignments/quiz/<assignment_id>/submit` - Submit MCQ quiz answers and get marks/ratings
- `GET /api/assignments/<assignment_id>/detail` - Detailed assignment view (including MCQ breakdown)
- `POST /api/assignments/<assignment_id>/report` - Report an assignment
- `POST /api/assignments/<assignment_id>/questions/<idx>/report` - Report a specific MCQ question
- `POST /api/games/flashcards` - (Internal) generate flashcards/puzzles (used previously)
- `POST /api/games/crossword` - Generate crossword entries (clue + answer)
- `POST /api/games/crossword/score` - Record crossword score (correct words + time)
- `POST /api/games/wordsearch` - Generate word search word list
- `POST /api/games/wordsearch/score` - Record word search score (words found + time)
- `POST /api/games/tictactoe/score` - Record Tic Tac Toe game result (win/draw/loss)

## Contributors

- **Rohit Raj** – rohitraj16092004@gmail.com
- **Prashant Jha** – prashantb3005@gmail.com
- **Siri Dayanand** – siridayanand224@gmail.com
- **Saurabh Chandra** – saurabhchandra9170@gmail.com

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
