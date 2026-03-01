import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer style={{ borderTop: '1px solid #1e1e30', background: '#080810' }}>
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="flex flex-col md:flex-row justify-between items-start gap-8">
          <div>
            <span className="font-display text-2xl italic" style={{ background: 'linear-gradient(135deg, #7c6af7, #c9a84c)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              νόησις
            </span>
            <p className="font-mono text-xs mt-2" style={{ color: '#4a4960', letterSpacing: '0.08em' }}>
              Compute when compute is required.<br />
              Memory when memory is required.
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <span className="font-mono text-xs uppercase tracking-widest mb-1" style={{ color: '#4a4960' }}>Explore</span>
            {[
              ['/results', 'Results'],
              ['/architecture', 'Architecture'],
              ['/agent', 'Agent'],
              ['/environment', 'Environment'],
              ['/about', 'About'],
            ].map(([to, label]) => (
              <Link key={to} to={to} className="nav-link" style={{ fontSize: '0.72rem' }}>{label}</Link>
            ))}
          </div>
        </div>

        <div className="mt-8 pt-6" style={{ borderTop: '1px solid #1e1e30', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <span className="font-mono text-xs" style={{ color: '#4a4960', letterSpacing: '0.06em' }}>
            © 2026 Timothy Wesley Stone · Noesis Lab · All Rights Reserved
          </span>
          <span className="font-mono text-xs" style={{ color: '#4a4960' }}>
            νόησις™ — Intelligence, Engineered
          </span>
        </div>
      </div>
    </footer>
  )
}
