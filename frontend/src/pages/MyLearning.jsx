import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchMyEnrollments } from '../api/courseApi';
import './MyLearning.css';

const MyLearning = () => {
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getEnrolled = async () => {
      try {
        const data = await fetchMyEnrollments();
        setEnrolledCourses(data);
      } catch (err) {
        console.error('Failed to load enrolled courses:', err);
      } finally {
        setLoading(false);
      }
    };
    getEnrolled();
  }, []);

  return (
    <div className="my-learning-container">
      <h1>My Learning</h1>
      {loading ? (
        <p className="loading-text">Loading your enrolled courses...</p>
      ) : enrolledCourses.length > 0 ? (
        <div className="courses-grid">
          {enrolledCourses.map((course) => (
            <div key={course.id} className="enrolled-card">
              <img
                src={course.thumbnail_url || 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500'}
                alt={course.title}
                className="enrolled-card-img"
              />
              <div className="enrolled-card-body">
                <h3>{course.title}</h3>
                <p>{course.description}</p>
                <Link to={`/learning/${course.id}`} className="btn-start-learning">
                  Start Learning
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-enrollments">
          <p>You haven't enrolled in any courses yet.</p>
          <Link to="/" className="btn-explore">
            Explore Catalog
          </Link>
        </div>
      )}
    </div>
  );
};

export default MyLearning;