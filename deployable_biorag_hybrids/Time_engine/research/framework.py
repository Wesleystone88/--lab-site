"""
TFE Research Framework
Utilities for running exhaustive, seeded tests.
"""
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
import time

@dataclass
class TestResult:
    test_id: str
    phase: str
    seed: int
    passed: bool
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None

class ResearchSuite:
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        
    def run_seeded(self, test_func: Callable, test_id: str, phase: str, seeds: int = 50):
        print(f"Running {test_id} ({phase}) x{seeds} seeds...", end="", flush=True)
        failures = 0
        
        for i in range(seeds):
            seed = 42 + i
            rng = random.Random(seed)
            try:
                # Test function should return metrics dict or None
                # It should raise AssertionError on failure
                metrics = test_func(rng, seed)
                self.results.append(TestResult(test_id, phase, seed, True, metrics or {}))
            except AssertionError as e:
                self.results.append(TestResult(test_id, phase, seed, False, {}, str(e)))
                failures += 1
            except Exception as e:
                self.results.append(TestResult(test_id, phase, seed, False, {}, f"CRASH: {e}"))
                failures += 1
        
        if failures == 0:
            print(" PASS")
        else:
            print(f" FAIL ({failures}/{seeds})")

    def print_summary(self):
        print("\n" + "="*60)
        print(f"RESULTS: {self.name}")
        print("="*60)
        
        by_test = {}
        for r in self.results:
            if r.test_id not in by_test:
                by_test[r.test_id] = {"passed": 0, "total": 0, "errors": []}
            by_test[r.test_id]["total"] += 1
            if r.passed:
                by_test[r.test_id]["passed"] += 1
            else:
                by_test[r.test_id]["errors"].append(r.error)
                
        for tid, stat in by_test.items():
            pass_rate = stat["passed"] / stat["total"] * 100
            print(f"{tid:<5} | {pass_rate:6.1f}% Pass | {stat['passed']}/{stat['total']}")
            if stat["errors"]:
                print(f"      Sample Error: {stat['errors'][0]}")
        print("="*60 + "\n")
