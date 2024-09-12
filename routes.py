from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from models.user import User
from models.expense import Expense
from functions.auth import auth_user
import math

routes = Blueprint('main', __name__)

@routes.route('/')
def home():
    return render_template('index.html')

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('main.register'))
        
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose another.')
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                           (username, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('main.login'))
        
        conn.close()

    return render_template('auth/register.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if auth_user(username, password):
            flash('Login successful!')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('auth/login.html')


@routes.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user = current_user)

@routes.route('/expenses')
@login_required
def expenses():
    user_id = current_user.id
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 5, type=int)
    sort_by = request.args.get('sort_by', 'date')  # Default to sorting by date
    sort_order = request.args.get('sort_order', 'asc')  # Default to ascending order

    filters = {key: request.args.get(key) for key in ['category', 'start_date', 'end_date', 'min_amount', 'max_amount']}
    expenses, total_expenses = Expense.get_expenses(user_id, page, size, filters, sort_by, sort_order)

    total_pages = math.ceil(total_expenses / size)
    max_pages_displayed = 4
    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + max_pages_displayed - 1)

    if end_page - start_page < max_pages_displayed - 1:
        start_page = max(1, end_page - max_pages_displayed + 1)

    return render_template('expense/list.html', 
                           expenses=expenses,
                           page=page,
                           total_pages=total_pages,
                           end_page=end_page,
                           start_page=start_page,
                           filters=filters,
                           size=size,
                           sort_by=sort_by,
                           sort_order=sort_order)

@routes.route('/add_expense', methods=['POST'])
def add_expense():
    amount, category, description, date = [request.form[key] for key in ['amount', 'category', 'description', 'date']]
    page = request.form.get('page', 1, type=int)
    size = request.form.get('size', 5, type=int)
    filters = {key: request.form.get(key) for key in ['category', 'start_date', 'end_date', 'min_amount', 'max_amount']}
    Expense.add_expense(current_user.id, amount, category, description, date)
    return redirect(url_for('main.expenses', page=page, size=size, **filters))
@routes.route('/edit_expense', methods=['POST'])
def edit_expense():
    expense_id = request.form['expenseId']
    amount, category, description, date = [request.form[key] for key in ['amount', 'category', 'description', 'date']]
    filters = {key: request.form.get(key) for key in ['category_filter', 'start_date', 'end_date', 'min_amount', 'max_amount']}
    page = request.form.get('page', 1, type=int)
    size = request.form.get('size', 5, type=int)
    Expense.update_expense(expense_id, amount, category, description, date)
    return redirect(url_for('main.expenses', page=page, size=size, **filters))

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))
