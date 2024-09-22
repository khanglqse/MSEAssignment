from flask import Blueprint, render_template, redirect, url_for, request, flash, Response,session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from models.user import User
from models.expense import Expense
import models.family as Family
from functions.auth import auth_user
import math
import csv
import io
from core.currency_exchange import get_exchange_rate
from flask_babel import gettext as _
routes = Blueprint('main', __name__)
auth_routes = Blueprint('auth', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
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
            cursor.execute('INSERT INTO users (username, name, password) VALUES (?, ?, ?)', 
                           (username, name, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('auth.login'))
        
        conn.close()

    return render_template('auth/register.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if auth_user(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('auth/login.html')

@routes.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')

@routes.route('/update_language', methods=['POST'])
def update_language():
    language = request.form.get('language')
    if language:
        User.update_language(current_user.id, language)
        login_user(current_user, remember=True)
        flash("Language preference updated!", "success")
    return redirect(url_for('main.profile'))


@routes.route('/dashboard')
@login_required
def dashboard():
    line_data, pie_data, total_week, total_month, total_year = Expense.get_report(current_user.id)
    total_week = get_amount(float(total_week))
    total_month = get_amount(float(total_month))
    total_year = get_amount(float(total_year))
    return render_template('dashboard.html', user = current_user, line_data = line_data, pie_data = pie_data, total_week = total_week, total_month = total_month, total_year = total_year)

@routes.route('/expenses')
@login_required
def expenses():
    user_id = current_user.id
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 5, type=int)
    sort_by = request.args.get('sort_by', 'date') 
    sort_order = request.args.get('sort_order', 'asc')  

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
    flash('Expense added successfully!', 'success')
    return redirect(url_for('main.expenses', page=page, size=size))


@routes.route('/edit_expense', methods=['POST'])
def edit_expense():
    expense_id = request.form['expenseId']
    amount, category, description, date = [request.form[key] for key in ['amount', 'category', 'description', 'date']]
    filters = {key: request.form.get(key) for key in ['category_filter', 'start_date', 'end_date', 'min_amount', 'max_amount']}
    page = request.form.get('page', 1, type=int)
    size = request.form.get('size', 5, type=int)
    Expense.update_expense(expense_id, amount, category, description, date)
    return redirect(url_for('main.expenses', page=page, size=size))

#
@routes.route('/add_family', methods=['POST'])
def add_family():
    family_name = request.form['family_name']
    Family.add_family(family_name, current_user.id)
    return redirect(url_for('main.family'))

@routes.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['member_name']
    f_id = request.form['family_id']
    Family.add_family_member(f_id, name)
    return redirect(url_for('main.family'))

@routes.route('/family')
@login_required
def family():
    families = Family.get_all_family(current_user.id)
    return render_template('family/family.html', families=families)

@routes.route('/export-expenses-csv')
def export_expenses_csv():
    sort_by = request.args.get('sort_by', 'date') 
    sort_order = request.args.get('sort_order', 'asc')  
    expenses = Expense.get_expenses(current_user.id, 1, 99999, dict(), sort_by, sort_order)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(['Id', 'Category', 'Amount', 'Date', 'Description'])
    
    for expense in expenses[0]:
        writer.writerow([str(expense[0]), str(expense[1]), expense[2], expense[3], expense[4], expense[5]])
    
    output.seek(0) 

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=expenses.csv"}
    )

@routes.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    Expense.delete_expense(expense_id)  
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('main.expenses'))

@routes.route('/update_currency', methods=['POST'])
@login_required
def update_currency():
    currency = request.form.get('currency')
    rate = get_exchange_rate()
    session['currency'] = currency
    session['rate'] = rate
    flash(f"Currency preference updated to {currency}!", "success")
    return redirect(url_for('main.dashboard'))

def get_amount(amount):
    currency = session.get('currency', 'VND')  
    if currency == 'USD':
        exchange_rate = session['rate']  
        return f"{'{:,.2f}'.format(amount / exchange_rate)} USD"  
    return f"{'{:,.0f}'.format(amount)} VND"

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
