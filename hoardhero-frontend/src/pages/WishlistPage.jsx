import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import { useUser } from '@clerk/clerk-react'
import { COLLECTION_TYPES } from '../config/collectionConfig'
import {
  getWishlist, addWishlistItem, deleteWishlistItem,
  getCollections, addItem,
} from '../api/hoardheroAPI'
import './WishlistPage.css'

const DJANGO_TO_FRONTEND_TYPE = {
  video_games:   'games',
  trading_cards: 'trading_cards',
  comics:        'comics',
  funko_pops:    'funko',
  lego_sets:     'lego',
  sports_cards:  'sports_cards',
  music:         'music',
  movies:        'movies',
}

const FRONTEND_TO_DJANGO_TYPE = {
  games:         'video_games',
  trading_cards: 'trading_cards',
  comics:        'comics',
  funko:         'funko_pops',
  lego:          'lego_sets',
  sports_cards:  'sports_cards',
  music:         'music',
  movies:        'movies',
}

function typeIcon(djangoType) {
  const frontendType = DJANGO_TO_FRONTEND_TYPE[djangoType] ?? djangoType
  return COLLECTION_TYPES.find(t => t.value === frontendType)?.icon ?? '📦'
}

function typeLabel(djangoType) {
  const frontendType = DJANGO_TO_FRONTEND_TYPE[djangoType] ?? djangoType
  return COLLECTION_TYPES.find(t => t.value === frontendType)?.label ?? djangoType
}

export default function WishlistPage({ navigate }) {
  const { user, isLoaded } = useUser()
  const [items,            setItems]            = useState([])
  const [collections,      setCollections]      = useState([])
  const [loading,          setLoading]          = useState(true)
  const [pageError,        setPageError]        = useState('')
  const [showAddModal,     setShowAddModal]     = useState(false)
  const [newItem,          setNewItem]          = useState({ name: '', collectionType: 'games', notes: '', priceTarget: '', link: '' })
  const [formError,        setFormError]        = useState('')
  const [confirmDelete,    setConfirmDelete]    = useState(null)
  const [boughtModal,      setBoughtModal]      = useState(null)
  const [boughtCollection, setBoughtCollection] = useState('')
  const [boughtLoading,    setBoughtLoading]    = useState(false)
  const [boughtError,      setBoughtError]      = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setPageError('')
      const [wishlistData, collectionsData] = await Promise.all([
        getWishlist(),
        getCollections(),
      ])
      setItems(Array.isArray(wishlistData) ? wishlistData : [])

      // Map collections for the "mark as bought" picker
      const mapped = (Array.isArray(collectionsData) ? collectionsData : []).map(col => {
        const serverType = col.type || col.collection_type
        const frontendType = DJANGO_TO_FRONTEND_TYPE[serverType] ?? serverType
        const typeObj = COLLECTION_TYPES.find(t => t.value === frontendType)
        return {
          id: col.id,
          name: col.name,
          icon: typeObj?.icon ?? '📦',
        }
      })
      setCollections(mapped)
    } catch (err) {
      setPageError('Could not load wishlist. Is the Django server running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // ── Add wishlist item ─────────────────────────────────────────────────────
  const handleAdd = async () => {
    console.log("HANDLE ADD CALLED")
    if (!isLoaded) {
      console.log("Clerk still loading")
      console.log("isLoaded", isLoaded)
      return
    }

    if (!user) {
      console.log("No user available")
      console.log("User", user)
      return
    }
    console.log("FLAG")
    if (!newItem.name.trim()) { setFormError('Name is required.'); return }
    try {
      setFormError('')
      const djangoType = FRONTEND_TO_DJANGO_TYPE[newItem.collectionType] || 'video_games'
      const data = await addWishlistItem({
        name: newItem.name,
        collectionType: djangoType,
        notes: newItem.notes,
        priceTarget: newItem.priceTarget,
        link: newItem.link,
        clerk_user_id: user.id
      })
      console.log("HANDLE ADD PAYLOAD", {
        name: newItem.name,
        clerk_user_id: user.id
      })
      setItems(prev => [data, ...prev])
      setNewItem({ name: '', collectionType: 'games', notes: '', priceTarget: '', link: '' })
      setShowAddModal(false)
    } catch (err) {
      setFormError(err.message || 'Failed to add item.')
    }
  }

  // ── Remove wishlist item ──────────────────────────────────────────────────
  const handleDelete = async (id) => {
    try {
      await deleteWishlistItem(id)
      setItems(prev => prev.filter(i => i.id !== id))
    } catch (err) {
      console.error('Delete failed:', err)
    } finally {
      setConfirmDelete(null)
    }
  }

  // ── Mark as bought ────────────────────────────────────────────────────────
  const openBoughtModal = (item) => {
    setBoughtModal(item)
    setBoughtCollection(collections[0]?.id?.toString() ?? '')
    setBoughtError('')
  }

  const handleMarkBought = async () => {
    if (!boughtCollection) { setBoughtError('Please select a collection.'); return }
    if (!isLoaded || !user) return
    setBoughtLoading(true)
    setBoughtError('')
    try {
      await addItem(parseInt(boughtCollection), { title: boughtModal.name, description: boughtModal.description })
      await deleteWishlistItem(boughtModal.id)
      setItems(prev => prev.filter(i => i.id !== boughtModal.id))
      setBoughtModal(null)
    } catch (err) {
      setBoughtError(err.message || 'Failed to move item to collection.')
    } finally {
      setBoughtLoading(false)
    }
  }

  return (
    <div className="wishlist-page">
      <Navbar navigate={navigate} showBack backLabel="Home" />

      <main className="wishlist-main">

        {/* Header */}
        <div className="wishlist-header animate-in">
          <div className="wishlist-header-left">
            <span className="wishlist-icon">⭐</span>
            <div>
              <h1 className="wishlist-title">Wishlist</h1>
              <p className="wishlist-subtitle">{items.length} {items.length === 1 ? 'item' : 'items'} you want to collect</p>
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => { setShowAddModal(true); setFormError('') }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Add to Wishlist
          </button>
        </div>

        {/* Error / loading */}
        {pageError && (
          <div className="wishlist-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
            </svg>
            {pageError}
            <button className="btn btn-sm btn-secondary" onClick={fetchData}>Retry</button>
          </div>
        )}

        {loading && !pageError && (
          <div className="wishlist-loading">
            <div className="spinner" />
            <p>Loading wishlist...</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && !pageError && items.length === 0 && (
          <div className="wishlist-empty animate-in">
            <div className="wishlist-empty-icon">⭐</div>
            <h3>Your wishlist is empty</h3>
            <p>Add items you want to collect and track them here.</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setShowAddModal(true)}>
              + Add first item
            </button>
          </div>
        )}

        {/* Wishlist grid */}
        {!loading && !pageError && items.length > 0 && (
          <div className="wishlist-grid animate-in">
            {items.map((item, i) => (
              <div key={item.id} className="wishlist-card" style={{ animationDelay: `${i * 40}ms` }}>
                <div className="wishlist-card-icon">{typeIcon(item.collection_type)}</div>
                <div className="wishlist-card-body">
                  <div className="wishlist-card-header">
                    <h3 className="wishlist-card-name">{item.name}</h3>
                    <span className="wishlist-card-type">{typeLabel(item.collection_type)}</span>
                  </div>
                  {item.notes && (
                    <p className="wishlist-card-notes">{item.notes}</p>
                  )}
                  <div className="wishlist-card-meta">
                    {parseFloat(item.price_target) > 0 && (
                      <span className="wishlist-price-target">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                        </svg>
                        Target: ${parseFloat(item.price_target).toFixed(2)}
                      </span>
                    )}
                    {item.link && (
                      <a
                        href={item.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="wishlist-link"
                        onClick={e => e.stopPropagation()}
                      >
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3"/>
                        </svg>
                        View link
                      </a>
                    )}
                  </div>
                </div>
                <div className="wishlist-card-actions">
                  <button
                    className="btn btn-success btn-sm"
                    onClick={() => openBoughtModal(item)}
                    title="Mark as bought — move to a collection"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Got it!
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => setConfirmDelete(item)}
                    title="Remove from wishlist"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6l-1 14H6L5 6M10 11v6M14 11v6M9 6V4h6v2"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* ── Add Item Modal ── */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => { setShowAddModal(false); setFormError('') }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add to Wishlist</h2>
              <button className="modal-close" onClick={() => { setShowAddModal(false); setFormError('') }}>×</button>
            </div>
            {formError && <div className="form-error">{formError}</div>}
            <div className="form-grid">
              <div className="form-group form-span-2">
                <label className="form-label">Name *</label>
                <input
                  type="text"
                  placeholder="e.g. The Legend of Zelda"
                  value={newItem.name}
                  onChange={e => setNewItem(p => ({ ...p, name: e.target.value }))}
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select
                  value={newItem.collectionType}
                  onChange={e => setNewItem(p => ({ ...p, collectionType: e.target.value }))}
                >
                  {COLLECTION_TYPES.map(t => (
                    <option key={t.value} value={t.value}>{t.icon} {t.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Price Target ($)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  value={newItem.priceTarget}
                  onChange={e => setNewItem(p => ({ ...p, priceTarget: e.target.value }))}
                />
              </div>
              <div className="form-group form-span-2">
                <label className="form-label">Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Need CIB, prefer Switch version"
                  value={newItem.notes}
                  onChange={e => setNewItem(p => ({ ...p, notes: e.target.value }))}
                />
              </div>
              <div className="form-group form-span-2">
                <label className="form-label">Link (optional)</label>
                <input
                  type="url"
                  placeholder="https://..."
                  value={newItem.link}
                  onChange={e => setNewItem(p => ({ ...p, link: e.target.value }))}
                />
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => { setShowAddModal(false); setFormError('') }}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAdd}>Add to Wishlist</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Confirm Remove Modal ── */}
      {confirmDelete && (
        <div className="modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="modal modal-sm" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Remove Item?</h2>
              <button className="modal-close" onClick={() => setConfirmDelete(null)}>×</button>
            </div>
            <p className="delete-confirm-text">
              Remove <strong>"{confirmDelete.name}"</strong> from your wishlist?
            </p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancel</button>
              <button className="btn btn-primary btn-delete-confirm" onClick={() => handleDelete(confirmDelete.id)}>Remove</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Mark as Bought Modal ── */}
      {boughtModal && (
        <div className="modal-overlay" onClick={() => { setBoughtModal(null); setBoughtError('') }}>
          <div className="modal modal-sm" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Move to Collection</h2>
              <button className="modal-close" onClick={() => { setBoughtModal(null); setBoughtError('') }}>×</button>
            </div>
            <p className="delete-confirm-text">
              You got <strong>"{boughtModal.name}"</strong>! Which collection should it go into?
            </p>
            {boughtError && <div className="form-error">{boughtError}</div>}
            {collections.length === 0 ? (
              <p className="wishlist-no-collections">
                You don't have any collections yet. Create one from the home page first.
              </p>
            ) : (
              <div className="form-group" style={{ marginBottom: 8 }}>
                <label className="form-label">Collection</label>
                <select
                  value={boughtCollection}
                  onChange={e => setBoughtCollection(e.target.value)}
                >
                  {collections.map(c => (
                    <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => { setBoughtModal(null); setBoughtError('') }}>Cancel</button>
              {collections.length > 0 && (
                <button
                  className="btn btn-success"
                  onClick={handleMarkBought}
                  disabled={boughtLoading}
                >
                  {boughtLoading ? 'Moving...' : 'Add to Collection'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
