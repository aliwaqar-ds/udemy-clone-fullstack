import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  fetchCourseById,
  fetchCourses,
  fetchCourseCurriculum,
  fetchCourseProgress,
  toggleLessonCompletion,
  fetchCourseCertificate,
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

  // Certificate Modal State
  const [certificate, setCertificate] = useState(null);
  const [certError, setCertError] = useState('');
  const [showCertModal, setShowCertModal] = useState(false);

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
          fetchCourseProgress(cleanId).catch(() => null),
        ]);

        setCurriculum(sections || []);

        if (progressData) {
          setProgress(progressData);
          if (progressData.completed_lesson_ids) {
            const initialMap = {};
            progressData.completed_lesson_ids.forEach((id) => {
              initialMap[id] = true;
            });
            setCompletedLessons(initialMap);
          }
        }

        // Auto-select first lesson
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

  // Toggle lesson completion state
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

  // Claim Certificate
  const handleClaimCertificate = async () => {
    setCertError('');
    try {
      const certData = await fetchCourseCertificate(Number(courseId));
      setCertificate(certData);
      setShowCertModal(true);
    } catch (err) {
      setCertError(err.response?.data?.detail || 'Failed to claim certificate.');
    }
  };

  if (loading) return <div className="player-loading">Loading classroom...</div>;

  return (
    <div className="player-container">
      {/* MAIN VIEWPORT */}
      <div className="main-content">
        <div className="player-top-bar">
          <Link to="/my-learning" className="btn-back">
            ← Back to My Learning
          </Link>
          <h2>{course?.title || 'Classroom'}</h2>
        </div>

        <div className="video-viewport">
          {activeLesson?.video_url && activeLesson.video_url !== 'string' ? (
            <video
              src={activeLesson.video_url}
              controls
              className="video-frame"
              style={{ width: '100%', height: '100%' }}
            />
          ) : (
            <div className="video-placeholder">
              <p>📹 {activeLesson ? activeLesson.title : 'Select a lesson to begin'}</p>
            </div>
          )}
        </div>

        <div className="lesson-details">
          <h2>{activeLesson?.title || 'Course Overview'}</h2>
          <p>{activeLesson?.content || 'Select a lesson from the curriculum sidebar to watch.'}</p>
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

      {/* CURRICULUM SIDEBAR */}
      <aside className="sidebar-curriculum">
        <div className="sidebar-header">
          <h3>Course Curriculum</h3>
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

              {/* Claim Certificate Button */}
              {progress.progress_percentage === 100 && (
                <button
                  onClick={handleClaimCertificate}
                  style={{
                    marginTop: '0.8rem',
                    width: '100%',
                    padding: '0.6rem',
                    backgroundColor: '#22c55e',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                  }}
                >
                  🎓 Claim Certificate
                </button>
              )}
              {certError && (
                <p style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.4rem' }}>
                  {certError}
                </p>
              )}
            </div>
          )}
        </div>

        <div className="curriculum-list">
          {curriculum.length === 0 ? (
            <p style={{ padding: '1rem', color: '#94a3b8', fontSize: '0.9rem' }}>
              No sections or lessons uploaded yet.
            </p>
          ) : (
            curriculum.map((section) => (
              <div key={section.id} className="sidebar-section">
                <h4>{section.title}</h4>
                <ul>
                  {section.lessons && section.lessons.length > 0 ? (
                    section.lessons.map((lesson) => (
                      <li
                        key={lesson.id}
                        className={`sidebar-lesson-item ${
                          activeLesson?.id === lesson.id ? 'active' : ''
                        }`}
                        onClick={() => setActiveLesson(lesson)}
                      >
                        <span>📖 {lesson.title}</span>
                        <input
                          type="checkbox"
                          checked={!!completedLessons[lesson.id]}
                          onChange={() => handleToggleLesson(lesson.id)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </li>
                    ))
                  ) : (
                    <li style={{ fontSize: '0.8rem', color: '#64748b', padding: '0.3rem 0.5rem' }}>
                      No lessons in this section
                    </li>
                  )}
                </ul>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* CERTIFICATE MODAL */}
      {showCertModal && certificate && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.85)', display: 'flex',
          justifyContent: 'center', alignItems: 'center', zIndex: 2000
        }}>
          <div style={{
            backgroundColor: '#fff', color: '#1e293b', padding: '3rem',
            borderRadius: '12px', border: '8px double #a435f0',
            maxWidth: '650px', textAlign: 'center', position: 'relative'
          }}>
            <button
              onClick={() => setShowCertModal(false)}
              style={{ position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
            >
              ✕
            </button>
            <h1 style={{ color: '#a435f0', fontFamily: 'serif', marginBottom: '0.5rem' }}>
              Certificate of Completion
            </h1>
            <p style={{ fontSize: '0.9rem', color: '#64748b' }}>This is to certify that</p>
            <h2 style={{ fontSize: '2rem', margin: '0.8rem 0', color: '#0f172a' }}>
              {certificate.student_name}
            </h2>
            <p style={{ fontSize: '0.95rem', color: '#64748b' }}>
              has successfully completed the online course
            </p>
            <h3 style={{ fontSize: '1.4rem', color: '#1e293b', margin: '0.8rem 0' }}>
              {certificate.course_title}
            </h3>
            <div style={{
              marginTop: '2rem', display: 'flex', justifyContent: 'space-between',
              borderTop: '1px solid #cbd5e1', paddingTop: '1rem',
              fontSize: '0.85rem', color: '#64748b'
            }}>
              <div>
                <strong>Instructor:</strong> {certificate.instructor_name}
              </div>
              <div>
                <strong>Date:</strong> {certificate.issued_date}
              </div>
            </div>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '1rem' }}>
              ID: {certificate.certificate_id}
            </p>
            <button
              onClick={() => window.print()}
              style={{
                marginTop: '1.5rem', padding: '0.6rem 1.2rem',
                backgroundColor: '#a435f0', color: '#fff',
                border: 'none', borderRadius: '6px',
                fontWeight: 'bold', cursor: 'pointer'
              }}
            >
              🖨️ Print / Save as PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LearningPlayer;