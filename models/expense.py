import sqlite3

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