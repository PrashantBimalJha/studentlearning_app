# Student Learning Platform - Education Management System

A comprehensive student learning platform built with Flask and modern web technologies.

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd booking_app
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**
   Edit `.env` file with your actual values:
   - `MONGO_URI`: Your MongoDB connection string
   - `SECRET_KEY`: Generate a secure secret key
   - `DB_NAME`: Your database name (e.g., student_learning)

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Security Notes

- **Never commit `.env` files** - They contain sensitive information
- **Use `.env.example`** as a template for required environment variables
- **Generate a strong SECRET_KEY** for production use
- **Keep your MongoDB credentials secure**

## Project Structure

```
booking_app/
├── backend/
│   └── app.py                 # Main Flask application
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template with common elements
│   ├── landing.html          # Landing page
│   ├── login.html            # Login page
│   ├── signup.html           # Signup page
│   ├── profile_setup.html    # Profile setup page
│   ├── booking.html          # Main booking/marketplace page
│   └── about.html            # About us page
├── static/
│   └── js/                   # Organized JavaScript modules
│       ├── validation.js     # Form validation functions
│       ├── forms.js          # Form handling
│       ├── marketplace.js    # Crop marketplace functionality
│       ├── profile.js        # Profile management
│       └── main.js           # Main application logic
├── webpage/
│   ├── styles.css            # Main CSS file
│   └── script.js             # Main JavaScript file
├── utils/
│   └── logger.py             # Logging utilities
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Features

### 🌱 Core Features
- **User Authentication**: Secure login/signup with email and phone validation
- **Profile Management**: Complete user profile setup and management
- **Crop Marketplace**: Instagram-style interface for buying and selling crops
- **Digital Management**: Comprehensive farming operations management
- **Mobile Responsive**: Optimized for all device sizes

### 🎯 Key Pages
1. **Landing Page**: Welcome page with features and call-to-action
2. **Login/Signup**: User authentication with validation
3. **Profile Setup**: Complete user profile configuration
4. **Booking/Marketplace**: Main application interface
5. **About Us**: Company information and contact details

### 🛠️ Technical Features
- **Template System**: Clean separation using Jinja2 templates
- **Modular JavaScript**: Organized code structure for maintainability
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Form Validation**: Client-side and server-side validation
- **Session Management**: Secure user session handling
- **Database Integration**: MongoDB for data persistence

## Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd booking_app
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
   DB_NAME=farming
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
1. **Separated HTML Files**: Each page now has its own template
2. **Organized JavaScript**: Modular structure for better code management
3. **Clean Backend**: Simplified routes using template rendering
4. **Better Structure**: Clear separation of concerns
5. **Maintainable Code**: Easier to modify and extend

## API Endpoints

- `GET /` - Landing page
- `GET /login-page` - Login page
- `POST /login` - User login
- `GET /signup-page` - Signup page
- `POST /signup` - User registration
- `GET /profile-setup` - Profile setup page
- `POST /complete-profile` - Complete user profile
- `GET /booking` - Main marketplace page
- `GET /about` - About us page
- `GET /logout` - User logout

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
