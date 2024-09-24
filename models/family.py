import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('pig_save.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_family(family_name, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO family (family_name) VALUES (?)", (family_name,))
    cursor.execute("INSERT INTO family_members (family_id, user_id) VALUES (?, ?)", (cursor.lastrowid, user_id))
    conn.commit()
    conn.close()

def add_family_member(family_id, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    if user_id:
        user_id = user_id[0]
        cursor.execute("INSERT INTO family_members (family_id, user_id) VALUES (?, ?)", (family_id, user_id))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False
def get_all_family(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, f.family_name
        FROM family_members fm
        LEFT JOIN family f ON fm.family_id = f.id
        WHERE fm.user_id = ?
    """, (user_id,))
    families = cursor.fetchall()
    lst_family = []
    for f in families:
       
       lst_family.append({
           'family_name': f[1],
           'id': f[0],
           'data': get_family_expenses(f[0])
           })
    conn.commit()
    conn.close()
    return lst_family
def get_family_expenses(family_id):
    current_year = datetime.now().strftime('%Y')
    current_month = datetime.now().strftime('%m')
    current_week = datetime.now().strftime('%W')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN strftime('%Y', e.date) = ? THEN e.amount ELSE 0 END) as total_year,
            SUM(CASE WHEN strftime('%Y-%m', e.date) = ? THEN e.amount ELSE 0 END) as total_month,
            SUM(CASE WHEN strftime('%Y-%W', e.date) = ? THEN e.amount ELSE 0 END) as total_week
        FROM family_members fm
        JOIN users u ON u.id = fm.user_id
        JOIN expenses e ON e.user_id = u.id
        WHERE fm.family_id = ?
    """, (current_year, f"{current_year}-{current_month}", f"{current_year}-{current_week}", family_id))

    total_family_expenses = cursor.fetchone()

    cursor.execute("""
        SELECT u.name,
               SUM(CASE WHEN strftime('%Y', e.date) = ? THEN e.amount ELSE 0 END) as total_year,
               SUM(CASE WHEN strftime('%Y-%m', e.date) = ? THEN e.amount ELSE 0 END) as total_month,
               SUM(CASE WHEN strftime('%Y-%W', e.date) = ? THEN e.amount ELSE 0 END) as total_week,
                   u.id
        FROM family_members fm
        JOIN users u ON u.id = fm.user_id
        LEFT JOIN expenses e ON e.user_id = u.id
        WHERE fm.family_id = ?
        GROUP BY u.name
    """, (current_year, f"{current_year}-{current_month}", f"{current_year}-{current_week}", family_id))

    member_expenses = cursor.fetchall()
    conn.close()

    member_expenses_list = [
        {
            'id': row[4],
            'name': row[0],
            'total_year': '{:,.0f}'.format(row[1] or 0),
            'total_month': '{:,.0f}'.format(row[2] or 0),
            'total_week': '{:,.0f}'.format(row[3] or 0)
        }
        for row in member_expenses
    ]

    return {
        'total_family': {
            'total_year': '{:,.0f}'.format(total_family_expenses[0] or 0),
            'total_month': '{:,.0f}'.format(total_family_expenses[1] or 0),
            'total_week': '{:,.0f}'.format(total_family_expenses[2] or 0)
        },
        'members': member_expenses_list
    }

