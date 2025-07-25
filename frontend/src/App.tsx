#import React, { useState } from 'react'
import { TestGeniePanel } from './components/TestGeniePanel'
import { EpicRoastPanel } from './components/EpicRoastPanel'
import { Header } from './components/Header'
import { LoadingSpinner } from './components/LoadingSpinner'

function App() {
  const [sharedTicketNumber, setSharedTicketNumber] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'epicroast' | 'testgenie'>('epicroast')

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-yellow-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Tab Navigation - Mobile First */}
        <div className="mb-8">
          <div className="flex bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-orange-200 p-1 max-w-md mx-auto">
            <button
              onClick={() => setActiveTab('epicroast')}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-lg transition-all duration-200 ${
                activeTab === 'epicroast'
                  ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-orange-50'
              }`}
            >
              <span className="text-lg">🔥</span>
              <span className="font-medium">EpicRoast</span>
            </button>
            <button
              onClick={() => setActiveTab('testgenie')}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-lg transition-all duration-200 ${
                activeTab === 'testgenie'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-blue-50'
              }`}
            >
              <span className="text-lg">🧙‍♂️</span>
              <span className="font-medium">TestGenie</span>
            </button>
          </div>
        </div>

        {/* Desktop Layout - Swapped positions */}
        <div className="hidden lg:grid lg:grid-cols-2 gap-8">
          <EpicRoastPanel 
            sharedTicketNumber={sharedTicketNumber}
            setSharedTicketNumber={setSharedTicketNumber}
            setIsLoading={setIsLoading}
          />
          <TestGeniePanel 
            sharedTicketNumber={sharedTicketNumber}
            setSharedTicketNumber={setSharedTicketNumber}
            setIsLoading={setIsLoading}
          />
        </div>

        {/* Mobile Layout - Tabbed */}
        <div className="lg:hidden">
          {activeTab === 'epicroast' && (
            <EpicRoastPanel 
              sharedTicketNumber={sharedTicketNumber}
              setSharedTicketNumber={setSharedTicketNumber}
              setIsLoading={setIsLoading}
            />
          )}
          {activeTab === 'testgenie' && (
            <TestGeniePanel 
              sharedTicketNumber={sharedTicketNumber}
              setSharedTicketNumber={setSharedTicketNumber}
              setIsLoading={setIsLoading}
            />
          )}
        </div>
      </main>
      
      {/* Loading Overlay */}
      {isLoading && <LoadingSpinner />}
    </div>
  )
}

export default App 
