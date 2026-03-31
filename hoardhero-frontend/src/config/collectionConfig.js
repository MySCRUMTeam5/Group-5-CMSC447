// collectionConfig.js
// Defines per-collection-type columns, filters, and form fields.
// TODO: Some dropdown options (platforms, genres, etc.) should eventually
//       come from GET /api/collection-options/:type/ on the Django backend.

export const COLLECTION_TYPES = [
  { value: 'games',        label: 'Video Games',    icon: '🎮' },
  { value: 'trading_cards',label: 'Trading Cards',  icon: '🃏' },
  { value: 'comics',       label: 'Comics',         icon: '📚' },
  { value: 'funko',        label: 'Funko Pops',     icon: '🧸' },
  { value: 'lego',         label: 'LEGO Sets',      icon: '🧱' },
  { value: 'sports_cards', label: 'Sports Cards',   icon: '⚾' },
  { value: 'music',        label: 'Music',          icon: '🎵' },
  { value: 'movies',       label: 'Movies',         icon: '🎬' },
]

export const CONDITION_OPTIONS = ['Mint', 'Near Mint', 'Excellent', 'Good', 'Fair', 'Poor']
export const GRADE_OPTIONS     = ['CGC 10', 'CGC 9.8', 'CGC 9.6', 'CGC 9.4', 'CGC 9.0', 'CGC 8.5', 'PSA 10', 'PSA 9', 'PSA 8', 'PSA 7', 'Ungraded']

// ---------------------------------------------------------------------------
// Per-type configuration
// ---------------------------------------------------------------------------

const CONFIGS = {

  // ── VIDEO GAMES ──────────────────────────────────────────────────────────
  games: {
    statusField:   'playStatus',
    statusOptions: ['Played', 'Playing', 'Unplayed'],
    columns: [
      { key: 'title',       label: 'Title',        primary: true },
      { key: 'platform',    label: 'Platform' },
      { key: 'genre',       label: 'Genre' },
      { key: 'completeness',label: 'Completeness' },
      { key: 'condition',   label: 'Condition',    dot: true },
      { key: 'playStatus',  label: 'Status',       badge: true },
      { key: 'purchasePrice', label: 'Paid',       price: true },
      { key: 'currentValue',  label: 'Value',      value: true },
    ],
    filters: [
      { key: 'platform', label: 'Platform', options: [
        'Nintendo Switch', 'Nintendo Switch 2', 'PS5', 'PS4', 'PS3',
        'Xbox Series X', 'Xbox One', 'Xbox 360', 'PC',
        'Nintendo 64', 'GameBoy', 'GameBoy Advance', 'Nintendo DS',
        'Nintendo 3DS', 'Wii', 'Wii U', 'Sega Genesis', 'Atari 2600', 'Other',
      ]},
      { key: 'genre', label: 'Genre', options: [
        'Action', 'Adventure', 'RPG', 'FPS', 'Sports', 'Racing',
        'Puzzle', 'Strategy', 'Simulation', 'Horror', 'Fighting', 'Other',
      ]},
      { key: 'completeness', label: 'Completeness', options: ['Complete in Box', 'Game Only', 'Box Only', 'Loose'] },
    ],
    formFields: [
      { key: 'title',        label: 'Title',        type: 'text',   required: true, span: 2 },
      { key: 'platform',     label: 'Platform',     type: 'select', options: [
        'Nintendo Switch', 'Nintendo Switch 2', 'PS5', 'PS4', 'PS3',
        'Xbox Series X', 'Xbox One', 'Xbox 360', 'PC',
        'Nintendo 64', 'GameBoy', 'GameBoy Advance', 'Nintendo DS',
        'Nintendo 3DS', 'Wii', 'Wii U', 'Sega Genesis', 'Atari 2600', 'Other',
      ]},
      { key: 'genre',        label: 'Genre',        type: 'select', options: [
        'Action', 'Adventure', 'RPG', 'FPS', 'Sports', 'Racing',
        'Puzzle', 'Strategy', 'Simulation', 'Horror', 'Fighting', 'Other',
      ]},
      { key: 'completeness', label: 'Completeness', type: 'select', options: ['Complete in Box', 'Game Only', 'Box Only', 'Loose'] },
      { key: 'condition',    label: 'Condition',    type: 'select', options: CONDITION_OPTIONS },
      { key: 'playStatus',   label: 'Play Status',  type: 'select', options: ['Played', 'Playing', 'Unplayed'] },
      { key: 'purchasePrice',label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue', label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── TRADING CARDS ─────────────────────────────────────────────────────────
  trading_cards: {
    statusField:   null,
    statusOptions: [],
    columns: [
      { key: 'title',      label: 'Card Name',   primary: true },
      { key: 'series',     label: 'Series' },
      { key: 'setName',    label: 'Set Name' },
      { key: 'cardNumber', label: 'Card #' },
      { key: 'condition',  label: 'Condition',   dot: true },
      { key: 'grade',      label: 'Grade',       badge: true },
      { key: 'purchasePrice', label: 'Paid',     price: true },
      { key: 'currentValue',  label: 'Value',    value: true },
    ],
    filters: [
      { key: 'series',  label: 'Series',  options: ['Pokémon', 'Magic: The Gathering', 'Yu-Gi-Oh!', 'Dragon Ball', 'One Piece', 'Other'] },
      { key: 'grade',   label: 'Grade',   options: GRADE_OPTIONS },
    ],
    formFields: [
      { key: 'title',       label: 'Card Name',   type: 'text',   required: true, span: 2 },
      { key: 'series',      label: 'Series',      type: 'select', options: ['Pokémon', 'Magic: The Gathering', 'Yu-Gi-Oh!', 'Dragon Ball', 'One Piece', 'Other'] },
      { key: 'setName',     label: 'Set Name',    type: 'text' },
      { key: 'cardNumber',  label: 'Card #',      type: 'text' },
      { key: 'condition',   label: 'Condition',   type: 'select', options: CONDITION_OPTIONS },
      { key: 'grade',       label: 'Grade',       type: 'select', options: GRADE_OPTIONS },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── COMICS ────────────────────────────────────────────────────────────────
  comics: {
    statusField:   'readStatus',
    statusOptions: ['Read', 'Unread'],
    columns: [
      { key: 'title',       label: 'Title',       primary: true },
      { key: 'publisher',   label: 'Publisher' },
      { key: 'issueTitle',  label: 'Issue Title' },
      { key: 'issueNumber', label: 'Issue #' },
      { key: 'condition',   label: 'Condition',   dot: true },
      { key: 'grade',       label: 'Grade',       badge: true },
      { key: 'readStatus',  label: 'Status',      badge: true },
      { key: 'purchasePrice', label: 'Paid',      price: true },
      { key: 'currentValue',  label: 'Value',     value: true },
    ],
    filters: [
      { key: 'publisher',  label: 'Publisher',  options: ['Marvel', 'DC', 'Image', 'Dark Horse', 'IDW', 'BOOM! Studios', 'Other'] },
      { key: 'readStatus', label: 'Read Status', options: ['Read', 'Unread'] },
      { key: 'grade',      label: 'Grade',       options: GRADE_OPTIONS },
    ],
    formFields: [
      { key: 'title',       label: 'Series Title',  type: 'text',   required: true, span: 2 },
      { key: 'publisher',   label: 'Publisher',     type: 'select', options: ['Marvel', 'DC', 'Image', 'Dark Horse', 'IDW', 'BOOM! Studios', 'Other'] },
      { key: 'issueTitle',  label: 'Issue Title',   type: 'text' },
      { key: 'issueNumber', label: 'Issue #',       type: 'text' },
      { key: 'condition',   label: 'Condition',     type: 'select', options: CONDITION_OPTIONS },
      { key: 'grade',       label: 'Grade',         type: 'select', options: GRADE_OPTIONS },
      { key: 'readStatus',  label: 'Read Status',   type: 'select', options: ['Read', 'Unread'] },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── FUNKO POPS ────────────────────────────────────────────────────────────
  funko: {
    statusField:   null,
    statusOptions: [],
    columns: [
      { key: 'title',        label: 'Name',        primary: true },
      { key: 'series',       label: 'Series' },
      { key: 'boxNumber',    label: 'Box #' },
      { key: 'completeness', label: 'Completeness' },
      { key: 'condition',    label: 'Condition',   dot: true },
      { key: 'exclusive',    label: 'Exclusive',   badge: true },
      { key: 'purchasePrice', label: 'Paid',       price: true },
      { key: 'currentValue',  label: 'Value',      value: true },
    ],
    filters: [
      { key: 'series',       label: 'Series',       options: ['Marvel', 'DC', 'Disney', 'Star Wars', 'Anime', 'Games', 'Movies', 'TV', 'Other'] },
      { key: 'completeness', label: 'Completeness', options: ['Mint in Box', 'Out of Box', 'Box Only'] },
      { key: 'exclusive',    label: 'Exclusive',    options: ['Hot Topic', 'Target', 'Walmart', 'GameStop', 'Amazon', 'SDCC', 'None'] },
    ],
    formFields: [
      { key: 'title',        label: 'Name',         type: 'text',   required: true, span: 2 },
      { key: 'series',       label: 'Series',       type: 'select', options: ['Marvel', 'DC', 'Disney', 'Star Wars', 'Anime', 'Games', 'Movies', 'TV', 'Other'] },
      { key: 'boxNumber',    label: 'Box #',        type: 'text' },
      { key: 'completeness', label: 'Completeness', type: 'select', options: ['Mint in Box', 'Out of Box', 'Box Only'] },
      { key: 'condition',    label: 'Condition',    type: 'select', options: CONDITION_OPTIONS },
      { key: 'exclusive',    label: 'Exclusive',    type: 'select', options: ['Hot Topic', 'Target', 'Walmart', 'GameStop', 'Amazon', 'SDCC', 'None'] },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── LEGO SETS ─────────────────────────────────────────────────────────────
  lego: {
    statusField:   null,
    statusOptions: [],
    columns: [
      { key: 'title',        label: 'Set Name',    primary: true },
      { key: 'series',       label: 'Series' },
      { key: 'setNumber',    label: 'Set #' },
      { key: 'pieceCount',   label: 'Pieces' },
      { key: 'completeness', label: 'Completeness' },
      { key: 'condition',    label: 'Condition',   dot: true },
      { key: 'purchasePrice', label: 'Paid',       price: true },
      { key: 'currentValue',  label: 'Value',      value: true },
    ],
    filters: [
      { key: 'series',       label: 'Theme',        options: ['Star Wars', 'Technic', 'City', 'Creator', 'Harry Potter', 'Marvel', 'Architecture', 'Icons', 'Other'] },
      { key: 'completeness', label: 'Completeness', options: ['Complete', 'Missing Pieces', 'Sealed', 'No Box'] },
    ],
    formFields: [
      { key: 'title',        label: 'Set Name',     type: 'text',   required: true, span: 2 },
      { key: 'series',       label: 'Theme/Series', type: 'select', options: ['Star Wars', 'Technic', 'City', 'Creator', 'Harry Potter', 'Marvel', 'Architecture', 'Icons', 'Other'] },
      { key: 'setNumber',    label: 'Set #',        type: 'text' },
      { key: 'pieceCount',   label: 'Piece Count',  type: 'number' },
      { key: 'completeness', label: 'Completeness', type: 'select', options: ['Complete', 'Missing Pieces', 'Sealed', 'No Box'] },
      { key: 'condition',    label: 'Condition',    type: 'select', options: CONDITION_OPTIONS },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── SPORTS CARDS ──────────────────────────────────────────────────────────
  sports_cards: {
    statusField:   null,
    statusOptions: [],
    columns: [
      { key: 'title',      label: 'Card Name',  primary: true },
      { key: 'sport',      label: 'Sport' },
      { key: 'playerName', label: 'Player' },
      { key: 'cardNumber', label: 'Card #' },
      { key: 'year',       label: 'Year' },
      { key: 'condition',  label: 'Condition',  dot: true },
      { key: 'grade',      label: 'Grade',      badge: true },
      { key: 'purchasePrice', label: 'Paid',    price: true },
      { key: 'currentValue',  label: 'Value',   value: true },
    ],
    filters: [
      { key: 'sport', label: 'Sport', options: ['Baseball', 'Basketball', 'Football', 'Hockey', 'Soccer', 'Golf', 'Tennis', 'Other'] },
      { key: 'grade', label: 'Grade', options: GRADE_OPTIONS },
    ],
    formFields: [
      { key: 'title',      label: 'Card Name',  type: 'text',   required: true, span: 2 },
      { key: 'sport',      label: 'Sport',      type: 'select', options: ['Baseball', 'Basketball', 'Football', 'Hockey', 'Soccer', 'Golf', 'Tennis', 'Other'] },
      { key: 'playerName', label: 'Player Name', type: 'text' },
      { key: 'cardNumber', label: 'Card #',     type: 'text' },
      { key: 'year',       label: 'Year',       type: 'number' },
      { key: 'condition',  label: 'Condition',  type: 'select', options: CONDITION_OPTIONS },
      { key: 'grade',      label: 'Grade',      type: 'select', options: GRADE_OPTIONS },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── MUSIC ─────────────────────────────────────────────────────────────────
  music: {
    statusField:   null,
    statusOptions: [],
    columns: [
      { key: 'title',     label: 'Album Title', primary: true },
      { key: 'artist',    label: 'Artist' },
      { key: 'format',    label: 'Format',      badge: true },
      { key: 'genre',     label: 'Genre' },
      { key: 'condition', label: 'Condition',   dot: true },
      { key: 'purchasePrice', label: 'Paid',    price: true },
      { key: 'currentValue',  label: 'Value',   value: true },
    ],
    filters: [
      { key: 'format', label: 'Format', options: ['Vinyl', 'CD', 'Cassette', 'Digital', '8-Track'] },
      { key: 'genre',  label: 'Genre',  options: ['Rock', 'Pop', 'Hip-Hop', 'Jazz', 'Classical', 'Country', 'R&B', 'Electronic', 'Metal', 'Other'] },
    ],
    formFields: [
      { key: 'title',   label: 'Album Title', type: 'text',   required: true, span: 2 },
      { key: 'artist',  label: 'Artist',      type: 'text',   required: true },
      { key: 'format',  label: 'Format',      type: 'select', options: ['Vinyl', 'CD', 'Cassette', 'Digital', '8-Track'] },
      { key: 'genre',   label: 'Genre',       type: 'select', options: ['Rock', 'Pop', 'Hip-Hop', 'Jazz', 'Classical', 'Country', 'R&B', 'Electronic', 'Metal', 'Other'] },
      { key: 'condition', label: 'Condition', type: 'select', options: CONDITION_OPTIONS },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },

  // ── MOVIES ────────────────────────────────────────────────────────────────
  movies: {
    statusField:   'watchedStatus',
    statusOptions: ['Watched', 'Unwatched'],
    columns: [
      { key: 'title',        label: 'Title',       primary: true },
      { key: 'format',       label: 'Format',      badge: true },
      { key: 'genre',        label: 'Genre' },
      { key: 'director',     label: 'Director' },
      { key: 'condition',    label: 'Condition',   dot: true },
      { key: 'watchedStatus',label: 'Status',      badge: true },
      { key: 'purchasePrice', label: 'Paid',       price: true },
      { key: 'currentValue',  label: 'Value',      value: true },
    ],
    filters: [
      { key: 'format',       label: 'Format',  options: ['4K UHD', 'Blu-ray', 'DVD', 'Digital', 'VHS'] },
      { key: 'genre',        label: 'Genre',   options: ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Thriller', 'Animation', 'Documentary', 'Other'] },
      { key: 'watchedStatus',label: 'Status',  options: ['Watched', 'Unwatched'] },
    ],
    formFields: [
      { key: 'title',    label: 'Title',    type: 'text',   required: true, span: 2 },
      { key: 'format',   label: 'Format',   type: 'select', options: ['4K UHD', 'Blu-ray', 'DVD', 'Digital', 'VHS'] },
      { key: 'genre',    label: 'Genre',    type: 'select', options: ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Thriller', 'Animation', 'Documentary', 'Other'] },
      { key: 'director', label: 'Director', type: 'text' },
      { key: 'condition',label: 'Condition',type: 'select', options: CONDITION_OPTIONS },
      { key: 'watchedStatus', label: 'Watched Status', type: 'select', options: ['Watched', 'Unwatched'] },
      { key: 'purchasePrice', label: 'Purchase Price ($)', type: 'number' },
      { key: 'currentValue',  label: 'Current Value ($)',  type: 'number' },
    ],
  },
}

export function getConfig(type) {
  return CONFIGS[type] || CONFIGS['games']
}

export const BADGE_COLORS = {
  // Play status
  Played:    'badge-green',
  Playing:   'badge-blue',
  Unplayed:  'badge-gray',
  // Read status
  Read:      'badge-green',
  Unread:    'badge-gray',
  // Watched status
  Watched:   'badge-green',
  Unwatched: 'badge-gray',
  // Formats
  Vinyl:     'badge-blue',
  CD:        'badge-gray',
  Cassette:  'badge-yellow',
  '4K UHD':  'badge-blue',
  'Blu-ray': 'badge-green',
  DVD:       'badge-gray',
  // Grades
  'CGC 10':  'badge-green',
  'PSA 10':  'badge-green',
  'CGC 9.8': 'badge-blue',
  'PSA 9':   'badge-blue',
  Ungraded:  'badge-gray',
}

export const CONDITION_COLORS = {
  'Mint':      '#22C55E',
  'Near Mint': '#4ADE80',
  'Excellent': '#3B82F6',
  'Good':      '#F59E0B',
  'Fair':      '#F97316',
  'Poor':      '#EF4444',
}
