from flask_login import UserMixin
import sqlite3
class User(UserMixin):
    def __init__(self, id, username,name):
        self.id = id
        self.username = username
        self.name = name
        
    def getUser(user_id):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2])
        return None

