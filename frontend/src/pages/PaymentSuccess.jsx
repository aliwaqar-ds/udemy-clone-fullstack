import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const PaymentSuccess = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/my-learning');
    }, 3000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      <h1 style={{ color: '#16a34a' }}>🎉 Payment Successful!</h1>
      <p>Thank you for your purchase. You are now enrolled in the course.</p>
      <p style={{ color: '#64748b' }}>Redirecting to My Learning...</p>
    </div>
  );
};

export default PaymentSuccess;