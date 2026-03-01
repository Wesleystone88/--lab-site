import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import {
  routedIQResults, substrateAccuracy, coldVsWarm, unroutedIQResults,
  triageLearningCurve, navLearningCurve, diagnosisLearningCurve,
  triageQValues, navQValues, diagnosisQValues,
  triageBeforeAfter, navBeforeAfter, diagnosisBeforeAfter,
  glyphs, routedEpisodeTraces, unroutedEpisodeTraces,
} from '../data/results'

function LearningCurve({ data, color = '#7c6af7' }: { data: { window: string; pct: number }[]; color?: string }) {
  const w = 600, h = 80, padT = 8
  const xStep = w / (data.length - 1)
  const yScale = (pct: number) => padT + (h - padT) * (1 - pct / 100)
  const points = data.map((d, i) => `${i * xStep},${yScale(d.pct)}`).join(' ')
  const area = `M0,${h} ` + data.map((d, i) => `L${i * xStep},${yScale(d.pct)}`).join(' ') + ` L${(data.length - 1) * xStep},${h} Z`
  const gradId = `g${color.replace('#', '')}`
  return (
    <div style={{ width: '100%', height: 80 }}>
      <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.18" />
            <stop offset="100%" stopColor={color} stopOpacity="0.01" />
          </linearGradient>
        </defs>
        <path d={area} fill={`url(#${gradId})`} />
        <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    </div>
  )
}

function BeforeAfterTable({ data }: { data: typeof triageBeforeAfter }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #1e1e30' }}>
            {['Context', 'Correct', 'Episode 0', 'Episode 300'].map(h => (
              <th key={h} style={{ padding: '6px 12px', color: '#4a4960', textAlign: 'left', fontWeight: 400, letterSpacing: '0.08em' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #0e0e1a' }}>
              <td style={{ padding: '8px 12px', color: '#8b8aaa' }}>{row.context}</td>
              <td style={{ padding: '8px 12px', color: '#4a4960' }}>{row.correct}</td>
              <td style={{ padding: '8px 12px', color: row.ep0correct ? '#7c6af7' : '#e87c7c' }}>{row.ep0correct ? '✓' : '✗'} {row.ep0}</td>
              <td style={{ padding: '8px 12px', color: row.ep300correct ? '#7c6af7' : '#e87c7c' }}>{row.ep300correct ? '✓' : '✗'} {row.ep300}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function QValueTable({ data }: { data: typeof triageQValues }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #1e1e30' }}>
            {['Context', 'Top Choice', 'Q-Value'].map(h => (
              <th key={h} style={{ padding: '6px 12px', color: '#4a4960', textAlign: 'left', fontWeight: 400, letterSpacing: '0.08em' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #0e0e1a' }}>
              <td style={{ padding: '6px 12px', color: '#8b8aaa' }}>{row.context}</td>
              <td style={{ padding: '6px 12px', color: '#c9a84c' }}>{row.topChoice}</td>
              <td style={{ padding: '6px 12px' }}>
                <span style={{ color: '#7c6af7' }}>{row.qValue.toFixed(3)}</span>
                <span style={{ color: '#4a3fa0', marginLeft: 8, fontSize: '0.65rem' }}>
                  {'█'.repeat(Math.round(row.qValue * 10))}{'░'.repeat(10 - Math.round(row.qValue * 10))}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Expandable({ label, children }: { label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <button onClick={() => setOpen(!open)} className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest"
        style={{ color: open ? '#7c6af7' : '#4a4960', background: 'none', border: 'none', cursor: 'pointer', padding: 0, letterSpacing: '0.1em' }}>
        {open ? <ChevronUp size={11} /> : <ChevronDown size={11} />}{label}
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  )
}

export default function Results() {
  return (
    <div style={{ paddingTop: '56px' }}>
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-5xl mx-auto px-6 py-14">
          <div className="pill pill-accent mb-5">Evidence</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            Results &<br /><span className="text-gradient">Episode Traces</span>
          </h1>
          <div className="section-divider" />
          <p className="font-body text-base font-light max-w-2xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            All data below is drawn directly from run logs. No values are approximated. Every trace shows exactly what the system was given, which substrate fired, what it reasoned, and what it chose.
          </p>
        </div>
      </section>

      {/* Routed IQ */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-accent mb-4">Routed IQ Test · 500 Episodes</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Passing the IQ Test</h2>
        <p className="font-body text-sm font-light mb-8 max-w-2xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          Five hard pattern classes. Five dedicated substrates routed by structural features. Before routing: the Bandit guessed. After: each class dispatched to the substrate that can actually solve it.
        </p>
        <div className="evidence-card overflow-hidden mb-6">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e1e30', background: '#080810' }}>
                  {['Pattern Class', 'Substrate', 'Final Accuracy', 'Difficulty', ''].map(h => (
                    <th key={h} style={{ padding: '10px 14px', color: '#4a4960', textAlign: 'left', fontWeight: 400 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {routedIQResults.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a' }}>
                    <td style={{ padding: '10px 14px', color: '#e8e6f0' }}>{row.class}</td>
                    <td style={{ padding: '10px 14px', color: '#c9a84c' }}>{row.substrate}</td>
                    <td style={{ padding: '10px 14px', color: '#7c6af7', fontWeight: 500 }}>{row.accuracy}%</td>
                    <td style={{ padding: '10px 14px' }}><span className="pill pill-dim">{row.difficulty}</span></td>
                    <td style={{ padding: '10px 14px', width: 120 }}>
                      <div style={{ height: 2, background: '#1e1e30', borderRadius: 1 }}>
                        <div style={{ height: '100%', width: `${row.accuracy}%`, background: 'linear-gradient(90deg, #4a3fa0, #7c6af7)', borderRadius: 1 }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="evidence-card overflow-hidden mb-6">
          <div style={{ padding: '10px 14px', borderBottom: '1px solid #1e1e30' }}>
            <span className="font-mono text-xs uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>Substrate Report · 100 Attempts Each</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e1e30' }}>
                  {['Substrate', 'Accuracy', 'Attempts', 'Note'].map(h => (
                    <th key={h} style={{ padding: '8px 14px', color: '#4a4960', textAlign: 'left', fontWeight: 400 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {substrateAccuracy.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a' }}>
                    <td style={{ padding: '8px 14px', color: '#c9a84c' }}>{row.substrate}</td>
                    <td style={{ padding: '8px 14px', color: '#7c6af7' }}>{row.accuracy}%</td>
                    <td style={{ padding: '8px 14px', color: '#4a4960' }}>{row.attempts}</td>
                    <td style={{ padding: '8px 14px', color: '#8b8aaa' }}>{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <Expandable label="Show Episode Traces (ep 1 → ep 500)">
          <div className="flex flex-col gap-3 mt-3">
            {routedEpisodeTraces.map((t, i) => (
              <div key={i} className="trace-block">
                <div style={{ color: '#4a4960', marginBottom: 6, fontSize: '0.7rem' }}>
                  Episode {t.ep} · {t.class} · surface={t.surface} · substrate={t.substrate} · <span style={{ color: t.correct ? '#7c6af7' : '#e87c7c' }}>{t.correct ? '✓ CORRECT' : '✗ WRONG'}</span>
                </div>
                <div style={{ marginBottom: 4 }}>
                  <span style={{ color: '#4a4960' }}>FEATURES  </span>
                  {Object.entries(t.features).map(([k, v]) => <span key={k} style={{ marginRight: 10 }}><span style={{ color: '#4a4960' }}>{k}=</span><span style={{ color: '#8b8aaa' }}>{v}</span></span>)}
                </div>
                <div style={{ color: '#8b8aaa', whiteSpace: 'pre', marginBottom: 4 }}><span style={{ color: '#4a4960' }}>PROBLEM   </span>{t.problem}</div>
                <div style={{ marginBottom: 4 }}><span style={{ color: '#c9a84c' }}>SUBSTRATE </span><span style={{ color: '#c9a84c', whiteSpace: 'pre' }}>{t.reasoning}</span></div>
                <div>
                  <span style={{ color: '#4a4960' }}>CHOICES   </span>
                  {t.choices.map((c, j) => <span key={j} style={{ marginRight: 12, color: c === t.chosen && c === t.answer ? '#7c6af7' : c === t.chosen ? '#e87c7c' : c === t.answer ? '#4a4960' : '#4a4960' }}>{c === t.chosen ? '► ' : '○ '}{c}</span>)}
                </div>
              </div>
            ))}
          </div>
        </Expandable>
      </section>

      {/* Cold vs Warm */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-gold mb-4">Persistent Memory · 200 Episodes Cold → 200 Episodes Warm</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Cold vs Warm Start</h2>
        <p className="font-body text-sm font-light mb-8 max-w-2xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          After 200 cold episodes the agent writes its learned state to disk as Glyphs and Cards. A second 200-episode run reloads from disk. The only class that improves is the only class that genuinely learns.
        </p>
        <div className="evidence-card overflow-hidden">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e1e30', background: '#080810' }}>
                  {['Pattern Class', 'Substrate', 'Cold', 'Warm', 'Delta', 'Why'].map(h => (
                    <th key={h} style={{ padding: '10px 14px', color: '#4a4960', textAlign: 'left', fontWeight: 400 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {coldVsWarm.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a', background: row.delta > 0 ? 'rgba(124,106,247,0.03)' : 'transparent' }}>
                    <td style={{ padding: '10px 14px', color: '#e8e6f0' }}>{row.class}</td>
                    <td style={{ padding: '10px 14px', color: '#c9a84c' }}>{row.substrate}</td>
                    <td style={{ padding: '10px 14px', color: '#8b8aaa' }}>{row.cold}%</td>
                    <td style={{ padding: '10px 14px', color: '#7c6af7' }}>{row.warm}%</td>
                    <td style={{ padding: '10px 14px', color: row.delta > 0 ? '#c9a84c' : '#4a4960', fontWeight: row.delta > 0 ? 500 : 400 }}>{row.delta > 0 ? `+${row.delta}%` : '—'}</td>
                    <td style={{ padding: '10px 14px', color: '#8b8aaa', fontSize: '0.66rem' }}>{row.why}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Emergence Scenarios */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-accent mb-4">Emergence · 3 Scenarios · 300 Episodes Each · Zero Prompting</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Hidden Rule Discovery</h2>
        <p className="font-body text-sm font-light mb-10 max-w-2xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          The agent was given scenarios with hidden rules it was never shown. It started knowing nothing. Every Q-value below was earned from binary outcome feedback alone — correct or incorrect, nothing else.
        </p>
        {[
          { title: 'Emergency Triage', hiddenRules: ['Critical severity always gets treated first', 'Minor cases defer when resources are scarce', 'Moderate cases wait when resources are ample'], curve: triageLearningCurve, beforeAfter: triageBeforeAfter, qValues: triageQValues, converged: 'Episode 60', accuracy: '100%' },
          { title: 'Route Navigation', hiddenRules: ['Never take high-risk routes regardless of urgency', 'Urgent + low-cost → always take fast route', 'Low urgency → always take scenic (low-risk) route'], curve: navLearningCurve, beforeAfter: navBeforeAfter, qValues: navQValues, converged: 'Episode 10', accuracy: '100%' },
          { title: 'Pattern Diagnosis', hiddenRules: ['Fever + rash → viral infection', 'Pain + swelling → physical injury', 'Fatigue + pallor → anemic condition', 'Multiple signals → dominant pattern wins'], curve: diagnosisLearningCurve, beforeAfter: diagnosisBeforeAfter, qValues: diagnosisQValues, converged: 'Episode 90', accuracy: '98%' },
        ].map((s) => (
          <div key={s.title} className="evidence-card mb-6">
            <div className="p-5" style={{ borderBottom: '1px solid #1e1e30' }}>
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <h3 className="font-display text-xl italic font-light" style={{ color: '#e8e6f0' }}>{s.title}</h3>
                <div className="flex items-center gap-3">
                  <span className="pill pill-gold">{s.converged}</span>
                  <span className="font-mono text-sm" style={{ color: '#7c6af7' }}>{s.accuracy}</span>
                </div>
              </div>
              {s.hiddenRules.map((r, i) => (
                <div key={i} className="flex items-start gap-2 mb-1">
                  <span style={{ color: '#4a4960', flexShrink: 0 }}>▸</span>
                  <span className="font-mono text-xs" style={{ color: '#8b8aaa' }}>Hidden rule: {r}</span>
                </div>
              ))}
              <div className="font-mono text-xs mt-4 mb-1" style={{ color: '#4a4960' }}>Accuracy per 10-episode window</div>
              <LearningCurve data={s.curve} />
            </div>
            <div className="p-5" style={{ borderBottom: '1px solid #1e1e30' }}>
              <div className="font-mono text-xs mb-3 uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>Before vs After</div>
              <BeforeAfterTable data={s.beforeAfter} />
            </div>
            <div className="p-5">
              <Expandable label="Learned Policy — Q-Values (posterior means of Beta distributions)">
                <QValueTable data={s.qValues} />
              </Expandable>
            </div>
          </div>
        ))}
      </section>

      {/* Unrouted / Honest */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-dim mb-4">High-IQ Stress Test · 500 Episodes · Bandit Only (Pre-Routing)</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Honest About Difficulty</h2>
        <p className="font-body text-sm font-light mb-8 max-w-2xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          Results before the CognitiveRouter was added. The Bandit alone on five classes designed to break surface-level systems. Code structure: mastered. The rest: genuinely hard. The system does not fake progress.
        </p>
        <div className="evidence-card overflow-hidden mb-6">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e1e30', background: '#080810' }}>
                  {['Pattern Class', 'Accuracy', 'Difficulty', 'Why it\'s hard'].map(h => (
                    <th key={h} style={{ padding: '10px 14px', color: '#4a4960', textAlign: 'left', fontWeight: 400 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {unroutedIQResults.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a', background: row.accuracy === 100 ? 'rgba(124,106,247,0.03)' : 'transparent' }}>
                    <td style={{ padding: '10px 14px', color: '#e8e6f0' }}>{row.class}</td>
                    <td style={{ padding: '10px 14px', color: row.accuracy === 100 ? '#7c6af7' : '#8b8aaa' }}>{row.accuracy}%</td>
                    <td style={{ padding: '10px 14px' }}><span className="pill pill-dim">{row.difficulty}</span></td>
                    <td style={{ padding: '10px 14px', color: '#8b8aaa', fontSize: '0.66rem' }}>{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <Expandable label="Show Episode Traces (includes wrong answers)">
          <div className="flex flex-col gap-3 mt-3">
            {unroutedEpisodeTraces.map((t, i) => (
              <div key={i} className="trace-block">
                <div style={{ color: '#4a4960', marginBottom: 6, fontSize: '0.7rem' }}>
                  Episode {t.ep} · {t.class} · surface={t.surface} · <span style={{ color: t.correct ? '#7c6af7' : '#e87c7c' }}>{t.correct ? '✓ CORRECT' : '✗ WRONG'}</span>
                </div>
                <div style={{ marginBottom: 4 }}>
                  {Object.entries(t.features).map(([k, v]) => <span key={k} style={{ marginRight: 10 }}><span style={{ color: '#4a4960' }}>{k}=</span><span style={{ color: '#8b8aaa' }}>{v}</span></span>)}
                </div>
                <div style={{ color: '#8b8aaa', whiteSpace: 'pre', marginBottom: 4 }}><span style={{ color: '#4a4960' }}>PROBLEM   </span>{t.problem}</div>
                <div>
                  <span style={{ color: '#4a4960' }}>CHOICES   </span>
                  {t.choices.map((c, j) => {
                    const isAgent = c.includes('← agent')
                    const isCorrect = c.includes('← correct')
                    return <span key={j} style={{ marginRight: 14, color: isAgent && !isCorrect ? '#e87c7c' : isCorrect ? '#7c6af7' : '#4a4960' }}>{c}</span>
                  })}
                </div>
              </div>
            ))}
          </div>
        </Expandable>
      </section>

      {/* Glyphs */}
      <section className="max-w-5xl mx-auto px-6 py-14">
        <div className="pill pill-gold mb-4">Persistent Memory Artifacts</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Glyphs</h2>
        <p className="font-body text-sm font-light mb-8 max-w-2xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          After each session the agent writes structural invariants to disk as Glyphs — one per pattern class. These are what the system learned. On the next run it reloads them. The glyph is the knowledge.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {glyphs.map((g) => (
            <div key={g.id} className="evidence-card p-5">
              <div className="font-mono text-xs mb-2" style={{ color: '#4a4960' }}>{g.id}</div>
              <div className="font-display text-lg italic font-light mb-2" style={{ color: '#e8e6f0' }}>{g.title}</div>
              <div className="flex items-center gap-2 mb-3">
                <span className="pill pill-dim">{g.substrate}</span>
                <span className="font-mono text-xs" style={{ color: g.accuracy.includes('→') ? '#c9a84c' : '#7c6af7' }}>{g.accuracy}</span>
              </div>
              <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa' }}>{g.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-8 p-5 rounded" style={{ background: 'rgba(124,106,247,0.04)', border: '1px solid rgba(124,106,247,0.1)' }}>
          <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa' }}>
            <span style={{ color: '#7c6af7' }}>On honesty: </span>
            A system scoring 100% on every class is either cheating or the test is too easy. This system masters what it can structurally represent, shows genuine difficulty on what it cannot, and tells you exactly why. The hard class results are here because the difficulty is real.
          </p>
        </div>
      </section>
    </div>
  )
}
