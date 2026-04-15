import { UserButton } from '@clerk/clerk-react'
import './Navbar.css'

export default function Navbar({ navigate, showBack, backLabel }) {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div
          className="navbar-brand"
          onClick={() => navigate('home')}
          style={{ cursor: 'pointer' }}
        >
          <div className="brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M9 22V12h6v10"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <span className="brand-name">HoardHero</span>
        </div>

        <div className="navbar-actions">
          {showBack && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => navigate('home')}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              {backLabel || 'Back'}
            </button>
          )}

          <button
            type="button"
            className="profile-nav-button"
            onClick={() => navigate('profile')}
          >
            Profile
          </button>

          <UserButton afterSignOutUrl="/" />
        </div>
      </div>
    </nav>
  )
}