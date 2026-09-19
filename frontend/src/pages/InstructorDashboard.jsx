import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchInstructorCourses, fetchInstructorAnalytics } from '../api/courseApi';
import './InstructorDashboard.css';

const InstructorDashboard = () => {
  const [courses, setCourses] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [coursesData, analyticsData] = await Promise.all([
          fetchInstructorCourses(),
          fetchInstructorAnalytics().catch(() => null),
        ]);
        setCourses(coursesData);
        setAnalytics(analyticsData);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardData();
  }, []);

  if (loading) return <div className="instructor-loading">Loading dashboard...</div>;

  return (
    <div className="instructor-container">
      <div className="instructor-header">
        <div>
          <h1>Instructor Dashboard</h1>
          <p>Track earnings, student enrollments, and course management.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link 
            to="/instructor/financials" 
            className="btn-create-course"
            style={{ backgroundColor: '#2563eb', border: 'none' }}
          >
            💳 Financials & Payouts
          </Link>
          <Link to="/instructor/create-course" className="btn-create-course">
            + Create New Course
          </Link>
        </div>
      </div>

      {/* 📊 Analytics Cards Grid */}
      {analytics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2.5rem' }}>
          <div style={{ background: '#fff', padding: '1.2rem', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '600' }}>TOTAL REVENUE</span>
            <h2 style={{ fontSize: '1.8rem', color: '#16a34a', margin: '0.3rem 0 0 0' }}>${analytics.total_revenue}</h2>
          </div>
          <div style={{ background: '#fff', padding: '1.2rem', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '600' }}>ENROLLED STUDENTS</span>
            <h2 style={{ fontSize: '1.8rem', color: '#2563eb', margin: '0.3rem 0 0 0' }}>{analytics.total_students}</h2>
          </div>
          <div style={{ background: '#fff', padding: '1.2rem', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '600' }}>TOTAL COURSES</span>
            <h2 style={{ fontSize: '1.8rem', color: '#9333ea', margin: '0.3rem 0 0 0' }}>{analytics.total_courses}</h2>
          </div>
          <div style={{ background: '#fff', padding: '1.2rem', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '600' }}>AVERAGE RATING</span>
            <h2 style={{ fontSize: '1.8rem', color: '#d97706', margin: '0.3rem 0 0 0' }}>⭐ {analytics.average_rating}</h2>
          </div>
        </div>
      )}

      <h2>Your Courses</h2>
      {courses.length === 0 ? (
        <div className="empty-instructor-state" style={{ marginTop: '1rem' }}>
          <h3>No courses created yet</h3>
          <p>Get started by creating your very first course!</p>
          <Link to="/instructor/create-course" className="btn-create-course">
            Create Course
          </Link>
        </div>
      ) : (
        <div className="instructor-courses-grid" style={{ marginTop: '1rem' }}>
          {courses.map((course) => (
            <div key={course.id} className="instructor-course-card">
              <img
                src={course.thumbnail_url || 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500'}
                alt={course.title}
                className="instructor-card-img"
              />
              <div className="instructor-card-body">
                <span className={`status-badge ${course.is_published ? 'published' : 'draft'}`}>
                  {course.is_published ? 'Published' : 'Draft'}
                </span>
                <h3>{course.title}</h3>
                <p className="price-text">${course.price}</p>
                <div className="card-actions">
                  <Link to={`/instructor/courses/${course.id}/curriculum`} className="btn-manage">
                    Manage Curriculum
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InstructorDashboard;