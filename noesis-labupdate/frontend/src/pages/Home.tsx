import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { ArrowRight, ChevronRight, Cpu, Network, Database, BrainCircuit, Activity, Eye, FileText, CheckCircle2 } from 'lucide-react'

function AnimatedStat({ value, label, delay = 0, suffix = '' }: { value: string; label: string; delay?: number, suffix?: string }) {
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
      className="flex flex-col gap-2"
    >
      <div className="font-display text-4xl md:text-5xl font-light text-gradient flex items-baseline gap-1">
        {value}
        {suffix && <span className="text-xl text-[#7c6af7] opacity-80">{suffix}</span>}
      </div>
      <div className="font-mono text-xs uppercase tracking-widest" style={{ color: '#8b8aaa', letterSpacing: '0.12em' }}>{label}</div>
    </div>
  )
}

function PillarCard({ icon: Icon, num, title, desc }: { icon: any, num: string, title: string, desc: string }) {
  return (
    <div className="evidence-card p-6 flex flex-col gap-4 group h-full">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-xs" style={{ color: '#4a4960' }}>{num}</span>
        <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: 'rgba(124,106,247,0.1)' }}>
          <Icon size={16} color="#7c6af7" />
        </div>
      </div>
      <h3 className="font-display text-lg tracking-wide" style={{ color: '#e8e6f0' }}>{title}</h3>
      <p className="font-body text-sm font-light flex-1" style={{ color: '#8b8aaa', lineHeight: 1.6 }}>{desc}</p>
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
    <div style={{ paddingTop: '56px', backgroundColor: '#050508' }}>
      {/* Hero */}
      <section
        className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden"
      >
        {/* Dynamic ambient glow */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `radial-gradient(ellipse 800px 600px at ${glowPos.x}% ${glowPos.y}%, rgba(124,106,247,0.05) 0%, transparent 60%)`,
            transition: 'background 0.4s ease-out',
          }}
        />

        {/* Grid lines (Terminal aesthetic) */}
        <div
          className="absolute inset-0 pointer-events-none opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />

        <div className="relative z-10 text-center px-6 max-w-5xl mx-auto flex flex-col items-center">

          <div className="mb-6 flex items-center gap-2 px-3 py-1 rounded-full border border-[#1e1e30] bg-[#0a0a0f]">
            <span className="w-2 h-2 rounded-full bg-[#7c6af7] animate-pulse" />
            <span className="font-mono text-[10px] uppercase tracking-wider text-[#8b8aaa]">System Online · Confirmed</span>
          </div>

          <h1
            className="font-display text-7xl md:text-9xl font-light tracking-tight mb-4"
            style={{
              color: '#ffffff',
              background: 'linear-gradient(180deg, #ffffff 0%, #a8a8bb 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.02em'
            }}
          >
            NOESIS
          </h1>

          <div className="flex items-center gap-4 mb-8">
            <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-[#4a4960]" />
            <span className="font-mono text-sm uppercase tracking-[0.2em] text-[#7c6af7]">
              Routed Reasoning Architecture
            </span>
            <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-[#4a4960]" />
          </div>

          <p className="font-body text-xl font-light max-w-2xl mx-auto leading-relaxed mb-12 text-[#8b8aaa]">
            A new class of reasoning system. One that expects structural invariants, accumulates genuine experience, and knows what it doesn't know.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-6">
            <Link
              to="/architecture"
              className="group flex items-center gap-3 font-mono text-xs uppercase tracking-widest px-6 py-4 rounded bg-[#ffffff] text-[#050508] transition-all hover:bg-[#e0e0e0]"
            >
              Examine Architecture <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/results"
              className="flex items-center gap-3 font-mono text-xs uppercase tracking-widest px-6 py-4 rounded border border-[#2a2a40] text-[#a8a8bb] transition-all hover:border-[#7c6af7] hover:text-[#ffffff]"
            >
              View Evidence <FileText size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* Primary Metrics (Evidence) */}
      <section className="border-y border-[#1e1e30] bg-[#08080c] relative z-10">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-12 lg:gap-8">
            <AnimatedStat value="98" suffix="–100%" label="Accuracy on hard constraint classes" delay={100} />
            <AnimatedStat value="5" label="Dedicated purpose-built substrates" delay={200} />
            <AnimatedStat value="+28" suffix="%" label="Warm-start memory gain (Bandit)" delay={300} />
            <AnimatedStat value="100" suffix="%" label="Traceable routing receipts" delay={400} />
          </div>
        </div>
      </section>

      {/* Core Principle / The Problem */}
      <section className="max-w-6xl mx-auto px-6 py-32">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          <div>
            <div className="pill pill-accent mb-6 inline-block">The Paradigm Shift</div>
            <h2 className="font-display text-4xl md:text-5xl font-light leading-tight mb-8 text-[#e8e6f0]">
              Every major system today assumes one mechanism handles everything. <span className="text-[#8b8aaa]">We do not.</span>
            </h2>
            <div className="space-y-6 font-body text-base font-light text-[#8b8aaa] leading-relaxed">
              <p>
                The same process that recalls a fact is not the optimal process to satisfy a simultaneous constraint or trace an inverted sequence. Yet current paradigms force all reasoning through a single, opaque function.
              </p>
              <p>
                Noesis is built on strictly routed cognition. Different problems require different cognitive instruments. Before computation begins, the system identifies the structural class of the problem, and routes it to the specific substrate engineered to solve it.
              </p>
              <p className="text-[#e8e6f0] border-l-2 border-[#7c6af7] pl-4 italic">
                Compute when compute is required. Memory when memory is required. The rest stays lean and honest.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { title: 'Honest Failure', desc: 'When the system fails, you know exactly which substrate failed and why. No silent drift.' },
              { title: 'Genuine Uncertainty', desc: 'Uncertainty is a real epistemic state, not a hallucinated confidence score.' },
              { title: 'Substrate Appropriate', desc: 'Constraint problems go to constraint solvers. Arithmetic to arithmetic modules.' },
              { title: 'Persistent Accumulation', desc: 'States accrete across sessions. The agent that starts run 2 is not the same as run 1.' },
            ].map((feature, i) => (
              <div key={i} className="evidence-card p-6 flex flex-col gap-3">
                <CheckCircle2 size={18} className="text-[#7c6af7]" />
                <h4 className="font-display tracking-wide text-[#e8e6f0]">{feature.title}</h4>
                <p className="font-body text-xs text-[#8b8aaa] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The Agent (SextBioRAG) */}
      <section className="bg-[#08080c] border-y border-[#1e1e30] py-32 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-1/2 h-full bg-[radial-gradient(ellipse_at_center,rgba(124,106,247,0.03)_0%,transparent_70%)] pointer-events-none" />
        <div className="max-w-6xl mx-auto px-6 relative z-10">
          <div className="max-w-3xl mb-16">
            <span className="font-mono text-xs uppercase tracking-widest text-[#7c6af7] mb-4 block">The Agent Layer</span>
            <h2 className="font-display text-4xl font-light text-[#ffffff] mb-6">
              SextBioRAG: A 6-Pillar Cognitive System
            </h2>
            <p className="font-body text-[#8b8aaa] text-lg font-light leading-relaxed">
              The agent learning layer of Noesis utilizes six pillars inspired by biological neuroscience. No gradient descent. No prompting. No language models. Learning emerges strictly through network energy landscapes, memory staleness, and dopaminergic error signals.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <PillarCard
              num="01" icon={Database} title="Constrained Memory (CME)"
              desc="Declarative rule memory with hard blocks. Acts as the factual grounding layer."
            />
            <PillarCard
              num="02" icon={Network} title="Action Bandit"
              desc="Thompson Sampling. Handles procedural action selection under uncertainty."
            />
            <PillarCard
              num="03" icon={Activity} title="Temporal Field (TFE)"
              desc="Time-aware staleness and recency weighting governing the decay of context."
            />
            <PillarCard
              num="04" icon={Cpu} title="Prediction Error (PEE)"
              desc="Computes dopaminergic surprise signals based on expectation vs actual outcomes."
            />
            <PillarCard
              num="05" icon={BrainCircuit} title="Episodic Attractor (BioRAG)"
              desc="Hopfield attractor network. Stores and retrieves episodes via energy landscape dynamics."
            />
            <PillarCard
              num="06" icon={Eye} title="Prefrontal Cortex (PFC)"
              desc="Impulse control and metacognitive self-calibration. Halts confident but wrong execution vectors."
            />
          </div>
        </div>
      </section>

      {/* The Receipt (Traceability) */}
      <section className="max-w-6xl mx-auto px-6 py-32">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div className="order-2 lg:order-1">
            <div className="rounded-lg border border-[#2a2a40] bg-[#0a0a0f] overflow-hidden font-mono text-[13px] leading-relaxed shadow-2xl">
              <div className="bg-[#101018] px-4 py-3 border-b border-[#2a2a40] flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#3a3a4d]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#3a3a4d]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#3a3a4d]" />
                </div>
                <span className="ml-4 text-[#8b8aaa] text-xs">trace_record_0492.log</span>
              </div>
              <div className="p-6 text-[#a8a8bb]">
                <div className="mb-4">
                  <span className="text-[#5c5c77] block mb-1"># Problem given</span>
                  <div>Series A: [6, 8, 6] <br />Series B: [7, 6, 6] <br />Series C: [42, 48, ?]</div>
                </div>

                <div className="mb-4 pl-4 border-l border-[#2a2a40]">
                  <span className="text-[#5c5c77] block mb-1"># Structure detected</span>
                  <div className="text-[#e8e6f0]">Class: <span className="text-[#7c6af7]">arithmetic dependency</span></div>
                  <div>Trend: rising · Magnitude: larger</div>
                </div>

                <div className="mb-4 pl-4 border-l border-[#2a2a40]">
                  <span className="text-[#5c5c77] block mb-1"># Substrate called</span>
                  <div className="text-emerald-400">→ Arithmetic_Module</div>
                </div>

                <div className="mb-4 pl-8 border-l border-[#2a2a40]">
                  <span className="text-[#5c5c77] block mb-1"># Reasoning recorded</span>
                  <div>A[n] × B[n] = C[n]</div>
                  <div className="text-[#5c5c77]">verified against [42, 48]</div>
                  <div>6 × 6 = 36</div>
                </div>

                <div>
                  <span className="text-[#5c5c77] block mb-1"># Answer returned</span>
                  <div className="text-white bg-[#ffffff10] inline-block px-2 py-0.5 rounded">36 · Correct</div>
                </div>
              </div>
            </div>
          </div>

          <div className="order-1 lg:order-2">
            <h2 className="font-display text-4xl md:text-5xl font-light text-[#e8e6f0] mb-6">
              Every answer comes with a receipt.
            </h2>
            <div className="space-y-4 font-body text-base font-light text-[#8b8aaa] leading-relaxed">
              <p>
                A system that scores 100% with no trace tells you nothing about whether it actually understood the problem. A system that scores 98% with a full trace tells you exactly what it understood, where it succeeded, and — when it fails — precisely why.
              </p>
              <p>
                In Noesis, the trace exists because routing happened. It is not an interpretability layer added afterward. You can read which structural class was detected, which substrate was triggered, what it computed, and what it returned.
              </p>
              <Link
                to="/results"
                className="inline-flex items-center gap-2 mt-4 font-mono text-xs uppercase tracking-widest text-[#7c6af7] hover:text-[#a89df9] transition-colors"
                style={{ letterSpacing: '0.12em' }}
              >
                View 500+ Episode Traces <ChevronRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Research Transparency / Disclaimer */}
      <section className="py-12 border-t border-[#1e1e30]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6 opacity-60 hover:opacity-100 transition-opacity">
            <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#7c6af7] whitespace-nowrap">
              Research Transparency
            </div>
            <p className="font-body text-xs font-light text-[#8b8aaa] leading-relaxed italic border-l border-[#1e1e30] pl-6">
              Noesis Lab is a research-focused initiative aiming to build a new class of reasoning system. We do not promote "AGI" hype, nor do we intend to replace existing human expertise or systems. Our focus is on structural invariants, genuine experience, and honest failure modes.
            </p>
          </div>
        </div>
      </section>

      {/* Name & Affiliation Notice */}
      <section className="py-12 bg-[#080810]/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="max-w-3xl border-l border-[#7c6af7]/30 pl-8">
            <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#7c6af7] mb-6">
              Name & Affiliation Notice
            </h3>
            <div className="space-y-4 font-body text-sm font-light text-[#8b8aaa] leading-relaxed">
              <p>
                The name <span className="text-[#e8e6f0] font-normal">νόησις</span> (Greek: noetic apprehension; direct intellectual insight) is used here in its original philosophical sense.
              </p>
              <p>
                This project is not affiliated with, endorsed by, or connected to any commercial organizations or consultancies operating under the Latinized name “Noesis.”
              </p>
              <p>
                We recognize that several such organizations provide excellent professional services in their respective domains. <span className="text-[#e8e6f0] font-normal">νόησις Lab</span> exists in a distinct context: as an independent research and experimental architecture focused on cognitive systems, reasoning substrates, and first-principles design.
              </p>
              <p className="text-[12px] opacity-70">
                Similarity in etymology reflects a shared linguistic root, not a shared entity, offering, or market.
              </p>
            </div>
          </div>
        </div>
      </section>

    </div>
  )
}
