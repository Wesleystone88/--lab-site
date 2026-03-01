"""
run_integration.py
==================
Wires PhilosopherCellsSim + QuintBioRAGAgent through NoesisBridge.

This is the Phase 1 integration runner.
Run this when you're ready to test the full stack together.

Usage:
    # Quick smoke test (small grid, few steps)
    python run_integration.py --quick

    # Full run with default settings
    python run_integration.py

    # Medical domain, save checkpoint + card log
    python run_integration.py --domain medical --steps 500 \\
        --checkpoint agent_medical.pkl --log cards_medical.jsonl

    # Resume from checkpoint
    python run_integration.py --load agent_medical.pkl --steps 200

    # Headless (no print spam)
    python run_integration.py --quiet

    # With philosopher cells visualization
    python run_integration.py --viz

Dependencies:
    pip install numpy matplotlib   (for philosopher cells)

File layout expected:
    philosopher_cells_mvp.py      ← sim
    quint_biorag.py               ← agent (with its full dependency tree)
    noesis_bridge.py              ← bridge (this middleware)
    domain_loader.py              ← domain profiles
    glyph_registry.py             ← glyph/card registry
    pfc_engine.py                 ← Pillar 6a
    metacognitive_monitor.py      ← Pillar 6b
"""

import sys
import os
import argparse
import json
import time

# ── Path setup ────────────────────────────────────────────────
# Add quint_biorag dependencies to path
_here = os.path.dirname(os.path.abspath(__file__))
_biorag_core = os.path.join(
    _here, "..", "anchor_v002", "anchor_v002",
    "Tester", "01_Core_Implementation"
)
_sandbox = os.path.join(
    _here, "..", "anchor_v002", "anchor_v002",
    "Tester", "sandbox_hybrid"
)
for _p in [_here, _biorag_core, _sandbox]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)


# ─────────────────────────────────────────────────────────────
# IMPORT GUARD — fail early with clear messages
# ─────────────────────────────────────────────────────────────

def check_dependencies() -> dict:
    """Check which dependencies are available."""
    status = {}

    try:
        import numpy
        status["numpy"] = True
    except ImportError:
        status["numpy"] = False

    try:
        import matplotlib
        status["matplotlib"] = True
    except ImportError:
        status["matplotlib"] = False

    try:
        # philosopher cells lives wherever you put it
        import importlib.util
        spec = importlib.util.find_spec("philosopher_cells_mvp")
        status["philosopher_cells"] = spec is not None
    except Exception:
        status["philosopher_cells"] = False

    try:
        from quint_biorag import QuintBioRAGAgent
        status["quint_biorag"] = True
    except ImportError as e:
        status["quint_biorag"] = False
        status["quint_biorag_error"] = str(e)

    try:
        from noesis_bridge import NoesisBridge, BridgeConfig
        status["noesis_bridge"] = True
    except ImportError:
        status["noesis_bridge"] = False

    try:
        from domain_loader import DomainLoader
        status["domain_loader"] = True
    except ImportError:
        status["domain_loader"] = False

    try:
        from glyph_registry import bootstrap_registry
        status["glyph_registry"] = True
    except ImportError:
        status["glyph_registry"] = False

    return status


def print_dependency_report(status: dict) -> bool:
    """Print dependency status. Returns True if core deps available."""
    print("\n  Dependencies:")
    all_ok = True
    core = ["numpy", "philosopher_cells", "quint_biorag", "noesis_bridge"]
    optional = ["matplotlib", "domain_loader", "glyph_registry"]

    for dep in core:
        ok = status.get(dep, False)
        icon = "✓" if ok else "✗"
        note = ""
        if not ok:
            all_ok = False
            if dep == "philosopher_cells":
                note = " (need philosopher_cells_mvp.py in path)"
            elif dep == "quint_biorag":
                err = status.get("quint_biorag_error", "")
                note = f" ({err[:60]})" if err else " (check path setup)"
        print(f"    {icon} {dep}{note}")

    for dep in optional:
        ok = status.get(dep, False)
        icon = "✓" if ok else "○"
        note = " (optional)" if not ok else ""
        print(f"    {icon} {dep}{note}")

    return all_ok


# ─────────────────────────────────────────────────────────────
# INTEGRATION RUNNER
# ─────────────────────────────────────────────────────────────

def run_integration(args):
    """Main integration run."""

    # ── 1. Check deps ─────────────────────────────────────────
    print(f"\n{'═'*64}")
    print(f"  NOESIS BRIDGE — Phase 1 Integration")
    print(f"{'═'*64}")

    status = check_dependencies()
    core_ok = print_dependency_report(status)

    if not core_ok and not args.mock:
        print("\n  ✗ Core dependencies missing. Cannot run.")
        print("  Tip: use --mock to run with built-in mock sim+agent")
        print("  See integration path notes in noesis_bridge.py")
        return None
    elif not core_ok:
        print("\n  ○ Running in mock mode (core deps not available)")

    # ── 2. Import everything ──────────────────────────────────
    from noesis_bridge import NoesisBridge, BridgeConfig, _MockSim, _MockAgent
    from domain_loader import DomainLoader, DOMAIN_PROFILES

    if status["glyph_registry"]:
        from glyph_registry import bootstrap_registry
        bootstrap_registry()

    # ── 3. Build sim ──────────────────────────────────────────
    if status["philosopher_cells"] and not args.mock:
        from philosopher_cells_mvp import PhilosopherCellsSim
        sim = PhilosopherCellsSim(
            n=args.n,
            k=args.k,
            seed=args.seed,
            diff_U=0.20,
            decay_U=0.010,
            advect_on=args.advect,
            diff_D=0.010,
            decay_D=0.0002,
            spoof_frac=0.03,
            immune_strength=0.12,
        )
        print(f"\n  Sim: PhilosopherCellsSim(n={args.n}, k={args.k})")
    else:
        sim = _MockSim()
        print(f"\n  Sim: _MockSim (philosopher_cells not available)")

    # ── 4. Build agent ────────────────────────────────────────
    if status["quint_biorag"] and not args.mock:
        from quint_biorag import QuintBioRAGAgent
        agent = QuintBioRAGAgent(seed=args.seed)

        if args.load:
            try:
                agent.load_state(args.load)
                print(f"  Agent: QuintBioRAGAgent (resumed from {args.load})")
            except Exception as e:
                print(f"  Agent: QuintBioRAGAgent (load failed: {e}, starting fresh)")
        else:
            print(f"  Agent: QuintBioRAGAgent(seed={args.seed})")
    else:
        agent = _MockAgent()
        print(f"  Agent: _MockAgent (quint_biorag not available)")

    # ── 5. Build domain loader ────────────────────────────────
    domain_loader = None
    if status["domain_loader"]:
        domain_loader = DomainLoader(agent)
        print(f"  DomainLoader: ready  ({len(DOMAIN_PROFILES)} profiles)")

    # ── 6. Build bridge ───────────────────────────────────────
    cfg = BridgeConfig(
        sim_steps_per_agent_step = args.sim_steps,
        log_every_n              = 1 if args.verbose else args.log_every,
        card_log_enabled         = True,
        checkpoint_every_n       = args.checkpoint_every,
    )

    bridge = NoesisBridge(sim, agent, config=cfg, domain_loader=domain_loader)

    print(f"  Bridge: sim_steps_per_agent_step={args.sim_steps}")
    print(f"  Steps:  {args.steps} agent steps "
          f"({args.steps * args.sim_steps} sim steps approx)")
    if args.domain:
        print(f"  Domain: {args.domain}")
    print(f"{'─'*64}")

    # ── 7. Run ────────────────────────────────────────────────
    t0 = time.time()

    report = bridge.run(
        steps           = args.steps,
        target          = args.domain,
        checkpoint_path = args.checkpoint,
        log_path        = args.log,
        verbose         = not args.quiet,
    )

    elapsed = time.time() - t0
    print(f"\n  Elapsed: {elapsed:.1f}s  "
          f"({args.steps * args.sim_steps / elapsed:.0f} sim-steps/sec)")

    # ── 8. Save final checkpoint ──────────────────────────────
    if args.checkpoint and hasattr(agent, 'save_state'):
        try:
            agent.save_state(args.checkpoint)
            print(f"  Checkpoint saved: {args.checkpoint}")
        except Exception as e:
            print(f"  Checkpoint failed: {e}")

    # ── 9. Save final report ──────────────────────────────────
    if args.report:
        report["elapsed_seconds"] = round(elapsed, 2)
        report["args"] = vars(args)
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  Report saved: {args.report}")

    # ── 10. What to look for ──────────────────────────────────
    if not args.quiet:
        print(f"\n{'─'*64}")
        print(f"  WHAT TO LOOK FOR")
        print(f"{'─'*64}")
        print(f"""
  Good signs (agent is learning):
    ✓ Action distribution diversifies past step ~50
      Right now: {_top_actions(report, 3)}
    ✓ Ship acts increase over time (agent steering toward consensus)
      Total ship acts: {report.get('ship_acts', 0)}
    ✓ avg_reward trends upward in the card log
      Current avg: {report.get('avg_reward', 0):.4f}
    ✓ PFC escalation rate drops (agent gaining confidence)
      Total escalations: {report.get('pfc_escalations', 0)}

  Warning signs (something's wrong):
    ✗ Agent stuck on one action for 200+ steps
    ✗ avg_reward < 0.3 after 200 steps
    ✗ Ship acts = 0 after 500 steps (throughput never crossing threshold)

  Next steps:
    1. Inspect card log: {args.log or '(no log path set)'}
    2. Load checkpoint:  python run_integration.py --load {args.checkpoint or 'agent.pkl'}
    3. Try domain:       python run_integration.py --domain medical
    4. Scale up:         python run_integration.py --n 160 --steps 2000
""")

    return report


def _top_actions(report: dict, n: int) -> str:
    counts = report.get("action_counts", {})
    sorted_acts = sorted(counts.items(), key=lambda x: -x[1])[:n]
    return ", ".join(f"{a}={c}" for a, c in sorted_acts)


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Noesis Bridge — Phase 1 Integration Runner"
    )

    # Run control
    ap.add_argument("--steps",      type=int,   default=200,
                    help="agent decision steps (default 200)")
    ap.add_argument("--sim-steps",  type=int,   default=5,
                    help="sim steps per agent step (default 5)")
    ap.add_argument("--domain",     type=str,   default=None,
                    choices=["default","coding","medical","legal","financial","research"],
                    help="domain to load at start")
    ap.add_argument("--seed",       type=int,   default=42)
    ap.add_argument("--mock",       action="store_true",
                    help="force mock sim+agent (no real dependencies)")

    # Philosopher cells sim params
    ap.add_argument("--n",      type=int,  default=64,
                    help="grid size (default 64, use 160 for full fidelity)")
    ap.add_argument("--k",      type=int,  default=3,
                    help="strategy vector dimension (default 3)")
    ap.add_argument("--advect", action="store_true",
                    help="enable charismata advection in sim")

    # Output
    ap.add_argument("--checkpoint",       type=str, default=None,
                    help="path to save/resume agent state (.pkl)")
    ap.add_argument("--load",             type=str, default=None,
                    help="resume from this checkpoint")
    ap.add_argument("--log",              type=str, default=None,
                    help="path to write JSONL card log")
    ap.add_argument("--report",           type=str, default=None,
                    help="path to write JSON performance report")
    ap.add_argument("--checkpoint-every", type=int, default=100)
    ap.add_argument("--log-every",        type=int, default=25)
    ap.add_argument("--quiet",            action="store_true")
    ap.add_argument("--verbose",          action="store_true")
    ap.add_argument("--viz",              action="store_true",
                    help="run philosopher cells with matplotlib (separate process)")

    # Convenience presets
    ap.add_argument("--quick", action="store_true",
                    help="quick smoke test: n=16, steps=20, mock if deps missing")

    args = ap.parse_args()

    if args.quick:
        args.n         = 16
        args.steps     = 20
        args.sim_steps = 2
        args.log_every = 5
        print("  [quick mode]")

    run_integration(args)


if __name__ == "__main__":
    main()
