import { useEffect, useState } from 'react';
import { fetchCourses } from '../api/courseApi';
import CourseCard from '../components/course/CourseCard';
import './Home.css';

const Home = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getCourses = async () => {
      try {
        const data = await fetchCourses();
        setCourses(data);
      } catch (error) {
        console.error('Failed to load courses:', error);
      } finally {
        setLoading(false);
      }
    };
    getCourses();
  }, []);

  return (
    <div className="catalog-container">
      <header className="hero-banner">
        <h1>Learn Without Limits</h1>
        <p>Start, switch, or advance your career with real-world skills.</p>
      </header>

      <section className="courses-section">
        <h2>Featured Courses</h2>
        {loading ? (
          <p className="loading-text">Loading catalog...</p>
        ) : courses.length > 0 ? (
          <div className="courses-grid">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        ) : (
          <p className="empty-text">No published courses available yet.</p>
        )}
      </section>
    </div>
  );
};

export default Home;