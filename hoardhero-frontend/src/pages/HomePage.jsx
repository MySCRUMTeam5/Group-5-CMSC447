import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import { COLLECTION_TYPES } from '../config/collectionConfig'
import './HomePage.css'

// TODO: Replace with GET /api/collections/
const MOCK_COLLECTIONS = []

export default function HomePage({ navigate }) {
  const [collections, setCollections] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [newCol, setNewCol]             = useState({ name: '', type: 'games' })
  const [loaded, setLoaded]             = useState(false)

  useEffect(() => {
    // TODO: fetch('/api/collections/').then(r => r.json()).then(setCollections)
    setTimeout(() => setLoaded(true), 80)
  }, [])

  const totalItems = collections.reduce((s, c) => s + (c.itemCount || 0), 0)
  const totalValue = collections.reduce((s, c) => s + (c.totalValue || 0), 0)

  const handleAddCollection = () => {
    if (!newCol.name.trim()) return
    const type = COLLECTION_TYPES.find(t => t.value === newCol.type)
    const created = {
      id: Date.now(),
      name: newCol.name,
      type: newCol.type,
      itemCount: 0,
      totalValue: 0,
      icon: type?.icon || '📦',
    }
    // TODO: POST /api/collections/  { name, type }
    setCollections(prev => [...prev, created])
    setNewCol({ name: '', type: 'games' })
    setShowAddModal(false)
  }

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
                <path d="M12 5v14M5 12h14"/>
              </svg>
              New Collection
            </button>
          </div>

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
                  <div className="collection-arrow">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </div>
                </div>
                <h3 className="collection-name">{col.name}</h3>
                <div className="collection-meta">
                  <span className="meta-item">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
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
                  <path d="M12 5v14M5 12h14"/>
                </svg>
              </div>
              <p className="add-label">Add a new collection</p>
            </div>
          </div>
        </section>
      </main>

      {/* Add Collection Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">New Collection</h2>
              <button className="modal-close" onClick={() => setShowAddModal(false)}>×</button>
            </div>

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
              <button className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAddCollection} disabled={!newCol.name.trim()}>
                Create Collection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
