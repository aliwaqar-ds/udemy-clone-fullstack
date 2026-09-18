import API from './axios';

// --- Public & Student Course Endpoints ---

export const fetchCourses = async (search = '', categoryId = '') => {
  const params = {};
  if (search) params.search = search;
  if (categoryId) params.category_id = categoryId;

  const response = await API.get('/courses', { params });
  return response.data;
};

export const fetchCourseById = async (courseId) => {
  const response = await API.get(`/courses/${courseId}`);
  return response.data;
};

export const fetchCourseCurriculum = async (courseId) => {
  const response = await API.get(`/courses/${courseId}/curriculum`);
  return response.data;
};

export const enrollInCourse = async (courseId) => {
  const response = await API.post('/enrollments', { course_id: Number(courseId) });
  return response.data;
};

// Fetch user's enrolled courses (alias exported to satisfy CourseDetail.jsx imports)
export const fetchMyEnrollments = async () => {
  const response = await API.get('/enrollments/me');
  return response.data;
};
export const fetchMyEnrolledCourses = fetchMyEnrollments;

export const toggleLessonCompletion = async (lessonId) => {
  const response = await API.post(`/lessons/${lessonId}/toggle-complete`);
  return response.data;
};

export const fetchCourseProgress = async (courseId) => {
  const response = await API.get(`/courses/${courseId}/progress`);
  return response.data;
};

// --- Instructor Management Endpoints ---

export const fetchInstructorCourses = async () => {
  const response = await API.get('/instructor/courses');
  return response.data;
};

export const createCourse = async (courseData) => {
  const response = await API.post('/courses', courseData);
  return response.data;
};

export const togglePublishCourse = async (courseId) => {
  const response = await API.patch(`/courses/${courseId}/publish`);
  return response.data;
};

export const createSection = async (sectionData) => {
  const response = await API.post('/sections', sectionData);
  return response.data;
};

export const deleteSection = async (sectionId) => {
  const response = await API.delete(`/sections/${sectionId}`);
  return response.data;
};

export const createLesson = async (lessonData) => {
  const response = await API.post('/lessons', lessonData);
  return response.data;
};

export const deleteLesson = async (lessonId) => {
  const response = await API.delete(`/lessons/${lessonId}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await API.get('/categories');
  return response.data;
};

// --- File Upload Endpoints ---

export const uploadImageFile = async (formData) => {
  const response = await API.post('/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const uploadVideoFile = async (formData) => {
  const response = await API.post('/upload/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// --- Stripe Payment Endpoints ---

export const createCheckoutSession = async (courseId) => {
  const response = await API.post(`/payments/create-checkout-session/${courseId}`);
  return response.data;
};

// --- Course Review Endpoints ---

export const createReview = async (reviewData) => {
  const response = await API.post('/reviews', reviewData);
  return response.data;
};

export const fetchCourseReviews = async (courseId) => {
  const response = await API.get(`/courses/${courseId}/reviews`);
  return response.data;
};