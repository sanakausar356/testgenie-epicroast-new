import { Loader2 } from 'lucide-react'

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
        <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
        <span className="text-gray-700 font-medium">Processing...</span>
      </div>
    </div>
  )
} 