import React from 'react'
import { Sparkles, Zap } from 'lucide-react'

export const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-8 w-8 text-primary-600" />
              <Zap className="h-8 w-8 text-secondary-600" />
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
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>API Connected</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
} 