import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function CheckoutModal({ course, onClose }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    card_number: '4242 4242 4242 4242',
    card_holder: 'Ali Waqar',
    expiry: '12/28',
    cvv: '123',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        'http://localhost:8000/api/v1/financials/checkout',
        {
          course_id: course.id,
          ...formData,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setLoading(false);
      setSuccessMsg('🎉 Payment successful! Redirecting to My Learning...');

      setTimeout(() => {
        navigate('/my-learning');
      }, 2000);
    } catch (err) {
      setLoading(false);
      const detail = err.response?.data?.detail || 'Payment failed.';
      
      // If student is already enrolled, show friendly message and redirect
      if (detail.includes('already enrolled')) {
        setSuccessMsg('You are already enrolled! Redirecting to My Learning...');
        setTimeout(() => {
          navigate('/my-learning');
        }, 1500);
      } else {
        setError(detail);
      }
    }
  };

  return (
    <div style={backdropStyle}>
      <div style={modalStyle}>
        <h3>Checkout: {course.title}</h3>
        <p style={{ fontWeight: 'bold', color: '#a435f0', fontSize: '1.2rem', margin: '0.5rem 0 1rem' }}>
          Price: ${course.price}
        </p>

        {successMsg && <div style={successStyle}>{successMsg}</div>}
        {error && <div style={errorStyle}>{error}</div>}

        {!successMsg && (
          <form onSubmit={handleSubmit}>
            <div style={inputGroup}>
              <label>Cardholder Name</label>
              <input
                type="text"
                name="card_holder"
                value={formData.card_holder}
                onChange={handleChange}
                required
                style={inputStyle}
              />
            </div>

            <div style={inputGroup}>
              <label>Card Number (Dummy)</label>
              <input
                type="text"
                name="card_number"
                value={formData.card_number}
                onChange={handleChange}
                required
                style={inputStyle}
              />
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <div style={{ ...inputGroup, flex: 1 }}>
                <label>Expiry (MM/YY)</label>
                <input
                  type="text"
                  name="expiry"
                  value={formData.expiry}
                  onChange={handleChange}
                  required
                  style={inputStyle}
                />
              </div>
              <div style={{ ...inputGroup, flex: 1 }}>
                <label>CVV</label>
                <input
                  type="password"
                  name="cvv"
                  value={formData.cvv}
                  onChange={handleChange}
                  required
                  style={inputStyle}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '1.5rem' }}>
              <button type="button" onClick={onClose} style={cancelBtnStyle} disabled={loading}>
                Cancel
              </button>
              <button type="submit" style={payBtnStyle} disabled={loading}>
                {loading ? 'Processing...' : `Pay $${course.price}`}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

const backdropStyle = {
  position: 'fixed',
  top: 0, left: 0, right: 0, bottom: 0,
  backgroundColor: 'rgba(0,0,0,0.5)',
  display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000,
};

const modalStyle = {
  backgroundColor: '#fff', padding: '2rem', borderRadius: '8px',
  width: '100%', maxWidth: '450px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
};

const inputGroup = { display: 'flex', flexDirection: 'column', marginBottom: '1rem' };
const inputStyle = { padding: '0.6rem', borderRadius: '4px', border: '1px solid #ccc', marginTop: '0.2rem' };
const successStyle = { backgroundColor: '#dcfce7', color: '#15803d', padding: '1rem', borderRadius: '6px', fontWeight: 'bold', textAlign: 'center', margin: '1rem 0' };
const errorStyle = { backgroundColor: '#fee2e2', color: '#991b1b', padding: '0.6rem', borderRadius: '4px', marginBottom: '1rem', fontSize: '0.9rem' };
const cancelBtnStyle = { padding: '0.6rem 1.2rem', borderRadius: '4px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer' };
const payBtnStyle = { padding: '0.6rem 1.2rem', borderRadius: '4px', border: 'none', backgroundColor: '#a435f0', color: '#fff', fontWeight: 'bold', cursor: 'pointer' };