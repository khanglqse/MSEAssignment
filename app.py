from flask import Flask
from flask_login import LoginManager
from config import Config
from routes import routes as main_routes
from core.scss_complier import compile_scss
app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    from models.user import User
    return User.getUser(id)

# compile_scss()
app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
