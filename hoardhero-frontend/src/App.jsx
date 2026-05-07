import { useState } from 'react'
import { SignedIn, SignedOut } from '@clerk/clerk-react'
import HomePage from './pages/HomePage'
import CollectionPage from './pages/CollectionPage'
import WishlistPage from './pages/WishlistPage'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'
import ProfilePage from './pages/ProfilePage'

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [selectedCollection, setSelectedCollection] = useState(null)
  const [authPage, setAuthPage] = useState('signin')

  const navigate = (page, data = null) => {
    if (page === 'signin' || page === 'signup') {
      setAuthPage(page)
      return
    }

    setCurrentPage(page)

    if (page === 'collection') {
      setSelectedCollection(data)
    }
  }

  return (
    <div className="app">
      <SignedOut>
        {authPage === 'signin' && <SignInPage navigate={navigate} />}
        {authPage === 'signup' && <SignUpPage navigate={navigate} />}
      </SignedOut>

      <SignedIn>
        {currentPage === 'home' && <HomePage navigate={navigate} />}

        {currentPage === 'collection' && (
          <CollectionPage navigate={navigate} collection={selectedCollection} />
        )}
        {currentPage === 'wishlist' && (
          <WishlistPage navigate={navigate} />
        )}
      </SignedIn>
    </div>
  )
}

export default App