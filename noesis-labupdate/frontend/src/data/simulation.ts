/**
 * Refracted Simulation Engine
 * A lightweight TypeScript version of the 6-pillar cognitive pipeline.
 * Demonstrates the ROUTING PATTERN — not the actual agent code.
 */

import type { PillarSignal, EpisodeTrace } from './demoData'

// ── Problem Generator ──

interface GeneratedProblem {
    scenario: string
    context: Record<string, string>
    actions: string[]
    correctAnswer: string
    ruleUsed: string
}

const TRIAGE_RULES: Array<{ match: (ctx: Record<string, string>) => boolean; answer: string; rule: string }> = [
    { match: c => c.severity === 'critical', answer: 'TREAT_FIRST', rule: 'Critical severity always gets treated first' },
    { match: c => c.severity === 'minor' && c.resource === 'scarce', answer: 'DEFER', rule: 'Minor cases defer when resources are scarce' },
    { match: c => c.severity === 'moderate' && c.resource === 'ample', answer: 'WAIT', rule: 'Moderate cases wait when resources are ample' },
    { match: c => c.severity === 'minor', answer: 'WAIT', rule: 'Minor cases default to wait' },
    { match: c => c.severity === 'moderate', answer: 'WAIT', rule: 'Moderate cases default to wait' },
]

const ROUTE_RULES: Array<{ match: (ctx: Record<string, string>) => boolean; answer: string; rule: string }> = [
    { match: c => c.risk === 'high', answer: 'SAFE_ROUTE', rule: 'Never take high-risk routes' },
    { match: c => c.urgency === 'urgent' && c.cost === 'low', answer: 'FAST_ROUTE', rule: 'Urgent + low-cost → fast route' },
    { match: c => c.urgency === 'relaxed', answer: 'SCENIC_ROUTE', rule: 'Low urgency → scenic route' },
    { match: () => true, answer: 'SAFE_ROUTE', rule: 'Default to safe route' },
]

function pick<T>(arr: T[]): T {
    return arr[Math.floor(Math.random() * arr.length)]
}

export function generateProblem(): GeneratedProblem {
    const scenario = pick(['Emergency Triage', 'Route Navigation'])

    if (scenario === 'Emergency Triage') {
        const context = {
            severity: pick(['critical', 'moderate', 'minor']),
            resource: pick(['scarce', 'ample']),
            wait_time: pick(['short', 'long']),
        }
        const rule = TRIAGE_RULES.find(r => r.match(context))!
        return {
            scenario,
            context,
            actions: ['TREAT_FIRST', 'WAIT', 'DEFER'],
            correctAnswer: rule.answer,
            ruleUsed: rule.rule,
        }
    } else {
        const context = {
            risk: pick(['high', 'medium', 'low']),
            urgency: pick(['urgent', 'normal', 'relaxed']),
            cost: pick(['high', 'low']),
        }
        const rule = ROUTE_RULES.find(r => r.match(context))!
        return {
            scenario,
            context,
            actions: ['SAFE_ROUTE', 'FAST_ROUTE', 'SCENIC_ROUTE'],
            correctAnswer: rule.answer,
            ruleUsed: rule.rule,
        }
    }
}

// ── Bandit State ──

interface BetaParams {
    alpha: number
    beta: number
}

const banditState: Map<string, Map<string, BetaParams>> = new Map()

function getBanditParams(ctxKey: string, action: string): BetaParams {
    if (!banditState.has(ctxKey)) banditState.set(ctxKey, new Map())
    const ctx = banditState.get(ctxKey)!
    if (!ctx.has(action)) ctx.set(action, { alpha: 1, beta: 1 })
    return ctx.get(action)!
}

function sampleBeta(a: number, b: number): number {
    // Approximate Beta sampling using the mean + noise
    const mean = a / (a + b)
    const variance = (a * b) / ((a + b) ** 2 * (a + b + 1))
    const noise = (Math.random() - 0.5) * Math.sqrt(variance) * 2
    return Math.max(0, Math.min(1, mean + noise))
}

// ── Temporal Field ──

const lastSeen: Map<string, number> = new Map()
let globalStep = 0

// ── Simulate 6-Pillar Pipeline ──

export interface SimulationResult {
    trace: EpisodeTrace
    pillarTimings: number[] // ms delay for each pillar (for animation)
}

export function simulatePipeline(problem: GeneratedProblem): SimulationResult {
    globalStep++
    const ctxKey = Object.entries(problem.context).sort().map(([k, v]) => `${k}=${v}`).join('|')

    // Pillar 3: TFE — Temporal Field Engine
    const tfeLastSeen = lastSeen.get(ctxKey) ?? 0
    const tfeRecency = tfeLastSeen > 0 ? 1.0 / (1 + (globalStep - tfeLastSeen) * 0.1) : 0
    lastSeen.set(ctxKey, globalStep)

    const tfeSignal: PillarSignal = {
        pillar: 'TFE',
        description: 'Temporal Field Engine',
        confidence: Math.min(0.9, tfeRecency),
        action: problem.correctAnswer,
        detail: tfeLastSeen > 0
            ? `Context last seen at step ${tfeLastSeen}, recency weight: ${tfeRecency.toFixed(2)}`
            : 'First encounter — no temporal data available',
    }

    // Pillar 1: CME — Constrained Memory Engine
    const cmeSignal: PillarSignal = {
        pillar: 'CME',
        description: 'Constrained Memory',
        confidence: 0.75 + Math.random() * 0.2,
        action: problem.correctAnswer,
        detail: `Rule matched: "${problem.ruleUsed}"`,
    }

    // Pillar 5: BioRAG — Episodic Attractor Memory
    const ragConfidence = 0.5 + Math.random() * 0.35
    const bioragSignal: PillarSignal = {
        pillar: 'BioRAG',
        description: 'Episodic Memory',
        confidence: ragConfidence,
        action: problem.correctAnswer,
        detail: `Hopfield retrieval: ${Math.floor(ragConfidence * 5)}/5 stored episodes align with ${problem.correctAnswer}`,
    }

    // Pillar 4: PEE — Prediction Error Engine
    const params = getBanditParams(ctxKey, problem.correctAnswer)
    const predicted = params.alpha / (params.alpha + params.beta)
    const peeSignal: PillarSignal = {
        pillar: 'PEE',
        description: 'Prediction Error',
        confidence: Math.abs(1 - predicted),
        action: problem.correctAnswer,
        detail: `Predicted P(success|${problem.correctAnswer}) = ${predicted.toFixed(3)}, surprise = ${Math.abs(1 - predicted).toFixed(3)}`,
    }

    // Pillar 6: PFC — Prefrontal Cortex
    const avgConfidence = (cmeSignal.confidence + bioragSignal.confidence + tfeSignal.confidence) / 3
    const pfcVerdict = avgConfidence > 0.5 ? 'PROCEED' : avgConfidence > 0.3 ? 'SLOW' : 'ESCALATE'
    const pfcSignal: PillarSignal = {
        pillar: 'PFC',
        description: 'Prefrontal Cortex',
        confidence: avgConfidence,
        action: problem.correctAnswer,
        detail: `Verdict: ${pfcVerdict} — avg pillar confidence: ${avgConfidence.toFixed(2)}`,
    }

    // Pillar 2: Bandit — Thompson Sampling
    const samples: Record<string, number> = {}
    for (const act of problem.actions) {
        const p = getBanditParams(ctxKey, act)
        samples[act] = sampleBeta(p.alpha, p.beta)
    }
    const banditChoice = Object.entries(samples).sort(([, a], [, b]) => b - a)[0][0]
    const chosenParams = getBanditParams(ctxKey, banditChoice)

    const banditSignal: PillarSignal = {
        pillar: 'Bandit',
        description: 'Thompson Sampling',
        confidence: samples[banditChoice],
        action: banditChoice,
        detail: `Beta(${chosenParams.alpha.toFixed(0)},${chosenParams.beta.toFixed(0)}) → sampled ${samples[banditChoice].toFixed(3)}, choosing: ${banditChoice}`,
    }

    // The final decision: CME+PFC consensus overrides bandit if high confidence
    const finalAction = cmeSignal.confidence > 0.7 ? problem.correctAnswer : banditChoice
    const isCorrect = finalAction === problem.correctAnswer

    // Update bandit posteriors
    const finalParams = getBanditParams(ctxKey, finalAction)
    if (isCorrect) {
        finalParams.alpha += 1
    } else {
        finalParams.beta += 1
    }

    return {
        trace: {
            id: globalStep,
            scenario: problem.scenario,
            context: problem.context,
            actions: problem.actions,
            pillarSignals: [tfeSignal, cmeSignal, bioragSignal, peeSignal, pfcSignal, banditSignal],
            fusedDecision: finalAction,
            correct: isCorrect,
            correctAnswer: problem.correctAnswer,
        },
        pillarTimings: [400, 600, 800, 500, 700, 900],
    }
}

export function resetSimulation() {
    banditState.clear()
    lastSeen.clear()
    globalStep = 0
}
