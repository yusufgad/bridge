import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from werkzeug.security import generate_password_hash # Import password hashing

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

    def __repr__(self):
        return f'<User {self.username}>'

# Create database tables if they don't exist
# This should ideally be handled with migrations (e.g., Flask-Migrate) in a larger app
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

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

# Placeholder Login Route (we'll implement this later)
@app.route('/login')
def login():
    # For now, just render a simple message or template
    # You might want to create a login.html template later
    return "Login Page Placeholder - Registration Successful!"

if __name__ == '__main__':
    # Keep host and port consistent with previous setup
    app.run(host='0.0.0.0', port=3000, debug=True) 