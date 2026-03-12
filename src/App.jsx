import { useState } from 'react'
import HomePage from './pages/HomePage'
import CollectionPage from './pages/CollectionPage'

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [selectedCollection, setSelectedCollection] = useState(null)

  const navigate = (page, data = null) => {
    setCurrentPage(page)
    if (data) setSelectedCollection(data)
  }

  return (
    <div className="app">
      {currentPage === 'home' && (
        <HomePage navigate={navigate} />
      )}
      {currentPage === 'collection' && (
        <CollectionPage navigate={navigate} collection={selectedCollection} />
      )}
    </div>
  )
}

export default App
