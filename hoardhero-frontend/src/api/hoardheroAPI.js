// hoardheroAPI.js
// Central place for all Django API calls.
// Base URL can be changed here when deploying.

const BASE_URL = 'http://127.0.0.1:8001'

// ── CSRF helper ───────────────────────────────────────────────────────────
// Django requires a CSRF token for POST/PUT/DELETE requests
function getCsrfToken() {
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const trimmed = cookie.trim()
    if (trimmed.startsWith(name + '=')) {
      return decodeURIComponent(trimmed.substring(name.length + 1))
    }
  }
  return null
}

// ── Helper ────────────────────────────────────────────────────────────────
async function request(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' }

  // Add CSRF token for any state-changing request
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrf = getCsrfToken()
    if (csrf) headers['X-CSRFToken'] = csrf
  }

  const options = { method, headers, credentials: 'include' }
  if (body) options.body = JSON.stringify(body)

  const res = await fetch(`${BASE_URL}${path}`, options)

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: `Request failed: ${res.status}` }))
    throw new Error(err.error || err.Error || err.detail || `Request failed: ${res.status}`)
  }

  // 204 No Content (Django delete) — no body to parse
  if (res.status === 204) return { success: true }

  return res.json()
}

// ── CSRF init ─────────────────────────────────────────────────────────────
// Call this once on app startup to get the CSRF cookie from Django
export async function initCsrf() {
  try {
    await fetch(`${BASE_URL}/api/collections/`, {
      method: 'GET',
      credentials: 'include',
    })
  } catch (err) {
    console.warn('Could not initialize CSRF token:', err)
  }
}

// ── Collections ───────────────────────────────────────────────────────────

// GET all collections
export async function getCollections() {
  return request('GET', '/api/collections/')
}

// POST create a new collection
export async function createCollection({ name, type, clerk_user_id }) {
  return request('POST', '/api/collections/', { name, type, clerk_user_id })
}

// DELETE remove a collection
export async function deleteCollection(collectionId) {
  return request('DELETE', `/api/collections/${collectionId}/`)
}

// ── Items ─────────────────────────────────────────────────────────────────

// GET items for a collection (includes type_attributes)
export async function getItems(collectionId) {
  return request('GET', `/api/collections/${collectionId}/items/`)
}

// camelCase → snake_case for type-specific field names
const toSnake = key => key.replace(/[A-Z]/g, c => '_' + c.toLowerCase())

// POST add an item — uses the custom view that creates type-specific records
export async function addItem(collectionId, itemData) {
  const body = {
    collection_id: collectionId,
    name: itemData.title,
    condition: itemData.condition?.toLowerCase().replace(/\s+/g, '_') || 'good',
    purchase_price: itemData.purchasePrice || 0,
    current_value: itemData.currentValue || 0,
    barcode: itemData.barcode || '',
    description: itemData.description || '',
    image_url: itemData.imageUrl || '',
    quantity: 1,
  }

  // Pass type-specific fields (camelCase → snake_case)
  const skipKeys = new Set([
    'title', 'condition', 'purchasePrice', 'currentValue', 'barcode',
    'description', 'imageUrl', 'id', 'dateAdded', 'created_at', 'updated_at',
    'collection', 'name', 'quantity',
  ])
  for (const [key, val] of Object.entries(itemData)) {
    if (!skipKeys.has(key) && val !== undefined && val !== null && val !== '') {
      body[toSnake(key)] = val
    }
  }

  return request('POST', '/api/items/add/', body)
}

// PATCH update base fields of an item
export async function updateItem(collectionId, itemId, itemData) {
  const body = {
    name: itemData.title,
    condition: itemData.condition?.toLowerCase().replace(/\s+/g, '_') || 'good',
    purchase_price: itemData.purchasePrice || 0,
    current_value: itemData.currentValue || 0,
    barcode: itemData.barcode || '',
    description: itemData.description || '',
    image_url: itemData.imageUrl || '',
  }

  const skipKeys = new Set([
    'title', 'condition', 'purchasePrice', 'currentValue', 'barcode',
    'description', 'imageUrl', 'id', 'dateAdded', 'created_at', 'updated_at',
    'collection', 'name', 'quantity',
  ])
  for (const [key, val] of Object.entries(itemData)) {
    if (!skipKeys.has(key) && val !== undefined && val !== null && val !== '') {
      body[toSnake(key)] = val
    }
  }

  return request('PATCH', `/api/items/update/${collectionId}/${itemId}/`, body)
}

// DELETE remove an item
export async function deleteItem(collectionId, itemId) {
  return request('DELETE', `/api/items/delete/${collectionId}/${itemId}/`)
}

// ── Barcode ───────────────────────────────────────────────────────────────

// POST an image file to scan a barcode and look up item details
export async function scanBarcode(imageFile, djangoItemType) {
  const formData = new FormData()
  formData.append('image', imageFile)
  formData.append('item_type', djangoItemType)

  const csrf = getCsrfToken()
  const headers = {}
  if (csrf) headers['X-CSRFToken'] = csrf

  const res = await fetch(`${BASE_URL}/api/barcode/`, {
    method: 'POST',
    headers,
    credentials: 'include',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: `Request failed: ${res.status}` }))
    throw new Error(err.error || `Request failed: ${res.status}`)
  }

  return res.json()
}

// ── Wishlist ──────────────────────────────────────────────────────────────

// GET all wishlist items for the current user
export async function getWishlist() {
  return request('GET', '/api/wishlist/')
}

// POST add a wishlist item
export async function addWishlistItem(itemData) {
  return request('POST', '/api/wishlist/add/', {
    name: itemData.name,
    description: itemData.description || '',
    collection_type: itemData.collectionType || 'video_games',
    notes: itemData.notes || '',
    price_target: itemData.priceTarget || 0,
    link: itemData.link || '',
    clerk_user_id: itemData.clerk_user_id
  })
}

// DELETE remove a wishlist item
export async function deleteWishlistItem(itemId) {
  return request('DELETE', `/api/wishlist/delete/${itemId}/`)
}
