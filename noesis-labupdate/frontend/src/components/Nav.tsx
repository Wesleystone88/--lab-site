import { NavLink, Link } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'

const links = [
  { to: '/results', label: 'Results' },
  { to: '/architecture', label: 'Architecture' },
  { to: '/agent', label: 'Agent' },
  { to: '/demo', label: 'Demo' },
  { to: '/environment', label: 'Environment' },
  { to: '/about', label: 'About' },
]

export default function Nav() {
  const [open, setOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50" style={{ background: 'rgba(8,8,16,0.85)', backdropFilter: 'blur(16px)', borderBottom: '1px solid #1e1e30' }}>
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-14">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group" style={{ textDecoration: 'none' }}>
          <span className="font-display text-xl italic" style={{ background: 'linear-gradient(135deg, #7c6af7, #c9a84c)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            νόησις
          </span>
          <span className="font-mono text-xs tracking-widest uppercase" style={{ color: '#4a4960', letterSpacing: '0.15em' }}>
            Lab
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              {label}
            </NavLink>
          ))}
        </div>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            to="/environment"
            className="font-mono text-xs tracking-widest uppercase px-4 py-2 rounded"
            style={{ background: 'rgba(124,106,247,0.12)', border: '1px solid rgba(124,106,247,0.3)', color: '#a89df9', textDecoration: 'none', letterSpacing: '0.12em', transition: 'all 0.2s ease' }}
            onMouseEnter={e => { (e.target as HTMLElement).style.background = 'rgba(124,106,247,0.2)'; (e.target as HTMLElement).style.borderColor = 'rgba(124,106,247,0.6)' }}
            onMouseLeave={e => { (e.target as HTMLElement).style.background = 'rgba(124,106,247,0.12)'; (e.target as HTMLElement).style.borderColor = 'rgba(124,106,247,0.3)' }}
          >
            Request Access
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setOpen(!open)}
          className="md:hidden p-2"
          style={{ color: '#8b8aaa', background: 'none', border: 'none', cursor: 'pointer' }}
        >
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden" style={{ borderTop: '1px solid #1e1e30', background: '#080810' }}>
          <div className="px-6 py-4 flex flex-col gap-4">
            {links.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                onClick={() => setOpen(false)}
              >
                {label}
              </NavLink>
            ))}
            <Link
              to="/environment"
              className="font-mono text-xs tracking-widest uppercase"
              style={{ color: '#7c6af7', textDecoration: 'none', letterSpacing: '0.12em' }}
              onClick={() => setOpen(false)}
            >
              Request Access →
            </Link>
          </div>
        </div>
      )}
    </nav>
  )
}
