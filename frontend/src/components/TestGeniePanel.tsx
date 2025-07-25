import React, { useState, useEffect, useRef } from 'react'
import { Sparkles, Download, Copy, Share2, CheckCircle, AlertCircle } from 'lucide-react'
import { generateTestScenarios } from '../services/api'

interface TestGeniePanelProps {
  sharedTicketNumber: string
  setSharedTicketNumber: (ticket: string) => void
  setIsLoading: (loading: boolean) => void
}

export const TestGeniePanel: React.FC<TestGeniePanelProps> = ({
  sharedTicketNumber,
  setSharedTicketNumber,
  setIsLoading
}) => {
  const [ticketNumber, setTicketNumber] = useState(sharedTicketNumber)
  const [acceptanceCriteria, setAcceptanceCriteria] = useState('')
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
    if (!ticketNumber && !acceptanceCriteria.trim()) {
      setValidationError('Please provide either a ticket number or acceptance criteria')
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
      const response = await generateTestScenarios({
        ticket_number: ticketNumber,
        acceptance_criteria: acceptanceCriteria
      })
      
      if (response.success) {
        setResults(response.data.scenarios)
        if (ticketNumber) {
          setSharedTicketNumber(ticketNumber)
        }
        setShowSuccess(true)
        setTimeout(() => setShowSuccess(false), 3000)
      } else {
        setError(response.error || 'Failed to generate test scenarios')
      }
    } catch (err) {
      setError('An error occurred while generating test scenarios')
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
    a.download = `test-scenarios-${ticketNumber || 'manual'}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const formatResults = (rawResults: string) => {
    // Split by sections and format with better styling
    const sections = rawResults.split(/(?=^#+ )/m)
    return sections.map((section, index) => {
      const lines = section.trim().split('\n')
      const title = lines[0]
      const content = lines.slice(1).join('\n')
      
      return (
        <div key={index} className="mb-6 last:mb-0">
          <h4 className="text-lg font-bold text-primary-700 mb-3 border-b border-primary-200 pb-2">
            {title.replace(/^#+\s*/, '')}
          </h4>
          <div className="space-y-2">
            {content.split('\n').map((line, lineIndex) => {
              if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                return (
                  <div key={lineIndex} className="flex items-start space-x-2 pl-4">
                    <span className="text-primary-500 mt-1">•</span>
                    <span className="text-gray-700">{line.replace(/^[-*]\s*/, '')}</span>
                  </div>
                )
              }
              if (line.trim()) {
                return (
                  <p key={lineIndex} className="text-gray-700 leading-relaxed">
                    {line}
                  </p>
                )
              }
              return null
            })}
          </div>
        </div>
      )
    })
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <span className="text-3xl">🧙‍♂️</span>
        <h2 className="text-xl font-semibold text-gray-900">Test Genie</h2>
        <span className="text-sm text-gray-500">✨ Generate Test Scenarios</span>
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
            className={`input-field ${validationError && !ticketNumber && !acceptanceCriteria.trim() ? 'border-red-300 focus:border-red-500' : ''}`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Enter a Jira ticket number to automatically fetch acceptance criteria
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
            Paste Acceptance Criteria
          </label>
          <textarea
            value={acceptanceCriteria}
            onChange={(e) => {
              setAcceptanceCriteria(e.target.value)
              setValidationError('')
            }}
            placeholder="Paste your acceptance criteria here... e.g., 'User should be able to reset password via email link'"
            rows={4}
            className={`input-field resize-none ${validationError && !ticketNumber && !acceptanceCriteria.trim() ? 'border-red-300 focus:border-red-500' : ''}`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Describe the feature requirements or paste existing acceptance criteria
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
          className="btn-primary w-full flex items-center justify-center space-x-2 py-3"
        >
          <Sparkles className="h-4 w-4" />
          <span>Generate Test Scenarios</span>
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
            <p className="text-green-700 text-sm">Test scenarios generated successfully!</p>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Generated Test Scenarios</h3>
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