import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation
import api from '../../api/financeApi';
import './summary.css';

function Summary({ token }) { // Accept token as a prop
  const [expenses, setExpenses] = useState([]);
  const [budget, setBudget] = useState(null);
  const [summary, setSummary] = useState({ total_expenses: 0, total_transactions: 0 });
  const [monthlySummaries, setMonthlySummaries] = useState([]); // Add state for monthly summaries
  const [totalExpenses, setTotalExpenses] = useState(null); // Initialize to null
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7)); // Add state for selected month
  const navigate = useNavigate(); // Initialize useNavigate

  const months = [
    { value: '01', label: 'January' },
    { value: '02', label: 'February' },
    { value: '03', label: 'March' },
    { value: '04', label: 'April' },
    { value: '05', label: 'May' },
    { value: '06', label: 'June' },
    { value: '07', label: 'July' },
    { value: '08', label: 'August' },
    { value: '09', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' },
  ];

  const years = Array.from(new Array(10), (val, index) => new Date().getFullYear() - index);

  useEffect(() => {
    const fetchSummaryData = async () => {
      try {
        const [year, monthNum] = selectedMonth.split('-');

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
  }, [token, selectedMonth]);

  useEffect(() => {
    const fetchMonthlySummaries = async () => {
      try {
        const response = await api.get('/summary/all', { headers: { Authorization: `Bearer ${token}` } });
        setMonthlySummaries(response.data);
        const total = response.data.reduce((acc, curr) => acc + curr.total_expenses, 0);
        setTotalExpenses(total); // Calculate total expenses
      } catch (error) {
        console.error("Error fetching monthly summaries:", error);
      }
    };
    fetchMonthlySummaries();
  }, [token]);

  const handleMonthChange = (e) => {
    const [year, month] = selectedMonth.split('-');
    setSelectedMonth(`${year}-${e.target.value}`);
  };

  const handleYearChange = (e) => {
    const [year, month] = selectedMonth.split('-');
    setSelectedMonth(`${e.target.value}-${month}`);
  };

  const handleBack = () => {
    navigate('/'); // Navigate back to the Expenses page
  };

  return (
    <div className="summary-container-wrapper">
      <button className="back-button" onClick={handleBack}>Back to Expenses</button> {/* Add Back button */}
      <div className="summary-container">
        <h2>Summary</h2>
        <div className="month-year-selectors">
          <select value={selectedMonth.split('-')[1]} onChange={handleMonthChange}>
            {months.map((month) => (
              <option key={month.value} value={month.value}>{month.label}</option>
            ))}
          </select>
          <select value={selectedMonth.split('-')[0]} onChange={handleYearChange}>
            {years.map((year) => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
        <div className="summary-details">
          <h3>Expenses</h3>
          {expenses.length > 0 ? (
            <ul>
              {expenses.map((expense, idx) => (
                <li key={idx}>
                  {expense.description}: Rs.{expense.amount} ({expense.payment_method})
                </li>
              ))}
            </ul>
          ) : (
            <p>No expenses for this month.</p>
          )}
        </div>
        <div className="summary-section">
          <h3>Budget</h3>
          {budget ? (
            <p>Amount: Rs.{budget.amount} (Month: {new Date(budget.start_date).toLocaleString('default', { month: 'long', year: 'numeric' })})</p>
          ) : (
            <p>No budget for this month.</p>
          )}
        </div>
        <div className="summary-section">
          <h3>Total Monthly Expenses</h3>
          <p>Rs.{summary.total_expenses}</p>
        </div>
        <div className="summary-section">
          <h3>Overview (All Months)</h3>
          <p>
            Total Expenses: {totalExpenses !== null ? `Rs.${parseFloat(totalExpenses, 10)}` : 'Loading...'}
          </p>
          <p>Total Transactions: {summary.total_transactions}</p>
        </div>

      </div>
      <div className="monthly-expenses-container">
        <h2>Monthly Expenses</h2>
        <ul>
          {monthlySummaries.map((monthlySummary, idx) => (
            <li key={idx}>
              {monthlySummary.month}: Rs.{monthlySummary.total_expenses}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Summary;
