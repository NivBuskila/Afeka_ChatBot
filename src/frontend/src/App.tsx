// App.tsx
import { useState } from 'react'

function App() {
  const [isLanding, setIsLanding] = useState(true)
  
  const handleContinue = () => {
    setIsLanding(false)
  }
  
  return (
    <div className="h-screen bg-black">
      {isLanding ? (
        // landing page
        <div 
          className="flex items-center justify-center h-full text-green-400 cursor-pointer"
          onClick={handleContinue}
        >
         Click here to continue
        </div>
      ) : (
        //chat
        <div className="flex items-center justify-center h-full text-green-400">
         chat
        </div>
      )}
    </div>
  )
}

export default App