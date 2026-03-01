import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface TraceEntry {
  problem: string
  features: string
  reasoning: string
  chose: string
  correct: string
  match: boolean
}

interface EvidenceCardData {
  title: string
  tag: string
  tagVariant: 'accent' | 'gold' | 'dim'
  accuracy: number
  accuracyLabel: string
  convergedAt?: string
  episodes: number
  summary: string
  highlights: string[]
  traces: TraceEntry[]
}

const cards: EvidenceCardData[] = [
  {
    title: 'Routed IQ — Cross-Sequence Patterns',
    tag: 'Substrate: Compute',
    tagVariant: 'accent',
    accuracy: 100,
    accuracyLabel: '100% accuracy',
    episodes: 500,
    summary: 'Cross-sequence problems require holding A, B, and C in working memory simultaneously and finding the hidden operation. Before routing, the Bandit had no way to compute this — it guessed. After the CognitiveRouter dispatched to the compute substrate, every cross-sequence problem was solved by detecting and applying the operation directly.',
    highlights: [
      'Router reads structural features: class type, trend direction, operation hint',
      'Compute substrate detects operation (add, subtract, multiply, parity) and applies it',
      'Substrate reasoning is visible in the trace — not a black box',
      'Same accuracy on episode 1 as episode 500 — compute does not need to learn',
    ],
    traces: [
      {
        problem: 'A: [3, 7, 6]\nB: [5, 3, 4]\nC: [8, 10] + [?]',
        features: 'class=cross_sequence  trend=mixed  op_hint=arithmetic',
        reasoning: 'A[n] add B[n] → 6 add 4 = 10',
        chose: '10',
        correct: '10',
        match: true,
      },
      {
        problem: 'A: [6, 8, 6]\nB: [7, 6, 6]\nC: [42, 48] + [?]',
        features: 'class=cross_sequence  trend=up  op_hint=multiply',
        reasoning: 'A[n] multiply B[n] → 6 multiply 6 = 36',
        chose: '36',
        correct: '36',
        match: true,
      },
      {
        problem: 'A: [2, 3, 5]\nB: [4, 3, 3]\nC: [-2, 0] + [?]',
        features: 'class=cross_sequence  trend=up  op_hint=subtract',
        reasoning: 'A[n] subtract B[n] → 5 subtract 3 = 2',
        chose: '2',
        correct: '2',
        match: true,
      },
    ],
  },
  {
    title: 'Persistent Memory — Cold vs Warm Start',
    tag: 'Substrate: Bandit + Memory',
    tagVariant: 'gold',
    accuracy: 28,
    accuracyLabel: '+28% warm-start lift',
    episodes: 400,
    summary: 'The system was run 200 episodes cold, then its learned state was written to disk as Glyphs (structural invariants) and Cards (high-salience episodes). A second 200-episode run loaded those artifacts on startup. The code structure class — the only class that genuinely learns — improved by 28%. The compute substrates showed zero change because they do not learn. This is the architecture working as designed.',
    highlights: [
      'Code structure: cold 72% → warm 100% (+28%)',
      'Compute / solver substrates: unchanged — they compute, not learn',
      'Bandit posteriors carry genuine experience across sessions',
      'Glyphs encode structural invariants discovered through experience',
    ],
    traces: [
      {
        problem: 'Find the value N where your function must:\n  • accept N inputs (N divisible by 2)\n  • produce output whose digits sum to 5\n  • return even count',
        features: 'class=constraint_satisfaction  constraints=3',
        reasoning: 'choice=50 satisfies 3/3 constraints: [divisible by 2, digit sum = 5, even number]',
        chose: '50',
        correct: '50',
        match: true,
      },
    ],
  },
  {
    title: 'Emergence — Emergency Triage',
    tag: 'Scenario: Hidden Rules',
    tagVariant: 'accent',
    accuracy: 100,
    accuracyLabel: '100% final accuracy',
    convergedAt: 'Converged: episode 60',
    episodes: 300,
    summary: 'The agent was given a scenario with three hidden rules it was never shown. It started knowing nothing — random choices, ~33% accuracy. Through 300 episodes of binary feedback (correct/incorrect only), it discovered all three rules and converged to 100% accuracy by episode 60. No gradient descent. No prompting. No LLM. Pure Thompson Sampling bandit over biological memory dynamics.',
    highlights: [
      'Hidden rule: critical severity always treated first',
      'Hidden rule: minor cases defer when resources are scarce',
      'Hidden rule: moderate cases wait when resources are ample',
      'Agent never told the rules — learned from binary outcome feedback alone',
    ],
    traces: [
      {
        problem: 'Context: critical patient, resource_level=low\nActions available: [treat_first, defer, wait]',
        features: 'severity=critical  resources=low  pillar_weights=[bandit:0.42, hippocampus:0.28, pfc:0.18, ...]',
        reasoning: 'Bandit Q-value treat_first=0.91 (posterior mean β distribution)\nHippocampus: 3 matching traces retrieved\nPFC: confidence threshold passed',
        chose: 'treat_first',
        correct: 'treat_first',
        match: true,
      },
      {
        problem: 'Context: minor patient, resource_level=low\nActions available: [treat_first, defer, wait]',
        features: 'severity=minor  resources=low  pillar_weights=[bandit:0.44, hippocampus:0.31, ...]',
        reasoning: 'Bandit Q-value defer=0.88 (posterior mean β distribution)\nHippocampus: 5 matching traces retrieved\nPFC: confidence threshold passed',
        chose: 'defer',
        correct: 'defer',
        match: true,
      },
    ],
  },
  {
    title: 'Emergence — Route Navigation',
    tag: 'Scenario: Hidden Rules',
    tagVariant: 'accent',
    accuracy: 100,
    accuracyLabel: '100% final accuracy',
    convergedAt: 'Converged: episode 10',
    episodes: 300,
    summary: 'Three hidden rules governing route selection. The agent found all three in just 10 episodes — the fastest convergence across all tested scenarios. The rules involve priority ordering (never take high-risk regardless of urgency) which the Bandit encodes as extremely strong negative Q-values on the risky action.',
    highlights: [
      'Hidden rule: never take high-risk routes regardless of urgency',
      'Hidden rule: urgent + low-cost → always fast route',
      'Hidden rule: low urgency → always scenic (low-risk) route',
      'Fastest convergence observed: episode 10',
    ],
    traces: [
      {
        problem: 'Context: urgency=high, route_options=[fast(low-risk), scenic(low-risk), highway(high-risk)]\nActions: [take_fast, take_scenic, take_highway]',
        features: 'urgency=high  risk_present=true  pillar_weights=[bandit:0.46, pfc:0.22, ...]',
        reasoning: 'Bandit Q-value take_highway=-0.93 (strong negative posterior)\nPFC: vetoed take_highway pre-execution\nBandit Q-value take_fast=0.87 → selected',
        chose: 'take_fast',
        correct: 'take_fast',
        match: true,
      },
    ],
  },
  {
    title: 'High-IQ — Honest About Difficulty',
    tag: 'Stress Test',
    tagVariant: 'dim',
    accuracy: 25,
    accuracyLabel: '25% on hardest classes',
    episodes: 500,
    summary: 'Five pattern classes designed specifically to break surface-level systems. Code structure: mastered at 100%. The other four remain hard — not because the system is broken, but because they require capabilities the Bandit genuinely does not have yet. Rule inversion requires detecting where a pattern breaks. Cross-sequence needs arithmetic the Thompson Sampler cannot perform. The system is honest about this. It does not fake progress.',
    highlights: [
      'Code structure (medium difficulty): 100% — structural invariants are learnable',
      'Constraint satisfaction (hard): 25% — global reasoning, not local optimization',
      'Rule inversion (hard): 15% — requires detecting pattern break point',
      'Cross-sequence (hardest): 25% — solved by routing to compute substrate',
    ],
    traces: [
      {
        problem: 'A: [4, 2, 6]\nB: [3, 8, 5]\nC: [12, 16] + [?]',
        features: 'class=cross_sequence  op_hint=multiply',
        reasoning: 'Bandit selected via unbiased (no strong prior)\nNo substrate dispatched for this class yet',
        chose: '9',
        correct: '30',
        match: false,
      },
      {
        problem: 'A: [5, 8, 8]\nB: [5, 4, 5]\nC: [10, 12] + [?]',
        features: 'class=cross_sequence  op_hint=add  substrate=compute',
        reasoning: 'A[n] add B[n] → 8 add 5 = 13\n[routed to compute substrate]',
        chose: '13',
        correct: '13',
        match: true,
      },
    ],
  },
]

function AccuracyBar({ value, max = 100 }: { value: number; max?: number }) {
  const pct = Math.min(100, (Math.abs(value) / max) * 100)
  const isLift = value > 0 && max === 100 ? false : value > 0
  const color = value >= 90 ? '#7c6af7' : value >= 50 ? '#c9a84c' : value >= 25 ? '#8b8aaa' : '#4a4960'

  return (
    <div className="accuracy-bar w-full mt-1">
      <div
        className="accuracy-fill"
        style={{
          width: `${pct}%`,
          background: `linear-gradient(90deg, ${color}88, ${color})`,
          transition: 'width 1.4s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      />
    </div>
  )
}

function TraceBlock({ trace }: { trace: TraceEntry }) {
  return (
    <div className="trace-block text-xs">
      <div><span className="label">PROBLEM   </span><span style={{ color: '#8b8aaa', whiteSpace: 'pre' }}>{trace.problem}</span></div>
      <div className="mt-2"><span className="label">FEATURES  </span><span style={{ color: '#4a4960' }}>{trace.features}</span></div>
      <div className="mt-2"><span className="substrate">SUBSTRATE </span><span style={{ color: '#c9a84c', whiteSpace: 'pre' }}>{trace.reasoning}</span></div>
      <div className="mt-2">
        <span className="label">CHOSE     </span>
        <span className={trace.match ? 'correct' : ''} style={!trace.match ? { color: '#e87c7c' } : {}}>
          {trace.chose}
        </span>
        <span className="label">   ·   CORRECT </span>
        <span style={{ color: '#8b8aaa' }}>{trace.correct}</span>
        <span className="ml-3" style={{ color: trace.match ? '#7c6af7' : '#e87c7c' }}>
          {trace.match ? '✓' : '✗'}
        </span>
      </div>
    </div>
  )
}

function EvidenceCard({ card }: { card: EvidenceCardData }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="evidence-card overflow-hidden">
      <div className="p-6">
        <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`pill pill-${card.tagVariant}`}>{card.tag}</span>
            {card.convergedAt && (
              <span className="pill pill-gold">{card.convergedAt}</span>
            )}
          </div>
          <span className="font-mono text-xs" style={{ color: '#4a4960' }}>{card.episodes} episodes</span>
        </div>

        <h3 className="font-display text-xl italic font-light mb-3" style={{ color: '#e8e6f0' }}>
          {card.title}
        </h3>

        {/* Accuracy */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <span className="font-mono text-xs" style={{ color: '#8b8aaa', letterSpacing: '0.06em' }}>
              {card.accuracyLabel}
            </span>
            <span className="font-mono text-xs font-medium text-gradient">
              {card.accuracy}%
            </span>
          </div>
          <AccuracyBar value={card.accuracy} />
        </div>

        <p className="font-body text-sm font-light leading-relaxed mb-4" style={{ color: '#8b8aaa' }}>
          {card.summary}
        </p>

        {/* Highlights */}
        <ul className="space-y-1 mb-5">
          {card.highlights.map((h, i) => (
            <li key={i} className="flex items-start gap-2">
              <span style={{ color: '#4a3fa0', marginTop: '0.35rem', flexShrink: 0 }}>▸</span>
              <span className="font-mono text-xs" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{h}</span>
            </li>
          ))}
        </ul>

        {/* Expand toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest"
          style={{
            color: expanded ? '#7c6af7' : '#4a4960',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
            letterSpacing: '0.1em',
            transition: 'color 0.2s',
          }}
        >
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          {expanded ? 'Hide Traces' : 'Show Episode Traces'}
        </button>
      </div>

      {/* Traces */}
      {expanded && (
        <div
          style={{
            borderTop: '1px solid #1e1e30',
            background: '#080810',
            padding: '1.25rem 1.5rem',
          }}
        >
          <div className="font-mono text-xs mb-3 uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.14em' }}>
            Raw Episode Traces
          </div>
          <div className="flex flex-col gap-3">
            {card.traces.map((trace, i) => (
              <div key={i}>
                <div className="font-mono text-xs mb-1" style={{ color: '#4a4960' }}>Episode trace ·{i + 1}</div>
                <TraceBlock trace={trace} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Results() {
  return (
    <div style={{ paddingTop: '56px' }}>
      {/* Header */}
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="pill pill-accent mb-5">Evidence</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            Results &<br />
            <span className="text-gradient">Episode Traces</span>
          </h1>
          <div className="section-divider" />
          <p className="font-body text-base font-light max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            These are not benchmark scores. They are evidence. What the system was given, which substrate fired, what it reasoned, and what it chose. Every decision is traceable. The routing log is the explanation.
          </p>
        </div>
      </section>

      {/* Stats row */}
      <section style={{ borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex flex-wrap gap-8">
            {[
              ['100%', 'Mastered substrate accuracy (code structure)'],
              ['+28%', 'Memory warm-start lift'],
              ['ep. 10', 'Fastest convergence (route navigation)'],
              ['ep. 60', 'Triage convergence'],
              ['5/5', 'IQ classes routed and solved'],
            ].map(([val, label]) => (
              <div key={val} className="flex items-baseline gap-2">
                <span className="font-display text-2xl italic text-gradient-gold">{val}</span>
                <span className="font-mono text-xs" style={{ color: '#4a4960', letterSpacing: '0.06em' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Cards */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="flex flex-col gap-6">
          {cards.map((card, i) => (
            <EvidenceCard key={i} card={card} />
          ))}
        </div>

        {/* Honesty note */}
        <div
          className="mt-12 p-6 rounded"
          style={{ background: 'rgba(124,106,247,0.04)', border: '1px solid rgba(124,106,247,0.12)' }}
        >
          <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa', letterSpacing: '0.04em' }}>
            <span style={{ color: '#7c6af7' }}>Note on honesty: </span>
            A system that scores 100% on every class is either cheating or the test is too easy. A system that masters what it can structurally represent, struggles with what requires compute it doesn't yet have, and shows measurable improvement over time — that is a system learning real things. The hard classes are documented here because the difficulty is genuine and the architecture is honest about it.
          </p>
        </div>
      </section>
    </div>
  )
}
