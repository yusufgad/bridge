import os
# Import session and check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Import password hashing and check_password_hash
from datetime import datetime, timezone # Import datetime

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bridge.db' # Set the database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable modification tracking

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Set a secret key for session security.
# In a real application, use a more secure method like environment variables.
app.config['SECRET_KEY'] = os.urandom(24)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Increased length for password hash
    password_hash = db.Column(db.String(256), nullable=False)
    # Define the relationship to the Post model
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

# Post Model (New)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(280), nullable=False) # e.g., Max 280 characters
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.body[:30]}...>'

# Create database tables if they don't exist
# This should ideally be handled with migrations (e.g., Flask-Migrate) in a larger app
with app.app_context():
    db.create_all()

# Updated Home Route
@app.route('/')
def home():
    user_id = session.get('user_id')
    user = None
    posts = []
    
    # Get all posts for the home page, newest first
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    if user_id:
        user = User.query.get(user_id)
    
    # Pass user info and posts to the template
    return render_template('index.html', user=user, posts=posts)

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('register'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return redirect(url_for('register'))

        # Hash the password
        # Explicitly set method to pbkdf2:sha256 due to LibreSSL not supporting scrypt
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256:600000')

        # Create new user
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login')) # Redirect to login page

    # GET request: display the registration form
    return render_template('register.html')

# Login Route Implementation
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any existing user_id - prevents logged-in users seeing login page directly
    # session.pop('user_id', None)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        # Check if user exists and password hash matches
        if user and check_password_hash(user.password_hash, password):
            # Store user ID in session
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('home')) # Redirect to home page after login
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    # GET request: display the login form
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None) # Remove user_id from session
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('login')) # Redirect to login page after logout

# New route for creating posts
@app.route('/create_post', methods=['POST'])
def create_post():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to create a post.', 'warning')
        return redirect(url_for('login'))
    
    # Get the post content from the form
    body = request.form.get('body')
    
    if not body:
        flash('Post cannot be empty.', 'warning')
        return redirect(url_for('home'))
    
    # Create new post
    new_post = Post(body=body, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    
    flash('Your post was created successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Keep host and port consistent with previous setup
    app.run(host='0.0.0.0', port=3000, debug=True) 