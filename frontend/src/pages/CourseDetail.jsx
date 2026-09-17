import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  fetchCourseById, 
  fetchCourseCurriculum, 
  createCheckoutSession, 
  enrollInCourse, 
  fetchMyEnrolledCourses,
  createReview,
  fetchCourseReviews 
} from '../api/courseApi';
import './CourseDetail.css';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [curriculum, setCurriculum] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  
  const [isOwner, setIsOwner] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);

  // Review form state
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reviewSubmitting, setReviewSubmitting] = useState(false);
  const [reviewError, setReviewError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      if (!id || id === 'undefined') return;
      setLoading(true);
      setError('');

      try {
        const courseData = await fetchCourseById(id);
        const curriculumData = await fetchCourseCurriculum(id);
        setCourse(courseData);
        setCurriculum(curriculumData);

        try {
          const reviewData = await fetchCourseReviews(id);
          setReviews(reviewData || []);
        } catch (revErr) {
          console.warn('Reviews could not be loaded:', revErr);
        }

        const token = localStorage.getItem('token');
        if (token) {
          // Verify if active user is course instructor
          try {
            const userRes = await fetch('http://127.0.0.1:8000/api/v1/auth/me', {
              headers: { Authorization: `Bearer ${token}` }
            });
            if (userRes.ok) {
              const userData = await userRes.json();
              if (userData.id === courseData.instructor_id) {
                setIsOwner(true);
              }
            }
          } catch (authErr) {
            console.warn('Could not verify instructor ownership:', authErr);
          }

          // Check student enrollment status
          try {
            const enrolledCourses = await fetchMyEnrolledCourses();
            const enrolled = enrolledCourses.some((c) => c.id === parseInt(id, 10));
            setIsEnrolled(enrolled);
          } catch (enrollErr) {
            console.warn('Could not verify enrollment status:', enrollErr);
          }
        }
      } catch (err) {
        setError('Failed to load course details.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id]);

  const handleEnrollOrBuy = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      if (course.price === 0) {
        await enrollInCourse(id);
        navigate('/my-learning');
      } else {
        const data = await createCheckoutSession(id);
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        } else {
          throw new Error('Failed to generate checkout session.');
        }
      }
    } catch (err) {
      setError(err.message || 'Payment initiation failed.');
      setProcessing(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setReviewSubmitting(true);
    setReviewError('');

    try {
      const newReview = await createReview({
        course_id: parseInt(id, 10),
        rating: Number(rating),
        comment,
      });
      setReviews([...reviews, newReview]);
      setComment('');
    } catch (err) {
      setReviewError(err.message || 'Failed to submit review.');
    } finally {
      setReviewSubmitting(false);
    }
  };

  if (loading) return <div className="detail-loading">Loading course details...</div>;
  if (error || !course) return <div className="detail-error">{error || 'Course not found.'}</div>;

  return (
    <div className="course-detail-container">
      <div className="course-header">
        <h1>{course.title}</h1>
        <p>{course.description || 'Master this course with hands-on practice.'}</p>
      </div>

      <div className="course-content-grid">
        <div className="curriculum-section">
          <h2>Course Content</h2>
          {curriculum.length === 0 ? (
            <p style={{ marginTop: '1rem', color: '#666' }}>No curriculum uploaded yet.</p>
          ) : (
            curriculum.map((section, idx) => (
              <div key={section.id || idx} className="section-block">
                <h3>Section {idx + 1}: {section.title}</h3>
                <ul>
                  {section.lessons?.map((lesson, lIdx) => (
                    <li key={lesson.id || lIdx}>
                      📖 {lesson.title} {lesson.duration_minutes > 0 && `(${lesson.duration_minutes} mins)`}
                    </li>
                  ))}
                </ul>
              </div>
            ))
          )}

          {/* Student Reviews Section */}
          <div className="reviews-section" style={{ marginTop: '2.5rem' }}>
            <h2>Student Reviews & Ratings</h2>

            {/* Render Review Form ONLY for enrolled students who are NOT the course owner */}
            {isEnrolled && !isOwner && (
              <form onSubmit={handleReviewSubmit} style={{ margin: '1rem 0', padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                <h3>Leave a Review</h3>
                {reviewError && <p style={{ color: 'red' }}>{reviewError}</p>}
                
                <div style={{ margin: '0.5rem 0' }}>
                  <label>Rating: </label>
                  <select value={rating} onChange={(e) => setRating(e.target.value)}>
                    <option value={5}>⭐⭐⭐⭐⭐ (5/5)</option>
                    <option value={4}>⭐⭐⭐⭐ (4/5)</option>
                    <option value={3}>⭐⭐⭐ (3/5)</option>
                    <option value={2}>⭐⭐ (2/5)</option>
                    <option value={1}>⭐ (1/5)</option>
                  </select>
                </div>

                <div style={{ margin: '0.5rem 0' }}>
                  <textarea
                    rows={3}
                    style={{ width: '100%', padding: '0.5rem' }}
                    placeholder="Write your review here..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    required
                  />
                </div>

                <button className="btn-enroll" style={{ width: 'auto' }} type="submit" disabled={reviewSubmitting}>
                  {reviewSubmitting ? 'Submitting...' : 'Submit Review'}
                </button>
              </form>
            )}

            {/* List Reviews */}
            {reviews.length === 0 ? (
              <p style={{ color: '#666', marginTop: '0.5rem' }}>No reviews yet. Be the first to review!</p>
            ) : (
              reviews.map((rev) => (
                <div key={rev.id} style={{ padding: '0.8rem 0', borderBottom: '1px solid #eee' }}>
                  <div style={{ fontWeight: 'bold' }}>{'⭐'.repeat(rev.rating)}</div>
                  <p>{rev.comment}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="sidebar-card">
          <div className="price-tag">${course.price}</div>

          {/* Prioritize Instructor View first */}
          {isOwner ? (
            <button className="btn-enroll" onClick={() => navigate('/instructor')}>
              Manage Course (Instructor)
            </button>
          ) : isEnrolled ? (
            <button className="btn-enroll" onClick={() => navigate(`/learning/${id}`)}>
              Go to Course
            </button>
          ) : (
            <button 
              className="btn-enroll" 
              onClick={handleEnrollOrBuy} 
              disabled={processing}
            >
              {processing ? 'Processing...' : course.price === 0 ? 'Enroll Now (Free)' : 'Buy Now'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;