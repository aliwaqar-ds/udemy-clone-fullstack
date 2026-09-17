import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCourse, getCategories, uploadImageFile } from '../api/courseApi';
import './CreateCourse.css';

const CreateCourse = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    description: '',
    price: '',
    category_id: '',
    thumbnail_url: '',
    is_published: false,
  });
  const [uploadingImage, setUploadingImage] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await getCategories();
        setCategories(data);
        if (data.length > 0) {
          setFormData((prev) => ({ ...prev, category_id: data[0].id }));
        }
      } catch (err) {
        setError('Failed to load categories');
      }
    };
    fetchCategories();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    if (name === 'title') {
      const generatedSlug = value
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9 -]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-');
      setFormData((prev) => ({ ...prev, slug: generatedSlug }));
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const imageFormData = new FormData();
    imageFormData.append('file', file);

    setUploadingImage(true);
    try {
      const data = await uploadImageFile(imageFormData);
      setFormData((prev) => ({ ...prev, thumbnail_url: data.url }));
    } catch (err) {
      setError(err.message || 'Image upload failed');
    } finally {
      setUploadingImage(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload = {
        ...formData,
        price: parseFloat(formData.price || 0),
        category_id: parseInt(formData.category_id, 10),
      };
      await createCourse(payload);
      navigate('/instructor');
    } catch (err) {
      setError(err.message || 'Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-course-container">
      <h2>Create a New Course</h2>
      {error && <div className="error-banner">{error}</div>}

      <form onSubmit={handleSubmit} className="create-course-form">
        <div className="form-group">
          <label>Course Title</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g. React & Vite Masterclass"
            required
          />
        </div>

        <div className="form-group">
          <label>URL Slug</label>
          <input
            type="text"
            name="slug"
            value={formData.slug}
            onChange={handleChange}
            placeholder="react-vite-masterclass"
            required
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            rows="4"
            value={formData.description}
            onChange={handleChange}
            placeholder="Detailed overview of what students will learn..."
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Price ($USD)</label>
            <input
              type="number"
              name="price"
              step="0.01"
              value={formData.price}
              onChange={handleChange}
              placeholder="29.99"
              required
            />
          </div>

          <div className="form-group">
            <label>Category</label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              required
            >
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Course Thumbnail Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            disabled={uploadingImage}
          />
          {uploadingImage && <small>Uploading image file...</small>}
          {formData.thumbnail_url && (
            <div style={{ marginTop: '0.5rem' }}>
              <img
                src={formData.thumbnail_url}
                alt="Thumbnail preview"
                style={{ width: '120px', height: '70px', objectFit: 'cover', borderRadius: '6px' }}
              />
            </div>
          )}
        </div>

        <div className="form-checkbox">
          <label>
            <input
              type="checkbox"
              name="is_published"
              checked={formData.is_published}
              onChange={handleChange}
            />
            Publish Course Immediately
          </label>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-cancel" onClick={() => navigate('/instructor')}>
            Cancel
          </button>
          <button type="submit" className="btn-submit" disabled={loading || uploadingImage}>
            {loading ? 'Creating...' : 'Create Course'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateCourse;