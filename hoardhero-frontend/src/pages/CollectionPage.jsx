import { useState, useEffect, useMemo } from 'react'
import Navbar from '../components/Navbar'
import './CollectionPage.css'

const MOCK_ITEMS = []

const STATUS_OPTIONS  = ['All', 'Played', 'Playing', 'Unplayed']
const SORT_OPTIONS    = [
  { value: 'dateAdded-desc', label: 'Newest First'     },
  { value: 'dateAdded-asc',  label: 'Oldest First'     },
  { value: 'title-asc',      label: 'Name A→Z'         },
  { value: 'title-desc',     label: 'Name Z→A'         },
  { value: 'purchasePrice-desc', label: 'Price High→Low' },
  { value: 'purchasePrice-asc',  label: 'Price Low→High' },
  { value: 'currentValue-desc',  label: 'Value High→Low' },
]
const CONDITION_OPTIONS = ['Mint', 'Excellent', 'Good', 'Fair', 'Poor']
const PLATFORM_OPTIONS  = ['Nintendo Switch', 'PS5', 'PS4', 'Xbox Series X', 'Xbox One', 'PC', 'Other']

const STATUS_BADGE = {
  Played:   'badge-green',
  Playing:  'badge-blue',
  Unplayed: 'badge-gray',
}

const emptyItem = {
  title: '', platform: '', condition: 'Mint',
  status: 'Unplayed', purchasePrice: '', currentValue: '',
}

export default function CollectionPage({ navigate, collection }) {
  const [items, setItems] = useState([])
  const [search, setSearch]             = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [sortBy, setSortBy]             = useState('dateAdded-desc')
  const [showAddModal, setShowAddModal] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [newItem, setNewItem]           = useState(emptyItem)
  const [formError, setFormError]       = useState('')

  useEffect(() => {
  }, [collection?.id])

  // --- Derived: filtered + sorted items ---
  const displayItems = useMemo(() => {
    let list = [...items]

    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter(i =>
        i.title.toLowerCase().includes(q) ||
        i.platform?.toLowerCase().includes(q)
      )
    }
    if (statusFilter !== 'All') {
      list = list.filter(i => i.status === statusFilter)
    }

    const [field, dir] = sortBy.split('-')
    list.sort((a, b) => {
      const av = a[field], bv = b[field]
      if (typeof av === 'string') return dir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
      return dir === 'asc' ? av - bv : bv - av
    })
    return list
  }, [items, search, statusFilter, sortBy])

  const totalValue    = items.reduce((s, i) => s + (i.currentValue || 0), 0)
  const totalSpent    = items.reduce((s, i) => s + (i.purchasePrice || 0), 0)

  // --- Add Item ---
  const handleAddItem = () => {
    if (!newItem.title.trim()) { setFormError('Title is required.'); return }
    const item = {
      ...newItem,
      id: Date.now(),
      purchasePrice: parseFloat(newItem.purchasePrice) || 0,
      currentValue:  parseFloat(newItem.currentValue)  || 0,
      dateAdded: new Date().toISOString().slice(0, 10),
    }
    // TODO: POST
    setItems(prev => [item, ...prev])
    setNewItem(emptyItem)
    setFormError('')
    setShowAddModal(false)
  }

  // --- Delete Item ---
  const handleDelete = (id) => {
    // TODO: DELETE
    setItems(prev => prev.filter(i => i.id !== id))
    setConfirmDelete(null)
  }

  const col = collection || { name: 'Collection', icon: '📦' }

  return (
    <div className="collection-page">
      <Navbar navigate={navigate} showBack backLabel="Home" />

      <main className="collection-main">
        {/* Page Header */}
        <div className="page-header animate-in">
          <div className="page-header-left">
            <span className="page-icon">{col.icon}</span>
            <div>
              <h1 className="page-title">{col.name}</h1>
              <p className="page-subtitle">{items.length} items · Est. value ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
            </div>
          </div>
          <div className="page-header-actions">
            <div className="value-chip">
              <span className="value-chip-label">Spent</span>
              <span className="value-chip-val spent">${totalSpent.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="value-chip">
              <span className="value-chip-label">Value</span>
              <span className={`value-chip-val ${totalValue >= totalSpent ? 'gain' : 'loss'}`}>
                ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>
              Add Item
            </button>
          </div>
        </div>

        {/* Filter / Sort Bar */}
        <div className="filter-bar animate-in" style={{ animationDelay: '80ms' }}>
          <div className="search-wrap">
            <svg className="search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              className="search-input"
              type="text"
              placeholder="Search items..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            {search && (
              <button className="search-clear" onClick={() => setSearch('')}>×</button>
            )}
          </div>

          <div className="filter-group">
            <span className="filter-label">Status</span>
            {STATUS_OPTIONS.map(s => (
              <button
                key={s}
                className={`filter-chip ${statusFilter === s ? 'active' : ''}`}
                onClick={() => setStatusFilter(s)}
              >
                {s}
              </button>
            ))}
          </div>

          <div className="sort-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M7 12h10M11 18h2"/>
            </svg>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="sort-select">
              {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </div>

        {/* Results count */}
        {(search || statusFilter !== 'All') && (
          <p className="results-count">
            Showing {displayItems.length} of {items.length} items
            {search && <> matching "<strong>{search}</strong>"</>}
          </p>
        )}

        {/* Items Table */}
        {displayItems.length === 0 ? (
          <div className="empty-state animate-in">
            <div className="empty-icon">🔍</div>
            <h3>No items found</h3>
            <p>Try adjusting your search or filters.</p>
          </div>
        ) : (
          <div className="items-table-wrap animate-in" style={{ animationDelay: '120ms' }}>
            <table className="items-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Platform</th>
                  <th>Condition</th>
                  <th>Status</th>
                  <th>Paid</th>
                  <th>Value</th>
                  <th>Added</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {displayItems.map((item, i) => {
                  const profit = item.currentValue - item.purchasePrice
                  return (
                    <tr key={item.id} style={{ animationDelay: `${i * 30}ms` }} className="item-row">
                      <td className="item-title-cell">
                        <span className="item-title">{item.title}</span>
                      </td>
                      <td>
                        <span className="badge badge-gray">{item.platform}</span>
                      </td>
                      <td>
                        <span className="condition-dot" data-cond={item.condition}></span>
                        {item.condition}
                      </td>
                      <td>
                        <span className={`badge ${STATUS_BADGE[item.status] || 'badge-gray'}`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="price-cell">${item.purchasePrice.toFixed(2)}</td>
                      <td className="price-cell">
                        <span className={profit >= 0 ? 'profit-pos' : 'profit-neg'}>
                          ${item.currentValue.toFixed(2)}
                        </span>
                        <span className={`profit-delta ${profit >= 0 ? 'pos' : 'neg'}`}>
                          {profit >= 0 ? '+' : ''}{profit.toFixed(2)}
                        </span>
                      </td>
                      <td className="date-cell">{item.dateAdded}</td>
                      <td>
                        <button
                          className="btn btn-danger btn-sm delete-btn"
                          onClick={() => setConfirmDelete(item)}
                          title="Delete item"
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6l-1 14H6L5 6"/>
                            <path d="M10 11v6M14 11v6"/>
                            <path d="M9 6V4h6v2"/>
                          </svg>
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* ── Add Item Modal ── */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal modal-wide" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add Item to {col.name}</h2>
              <button className="modal-close" onClick={() => setShowAddModal(false)}>×</button>
            </div>

            {formError && <div className="form-error">{formError}</div>}

            <div className="form-grid">
              <div className="form-group form-span-2">
                <label className="form-label">Title *</label>
                <input
                  type="text"
                  placeholder="e.g. The Legend of Zelda: Breath of the Wild"
                  value={newItem.title}
                  onChange={e => setNewItem(p => ({ ...p, title: e.target.value }))}
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label className="form-label">Platform</label>
                <select value={newItem.platform} onChange={e => setNewItem(p => ({ ...p, platform: e.target.value }))}>
                  <option value="">— Select —</option>
                  {PLATFORM_OPTIONS.map(p => <option key={p}>{p}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Condition</label>
                <select value={newItem.condition} onChange={e => setNewItem(p => ({ ...p, condition: e.target.value }))}>
                  {CONDITION_OPTIONS.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Status</label>
                <select value={newItem.status} onChange={e => setNewItem(p => ({ ...p, status: e.target.value }))}>
                  {STATUS_OPTIONS.filter(s => s !== 'All').map(s => <option key={s}>{s}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Purchase Price ($)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  value={newItem.purchasePrice}
                  onChange={e => setNewItem(p => ({ ...p, purchasePrice: e.target.value }))}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Current Value ($)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  value={newItem.currentValue}
                  onChange={e => setNewItem(p => ({ ...p, currentValue: e.target.value }))}
                />
              </div>
            </div>

            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => { setShowAddModal(false); setFormError('') }}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAddItem}>Add Item</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Confirm Delete Modal ── */}
      {confirmDelete && (
        <div className="modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="modal modal-sm" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Delete Item?</h2>
              <button className="modal-close" onClick={() => setConfirmDelete(null)}>×</button>
            </div>
            <p className="delete-confirm-text">
              Are you sure you want to remove <strong>"{confirmDelete.title}"</strong> from your collection? This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancel</button>
              <button className="btn btn-primary btn-delete-confirm" onClick={() => handleDelete(confirmDelete.id)}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}