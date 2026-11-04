
import { useState, useEffect } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

const defaultPerson = {
  name: 'Professional',
  role: 'Professional',
  company: 'Company',
  match: 0,
  initials: 'P',
  color: 'purple',
  matched_skills: [],
  reason: '',
}

function App() {
  const [activePage, setActivePage] = useState('Dashboard')

  // Profile states
  const [profile, setProfile] = useState('')
  const [careerGoal, setCareerGoal] = useState('')
  const [profileId, setProfileId] = useState(null)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [profileStatus, setProfileStatus] = useState('')
  const [profileStatusType, setProfileStatusType] = useState('')

  // Recommendation states
  const [connections, setConnections] = useState([])
  const [isLoadingConnections, setIsLoadingConnections] = useState(true)
  const [recommendationError, setRecommendationError] = useState('')

  // Search and message states
  const [search, setSearch] = useState('')
  const [selectedPerson, setSelectedPerson] = useState(defaultPerson)
  const [message, setMessage] = useState('')

  // Load saved profile information
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/profiles/`)

        if (!response.ok) {
          throw new Error('Unable to load profile information.')
        }

        const profiles = await response.json()

        if (profiles.length > 0) {
          const savedProfile = profiles[0]

          setProfileId(savedProfile.id)
          setProfile(savedProfile.linkedin_profile || '')
          setCareerGoal(savedProfile.career_goals || '')
        }
      } catch (error) {
        console.error('Profile loading error:', error)
        setProfileStatus(
          'Could not load profile. Please check the backend connection.'
        )
        setProfileStatusType('error')
      } finally {
        setIsLoadingProfile(false)
      }
    }

    loadProfile()
  }, [])

  // Fetch recommendations from FastAPI
  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        setIsLoadingConnections(true)
        setRecommendationError('')

        const response = await fetch(
          `${API_BASE_URL}/api/recommendations/`
        )

        const result = await response.json()

        if (!response.ok) {
          throw new Error(
            result.detail || 'Unable to load recommendations.'
          )
        }

        const fetchedConnections = result.recommendations || []

        setConnections(fetchedConnections)

        if (fetchedConnections.length > 0) {
          setSelectedPerson(fetchedConnections[0])
        }
      } catch (error) {
        console.error('Recommendation loading error:', error)
        setRecommendationError(
          error.message || 'Could not connect to the recommendations API.'
        )
      } finally {
        setIsLoadingConnections(false)
      }
    }

    loadRecommendations()
  }, [])

  // Save a new profile or update an existing profile
  const handleSaveProfile = async () => {
    if (!profile.trim()) {
      setProfileStatus('Please enter your LinkedIn profile information.')
      setProfileStatusType('error')
      return
    }

    setIsSavingProfile(true)
    setProfileStatus('')

    const profileData = {
      linkedin_profile: profile,
      career_goals: careerGoal,
    }

    try {
      const isUpdating = profileId !== null

      const response = await fetch(
        isUpdating
          ? `${API_BASE_URL}/api/profiles/${profileId}`
          : `${API_BASE_URL}/api/profiles/`,
        {
          method: isUpdating ? 'PUT' : 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profileData),
        }
      )

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          result.detail || 'Something went wrong while saving your profile.'
        )
      }

      setProfileId(result.id)
      setProfileStatus(
        isUpdating
          ? 'Profile updated successfully!'
          : 'Profile saved successfully!'
      )
      setProfileStatusType('success')

      // Refresh recommendations after saving profile changes
      const recommendationResponse = await fetch(
        `${API_BASE_URL}/api/recommendations/`
      )

      const recommendationResult = await recommendationResponse.json()

      if (!recommendationResponse.ok) {
        throw new Error(
          recommendationResult.detail || 'Profile saved, but recommendations could not be refreshed.'
        )
      }

      const updatedConnections = recommendationResult.recommendations || []

      setConnections(updatedConnections)

      if (updatedConnections.length > 0) {
        setSelectedPerson(updatedConnections[0])
      }

      setRecommendationError('')
    } catch (error) {
      console.error('Profile saving error:', error)
      setProfileStatus(error.message || 'Unable to save your profile.')
      setProfileStatusType('error')
    } finally {
      setIsSavingProfile(false)
    }
  }

  const navigation = [
    { name: 'Dashboard', icon: '▦' },
    { name: 'My Profile', icon: '◉' },
    { name: 'Find Connections', icon: '◎' },
    { name: 'Message Generator', icon: '✉' },
    { name: 'Activity', icon: '↗' },
  ]

  // Search through API recommendations
  const filteredConnections = connections.filter((person) =>
    `${person.name} ${person.role} ${person.company}`
      .toLowerCase()
      .includes(search.toLowerCase())
  )

  const handleNavigation = (page) => {
    setActivePage(page)
  }

  // Generate a message for the selected professional
  const handleSelectPerson = (person) => {
    setSelectedPerson(person)

    setMessage(
      `Hi ${person.name.split(' ')[0]}, I came across your professional profile at ${person.company} and was impressed by your experience. I'm a Computer Science student specializing in AI and Data Science, and I'm exploring opportunities in this field. I'd love to connect and learn from your experience. Thank you!`
    )

    setActivePage('Message Generator')
  }

  // Reusable recommendation card
  const renderConnection = (person) => (
    <div className="connection-row" key={person.name}>
      <div className={`person-avatar ${person.color || 'purple'}`}>
        {person.initials || person.name?.charAt(0) || 'P'}
      </div>

      <div className="person-details">
        <strong>{person.name}</strong>
        <span>{person.role} · {person.company}</span>

        {person.matched_skills?.length > 0 && (
          <small>
            Matched skills: {person.matched_skills.join(', ')}
          </small>
        )}

        {person.reason && (
          <small>{person.reason}</small>
        )}
      </div>

      <div className="match-score">
        <strong>{person.match}%</strong>
        <span>Match</span>
      </div>

      <button
        className="connect-button"
        onClick={() => handleSelectPerson(person)}
      >
        Generate message
      </button>
    </div>
  )

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">N</div>
          <div>
            <h2>Netwise<span>.</span></h2>
            <p>NETWORKING COPILOT</p>
          </div>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? 'active' : ''}`}
              onClick={() => handleNavigation(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}

              {item.name === 'Find Connections' && (
                <span className="nav-count">{connections.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">✦</div>
            <h3>AI-powered networking</h3>
            <p>
              Build meaningful professional connections with smarter insights.
            </p>
          </div>

          <div className="user-profile">
            <div className="user-avatar">KK</div>
            <div className="user-info">
              <strong>Your Workspace</strong>
              <span>Free Plan</span>
            </div>
            <span className="more-icon">···</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="status-indicator">
              <span></span> AI Assistant Ready
            </span>

            <button className="notification-button" aria-label="Notifications">
              ♧
              <i></i>
            </button>

            <div className="top-avatar">KK</div>
          </div>
        </header>

        <div className="page-container">
          {/* DASHBOARD */}
          {activePage === 'Dashboard' && (
            <>
              <section className="welcome-section">
                <div>
                  <p className="eyebrow">YOUR PROFESSIONAL GROWTH</p>
                  <h1>Good to see you! <span>✦</span></h1>
                  <p className="welcome-description">
                    Your AI networking assistant is ready to help you build
                    meaningful connections.
                  </p>
                </div>

                <button
                  className="primary-button"
                  onClick={() => setActivePage('Find Connections')}
                >
                  <span>✦</span> Find connections
                </button>
              </section>

              <section className="stats-grid">
                <div className="stat-card">
                  <div className="stat-top">
                    <span>Connections discovered</span>
                    <span className="stat-icon lavender">◎</span>
                  </div>
                  <h2>{connections.length}</h2>
                  <p>Based on your saved profile</p>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <span>Messages generated</span>
                    <span className="stat-icon blue-bg">✉</span>
                  </div>
                  <h2>0</h2>
                  <p>Start creating messages</p>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <span>Connection requests</span>
                    <span className="stat-icon green-bg">↗</span>
                  </div>
                  <h2>0</h2>
                  <p>Keep building relationships</p>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <span>Profile completeness</span>
                    <span className="stat-icon orange-bg">◈</span>
                  </div>
                  <h2>{profile.trim() ? '75%' : '0%'}</h2>
                  <p>{profile.trim() ? 'Profile information added' : 'Add your profile details'}</p>
                </div>
              </section>

              <section className="content-grid">
                <div className="panel recommendations-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Recommended connections</h2>
                      <p>People who match your career interests</p>
                    </div>

                    <button
                      className="text-button"
                      onClick={() => setActivePage('Find Connections')}
                    >
                      View all →
                    </button>
                  </div>

                  <div className="connection-list">
                    {isLoadingConnections ? (
                      <p className="empty-state">Loading recommendations...</p>
                    ) : recommendationError ? (
                      <p className="empty-state">{recommendationError}</p>
                    ) : connections.length > 0 ? (
                      connections.map((person) => renderConnection(person))
                    ) : (
                      <p className="empty-state">
                        No recommendations available. Save your profile first.
                      </p>
                    )}
                  </div>
                </div>

                <div className="panel activity-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Recent activity</h2>
                      <p>Your networking progress</p>
                    </div>
                  </div>

                  <div className="activity-list">
                    <div className="activity-item">
                      <span className="activity-dot purple-dot"></span>
                      <div>
                        <strong>Recommendations loaded</strong>
                        <p>{connections.length} sample professionals found</p>
                        <small>Today</small>
                      </div>
                    </div>

                    <div className="activity-item">
                      <span className="activity-dot blue-dot"></span>
                      <div>
                        <strong>Profile analysis</strong>
                        <p>Your saved profile is used for matching</p>
                        <small>Today</small>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section className="quick-start panel">
                <div className="quick-start-icon">✦</div>
                <div>
                  <h2>Ready to grow your network?</h2>
                  <p>Start by adding your LinkedIn profile and career goals.</p>
                </div>

                <button
                  className="primary-button"
                  onClick={() => setActivePage('My Profile')}
                >
                  Set up my profile →
                </button>
              </section>
            </>
          )}

          {/* MY PROFILE */}
          {activePage === 'My Profile' && (
            <section className="inner-page">
              <p className="eyebrow">PERSONAL INFORMATION</p>
              <h1>My Profile</h1>

              <p className="welcome-description">
                Add your LinkedIn details and career goals to help the AI
                understand your professional interests.
              </p>

              <div className="panel form-panel">
                <h2>LinkedIn profile details</h2>

                <p className="form-description">
                  Copy and paste your profile information below.
                </p>

                <label htmlFor="profile">Profile information</label>

                <textarea
                  id="profile"
                  rows="8"
                  value={profile}
                  onChange={(e) => setProfile(e.target.value)}
                  placeholder="Paste your LinkedIn headline, About section, skills, education, and experience..."
                />

                <label htmlFor="careerGoal">Career goals</label>

                <textarea
                  id="careerGoal"
                  rows="4"
                  value={careerGoal}
                  onChange={(e) => setCareerGoal(e.target.value)}
                  placeholder="Example: Looking for AI/ML internships and fresher roles in software development..."
                />

                <button
                  className="primary-button"
                  onClick={handleSaveProfile}
                  disabled={isSavingProfile || isLoadingProfile}
                >
                  {isLoadingProfile
                    ? 'Loading profile...'
                    : isSavingProfile
                      ? 'Saving...'
                      : profileId
                        ? 'Update profile details'
                        : 'Save profile details'}
                </button>

                {profileStatus && (
                  <p
                    role="status"
                    style={{
                      marginTop: '14px',
                      color: profileStatusType === 'success' ? 'green' : 'red',
                    }}
                  >
                    {profileStatus}
                  </p>
                )}
              </div>
            </section>
          )}

          {/* FIND CONNECTIONS */}
          {activePage === 'Find Connections' && (
            <section className="inner-page">
              <p className="eyebrow">EXPAND YOUR NETWORK</p>
              <h1>Find connections</h1>

              <p className="welcome-description">
                Discover professionals who align with your career goals.
              </p>

              <div className="search-box">
                <span>⌕</span>

                <input
                  type="text"
                  placeholder="Search by name, role or company..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

              <div className="panel connection-results">
                <div className="panel-heading">
                  <div>
                    <h2>Suggested professionals</h2>
                    <p>Recommendations generated from your saved profile</p>
                  </div>

                  <span className="result-count">
                    {isLoadingConnections ? 'Loading...' : `${filteredConnections.length} results`}
                  </span>
                </div>

                {isLoadingConnections ? (
                  <p className="empty-state">Loading recommendations...</p>
                ) : recommendationError ? (
                  <p className="empty-state">{recommendationError}</p>
                ) : (
                  <>
                    {filteredConnections.map((person) =>
                      renderConnection(person)
                    )}

                    {filteredConnections.length === 0 && (
                      <p className="empty-state">
                        No matching professionals found.
                      </p>
                    )}
                  </>
                )}

                <p className="disclaimer">
                  Demo recommendations use fictional sample professionals.
                  Match scores are calculated by a basic skill-matching algorithm,
                  not live LinkedIn data.
                </p>
              </div>
            </section>
          )}

          {/* MESSAGE GENERATOR */}
          {activePage === 'Message Generator' && (
            <section className="inner-page">
              <p className="eyebrow">PERSONALIZED OUTREACH</p>
              <h1>Message Generator</h1>

              <p className="welcome-description">
                Create thoughtful connection messages for your professional
                networking.
              </p>

              <div className="panel message-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Connection request message</h2>
                    <p>
                      Message for {selectedPerson.name} · {selectedPerson.company}
                    </p>
                  </div>

                  <span className="ai-tag">✦ AI ASSISTED</span>
                </div>

                <textarea
                  className="message-editor"
                  rows="8"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Select a professional from Find Connections to generate a message..."
                />

                <div className="message-footer">
                  <span>{message.length} characters</span>

                  <button
                    className="primary-button"
                    disabled={!message.trim()}
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(message)
                        alert('Message copied to clipboard!')
                      } catch {
                        alert('Unable to copy. Please copy the message manually.')
                      }
                    }}
                  >
                    Copy message
                  </button>
                </div>

                <p className="disclaimer">
                  Review and personalize the message before sending it through
                  LinkedIn.
                </p>
              </div>
            </section>
          )}

          {/* ACTIVITY */}
          {activePage === 'Activity' && (
            <section className="inner-page">
              <p className="eyebrow">NETWORKING OVERVIEW</p>
              <h1>Activity</h1>

              <p className="welcome-description">
                Keep track of your professional networking journey.
              </p>

              <div className="stats-grid">
                <div className="stat-card">
                  <span>Connections discovered</span>
                  <h2>{connections.length}</h2>
                </div>

                <div className="stat-card">
                  <span>Messages generated</span>
                  <h2>0</h2>
                </div>

                <div className="stat-card">
                  <span>Requests sent</span>
                  <h2>0</h2>
                </div>

                <div className="stat-card">
                  <span>Pending responses</span>
                  <h2>0</h2>
                </div>
              </div>

              <div className="panel activity-panel full-panel">
                <h2>Networking timeline</h2>

                <p className="form-description">
                  Your recent networking actions will appear here.
                </p>

                <div className="activity-list">
                  <div className="activity-item">
                    <span className="activity-dot purple-dot"></span>
                    <div>
                      <strong>Connection recommendations reviewed</strong>
                      <p>{connections.length} professionals matched with your interests</p>
                      <small>Today</small>
                    </div>
                  </div>

                  <div className="activity-item">
                    <span className="activity-dot blue-dot"></span>
                    <div>
                      <strong>Personalized message prepared</strong>
                      <p>Connection message ready for review</p>
                      <small>Today</small>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          <footer className="footer">
            <span>© 2026 Netwise AI</span>
            <span>Built for meaningful professional connections.</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App
