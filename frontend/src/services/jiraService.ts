interface JiraCard {
  key: string
  summary: string
  status: string
  priority: string
  assignee?: string
  project: string
  issueType: string
  created: string
  description?: string
  team: string
}

interface JiraConfig {
  baseUrl: string
  email: string
  apiToken: string
}

// Jira configuration - using existing .env file
const JIRA_CONFIG: JiraConfig = {
  baseUrl: (import.meta as any).env?.VITE_JIRA_URL || (import.meta as any).env?.JIRA_URL || 'https://your-company.atlassian.net',
  email: (import.meta as any).env?.VITE_JIRA_USERNAME || (import.meta as any).env?.JIRA_USERNAME || '',
  apiToken: (import.meta as any).env?.VITE_JIRA_API_TOKEN || (import.meta as any).env?.JIRA_API_TOKEN || ''
}

// Team to board mapping
const TEAM_BOARD_MAPPING = {
  'odyssey': { boardId: '123', projectKey: 'ODCD' },
  'everest': { boardId: '124', projectKey: 'ODCD-EVEREST' },
  'everest-pwa': { boardId: '125', projectKey: 'EVEREST-PWA' },
  'batman': { boardId: '126', projectKey: 'BATMAN' },
  'silver-surfers': { boardId: '127', projectKey: 'ODCD-SILVER' }
}

// Status mapping for filtering
const STATUS_FILTERS = {
  'ready-to-groom': ['Ready to Groom', 'Backlog', 'To Do'],
  'ready-for-dev': ['Ready for Dev', 'Ready for Development', 'In Development']
}

export class JiraService {
  private static getAuthHeader(): string {
    const credentials = btoa(`${JIRA_CONFIG.email}:${JIRA_CONFIG.apiToken}`)
    return `Basic ${credentials}`
  }

  private static async makeRequest(endpoint: string): Promise<any> {
    try {
      const response = await fetch(`${JIRA_CONFIG.baseUrl}/rest/api/3/${endpoint}`, {
        headers: {
          'Authorization': this.getAuthHeader(),
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Jira API error: ${response.status} ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Jira API request failed:', error)
      throw error
    }
  }

  static async fetchBoardIssues(boardId: string, statusFilter: string[]): Promise<JiraCard[]> {
    try {
      // JQL query to get issues from specific board with status filter
      const jql = `project in (${Object.values(TEAM_BOARD_MAPPING).map(t => t.projectKey).join(', ')}) AND status in ("${statusFilter.join('", "')}") ORDER BY created DESC`
      
      const response = await this.makeRequest(`search?jql=${encodeURIComponent(jql)}&maxResults=50&fields=summary,status,priority,assignee,issuetype,created,description`)
      
      return response.issues.map((issue: any) => ({
        key: issue.key,
        summary: issue.fields.summary,
        status: issue.fields.status.name,
        priority: issue.fields.priority?.name || 'Medium',
        assignee: issue.fields.assignee?.displayName,
        project: issue.fields.project.key,
        issueType: issue.fields.issuetype.name,
        created: issue.fields.created,
        description: issue.fields.description,
        team: this.getTeamFromProject(issue.fields.project.key)
      }))
    } catch (error) {
      console.error('Failed to fetch board issues:', error)
      throw error
    }
  }

  private static getTeamFromProject(projectKey: string): string {
    for (const [team, config] of Object.entries(TEAM_BOARD_MAPPING)) {
      if (config.projectKey === projectKey) {
        return team
      }
    }
    return 'unknown'
  }

  static async fetchReadyToGroomCards(teamFilter: string = 'all'): Promise<JiraCard[]> {
    try {
      const statusFilter = STATUS_FILTERS['ready-to-groom']
      const allIssues = await this.fetchBoardIssues('all', statusFilter)
      
      if (teamFilter === 'all') {
        return allIssues
      }
      
      return allIssues.filter(issue => issue.team === teamFilter)
    } catch (error) {
      console.error('Failed to fetch Ready to Groom cards:', error)
      throw error
    }
  }

  static async fetchReadyForDevCards(teamFilter: string = 'all'): Promise<JiraCard[]> {
    try {
      const statusFilter = STATUS_FILTERS['ready-for-dev']
      const allIssues = await this.fetchBoardIssues('all', statusFilter)
      
      if (teamFilter === 'all') {
        return allIssues
      }
      
      return allIssues.filter(issue => issue.team === teamFilter)
    } catch (error) {
      console.error('Failed to fetch Ready for Dev cards:', error)
      throw error
    }
  }

  static async fetchAllCards(teamFilter: string = 'all'): Promise<JiraCard[]> {
    try {
      const [readyToGroom, readyForDev] = await Promise.all([
        this.fetchReadyToGroomCards(teamFilter),
        this.fetchReadyForDevCards(teamFilter)
      ])
      
      return [...readyToGroom, ...readyForDev]
    } catch (error) {
      console.error('Failed to fetch all cards:', error)
      throw error
    }
  }

  // Fallback to mock data if Jira API is not configured
  static getMockData(): JiraCard[] {
    return [
      {
        key: 'ODCD-33741',
        summary: 'Implement user authentication flow',
        status: 'Ready to Groom',
        priority: 'High',
        assignee: 'John Doe',
        project: 'ODCD',
        issueType: 'Story',
        created: '2024-01-15',
        team: 'odyssey'
      },
      {
        key: 'ODCD-33742',
        summary: 'Add payment gateway integration',
        status: 'Ready for Dev',
        priority: 'Medium',
        assignee: 'Jane Smith',
        project: 'ODCD',
        issueType: 'Story',
        created: '2024-01-16',
        team: 'odyssey'
      },
      {
        key: 'EVEREST-1234',
        summary: 'Upgrade PWA Kit to latest version',
        status: 'Ready to Groom',
        priority: 'High',
        assignee: 'Mike Johnson',
        project: 'EVEREST-PWA',
        issueType: 'Epic',
        created: '2024-01-14',
        team: 'everest-pwa'
      },
      {
        key: 'BATMAN-5678',
        summary: 'Implement dark mode feature',
        status: 'Ready for Dev',
        priority: 'Low',
        assignee: 'Sarah Wilson',
        project: 'BATMAN',
        issueType: 'Story',
        created: '2024-01-17',
        team: 'batman'
      },
      {
        key: 'ODCD-33743',
        summary: 'Optimize database queries',
        status: 'Ready to Groom',
        priority: 'High',
        assignee: 'Alex Brown',
        project: 'ODCD-SILVER',
        issueType: 'Task',
        created: '2024-01-18',
        team: 'silver-surfers'
      }
    ]
  }
} 