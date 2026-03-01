# EMERGENCE MVP — CONFIG & NEXT STEPS
# Edit this file to switch features on/off and track progress.
# No need to dig through code — all the knobs are here.

# ===========================================================================
# EXPERIMENT SETTINGS
# ===========================================================================

EPISODES = 100          # total episodes per agent run
PROBE_INTERVAL = 25     # run diagnostic suite every N episodes
CAPACITY_TOTAL = 50     # max AST nodes the library can hold
EPISODE_BUDGET = 5.0    # reward budget per episode

# Action costs (Tier 0 / 1 / 2)
COST_ASSEMBLE = 0.05
COST_MUTATE   = 0.30
COST_MINT     = 1.00

# Compression
STABILITY_WINDOW    = 10    # rolling window for time-to-stability
STABILITY_THRESHOLD = 0.05  # reward variance below this = stable

# Primitive matching
EDIT_BUDGET_EPSILON = 2     # max AST node edits for a "match"
                            # 0 = exact only (too rigid)
                            # 1-2 = good for math/logic
                            # scale to primitive size for larger domains


# ===========================================================================
# AGENT SELECTION
# ============================================================================
# Swap the active agent here. Options:
#
#   "candidate"   → CandidateAgent (placeholder, demonstrates plumbing)
#   "null_b"      → NullB_NoMinting (assembly only, no new primitives)
#   "null_c"      → NullC_EpisodicMemory (persistence, no structure)
#   "claude"      → ClaudeAgent (LLM-powered — see agents/claude_agent.py)
#   "custom"      → point CUSTOM_AGENT_PATH to your own file
#
ACTIVE_AGENT = "candidate"

CUSTOM_AGENT_PATH = ""   # e.g. "agents/my_agent.py" — must subclass AgentClient


# ===========================================================================
# TASK GENERATOR
# ===========================================================================
# Style index controls which variable pool is used.
# Swap mid-run to test generator leakage.
#
#   0 → [x, y, z]
#   1 → [a, b, c]
#   2 → [u, v, w]
#   3 → [p, q, r]
#
GENERATOR_STYLE = 0
GENERATOR_SEED  = 42

# Set to True to run multi-generator leakage probe automatically
RUN_LEAKAGE_PROBE = False   # TODO: wire to second generator in math_env.py


# ===========================================================================
# NULL MODELS TO RUN
# ===========================================================================
# Toggle which nulls run in the comparison.
# All three should be True for a valid emergence claim.
#
RUN_NULL_A = False   # Library reset (TODO: needs env-side reset hook)
RUN_NULL_B = True    # No minting
RUN_NULL_C = True    # Episodic memory only


# ===========================================================================
# METRICS TO REPORT
# ===========================================================================
REPORT_REUSE_RATE       = True
REPORT_BCG              = True    # NOTE: needs used_library_primitive fix first
REPORT_TIME_TO_STABILITY = True
REPORT_NET_BCG          = False   # TODO: charge library description length


# ===========================================================================
# NEXT STEPS (check off as done)
# ===========================================================================
#
# WIRING FIXES (small, do first)
# [ ] Fix BCG: propagate used_library_primitive flag from StepResult → trace
# [ ] Wire ACTIVE_AGENT switch into run_experiment.py
# [ ] Wire RUN_NULL_A: add library.reset() hook to MathEnvironment
#
# GENERATOR (defeat leakage)
# [ ] Add 3 more TaskGenerators with different surface styles
# [ ] Wire generator swap probe (currently stubbed in run_probes())
# [ ] Add spurious correlation: inject a fake formatting pattern at training,
#     invert at eval — if agent chases it, you caught leakage
#
# METRICS
# [ ] NetBCG: subtract DL(library) from BCG so big unused libraries don't win
# [ ] Counterfactual Avoidance: track failed actions, measure re-attempt rate
# [ ] Perturbation Recovery: break env slightly mid-run, measure recovery speed
#
# AGENTS
# [ ] ClaudeAgent: call Anthropic API, pass Observation as prompt,
#     parse Action from response — claude_agent.py skeleton ready to fill
# [ ] Real RL agent (PPO or similar) — environment is Gym-compatible enough
#
# GOLDEN SET (do before any serious claims)
# [ ] Build 20+ known-equivalent expression pairs for ε calibration
# [ ] Build 20+ known-distinct pairs
# [ ] Tune EDIT_BUDGET_EPSILON until matcher hits >95% on golden set
# [ ] Document failures
#
# VALIDITY
# [ ] Confirm candidate beats ALL active nulls on:
#       mean_reward, reuse_rate, bcg, cross-generator transfer
# [ ] If not → no emergence claim. That's fine. Means instrument is working.
