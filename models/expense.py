import sqlite3
from datetime import datetime, timedelta
class Expense:
    def __init__(self, id, user_id, amount, category, description, date):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date
    def get_expenses(user_id, page, size, filters, sort_by, sort_order):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        
        query = 'SELECT * FROM expenses WHERE user_id = ?'
        params = [user_id]
        
        if filters.get('category'):
            query += ' AND category = ?'
            params.append(filters['category'])
        
        if filters.get('start_date'):
            query += ' AND date >= ?'
            params.append(filters['start_date'])

        if filters.get('end_date'):
            query += ' AND date <= ?'
            params.append(filters['end_date'])

        if filters.get('min_amount'):
            query += ' AND amount >= ?'
            params.append(filters['min_amount'])

        if filters.get('max_amount'):
            query += ' AND amount <= ?'
            params.append(filters['max_amount'])
        
        params.extend([size, (page - 1) * size])
        query += f' ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?'
        cursor.execute(query, params)
        expenses = cursor.fetchall()
        
        query_count = 'SELECT COUNT(*) FROM expenses WHERE user_id = ?'
        count_params = [user_id]
        
        if filters.get('category'):
            query_count += ' AND category = ?'
            count_params.append(filters['category'])
        
        if filters.get('start_date'):
            query_count += ' AND date >= ?'
            count_params.append(filters['start_date'])

        if filters.get('end_date'):
            query_count += ' AND date <= ?'
            count_params.append(filters['end_date'])

        if filters.get('min_amount'):
            query_count += ' AND amount >= ?'
            count_params.append(filters['min_amount'])

        if filters.get('max_amount'):
            query_count += ' AND amount <= ?'
            count_params.append(filters['max_amount'])
        total_expenses = conn.execute(query_count, count_params).fetchone()[0]
        conn.close()
        
        return expenses, total_expenses
    def add_expense(user_id, amount, category, description, date):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, amount, category, description, date))
        conn.commit()
        conn.close()
    def update_expense(expense_id, amount, category, description, date):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE expenses SET  amount = ?, category = ?, description = ?, date = ? WHERE id = ?",
                       (amount, category, description, date, expense_id))
        conn.commit()
        conn.close()
    def get_report(user_id):
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute("""
            SELECT SUM(amount) AS total
            FROM expenses
            WHERE strftime('%Y', date) = ? and user_id = ?
        """, (now.strftime('%Y'), user_id))
        total_year = '{:,.0f}'.format(cursor.fetchone()[0])

        cursor.execute("""
        SELECT SUM(amount) AS total
        FROM expenses
        WHERE strftime('%m', date) = ? and user_id = ?
        """, (now.strftime('%m'), user_id))
        total_month = '{:,.0f}'.format(cursor.fetchone()[0])
        
        start_of_week = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT SUM(amount) AS total
            FROM expenses
            WHERE date >= ?
        """, (start_of_week,))
        total_week = '{:,.0f}'.format(cursor.fetchone()[0])
        cursor.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
        FROM expenses
        WHERE strftime('%Y', date) = '2024' and user_id = ?
        GROUP BY month
        ORDER BY month
        """, (user_id,))
        line_data = [{'x': f'{row[0]}-01', 'y': row[1]} for row in cursor.fetchall()]

        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            where user_id = ?
            GROUP BY category
            ORDER BY total DESC
        """, (user_id,))

        pie_data = [{'name': row[0], 'value': row[1]} for row in  cursor.fetchall()]
        conn.close()
        return line_data, pie_data, total_week, total_month, total_year
    def get_connection():
        conn = sqlite3.connect('pig_save.db')
        cursor = conn.cursor()
        return conn, cursor