// API service for communicating with the Flask backend

const API_BASE_URL = '/api'

interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  suggestion?: string
}

interface TestGenieRequest {
  ticket_number?: string
  acceptance_criteria?: string
}

interface EpicRoastRequest {
  ticket_number?: string
  ticket_content?: string
  theme?: string
  level?: string
}

interface GroomRoomRequest {
  ticket_number?: string
  ticket_content?: string
  level?: string
}

export const generateTestScenarios = async (request: TestGenieRequest): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/testgenie/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    
    return await response.json()
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    }
  }
}

export const generateRoast = async (request: EpicRoastRequest): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/epicroast/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    
    return await response.json()
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    }
  }
}

export const generateGroom = async (request: GroomRoomRequest): Promise<ApiResponse> => {
  try {
    // Add cache-busting timestamp to prevent cached responses
    const timestamp = Date.now()
    const requestWithTimestamp = {
      ...request,
      timestamp
    }
    
    console.log('API: Making request to /groomroom with:', requestWithTimestamp, 'v2.0')
    
    const response = await fetch(`${API_BASE_URL}/groomroom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      },
      body: JSON.stringify(requestWithTimestamp),
    })
    
    console.log('API: Response status:', response.status)
    
    const responseData = await response.json()
    console.log('API: Response data:', responseData)
    
    // Handle specific error cases
    if (!response.ok && responseData.error) {
      return {
        success: false,
        error: responseData.error,
        suggestion: responseData.suggestion
      }
    }
    
    return responseData
  } catch (error) {
    console.error('API: Error in generateGroom:', error)
    return {
      success: false,
      error: 'Unable to reach GroomRoom service. Please check connection or try "Paste Ticket Content" instead.'
    }
  }
}

export const getJiraTicket = async (ticketNumber: string): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/jira/ticket/${ticketNumber}`)
    return await response.json()
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    }
  }
}

export const shareToTeams = async (type: 'testgenie' | 'epicroast', content: string, ticketNumber?: string): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams/share`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type,
        content,
        ticket_number: ticketNumber
      }),
    })
    
    return await response.json()
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    }
  }
}

export const healthCheck = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    return await response.json()
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    }
  }
} 