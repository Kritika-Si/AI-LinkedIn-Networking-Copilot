
import { useState } from 'react'
import './Auth.css'

const API_BASE_URL = 'http://localhost:8000'

function Auth({ onAuthenticated }) {
  const [isLogin, setIsLogin] = useState(true)
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!isLogin && fullName.trim().length < 2) {
      setError('Please enter your full name.')
      return
    }

    if (!email.trim()) {
      setError('Please enter your email address.')
      return
    }

    if (password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    setIsLoading(true)

    try {
      const endpoint = isLogin ? 'login' : 'register'

      const payload = isLogin
        ? { email: email.trim(), password }
        : {
            full_name: fullName.trim(),
            email: email.trim(),
            password,
          }

      const response = await fetch(
        `${API_BASE_URL}/api/auth/${endpoint}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(payload),
        }
      )

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          result.detail || 'Authentication failed. Please try again.'
        )
      }

      setPassword('')
      onAuthenticated(result)
    } catch (requestError) {
      setError(
        requestError.message ||
          'Unable to connect to the server. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const switchMode = () => {
    setIsLogin((previous) => !previous)
    setError('')
    setPassword('')
  }

  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand">
          <div className="auth-brand-icon">N</div>
          <div>
            <h1>Netwise<span>.</span></h1>
            <p>AI NETWORKING COPILOT</p>
          </div>
        </div>

        <div className="auth-brand-content">
          <span className="auth-eyebrow">YOUR PROFESSIONAL JOURNEY</span>
          <h2>
            Build meaningful
            <span> professional connections.</span>
          </h2>
          <p>
            Discover relevant professionals, create personalized
            networking messages, and manage your career connections
            in one place.
          </p>

          <div className="auth-feature-list">
            <div><span>✦</span> Personalized connection recommendations</div>
            <div><span>✦</span> AI-assisted networking messages</div>
            <div><span>✦</span> Your own professional workspace</div>
          </div>
        </div>

        <p className="auth-brand-footer">
          © 2026 Netwise AI. Built for meaningful connections.
        </p>
      </section>

      <section className="auth-form-panel">
        <div className="auth-form-container">
          <div className="auth-mobile-brand">
            <div className="auth-brand-icon">N</div>
            <h1>Netwise<span>.</span></h1>
          </div>

          <span className="auth-eyebrow">
            {isLogin ? 'WELCOME BACK' : 'GET STARTED'}
          </span>

          <h2>{isLogin ? 'Sign in to Netwise' : 'Create your account'}</h2>

          <p className="auth-description">
            {isLogin
              ? 'Enter your account details to continue.'
              : 'Create your personal professional networking workspace.'}
          </p>

          <form onSubmit={handleSubmit} className="auth-form">
            {!isLogin && (
              <div className="auth-field">
                <label htmlFor="authFullName">Full name</label>
                <input
                  id="authFullName"
                  type="text"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  minLength={2}
                  maxLength={150}
                  autoComplete="name"
                  required
                />
              </div>
            )}

            <div className="auth-field">
              <label htmlFor="authEmail">Email address</label>
              <input
                id="authEmail"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="authPassword">Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="authPassword"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={8}
                  maxLength={128}
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  required
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword((previous) => !previous)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              {!isLogin && (
                <small className="auth-hint">
                  Use at least 8 characters.
                </small>
              )}
            </div>

            {error && <div className="auth-error" role="alert">{error}</div>}

            <button
              type="submit"
              className="auth-submit-button"
              disabled={isLoading}
            >
              {isLoading
                ? 'Please wait...'
                : isLogin
                  ? 'Sign in'
                  : 'Create account'}
            </button>
          </form>

          <div className="auth-switch">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}
            <button type="button" onClick={switchMode}>
              {isLogin ? 'Create account' : 'Sign in'}
            </button>
          </div>

          <p className="auth-security-note">
            Your account is protected with secure authentication.
          </p>
        </div>
      </section>
    </main>
  )
}

export default Auth
