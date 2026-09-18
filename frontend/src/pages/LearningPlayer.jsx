import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  fetchCourseById,
  fetchCourses,
  fetchCourseCurriculum,
  fetchCourseProgress,
  toggleLessonCompletion,
  saveLessonTimestamp,
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
  const videoRef = useRef(null);

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
        if (progressData) setProgress(progressData);

        // 🎯 Auto-select the very first lesson found in the curriculum
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

  // Save video timestamp every 5 seconds during playback
  const handleTimeUpdate = () => {
    if (videoRef.current && activeLesson) {
      const currentTime = videoRef.current.currentTime;
      if (Math.floor(currentTime) % 5 === 0 && currentTime > 0) {
        saveLessonTimestamp(activeLesson.id, currentTime).catch(() => {});
      }
    }
  };

  // 🎯 Auto-seek video to last saved timestamp when metadata is loaded
  const handleLoadedMetadata = () => {
    if (videoRef.current && activeLesson?.last_watched_second) {
      videoRef.current.currentTime = activeLesson.last_watched_second;
    }
  };

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
          <h2>{course?.title || 'Classroom'}</h2>
        </div>

        <div className="video-viewport">
          {activeLesson?.video_url && activeLesson.video_url !== 'string' ? (
            <video
              ref={videoRef}
              src={activeLesson.video_url}
              controls
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
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
          <h2>{activeLesson?.title || 'Lesson Overview'}</h2>
          <p>{activeLesson?.content || 'Select a lesson from the sidebar to start watching.'}</p>
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
    </div>
  );
};

export default LearningPlayer;