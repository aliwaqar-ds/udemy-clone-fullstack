import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  fetchCourseById,
  fetchCourses,
  fetchCourseCurriculum,
  fetchCourseProgress,
  toggleLessonCompletion,
} from '../api/courseApi';
import './LearningPlayer.css';

const LearningPlayer = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [curriculum, setCurriculum] = useState([]);
  const [activeLesson, setActiveLesson] = useState(null);
  const [completedLessons, setCompletedLessons] = useState({});
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cleanId = Number(courseId);
    if (!courseId || isNaN(cleanId)) {
      setLoading(false);
      return;
    }

    const loadPlayer = async () => {
      try {
        const [sections, progressData] = await Promise.all([
          fetchCourseCurriculum(cleanId),
          fetchCourseProgress(cleanId),
        ]);

        setCurriculum(sections);
        setProgress(progressData);

        if (sections && sections.length > 0) {
          for (const sec of sections) {
            if (sec.lessons && sec.lessons.length > 0) {
              setActiveLesson(sec.lessons[0]);
              break;
            }
          }
        }

        try {
          const courseData = await fetchCourseById(cleanId);
          setCourse(courseData);
        } catch {
          const allCourses = await fetchCourses();
          const found = allCourses.find((c) => c.id === cleanId);
          setCourse(found || null);
        }
      } catch (err) {
        console.error('Failed to load classroom data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPlayer();
  }, [courseId]);

  const handleToggleLesson = async (lessonId) => {
    try {
      const result = await toggleLessonCompletion(lessonId);
      setCompletedLessons((prev) => ({
        ...prev,
        [lessonId]: result.is_completed,
      }));

      const updatedProgress = await fetchCourseProgress(Number(courseId));
      setProgress(updatedProgress);
    } catch (err) {
      console.error('Failed to update lesson status:', err);
    }
  };

  if (loading) return <div className="player-loading">Loading classroom...</div>;

  return (
    <div className="player-container">
      {/* LEFT CONTENT AREA */}
      <div className="main-content">
        <div className="player-top-bar">
          <Link to="/my-learning" className="btn-back">
            ← Back to My Learning
          </Link>
          <h2>{course?.title || 'FastAPI Masterclass'}</h2>
        </div>

        <div className="video-viewport">
            {activeLesson?.video_url && activeLesson.video_url !== "string" ? (
                <iframe
                    src={activeLesson.video_url}
                    title={activeLesson.title || 'Lesson Video'}
                    className="video-frame"
                    allowFullScreen
                />
            ) : (
            <div className="video-placeholder">
                <p>📹 {activeLesson ? activeLesson.title : 'Select a lesson to begin'}</p>
            </div>
            )}
        </div>

        <div className="lesson-details">
          <h2>{activeLesson?.title || 'Environment Setup'}</h2>
          <p>{activeLesson?.content || 'Welcome to the course! Select a lesson to begin.'}</p>
          {activeLesson && (
            <button
              className={`btn-toggle-complete ${
                completedLessons[activeLesson.id] ? 'completed' : ''
              }`}
              onClick={() => handleToggleLesson(activeLesson.id)}
            >
              {completedLessons[activeLesson.id] ? '✓ Completed' : 'Mark as Complete'}
            </button>
          )}
        </div>
      </div>

      {/* RIGHT SIDEBAR */}
      <aside className="sidebar-curriculum">
        <div className="sidebar-header">
          <h3>{course?.title || 'FastAPI Masterclass'}</h3>
          {progress && (
            <div className="progress-bar-container">
              <div className="progress-text">
                {progress.completed_lessons} / {progress.total_lessons} completed (
                {progress.progress_percentage}%)
              </div>
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{ width: `${progress.progress_percentage}%` }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="curriculum-list">
          {curriculum.map((section) => (
            <div key={section.id} className="sidebar-section">
              <h4>{section.title}</h4>
              <ul>
                {section.lessons?.map((lesson) => (
                  <li
                    key={lesson.id}
                    className={`sidebar-lesson-item ${
                      activeLesson?.id === lesson.id ? 'active' : ''
                    }`}
                    onClick={() => setActiveLesson(lesson)}
                  >
                    <span>{lesson.title}</span>
                    <input
                      type="checkbox"
                      checked={!!completedLessons[lesson.id]}
                      onChange={() => handleToggleLesson(lesson.id)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
};

export default LearningPlayer;