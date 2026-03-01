// All data extracted directly from documents — no mocked values

export const substrateAccuracy = [
  { substrate: 'compute', accuracy: 99, attempts: 100, note: 'Missed 1: parity operation not found from given data' },
  { substrate: 'solver', accuracy: 100, attempts: 100, note: 'Perfect. Constraint parsing and global evaluation correct.' },
  { substrate: 'decomposer', accuracy: 99, attempts: 100, note: 'One edge case where multiple transforms fit A→B equally' },
  { substrate: 'memory_probe', accuracy: 100, attempts: 100, note: 'Perfect. Delta sign change detection robust.' },
  { substrate: 'bandit', accuracy: 84, attempts: 100, note: 'Learned from experience. Starts ~50%, ends ~96% with warm start.' },
]

export const routedIQResults = [
  { class: 'Constraint Satisfaction', substrate: 'solver', accuracy: 100, difficulty: 'Hard', bar: 20 },
  { class: 'Rule Inversion', substrate: 'memory_probe', accuracy: 100, difficulty: 'Hard', bar: 20 },
  { class: 'Structural Analogy', substrate: 'decomposer', accuracy: 100, difficulty: 'Hard', bar: 20 },
  { class: 'Code Structure', substrate: 'bandit', accuracy: 96, difficulty: 'Medium', bar: 19 },
  { class: 'Cross-Sequence', substrate: 'compute', accuracy: 98, difficulty: 'Hardest', bar: 20 },
]

export const coldVsWarm = [
  { class: 'Constraint Satisfaction', substrate: 'solver', cold: 100, warm: 100, delta: 0, why: 'Compute substrate — no learning, same result every time' },
  { class: 'Rule Inversion', substrate: 'memory_probe', cold: 100, warm: 100, delta: 0, why: 'Compute substrate — no learning, same result every time' },
  { class: 'Structural Analogy', substrate: 'decomposer', cold: 98, warm: 98, delta: 0, why: 'Compute substrate — no learning, same result every time' },
  { class: 'Code Structure', substrate: 'bandit', cold: 65, warm: 93, delta: 28, why: 'Bandit posteriors warm-started — learned action preferences transferred' },
  { class: 'Cross-Sequence', substrate: 'compute', cold: 100, warm: 100, delta: 0, why: 'Compute substrate — no learning, same result every time' },
]

export const unroutedIQResults = [
  { class: 'Constraint Satisfaction', accuracy: 25, difficulty: 'Hard', note: 'Multiple rules must ALL hold simultaneously. Global reasoning — not local optimization.' },
  { class: 'Rule Inversion', accuracy: 15, difficulty: 'Hard', note: 'Pattern holds then inverts. Any system extrapolating first pattern fails every inversion.' },
  { class: 'Structural Analogy', accuracy: 20, difficulty: 'Hard', note: 'A→B compound transform. Simple ratio/difference fails. Requires algebraic decomposition.' },
  { class: 'Code Structure', accuracy: 100, difficulty: 'Medium', note: 'Structural programming invariants. Stable across surfaces. Bandit mastered.' },
  { class: 'Cross-Sequence', accuracy: 25, difficulty: 'Hardest', note: 'Rule lives BETWEEN series. Requires holding A, B, C in working memory simultaneously.' },
]

// Learning curves from emergence_artifact_report.docx — exact values
export const triageLearningCurve = [
  { window: '0–10', pct: 30 }, { window: '10–20', pct: 40 }, { window: '20–30', pct: 50 },
  { window: '30–40', pct: 60 }, { window: '40–50', pct: 80 }, { window: '50–60', pct: 80 },
  { window: '60–70', pct: 100 }, { window: '70–80', pct: 90 }, { window: '80–90', pct: 100 },
  { window: '90–100', pct: 100 }, { window: '100–110', pct: 100 }, { window: '110–120', pct: 100 },
  { window: '120–130', pct: 100 }, { window: '130–140', pct: 100 }, { window: '140–150', pct: 100 },
  { window: '150–160', pct: 100 }, { window: '160–170', pct: 100 }, { window: '170–180', pct: 100 },
  { window: '180–190', pct: 100 }, { window: '190–200', pct: 100 }, { window: '200–210', pct: 100 },
  { window: '210–220', pct: 100 }, { window: '220–230', pct: 100 }, { window: '230–240', pct: 100 },
  { window: '240–250', pct: 100 }, { window: '250–260', pct: 100 }, { window: '260–270', pct: 100 },
  { window: '270–280', pct: 100 }, { window: '280–290', pct: 100 }, { window: '290–300', pct: 100 },
]

export const navLearningCurve = [
  { window: '0–10', pct: 30 }, { window: '10–20', pct: 90 }, { window: '20–30', pct: 40 },
  { window: '30–40', pct: 50 }, { window: '40–50', pct: 90 }, { window: '50–60', pct: 70 },
  { window: '60–70', pct: 50 }, { window: '70–80', pct: 90 }, { window: '80–90', pct: 90 },
  { window: '90–100', pct: 100 }, { window: '100–110', pct: 80 }, { window: '110–120', pct: 90 },
  { window: '120–130', pct: 90 }, { window: '130–140', pct: 100 }, { window: '140–150', pct: 100 },
  { window: '150–160', pct: 100 }, { window: '160–170', pct: 90 }, { window: '170–180', pct: 80 },
  { window: '180–190', pct: 100 }, { window: '190–200', pct: 100 }, { window: '200–210', pct: 100 },
  { window: '210–220', pct: 100 }, { window: '220–230', pct: 100 }, { window: '230–240', pct: 100 },
  { window: '240–250', pct: 100 }, { window: '250–260', pct: 100 }, { window: '260–270', pct: 100 },
  { window: '270–280', pct: 100 }, { window: '280–290', pct: 100 }, { window: '290–300', pct: 100 },
]

export const diagnosisLearningCurve = [
  { window: '0–10', pct: 20 }, { window: '10–20', pct: 20 }, { window: '20–30', pct: 40 },
  { window: '30–40', pct: 50 }, { window: '40–50', pct: 50 }, { window: '50–60', pct: 60 },
  { window: '60–70', pct: 70 }, { window: '70–80', pct: 80 }, { window: '80–90', pct: 80 },
  { window: '90–100', pct: 100 }, { window: '100–110', pct: 90 }, { window: '110–120', pct: 80 },
  { window: '120–130', pct: 70 }, { window: '130–140', pct: 100 }, { window: '140–150', pct: 80 },
  { window: '150–160', pct: 80 }, { window: '160–170', pct: 90 }, { window: '170–180', pct: 100 },
  { window: '180–190', pct: 90 }, { window: '190–200', pct: 100 }, { window: '200–210', pct: 100 },
  { window: '210–220', pct: 80 }, { window: '220–230', pct: 90 }, { window: '230–240', pct: 100 },
  { window: '240–250', pct: 100 }, { window: '250–260', pct: 90 }, { window: '260–270', pct: 100 },
  { window: '270–280', pct: 100 }, { window: '280–290', pct: 100 }, { window: '290–300', pct: 100 },
]

// Q-value tables from emergence_artifact_report.docx — exact values
export const triageQValues = [
  { context: 'resource=scarce | severity=critical | wait_time=short', topChoice: 'TREAT_FIRST', qValue: 0.963 },
  { context: 'resource=ample | severity=minor | wait_time=long', topChoice: 'WAIT', qValue: 0.964 },
  { context: 'resource=ample | severity=moderate | wait_time=long', topChoice: 'WAIT', qValue: 0.966 },
  { context: 'resource=scarce | severity=minor | wait_time=short', topChoice: 'DEFER', qValue: 0.962 },
  { context: 'resource=ample | severity=minor | wait_time=short', topChoice: 'WAIT', qValue: 0.957 },
  { context: 'resource=scarce | severity=minor | wait_time=long', topChoice: 'DEFER', qValue: 0.966 },
  { context: 'resource=ample | severity=critical | wait_time=long', topChoice: 'TREAT_FIRST', qValue: 0.960 },
  { context: 'resource=scarce | severity=critical | wait_time=long', topChoice: 'TREAT_FIRST', qValue: 0.966 },
  { context: 'resource=ample | severity=moderate | wait_time=short', topChoice: 'WAIT', qValue: 0.957 },
  { context: 'resource=ample | severity=critical | wait_time=short', topChoice: 'TREAT_FIRST', qValue: 0.955 },
  { context: 'resource=scarce | severity=moderate | wait_time=long', topChoice: 'WAIT', qValue: 0.950 },
  { context: 'resource=scarce | severity=moderate | wait_time=short', topChoice: 'WAIT', qValue: 0.964 },
]

export const navQValues = [
  { context: 'cost=high | risk=high | urgency=urgent', topChoice: 'SAFE_ROUTE', qValue: 0.941 },
  { context: 'cost=low | risk=low | urgency=relaxed', topChoice: 'SCENIC_ROUTE', qValue: 0.950 },
  { context: 'cost=low | risk=medium | urgency=normal', topChoice: 'SAFE_ROUTE', qValue: 0.950 },
  { context: 'cost=high | risk=low | urgency=urgent', topChoice: 'SAFE_ROUTE', qValue: 0.938 },
  { context: 'cost=high | risk=low | urgency=normal', topChoice: 'SAFE_ROUTE', qValue: 0.950 },
  { context: 'cost=high | risk=low | urgency=relaxed', topChoice: 'SCENIC_ROUTE', qValue: 0.944 },
  { context: 'cost=high | risk=high | urgency=relaxed', topChoice: 'SAFE_ROUTE', qValue: 0.952 },
  { context: 'cost=low | risk=low | urgency=urgent', topChoice: 'FAST_ROUTE', qValue: 0.941 },
  { context: 'cost=low | risk=high | urgency=normal', topChoice: 'SAFE_ROUTE', qValue: 0.941 },
  { context: 'cost=low | risk=high | urgency=urgent', topChoice: 'SAFE_ROUTE', qValue: 0.941 },
  { context: 'cost=high | risk=medium | urgency=normal', topChoice: 'SAFE_ROUTE', qValue: 0.950 },
  { context: 'cost=high | risk=high | urgency=normal', topChoice: 'SAFE_ROUTE', qValue: 0.944 },
]

export const diagnosisQValues = [
  { context: 'duration=acute | symptom_a=fever | symptom_b=rash', topChoice: 'VIRAL', qValue: 0.944 },
  { context: 'duration=chronic | symptom_a=fatigue | symptom_b=pallor', topChoice: 'ANEMIA', qValue: 0.941 },
  { context: 'duration=chronic | symptom_a=pain | symptom_b=swelling', topChoice: 'INJURY', qValue: 0.944 },
  { context: 'duration=acute | symptom_a=fatigue | symptom_b=rash', topChoice: 'UNCLEAR', qValue: 0.929 },
  { context: 'duration=acute | symptom_a=fatigue | symptom_b=swelling', topChoice: 'UNCLEAR', qValue: 0.947 },
  { context: 'duration=acute | symptom_a=fatigue | symptom_b=pallor', topChoice: 'ANEMIA', qValue: 0.941 },
  { context: 'duration=acute | symptom_a=fever | symptom_b=pallor', topChoice: 'UNCLEAR', qValue: 0.950 },
  { context: 'duration=chronic | symptom_a=fatigue | symptom_b=rash', topChoice: 'UNCLEAR', qValue: 0.929 },
  { context: 'duration=chronic | symptom_a=fever | symptom_b=swelling', topChoice: 'UNCLEAR', qValue: 0.938 },
  { context: 'duration=chronic | symptom_a=fever | symptom_b=rash', topChoice: 'VIRAL', qValue: 0.933 },
  { context: 'duration=acute | symptom_a=pain | symptom_b=swelling', topChoice: 'INJURY', qValue: 0.947 },
  { context: 'duration=acute | symptom_a=fever | symptom_b=swelling', topChoice: 'UNCLEAR', qValue: 0.941 },
]

// Before/after tables from emergence_artifact_report.docx
export const triageBeforeAfter = [
  { context: 'severity=critical  resource=scarce  wait_time=short', correct: 'TREAT_FIRST', ep0: 'TREAT_FIRST', ep0correct: true, ep300: 'TREAT_FIRST', ep300correct: true },
  { context: 'severity=minor  resource=ample  wait_time=long', correct: 'WAIT', ep0: 'TREAT_FIRST', ep0correct: false, ep300: 'WAIT', ep300correct: true },
  { context: 'severity=moderate  resource=ample  wait_time=long', correct: 'WAIT', ep0: 'WAIT', ep0correct: true, ep300: 'WAIT', ep300correct: true },
]

export const navBeforeAfter = [
  { context: 'risk=high  urgency=urgent  cost=high', correct: 'SAFE_ROUTE', ep0: 'FAST_ROUTE', ep0correct: false, ep300: 'SAFE_ROUTE', ep300correct: true },
  { context: 'risk=low  urgency=relaxed  cost=low', correct: 'SCENIC_ROUTE', ep0: 'FAST_ROUTE', ep0correct: false, ep300: 'SCENIC_ROUTE', ep300correct: true },
  { context: 'risk=medium  urgency=normal  cost=low', correct: 'SAFE_ROUTE', ep0: 'SAFE_ROUTE', ep0correct: true, ep300: 'SAFE_ROUTE', ep300correct: true },
]

export const diagnosisBeforeAfter = [
  { context: 'symptom_a=fever  symptom_b=rash  duration=acute', correct: 'VIRAL', ep0: 'VIRAL', ep0correct: true, ep300: 'VIRAL', ep300correct: true },
  { context: 'symptom_a=fatigue  symptom_b=pallor  duration=chronic', correct: 'ANEMIA', ep0: 'VIRAL', ep0correct: false, ep300: 'ANEMIA', ep300correct: true },
  { context: 'symptom_a=pain  symptom_b=swelling  duration=chronic', correct: 'INJURY', ep0: 'INJURY', ep0correct: true, ep300: 'INJURY', ep300correct: true },
]

// Glyphs from EmerEviro_Evidence-1.docx — exact IDs, titles, substrates, accuracy
export const glyphs = [
  {
    id: 'g-cross-sequence@1.0.0',
    title: 'Cross Sequence Rule',
    substrate: 'compute',
    accuracy: '100%',
    description: 'C[n] = A[n] OP B[n]. Operation discovered by testing add/subtract/multiply/parity against known C values.',
  },
  {
    id: 'g-constraint-sat@1.0.0',
    title: 'Constraint Satisfaction Rule',
    substrate: 'solver',
    accuracy: '100%',
    description: 'One answer satisfies ALL constraints simultaneously. Parse constraints, evaluate every choice globally.',
  },
  {
    id: 'g-rule-inversion@1.0.0',
    title: 'Rule Inversion Detection',
    substrate: 'memory_probe',
    accuracy: '100%',
    description: 'Sequence follows rule R then inverts. Detect by delta sign change. Post-inversion delta extrapolates answer.',
  },
  {
    id: 'g-structural-analogy@1.0.0',
    title: 'Structural Analogy Transform',
    substrate: 'decomposer',
    accuracy: '98%',
    description: 'Transform is compound (×m+c, x²+c, -x+c). Decompose from A→B, apply identically to C.',
  },
  {
    id: 'g-code-pattern@1.0.0',
    title: 'Code Structure Invariant',
    substrate: 'bandit',
    accuracy: '65%→92%',
    description: 'Structural programming invariants. Stable across surfaces. Bandit learns from binary feedback — benefits from warm start.',
  },
]

// Real episode traces from routed_iq_report-1.docx
export const routedEpisodeTraces = [
  {
    ep: 1,
    class: 'Constraint Satisfaction',
    substrate: 'solver',
    correct: true,
    surface: 'code',
    features: { class: 'constraint_satisfaction', surface: 'code', constraint_count: '3', all_must_hold: 'true', has_divisibility: 'true', has_parity: 'true' },
    problem: 'Find the value N where your function must:\n  • accept N inputs (N divisible by 2)\n  • produce output whose digits sum to 5\n  • return even count',
    reasoning: 'choice=50 satisfies 3/3 constraints: [divisible by 2, digit sum = 5, even number]',
    choices: ['60', '50', '52', '49'],
    chosen: '50',
    answer: '50',
  },
  {
    ep: 5,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'code',
    features: { class: 'cross_sequence', surface: 'code', c_trend: 'up', a_vs_b: 'a_bigger', op_hint: 'add', relationship: 'between_series' },
    problem: 'A: [3, 7, 6]\nB: [5, 3, 4]\nC: [8, 10] + [?]',
    reasoning: 'A[n] add B[n] → 6 add 4 = 10',
    choices: ['12', '9', '10', '13'],
    chosen: '10',
    answer: '10',
  },
  {
    ep: 20,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'numeric',
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'down', a_vs_b: 'b_bigger', op_hint: 'sub', relationship: 'between_series' },
    problem: 'A: [1, 5, 3]\nB: [2, 5, 4]\nC: [1, 0] + [?]',
    reasoning: 'A[n] subtract B[n] → 3 subtract 4 = 1\nNote: parity check: 3 parity 4 = 1',
    choices: ['-2', '3', '4', '1'],
    chosen: '1',
    answer: '1',
  },
  {
    ep: 50,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'symbolic',
    features: { class: 'cross_sequence', surface: 'symbolic', c_trend: 'down', a_vs_b: 'b_bigger', op_hint: 'add', relationship: 'between_series' },
    problem: 'A: [2, 3, 1]\nB: [6, 3, 7]\nC: [8, 6] + [?]',
    reasoning: 'A[n] add B[n] → 1 add 7 = 8',
    choices: ['4', '10', '8', '3'],
    chosen: '8',
    answer: '8',
  },
  {
    ep: 100,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'numeric',
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'up', a_vs_b: 'a_bigger', op_hint: 'mul', relationship: 'between_series' },
    problem: 'A: [6, 8, 6]\nB: [7, 6, 6]\nC: [42, 48] + [?]',
    reasoning: 'A[n] multiply B[n] → 6 multiply 6 = 36',
    choices: ['40', '54', '36', '33'],
    chosen: '36',
    answer: '36',
  },
  {
    ep: 200,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'numeric',
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'up', a_vs_b: 'equal', op_hint: 'sub', relationship: 'between_series' },
    problem: 'A: [2, 3, 5]\nB: [4, 3, 3]\nC: [-2, 0] + [?]',
    reasoning: 'A[n] subtract B[n] → 5 subtract 3 = 2',
    choices: ['2', '8', '0', '3'],
    chosen: '2',
    answer: '2',
  },
  {
    ep: 300,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'numeric',
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'up', a_vs_b: 'b_bigger', op_hint: 'mul', relationship: 'between_series' },
    problem: 'A: [4, 2, 6]\nB: [3, 8, 5]\nC: [12, 16] + [?]',
    reasoning: 'A[n] multiply B[n] → 6 multiply 5 = 30',
    choices: ['20', '30', '32', '9'],
    chosen: '30',
    answer: '30',
  },
  {
    ep: 500,
    class: 'Cross-Sequence',
    substrate: 'compute',
    correct: true,
    surface: 'numeric',
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'up', a_vs_b: 'a_bigger', op_hint: 'add', relationship: 'between_series' },
    problem: 'A: [5, 8, 8]\nB: [5, 4, 5]\nC: [10, 12] + [?]',
    reasoning: 'A[n] add B[n] → 8 add 5 = 13',
    choices: ['11', '13', '14'],
    chosen: '13',
    answer: '13',
  },
]

// Unrouted traces from iq_emergence_report.docx — includes wrong answers
export const unroutedEpisodeTraces = [
  {
    ep: 1, class: 'Constraint Satisfaction', surface: 'code', correct: false,
    features: { class: 'constraint_satisfaction', surface: 'code', constraint_count: '3', all_must_hold: 'true', has_divisibility: 'true', has_parity: 'true' },
    problem: 'Find the value N where your function must:\n  • accept N inputs (N divisible by 2)\n  • produce output whose digits sum to 5\n  • return even count',
    choices: ['60 ← agent', '50 ← correct', '52', '49'],
    chosen: '60', answer: '50',
  },
  {
    ep: 5, class: 'Cross-Sequence', surface: 'code', correct: false,
    features: { class: 'cross_sequence', surface: 'code', c_trend: 'up', a_vs_b: 'a_bigger', op_hint: 'add', relationship: 'between_series' },
    problem: 'A: [3, 7, 6]\nB: [5, 3, 4]\nC: [8, 10] + [?]',
    choices: ['12', '9', '10 ← correct', '13 ← agent'],
    chosen: '13', answer: '10',
  },
  {
    ep: 20, class: 'Cross-Sequence', surface: 'numeric', correct: true,
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'down', a_vs_b: 'b_bigger', op_hint: 'sub', relationship: 'between_series' },
    problem: 'A: [1, 5, 3]\nB: [2, 5, 4]\nC: [1, 0] + [?]',
    choices: ['-2', '3', '4', '1 ← correct ← agent'],
    chosen: '1', answer: '1',
  },
  {
    ep: 50, class: 'Cross-Sequence', surface: 'symbolic', correct: false,
    features: { class: 'cross_sequence', surface: 'symbolic', c_trend: 'down', a_vs_b: 'b_bigger', op_hint: 'add', relationship: 'between_series' },
    problem: 'A: [2, 3, 1]\nB: [6, 3, 7]\nC: [8, 6] + [?]',
    choices: ['4', '10', '8 ← correct', '3 ← agent'],
    chosen: '3', answer: '8',
  },
  {
    ep: 500, class: 'Cross-Sequence', surface: 'numeric', correct: false,
    features: { class: 'cross_sequence', surface: 'numeric', c_trend: 'up', a_vs_b: 'a_bigger', op_hint: 'add', relationship: 'between_series' },
    problem: 'A: [5, 8, 8]\nB: [5, 4, 5]\nC: [10, 12] + [?]',
    choices: ['11', '13 ← correct', '14 ← agent'],
    chosen: '14', answer: '13',
  },
]

// Architecture layer table from EmerEviro_Blueprint.docx
export const architectureLayers = [
  { layer: 'Environment Layer', component: 'IQPatternEnv + EnvironmentBase', role: 'Problem generation, surface rotation, structural feature extraction' },
  { layer: 'Feature Extraction', component: '_extract_structural_features()', role: 'Raw problem → stable context dict. Class, trend, op_hint, constraints' },
  { layer: 'Cognitive Router', component: 'router.py → CognitiveRouter', role: 'Feature dict → substrate dispatch. Five states. Full routing log' },
  { layer: 'Substrates (×4+1)', component: 'compute / solver / decomposer / memory_probe / bandit', role: 'Purpose-built solvers. Identical interface: run(features, problem, choices) → (answer, expl)' },
  { layer: 'SextBioRAG Agent', component: '6-pillar hybrid (CME+TFE+BioRAG+PEE+PFC+Bandit)', role: 'Bandit fallback. Biological memory dynamics. Continuous update' },
  { layer: 'Persistence Layer', component: 'PersistentMemory + GlyphRegistry', role: 'Glyphs (invariants) + Cards (episodes) + agent_state.pkl across sessions' },
  { layer: 'NN Engine (Future)', component: 'nn_engine/ — NOT YET BUILT', role: 'Continual-learning specialist. Replaces Beta distributions. Hooks defined here' },
]

// Pattern classes from Blueprint
export const patternClasses = [
  { class: 'cross_sequence', description: 'C[n]=A[n] OP B[n]. OP is hidden. Surface: numeric/symbolic/code. Requires arithmetic.' },
  { class: 'constraint_satisfaction', description: 'N satisfies ALL constraints simultaneously. Requires global constraint search.' },
  { class: 'rule_inversion', description: 'Sequence follows R then inverts to ~R. Requires temporal trace + inversion detection.' },
  { class: 'structural_analogy', description: 'T(A)=B compound transform. Apply T to C. Requires algebraic decomposition.' },
  { class: 'code_pattern_hybrid', description: 'Structural programming invariants across surfaces. Learnable via experience alone.' },
]

// Memory files from Blueprint
export const memoryFiles = [
  { file: 'memory/agent_state.pkl', size: '208KB', desc: 'Full agent state: bandit posteriors (Beta distributions), BioRAG hippocampal traces + Hopfield matrices, PEE calibration, TFE snapshot, signal bus state.' },
  { file: 'memory/agent_glyphs.json', size: '4.6KB', desc: 'Human-readable. run_number, class_stats (accuracy per class), 5 glyphs, N cards. Editable. Agent reads it back next session.' },
  { file: 'memory/agent_memory.json', size: '34KB', desc: 'Full posteriors dict, pinned traces, glyphs, cards. For inspection and debugging.' },
]

// Routing states from Blueprint
export const routingStates = [
  { state: 'ROUTES_TO substrate', desc: 'Substrate called, returned confident answer, used directly' },
  { state: 'bandit_fallback', desc: 'Substrate returned None — Bandit takes over' },
  { state: 'DEFER (future)', desc: 'Router has no prior for this context — substrate decides' },
  { state: 'CONFIRM (future)', desc: 'Memory agrees with substrate answer — high confidence' },
  { state: 'CONFLICT (future)', desc: 'Memory disagrees — surface conflict, default to substrate, log salience' },
  { state: 'OVERRIDE (future)', desc: 'Memory earned override authority (>threshold accuracy in conflicts)' },
  { state: 'RETRACT (future)', desc: 'Override was wrong — prior erodes back toward CONFLICT. Self-correcting.' },
]

// Six pillars from Blueprint — exact names and descriptions
export const sixPillars = [
  { num: '1', name: 'CME', full: 'Cognitive Metabolic Residue', desc: 'emit_bias(condition,actions)→BiasSurface. Hard blocks recently-used actions. Soft-reduces actions with negative history. Prevents perseveration.' },
  { num: '2', name: 'TFE', full: 'Time Field Engine', desc: 'open_key(), update()→TFEObservables. Temporal decay — orphaned actions (used and failed) get weight 0.1, abandoned get 0.5. Time is a signal.' },
  { num: '3', name: 'BioRAG', full: 'Hippocampal + Hopfield Memory', desc: 'retrieve(condition,actions)→PillarSignal. Hopfield attractor convergence over stored patterns. Hippocampal index for episodic memory. Returns weighted signal.' },
  { num: '4', name: 'PEE', full: 'Prediction Error Engine', desc: 'predict_from_beta(alpha,beta)→prob,conf. Locks prediction BEFORE action. Computes surprise = |predicted−actual| after. High surprise = deeper encoding.' },
  { num: '5', name: 'PFC', full: 'Prefrontal Cortex', desc: 'evaluate(context,actions,fused_weights,...)→PFCSignal. Impulse control gate. Adjusts final weights based on novelty, uncertainty, consequence risk.' },
  { num: '6', name: 'Bandit', full: 'Thompson Sampling', desc: 'get_action(ctx_key,actions,...)→action,source,weights. Samples from Beta(alpha,beta) posteriors. Balances explore/exploit by posterior uncertainty.' },
]
