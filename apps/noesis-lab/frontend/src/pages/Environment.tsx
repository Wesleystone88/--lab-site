import { useState } from 'react'
import { Send, CheckCircle } from 'lucide-react'

type FormState = 'idle' | 'sending' | 'success' | 'error'

export default function Environment() {
  const [form, setForm] = useState({ name: '', email: '', org: '', use: '', message: '' })
  const [formState, setFormState] = useState<FormState>('idle')
  const [errorMsg, setErrorMsg] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async () => {
    if (!form.name || !form.email) return
    setFormState('sending')

    try {
      const res = await fetch('/.netlify/functions/access-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })

      if (res.ok) {
        setFormState('success')
      } else {
        const data = await res.json()
        setErrorMsg(data.message || 'Request failed. Please try again.')
        setFormState('error')
      }
    } catch {
      setErrorMsg('Network error. Please try again.')
      setFormState('error')
    }
  }

  const inputStyle = {
    width: '100%',
    background: '#080810',
    border: '1px solid #1e1e30',
    borderRadius: '4px',
    padding: '0.65rem 0.85rem',
    color: '#e8e6f0',
    fontFamily: '"DM Sans", sans-serif',
    fontSize: '0.85rem',
    fontWeight: 300,
    outline: 'none',
    transition: 'border-color 0.2s ease',
  }

  const labelStyle = {
    display: 'block',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.65rem',
    letterSpacing: '0.12em',
    textTransform: 'uppercase' as const,
    color: '#4a4960',
    marginBottom: '0.4rem',
  }

  return (
    <div style={{ paddingTop: '56px' }}>
      {/* Header */}
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="pill pill-accent mb-5">Service</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            The Emergence<br />
            <span className="text-gradient">Environment</span>
          </h1>
          <div className="section-divider" />
          <p className="font-body text-base font-light max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            The environment engine is designed to grow. Each new environment is a plugin — one class, four methods. The agent plugs in through the bus protocol. Results are structured and comparable across runs, environments, and agents.
          </p>
        </div>
      </section>

      {/* What the environment provides */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-2 gap-16">
          <div>
            <h2 className="font-display text-3xl italic font-light mb-6" style={{ color: '#e8e6f0' }}>
              What It Provides
            </h2>

            <div className="flex flex-col gap-4">
              {[
                {
                  title: 'Structured Problem Generation',
                  desc: 'Problems are generated with known structure and hidden rules. Surfaces rotate — variable names, specific values, representations change — but the underlying pattern is invariant. This means every run is fresh but structurally equivalent.',
                },
                {
                  title: 'Surface-Invariant Feature Extraction',
                  desc: 'The environment extracts a structural feature dictionary from every problem. Your agent sees features — class type, operation hints, constraint flags — not raw text. This forces genuine pattern learning, not surface memorization.',
                },
                {
                  title: 'Comparable, Reproducible Results',
                  desc: 'Episode outcomes are logged in a structured format. Cold vs warm start runs are directly comparable. Learning curves are computable. Results are exportable and auditable.',
                },
                {
                  title: 'Plugin Architecture',
                  desc: 'New environments are one class with four methods. Your agent connects through the bus protocol. The routing and logging infrastructure carries over automatically.',
                },
              ].map(({ title, desc }) => (
                <div key={title} className="evidence-card p-5">
                  <h3 className="font-mono text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: '#e8e6f0', letterSpacing: '0.08em' }}>{title}</h3>
                  <p className="font-body text-sm font-light leading-relaxed" style={{ color: '#8b8aaa' }}>{desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h2 className="font-display text-3xl italic font-light mb-6" style={{ color: '#e8e6f0' }}>
              What You Can Test
            </h2>

            <div className="flex flex-col gap-3 mb-8">
              {[
                'Whether your agent learns stable invariants or memorizes surfaces',
                'Cold start vs warm start — does memory actually help?',
                'Learning curve shape — rapid convergence or slow drift?',
                'Cross-environment transfer — does what was learned here transfer there?',
                'Substrate accuracy — which decisions need compute vs which need memory?',
                'Routing behavior — is the dispatch logic matching problem physics?',
              ].map((item) => (
                <div key={item} className="flex items-start gap-2">
                  <span style={{ color: '#4a3fa0', marginTop: '0.35rem', flexShrink: 0 }}>▸</span>
                  <span className="font-mono text-xs" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{item}</span>
                </div>
              ))}
            </div>

            {/* What we share / don't share */}
            <div
              className="p-5 rounded"
              style={{ background: '#080810', border: '1px solid #1e1e30' }}
            >
              <div className="font-mono text-xs uppercase tracking-widest mb-3" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>
                Transparency Policy
              </div>
              <div className="flex flex-col gap-2">
                {[
                  ['✓', 'Architecture description and layer interfaces'],
                  ['✓', 'Episode traces and outcome logs'],
                  ['✓', 'Learning curves and convergence data'],
                  ['✓', 'Feature extraction schemas'],
                  ['✗', 'Agent implementation code'],
                  ['✗', 'Substrate internal logic'],
                  ['✗', 'Training data or glyph content'],
                ].map(([icon, text]) => (
                  <div key={text} className="flex items-center gap-2">
                    <span className="font-mono text-xs" style={{ color: icon === '✓' ? '#7c6af7' : '#4a4960' }}>{icon}</span>
                    <span className="font-mono text-xs" style={{ color: icon === '✓' ? '#8b8aaa' : '#4a4960' }}>{text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Access request form */}
      <section style={{ borderTop: '1px solid #1e1e30' }}>
        <div className="max-w-2xl mx-auto px-6 py-16">
          <div className="text-center mb-10">
            <div className="pill pill-accent mb-4" style={{ display: 'inline-block' }}>Access Request</div>
            <h2 className="font-display text-3xl italic font-light" style={{ color: '#e8e6f0' }}>
              Request Environment Access
            </h2>
            <p className="font-body text-sm font-light mt-3" style={{ color: '#8b8aaa' }}>
              Currently in limited access. Describe your use case and we'll be in touch.
            </p>
          </div>

          {formState === 'success' ? (
            <div
              className="p-8 rounded text-center"
              style={{ background: 'rgba(124,106,247,0.06)', border: '1px solid rgba(124,106,247,0.2)' }}
            >
              <CheckCircle size={32} style={{ color: '#7c6af7', margin: '0 auto 1rem' }} />
              <h3 className="font-display text-xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Request Received</h3>
              <p className="font-body text-sm font-light" style={{ color: '#8b8aaa' }}>
                We'll review your request and reach out via the email provided.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-5">
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label style={labelStyle}>Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Your name"
                    style={inputStyle}
                    onFocus={e => (e.target.style.borderColor = '#4a3fa0')}
                    onBlur={e => (e.target.style.borderColor = '#1e1e30')}
                  />
                </div>
                <div>
                  <label style={labelStyle}>Email *</label>
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="your@email.com"
                    style={inputStyle}
                    onFocus={e => (e.target.style.borderColor = '#4a3fa0')}
                    onBlur={e => (e.target.style.borderColor = '#1e1e30')}
                  />
                </div>
              </div>

              <div>
                <label style={labelStyle}>Organization / Affiliation</label>
                <input
                  type="text"
                  name="org"
                  value={form.org}
                  onChange={handleChange}
                  placeholder="Lab, company, independent"
                  style={inputStyle}
                  onFocus={e => (e.target.style.borderColor = '#4a3fa0')}
                  onBlur={e => (e.target.style.borderColor = '#1e1e30')}
                />
              </div>

              <div>
                <label style={labelStyle}>Primary Use Case</label>
                <select
                  name="use"
                  value={form.use}
                  onChange={handleChange}
                  style={{ ...inputStyle, cursor: 'pointer' }}
                  onFocus={e => (e.target.style.borderColor = '#4a3fa0')}
                  onBlur={e => (e.target.style.borderColor = '#1e1e30')}
                >
                  <option value="">Select a use case</option>
                  <option value="research">Academic / AI Research</option>
                  <option value="benchmarking">Agent Benchmarking</option>
                  <option value="development">Agent Development & Testing</option>
                  <option value="enterprise">Enterprise AI Evaluation</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Tell us more</label>
                <textarea
                  name="message"
                  value={form.message}
                  onChange={handleChange}
                  placeholder="What are you building or researching? What would you test in this environment?"
                  rows={4}
                  style={{ ...inputStyle, resize: 'vertical', minHeight: '100px' }}
                  onFocus={e => (e.target.style.borderColor = '#4a3fa0')}
                  onBlur={e => (e.target.style.borderColor = '#1e1e30')}
                />
              </div>

              {formState === 'error' && (
                <div
                  className="p-3 rounded font-mono text-xs"
                  style={{ background: 'rgba(232,124,124,0.06)', border: '1px solid rgba(232,124,124,0.2)', color: '#e87c7c' }}
                >
                  {errorMsg}
                </div>
              )}

              <button
                onClick={handleSubmit}
                disabled={formState === 'sending' || !form.name || !form.email}
                className="flex items-center justify-center gap-2 font-mono text-xs uppercase tracking-widest px-6 py-3 rounded"
                style={{
                  background: form.name && form.email ? 'rgba(124,106,247,0.15)' : 'rgba(124,106,247,0.05)',
                  border: `1px solid ${form.name && form.email ? 'rgba(124,106,247,0.4)' : 'rgba(124,106,247,0.15)'}`,
                  color: form.name && form.email ? '#a89df9' : '#4a4960',
                  cursor: form.name && form.email ? 'pointer' : 'not-allowed',
                  letterSpacing: '0.12em',
                  transition: 'all 0.2s ease',
                }}
              >
                {formState === 'sending' ? (
                  <>Sending...</>
                ) : (
                  <>Send Request <Send size={12} /></>
                )}
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
