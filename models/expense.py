import sqlite3

class Expense:
    def __init__(self, id, user_id, amount, category, description, date):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date
    def getAllExpense(user_id, page, size):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE user_id = ? LIMIT ? OFFSET ?', (user_id, size, (page -1) * size))
        expenses = cursor.fetchall()
        total_expenses = conn.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
        conn.close()
        return expenses, total_expenses
    def add_expense(user_id, description, amount, date):
        conn = sqlite3.connect('pig_save.db')  # Update with your actual database path
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, description, amount, date) VALUES (?, ?, ?, ?)",
                    (description, amount, date))
        conn.commit()
        conn.close()