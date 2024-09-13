import sqlite3
import random
from datetime import datetime, timedelta

# Connect to your SQLite database
conn = sqlite3.connect('../pig_save.db')
cursor = conn.cursor()

def generate_random_data():
    categories = ['Food', 'Travel', 'Utilities', 'Entertainment', 'Healthcare', 'Others']
    descriptions = ['Groceries', 'Bus ticket', 'Electric bill', 'Movie ticket', 'Doctor visit', 'Miscellaneous']
    amount = random.randrange(1000, 50000001, 1000)
    category = random.choice(categories)
    description = random.choice(descriptions)
    date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')  # Random date within the past year
    print('called!!')
    return (1, amount, category, description, date)

# Insert 500 random records

for _ in range(500):
    data = generate_random_data()
    cursor.execute('''
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    ''', data)
conn.commit()
conn.close()