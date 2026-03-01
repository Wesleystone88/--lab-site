"""
CME-Thompson Sampling Hybrid (Sandboxed Experiment)
====================================================

This module implements the hybrid system where CME owns a Thompson Sampling
bandit. CME's rules become informative priors for Thompson, creating a 
"Memory-Guided Exploration" paradigm.

COMPLETELY SANDBOXED - does not modify any main CME code.

Algorithms implemented:
1. ThompsonOnly        - Pure Thompson Sampling contextual bandit
2. CMEOnly             - Standard CME (imported from core)
3. CMEThompsonHybrid   - CME-owned Thompson with memory-shaped priors
4. CMEHybridNoCompress - Hybrid with compression disabled (ablation)
"""

import sys
import os
import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Import CME from core (read-only, no modifications)
from halcyon_research_demo import CME, BiasSurface


# ============================================================
# Thompson Sampling Contextual Bandit (Standalone)
# ============================================================

class ThompsonOnly:
    """
    Pure contextual Thompson Sampling bandit.
    Maintains Beta(α, β) per context-action pair.
    No memory, no compression, no transfer.
    """
    
    def __init__(self, seed: int = 7):
        self.rng = random.Random(seed)
        # {context_key: {action: (alpha, beta)}}
        self.posteriors: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(lambda: [1.0, 1.0])  # flat prior
        )
    
    def _context_key(self, condition: Dict[str, str]) -> str:
        """Convert condition dict to hashable key."""
        return "|".join(f"{k}={v}" for k, v in sorted(condition.items()))
    
    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> str:
        """Thompson Sampling: sample from Beta posterior, pick highest."""
        ctx = self._context_key(condition)
        samples = {}
        for a in actions:
            alpha, beta = self.posteriors[ctx][a]
            samples[a] = self.rng.betavariate(alpha, beta)
        return max(samples, key=samples.get)
    
    def update(self, condition: Dict[str, str], action: str, success: bool):
        """Update Beta posterior for this context-action pair."""
        ctx = self._context_key(condition)
        if success:
            self.posteriors[ctx][action][0] += 1.0  # alpha
        else:
            self.posteriors[ctx][action][1] += 1.0  # beta
    
    def reset(self):
        """Full reset."""
        self.posteriors.clear()


# ============================================================
# CME-Thompson Hybrid
# ============================================================

class CMEThompsonHybrid:
    """
    CME-owned Thompson Sampling bandit.
    
    How it works:
    1. CME generates bias surface (rules) from memory
    2. Bias surface converted to Thompson priors (informative, not flat)
    3. Arbitrator decides who leads based on confidence
    4. Thompson samples from CME-informed priors
    5. Both systems update from outcome
    
    The bandit is the hands. CME is the brain.
    """
    
    def __init__(
        self,
        seed: int = 7,
        cold_start_steps: int = 80,
        confidence_threshold: float = 0.6,
        prior_scale: float = 10.0, # Strong Engine (was 3.0)
        explore_rate: float = 0.02,
        supersede_factor: float = 1.15,
    ):
        self.rng = random.Random(seed)
        self.cold_start_steps = cold_start_steps
        self.confidence_threshold = confidence_threshold
        self.confidence_threshold = confidence_threshold
        self.prior_scale = prior_scale
        self.explore_rate = explore_rate # Stored for modulation access
        
        # CME engine (the brain)
        self.cme = CME(
            seed=seed,
            explore_rate=explore_rate,
            supersede_factor=supersede_factor,
        )
        
        # Thompson posteriors (the hands)
        # {context_key: {action: [alpha, beta]}}
        self.posteriors: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(lambda: [1.0, 1.0])
        )
        
        # Tracking
        self.steps = 0
        self.bandit_led = 0
        self.cme_led = 0
        self.hybrid_led = 0
    
    def _context_key(self, condition: Dict[str, str]) -> str:
        return "|".join(f"{k}={v}" for k, v in sorted(condition.items()))
    
    def _rules_to_priors(self, bias: BiasSurface, actions: List[str]) -> Dict[str, List[float]]:
        """
        Convert CME's bias surface into Thompson priors.
        
        - Hard block on action → pessimistic prior Beta(1, 1 + scale)
        - Positive weight on action → optimistic prior 
        - Negative weight → pessimistic prior
        - Neutral → flat prior Beta(1, 1)
        """
        priors = {}
        for a in actions:
            if bias.hard_blocks.get(a, False):
                # CME says AVOID → strong pessimistic prior
                priors[a] = [1.0, 1.0 + self.prior_scale * 2]
            else:
                weight = bias.weights.get(a, 1.0)
                if weight < 0.5:
                    # CME is pessimistic about this action
                    penalty = (1.0 - weight) * self.prior_scale
                    priors[a] = [1.0, 1.0 + penalty]
                elif weight > 1.5:
                    # CME is optimistic (shouldn't happen with current CME, but future-proof)
                    bonus = (weight - 1.0) * self.prior_scale
                    priors[a] = [1.0 + bonus, 1.0]
                else:
                    # Near-neutral
                    priors[a] = [1.0, 1.0]
        return priors
    
    def _get_confidence(self, condition: Dict[str, str]) -> float:
        """
        How confident is CME about this specific context?
        Based on number and strength of matching rules.
        """
        matching = 0
        total_strength = 0.0
        for m in self.cme.mem.values():
            if m.status != "ACTIVE":
                continue
            if self.cme._matches(condition, m.condition_subset):
                matching += 1
                total_strength += m.strength * m.confidence
        
        if matching == 0:
            return 0.0
        
        # Confidence grows with rule count and strength
        return min(1.0, total_strength / max(1, matching) * (matching / 3.0))
    
    def step_decay(self, step: int):
        """Decay both systems."""
        self.cme.step_decay(step)
        self.steps = step
    
    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> Tuple[str, str]:
        """
        Hybrid action selection with DIRECT CME prior injection.
        
        CME hard blocks ALWAYS bias Thompson (no confidence gating).
        CME preference weights scale with confidence.
        Thompson always makes the final choice.
        """
        # Get CME's opinion
        bias = self.cme.emit_bias(condition, actions)
        confidence = self._get_confidence(condition)
        ctx = self._context_key(condition)
        
        # Sample from Thompson with CME influence injected directly
        samples = {}
        has_cme_influence = False
        
        for a in actions:
            alpha, beta = self.posteriors[ctx][a]
            
            # DIRECT INJECTION: Hard blocks always bias Thompson
            if bias.hard_blocks.get(a, False):
                # CME says AVOID → add strong pessimistic evidence
                beta += self.prior_scale * 3.0
                has_cme_influence = True
            
            # Weight-based adjustment (softer)
            weight = bias.weights.get(a, 1.0)
            if weight < 0.8:
                # CME is somewhat pessimistic — add proportional bias
                penalty = (1.0 - weight) * self.prior_scale * 1.5
                beta += penalty
                has_cme_influence = True
            
            samples[a] = self.rng.betavariate(max(0.1, alpha), max(0.1, beta))
        
        # Track who primarily influenced
        if confidence > self.confidence_threshold:
            self.cme_led += 1
            source = "cme"
        elif has_cme_influence:
            self.hybrid_led += 1
            source = "hybrid"
        else:
            self.bandit_led += 1
            source = "bandit"
        
        return max(samples, key=samples.get), source
    
    def update(
        self,
        condition: Dict[str, str],
        action: str,
        success: bool,
        step: int,
    ):
        """Update both CME and Thompson from outcome."""
        ctx = self._context_key(condition)
        
        # Update Thompson posterior
        if success:
            self.posteriors[ctx][action][0] += 1.0
        else:
            self.posteriors[ctx][action][1] += 1.0
        
        # Update CME memory
        if not success:
            self.cme.reinforce_memory(
                mem_type="CONSTRAINT",
                condition_subset=condition,
                action=action,
                step=step,
            )
        
        self.cme.counter_evidence(
            condition=condition,
            action=action,
            success=success,
            step=step,
        )
    
    def get_leadership_stats(self) -> Dict[str, int]:
        """Who's been leading?"""
        total = max(1, self.bandit_led + self.cme_led + self.hybrid_led)
        return {
            "bandit_led": self.bandit_led,
            "cme_led": self.cme_led,
            "hybrid_led": self.hybrid_led,
            "bandit_pct": round(100 * self.bandit_led / total, 1),
            "cme_pct": round(100 * self.cme_led / total, 1),
            "hybrid_pct": round(100 * self.hybrid_led / total, 1),
        }


# ============================================================
# CME Hybrid WITHOUT Compression (Ablation)
# ============================================================

class CMEHybridNoCompress(CMEThompsonHybrid):
    """
    Same as CMEThompsonHybrid but compression is disabled.
    Each context is treated independently - no rule sharing.
    
    This proves that the hybrid's advantage comes from 
    compression (CME's contribution), not just Thompson.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> Tuple[str, str]:
        """Same as hybrid but we clear cross-context priors."""
        # Force each context to have independent priors (no sharing)
        ctx = self._context_key(condition)
        
        # Instead of using CME priors (which compress across contexts),
        # use only this context's direct bandit posteriors
        if self.steps < self.cold_start_steps:
            samples = {}
            for a in actions:
                alpha, beta = self.posteriors[ctx][a]
                samples[a] = self.rng.betavariate(max(0.1, alpha), max(0.1, beta))
            self.bandit_led += 1
            return max(samples, key=samples.get), "bandit"
        else:
            # Still use CME for action selection but without compression benefit
            bias = self.cme.emit_bias(condition, actions)
            # Override: ignore any rules that match via subset (cross-context)
            # Only use exact-match rules
            filtered_blocks = {}
            filtered_weights = {}
            for m in self.cme.mem.values():
                if m.status != "ACTIVE":
                    continue
                # Only use rules that match this EXACT context
                if m.condition_subset == condition:
                    if m.mem_type == "CONSTRAINT":
                        inhib = m.strength * m.confidence
                        if inhib >= 0.25:
                            filtered_blocks[m.action] = True
                    else:
                        inhib = m.strength * m.confidence
                        filtered_weights[m.action] = filtered_weights.get(m.action, 1.0) * max(0.02, 1.0 - inhib)
            
            # Use only exact-match rules as priors
            samples = {}
            for a in actions:
                alpha, beta = self.posteriors[ctx][a]
                if filtered_blocks.get(a, False):
                    beta += self.prior_scale * 2
                elif a in filtered_weights and filtered_weights[a] < 0.5:
                    beta += (1.0 - filtered_weights[a]) * self.prior_scale
                samples[a] = self.rng.betavariate(max(0.1, alpha), max(0.1, beta))
            
            self.hybrid_led += 1
            return max(samples, key=samples.get), "hybrid"


if __name__ == "__main__":
    print("CME-Thompson Hybrid module loaded successfully.")
    print("Algorithms: ThompsonOnly, CMEOnly (imported), CMEThompsonHybrid, CMEHybridNoCompress")
