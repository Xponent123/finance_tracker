import React, { useState, useEffect } from 'react';
import api from '../../api/financeApi';
import './Summary.css';

function Summary({ token }) {
  const [expenses, setExpenses] = useState([]);
  const [budget, setBudget] = useState(null);
  const [loading, setLoading] = useState(false);
  const [totalExpense, setTotalExpense] = useState(0);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1); // Initialize with current month
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear()); 

  const fetchSummaryData = async (month, year) => {
    setLoading(true);
    try {
      const currentMonth = `${year}-${month < 10 ? '0' + month : month}`;

      const expensesResponse = await api.get(`/expenses?month=${month}&year=${year}`, { headers: { Authorization: `Bearer ${token}` } });
      setExpenses(expensesResponse.data);

      const total = expensesResponse.data.reduce((sum, expense) => sum + parseFloat(expense.amount), 0); // Ensure correct summation
      setTotalExpense(total.toFixed(2)); // Round to 2 decimal places

      const budgetsResponse = await api.get('/budgets', { headers: { Authorization: `Bearer ${token}` } });
      const currentMonthBudget = budgetsResponse.data.find(b => b.month === currentMonth);
      setBudget(currentMonthBudget || null);

      setLoading(false);
    } catch (error) {
      console.error("Error fetching summary data:", error);
      setLoading(false);
    }
  };

  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
  };

  const handleYearChange = (event) => {
    setSelectedYear(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedMonth && selectedYear) {
      fetchSummaryData(selectedMonth, selectedYear);
    }
  };

  useEffect(() => {
    fetchSummaryData(new Date().getMonth() + 1, new Date().getFullYear());
  }, [token]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="summary-container">
      <h2>Summary</h2>

      {/* Month and Year Selection */}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="month">Month: </label>
          <select id="month" value={selectedMonth} onChange={handleMonthChange}>
            {[...Array(12)].map((_, i) => (
              <option key={i} value={i + 1}>
                {new Date(0, i).toLocaleString('default', { month: 'long' })}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="year">Year: </label>
          <select id="year" value={selectedYear} onChange={handleYearChange}>
            {[...Array(5)].map((_, i) => (
              <option key={i} value={selectedYear - i}>
                {selectedYear - i}
              </option>
            ))}
          </select>
        </div>
        <button type="submit">View Summary</button>
      </form>

      <div className="summary-section">
        <h3>Expenses for {new Date(selectedYear, selectedMonth - 1).toLocaleString('default', { month: 'long' })} {selectedYear}</h3>
        {expenses.length > 0 ? (
          <ul className="summary-list">
            {expenses.map((expense, idx) => (
              <li key={idx}>
                {expense.description}: Rs {expense.amount} ({expense.payment_method})
              </li>
            ))}
          </ul>
        ) : (
          <p>No expenses recorded for this month.</p>
        )}
        <p>Total Expense: Rs {totalExpense}</p> {/* Display total expense */}
      </div>

      <div className="summary-section">
        <h3>Budget</h3>
        {budget ? (
          <p>Budget Amount: Rs{budget.amount}</p>
        ) : (
          <p>No budget set for this month.</p>
        )}
      </div>
    </div>
  );
}

export default Summary;
