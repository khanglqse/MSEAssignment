from flask_login import UserMixin
import sqlite3
class User(UserMixin):
    def __init__(self, id, username,name, language, age):
        self.id = id
        self.username = username
        self.name = name
        self.language = language
        self.age = age
        
    def getUser(user_id):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, name, language, age FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2], user[3], user[4])
        return None

    def update_language(user_id, language):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
        conn.commit()
        conn.close()
