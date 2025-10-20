import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { Zap, Download, Copy, Share2, CheckCircle, AlertCircle, Search, Sparkles } from 'lucide-react'
import { generateGroom } from '../services/api'

interface GroomRoomPanelProps {
  sharedTicketNumber: string
  setSharedTicketNumber: (ticket: string) => void
  setIsLoading: (loading: boolean) => void
}

export const GroomRoomPanel: React.FC<GroomRoomPanelProps> = ({
  sharedTicketNumber,
  setSharedTicketNumber,
  setIsLoading
}) => {
  const [ticketNumber, setTicketNumber] = useState(sharedTicketNumber)
  const [ticketContent, setTicketContent] = useState('')
  const [level, setLevel] = useState('updated')
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
      console.log('Calling generateGroom with:', { ticket_number: ticketNumber, ticket_content: ticketContent, level })
      
      const response = await generateGroom({
        ticket_number: ticketNumber,
        ticket_content: ticketContent,
        level
      })
      
      console.log('Response received:', response)
      console.log('Response success:', response.success)
      console.log('Response data:', response.data)
      console.log('Groom content length:', response.data?.groom?.length || 0)
      console.log('Groom content preview:', response.data?.groom?.substring(0, 200) || 'No content')
      
      if (response.success) {
        console.log('Setting results to:', response.data.groom)
        setResults(response.data.groom)
        if (ticketNumber) {
          setSharedTicketNumber(ticketNumber)
        }
        setShowSuccess(true)
        setTimeout(() => setShowSuccess(false), 3000)
      } else {
        console.log('Error in response:', response.error)
        setError(response.error || 'Failed to generate groom analysis')
      }
    } catch (err) {
      console.error('Exception in handleGenerate:', err)
      setError('An error occurred while generating groom analysis')
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
    a.download = `groom-analysis-${ticketNumber || 'manual'}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'updated': return '🔄'
      case 'strict': return '🔒'
      case 'light': return '💡'
      case 'default': return '📊'
      case 'insight': return '🔍'
      case 'deep_dive': return '🔬'
      case 'actionable': return '⚡'
      case 'summary': return '📝'
      default: return '📊'
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
        

      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <span className="text-2xl">🧹</span>
        <h2 className="text-xl font-semibold text-gray-900">Groom Room</h2>
        <span className="text-sm text-gray-500">Groom Analysis</span>
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
            placeholder="Paste the ticket content to analyze... e.g., 'As a user, I want to be able to click a button'"
            rows={4}
            className={`beach-input w-full resize-none ${validationError && !ticketNumber && !ticketContent.trim() ? 'border-red-300 focus:border-red-500' : ''}`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Paste the ticket description, acceptance criteria, or any content to analyze
          </p>
        </div>

        {/* Groom Level Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Groom Level {getLevelIcon(level)}
          </label>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="beach-input w-full"
          >
            <option value="updated">🔄 Updated (QA Refinement)</option>
            <option value="strict">🔒 Strict</option>
            <option value="light">💡 Light</option>
            <option value="default">📊 Default</option>
            <option value="insight">🔍 Insight</option>
            <option value="deep_dive">🔬 Deep Dive</option>
            <option value="actionable">⚡ Actionable</option>
            <option value="summary">📝 Summary</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            {level === 'updated' && 'QA Refinement Assistant: concise, story-specific, refinement-ready analysis'}
            {level === 'strict' && 'Zero tolerance: enforce ALL Definition of Ready requirements'}
            {level === 'light' && 'Flexible approach: focus on critical elements with reasonable flexibility'}
            {level === 'default' && 'Balanced mix of feedback and gentle tone'}
            {level === 'insight' && 'Focused analysis: missing details and implied risks'}
            {level === 'deep_dive' && 'Thorough analysis: edge cases, validations, compliance'}
            {level === 'actionable' && 'Direct mapping to user stories with next steps'}
            {level === 'summary' && 'Ultra-brief: 3 key gaps and 2 critical suggestions'}
          </p>
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
          <Search className="h-4 w-4" />
          <span>Generate Groom Analysis</span>
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
            <p className="text-green-700 text-sm">Groom analysis generated successfully!</p>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Groom Analysis</h3>
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
          
          <div className="bg-white border border-gray-200 rounded-lg p-6 max-h-[600px] overflow-y-auto shadow-sm">
            <div className="prose prose-sm max-w-none">
              {formatResults(results)}
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 