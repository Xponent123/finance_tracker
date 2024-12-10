import mysql.connector
from mysql.connector import Error
from datetime import datetime

class FinanceDBManager:
    def __init__(self):
        # Direct database configuration
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Bomb$astic005',  # Replace with your MySQL password
            'database': 'finance_tracker'
        }

    def connect(self):
        """Create database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def create_database(self):
        """Create the database and tables"""
        try:
            # Connect without database selected
            connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )
            
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS finance_tracker")
            cursor.execute("USE finance_tracker")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    status ENUM('active', 'inactive') DEFAULT 'active'
                )
            """)
            
            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    category_name VARCHAR(50) NOT NULL,
                    description TEXT,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE KEY unique_category_per_user (user_id, category_name)
                )
            """)
            
            # Create expenses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    category_id INT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    description TEXT,
                    expense_date DATE NOT NULL,
                    payment_method ENUM('cash', 'credit_card', 'debit_card', 'upi', 'other'),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
                )
            """)
            
            # Create budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    budget_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    category_id INT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT,
                    UNIQUE KEY unique_budget (user_id, category_id, start_date, end_date)
                )
            """)

            # Insert default categories
            default_categories = [
                ('Food & Dining', 'Restaurants, groceries, and dining expenses'),
                ('Transportation', 'Fuel, public transport, and vehicle maintenance'),
                ('Housing', 'Rent, mortgage, and housing maintenance'),
                ('Utilities', 'Electricity, water, gas, and internet bills'),
                ('Healthcare', 'Medical expenses and insurance'),
                ('Entertainment', 'Movies, games, and recreational activities'),
                ('Shopping', 'Clothing, electronics, and personal items'),
                ('Education', 'Tuition, books, and courses'),
                ('Savings', 'Money set aside for future use'),
                ('Others', 'Miscellaneous expenses')
            ]

            for category_name, description in default_categories:
                cursor.execute("""
                    INSERT IGNORE INTO categories (category_name, description, is_default)
                    VALUES (%s, %s, TRUE)
                """, (category_name, description))

            connection.commit()
            print("Database and tables created successfully!")
            
        except Error as e:
            print(f"Error creating database: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_expense(self, user_id, category_id, amount, description, expense_date, payment_method='cash'):
        """Add a new expense"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO expenses (user_id, category_id, amount, description, expense_date, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (user_id, category_id, amount, description, expense_date, payment_method)
            cursor.execute(query, values)
            connection.commit()
            return cursor.lastrowid
            
        except Error as e:
            print(f"Error adding expense: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_monthly_expenses(self, user_id, year, month):
        """Get monthly expenses with category names"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT e.*, c.category_name 
                FROM expenses e
                JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s 
                AND YEAR(e.expense_date) = %s 
                AND MONTH(e.expense_date) = %s
                ORDER BY e.expense_date DESC
            """
            cursor.execute(query, (user_id, year, month))
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting monthly expenses: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_expense_summary(self, user_id, year, month):
        """Get expense summary by category"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    c.category_name,
                    SUM(e.amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM expenses e
                JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s 
                AND YEAR(e.expense_date) = %s 
                AND MONTH(e.expense_date) = %s
                GROUP BY c.category_name
                ORDER BY total_amount DESC
            """
            cursor.execute(query, (user_id, year, month))
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting expense summary: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_categories(self, user_id=None):
        """Get all categories (default + user-specific if user_id provided)"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            if user_id:
                query = """
                    SELECT * FROM categories 
                    WHERE is_default = TRUE OR user_id = %s 
                    ORDER BY category_name
                """
                cursor.execute(query, (user_id,))
            else:
                query = "SELECT * FROM categories WHERE is_default = TRUE ORDER BY category_name"
                cursor.execute(query)
                
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting categories: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_yearly_summary(self, user_id, year):
        """Get yearly expense summary by month"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    MONTH(expense_date) as month,
                    SUM(amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM expenses
                WHERE user_id = %s 
                AND YEAR(expense_date) = %s
                GROUP BY MONTH(expense_date)
                ORDER BY month
            """
            cursor.execute(query, (user_id, year))
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting yearly summary: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Example usage
if __name__ == "__main__":
    # Initialize database manager
    db = FinanceDBManager()
    
    # Create database and tables (first time only)
    db.create_database()
    
    # Example: Add an expense
    expense_id = db.add_expense(
        user_id=1,  # Assuming user_id 1 exists
        category_id=1,  # Assuming category_id 1 exists
        amount=50.25,
        description="Grocery shopping",
        expense_date=datetime.now().date()
    )
    
    # Get current month's expenses
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Get monthly expenses
    monthly_expenses = db.get_monthly_expenses(1, current_year, current_month)
    print("\nMonthly Expenses:")
    print(monthly_expenses)
    
    # Get expense summary by category
    expense_summary = db.get_expense_summary(1, current_year, current_month)
    print("\nExpense Summary by Category:")
    print(expense_summary)
    
    # Get all categories
    categories = db.get_categories(user_id=1)
    print("\nAvailable Categories:")
    print(categories)
    
    # Get yearly summary
    yearly_summary = db.get_yearly_summary(1, current_year)
    print("\nYearly Summary:")
    print(yearly_summary)