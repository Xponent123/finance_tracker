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
    'password': 'Bomb$astic005',
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
        except:
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
        cursor.execute("INSERT INTO expenses (user_id, amount, description, expense_date, payment_method) VALUES (%s, %s, %s, %s, %s)", 
                      (current_user, data['amount'], data['description'], data['expense_date'], data['payment_method']))
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
        cursor.execute("SELECT * FROM expenses WHERE user_id = %s AND YEAR(expense_date) = %s AND MONTH(expense_date) = %s ORDER BY expense_date DESC", 
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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Check if a budget for this month already exists
        cursor.execute("SELECT id FROM budgets WHERE user_id = %s AND month = %s", (current_user, data['month']))
        existing_budget = cursor.fetchone()
        
        if existing_budget:
            return jsonify({'error': 'A budget for this month already exists!'}), 400
        
        # Add new budget
        cursor.execute("INSERT INTO budgets (user_id, amount, month) VALUES (%s, %s, %s)", 
                       (current_user, data['amount'], data['month']))
        conn.commit()
        return jsonify({'message': 'Budget added successfully!', 'id': cursor.lastrowid}), 201
    
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 400
    
    finally:
        cursor.close()
        conn.close()

@app.route('/api/budgets', methods=['GET'])
@token_required
def get_budgets(current_user):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM budgets WHERE user_id = %s ORDER BY month DESC", (current_user,))  # Order by month
        budgets = cursor.fetchall()
        return jsonify(budgets)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)