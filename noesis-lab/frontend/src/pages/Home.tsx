import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { ArrowRight, ChevronRight } from 'lucide-react'

function AnimatedStat({ value, label, delay = 0 }: { value: string; label: string; delay?: number }) {
  const [visible, setVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <div
      ref={ref}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(16px)',
        transition: 'opacity 0.7s ease, transform 0.7s ease',
      }}
    >
      <div className="font-display text-4xl md:text-5xl italic text-gradient-gold">{value}</div>
      <div className="font-mono text-xs mt-1 uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>{label}</div>
    </div>
  )
}

export default function Home() {
  const [glowPos, setGlowPos] = useState({ x: 50, y: 50 })

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setGlowPos({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100,
      })
    }
    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  return (
    <div style={{ paddingTop: '56px' }}>
      {/* Hero */}
      <section
        className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden"
        style={{ background: '#080810' }}
      >
        {/* Dynamic background glow */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `radial-gradient(ellipse 600px 500px at ${glowPos.x}% ${glowPos.y}%, rgba(124,106,247,0.07) 0%, transparent 70%)`,
            transition: 'background 0.3s ease',
          }}
        />

        {/* Static ambient glow behind Greek letter */}
        <div
          className="absolute pointer-events-none"
          style={{
            width: '800px',
            height: '600px',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'radial-gradient(ellipse, rgba(124,106,247,0.08) 0%, transparent 65%)',
          }}
        />

        {/* Grid lines */}
        <div
          className="absolute inset-0 pointer-events-none opacity-30"
          style={{
            backgroundImage: `
              linear-gradient(rgba(124,106,247,0.04) 1px, transparent 1px),
              linear-gradient(90deg, rgba(124,106,247,0.04) 1px, transparent 1px)
            `,
            backgroundSize: '80px 80px',
          }}
        />

        <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
          {/* Eyebrow */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div style={{ width: '32px', height: '1px', background: 'linear-gradient(90deg, transparent, #4a4960)' }} />
            <span className="font-mono text-xs uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.18em' }}>
              Noesis Lab · Research Division
            </span>
            <div style={{ width: '32px', height: '1px', background: 'linear-gradient(90deg, #4a4960, transparent)' }} />
          </div>

          {/* Greek centerpiece */}
          <div
            className="animate-float"
            style={{
              fontSize: 'clamp(100px, 20vw, 220px)',
              fontFamily: '"Cormorant Garamond", serif',
              fontWeight: 300,
              fontStyle: 'italic',
              lineHeight: 1,
              background: 'linear-gradient(135deg, #7c6af7 0%, #c9a84c 45%, #a89df9 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              filter: 'drop-shadow(0 0 60px rgba(124,106,247,0.35))',
              marginBottom: '-0.1em',
            }}
          >
            νόησις
          </div>

          {/* Tagline */}
          <h1
            className="font-body text-lg md:text-xl font-light mt-6"
            style={{ color: '#8b8aaa', letterSpacing: '0.04em', maxWidth: '480px', margin: '1.5rem auto 0' }}
          >
            A routed cognitive architecture that computes, remembers, and learns — each substrate honest about its own nature.
          </h1>

          {/* CTA row */}
          <div className="flex flex-wrap items-center justify-center gap-4 mt-10">
            <Link
              to="/results"
              className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest px-5 py-3 rounded"
              style={{
                background: 'rgba(124,106,247,0.15)',
                border: '1px solid rgba(124,106,247,0.4)',
                color: '#a89df9',
                textDecoration: 'none',
                letterSpacing: '0.12em',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={e => { const el = e.currentTarget; el.style.background = 'rgba(124,106,247,0.25)'; el.style.borderColor = 'rgba(124,106,247,0.7)' }}
              onMouseLeave={e => { const el = e.currentTarget; el.style.background = 'rgba(124,106,247,0.15)'; el.style.borderColor = 'rgba(124,106,247,0.4)' }}
            >
              View Evidence <ArrowRight size={12} />
            </Link>
            <Link
              to="/architecture"
              className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest px-5 py-3 rounded"
              style={{
                background: 'transparent',
                border: '1px solid #1e1e30',
                color: '#4a4960',
                textDecoration: 'none',
                letterSpacing: '0.12em',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={e => { const el = e.currentTarget; el.style.borderColor = '#4a4960'; el.style.color = '#8b8aaa' }}
              onMouseLeave={e => { const el = e.currentTarget; el.style.borderColor = '#1e1e30'; el.style.color = '#4a4960' }}
            >
              The Architecture
            </Link>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2" style={{ color: '#4a4960' }}>
          <span className="font-mono text-xs uppercase tracking-widest" style={{ fontSize: '0.6rem', letterSpacing: '0.18em' }}>Scroll</span>
          <div
            style={{
              width: '1px',
              height: '40px',
              background: 'linear-gradient(to bottom, #4a4960, transparent)',
              animation: 'pulse 2s infinite',
            }}
          />
        </div>
      </section>

      {/* Stats bar */}
      <section style={{ borderTop: '1px solid #1e1e30', borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
            <AnimatedStat value="100%" label="Mastered substrate accuracy" delay={100} />
            <AnimatedStat value="+28%" label="Warm-start memory lift" delay={200} />
            <AnimatedStat value="500" label="Routed IQ episodes" delay={300} />
            <AnimatedStat value="5" label="IQ pattern classes solved" delay={400} />
          </div>
        </div>
      </section>

      {/* What we're building */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <div className="grid md:grid-cols-2 gap-16 items-start">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="pill pill-accent">Research</div>
            </div>
            <h2 className="font-display text-4xl md:text-5xl italic font-light leading-tight" style={{ color: '#e8e6f0' }}>
              Not a language model.<br />
              <span className="text-gradient">A cognitive architecture.</span>
            </h2>
            <div className="section-divider" />
            <p className="font-body text-base font-light leading-relaxed" style={{ color: '#8b8aaa' }}>
              νόησις is a layered system where every decision is routed to the substrate that can actually solve it — compute, constraint satisfaction, memory retrieval, or learned preference. Each component is honest about its own nature.
            </p>
            <p className="font-body text-base font-light leading-relaxed mt-4" style={{ color: '#8b8aaa' }}>
              The routing log is the explanation. Nothing is a black box. Every substrate call is traceable from feature extraction to final answer.
            </p>
            <Link
              to="/architecture"
              className="inline-flex items-center gap-2 mt-8 font-mono text-xs uppercase tracking-widest"
              style={{ color: '#7c6af7', textDecoration: 'none', letterSpacing: '0.12em' }}
            >
              Explore the layers <ChevronRight size={12} />
            </Link>
          </div>

          <div className="flex flex-col gap-4">
            {[
              {
                num: '01',
                title: 'CognitiveRouter',
                desc: 'Reads structural features. Dispatches to the right substrate. Logs every decision.',
                tag: 'Dispatch',
              },
              {
                num: '02',
                title: 'Dedicated Substrates',
                desc: 'Compute. Constraint solve. Decompose. Memory probe. Each purpose-built, nothing always on.',
                tag: 'Reasoning',
              },
              {
                num: '03',
                title: 'SextBioRAG Agent',
                desc: 'Six biological pillars. Thompson Sampling bandit. Hopfield attractor memory. Zero prompting.',
                tag: 'Learning',
              },
              {
                num: '04',
                title: 'Persistent State',
                desc: 'State accretes across sessions. Glyphs, cards, bandit posteriors. The agent that starts run 2 is not the same as run 1.',
                tag: 'Memory',
              },
            ].map(({ num, title, desc, tag }) => (
              <div key={num} className="evidence-card p-5 flex gap-4">
                <span className="font-mono text-xs mt-0.5 shrink-0" style={{ color: '#4a4960' }}>{num}</span>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs font-medium" style={{ color: '#e8e6f0' }}>{title}</span>
                    <span className="pill pill-dim">{tag}</span>
                  </div>
                  <p className="font-body text-sm font-light" style={{ color: '#8b8aaa', lineHeight: 1.6 }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The principle */}
      <section style={{ borderTop: '1px solid #1e1e30', borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-3xl mx-auto px-6 py-20 text-center">
          <blockquote
            className="font-display text-2xl md:text-3xl italic font-light leading-relaxed"
            style={{ color: '#e8e6f0' }}
          >
            "Compute when compute is required.<br />
            Memory when memory is required.<br />
            <span className="text-gradient">The rest stays lean and honest.</span>"
          </blockquote>
          <div className="flex items-center justify-center gap-3 mt-6">
            <div style={{ width: '20px', height: '1px', background: '#1e1e30' }} />
            <span className="font-mono text-xs" style={{ color: '#4a4960', letterSpacing: '0.1em' }}>Design Principle · νόησις Architecture</span>
            <div style={{ width: '20px', height: '1px', background: '#1e1e30' }} />
          </div>
        </div>
      </section>

      {/* Preview cards for other pages */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              to: '/results',
              tag: 'Evidence',
              title: 'Results & Traces',
              desc: 'Actual episode traces. Learning curves. Before/after comparisons. The routing log speaks for itself.',
              stat: '900+ episodes documented',
            },
            {
              to: '/agent',
              tag: 'System',
              title: 'The Agent',
              desc: 'SextBioRAG — six biological cognitive pillars operating through a unified signal bus. No LLM. No prompting.',
              stat: '6-pillar architecture',
            },
            {
              to: '/environment',
              tag: 'Service',
              title: 'Environment Access',
              desc: 'The emergence environment is designed to grow. Plugin architecture. Structured, comparable results across runs.',
              stat: 'Request access →',
            },
          ].map(({ to, tag, title, desc, stat }) => (
            <Link
              key={to}
              to={to}
              className="evidence-card p-6 flex flex-col gap-4 group"
              style={{ textDecoration: 'none' }}
            >
              <div className="pill pill-accent">{tag}</div>
              <h3 className="font-display text-xl italic font-light" style={{ color: '#e8e6f0' }}>{title}</h3>
              <p className="font-body text-sm font-light flex-1" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{desc}</p>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs" style={{ color: '#7c6af7', letterSpacing: '0.06em' }}>{stat}</span>
                <ArrowRight size={10} style={{ color: '#7c6af7', transition: 'transform 0.2s' }} className="group-hover:translate-x-1" />
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
