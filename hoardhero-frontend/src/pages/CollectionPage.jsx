import { useState, useEffect, useMemo } from 'react'
import Navbar from '../components/Navbar'
import { getConfig, BADGE_COLORS, CONDITION_COLORS } from '../config/collectionConfig'
import { getItems, addItem, deleteItem } from '../api/hoardheroAPI'
import './CollectionPage.css'

const SORT_OPTIONS = [
  { value: 'dateAdded-desc', label: 'Newest First' },
  { value: 'dateAdded-asc',  label: 'Oldest First' },
  { value: 'title-asc',      label: 'Name A→Z' },
  { value: 'title-desc',     label: 'Name Z→A' },
  { value: 'purchasePrice-desc', label: 'Price High→Low' },
  { value: 'purchasePrice-asc',  label: 'Price Low→High' },
  { value: 'currentValue-desc',  label: 'Value High→Low' },
]

// ── Duplicate helpers ────────────────────────────────────────────────────────

// Generate a fingerprint of all fields except id and dateAdded
// If two items share the same fingerprint they are EXACT duplicates
function itemFingerprint(item) {
  const { id, dateAdded, ...rest } = item
  return JSON.stringify(rest, Object.keys(rest).sort())
}

// Returns a map of { fingerprint -> [items] } for exact duplicates
function buildExactDupeMap(items) {
  const map = {}
  items.forEach(item => {
    const fp = itemFingerprint(item)
    if (!map[fp]) map[fp] = []
    map[fp].push(item)
  })
  return map
}

// Returns a map of { normalizedTitle -> [items] } for same-title variants
function buildTitleVariantMap(items) {
  const map = {}
  items.forEach(item => {
    const key = (item.title || '').toLowerCase().trim()
    if (!key) return
    if (!map[key]) map[key] = []
    map[key].push(item)
  })
  return map
}

export default function CollectionPage({ navigate, collection }) {
  const col    = collection || { name: 'Collection', icon: '📦', type: 'games' }
  const config = getConfig(col.type)

  const [items,          setItems]          = useState([])
  const [search,         setSearch]         = useState('')
  const [activeFilters,  setActiveFilters]  = useState({})
  const [sortBy,         setSortBy]         = useState('dateAdded-desc')
  const [showAddModal,   setShowAddModal]   = useState(false)
  const [confirmDelete,  setConfirmDelete]  = useState(null)
  const [newItem,        setNewItem]        = useState({})
  const [formError,      setFormError]      = useState('')
  const [expandedTitles, setExpandedTitles] = useState({})
  const [loading,        setLoading]        = useState(true)
  const [pageError,      setPageError]      = useState('')

  useEffect(() => {
    setItems([])
    setSearch('')
    setActiveFilters({})
    setNewItem({})
    setExpandedTitles({})
    fetchItems()
  }, [col.id])

  const fetchItems = async () => {
    try {
      setLoading(true)
      setPageError('')
      const data = await getItems(col.id, col.type)
      // Map Django Item fields to frontend shape
      const mapped = (Array.isArray(data) ? data : []).map(item => ({
        id:            item.id,
        title:         item.name,
        condition:     item.condition,
        purchasePrice: parseFloat(item.purchase_price) || 0,
        currentValue:  parseFloat(item.current_value)  || 0,
        dateAdded:     item.created_at?.slice(0, 10) || '',
        // Type-specific fields spread in
        ...item,
      }))
      setItems(mapped)
    } catch (err) {
      setPageError('Could not load items. Is the Django server running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // ── Duplicate maps (computed from ALL items, before filtering) ────────────
  const exactDupeMap   = useMemo(() => buildExactDupeMap(items),   [items])
  const titleVariantMap = useMemo(() => buildTitleVariantMap(items), [items])

  // For a given item, how many exact copies exist (including itself)?
  const exactCount = (item) => {
    const fp = itemFingerprint(item)
    return exactDupeMap[fp]?.length || 1
  }

  // Total copies of a title across ALL versions (exact dupes + variants)
  const totalTitleCount = (item) => {
    const key = (item.title || '').toLowerCase().trim()
    const group = titleVariantMap[key] || []
    return group.reduce((sum, i) => sum + (exactDupeMap[itemFingerprint(i)]?.length || 1), 0)
  }

  // Is this item a "representative" of its exact-dupe group?
  // (only the first item in the group is shown as a row)
  const isRepresentative = (item) => {
    const fp = itemFingerprint(item)
    return exactDupeMap[fp][0].id === item.id
  }

  // Does this title have same-title variants with DIFFERENT fields?
  const hasTitleVariants = (item) => {
    const key   = (item.title || '').toLowerCase().trim()
    const group = titleVariantMap[key] || []
    // Filter to only representatives so we don't double-count exact dupes
    const reps  = group.filter(i => isRepresentative(i))
    return reps.length > 1
  }

  // All representative items for a given title (for the dropdown)
  const titleVariants = (item) => {
    const key = (item.title || '').toLowerCase().trim()
    return (titleVariantMap[key] || []).filter(i => isRepresentative(i))
  }

  // ── Filtered + sorted display list ───────────────────────────────────────
  const displayItems = useMemo(() => {
    let list = [...items]

    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter(i =>
        Object.values(i).some(v => String(v).toLowerCase().includes(q))
      )
    }

    Object.entries(activeFilters).forEach(([key, val]) => {
      if (val && val !== 'All') list = list.filter(i => i[key] === val)
    })

    const [field, dir] = sortBy.split('-')
    list.sort((a, b) => {
      const av = a[field] ?? '', bv = b[field] ?? ''
      if (typeof av === 'string') return dir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
      return dir === 'asc' ? av - bv : bv - av
    })

    // Only keep one representative per exact-dupe group AND one row per title
    const seen = new Set()
    const seenTitles = new Set()
    return list.filter(item => {
      const fp = itemFingerprint(item)
      if (seen.has(fp)) return false
      seen.add(fp)
      // Only show one row per title (the first/representative one)
      const titleKey = (item.title || '').toLowerCase().trim()
      if (seenTitles.has(titleKey)) return false
      seenTitles.add(titleKey)
      return true
    })
  }, [items, search, activeFilters, sortBy])

  const totalValue = items.reduce((s, i) => s + (parseFloat(i.currentValue)  || 0), 0)
  const totalSpent = items.reduce((s, i) => s + (parseFloat(i.purchasePrice) || 0), 0)

  // Total duplicate count across entire collection
  const totalDupes = useMemo(() => {
    return Object.values(exactDupeMap).filter(g => g.length > 1).length
  }, [exactDupeMap])

  // ── Add item ──────────────────────────────────────────────────────────────
  const handleAddItem = async () => {
    if (!newItem.title?.trim()) { setFormError('Title is required.'); return }
    try {
      setFormError('')
      const data = await addItem(col.id, newItem)
      const created = {
        id:            data.item?.id || Date.now(),
        title:         data.item?.name || newItem.title,
        condition:     newItem.condition,
        purchasePrice: parseFloat(newItem.purchasePrice) || 0,
        currentValue:  parseFloat(newItem.currentValue)  || 0,
        dateAdded:     data.item?.created_at?.slice(0, 10) || new Date().toISOString().slice(0, 10),
        ...newItem,
      }
      setItems(prev => [created, ...prev])
      setNewItem({})
      setShowAddModal(false)
    } catch (err) {
      setFormError(err.message || 'Failed to add item. Please try again.')
      console.error(err)
    }
  }

  // ── Delete item ───────────────────────────────────────────────────────────
  const handleDelete = async (id) => {
    if (!id) return
    try {
      await deleteItem(col.id, id)
      setItems(prev => prev.filter(i => i.id !== id))
    } catch (err) {
      // 404 means already deleted — still remove from UI
      if (err.message?.includes('404') || err.message?.includes('Not found')) {
        setItems(prev => prev.filter(i => i.id !== id))
      } else {
        console.error('Delete failed:', err)
      }
    } finally {
      setConfirmDelete(null)
    }
  }

  // Delete ALL exact copies of an item
  const handleDeleteAll = async (item) => {
    const fp  = itemFingerprint(item)
    const ids = (exactDupeMap[fp] || []).map(i => i.id)
    const idSet = new Set(ids)
    try {
      await Promise.all(ids.map(id => deleteItem(col.id, id)))
    } catch (err) {
      console.error('Delete all failed:', err)
    } finally {
      setItems(prev => prev.filter(i => !idSet.has(i.id)))
      setConfirmDelete(null)
    }
  }

  // ── Filter change ─────────────────────────────────────────────────────────
  const handleFilter = (key, val) => {
    setActiveFilters(prev => ({ ...prev, [key]: val }))
  }

  const hasActiveFilters = search ||
    Object.values(activeFilters).some(v => v && v !== 'All')

  const toggleExpanded = (title) => {
    const key = title.toLowerCase().trim()
    setExpandedTitles(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const isExpanded = (title) => {
    return !!expandedTitles[(title || '').toLowerCase().trim()]
  }

  // ── Cell renderer ─────────────────────────────────────────────────────────
  const renderCell = (item, col) => {
    const val = item[col.key]
    if (val === undefined || val === null || val === '') {
      return <span style={{ color: 'var(--text-muted)' }}>—</span>
    }
    if (col.primary) return <span className="item-title">{val}</span>
    if (col.dot) return (
      <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span className="condition-dot" style={{ background: CONDITION_COLORS[val] || '#9CA3AF' }} />
        {val}
      </span>
    )
    if (col.badge) {
      return <span className={`badge ${BADGE_COLORS[val] || 'badge-gray'}`}>{val}</span>
    }
    if (col.price) return <span>${parseFloat(val).toFixed(2)}</span>
    if (col.value) {
      const spent  = parseFloat(item.purchasePrice) || 0
      const curr   = parseFloat(val) || 0
      const profit = curr - spent
      return (
        <span>
          <span className={profit >= 0 ? 'profit-pos' : 'profit-neg'}>${curr.toFixed(2)}</span>
          <span className={`profit-delta ${profit >= 0 ? 'pos' : 'neg'}`}>
            {profit >= 0 ? '+' : ''}{profit.toFixed(2)}
          </span>
        </span>
      )
    }
    return <span>{val}</span>
  }

  const colSpan = config.columns.length + 1

  return (
    <div className="collection-page">
      <Navbar navigate={navigate} showBack backLabel="Home" />

      <main className="collection-main">

        {/* Page header */}
        <div className="page-header animate-in">
          <div className="page-header-left">
            <span className="page-icon">{col.icon}</span>
            <div>
              <h1 className="page-title">{col.name}</h1>
              <p className="page-subtitle">
                {items.length} items · Est. value ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                {totalDupes > 0 && (
                  <span className="dupe-summary-badge">
                    ⚠ {totalDupes} duplicate {totalDupes === 1 ? 'group' : 'groups'}
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="page-header-actions">
            <div className="value-chip">
              <span className="value-chip-label">Spent</span>
              <span className="value-chip-val spent">
                ${totalSpent.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="value-chip">
              <span className="value-chip-label">Value</span>
              <span className={`value-chip-val ${totalValue >= totalSpent ? 'gain' : 'loss'}`}>
                ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              Add Item
            </button>
          </div>
        </div>

        {/* Filter / sort bar */}
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
            {search && <button className="search-clear" onClick={() => setSearch('')}>×</button>}
          </div>

          {config.statusField && config.statusOptions.length > 0 && (
            <div className="filter-group">
              <span className="filter-label">Status</span>
              <select
                className="sort-select"
                value={activeFilters[config.statusField] || 'All'}
                onChange={e => handleFilter(config.statusField, e.target.value)}
              >
                <option value="All">All</option>
                {config.statusOptions.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
          )}

          {config.filters.map(f => (
            <div key={f.key} className="filter-group">
              <span className="filter-label">{f.label}</span>
              <select
                className="sort-select"
                value={activeFilters[f.key] || 'All'}
                onChange={e => handleFilter(f.key, e.target.value)}
              >
                <option value="All">All</option>
                {f.options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
          ))}

          <div className="sort-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M7 12h10M11 18h2"/>
            </svg>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="sort-select">
              {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>

          {hasActiveFilters && (
            <button className="btn btn-ghost btn-sm" onClick={() => { setSearch(''); setActiveFilters({}) }}>
              Clear filters
            </button>
          )}
        </div>

        {hasActiveFilters && (
          <p className="results-count">Showing {displayItems.length} of {items.length} items</p>
        )}

        {/* API error state */}
        {pageError && (
          <div className="api-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
            </svg>
            {pageError}
            <button className="btn btn-sm btn-secondary" onClick={fetchItems}>Retry</button>
          </div>
        )}

        {/* Loading state */}
        {loading && !pageError && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Loading items...</p>
          </div>
        )}

        {/* Empty states */}
        {!loading && !pageError && items.length === 0 ? (
          <div className="empty-state animate-in">
            <div className="empty-icon">{col.icon}</div>
            <h3>No items yet</h3>
            <p>Click "Add Item" to start building your {col.name} collection.</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setShowAddModal(true)}>
              + Add your first item
            </button>
          </div>

        ) : displayItems.length === 0 ? (
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
                  {config.columns.map(c => <th key={c.key}>{c.label}</th>)}
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {displayItems.map((item, i) => {
                  const count    = exactCount(item)
                  const variants = hasTitleVariants(item)
                  const expanded = isExpanded(item.title)

                  return (
                    <>
                      {/* ── Main row ── */}
                      <tr key={item.id} className="item-row" style={{ animationDelay: `${i * 30}ms` }}>
                        {config.columns.map(c => (
                          <td key={c.key}>
                            {/* Title cell gets badges + variant toggle */}
                            {c.primary ? (
                              <div className="title-cell">
                                <span className="item-title">{item.title}</span>
                                <div className="title-badges">
                                {/* Count badge — total copies of this title */}
                                  {totalTitleCount(item) > 1 && (
                                    <span className="dupe-count-badge" title={`${totalTitleCount(item)} total copies of this title`}>
                                      ×{totalTitleCount(item)}
                                    </span>
                                  )}
                                  {/* Variant dropdown arrow — only shows if variants exist */}
                                  {variants && (
                                    <button
                                      className="variant-arrow"
                                      onClick={() => toggleExpanded(item.title)}
                                      title="This title has multiple versions — click to expand"
                                    >
                                      <svg
                                        width="14" height="14"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2.5"
                                        style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
                                      >
                                        <path d="M6 9l6 6 6-6"/>
                                      </svg>
                                    </button>
                                  )}
                                </div>
                              </div>
                            ) : renderCell(item, c)}
                          </td>
                        ))}
                        <td>
                          <button
                            className="btn btn-danger btn-sm delete-btn"
                            onClick={() => setConfirmDelete({ item, isExact: count > 1 })}
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

                      {/* ── Variant dropdown rows ── */}
                      {variants && expanded && (
                        <tr key={`${item.id}-variants`} className="variant-row">
                          <td colSpan={colSpan}>
                            <div className="variant-panel">
                              <div className="variant-panel-header">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <circle cx="12" cy="12" r="10"/>
                                  <path d="M12 8v4M12 16h.01"/>
                                </svg>
                                Multiple versions of <strong>"{item.title}"</strong> found in your collection
                              </div>
                              <table className="variant-table">
                                <thead>
                                  <tr>
                                    {config.columns.filter(c => !c.primary).map(c => (
                                      <th key={c.key}>{c.label}</th>
                                    ))}
                                    <th>Copies</th>
                                    <th></th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {titleVariants(item).map(v => (
                                    <tr key={v.id} className="variant-item-row">
                                      {config.columns.filter(c => !c.primary).map(c => (
                                        <td key={c.key}>{renderCell(v, c)}</td>
                                      ))}
                                      <td>
                                        <span className={exactCount(v) > 1 ? 'dupe-count-badge' : 'badge badge-gray'}>
                                          ×{exactCount(v)}
                                        </span>
                                      </td>
                                      <td>
                                        <button
                                          className="btn btn-danger btn-sm delete-btn"
                                          onClick={() => setConfirmDelete({ item: v, isExact: exactCount(v) > 1 })}
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
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
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
              <button className="modal-close" onClick={() => { setShowAddModal(false); setFormError('') }}>×</button>
            </div>
            {formError && <div className="form-error">{formError}</div>}
            <div className="form-grid">
              {config.formFields.map(field => (
                <div key={field.key} className={`form-group ${field.span === 2 ? 'form-span-2' : ''}`}>
                  <label className="form-label">{field.label}{field.required ? ' *' : ''}</label>
                  {field.type === 'select' ? (
                    <select
                      value={newItem[field.key] || ''}
                      onChange={e => setNewItem(p => ({ ...p, [field.key]: e.target.value }))}
                    >
                      <option value="">— Select —</option>
                      {field.options.map(o => <option key={o} value={o}>{o}</option>)}
                    </select>
                  ) : (
                    <input
                      type={field.type}
                      min={field.type === 'number' ? '0' : undefined}
                      step={field.type === 'number' ? '0.01' : undefined}
                      placeholder={field.type === 'number' ? '0.00' : ''}
                      value={newItem[field.key] || ''}
                      onChange={e => setNewItem(p => ({ ...p, [field.key]: e.target.value }))}
                      autoFocus={field.key === 'title'}
                    />
                  )}
                </div>
              ))}
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
              {confirmDelete.isExact ? (
                <>
                  <strong>"{confirmDelete.item.title}"</strong> has {exactCount(confirmDelete.item)} identical copies.
                  Do you want to delete just one copy or all {exactCount(confirmDelete.item)} copies?
                </>
              ) : (
                <>
                  Are you sure you want to remove <strong>"{confirmDelete.item.title}"</strong> from
                  your collection? This action cannot be undone.
                </>
              )}
            </p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancel</button>
              {confirmDelete.isExact && (
                <button className="btn btn-secondary" onClick={() => handleDelete(confirmDelete.item.id)}>
                  Delete One
                </button>
              )}
              <button
                className="btn btn-primary btn-delete-confirm"
                onClick={() => confirmDelete.isExact
                  ? handleDeleteAll(confirmDelete.item)
                  : handleDelete(confirmDelete.item.id)
                }
              >
                {confirmDelete.isExact ? `Delete All ${exactCount(confirmDelete.item)}` : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
