from flask import Flask
from flask_login import LoginManager
from config import Config
from routes import routes as main_routes, auth_routes
# from scss_complier import compile_scss
import os
app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# compile_scss()
@login_manager.user_loader
def load_user(id):
    from models.user import User
    return User.getUser(id)

app.register_blueprint(main_routes)
app.register_blueprint(auth_routes)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
