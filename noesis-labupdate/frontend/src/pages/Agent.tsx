import { sixPillars } from '../data/results'

export default function Agent() {
  return (
    <div style={{ paddingTop: '56px' }}>
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-5xl mx-auto px-6 py-14">
          <div className="pill pill-gold mb-5">Agent</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            SextBioRAG<br /><span className="text-gradient-gold">Six-Pillar Cognitive System</span>
          </h1>
          <div className="section-divider" style={{ background: 'linear-gradient(90deg, #c9a84c, transparent)' }} />
          <p className="font-body text-base font-light max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            The agent that handles decisions when the router finds no dedicated substrate. Not an LLM. No transformer weights, no token embeddings, no attention heads. Cannot be prompted. Learns through six cognitive pillars from binary feedback alone.
          </p>
        </div>
      </section>

      {/* What it is not */}
      <section style={{ borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[['✗', 'No gradient descent'], ['✗', 'No token embeddings'], ['✗', 'No prompt engineering'], ['✓', 'Binary feedback only — correct or incorrect, nothing else']].map(([icon, label]) => (
              <div key={label} className="flex items-start gap-2">
                <span className="font-mono text-sm shrink-0" style={{ color: icon === '✓' ? '#7c6af7' : '#4a4960' }}>{icon}</span>
                <span className="font-mono text-xs" style={{ color: icon === '✓' ? '#8b8aaa' : '#4a4960', lineHeight: 1.6 }}>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Public interface */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-dim mb-4">Public Interface</div>
        <h2 className="font-display text-3xl italic font-light mb-6" style={{ color: '#e8e6f0' }}>Decision Flow</h2>
        <div className="trace-block mb-6">
          {`choose_action(condition: Dict[str,str], actions: List[str]) -> Tuple[str, str]
  Returns (action, source)
  source indicates which pillar drove: explore | exploit | CME | PFC | etc.

update(condition, action, success: bool, step: int)
  Update all pillars from outcome.
  Bandit posteriors, hippocampal encoding, PEE surprise, CME memory.

save_state(filepath: str)
  Full serialization: bandit posteriors, BioRAG hippocampal traces + Hopfield matrices,
  PEE calibration, signal bus state.

load_state(filepath: str)
  Full restoration from saved state. Agent picks up exactly where it left off.

get_stats() -> Dict[str, Any]
  Returns pillar-level statistics for monitoring and debugging.`}
        </div>

        <div className="font-mono text-xs mb-3 uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>Signal bus — every call passes through all six pillars in sequence</div>
        <div className="trace-block">
          {`choose_action(condition, actions)
  ↓ CME.emit_bias(condition, actions)           → BiasSurface (hard blocks + soft-reduces)
  ↓ TFE.update()                                → TFEObservables (temporal decay weights)
  ↓ BioRAG.retrieve(condition, actions)         → PillarSignal (hippocampal attractor convergence)
  ↓ PEE.predict_from_beta(alpha, beta)          → prob, conf (locks prediction BEFORE action)
  ↓ bus.fuse([tfe, cme, rag], actions)          → Dict[str, float] (metacog trust-weighted fusion)
  ↓ PFC.evaluate(context, actions, fused, ...)  → PFCSignal (impulse control gate)
  ↓ Bandit.get_action(ctx_key, actions, ...)    → action, source, weights
  return action, source`}
        </div>
      </section>

      {/* Six pillars */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-gold mb-4">The Six Pillars</div>
        <h2 className="font-display text-3xl italic font-light mb-6" style={{ color: '#e8e6f0' }}>Pillar Descriptions</h2>
        <div className="flex flex-col gap-4">
          {sixPillars.map((p) => (
            <div key={p.num} className="evidence-card p-5">
              <div className="flex flex-wrap items-center gap-3 mb-3">
                <span className="font-mono text-xs" style={{ color: '#4a4960' }}>Pillar {p.num}</span>
                <span className="font-mono text-sm font-medium" style={{ color: '#c9a84c' }}>{p.name}</span>
                <span className="pill pill-dim">{p.full}</span>
              </div>
              <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa' }}>{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Hippocampal memory detail */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-dim mb-4">BioRAG — Biological Memory Detail</div>
        <h2 className="font-display text-3xl italic font-light mb-6" style={{ color: '#e8e6f0' }}>Hippocampal Interface</h2>
        <div className="trace-block mb-4">
          {`agent.rag.hippocampus.encode(context, action, success, salience)
  Stores episode in hippocampal index.
  Salience set by PEE surprise weight. High surprise = stronger encoding.

agent.rag.hippocampus.retrieve(context, actions, top_k, n_cycles) -> List[Tuple[MemoryTrace, float]]
  Hopfield attractor convergence over stored traces.
  Returns top_k most similar with confidence scores.
  Retrieval is convergence dynamics — not lookup.

agent.rag.hippocampus.consolidate(n_replays, max_capacity)
  Sleep consolidation. Replays high-salience traces into Hopfield weights.
  Called between sessions.

agent.rag.hippocampus.pin(trace_id) -> bool
  Pin a trace. Pinned traces never decay. Use for critical memories.

agent.rag.working_memory.add(action, success, salience)
  Working memory buffer (CAPACITY=7). Decays each tick. Short-term action context.`}
        </div>
        <div className="p-4 rounded font-mono text-xs" style={{ background: 'rgba(201,168,76,0.04)', border: '1px solid rgba(201,168,76,0.1)', color: '#c9a84c', lineHeight: 1.7 }}>
          Hopfield attractor dynamics: queries fall into the nearest energy basin. The memory landscape is shaped by experience. Pattern-completion behavior — partial or noisy queries still retrieve the most relevant stored episode.
        </div>
      </section>

      {/* Sext vs Quint */}
      <section className="max-w-5xl mx-auto px-6 py-14">
        <div className="pill pill-dim mb-4">Architecture Note</div>
        <h2 className="font-display text-3xl italic font-light mb-4" style={{ color: '#e8e6f0' }}>SextBioRAG vs QuintBioRAG</h2>
        <div className="evidence-card p-5">
          <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa' }}>
            The predecessor system, QuintBioRAG, operated on five pillars — omitting the PFC impulse control layer. SextBioRAG adds the PFC as the sixth pillar. The PFC evaluates action confidence before execution and vetoes low-confidence selections, returning control to the Bandit for resampling. This prevents the system from wasting episode budget on low-confidence exploratory actions when it has sufficient prior experience to be selective. The sixth pillar does not add intelligence — it adds discipline.
          </p>
        </div>
      </section>
    </div>
  )
}
