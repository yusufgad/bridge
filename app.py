import os
from flask import Flask, render_template

app = Flask(__name__)

# Set a secret key for session security. 
# In a real application, use a more secure method like environment variables.
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True) 