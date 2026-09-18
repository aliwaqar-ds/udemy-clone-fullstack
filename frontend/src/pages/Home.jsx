import { useEffect, useState } from 'react';
import { fetchCourses, getCategories } from '../api/courseApi';
import CourseCard from '../components/course/CourseCard';
import './Home.css';

const Home = () => {
  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await getCategories();
        setCategories(cats);
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    };
    loadCategories();
  }, []);

  useEffect(() => {
    const getCourses = async () => {
      setLoading(true);
      try {
        const data = await fetchCourses(search, selectedCategory);
        setCourses(data);
      } catch (error) {
        console.error('Failed to load courses:', error);
      } finally {
        setLoading(false);
      }
    };

    const delayDebounce = setTimeout(() => {
      getCourses();
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [search, selectedCategory]);

  return (
    <div className="catalog-container">
      <header className="hero-banner">
        <h1>Learn Without Limits</h1>
        <p>Start, switch, or advance your career with real-world skills.</p>
        
        {/* Search Input Bar */}
        <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'center' }}>
          <input
            type="text"
            placeholder="🔍 Search for courses by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              maxWidth: '500px',
              padding: '0.8rem 1.2rem',
              borderRadius: '25px',
              border: 'none',
              fontSize: '1rem',
              outline: 'none',
              color: '#1a1a1a'
            }}
          />
        </div>
      </header>

      {/* Category Pills Filter */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        <button
          onClick={() => setSelectedCategory('')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            border: '1px solid #a435f0',
            backgroundColor: selectedCategory === '' ? '#a435f0' : '#fff',
            color: selectedCategory === '' ? '#fff' : '#a435f0',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              border: '1px solid #a435f0',
              backgroundColor: selectedCategory === cat.id ? '#a435f0' : '#fff',
              color: selectedCategory === cat.id ? '#fff' : '#a435f0',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            {cat.name}
          </button>
        ))}
      </div>

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
          <p className="empty-text">No courses found matching your search.</p>
        )}
      </section>
    </div>
  );
};

export default Home;