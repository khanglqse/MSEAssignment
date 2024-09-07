from werkzeug.security import check_password_hash
from flask_login import login_user
from models.user import User
from database import get_db_connection

def auth_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        user_obj = User(id=user['id'], username=user['username'])
        login_user(user_obj)
        return True
    return False
