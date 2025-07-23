import React, { useState } from 'react'
import { Sparkles, Download, Copy, Share2 } from 'lucide-react'
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

  const handleGenerate = async () => {
    if (!ticketNumber && !acceptanceCriteria.trim()) {
      setError('Please provide either a ticket number or acceptance criteria')
      return
    }

    setIsLoading(true)
    setError('')
    
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
      } else {
        setError(response.error || 'Failed to generate test scenarios')
      }
    } catch (err) {
      setError('An error occurred while generating test scenarios')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(results)
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

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <Sparkles className="h-6 w-6 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">TestGenie</h2>
      </div>

      {/* Input Section */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Jira Ticket Number
          </label>
          <input
            type="text"
            value={ticketNumber}
            onChange={(e) => setTicketNumber(e.target.value.toUpperCase())}
            placeholder="e.g., ODCD-33741"
            className="input-field"
          />
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
            onChange={(e) => setAcceptanceCriteria(e.target.value)}
            placeholder="Paste your acceptance criteria here..."
            rows={4}
            className="input-field resize-none"
          />
        </div>

        <button
          onClick={handleGenerate}
          className="btn-primary w-full flex items-center justify-center space-x-2"
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

      {/* Results Section */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Generated Test Scenarios</h3>
            <div className="flex space-x-2">
              <button
                onClick={handleCopy}
                className="btn-outline flex items-center space-x-1 text-sm"
              >
                <Copy className="h-4 w-4" />
                <span>Copy</span>
              </button>
              <button
                onClick={handleExport}
                className="btn-outline flex items-center space-x-1 text-sm"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </button>
              <button className="btn-outline flex items-center space-x-1 text-sm">
                <Share2 className="h-4 w-4" />
                <span>Teams</span>
              </button>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
              {results}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
} 