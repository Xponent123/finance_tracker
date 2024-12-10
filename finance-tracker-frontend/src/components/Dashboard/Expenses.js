import React, { useState, useEffect } from 'react';
import api from '../../api/financeApi';
import './Expenses.css';
import { useNavigate } from 'react-router-dom'; // Import useNavigate from react-router-dom

function Expenses({ token, setToken }) {
  const navigate = useNavigate(); // Initialize useNavigate
  const [expenses, setExpenses] = useState([]);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [budget, setBudget] = useState('');

  const [budgets, setBudgets] = useState([]);
  const [showDeleteExpenses, setShowDeleteExpenses] = useState(false);
  const [budgetMonth, setBudgetMonth] = useState(''); // Add state for budget month

  useEffect(() => {
    const fetchExpensesAndBudgets = async () => {
      try {
        const expensesResponse = await api.get('/expenses', { headers: { Authorization: `Bearer ${token}` } });
        setExpenses(expensesResponse.data);
        
        const budgetsResponse = await api.get('/budgets', { headers: { Authorization: `Bearer ${token}` } });
        setBudgets(budgetsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchExpensesAndBudgets();
  }, [token]);

  const handleAddExpense = async (e) => {
    e.preventDefault();
    const newExpense = {
      amount,
      description,
      expense_date: new Date().toISOString().split('T')[0],
      payment_method: paymentMethod,
    };
    try {
      await api.post('/expenses', newExpense, { headers: { Authorization: `Bearer ${token}` } });
      setAmount('');
      setDescription('');
      setExpenses([...expenses, newExpense]);
    } catch (error) {
      console.error("Error adding expense:", error);
    }
  };

  const handleAddBudget = async (e) => {
    e.preventDefault();
  
    // Check for duplicate month
    if (budgets.some((b) => b.month === budgetMonth)) {
      alert(`A budget for ${budgetMonth} already exists.`);
      return;
    }
  
    const newBudget = {
      amount: budget,
      month: budgetMonth, // Use budget month
    };
  
    try {
      await api.post('/budgets', newBudget, { headers: { Authorization: `Bearer ${token}` } });
  
      setBudget('');
      setBudgetMonth('');
      setBudgets([...budgets, newBudget]); // Append the newly added budget to the list
    } catch (error) {
      console.error("Error adding budget:", error.response ? error.response.data : error.message);
    }
  };
  
  const handleDeleteExpense = async (expenseId) => {
    try {
      await api.delete(`/expenses/${expenseId}`, { headers: { Authorization: `Bearer ${token}` } });
      setExpenses(expenses.filter(expense => expense.expense_id !== expenseId));
    } catch (error) {
      console.error("Error deleting expense:", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  const handleGoToSummary = () => {
    navigate('/summary'); // Redirect to summary page
  };

  return (
    <div className="expenses-container">
      <div className="expense-box">
        <div className="expense-form-container">
          <h2>Add Expense</h2>
          <form className="expense-form" onSubmit={handleAddExpense}>
            <input type="number" placeholder="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
            <input type="text" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
            <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
              <option value="cash">Cash</option>
              <option value="credit_card">Credit</option>
              <option value="upi">UPI</option>
              <option value="other">Other</option>
            </select>
            <button type="submit">Add Expense</button>
          </form>
          <button className="logout-button" onClick={handleLogout}>Logout</button>
          <button className="delete-expense-button" onClick={() => setShowDeleteExpenses(!showDeleteExpenses)}>Delete Expense</button>
          <button className="summary-button" onClick={handleGoToSummary}>Go to Summary</button> {/* Add Go to Summary button */}
        </div>

        <div className="expense-list-container">
          <h2>Expenses</h2>
          <ul className="expenses-list">
            {expenses.map((expense, idx) => (
              <li key={idx}>
                {expense.description}: Rs{expense.amount} ({expense.payment_method})
                {showDeleteExpenses && (
                  <button onClick={() => handleDeleteExpense(expense.expense_id)}>Delete</button>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="budget-box">
        <div className="budget-form-container">
          <h2>Add Budget</h2>
          <form className="budget-form" onSubmit={handleAddBudget}>
            <input type="number" placeholder="Budget Amount" value={budget} onChange={(e) => setBudget(e.target.value)} />
            <input type="month" placeholder="Select Month" value={budgetMonth} onChange={(e) => setBudgetMonth(e.target.value)} /> {/* Add month input */}
            <button type="submit">Add Budget</button>
          </form>
        </div>

        <div className="budget-list-container">
          <h2>Budgets</h2>
          <ul className="budgets-list">
            {budgets.map((budget, idx) => (
              <li key={idx}>
                Amount: Rs{budget.amount} (Month: {budget.month}) {/* Display month */}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Expenses;
