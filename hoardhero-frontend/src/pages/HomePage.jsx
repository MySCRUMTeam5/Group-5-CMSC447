import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import { COLLECTION_TYPES } from '../config/collectionConfig'
import { getCollections, createCollection, deleteCollection } from '../api/hoardheroAPI'
import './HomePage.css'

// ── Single source of truth for type mapping ───────────────────────────────────
// Django → frontend (used when reading collections from the server)
const DJANGO_TO_FRONTEND_TYPE = {
  'video_games': 'games',
  'trading_cards': 'trading_cards',
  'comics': 'comics',
  'funko_pops': 'funko',
  'lego_sets': 'lego',
  'sports_cards': 'sports_cards',
  'music': 'music',
  'movies': 'movies',
  // Pass-throughs: if the frontend value somehow comes back directly, handle it
  'games': 'games',
  'funko': 'funko',
  'lego': 'lego',
}

// Frontend → Django (used when sending a new collection to the server)
const FRONTEND_TO_DJANGO_TYPE = {
  'games': 'video_games',
  'trading_cards': 'trading_cards',
  'comics': 'comics',
  'funko': 'funko_pops',
  'lego': 'lego_sets',
  'sports_cards': 'sports_cards',
  'music': 'music',
  'movies': 'movies',
}

export default function HomePage({ navigate }) {
  const [collections, setCollections] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [newCol, setNewCol] = useState({ name: '', type: 'games' })
  const [loaded, setLoaded] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [addError, setAddError] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(null)

  // ── Load collections on mount ─────────────────────────────────────────
  useEffect(() => {
    fetchCollections()
  }, [])

  const fetchCollections = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getCollections()
      const mapped = (Array.isArray(data) ? data : data.results || []).map(col => {
        // Backend sends "type" field containing the Django value (e.g. "video_games")
        const serverType = col.type || col.collection_type
        const frontendType = DJANGO_TO_FRONTEND_TYPE[serverType] ?? serverType
        const type = COLLECTION_TYPES.find(t => t.value === frontendType)
        return {
          id: col.id,
          name: col.name,
          type: frontendType,
          itemCount: col.itemCount || col.item_count || 0,
          totalValue: parseFloat(col.totalValue || col.total_value) || 0,
          icon: type?.icon || '📦',
        }
      })
      setCollections(mapped)
    } catch (err) {
      setError('Could not load collections. Is the Django server running?')
      console.error(err)
    } finally {
      setLoading(false)
      setLoaded(true)
    }
  }

  // ── Create a new collection ───────────────────────────────────────────
  const handleAddCollection = async () => {
    if (!newCol.name.trim()) return
    try {
      setAddError('')
      const djangoType = FRONTEND_TO_DJANGO_TYPE[newCol.type] ?? newCol.type
      const data = await createCollection({ name: newCol.name, type: djangoType })
      // Use the type the server echoed back so local state always matches DB
      const savedServerType = data.type || data.collection_type || djangoType
      const savedFrontendType = DJANGO_TO_FRONTEND_TYPE[savedServerType] ?? newCol.type
      const type = COLLECTION_TYPES.find(t => t.value === savedFrontendType)
      const created = {
        id: data.id,
        name: data.name,
        type: savedFrontendType,
        itemCount: 0,
        totalValue: 0,
        icon: type?.icon || '📦',
      }
      setCollections(prev => [...prev, created])
      setNewCol({ name: '', type: 'games' })
      setShowAddModal(false)
    } catch (err) {
      setAddError(err.message || 'Failed to create collection.')
      console.error(err)
    }
  }

  // ── Delete a collection ───────────────────────────────────────────────
  const handleDeleteCollection = async () => {
    if (!confirmDelete) return
    try {
      await deleteCollection(confirmDelete.id)
      setCollections(prev => prev.filter(c => c.id !== confirmDelete.id))
    } catch (err) {
      console.error('Delete failed:', err)
    } finally {
      setConfirmDelete(null)
    }
  }

  const totalItems = collections.reduce((s, c) => s + (c.itemCount || 0), 0)
  const totalValue = collections.reduce((s, c) => s + (c.totalValue || 0), 0)

  return (
    <div className="home-page">
      <Navbar navigate={navigate} />

      <main className="home-main">
        {/* Hero */}
        <section className="home-hero animate-in">
          <div className="hero-text">
            <h1 className="hero-title">Your Collections,<br />Organized.</h1>
            <p className="hero-subtitle">
              Track, manage, and discover the value of everything you collect — all in one place.
            </p>
          </div>
          <div className="hero-stats">
            <div className="stat-card">
              <span className="stat-value">{collections.length}</span>
              <span className="stat-label">Collections</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{totalItems.toLocaleString()}</span>
              <span className="stat-label">Total Items</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">${totalValue.toLocaleString('en-US', { minimumFractionDigits: 0 })}</span>
              <span className="stat-label">Est. Value</span>
            </div>
          </div>
        </section>

        {/* Collections Grid */}
        <section className="collections-section">
          <div className="section-header">
            <h2 className="section-title">My Collections</h2>
            <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 5v14M5 12h14" />
              </svg>
              New Collection
            </button>
          </div>

          {/* Error state */}
          {error && (
            <div className="api-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
              </svg>
              {error}
              <button className="btn btn-sm btn-secondary" onClick={fetchCollections}>Retry</button>
            </div>
          )}

          {/* Loading state */}
          {loading && !error && (
            <div className="loading-state">
              <div className="spinner" />
              <p>Loading collections...</p>
            </div>
          )}

          {/* Collections grid */}
          {!loading && !error && (
            <div className={`collections-grid ${loaded ? 'loaded' : ''}`}>
              {collections.map((col, i) => (
                <div
                  key={col.id}
                  className="collection-card"
                  style={{ animationDelay: `${i * 55}ms` }}
                  onClick={() => navigate('collection', col)}
                >
                  <div className="collection-card-top">
                    <div className="collection-icon">{col.icon}</div>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={(e) => { e.stopPropagation(); setConfirmDelete(col); }}
                      title="Delete Collection"
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6l-1 14H6L5 6" />
                        <path d="M10 11v6M14 11v6" />
                        <path d="M9 6V4h6v2" />
                      </svg>
                    </button>
                  </div>
                  <h3 className="collection-name">{col.name}</h3>
                  <div className="collection-meta">
                    <span className="meta-item">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18M9 21V9" />
                      </svg>
                      {col.itemCount} items
                    </span>
                    <span className="meta-item meta-value">
                      ${(col.totalValue || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="collection-footer">
                    <span className="btn btn-primary btn-sm view-btn">View Collection</span>
                  </div>
                </div>
              ))}

              {/* Add card */}
              <div className="collection-card collection-card-add" onClick={() => setShowAddModal(true)}>
                <div className="add-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                </div>
                <p className="add-label">Add a new collection</p>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Add Collection Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">New Collection</h2>
              <button className="modal-close" onClick={() => { setShowAddModal(false); setAddError('') }}>×</button>
            </div>

            {addError && <div className="form-error">{addError}</div>}

            <div className="form-group">
              <label className="form-label">Collection Name</label>
              <input
                type="text"
                placeholder='e.g. "My Vinyl Records"'
                value={newCol.name}
                onChange={e => setNewCol(p => ({ ...p, name: e.target.value }))}
                onKeyDown={e => e.key === 'Enter' && handleAddCollection()}
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="form-label">Collection Type</label>
              <div className="type-grid">
                {COLLECTION_TYPES.map(t => (
                  <div
                    key={t.value}
                    className={`type-option ${newCol.type === t.value ? 'selected' : ''}`}
                    onClick={() => setNewCol(p => ({ ...p, type: t.value }))}
                  >
                    <span className="type-icon">{t.icon}</span>
                    <span className="type-label">{t.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => { setShowAddModal(false); setAddError('') }}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAddCollection} disabled={!newCol.name.trim()}>
                Create Collection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Delete Modal */}
      {confirmDelete && (
        <div className="modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="modal modal-sm" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Delete Collection?</h2>
              <button className="modal-close" onClick={() => setConfirmDelete(null)}>×</button>
            </div>
            <p className="delete-confirm-text" style={{ fontSize: '14px', marginBottom: '16px', lineHeight: '1.5' }}>
              Are you sure you want to permanently delete <strong>"{confirmDelete.name}"</strong>?
              This will delete all items inside it. This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancel</button>
              <button className="btn btn-primary" style={{ background: 'var(--danger)', borderColor: 'var(--danger)' }} onClick={handleDeleteCollection}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}