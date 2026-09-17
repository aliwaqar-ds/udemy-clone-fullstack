import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchInstructorCourses } from '../api/courseApi';
import './InstructorDashboard.css';

const InstructorDashboard = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await fetchInstructorCourses();
        setCourses(data);
      } catch (err) {
        console.error('Failed to load instructor courses:', err);
      } finally {
        setLoading(false);
      }
    };
    loadCourses();
  }, []);

  if (loading) return <div className="instructor-loading">Loading dashboard...</div>;

  return (
    <div className="instructor-container">
      <div className="instructor-header">
        <div>
          <h1>Instructor Dashboard</h1>
          <p>Manage your existing courses or create a new one.</p>
        </div>
        <Link to="/instructor/create-course" className="btn-create-course">
          + Create New Course
        </Link>
      </div>

      {courses.length === 0 ? (
        <div className="empty-instructor-state">
          <h3>No courses created yet</h3>
          <p>Get started by creating your very first course!</p>
          <Link to="/instructor/create-course" className="btn-create-course">
            Create Course
          </Link>
        </div>
      ) : (
        <div className="instructor-courses-grid">
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