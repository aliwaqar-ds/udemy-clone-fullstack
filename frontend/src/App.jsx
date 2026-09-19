import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import ProtectedRoute from './components/common/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import VerifyOtp from './pages/VerifyOtp';
import CourseDetail from './pages/CourseDetail';
import MyLearning from './pages/MyLearning';
import LearningPlayer from './pages/LearningPlayer';
import InstructorDashboard from './pages/InstructorDashboard';
import CreateCourse from './pages/CreateCourse';
import ManageCurriculum from './pages/ManageCurriculum';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentCancelled from './pages/PaymentCancelled'
import Financials from './pages/Financials';

const MainLayout = () => (
  <>
    <Navbar />
    <main>
      <Outlet />
    </main>
  </>
);

function App() {
  return (
    <Router>
      <Routes>
        {/* Standard Pages (WITH Navbar) */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-otp" element={<VerifyOtp />} />
          <Route path="/courses/:id" element={<CourseDetail />} />

          <Route element={<ProtectedRoute allowedRoles={['student', 'instructor']} />}>
            <Route path="/my-learning" element={<MyLearning />} />
            <Route path="/dashboard" element={<div style={{ padding: '2rem' }}>Student Dashboard</div>} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['instructor']} />}>
            <Route path="/instructor" element={<InstructorDashboard />} />
            <Route path="/instructor/create-course" element={<CreateCourse />} />
            <Route path="/instructor/courses/:courseId/curriculum" element={<ManageCurriculum />} />
          </Route>
        </Route>

        {/* Fullscreen Video Classroom (NO Navbar) */}
        <Route element={<ProtectedRoute allowedRoles={['student', 'instructor']} />}>
          <Route path="/learning/:courseId" element={<LearningPlayer />} />
        </Route>

        <Route path="/payment-success" element={<PaymentSuccess />} />
        <Route path="/payment-cancelled" element={<PaymentCancelled />} />

        <Route path="/instructor/financials" element={<Financials />} />

      </Routes>
    </Router>
  );
}

export default App;
