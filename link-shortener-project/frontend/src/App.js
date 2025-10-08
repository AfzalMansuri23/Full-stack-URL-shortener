import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State for the form input
  const [longUrl, setLongUrl] = useState('');
  // State for the most recent API result
  const [shortURL, setShortURL] = useState(null);
  // State for the list of all links (for the history table)
  const [links, setLinks] = useState([]);
  // State for loading and error messages
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // --- This effect runs once when the component loads to fetch history ---
  useEffect(() => {
    const fetchLinks = async () => {
      try {
        const response = await fetch('/api/links');
        const data = await response.json();
        setLinks(data.links);
      } catch (error) {
        console.error("Failed to fetch links:", error);
        setError("Could not load link history. Is the backend running?");
      }
    };
    fetchLinks();
  }, []); // The empty array ensures this runs only once

  // --- This function handles the form submission ---
  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setShortURL(null);

    if (!longUrl || !longUrl.startsWith('http')) {
      setError('Please enter a valid URL (e.g., https://www.google.com)');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/shorten', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ long_url: longUrl }),
      });

      if (!response.ok) {
        throw new Error('Something went wrong with the request.');
      }

      const data = await response.json();
      setShortURL(data); // Show the user the result of their submission

      // If a *new* link was created, add it to the top of our history list
      if (response.status === 201) {
        setLinks(prevLinks => [data, ...prevLinks]);
      }

    } catch (error) {
      setError(error.message || 'Failed to shorten URL. Please check if the backend is running.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>URL Shortener</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={longUrl}
            onChange={(e) => setLongUrl(e.target.value)}
            placeholder="Enter a long URL to shorten"
            className="url-input"
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Shortening...' : 'Shorten'}
          </button>
        </form>
        
        {error && <p className="error-message">{error}</p>}

        {shortURL && (
          <div className="result">
            <p>Your Link:</p>
            <a href={shortURL.short_url} target="_blank" rel="noopener noreferrer">
              {shortURL.short_url}
            </a>
          </div>
        )}

        {/* --- Link History Table --- */}
        <div className="history-container">
          <h2>Link History</h2>
          {links.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Original URL</th>
                  <th>Short URL</th>
                </tr>
              </thead>
              <tbody>
                {links.map((link) => (
                  <tr key={link.short_code}>
                    <td className="long-url-cell">{link.long_url}</td>
                    <td>
                      <a href={link.short_url} target="_blank" rel="noopener noreferrer">
                        {link.short_url}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No links shortened yet.</p>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;