import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Financials() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutMethod, setPayoutMethod] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const fetchFinancials = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(
        'http://localhost:8000/api/v1/financials/instructor/overview',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setData(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFinancials();
  }, []);

  const handlePayoutRequest = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        'http://localhost:8000/api/v1/financials/instructor/request-payout',
        {
          amount: parseFloat(payoutAmount),
          payout_method: payoutMethod,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setMessage('Payout request processed successfully!');
      setPayoutAmount('');
      setPayoutMethod('');
      fetchFinancials();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to request payout.');
    }
  };

  if (loading) return <div style={{ padding: '2rem' }}>Loading Financial Overview...</div>;

  return (
    <div style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1rem' }}>
      <h2>Instructor Financials & Payouts</h2>

      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', margin: '1.5rem 0' }}>
        <div style={cardStyle}>
          <h4>Gross Sales</h4>
          <p style={amountStyle}>${data.gross_revenue.toFixed(2)}</p>
        </div>
        <div style={cardStyle}>
          <h4>Your Net Earnings (80%)</h4>
          <p style={amountStyle}>${data.instructor_earnings.toFixed(2)}</p>
        </div>
        <div style={cardStyle}>
          <h4>Total Withdrawn</h4>
          <p style={amountStyle}>${data.total_withdrawn.toFixed(2)}</p>
        </div>
        <div style={{ ...cardStyle, borderLeft: '4px solid #a435f0' }}>
          <h4>Available Balance</h4>
          <p style={{ ...amountStyle, color: '#a435f0' }}>${data.available_balance.toFixed(2)}</p>
        </div>
      </div>

      {/* Payout Form */}
      <div style={{ backgroundColor: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '2rem' }}>
        <h3>Request Payout</h3>
        {message && <div style={{ color: 'green', marginBottom: '1rem' }}>{message}</div>}
        {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handlePayoutRequest} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.3rem' }}>Amount ($)</label>
            <input
              type="number"
              step="0.01"
              max={data.available_balance}
              placeholder="0.00"
              value={payoutAmount}
              onChange={(e) => setPayoutAmount(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.3rem' }}>Payout Method (e.g. PayPal Email)</label>
            <input
              type="text"
              placeholder="PayPal / Bank details"
              value={payoutMethod}
              onChange={(e) => setPayoutMethod(e.target.value)}
              required
              style={{ ...inputStyle, width: '250px' }}
            />
          </div>

          <button type="submit" style={buttonStyle} disabled={data.available_balance <= 0}>
            Withdraw Funds
          </button>
        </form>
      </div>

      {/* Transaction History Table */}
      <h3>Recent Sales</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
        <thead>
          <tr style={{ backgroundColor: '#f1f5f9', textAlign: 'left' }}>
            <th style={thTd}>Date</th>
            <th style={thTd}>Gross Amount</th>
            <th style={thTd}>Your Earnings (80%)</th>
            <th style={thTd}>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.transactions.length === 0 ? (
            <tr><td colSpan="4" style={thTd}>No course sales yet.</td></tr>
          ) : (
            data.transactions.map((t) => (
              <tr key={t.id}>
                <td style={thTd}>{new Date(t.created_at).toLocaleDateString()}</td>
                <td style={thTd}>${t.amount.toFixed(2)}</td>
                <td style={thTd}>${t.instructor_earnings.toFixed(2)}</td>
                <td style={thTd}><span style={{ color: 'green', fontWeight: 'bold' }}>{t.status}</span></td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

const cardStyle = {
  backgroundColor: '#fff',
  padding: '1.2rem',
  borderRadius: '8px',
  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
  border: '1px solid #e2e8f0',
};

const amountStyle = {
  fontSize: '1.5rem',
  fontWeight: 'bold',
  marginTop: '0.5rem',
  color: '#1e293b',
};

const inputStyle = {
  padding: '0.6rem',
  borderRadius: '4px',
  border: '1px solid #cbd5e1',
};

const buttonStyle = {
  padding: '0.6rem 1.2rem',
  backgroundColor: '#a435f0',
  color: '#fff',
  border: 'none',
  borderRadius: '4px',
  fontWeight: 'bold',
  cursor: 'pointer',
};

const thTd = {
  padding: '0.8rem',
  borderBottom: '1px solid #e2e8f0',
};