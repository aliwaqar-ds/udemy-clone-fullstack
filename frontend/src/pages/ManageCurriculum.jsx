import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  fetchCourseCurriculum, 
  createSection, 
  createLesson, 
  fetchCourseById, 
  togglePublishCourse,
  uploadVideoFile,
  deleteSection,
  deleteLesson
} from '../api/courseApi';
import './ManageCurriculum.css';

const ManageCurriculum = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [sections, setSections] = useState([]);
  const [newSectionTitle, setNewSectionTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadingVideo, setUploadingVideo] = useState(false);
  const [error, setError] = useState('');
  const [isPublished, setIsPublished] = useState(false);

  const [activeSectionId, setActiveSectionId] = useState(null);
  const [lessonFormData, setLessonFormData] = useState({
    title: '',
    video_url: '',
    duration_minutes: '',
  });

  useEffect(() => {
    loadCurriculum();
    loadCourseDetails();
  }, [courseId]);

  const loadCourseDetails = async () => {
    try {
      const course = await fetchCourseById(courseId);
      if (course) {
        setIsPublished(course.is_published);
      }
    } catch (err) {
      console.error('Failed to load course details:', err);
    }
  };

  const loadCurriculum = async () => {
    try {
      const data = await fetchCourseCurriculum(courseId);
      setSections(data);
    } catch (err) {
      setError('Failed to load course curriculum.');
    }
  };

  const handleTogglePublish = async () => {
    try {
      setError('');
      const updated = await togglePublishCourse(courseId);
      setIsPublished(updated.is_published);
    } catch (err) {
      setError(err.message || 'Failed to update course status.');
    }
  };

  const handleAddSection = async (e) => {
    e.preventDefault();
    if (!newSectionTitle.trim()) return;

    setLoading(true);
    setError('');

    try {
      const payload = {
        title: newSectionTitle,
        course_id: parseInt(courseId, 10),
        order: sections.length + 1,
      };

      await createSection(payload);
      setNewSectionTitle('');
      loadCurriculum();
    } catch (err) {
      setError(err.message || 'Failed to add section.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSection = async (sectionId) => {
  if (!window.confirm('Are you sure you want to delete this section and all its lessons?')) return;
  try {
    await deleteSection(courseId, sectionId);
    loadCurriculum();
  } catch (err) {
    setError(err.message || 'Failed to delete section');
  }
};
    
    

  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Are you sure you want to delete this lesson?')) return;
    try {
      await deleteLesson(lessonId);
      loadCurriculum();
    } catch (err) {
      setError(err.message || 'Failed to delete lesson');
    }
  };

  const handleLessonChange = (e) => {
    const { name, value } = e.target;
    setLessonFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleVideoFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const videoFormData = new FormData();
    videoFormData.append('file', file);

    setUploadingVideo(true);
    setError('');
    try {
      const data = await uploadVideoFile(videoFormData);
      setLessonFormData((prev) => ({ ...prev, video_url: data.url }));
    } catch (err) {
      setError(err.message || 'Video upload failed');
    } finally {
      setUploadingVideo(false);
    }
  };

  const handleAddLessonSubmit = async (e, sectionId) => {
    e.preventDefault();
    if (!lessonFormData.title.trim()) return;

    try {
      const currentSection = sections.find((s) => s.id === sectionId);
      const existingLessonsCount = currentSection?.lessons?.length || 0;

      const payload = {
        title: lessonFormData.title,
        video_url: lessonFormData.video_url || null,
        duration_minutes: parseInt(lessonFormData.duration_minutes || 0, 10),
        section_id: sectionId,
        order: existingLessonsCount + 1,
        is_free_preview: false,
      };

      await createLesson(payload);
      
      setLessonFormData({ title: '', video_url: '', duration_minutes: '' });
      setActiveSectionId(null);
      loadCurriculum();
    } catch (err) {
      setError(err.message || 'Failed to add lesson.');
    }
  };

  return (
    <div className="curriculum-container">
      <div className="curriculum-header">
        <button className="btn-back" onClick={() => navigate('/instructor')}>
          ← Back to Dashboard
        </button>
        <h2>Manage Course Curriculum (Course ID: {courseId})</h2>
        <button 
          className={isPublished ? "btn-unpublish" : "btn-publish"} 
          onClick={handleTogglePublish}
          style={{
            marginLeft: 'auto',
            padding: '0.6rem 1.2rem',
            cursor: 'pointer',
            backgroundColor: isPublished ? '#d9534f' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}
        >
          {isPublished ? 'Unpublish Course' : 'Publish Course'}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="add-section-box">
        <h3>Add New Section</h3>
        <form onSubmit={handleAddSection} className="section-form">
          <input
            type="text"
            placeholder="e.g. Section 1: Getting Started"
            value={newSectionTitle}
            onChange={(e) => setNewSectionTitle(e.target.value)}
            required
          />
          <button type="submit" className="btn-add" disabled={loading}>
            {loading ? 'Adding...' : 'Add Section'}
          </button>
        </form>
      </div>

      <div className="sections-list">
        {sections.length === 0 ? (
          <p className="no-sections">No sections added yet. Start by creating one above!</p>
        ) : (
          sections.map((section, idx) => (
            <div key={section.id || idx} className="section-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <h4 style={{ margin: 0 }}>
                  Section {idx + 1}: {section.title}
                </h4>
                <button 
                  onClick={() => handleDeleteSection(section.id)}
                  style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', fontSize: '0.85rem', fontWeight: '600' }}
                >
                  🗑️ Delete Section
                </button>
              </div>

              <div className="lessons-list">
                {section.lessons && section.lessons.length > 0 ? (
                  section.lessons.map((lesson, lIdx) => (
                    <div key={lesson.id || lIdx} className="lesson-item">
                      <span className="lesson-title">📖 {lesson.title}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {lesson.duration_minutes > 0 && (
                          <span className="lesson-duration">{lesson.duration_minutes} mins</span>
                        )}
                        <button
                          onClick={() => handleDeleteLesson(lesson.id)}
                          style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', fontSize: '0.8rem' }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="no-lessons">No video lessons in this section.</p>
                )}

                {activeSectionId === section.id ? (
                  <form onSubmit={(e) => handleAddLessonSubmit(e, section.id)} className="inline-lesson-form">
                    <h5>New Lesson Details</h5>
                    <input
                      type="text"
                      name="title"
                      placeholder="Lesson Title (e.g. Installing Dependencies)"
                      value={lessonFormData.title}
                      onChange={handleLessonChange}
                      required
                    />
                    
                    <div className="video-input-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      <label style={{ fontSize: '0.85rem', fontWeight: '600', color: '#475569' }}>
                        Lesson Video (Upload MP4/WebM file or paste URL)
                      </label>
                      <input
                        type="file"
                        accept="video/mp4,video/webm,video/mkv"
                        onChange={handleVideoFileUpload}
                        disabled={uploadingVideo}
                      />
                      {uploadingVideo && <small style={{ color: '#a855f7' }}>Uploading video file to server...</small>}
                      <input
                        type="text"
                        name="video_url"
                        placeholder="Or paste video URL (e.g. https://...)"
                        value={lessonFormData.video_url}
                        onChange={handleLessonChange}
                      />
                    </div>

                    <input
                      type="number"
                      name="duration_minutes"
                      placeholder="Duration (minutes)"
                      value={lessonFormData.duration_minutes}
                      onChange={handleLessonChange}
                    />
                    <div className="inline-form-actions">
                      <button type="submit" className="btn-save-lesson" disabled={uploadingVideo}>
                        Save Lesson
                      </button>
                      <button type="button" className="btn-cancel-inline" onClick={() => setActiveSectionId(null)}>
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <button className="btn-add-lesson" onClick={() => setActiveSectionId(section.id)}>
                    + Add Lesson
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ManageCurriculum;