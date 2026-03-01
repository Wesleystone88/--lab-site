const layers = [
  {
    num: '01',
    name: 'Environment',
    subtitle: 'IQPatternEnv',
    tag: 'Input Boundary',
    tagVariant: 'dim',
    description: 'The environment generates problems, rotates surfaces, and extracts structural features. It is the input boundary of the system. Nothing downstream sees raw problem text — only the structured feature dictionary.',
    details: [
      'Five pattern classes: constraint satisfaction, rule inversion, structural analogy, code structure, cross-sequence',
      'Surface-invariant feature extraction — the pattern class stays constant while variable names and specific values rotate',
      '_extract_structural_features() is the most important method: class type, trend direction, operation hint, constraint flags',
      'Extensible by adding new pattern classes or new surfaces (visual, audio) — the router picks up automatically',
    ],
    principle: 'The router reads nothing but structural features. Surface change is invisible to everything downstream.',
  },
  {
    num: '02',
    name: 'CognitiveRouter',
    subtitle: 'Dispatch Layer',
    tag: 'Routing',
    tagVariant: 'accent',
    description: 'The router reads structural features, selects the substrate, calls it, and logs everything. It does not make decisions itself — it routes them. Every decision is in the log.',
    details: [
      'SUBSTRATE_MAP: static dispatch table mapping feature patterns to substrates',
      'Routing log entry: episode, class, substrate selected, features, outcome — appended after every call',
      'Routing states: DISPATCH (substrate found), FALLBACK (no match, agent handles), OVERRIDE (memory prior takes precedence)',
      'Future hook: NN router replaces static SUBSTRATE_MAP with learned prediction — same interface, weights inside',
    ],
    principle: 'The routing log is the explanation. If you want to know why the system chose X, read the log.',
  },
  {
    num: '03',
    name: 'Substrates',
    subtitle: 'Purpose-Built Solvers',
    tag: 'Reasoning',
    tagVariant: 'accent',
    description: 'Every substrate exposes exactly one function. The interface is identical across all four. Adding a new substrate means creating a file with this function and adding one line to the dispatch table.',
    details: [
      'compute — arithmetic substrate: detects operation (add, subtract, multiply, parity) and applies it to cross-sequence problems',
      'solver — constraint satisfaction: handles divisibility, digit sums, range constraints, parity — finds the single answer satisfying all rules simultaneously',
      'decomposer — transform algebra: decomposes compound A→B transformations and re-applies them to C→?',
      'memory_probe — temporal trace: retrieves sequence history for rule-inversion class problems',
    ],
    principle: 'Nothing is always on. Each substrate is called only when the router identifies its pattern class.',
  },
  {
    num: '04',
    name: 'SextBioRAG Agent',
    subtitle: '6-Pillar Cognitive System',
    tag: 'Learning',
    tagVariant: 'gold',
    description: 'The agent is the Bandit fallback and the biological memory layer. When the router cannot dispatch to a substrate, the agent handles the decision through six coordinated pillars inspired by neuroscience.',
    details: [
      'Thompson Sampling bandit: Beta distributions over every action in every context — uncertainty drives exploration, confidence drives exploitation',
      'Hopfield attractor memory (hippocampus): queries fall into the nearest energy basin — retrieval is convergence dynamics, not lookup',
      'Dopaminergic surprise signal: high-surprise outcomes get deeper encoding — exactly like emotional memory consolidation',
      'Prefrontal cortex (impulse control): vetoes low-confidence actions before execution — why SextBioRAG outperforms QuintBioRAG',
      'Signal bus: all six pillars contribute weighted scores to a unified fusion layer before any action is selected',
    ],
    principle: 'Every Q-value in every policy table was earned from binary outcome feedback alone. Correct or incorrect. Nothing else.',
  },
  {
    num: '05',
    name: 'Persistence Layer',
    subtitle: 'Glyphs + Cards',
    tag: 'Memory',
    tagVariant: 'gold',
    description: 'The persistence layer is what separates this from an LLM. State accumulates across sessions. The agent that starts run 2 is not the same as the agent that started run 1.',
    details: [
      'Glyphs: structural invariants discovered through experience — one per pattern class, encoding the learned signature',
      'Cards: high-salience episodic memories — pinned correct episodes from each substrate that survived the confidence threshold',
      'Bandit state: Beta distribution posteriors persisted across sessions — action preferences that represent real accumulated experience',
      'What resets: episode counter, surface-specific context. What persists: everything learned.',
    ],
    principle: 'An LLM\'s weights are frozen. This system\'s state is always accreting.',
  },
  {
    num: '06',
    name: 'Memory-Compute Hybrid',
    subtitle: 'Architecture Defined',
    tag: 'Planned',
    tagVariant: 'dim',
    description: 'The insight: compute cannot use memory, but memory can remember what compute did. The router wraps every substrate call with a memory layer that tracks outcomes per structural context and earns authority to influence routing over time.',
    details: [
      'Five states: DEFER (memory not confident), CONFIRM (memory agrees with substrate), CONFLICT (disagree — substrate wins), OVERRIDE (memory earned authority), LEARN (outcome recorded)',
      'Override threshold: the one deliberately-set parameter — everything else derived from conflict history',
      'Memory prior tracks per-substrate context outcomes — cross-substrate patterns possible in future extension',
    ],
    principle: 'Memory earns routing authority over time. It does not start with it.',
  },
  {
    num: '07',
    name: 'NN Engine Hooks',
    subtitle: 'Future Extension Points',
    tag: 'Future',
    tagVariant: 'dim',
    description: 'Five hook points are defined now so a neural engine can be built to match exactly. Nothing here is built yet. These are contracts — the interfaces exist, the implementations do not.',
    details: [
      'Hook 1 — NN Router: replace static SUBSTRATE_MAP with learned prediction (features → substrate, confidence)',
      'Hook 2 — NN Hippocampus: replace Hopfield attractor with learned retrieval — same encode/retrieve interface',
      'Hook 3 — NN Bandit: replace Thompson Sampling with continual-learning network — same get_action interface',
      'Hook 4 — NN Memory Prior: replace counting logic with learned context-to-authority prediction',
      'Hook 5 — NN Metacognitive Trust: replace rule-based pillar weights with learned trust dynamics',
    ],
    principle: 'The NN engine connects through hook points only. It can be developed, tested, and versioned independently.',
  },
]

export default function Architecture() {
  return (
    <div style={{ paddingTop: '56px' }}>
      {/* Header */}
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="pill pill-accent mb-5">System</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            Architecture<br />
            <span className="text-gradient">Seven Layers Deep</span>
          </h1>
          <div className="section-divider" />
          <p className="font-body text-base font-light max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            A layered cognitive system where each layer has a single responsibility and a defined interface. Every component can be replaced independently. The system is built to match the physics of the problems it solves — not to memorize their surface.
          </p>
        </div>
      </section>

      {/* Design principle callout */}
      <section style={{ borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row gap-6 md:gap-12">
            <div className="flex-1">
              <span className="font-mono text-xs uppercase tracking-widest mb-2 block" style={{ color: '#4a4960' }}>Single Design Principle</span>
              <p className="font-display text-xl italic font-light" style={{ color: '#e8e6f0' }}>
                "Match the architecture to the problem's physics — not to its surface."
              </p>
            </div>
            <div className="flex gap-6 md:gap-10 shrink-0">
              {[['7', 'Layers'], ['5', 'NN Hooks'], ['4', 'Substrates'], ['6', 'Agent Pillars']].map(([n, l]) => (
                <div key={l} className="text-center">
                  <div className="font-display text-3xl italic text-gradient-gold">{n}</div>
                  <div className="font-mono text-xs mt-1" style={{ color: '#4a4960', letterSpacing: '0.08em' }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Layer walkthrough */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="flex flex-col gap-0">
          {layers.map((layer, i) => (
            <div key={layer.num} className="layer-node pb-10">
              <div className="evidence-card p-6">
                <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs" style={{ color: '#4a4960' }}>Layer {layer.num}</span>
                    <span className={`pill pill-${layer.tagVariant}`}>{layer.tag}</span>
                  </div>
                </div>

                <h2 className="font-display text-2xl italic font-light mb-1" style={{ color: '#e8e6f0' }}>
                  {layer.name}
                </h2>
                <div className="font-mono text-xs mb-4" style={{ color: '#4a4960', letterSpacing: '0.08em' }}>
                  {layer.subtitle}
                </div>

                <p className="font-body text-sm font-light leading-relaxed mb-4" style={{ color: '#8b8aaa' }}>
                  {layer.description}
                </p>

                <ul className="space-y-2 mb-5">
                  {layer.details.map((d, j) => (
                    <li key={j} className="flex items-start gap-2">
                      <span style={{ color: '#4a3fa0', marginTop: '0.35rem', flexShrink: 0 }}>▸</span>
                      <span className="font-mono text-xs" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{d}</span>
                    </li>
                  ))}
                </ul>

                <div
                  className="p-3 rounded font-mono text-xs"
                  style={{
                    background: 'rgba(124,106,247,0.04)',
                    border: '1px solid rgba(124,106,247,0.1)',
                    color: '#7c6af7',
                    letterSpacing: '0.04em',
                    lineHeight: 1.6,
                  }}
                >
                  ↳ {layer.principle}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
