import { useState, useEffect } from 'react'
import { Sparkles, Zap, CheckCircle, Wifi, WifiOff } from 'lucide-react'
import { healthCheck } from '../services/api'

export const Header: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting')

  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const response = await healthCheck()
        if (response.success) {
          setApiStatus('connected')
        } else {
          setApiStatus('disconnected')
        }
      } catch (error) {
        setApiStatus('disconnected')
      }
    }

    checkApiHealth()
    const interval = setInterval(checkApiHealth, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const getStatusDisplay = () => {
    switch (apiStatus) {
      case 'connected':
        return (
          <div className="flex items-center space-x-2 text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
            <CheckCircle className="h-4 w-4" />
            <span>Ready to Generate</span>
          </div>
        )
      case 'connecting':
        return (
          <div className="flex items-center space-x-2 text-sm text-yellow-600 bg-yellow-50 px-3 py-1 rounded-full">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
            <span>Connecting...</span>
          </div>
        )
      case 'disconnected':
        return (
          <div className="flex items-center space-x-2 text-sm text-red-600 bg-red-50 px-3 py-1 rounded-full">
            <WifiOff className="h-4 w-4" />
            <span>Check API Key</span>
          </div>
        )
    }
  }

  return (
    <header className="bg-white/90 backdrop-blur-sm shadow-lg border-b border-orange-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className="text-4xl">🧙‍♂️</span>
              <span className="text-4xl">🤖</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                TestGenie & EpicRoast
              </h1>
              <p className="text-sm text-gray-600">
                AI-Powered Test Generation & Ticket Roasting
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {getStatusDisplay()}
          </div>
        </div>
      </div>
    </header>
  )
} 