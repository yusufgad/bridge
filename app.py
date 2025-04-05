import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy

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

if __name__ == '__main__':
    # Keep host and port consistent with previous setup
    app.run(host='0.0.0.0', port=3000, debug=True) 