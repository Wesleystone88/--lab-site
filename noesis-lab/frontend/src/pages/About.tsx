import { Link } from 'react-router-dom'

export default function About() {
  return (
    <div style={{ paddingTop: '56px' }}>
      {/* Header */}
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="pill pill-dim mb-5">About</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            Noesis Lab
          </h1>
          <div className="section-divider" />
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-2 gap-16">
          <div>
            <h2 className="font-display text-2xl italic font-light mb-4" style={{ color: '#e8e6f0' }}>
              The Work
            </h2>
            <div className="flex flex-col gap-4">
              <p className="font-body text-base font-light leading-relaxed" style={{ color: '#8b8aaa' }}>
                Noesis Lab is building a routed cognitive architecture — a system where every decision is dispatched to the component that can actually solve it, rather than fed into a single general model that handles everything through pattern matching.
              </p>
              <p className="font-body text-base font-light leading-relaxed" style={{ color: '#8b8aaa' }}>
                The research question is straightforward: can a system learn to match its reasoning strategy to the structural class of the problem it faces? Not through fine-tuning or prompting — through architecture.
              </p>
              <p className="font-body text-base font-light leading-relaxed" style={{ color: '#8b8aaa' }}>
                The results published here are real runs on a real system. The evidence is honest about what works, what doesn't, and why. Nothing is scaled up to obscure the mechanism.
              </p>
            </div>

            <div className="mt-8">
              <h2 className="font-display text-2xl italic font-light mb-4" style={{ color: '#e8e6f0' }}>
                The Principle
              </h2>
              <blockquote
                className="font-display text-xl italic font-light leading-relaxed pl-4"
                style={{ color: '#e8e6f0', borderLeft: '2px solid #4a3fa0' }}
              >
                "Compute when compute is required. Memory when memory is required. The rest stays lean and honest."
              </blockquote>
            </div>
          </div>

          <div>
            <h2 className="font-display text-2xl italic font-light mb-4" style={{ color: '#e8e6f0' }}>
              What This Is Not
            </h2>
            <div className="flex flex-col gap-3 mb-8">
              {[
                'This is not a claim of artificial general intelligence',
                'This is not a replacement for language models',
                'This is not a benchmark designed to be beaten',
                'This is not a black box — every decision is traceable',
              ].map((item) => (
                <div key={item} className="flex items-start gap-2">
                  <span className="font-mono text-xs mt-0.5" style={{ color: '#4a4960' }}>✗</span>
                  <span className="font-body text-sm font-light" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{item}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-col gap-3">
              {[
                'This is a routed architecture where each substrate is honest about its capabilities',
                'This is evidence that persistent memory produces measurable improvement',
                'This is a system that masters what it can structurally represent and tells you when it can\'t',
                'This is a foundation — the NN engine hooks are defined and waiting',
              ].map((item) => (
                <div key={item} className="flex items-start gap-2">
                  <span className="font-mono text-xs mt-0.5" style={{ color: '#7c6af7' }}>✓</span>
                  <span className="font-body text-sm font-light" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{item}</span>
                </div>
              ))}
            </div>

            <div className="mt-8 evidence-card p-5">
              <div className="font-mono text-xs uppercase tracking-widest mb-2" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>
                Founded by
              </div>
              <div className="font-display text-xl italic font-light" style={{ color: '#e8e6f0' }}>
                Timothy Wesley Stone
              </div>
              <div className="font-mono text-xs mt-1" style={{ color: '#4a4960' }}>
                Noesis Lab · 2026
              </div>
            </div>
          </div>
        </div>

        {/* CTA row */}
        <div
          className="mt-16 p-8 rounded text-center"
          style={{ background: 'rgba(124,106,247,0.04)', border: '1px solid rgba(124,106,247,0.12)' }}
        >
          <div
            className="font-display text-4xl italic mb-2"
            style={{
              background: 'linear-gradient(135deg, #7c6af7, #c9a84c)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            νόησις
          </div>
          <p className="font-body text-sm font-light mb-6" style={{ color: '#8b8aaa' }}>
            See the evidence. Understand the architecture. Request access.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/results"
              className="font-mono text-xs uppercase tracking-widest px-4 py-2 rounded"
              style={{
                background: 'rgba(124,106,247,0.12)',
                border: '1px solid rgba(124,106,247,0.3)',
                color: '#a89df9',
                textDecoration: 'none',
                letterSpacing: '0.12em',
              }}
            >
              Results
            </Link>
            <Link
              to="/architecture"
              className="font-mono text-xs uppercase tracking-widest px-4 py-2 rounded"
              style={{
                background: 'transparent',
                border: '1px solid #1e1e30',
                color: '#4a4960',
                textDecoration: 'none',
                letterSpacing: '0.12em',
              }}
            >
              Architecture
            </Link>
            <Link
              to="/environment"
              className="font-mono text-xs uppercase tracking-widest px-4 py-2 rounded"
              style={{
                background: 'transparent',
                border: '1px solid #1e1e30',
                color: '#4a4960',
                textDecoration: 'none',
                letterSpacing: '0.12em',
              }}
            >
              Request Access
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
