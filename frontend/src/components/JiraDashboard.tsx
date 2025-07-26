import React, { useState, useEffect } from 'react'
import { Search, Filter, RefreshCw, ExternalLink } from 'lucide-react'

interface JiraCard {
  key: string
  summary: string
  status: string
  priority: string
  assignee?: string
  project: string
  issueType: string
  created: string
}

interface JiraDashboardProps {
  onSelectTicket: (ticketKey: string) => void
}

export const JiraDashboard: React.FC<JiraDashboardProps> = ({ onSelectTicket }) => {
  const [cards, setCards] = useState<JiraCard[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProject, setSelectedProject] = useState('all')
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  const projects = [
    { key: 'all', name: 'All Projects' },
    { key: 'ODCD', name: 'ODCD - Odyssey Continuous Delivery' },
    { key: 'ODCD-EVEREST', name: 'ODCD - Everest' },
    { key: 'EVEREST-PWA', name: 'Everest - PWA Kit Upgrade Project' },
    { key: 'BATMAN', name: 'The Batman' },
    { key: 'ODCD-SILVER', name: 'ODCD - Silver Surfers Scrum' }
  ]

  // Mock data for demonstration - replace with actual Jira API calls
  const mockCards: JiraCard[] = [
    {
      key: 'ODCD-33741',
      summary: 'Implement user authentication flow',
      status: 'Ready to Groom',
      priority: 'High',
      assignee: 'John Doe',
      project: 'ODCD',
      issueType: 'Story',
      created: '2024-01-15'
    },
    {
      key: 'ODCD-33742',
      summary: 'Add payment gateway integration',
      status: 'Ready to Groom',
      priority: 'Medium',
      assignee: 'Jane Smith',
      project: 'ODCD',
      issueType: 'Story',
      created: '2024-01-16'
    },
    {
      key: 'EVEREST-1234',
      summary: 'Upgrade PWA Kit to latest version',
      status: 'Ready to Groom',
      priority: 'High',
      assignee: 'Mike Johnson',
      project: 'EVEREST-PWA',
      issueType: 'Epic',
      created: '2024-01-14'
    },
    {
      key: 'BATMAN-5678',
      summary: 'Implement dark mode feature',
      status: 'Ready to Groom',
      priority: 'Low',
      assignee: 'Sarah Wilson',
      project: 'BATMAN',
      issueType: 'Story',
      created: '2024-01-17'
    },
    {
      key: 'ODCD-33743',
      summary: 'Optimize database queries',
      status: 'Ready to Groom',
      priority: 'High',
      assignee: 'Alex Brown',
      project: 'ODCD-SILVER',
      issueType: 'Task',
      created: '2024-01-18'
    }
  ]

  const fetchJiraCards = async () => {
    setLoading(true)
    setError('')
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Filter by selected project
      let filteredCards = mockCards
      if (selectedProject !== 'all') {
        filteredCards = mockCards.filter(card => card.project === selectedProject)
      }
      
      setCards(filteredCards)
      setLastRefresh(new Date())
    } catch (err) {
      setError('Failed to fetch Jira cards')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJiraCards()
  }, [selectedProject])

  const filteredCards = cards.filter(card =>
    card.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (card.assignee && card.assignee.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getIssueTypeIcon = (issueType: string) => {
    switch (issueType.toLowerCase()) {
      case 'story': return '📖'
      case 'epic': return '📚'
      case 'task': return '✅'
      case 'bug': return '🐛'
      default: return '📋'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">📊</span>
          <h2 className="text-xl font-semibold text-gray-900">Jira Dashboard</h2>
          <span className="text-sm text-gray-500">Ready to Groom Cards</span>
        </div>
        <button
          onClick={fetchJiraCards}
          disabled={loading}
          className="beach-button flex items-center space-x-2"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Cards
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by key, summary, or assignee..."
              className="beach-input w-full pl-10"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Project Filter
          </label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="beach-input w-full"
          >
            {projects.map(project => (
              <option key={project.key} value={project.key}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Last Refresh Info */}
      {lastRefresh && (
        <div className="text-xs text-gray-500 mb-4">
          Last refreshed: {lastRefresh.toLocaleTimeString()}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-full flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
          </div>
        ) : filteredCards.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            No Ready to Groom cards found
          </div>
        ) : (
          filteredCards.map((card) => (
            <div
              key={card.key}
              className="bg-white/80 backdrop-blur-sm rounded-xl border border-cyan-200/50 p-4 hover:shadow-lg transition-all duration-200 cursor-pointer group"
              onClick={() => onSelectTicket(card.key)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getIssueTypeIcon(card.issueType)}</span>
                  <span className="font-mono text-sm text-gray-600">{card.key}</span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(card.priority)}`}>
                  {card.priority}
                </span>
              </div>
              
              <h3 className="font-medium text-gray-900 mb-2 group-hover:text-cyan-600 transition-colors">
                {card.summary}
              </h3>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-4">
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {card.project}
                  </span>
                  <span>{card.issueType}</span>
                </div>
                {card.assignee && (
                  <span className="text-gray-600">👤 {card.assignee}</span>
                )}
              </div>
              
              <div className="mt-3 pt-3 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    Created: {new Date(card.created).toLocaleDateString()}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      window.open(`https://jira.company.com/browse/${card.key}`, '_blank')
                    }}
                    className="text-cyan-600 hover:text-cyan-700 text-xs flex items-center space-x-1"
                  >
                    <ExternalLink className="h-3 w-3" />
                    <span>Open in Jira</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 p-4 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl border border-cyan-200/30">
        <h3 className="font-medium text-gray-900 mb-2">Quick Actions</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedProject('all')}
            className="text-xs bg-white/60 backdrop-blur-sm px-3 py-1 rounded-lg border border-cyan-200/30 hover:bg-white/80 transition-colors"
          >
            Show All Projects
          </button>
          <button
            onClick={() => setSearchTerm('')}
            className="text-xs bg-white/60 backdrop-blur-sm px-3 py-1 rounded-lg border border-cyan-200/30 hover:bg-white/80 transition-colors"
          >
            Clear Search
          </button>
        </div>
      </div>
    </div>
  )
} 