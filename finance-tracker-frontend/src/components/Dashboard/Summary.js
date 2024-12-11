import React, { useState, useEffect } from 'react';
import api from '../../api/financeApi';
import './summary.css';

function Summary({ token }) { // Accept token as a prop
  const [month, setMonth] = useState('');
  const [expenses, setExpenses] = useState([]);
  const [budget, setBudget] = useState(null);
  const [summary, setSummary] = useState({ total_expenses: 0, total_transactions: 0 });

  useEffect(() => {
    if (month) {
      const fetchSummaryData = async () => {
        try {
          const [year, monthNum] = month.split('-');
          const expensesResponse = await api.get(`/expenses?month=${monthNum}&year=${year}`, { headers: { Authorization: `Bearer ${token}` } });
          setExpenses(expensesResponse.data);

          const budgetsResponse = await api.get(`/budgets`, { headers: { Authorization: `Bearer ${token}` } });
          const selectedBudget = budgetsResponse.data.find(budget => {
            const budgetDate = new Date(budget.start_date);
            return budgetDate.getFullYear() === parseInt(year) && (budgetDate.getMonth() + 1) === parseInt(monthNum);
          });
          setBudget(selectedBudget || null);

          const summaryResponse = await api.get('/summary', { params: { month: monthNum, year: year }, headers: { Authorization: `Bearer ${token}` } });
          setSummary(summaryResponse.data);
        } catch (error) {
          console.error("Error fetching summary data:", error);
        }
      };
      fetchSummaryData();
    }
  }, [month, token]);

  return (
    <div className="summary-container">
      <h2>Summary</h2>
      <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
      <div className="summary-details">
        <h3>Expenses</h3>
        {expenses.length > 0 ? (
          <ul>
            {expenses.map((expense, idx) => (
              <li key={idx}>
                {expense.description}: Rs{expense.amount} ({expense.payment_method})
              </li>
            ))}
          </ul>
        ) : (
          <p>No expenses for this month.</p>
        )}
      </div>
      <div className="summary-details">
        <h3>Budget</h3>
        {budget ? (
          <p>Amount: Rs{budget.amount} (Month: {new Date(budget.start_date).toLocaleString('default', { month: 'long', year: 'numeric' })})</p>
        ) : (
          <p>No budget for this month.</p>
        )}
      </div>
      <div className="summary-overview">
        <h3>Overview</h3>
        <p>Total Expenses: Rs{summary.total_expenses}</p>
        <p>Total Transactions: {summary.total_transactions}</p>
      </div>
    </div>
  );
}

export default Summary;
