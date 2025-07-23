import React, { useState } from 'react'
import { TestGeniePanel } from './components/TestGeniePanel'
import { EpicRoastPanel } from './components/EpicRoastPanel'
import { Header } from './components/Header'
import { LoadingSpinner } from './components/LoadingSpinner'

function App() {
  const [sharedTicketNumber, setSharedTicketNumber] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* TestGenie Panel */}
          <div className="space-y-6">
            <TestGeniePanel 
              sharedTicketNumber={sharedTicketNumber}
              setSharedTicketNumber={setSharedTicketNumber}
              setIsLoading={setIsLoading}
            />
          </div>
          
          {/* EpicRoast Panel */}
          <div className="space-y-6">
            <EpicRoastPanel 
              sharedTicketNumber={sharedTicketNumber}
              setSharedTicketNumber={setSharedTicketNumber}
              setIsLoading={setIsLoading}
            />
          </div>
        </div>
      </main>
      
      {/* Loading Overlay */}
      {isLoading && <LoadingSpinner />}
    </div>
  )
}

export default App 