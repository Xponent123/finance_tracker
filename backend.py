from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import os

key = os.urandom(24)
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'bomb$astic005',
    'database': 'finance_tracker'
}

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split()[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# User routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('email'):
        return jsonify({'error': 'Email is required!'}), 400
    hashed_password = generate_password_hash(data['password'])
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                      (data['username'], data['email'], hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], data['password']):
            token = jwt.encode({
                'user_id': user['user_id'],
                'exp': datetime.utcnow() + timedelta(days=1)  # 24 hour expiration
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'token': token,
                'user_id': user['user_id'],
                'username': user['username']
            })
        
        return jsonify({'message': 'Invalid credentials!'}), 401
    finally:
        cursor.close()
        conn.close()

# Expense routes
@app.route('/api/expenses', methods=['POST'])
@token_required
def add_expense(current_user):
    data = request.get_json()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO expenses (user_id, category_id, amount, description, expense_date, payment_method) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (current_user, data['category_id'], data['amount'], data['description'], data['expense_date'], data['payment_method']))
        conn.commit()
        return jsonify({'message': 'Expense added successfully!', 'id': cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/expenses', methods=['GET'])
@token_required
def get_expenses(current_user):
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT e.*, c.category_name FROM expenses e JOIN categories c ON e.category_id = c.category_id WHERE e.user_id = %s AND YEAR(e.expense_date) = %s AND MONTH(e.expense_date) = %s ORDER BY e.expense_date DESC", 
                      (current_user, year, month))
        expenses = cursor.fetchall()
        return jsonify(expenses)
    finally:
        cursor.close()
        conn.close()

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM expenses WHERE user_id = %s AND expense_id = %s", (current_user, expense_id))
        conn.commit()
        return jsonify({'message': 'Expense deleted successfully!'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# Budget routes
@app.route('/api/budgets', methods=['POST'])
@token_required
def add_budget(current_user):
    data = request.get_json()
    start_date = data['start_date']
    end_date = data['end_date']
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Check if a budget already exists for the given month
        cursor.execute("""
            SELECT * FROM budgets 
            WHERE user_id = %s AND 
                  YEAR(start_date) = YEAR(%s) AND 
                  MONTH(start_date) = MONTH(%s)
        """, (current_user, start_date, start_date))
        existing_budget = cursor.fetchone()
        
        if (existing_budget):
            return jsonify({'error': 'A budget already exists for this month!'}), 400
        
        cursor.execute("INSERT INTO budgets (user_id, amount, start_date, end_date) VALUES (%s, %s, %s, %s)", 
                      (current_user, data['amount'], start_date, end_date))
        conn.commit()
        return jsonify({'message': 'Budget added successfully!', 'id': cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error: {err}")  # Log the error to the console
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()
    return jsonify({'message': 'An unexpected error occurred!'}), 500

@app.route('/api/budgets', methods=['GET'])
@token_required
def get_budgets(current_user):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM budgets WHERE user_id = %s ORDER BY start_date DESC", (current_user,))
        budgets = cursor.fetchall()
        return jsonify(budgets)
    finally:
        cursor.close()
        conn.close()

# Category routes
@app.route('/api/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM categories WHERE is_default = TRUE OR user_id = %s ORDER BY category_name", (current_user,))
        categories = cursor.fetchall()
        return jsonify(categories)
    finally:
        cursor.close()
        conn.close()

@app.route('/api/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:                                                                            
        cursor.execute("""
            SELECT 
                COALESCE(SUM(amount), 0) as total_expenses,
                COUNT(expense_id) as total_transactions
            FROM expenses
            WHERE user_id = %s AND YEAR(expense_date) = %s AND MONTH(expense_date) = %s
        """, (current_user, year, month))
        summary = cursor.fetchone()
        return jsonify(summary)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
