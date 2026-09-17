import { useNavigate } from 'react-router-dom';

const PaymentCancelled = () => {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      <h1 style={{ color: '#dc2626' }}>Payment Cancelled</h1>
      <p>Your transaction was not completed.</p>
      <button 
        onClick={() => navigate('/')} 
        style={{ marginTop: '1rem', padding: '0.6rem 1.2rem', cursor: 'pointer' }}
      >
        Return to Catalog
      </button>
    </div>
  );
};

export default PaymentCancelled;