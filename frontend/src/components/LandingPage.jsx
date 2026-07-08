import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, Link as LinkIcon, Loader2, CheckCircle, AlertCircle, Database } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/pipeline';

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState('upload');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [clearExisting, setClearExisting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState({ is_running: false, last_error: null, last_url: null });
  const fileInputRef = useRef(null);

  // Poll backend status
  useEffect(() => {
    let interval;
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${API_BASE}/status`);
        setStatus(res.data);
        if (res.data.is_running) {
          setIsSubmitting(true);
        } else {
          setIsSubmitting(false);
        }
      } catch (err) {
        console.error("Status fetch error", err);
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;
    setIsSubmitting(true);
    try {
      await axios.post(`${API_BASE}/ingest-url`, {
        url,
        clear_existing: clearExisting
      });
      setUrl('');
    } catch (err) {
      alert("Failed to submit URL: " + (err.response?.data?.detail || err.message));
      setIsSubmitting(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setIsSubmitting(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('clear_existing', clearExisting);

    try {
      await axios.post(`${API_BASE}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      alert("Failed to upload file: " + (err.response?.data?.detail || err.message));
      setIsSubmitting(false);
    }
  };

  const StatusIndicator = () => {
    if (status.is_running) {
      return (
        <div className="status-badge">
          <div className="status-dot active"></div>
          Processing: {status.last_url || "Document"}...
        </div>
      );
    }
    if (status.last_error) {
      return (
        <div className="status-badge" style={{ borderColor: 'var(--error)' }}>
          <div className="status-dot error"></div>
          Error: {status.last_error}
        </div>
      );
    }
    return (
      <div className="status-badge">
        <div className="status-dot idle"></div>
        System Ready
      </div>
    );
  };

  return (
    <div className="app-container">
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
          <Database size={64} color="var(--primary)" />
        </div>
        <h1 className="title">CLARIQ Data Engine</h1>
        <p className="subtitle">
          Upload NCERT Science textbooks or PDF URLs to securely index them into the local Vector Database. 
          The Socratic Tutor will instantly use this new knowledge.
        </p>
        <div style={{ marginTop: '2rem' }}>
          <StatusIndicator />
        </div>
      </header>

      <main style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div className="glass-card">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <UploadCloud size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              Upload PDF
            </button>
            <button 
              className={`tab ${activeTab === 'link' ? 'active' : ''}`}
              onClick={() => setActiveTab('link')}
            >
              <LinkIcon size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              Submit URL
            </button>
          </div>

          <div className="input-group" style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={clearExisting} 
                onChange={(e) => setClearExisting(e.target.checked)} 
                style={{ width: '1.25rem', height: '1.25rem', accentColor: 'var(--primary)' }}
              />
              <span className="input-label" style={{ color: clearExisting ? 'var(--error)' : 'var(--text-main)' }}>
                Clear Database (Deletes all existing curriculum data before indexing this PDF)
              </span>
            </label>
          </div>

          {activeTab === 'upload' && (
            <form onSubmit={handleFileUpload}>
              <div 
                className="upload-zone" 
                onClick={() => fileInputRef.current?.click()}
              >
                <UploadCloud size={48} color="var(--primary)" style={{ marginBottom: '1rem' }} />
                <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                  {file ? file.name : "Click to select or drag PDF here"}
                </h3>
                <p style={{ color: 'var(--text-muted)' }}>
                  {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Only .pdf files are supported"}
                </p>
                <input 
                  type="file" 
                  accept="application/pdf"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={(e) => setFile(e.target.files[0])}
                />
              </div>
              <div style={{ marginTop: '2rem', textAlign: 'right' }}>
                <button type="submit" className="btn btn-primary" disabled={!file || isSubmitting}>
                  {isSubmitting ? <Loader2 className="animate-spin" /> : <CheckCircle />}
                  {isSubmitting ? 'Processing...' : 'Upload & Index'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'link' && (
            <form onSubmit={handleUrlSubmit}>
              <div className="input-group">
                <label className="input-label">PDF URL</label>
                <input 
                  type="url" 
                  className="text-input" 
                  placeholder="https://example.com/textbook.pdf" 
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                />
              </div>
              <div style={{ marginTop: '2rem', textAlign: 'right' }}>
                <button type="submit" className="btn btn-primary" disabled={!url || isSubmitting}>
                  {isSubmitting ? <Loader2 className="animate-spin" /> : <LinkIcon />}
                  {isSubmitting ? 'Downloading...' : 'Fetch & Index'}
                </button>
              </div>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
