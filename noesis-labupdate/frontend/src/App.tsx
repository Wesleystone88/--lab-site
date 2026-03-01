import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Nav from './components/Nav'
import Footer from './components/Footer'
import Home from './pages/Home'
import Results from './pages/Results'
import Architecture from './pages/Architecture'
import Agent from './pages/Agent'
import Environment from './pages/Environment'
import About from './pages/About'
import Demo from './pages/Demo'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return null
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <div className="min-h-screen flex flex-col relative">
        <Nav />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results" element={<Results />} />
            <Route path="/architecture" element={<Architecture />} />
            <Route path="/agent" element={<Agent />} />
            <Route path="/environment" element={<Environment />} />
            <Route path="/demo" element={<Demo />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}
