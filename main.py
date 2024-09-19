from flask import Flask, g,request
from flask_login import LoginManager, current_user
from flask_babel import Babel
from config import Config
from routes import routes as main_routes, auth_routes
# from scss_complier import compile_scss
import os
from core.scss_complier import compile_scss
import sqlite3

app = Flask(__name__)
# compile_scss()
app.config.from_object(Config)

# Initialize Flask-Babel
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATABASE = 'pig_save.db'




@app.before_request
def load_user_language():
    if current_user.is_authenticated:
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE id = ?", (current_user.id,))
        result = cursor.fetchone()
        print(f'langauge: {result}')
        if result:
            g.language = result[0]
        else:
            g.language = 'en' 

def get_locale():
    language = getattr(g, 'language', 'en')
    return language

babel = Babel(app, locale_selector=get_locale)


@login_manager.user_loader
def load_user(id):
    from models.user import User
    return User.getUser(id)

app.register_blueprint(main_routes)
app.register_blueprint(auth_routes)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
