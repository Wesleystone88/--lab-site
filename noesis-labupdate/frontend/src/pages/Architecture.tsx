import { architectureLayers, patternClasses, routingStates, memoryFiles } from '../data/results'

export default function Architecture() {
  return (
    <div style={{ paddingTop: '56px' }}>
      <section style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="max-w-5xl mx-auto px-6 py-14">
          <div className="pill pill-accent mb-5">System</div>
          <h1 className="font-display text-5xl md:text-6xl italic font-light leading-tight mb-4" style={{ color: '#e8e6f0' }}>
            Architecture<br /><span className="text-gradient">Seven Layers Deep</span>
          </h1>
          <div className="section-divider" />
          <p className="font-body text-base font-light max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
            A layered cognitive system where each layer has a single responsibility and a defined interface. Every component can be replaced independently. The system is built to match the physics of the problems it solves.
          </p>
        </div>
      </section>

      {/* Design principle */}
      <section style={{ borderBottom: '1px solid #1e1e30', background: '#0e0e1a' }}>
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row gap-8 md:gap-12 items-start">
            <div className="flex-1">
              <span className="font-mono text-xs uppercase tracking-widest mb-2 block" style={{ color: '#4a4960' }}>Single Design Principle</span>
              <p className="font-display text-xl italic font-light" style={{ color: '#e8e6f0' }}>
                "An LLM's weights are frozen. This system's state is always accreting."
              </p>
            </div>
            <div className="flex gap-8 shrink-0">
              {[['7', 'Layers'], ['5', 'NN Hooks'], ['4', 'Substrates'], ['6', 'Agent Pillars']].map(([n, l]) => (
                <div key={l} className="text-center">
                  <div className="font-display text-3xl italic text-gradient-gold">{n}</div>
                  <div className="font-mono text-xs mt-1" style={{ color: '#4a4960' }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Layer overview table */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-accent mb-4">Layer Overview</div>
        <h2 className="font-display text-3xl italic font-light mb-6" style={{ color: '#e8e6f0' }}>System Map</h2>
        <div className="evidence-card overflow-hidden">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e1e30', background: '#080810' }}>
                  {['Layer', 'Component', 'Role'].map(h => (
                    <th key={h} style={{ padding: '10px 16px', color: '#4a4960', textAlign: 'left', fontWeight: 400, letterSpacing: '0.08em' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {architectureLayers.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a', background: row.layer.includes('NN Engine') ? 'rgba(74,73,96,0.1)' : 'transparent' }}>
                    <td style={{ padding: '10px 16px', color: '#e8e6f0', whiteSpace: 'nowrap' }}>{row.layer}</td>
                    <td style={{ padding: '10px 16px', color: '#c9a84c' }}>{row.component}</td>
                    <td style={{ padding: '10px 16px', color: '#8b8aaa' }}>{row.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Pattern classes */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-dim mb-4">Environment Layer</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Five Pattern Classes</h2>
        <p className="font-body text-sm font-light mb-6 max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          The environment generates problems across five structural classes. The surface rotates — variable names, specific values, representations change — but the underlying pattern is invariant. Nothing downstream sees raw problem text.
        </p>
        <div className="evidence-card overflow-hidden mb-6">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e1e30', background: '#080810' }}>
                  {['Class', 'What it requires'].map(h => (
                    <th key={h} style={{ padding: '10px 16px', color: '#4a4960', textAlign: 'left', fontWeight: 400 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {patternClasses.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a' }}>
                    <td style={{ padding: '10px 16px', color: '#c9a84c', whiteSpace: 'nowrap' }}>{row.class}</td>
                    <td style={{ padding: '10px 16px', color: '#8b8aaa' }}>{row.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Feature schema */}
        <div className="font-mono text-xs mb-3 uppercase tracking-widest" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>_extract_structural_features() output schema (key fields)</div>
        <div className="trace-block">
          {`class:              cross_sequence | constraint_satisfaction | rule_inversion | structural_analogy | code_pattern_hybrid
surface:            numeric | symbolic | code
c_trend:            up | down | flat          [cross_seq]
a_vs_b:             a_bigger | b_bigger | equal [cross_seq]
op_hint:            add | sub | mul            [cross_seq]
relationship:       between_series             [cross_seq]
constraint_count:   3                          [constraint]
all_must_hold:      true                       [constraint]
has_divisibility:   true | false               [constraint]
has_parity:         true | false               [constraint]
pre_trend:          up | down                  [rule_inv]
inversion_detected: true | false               [rule_inv]
structural_type:    dependency | guard         [code]
inv_name:           dependency_order | guard_before_use [code]`}
        </div>
      </section>

      {/* Routing states */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-accent mb-4">Cognitive Router</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Routing States</h2>
        <p className="font-body text-sm font-light mb-6 max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          The router does not make decisions — it routes them. Every decision is in the log. Future states are defined now so the memory-compute hybrid can be built to match exactly.
        </p>
        <div className="evidence-card overflow-hidden">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.72rem' }}>
              <tbody>
                {routingStates.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0e0e1a', opacity: row.state.includes('future') ? 0.5 : 1 }}>
                    <td style={{ padding: '10px 16px', color: '#c9a84c', whiteSpace: 'nowrap', width: 220 }}>{row.state}</td>
                    <td style={{ padding: '10px 16px', color: '#8b8aaa' }}>{row.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Persistence / memory files */}
      <section className="max-w-5xl mx-auto px-6 py-14" style={{ borderBottom: '1px solid #1e1e30' }}>
        <div className="pill pill-gold mb-4">Persistence Layer</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>Memory Files</h2>
        <p className="font-body text-sm font-light mb-6 max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          State accumulates across sessions. The agent that starts run 2 is not the same as the agent that started run 1.
        </p>
        <div className="flex flex-col gap-4">
          {memoryFiles.map((f) => (
            <div key={f.file} className="evidence-card p-5 flex gap-4">
              <div className="shrink-0">
                <div className="font-mono text-xs" style={{ color: '#c9a84c' }}>{f.file}</div>
                <div className="font-mono text-xs mt-1" style={{ color: '#4a4960' }}>{f.size}</div>
              </div>
              <p className="font-mono text-xs leading-relaxed" style={{ color: '#8b8aaa' }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Persists vs resets */}
        <div className="grid md:grid-cols-2 gap-4 mt-6">
          <div className="evidence-card p-5">
            <div className="font-mono text-xs uppercase tracking-widest mb-3" style={{ color: '#7c6af7', letterSpacing: '0.12em' }}>Persists Across Sessions</div>
            {['Bandit Beta posteriors — accumulated action preferences per structural context',
              'BioRAG hippocampal traces (pinned) — high-salience episodic memories',
              'Hopfield attractor matrices — pattern energy landscape',
              'Glyph accuracy weights — what the system knows about each class',
              'Cards — episodic evidence for each substrate',
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-2 mb-1">
                <span style={{ color: '#4a3fa0', flexShrink: 0 }}>▸</span>
                <span className="font-mono text-xs" style={{ color: '#8b8aaa', lineHeight: 1.7 }}>{item}</span>
              </div>
            ))}
          </div>
          <div className="evidence-card p-5">
            <div className="font-mono text-xs uppercase tracking-widest mb-3" style={{ color: '#4a4960', letterSpacing: '0.12em' }}>Resets Each Session</div>
            {['Router routing_log (in-memory only — persistent log is a future hook)',
              'TFE temporal keys (fresh decay for each session)',
              'Working memory buffer (short-term, intentional)',
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-2 mb-1">
                <span style={{ color: '#4a4960', flexShrink: 0 }}>—</span>
                <span className="font-mono text-xs" style={{ color: '#4a4960', lineHeight: 1.7 }}>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* NN Hooks */}
      <section className="max-w-5xl mx-auto px-6 py-14">
        <div className="pill pill-dim mb-4">Future Extension</div>
        <h2 className="font-display text-3xl italic font-light mb-2" style={{ color: '#e8e6f0' }}>NN Engine Hooks</h2>
        <p className="font-body text-sm font-light mb-6 max-w-xl" style={{ color: '#8b8aaa', lineHeight: 1.8 }}>
          Five hook points are defined now so a neural engine can be built to match exactly. The interfaces are contracts. Nothing here is built yet — the NN engine is a separate package that slots into these hooks only.
        </p>
        <div className="flex flex-col gap-3">
          {[
            { hook: 'Hook 1 — nn_router.py', desc: 'replace static SUBSTRATE_MAP with learned prediction. Input: features dict. Output: (substrate, confidence). Falls back to static map if confidence < threshold.' },
            { hook: 'Hook 2 — nn_hippocampus.py', desc: 'replace Hopfield attractor with learned retrieval. Same encode/retrieve interface — weights inside instead of Hopfield matrices.' },
            { hook: 'Hook 3 — nn_bandit.py', desc: 'replace Thompson Sampling with continual-learning network. Same get_action interface. Must expose posteriors dict for PEE compatibility.' },
            { hook: 'Hook 4 — nn_prior.py', desc: 'replace manual conflict counting in memory-compute hybrid. Input: features + substrate_answer. Output: (state, confidence).' },
            { hook: 'Hook 5 — nn_metacog.py', desc: 'replace rule-based pillar trust weights. Input: pillar_name + recent_decisions. Output: trust weight 0.0–1.0.' },
          ].map((row, i) => (
            <div key={i} className="evidence-card p-4 flex gap-4" style={{ opacity: 0.7 }}>
              <span className="font-mono text-xs shrink-0 mt-0.5" style={{ color: '#4a4960' }}>{i + 1}</span>
              <div>
                <div className="font-mono text-xs mb-1" style={{ color: '#8b8aaa' }}>{row.hook}</div>
                <div className="font-mono text-xs" style={{ color: '#4a4960', lineHeight: 1.7 }}>{row.desc}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 p-4 rounded font-mono text-xs" style={{ background: 'rgba(74,63,160,0.06)', border: '1px solid rgba(74,63,160,0.15)', color: '#8b8aaa', lineHeight: 1.7 }}>
          Integration pattern: (1) Build nn_engine/nn_X.py implementing the exact interface above → (2) Test in isolation against deterministic baseline → (3) Slot in by replacing the one object instantiation site → (4) Add nn_X.save()/load() to PersistentMemory cycle → (5) Verify routing log format unchanged
        </div>
      </section>
    </div>
  )
}
