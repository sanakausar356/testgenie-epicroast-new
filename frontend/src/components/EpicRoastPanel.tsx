import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { Zap, Download, Copy, Share2, CheckCircle, AlertCircle, Flame, Sparkles } from 'lucide-react'
import { generateRoast } from '../services/api'

interface EpicRoastPanelProps {
  sharedTicketNumber: string
  setSharedTicketNumber: (ticket: string) => void
  setIsLoading: (loading: boolean) => void
}

export const EpicRoastPanel: React.FC<EpicRoastPanelProps> = ({
  sharedTicketNumber,
  setSharedTicketNumber,
  setIsLoading
}) => {
  const [ticketNumber, setTicketNumber] = useState(sharedTicketNumber)
  const [ticketContent, setTicketContent] = useState('')
  const [theme, setTheme] = useState('default')
  const [level, setLevel] = useState('savage')
  const [results, setResults] = useState('')
  const [error, setError] = useState('')
  const [showSuccess, setShowSuccess] = useState(false)
  const [validationError, setValidationError] = useState('')
  
  const ticketInputRef = useRef<HTMLInputElement>(null)

  // Auto-focus first input on mount
  useEffect(() => {
    if (ticketInputRef.current) {
      ticketInputRef.current.focus()
    }
  }, [])

  // Update ticket number when shared ticket changes
  useEffect(() => {
    if (sharedTicketNumber && !ticketNumber) {
      setTicketNumber(sharedTicketNumber)
    }
  }, [sharedTicketNumber, ticketNumber])

  const validateInputs = () => {
    if (!ticketNumber && !ticketContent.trim()) {
      setValidationError('Please provide either a ticket number or ticket content')
      return false
    }
    setValidationError('')
    return true
  }

  const handleGenerate = async () => {
    if (!validateInputs()) return

    setIsLoading(true)
    setError('')
    setValidationError('')
    
    try {
      const response = await generateRoast({
        ticket_number: ticketNumber,
        ticket_content: ticketContent,
        theme,
        level
      })
      
      if (response.success) {
        setResults(response.data.roast)
        if (ticketNumber) {
          setSharedTicketNumber(ticketNumber)
        }
        setShowSuccess(true)
        setTimeout(() => setShowSuccess(false), 3000)
      } else {
        setError(response.error || 'Failed to generate roast')
      }
    } catch (err) {
      setError('An error occurred while generating roast')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(results)
      // Show success feedback
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleExport = () => {
    const blob = new Blob([results], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `epic-roast-${ticketNumber || 'manual'}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'light': return '🧂'
      case 'savage': return '🌶️'
      case 'extra_crispy': return '🔥'
      default: return '🌶️'
    }
  }

  const getThemeIcon = (theme: string) => {
    switch (theme) {
      case 'default': return '🎯'
      case 'pirate': return '🏴‍☠️'
      case 'shakespeare': return '📜'
      case 'genz': return '💅'
      default: return '🎯'
    }
  }

  const formatResults = (rawResults: string) => {
    return (
      <div className="prose prose-lg max-w-none">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-2xl font-bold text-secondary-700 mb-4 flex items-center">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl font-semibold text-secondary-600 mb-3 flex items-center">
                {children}
              </h2>
            ),
            p: ({ children }) => (
              <p className="text-gray-700 leading-relaxed mb-3">
                {children}
              </p>
            ),
            ul: ({ children }) => (
              <ul className="space-y-2 mb-4">
                {children}
              </ul>
            ),
            li: ({ children }) => (
              <li className="flex items-start space-x-2">
                <span className="text-secondary-500 mt-1">•</span>
                <span className="text-gray-700">{children}</span>
              </li>
            ),
            strong: ({ children }) => (
              <strong className="font-bold text-secondary-700">
                {children}
              </strong>
            ),
            em: ({ children }) => (
              <em className="italic text-gray-600">
                {children}
              </em>
            )
          }}
        >
          {rawResults}
        </ReactMarkdown>
        
        {/* Action Items Section */}
        <div className="action-items mt-6">
          <h3 className="text-lg font-bold text-orange-800 mb-3 flex items-center">
            ⛱️ Action Items Summary
          </h3>
          <div className="space-y-2">
            <div className="action-item">
              <span className="text-orange-600 font-medium">Scrum Master</span>
              <span className="text-gray-600">→</span>
              <span className="text-gray-700">Facilitate retrospective session</span>
            </div>
            <div className="action-item">
              <span className="text-orange-600 font-medium">Developer</span>
              <span className="text-gray-600">→</span>
              <span className="text-gray-700">Review and refactor code based on feedback</span>
            </div>
            <div className="action-item">
              <span className="text-orange-600 font-medium">Product Owner</span>
              <span className="text-gray-600">→</span>
              <span className="text-gray-700">Clarify acceptance criteria for better quality</span>
            </div>
            <div className="action-item">
              <span className="text-orange-600 font-medium">QA</span>
              <span className="text-gray-600">→</span>
              <span className="text-gray-700">Run regression tests to ensure stability</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <span className="text-2xl">🔥</span>
        <h2 className="text-xl font-semibold text-gray-900">Epic Roast</h2>
        <span className="text-sm text-gray-500">Create Hilarious Roasts</span>
      </div>

      {/* Input Section */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Jira Ticket Number
          </label>
          <input
            ref={ticketInputRef}
            type="text"
            value={ticketNumber}
            onChange={(e) => {
              setTicketNumber(e.target.value.toUpperCase())
              setValidationError('')
            }}
            placeholder="e.g., ODCD-33741"
            className={`beach-input w-full ${validationError && !ticketNumber && !ticketContent.trim() ? 'border-red-300 focus:border-red-500' : ''}`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Enter a Jira ticket number to automatically fetch ticket content
          </p>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">OR</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Paste Ticket Content
          </label>
          <textarea
            value={ticketContent}
            onChange={(e) => {
              setTicketContent(e.target.value)
              setValidationError('')
            }}
            placeholder="Paste the ticket content to roast... e.g., 'As a user, I want to be able to click a button'"
            rows={4}
            className={`beach-input w-full resize-none ${validationError && !ticketNumber && !ticketContent.trim() ? 'border-red-300 focus:border-red-500' : ''}`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Paste the ticket description, acceptance criteria, or any content to roast
          </p>
        </div>

        {/* Roast Options - Reordered for better flow */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Theme {getThemeIcon(theme)}
            </label>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="beach-input w-full"
            >
              <option value="default">🎯 Default</option>
              <option value="pirate">🏴‍☠️ Pirate</option>
              <option value="shakespeare">📜 Shakespeare</option>
              <option value="genz">💅 Gen Z</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Roast Level {getLevelIcon(level)}
            </label>
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="beach-input w-full"
            >
              <option value="light">🧂 Light</option>
              <option value="savage">🌶️ Savage</option>
              <option value="extra_crispy">🔥 Extra Crispy</option>
            </select>
          </div>
        </div>

        {/* Validation Error */}
        {validationError && (
          <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <p className="text-red-700 text-sm">{validationError}</p>
          </div>
        )}

        <button
          onClick={handleGenerate}
          className="beach-button w-full flex items-center justify-center space-x-2"
        >
          <Zap className="h-4 w-4" />
          <span>Generate Epic Roast</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Success Animation */}
      {showSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg animate-pulse">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <p className="text-green-700 text-sm">Epic roast generated successfully!</p>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Epic Roast</h3>
            <div className="flex space-x-2">
              <button
                onClick={handleCopy}
                className="btn-outline flex items-center space-x-1 text-sm"
                title="Copy to clipboard"
              >
                <Copy className="h-4 w-4" />
                <span>Copy</span>
              </button>
              <button
                onClick={handleExport}
                className="btn-outline flex items-center space-x-1 text-sm"
                title="Download as markdown"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </button>
              <button 
                className="btn-outline flex items-center space-x-1 text-sm"
                title="Share to Teams"
              >
                <Share2 className="h-4 w-4" />
                <span>Teams</span>
              </button>
            </div>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-6 max-h-96 overflow-y-auto shadow-sm">
            <div className="prose prose-sm max-w-none">
              {formatResults(results)}
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 