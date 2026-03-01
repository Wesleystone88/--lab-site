const pillars = [
  {
    num: '01',
    name: 'Thompson Sampling Bandit',
    bio: 'Striatal Reward Learning',
    description: 'Maintains Beta distributions over every action in every context. Uncertainty drives exploration early; confidence drives exploitation as posteriors narrow. Every Q-value is earned from outcome feedback — not initialized, not prompted.',
    detail: 'The Bandit is the core decision mechanism. Each context key maps to a set of Beta(α, β) distributions — one per action. On each episode, it samples from those distributions and selects the highest draw. A correct outcome increments α; incorrect increments β. Over time, the distributions tighten around the true best action. This is not approximation — it is the correct Bayesian update.',
    capability: 'Learns stable context-to-action mappings from binary feedback. Transfers across sessions via posterior persistence.',
  },
  {
    num: '02',
    name: 'Hippocampal Memory (BioRAG)',
    bio: 'Episodic Memory Retrieval',
    description: 'Queries fall into the nearest energy basin. Retrieval is convergence dynamics — not lookup. The memory landscape is shaped by accumulated experience and reorganizes as new episodes are encoded.',
    detail: 'The hippocampal index uses Hopfield attractor dynamics. Encoded experiences become energy minima in a high-dimensional space. At retrieval time, the query pattern is evolved until it converges to the nearest stable attractor. This produces pattern-completion behavior: partial or noisy queries still retrieve the most relevant stored experience.',
    capability: 'Pattern completion. Retrieves relevant past episodes even under partial or surface-varied queries.',
  },
  {
    num: '03',
    name: 'Dopaminergic Surprise Signal',
    bio: 'Prediction Error Encoding (PEE)',
    description: 'Publishes encoding weight to the signal bus proportional to outcome surprise. High-surprise outcomes receive deeper hippocampal encoding — exactly like emotional memory consolidation in biological systems.',
    detail: 'The PEE pillar computes the difference between predicted outcome probability and actual outcome. High prediction error (surprise) triggers elevated encoding weight on the signal bus. The hippocampus reads this weight and deepens the trace for high-surprise episodes. Low-surprise outcomes — those the system already confidently predicts — receive shallower encoding.',
    capability: 'Prioritizes encoding of informative experiences over redundant confirmation.',
  },
  {
    num: '04',
    name: 'Prefrontal Cortex (Impulse Control)',
    bio: 'Executive Veto',
    description: 'Evaluates action confidence before execution. Vetoes low-confidence selections, returning control to the Bandit for resampling. This is the 6th pillar that separates SextBioRAG from QuintBioRAG.',
    detail: 'The PFC pillar computes a confidence score from the current action selection. If the score falls below a calibrated threshold, the pillar issues a veto on the signal bus. The Bandit resamples — drawing from a different region of its uncertainty. This prevents the system from wasting budget on low-information exploratory actions when it has sufficient prior experience to be selective.',
    capability: 'Reduces wasted episodes on low-confidence exploratory actions. Measurably improves sample efficiency.',
  },
  {
    num: '05',
    name: 'Contextual Memory Engine (CME)',
    bio: 'Working Memory',
    description: 'Tracks contextual features across the current episode sequence. Provides weighted signal to the bus based on contextual similarity to recent high-value outcomes.',
    detail: 'The CME maintains a sliding window of recent episode contexts and outcomes. When the current context has high similarity to recent successful contexts, the CME contributes a positive weight signal to the fusion layer. When context matches recent failures, it contributes a negative signal (cme_weight_neg). This provides short-term contextual awareness that complements the Bandit\'s long-term learned priors.',
    capability: 'Short-term contextual awareness. Modulates Bandit selection based on recent episode history.',
  },
  {
    num: '06',
    name: 'Signal Bus (Pillar Fusion)',
    bio: 'Integration Layer',
    description: 'All five pillars contribute weights to a unified signal bus before any action executes. The final selection is the fusion of all active signals — no single pillar acts alone.',
    detail: 'The signal bus collects pillar contributions as a weighted sum. Each pillar contributes its weight signal and a trust score. The metacognitive layer adjusts pillar trust over time based on predictive accuracy — pillars that reliably signal correct actions gain trust weight; pillars with poor predictive accuracy lose it. Final action selection emerges from this weighted fusion.',
    capability: 'Unified decision emergence from distributed cognitive signals. No single-point failure.',
  },
]

export default function Agent() {
  return (
    <div style={{ paddingTop: '56px' }}>
      {/* Header */}
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="pill pill-gold mb-5">Agent</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            SextBioRAG<br />
            <span className="text-gradient-gold">Six-Pillar Cognitive System</span>
          </h1>
          <div className="section-divider" style={{ background: 'linear-gradient(90deg, #c9a84c, transparent)' }} />
          <p className="font-body text-base font-light max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            The agent that handles decisions when the router finds no dedicated substrate. Not an LLM. No transformer weights, no token embeddings, no attention heads. Cannot be prompted. Learns through six cognitive pillars inspired by biological neuroscience.
          </p>
        </div>
      </section>

      {/* What it is not */}
      <section style={{ borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-6xl mx-auto px-6 py-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              ['✗', 'No gradient descent'],
              ['✗', 'No token embeddings'],
              ['✗', 'No prompt engineering'],
              ['✓', 'Binary feedback only'],
            ].map(([icon, label]) => (
              <div key={label} className="flex items-center gap-2">
                <span
                  className="font-mono text-sm"
                  style={{ color: icon === '✓' ? '#7c6af7' : '#4a4960' }}
                >
                  {icon}
                </span>
                <span className="font-mono text-xs" style={{ color: icon === '✓' ? '#8b8aaa' : '#4a4960' }}>
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Decision flow */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="mb-10">
          <h2 className="font-display text-3xl italic font-light mb-3" style={{ color: '#e8e6f0' }}>
            Decision Flow
          </h2>
          <p className="font-body text-sm font-light" style={{ color: '#8b8aaa', lineHeight: 1.8, maxWidth: '520px' }}>
            Every call to choose_action passes through all six pillars in sequence. Each contributes weights to the signal bus. The final decision emerges from the weighted fusion — no single pillar acts alone.
          </p>
        </div>

        {/* Flow diagram */}
        <div
          className="p-6 rounded mb-12"
          style={{ background: '#080810', border: '1px solid #1e1e30' }}
        >
          <div className="font-mono text-xs" style={{ color: '#4a4960', lineHeight: 2.2 }}>
            <div>
              <span style={{ color: '#8b8aaa' }}>choose_action(context, actions)</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#7c6af7' }}>hippocampus</span>
              <span style={{ color: '#4a4960' }}>.retrieve(context) → episodic_matches</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#7c6af7' }}>pee</span>
              <span style={{ color: '#4a4960' }}>.compute_surprise(context) → encoding_weight</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#7c6af7' }}>cme</span>
              <span style={{ color: '#4a4960' }}>.get_context_weight(context) → ctx_signal</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#7c6af7' }}>bus</span>
              <span style={{ color: '#4a4960' }}>.fuse_signals([hippocampus, pee, cme, ...]) → weights</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#7c6af7' }}>bandit</span>
              <span style={{ color: '#4a4960' }}>.get_action(context, actions, bus_weights) → action</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#c9a84c' }}>pfc</span>
              <span style={{ color: '#4a4960' }}>.evaluate_confidence(action) → [pass | veto]</span>
            </div>
            <div style={{ paddingLeft: '2rem' }}>
              ↓ <span style={{ color: '#8b8aaa' }}>return action, source, pillar_weights</span>
            </div>
          </div>
        </div>

        {/* Pillars */}
        <div className="flex flex-col gap-6">
          {pillars.map((pillar) => (
            <div key={pillar.num} className="evidence-card p-6">
              <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs" style={{ color: '#4a4960' }}>Pillar {pillar.num}</span>
                  <span className="pill pill-dim">{pillar.bio}</span>
                </div>
              </div>

              <h3 className="font-display text-xl italic font-light mb-1" style={{ color: '#e8e6f0' }}>
                {pillar.name}
              </h3>

              <p className="font-body text-sm font-light leading-relaxed mb-3" style={{ color: '#8b8aaa' }}>
                {pillar.description}
              </p>

              <p className="font-body text-sm font-light leading-relaxed mb-4" style={{ color: '#4a4960', fontStyle: 'italic' }}>
                {pillar.detail}
              </p>

              <div
                className="p-3 rounded font-mono text-xs"
                style={{
                  background: 'rgba(201,168,76,0.04)',
                  border: '1px solid rgba(201,168,76,0.1)',
                  color: '#c9a84c',
                  letterSpacing: '0.04em',
                }}
              >
                ↳ {pillar.capability}
              </div>
            </div>
          ))}
        </div>

        {/* Sext vs Quint note */}
        <div
          className="mt-8 p-5 rounded"
          style={{ background: 'rgba(124,106,247,0.04)', border: '1px solid rgba(124,106,247,0.12)' }}
        >
          <div className="font-mono text-xs mb-2 uppercase tracking-widest" style={{ color: '#7c6af7', letterSpacing: '0.12em' }}>
            Why Six Pillars vs Five
          </div>
          <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa' }}>
            The predecessor system, QuintBioRAG, operated on five pillars — omitting the PFC impulse control layer. SextBioRAG adds the prefrontal veto as the sixth pillar. The measured improvement: the PFC veto prevents the system from wasting episode budget on low-confidence exploratory actions when it has sufficient prior experience to be selective. The sixth pillar does not add intelligence — it adds discipline.
          </p>
        </div>
      </section>
    </div>
  )
}
