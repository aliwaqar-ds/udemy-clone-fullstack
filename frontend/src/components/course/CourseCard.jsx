import { Link } from 'react-router-dom';
import './CourseCard.css';

const DEFAULT_THUMBNAIL = 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&auto=format&fit=crop&q=60';

const CourseCard = ({ course }) => {
  return (
    <div className="course-card">
      <img
        src={course.thumbnail_url || DEFAULT_THUMBNAIL}
        alt={course.title}
        className="course-thumbnail"
        onError={(e) => { e.target.src = DEFAULT_THUMBNAIL; }}
      />
      <div className="course-info">
        <h3 className="course-title">{course.title}</h3>
        <p className="course-description">
          {course.description || 'No description provided.'}
        </p>
        <div className="course-price">
          {course.price > 0 ? `$${course.price.toFixed(2)}` : 'Free'}
        </div>
        <Link to={`/courses/${course.id}`} className="btn-details">
          View Details
        </Link>
      </div>
    </div>
  );
};

export default CourseCard;