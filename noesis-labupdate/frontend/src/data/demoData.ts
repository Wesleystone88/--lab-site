/**
 * Pre-recorded episode traces — sanitized from real evidence documents.
 * These are actual routing decisions the system made, with surface values changed.
 */

export interface PillarSignal {
    pillar: string
    description: string
    confidence: number
    action: string
    detail: string
}

export interface EpisodeTrace {
    id: number
    scenario: string
    context: Record<string, string>
    actions: string[]
    pillarSignals: PillarSignal[]
    fusedDecision: string
    correct: boolean
    correctAnswer: string
}

export interface Scenario {
    name: string
    description: string
    hiddenRules: string[]
    episodes: EpisodeTrace[]
}

export const scenarios: Scenario[] = [
    {
        name: 'Emergency Triage',
        description: 'Decide triage priority given severity, resource availability, and wait time. 300 episodes, converged at episode 60.',
        hiddenRules: [
            'Critical severity always gets treated first',
            'Minor cases defer when resources are scarce',
            'Moderate cases wait when resources are ample',
        ],
        episodes: [
            {
                id: 1,
                scenario: 'Emergency Triage',
                context: { severity: 'critical', resource: 'scarce', wait_time: 'short' },
                actions: ['TREAT_FIRST', 'WAIT', 'DEFER'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.2, action: 'TREAT_FIRST', detail: 'No prior temporal data — flat weights' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.85, action: 'TREAT_FIRST', detail: 'Rule: severity=critical → hard bias toward TREAT_FIRST' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.7, action: 'TREAT_FIRST', detail: 'Retrieved 3 similar episodes, all resolved with TREAT_FIRST' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.1, action: 'TREAT_FIRST', detail: 'Predicted P(success)=0.96, low surprise expected' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.9, action: 'TREAT_FIRST', detail: 'Verdict: PROCEED — high consensus across pillars' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.96, action: 'TREAT_FIRST', detail: 'Beta(48,2) → sampled 0.963, highest action: TREAT_FIRST' },
                ],
                fusedDecision: 'TREAT_FIRST',
                correct: true,
                correctAnswer: 'TREAT_FIRST',
            },
            {
                id: 2,
                scenario: 'Emergency Triage',
                context: { severity: 'minor', resource: 'scarce', wait_time: 'short' },
                actions: ['TREAT_FIRST', 'WAIT', 'DEFER'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.3, action: 'DEFER', detail: 'Recent DEFER successes boost recency weight' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.8, action: 'DEFER', detail: 'Rule: severity=minor + resource=scarce → bias DEFER' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.6, action: 'DEFER', detail: 'Closest episode: minor+scarce → DEFER was correct' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.15, action: 'DEFER', detail: 'Predicted P(success|DEFER)=0.96, confident' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.85, action: 'DEFER', detail: 'Verdict: PROCEED — consensus favors DEFER' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.96, action: 'DEFER', detail: 'Beta(47,2) → sampled 0.962, highest action: DEFER' },
                ],
                fusedDecision: 'DEFER',
                correct: true,
                correctAnswer: 'DEFER',
            },
            {
                id: 3,
                scenario: 'Emergency Triage',
                context: { severity: 'moderate', resource: 'ample', wait_time: 'long' },
                actions: ['TREAT_FIRST', 'WAIT', 'DEFER'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.25, action: 'WAIT', detail: 'Moderate staleness on WAIT — still fresh' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.75, action: 'WAIT', detail: 'Rule: moderate + ample resources → WAIT' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.65, action: 'WAIT', detail: 'Retrieved 2 similar episodes → WAIT was correct both times' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.12, action: 'WAIT', detail: 'Predicted P(success|WAIT)=0.96, low surprise' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.88, action: 'WAIT', detail: 'Verdict: PROCEED — pillars aligned on WAIT' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.97, action: 'WAIT', detail: 'Beta(49,2) → sampled 0.966, highest action: WAIT' },
                ],
                fusedDecision: 'WAIT',
                correct: true,
                correctAnswer: 'WAIT',
            },
            {
                id: 4,
                scenario: 'Emergency Triage',
                context: { severity: 'critical', resource: 'ample', wait_time: 'long' },
                actions: ['TREAT_FIRST', 'WAIT', 'DEFER'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.15, action: 'TREAT_FIRST', detail: 'All actions relatively fresh — minimal temporal signal' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.9, action: 'TREAT_FIRST', detail: 'Hard rule: critical → TREAT_FIRST regardless of resources' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.8, action: 'TREAT_FIRST', detail: '4/4 retrieved critical episodes → TREAT_FIRST' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.08, action: 'TREAT_FIRST', detail: 'Near-zero surprise — highly predictable outcome' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.95, action: 'TREAT_FIRST', detail: 'Verdict: PROCEED — overwhelming consensus' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.96, action: 'TREAT_FIRST', detail: 'Beta(46,3) → sampled 0.960, highest action: TREAT_FIRST' },
                ],
                fusedDecision: 'TREAT_FIRST',
                correct: true,
                correctAnswer: 'TREAT_FIRST',
            },
            {
                id: 5,
                scenario: 'Emergency Triage',
                context: { severity: 'minor', resource: 'ample', wait_time: 'long' },
                actions: ['TREAT_FIRST', 'WAIT', 'DEFER'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.2, action: 'WAIT', detail: 'WAIT action slightly more recent than others' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.7, action: 'WAIT', detail: 'Rule: minor + ample → WAIT (no urgency)' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.55, action: 'WAIT', detail: 'Mixed retrieval — 2 WAIT, 1 DEFER. WAIT wins by similarity' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.2, action: 'WAIT', detail: 'Moderate confidence — some uncertainty remains' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.82, action: 'WAIT', detail: 'Verdict: PROCEED — leaning WAIT but not overwhelming' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.96, action: 'WAIT', detail: 'Beta(48,2) → sampled 0.964, highest action: WAIT' },
                ],
                fusedDecision: 'WAIT',
                correct: true,
                correctAnswer: 'WAIT',
            },
        ],
    },
    {
        name: 'Route Navigation',
        description: 'Choose a route given risk level, urgency, and cost. 300 episodes, converged at episode 10.',
        hiddenRules: [
            'Never take high-risk routes regardless of urgency',
            'Urgent + low-cost → always take fast route',
            'Low urgency → always take scenic (low-risk) route',
        ],
        episodes: [
            {
                id: 1,
                scenario: 'Route Navigation',
                context: { risk: 'high', urgency: 'urgent', cost: 'high' },
                actions: ['SAFE_ROUTE', 'FAST_ROUTE', 'SCENIC_ROUTE'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.1, action: 'SAFE_ROUTE', detail: 'No temporal bias — all routes equally fresh' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.95, action: 'SAFE_ROUTE', detail: 'Hard block: risk=high → FAST_ROUTE blocked, SCENIC blocked' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.75, action: 'SAFE_ROUTE', detail: 'All high-risk episodes resolved with SAFE_ROUTE' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.05, action: 'SAFE_ROUTE', detail: 'Zero surprise — perfectly predicted' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.95, action: 'SAFE_ROUTE', detail: 'Verdict: PROCEED — CME hard block enforced' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.94, action: 'SAFE_ROUTE', detail: 'Beta(45,3) → sampled 0.941, SAFE_ROUTE dominates' },
                ],
                fusedDecision: 'SAFE_ROUTE',
                correct: true,
                correctAnswer: 'SAFE_ROUTE',
            },
            {
                id: 2,
                scenario: 'Route Navigation',
                context: { risk: 'low', urgency: 'urgent', cost: 'low' },
                actions: ['SAFE_ROUTE', 'FAST_ROUTE', 'SCENIC_ROUTE'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.15, action: 'FAST_ROUTE', detail: 'FAST_ROUTE slightly boosted by recent success' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.8, action: 'FAST_ROUTE', detail: 'Rule: urgent + low-cost → prefer FAST_ROUTE' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.7, action: 'FAST_ROUTE', detail: 'Retrieved: urgent+low-cost → FAST_ROUTE correct' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.1, action: 'FAST_ROUTE', detail: 'Low surprise expected' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.9, action: 'FAST_ROUTE', detail: 'Verdict: PROCEED — no risk conflict detected' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.94, action: 'FAST_ROUTE', detail: 'Beta(44,3) → sampled 0.941, FAST_ROUTE wins' },
                ],
                fusedDecision: 'FAST_ROUTE',
                correct: true,
                correctAnswer: 'FAST_ROUTE',
            },
            {
                id: 3,
                scenario: 'Route Navigation',
                context: { risk: 'low', urgency: 'relaxed', cost: 'low' },
                actions: ['SAFE_ROUTE', 'FAST_ROUTE', 'SCENIC_ROUTE'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.2, action: 'SCENIC_ROUTE', detail: 'SCENIC_ROUTE fresher in this context' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.75, action: 'SCENIC_ROUTE', detail: 'Rule: relaxed urgency → prefer SCENIC_ROUTE' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.65, action: 'SCENIC_ROUTE', detail: 'Similar relaxed episodes → SCENIC was correct' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.12, action: 'SCENIC_ROUTE', detail: 'Moderate confidence in prediction' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.85, action: 'SCENIC_ROUTE', detail: 'Verdict: PROCEED — low risk, relaxed context' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.95, action: 'SCENIC_ROUTE', detail: 'Beta(46,2) → sampled 0.950, SCENIC_ROUTE wins' },
                ],
                fusedDecision: 'SCENIC_ROUTE',
                correct: true,
                correctAnswer: 'SCENIC_ROUTE',
            },
            {
                id: 4,
                scenario: 'Route Navigation',
                context: { risk: 'high', urgency: 'relaxed', cost: 'high' },
                actions: ['SAFE_ROUTE', 'FAST_ROUTE', 'SCENIC_ROUTE'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.1, action: 'SAFE_ROUTE', detail: 'Flat temporal weights — no strong recency signal' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.95, action: 'SAFE_ROUTE', detail: 'Hard block: risk=high → blocks FAST and SCENIC' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.8, action: 'SAFE_ROUTE', detail: 'All high-risk retrievals → SAFE_ROUTE' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.05, action: 'SAFE_ROUTE', detail: 'Near-zero surprise' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.95, action: 'SAFE_ROUTE', detail: 'Verdict: PROCEED — hard block dominates' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.95, action: 'SAFE_ROUTE', detail: 'Beta(47,2) → sampled 0.952, SAFE_ROUTE only viable' },
                ],
                fusedDecision: 'SAFE_ROUTE',
                correct: true,
                correctAnswer: 'SAFE_ROUTE',
            },
            {
                id: 5,
                scenario: 'Route Navigation',
                context: { risk: 'medium', urgency: 'normal', cost: 'low' },
                actions: ['SAFE_ROUTE', 'FAST_ROUTE', 'SCENIC_ROUTE'],
                pillarSignals: [
                    { pillar: 'TFE', description: 'Temporal Field Engine', confidence: 0.18, action: 'SAFE_ROUTE', detail: 'SAFE_ROUTE slightly more recent' },
                    { pillar: 'CME', description: 'Constrained Memory', confidence: 0.6, action: 'SAFE_ROUTE', detail: 'Soft bias: medium risk → lean SAFE' },
                    { pillar: 'BioRAG', description: 'Episodic Memory', confidence: 0.5, action: 'SAFE_ROUTE', detail: 'Mixed retrieval — SAFE slightly preferred' },
                    { pillar: 'PEE', description: 'Prediction Error', confidence: 0.25, action: 'SAFE_ROUTE', detail: 'Some uncertainty in this context' },
                    { pillar: 'PFC', description: 'Prefrontal Cortex', confidence: 0.78, action: 'SAFE_ROUTE', detail: 'Verdict: PROCEED — moderate confidence' },
                    { pillar: 'Bandit', description: 'Thompson Sampling', confidence: 0.95, action: 'SAFE_ROUTE', detail: 'Beta(46,2) → sampled 0.950, SAFE_ROUTE edges out' },
                ],
                fusedDecision: 'SAFE_ROUTE',
                correct: true,
                correctAnswer: 'SAFE_ROUTE',
            },
        ],
    },
]
