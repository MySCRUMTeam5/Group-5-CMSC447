import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [collections, setCollections] = useState([])
  const [loading, setLoading] = useState(true)

  // This is the "Telephone Call" to the Backend
  useEffect(() => {
    fetch('http://localhost:8001/api/collections/')
      .then(response => response.json())
      .then(data => {
        setCollections(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching data:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div className="App">
      <h1>Hoard Hero Collections</h1>

      {loading ? (
        <p>Loading your treasures...</p>
      ) : (
        <div className="collection-list">
          {collections.length === 0 ? (
            <p>No collections found. Go to the Backend window to add one!</p>
          ) : (
            <ul>
              {collections.map(collection => (
                <li key={collection.id}>
                  <strong>{collection.name}</strong> - {collection.category}
                  <br />
                  <small>Owned by: {collection.owner}</small>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <p>
        <a href="http://localhost:8001/api/collections/" target="_blank" rel="noreferrer">
          Go to Backend Service Window
        </a>
      </p>
    </div>
  )
}

export default App
