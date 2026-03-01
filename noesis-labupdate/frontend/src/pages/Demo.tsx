import { useState, useEffect, useCallback } from 'react'
import { Play, SkipForward, SkipBack, Zap, RotateCcw, ChevronRight } from 'lucide-react'
import { scenarios, type EpisodeTrace, type PillarSignal } from '../data/demoData'
import { generateProblem, simulatePipeline, resetSimulation, type SimulationResult } from '../data/simulation'

const PILLAR_COLORS: Record<string, string> = {
    TFE: '#f59e0b',
    CME: '#3b82f6',
    BioRAG: '#8b5cf6',
    PEE: '#ef4444',
    PFC: '#10b981',
    Bandit: '#f97316',
}

const PILLAR_ICONS: Record<string, string> = {
    TFE: '⏱',
    CME: '📋',
    BioRAG: '🧠',
    PEE: '⚡',
    PFC: '🛡',
    Bandit: '🎯',
}

function PipelineNode({ signal, active, revealed }: { signal: PillarSignal; active: boolean; revealed: boolean }) {
    const color = PILLAR_COLORS[signal.pillar] || '#7c6af7'

    return (
        <div
            className="relative transition-all duration-500"
            style={{
                opacity: revealed ? 1 : 0.2,
                transform: active ? 'scale(1.05)' : 'scale(1)',
            }}
        >
            <div
                className="rounded-lg border p-4 transition-all duration-500"
                style={{
                    borderColor: active ? color : revealed ? `${color}40` : '#1e1e30',
                    background: active ? `${color}15` : '#0a0a0f',
                    boxShadow: active ? `0 0 20px ${color}30` : 'none',
                }}
            >
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{PILLAR_ICONS[signal.pillar]}</span>
                    <span className="font-mono text-xs font-medium" style={{ color }}>{signal.pillar}</span>
                    <span className="font-mono text-[10px] ml-auto" style={{ color: '#8b8aaa' }}>
                        {(signal.confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <div className="font-mono text-[11px]" style={{ color: '#8b8aaa' }}>{signal.description}</div>
                {revealed && (
                    <div className="font-mono text-[10px] mt-2 leading-relaxed" style={{ color: '#a8a8bb' }}>
                        {signal.detail}
                    </div>
                )}
            </div>
            {active && (
                <div
                    className="absolute -bottom-3 left-1/2 -translate-x-1/2"
                    style={{ color }}
                >
                    <ChevronRight size={14} className="rotate-90" />
                </div>
            )}
        </div>
    )
}

function TraceOutput({ trace, revealedPillars }: { trace: EpisodeTrace; revealedPillars: number }) {
    return (
        <div className="rounded-lg border border-[#2a2a40] bg-[#0a0a0f] overflow-hidden font-mono text-[12px]">
            <div className="bg-[#101018] px-4 py-2 border-b border-[#2a2a40] flex items-center gap-2">
                <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[#3a3a4d]" />
                    <div className="w-2 h-2 rounded-full bg-[#3a3a4d]" />
                    <div className="w-2 h-2 rounded-full bg-[#3a3a4d]" />
                </div>
                <span className="ml-3 text-[#8b8aaa] text-[10px]">routing_trace_{String(trace.id).padStart(4, '0')}.log</span>
            </div>
            <div className="p-4 space-y-3 text-[#a8a8bb] max-h-[400px] overflow-y-auto">
                <div>
                    <span className="text-[#5c5c77]"># Context</span>
                    <div className="mt-1">
                        {Object.entries(trace.context).map(([k, v]) => (
                            <span key={k} className="inline-block mr-3">
                                <span className="text-[#8b8aaa]">{k}</span>=<span className="text-[#e8e6f0]">{v}</span>
                            </span>
                        ))}
                    </div>
                </div>

                {trace.pillarSignals.slice(0, revealedPillars).map((signal, i) => {
                    const color = PILLAR_COLORS[signal.pillar] || '#7c6af7'
                    return (
                        <div key={i} className="pl-3 border-l-2 transition-all duration-300" style={{ borderColor: `${color}60` }}>
                            <span className="text-[#5c5c77]"># {signal.pillar}: {signal.description}</span>
                            <div className="mt-0.5" style={{ color }}>{signal.detail}</div>
                            <div className="text-[#5c5c77] text-[10px]">→ {signal.action} (conf: {(signal.confidence * 100).toFixed(0)}%)</div>
                        </div>
                    )
                })}

                {revealedPillars >= trace.pillarSignals.length && (
                    <div className="pt-2 border-t border-[#2a2a40]">
                        <span className="text-[#5c5c77]"># Decision</span>
                        <div className="mt-1">
                            <span
                                className="inline-block px-2 py-0.5 rounded text-sm font-medium"
                                style={{
                                    background: trace.correct ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                                    color: trace.correct ? '#10b981' : '#ef4444',
                                }}
                            >
                                {trace.fusedDecision} · {trace.correct ? 'Correct ✓' : `Wrong ✗ (expected ${trace.correctAnswer})`}
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

function ContextBadges({ context }: { context: Record<string, string> }) {
    return (
        <div className="flex flex-wrap gap-2">
            {Object.entries(context).map(([k, v]) => (
                <span key={k} className="font-mono text-[11px] px-2 py-1 rounded border border-[#2a2a40] bg-[#0a0a0f] text-[#a8a8bb]">
                    {k}=<span className="text-[#e8e6f0]">{v}</span>
                </span>
            ))}
        </div>
    )
}

export default function Demo() {
    const [mode, setMode] = useState<'replay' | 'live'>('replay')

    // Replay state
    const [selectedScenario, setSelectedScenario] = useState(0)
    const [selectedEpisode, setSelectedEpisode] = useState(0)
    const [revealedPillars, setRevealedPillars] = useState(0)
    const [isAnimating, setIsAnimating] = useState(false)

    // Live state
    const [liveResult, setLiveResult] = useState<SimulationResult | null>(null)
    const [liveRevealedPillars, setLiveRevealedPillars] = useState(0)
    const [isLiveAnimating, setIsLiveAnimating] = useState(false)
    const [episodeCount, setEpisodeCount] = useState(0)

    const currentScenario = scenarios[selectedScenario]
    const currentEpisode = currentScenario?.episodes[selectedEpisode]

    // Animate pillar reveal
    const animateReveal = useCallback((totalPillars: number, setter: (n: number) => void, onComplete?: () => void) => {
        setter(0)
        let i = 0
        const interval = setInterval(() => {
            i++
            setter(i)
            if (i >= totalPillars) {
                clearInterval(interval)
                onComplete?.()
            }
        }, 600)
        return () => clearInterval(interval)
    }, [])

    const playReplay = useCallback(() => {
        if (!currentEpisode || isAnimating) return
        setIsAnimating(true)
        const cleanup = animateReveal(currentEpisode.pillarSignals.length, setRevealedPillars, () => {
            setIsAnimating(false)
        })
        return cleanup
    }, [currentEpisode, isAnimating, animateReveal])

    const runLiveSimulation = useCallback(() => {
        if (isLiveAnimating) return
        setIsLiveAnimating(true)
        const problem = generateProblem()
        const result = simulatePipeline(problem)
        setLiveResult(result)
        setEpisodeCount(prev => prev + 1)
        animateReveal(result.trace.pillarSignals.length, setLiveRevealedPillars, () => {
            setIsLiveAnimating(false)
        })
    }, [isLiveAnimating, animateReveal])

    // Reset replay when changing episode
    useEffect(() => {
        setRevealedPillars(0)
    }, [selectedEpisode, selectedScenario])

    return (
        <div style={{ paddingTop: '56px', backgroundColor: '#050508', minHeight: '100vh' }}>
            <div className="max-w-6xl mx-auto px-6 py-16">
                {/* Header */}
                <div className="mb-12">
                    <span className="font-mono text-xs uppercase tracking-widest text-[#7c6af7] mb-3 block">Interactive Demo</span>
                    <h1 className="font-display text-4xl md:text-5xl font-light text-[#ffffff] mb-4">
                        Watch the Pipeline Think
                    </h1>
                    <p className="font-body text-lg text-[#8b8aaa] font-light max-w-2xl">
                        Step through real routing decisions or generate new problems and watch the 6-pillar cognitive pipeline process them in real-time.
                    </p>
                </div>

                {/* Mode Tabs */}
                <div className="flex gap-1 mb-10 p-1 rounded-lg bg-[#0a0a0f] border border-[#1e1e30] w-fit">
                    {(['replay', 'live'] as const).map(m => (
                        <button
                            key={m}
                            onClick={() => setMode(m)}
                            className="font-mono text-xs uppercase tracking-wider px-5 py-2.5 rounded transition-all"
                            style={{
                                background: mode === m ? 'rgba(124,106,247,0.15)' : 'transparent',
                                color: mode === m ? '#a89df9' : '#4a4960',
                                border: mode === m ? '1px solid rgba(124,106,247,0.3)' : '1px solid transparent',
                            }}
                        >
                            {m === 'replay' ? '📂 Replay Traces' : '⚡ Live Simulation'}
                        </button>
                    ))}
                </div>

                {/* Replay Mode */}
                {mode === 'replay' && currentEpisode && (
                    <div className="space-y-8">
                        {/* Controls */}
                        <div className="flex flex-wrap items-center gap-4">
                            <select
                                value={selectedScenario}
                                onChange={e => { setSelectedScenario(Number(e.target.value)); setSelectedEpisode(0) }}
                                className="font-mono text-xs bg-[#0a0a0f] border border-[#2a2a40] rounded px-3 py-2 text-[#a8a8bb] focus:border-[#7c6af7] focus:outline-none"
                            >
                                {scenarios.map((s, i) => (
                                    <option key={i} value={i}>{s.name}</option>
                                ))}
                            </select>

                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setSelectedEpisode(Math.max(0, selectedEpisode - 1))}
                                    disabled={selectedEpisode === 0}
                                    className="p-2 rounded border border-[#2a2a40] text-[#8b8aaa] hover:border-[#7c6af7] disabled:opacity-30 transition-all"
                                >
                                    <SkipBack size={14} />
                                </button>
                                <span className="font-mono text-xs text-[#8b8aaa] min-w-[80px] text-center">
                                    Episode {selectedEpisode + 1} / {currentScenario.episodes.length}
                                </span>
                                <button
                                    onClick={() => setSelectedEpisode(Math.min(currentScenario.episodes.length - 1, selectedEpisode + 1))}
                                    disabled={selectedEpisode >= currentScenario.episodes.length - 1}
                                    className="p-2 rounded border border-[#2a2a40] text-[#8b8aaa] hover:border-[#7c6af7] disabled:opacity-30 transition-all"
                                >
                                    <SkipForward size={14} />
                                </button>
                            </div>

                            <button
                                onClick={playReplay}
                                disabled={isAnimating}
                                className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider px-4 py-2 rounded bg-[#7c6af7] text-white hover:bg-[#6b5be6] disabled:opacity-50 transition-all"
                            >
                                <Play size={12} /> {isAnimating ? 'Running...' : 'Run Pipeline'}
                            </button>
                        </div>

                        {/* Scenario Info */}
                        <div className="rounded-lg border border-[#1e1e30] bg-[#08080c] p-4">
                            <div className="font-mono text-xs text-[#7c6af7] mb-2">{currentScenario.name}</div>
                            <p className="font-body text-sm text-[#8b8aaa] mb-3">{currentScenario.description}</p>
                            <div className="font-mono text-[10px] text-[#5c5c77]">
                                Hidden rules: {currentScenario.hiddenRules.map((r, i) => (
                                    <span key={i} className="block ml-4">▸ {r}</span>
                                ))}
                            </div>
                        </div>

                        {/* Context */}
                        <div>
                            <span className="font-mono text-xs text-[#5c5c77] mb-2 block">CONTEXT PRESENTED</span>
                            <ContextBadges context={currentEpisode.context} />
                        </div>

                        {/* Pipeline Visualization */}
                        <div>
                            <span className="font-mono text-xs text-[#5c5c77] mb-3 block">6-PILLAR PIPELINE</span>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                                {currentEpisode.pillarSignals.map((signal, i) => (
                                    <PipelineNode
                                        key={signal.pillar}
                                        signal={signal}
                                        active={revealedPillars === i + 1}
                                        revealed={i < revealedPillars}
                                    />
                                ))}
                            </div>
                        </div>

                        {/* Trace Output */}
                        <div>
                            <span className="font-mono text-xs text-[#5c5c77] mb-3 block">ROUTING TRACE</span>
                            <TraceOutput trace={currentEpisode} revealedPillars={revealedPillars} />
                        </div>
                    </div>
                )}

                {/* Live Mode */}
                {mode === 'live' && (
                    <div className="space-y-8">
                        {/* Controls */}
                        <div className="flex items-center gap-4">
                            <button
                                onClick={runLiveSimulation}
                                disabled={isLiveAnimating}
                                className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider px-5 py-3 rounded bg-[#7c6af7] text-white hover:bg-[#6b5be6] disabled:opacity-50 transition-all"
                            >
                                <Zap size={14} /> {isLiveAnimating ? 'Processing...' : 'Generate & Route'}
                            </button>

                            <button
                                onClick={() => { resetSimulation(); setLiveResult(null); setEpisodeCount(0); setLiveRevealedPillars(0) }}
                                className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider px-4 py-3 rounded border border-[#2a2a40] text-[#8b8aaa] hover:border-[#7c6af7] transition-all"
                            >
                                <RotateCcw size={12} /> Reset Agent
                            </button>

                            <span className="font-mono text-xs text-[#5c5c77]">
                                Episodes run: <span className="text-[#7c6af7]">{episodeCount}</span>
                            </span>
                        </div>

                        <div className="rounded-lg border border-[#1e1e30] bg-[#08080c] p-4">
                            <p className="font-body text-sm text-[#8b8aaa]">
                                Click <strong className="text-[#7c6af7]">Generate & Route</strong> to create a random problem. The 6-pillar pipeline will classify and solve it in real-time. The Bandit learns from each episode — watch its posteriors strengthen as you run more problems. Hit <strong className="text-[#8b8aaa]">Reset Agent</strong> to clear learned state.
                            </p>
                        </div>

                        {liveResult && (
                            <>
                                {/* Context */}
                                <div>
                                    <span className="font-mono text-xs text-[#5c5c77] mb-2 block">GENERATED PROBLEM — {liveResult.trace.scenario}</span>
                                    <ContextBadges context={liveResult.trace.context} />
                                </div>

                                {/* Pipeline */}
                                <div>
                                    <span className="font-mono text-xs text-[#5c5c77] mb-3 block">6-PILLAR PIPELINE</span>
                                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                                        {liveResult.trace.pillarSignals.map((signal, i) => (
                                            <PipelineNode
                                                key={signal.pillar}
                                                signal={signal}
                                                active={liveRevealedPillars === i + 1}
                                                revealed={i < liveRevealedPillars}
                                            />
                                        ))}
                                    </div>
                                </div>

                                {/* Trace */}
                                <div>
                                    <span className="font-mono text-xs text-[#5c5c77] mb-3 block">ROUTING TRACE</span>
                                    <TraceOutput trace={liveResult.trace} revealedPillars={liveRevealedPillars} />
                                </div>
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
