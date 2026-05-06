from flask import Flask
from login_package import bp as auth_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
