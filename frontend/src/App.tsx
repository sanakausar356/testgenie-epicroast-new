import { useState, useEffect } from 'react'
import { TestGeniePanel } from './components/TestGeniePanel'
import { EpicRoastPanel } from './components/EpicRoastPanel'
import { Header } from './components/Header'
import { LoadingSpinner } from './components/LoadingSpinner'

function App() {
  const [sharedTicketNumber, setSharedTicketNumber] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'epicroast' | 'testgenie'>('epicroast')
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    console.log('App component mounted successfully')
  }, [])

  if (hasError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-100 via-blue-100 to-orange-100 flex items-center justify-center">
        <div className="bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-cyan-200/50 p-8 max-w-md">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Application Error</h1>
          <p className="text-gray-700 mb-4">Something went wrong. Please refresh the page.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg"
          >
            Refresh Page
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-100 via-blue-100 to-orange-100 relative overflow-hidden">
      {/* Modern Beach Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-8 left-8 text-7xl opacity-15 animate-pulse">☀️</div>
        <div className="absolute top-16 right-16 text-5xl opacity-10 animate-bounce">☁️</div>
        <div className="absolute bottom-16 left-1/4 text-6xl opacity-20 animate-pulse">🌊</div>
        <div className="absolute top-1/3 right-1/3 text-4xl opacity-15 animate-bounce">🏖️</div>
        <div className="absolute bottom-8 right-8 text-5xl opacity-10 animate-pulse">🌴</div>
        <div className="absolute top-1/2 left-1/6 text-3xl opacity-20 animate-bounce">🩴</div>
        <div className="absolute bottom-1/3 right-1/6 text-4xl opacity-15 animate-pulse">🏄‍♂️</div>
      </div>
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Tab Navigation - Mobile First */}
        <div className="mb-8">
          <div className="flex bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-cyan-200/50 p-1 max-w-2xl mx-auto">
            <button
              onClick={() => setActiveTab('epicroast')}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-xl transition-all duration-300 ${
                activeTab === 'epicroast'
                  ? 'bg-gradient-to-r from-orange-400 to-red-500 text-white shadow-xl scale-105'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-cyan-50 hover:scale-105'
              }`}
            >
              <span className="text-lg">🔥</span>
              <span className="font-medium">Epic Roast</span>
            </button>
            <button
              onClick={() => setActiveTab('testgenie')}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-xl transition-all duration-300 ${
                activeTab === 'testgenie'
                  ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-white shadow-xl scale-105'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-cyan-50 hover:scale-105'
              }`}
            >
              <span className="text-lg">🧙‍♂️</span>
              <span className="font-medium">Test Genie</span>
            </button>
          </div>
        </div>

        {/* Desktop Layout - 2-column for both tabs */}
        <div className="hidden lg:block">
          {activeTab === 'epicroast' && (
            <div className="grid lg:grid-cols-2 gap-8">
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
          )}
          {activeTab === 'testgenie' && (
            <div className="grid lg:grid-cols-2 gap-8">
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
          )}
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
