import { Routes, Route } from 'react-router-dom'
import MainView from './pages/MainView'

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<MainView />} />
      </Routes>
    </div>
  )
}

export default App