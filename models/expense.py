import sqlite3

class Expense:
    def __init__(self, id, user_id, amount, category, description, date):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date
    def getAllExpense(user_id):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE user_id = ?', (user_id,))
        expenses = cursor.fetchall()
        conn.close()
        return expenses