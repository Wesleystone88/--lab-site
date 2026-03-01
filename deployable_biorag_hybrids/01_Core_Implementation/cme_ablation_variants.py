"""
CME Ablation Variants
=====================

Wrapper classes that disable specific CME mechanisms to prove necessity.

Variants:
1. CME-NoCompression: No rule sharing across contexts
2. CME-NoSupersession: Rules never superseded (immortal beliefs)
3. CME-NoTransfer: Memory wiped on environment change
4. CME-NoContextRouting: Ignores context, uses global rules
"""

from halcyon_research_demo import CME, RuleMemory, BiasSurface
from typing import Dict, List, Tuple
from collections import deque

# ============================================================
# Variant 1: CME-NoCompression
# ============================================================

class CME_NoCompression(CME):
    """
    CME without compression - forces separate rules per context.
    
    Mechanism Disabled: Rule sharing/generalization across contexts
    Expected Impact: Higher memory usage, no cross-context learning
    """
    
    def emit_bias(self, condition: Dict[str, str], actions: List[str]) -> BiasSurface:
        """
        Override: Only match rules with EXACT context match (no pattern sharing)
        """
        bias = BiasSurface(hard_blocks={}, weights={})
        
        for m in self.mem.values():
            if m.status != "ACTIVE":
                continue
            
            # KEY CHANGE: Require EXACT match, no generalization
            # Original CME uses _matches() which allows partial matches
            if m.condition_subset != condition:
                continue  # Skip if not exact match
            
            # Rest is same as parent
            if m.mem_type == "CONSTRAINT":
                bias.hard_blocks[m.action] = True
            elif m.mem_type == "PREFERENCE":
                bias.weights[m.action] = bias.weights.get(m.action, 0.0) + m.strength
        
        return bias

# ============================================================
# Variant 2: CME-NoSupersession
# ============================================================

class CME_NoSupersession(CME):
    """
    CME without supersession - rules are immortal.
    
    Mechanism Disabled: Evidence-based belief revision
    Expected Impact: Accumulates contradictory rules, confused in non-stationary environments
    """
    
    def counter_evidence(
        self,
        *,
        condition: Dict[str, str],
        action: str,
        success: bool,
        step: int,
    ) -> None:
        """
        Override: Track counter-evidence but NEVER supersede rules
        """
        if not success:
            return
        
        # Track evidence for observability, but don't act on it
        for m in self.mem.values():
            if m.status != "ACTIVE":
                continue
            if m.action != action:
                continue
            if not self._matches(condition, m.condition_subset):
                continue
            
            m.counter_evidence += 1.0
            m.counter_hits += 1
            
            # KEY CHANGE: Never mark as SUPERSEDED
            # Original CME would check threshold and supersede here
            # We just accumulate evidence but keep rule ACTIVE forever

# ============================================================
# Variant 3: CME-NoTransfer
# ============================================================

class CME_NoTransfer(CME):
    """
    CME without transfer learning - wipes memory on environment change.
    
    Mechanism Disabled: Knowledge retention across flips
    Expected Impact: No improvement in recovery time across flips
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recent_failures = deque(maxlen=20)
        self.failure_threshold = 0.5  # 50% failure rate triggers wipe
    
    def detect_environment_change(self) -> bool:
        """Detect if environment has changed (high failure rate)"""
        if len(self.recent_failures) < 20:
            return False
        
        failure_rate = sum(self.recent_failures) / len(self.recent_failures)
        return failure_rate > self.failure_threshold
    
    def reinforce_memory(
        self,
        *,
        mem_type,
        condition_subset: Dict[str, str],
        action: str,
        step: int,
    ) -> None:
        """
        Override: Track failures and wipe memory if environment change detected
        """
        # KEY CHANGE: Detect flip and wipe memory
        self.recent_failures.append(True)  # Track this failure
        
        if self.detect_environment_change():
            # WIPE MEMORY - start from scratch
            self.mem.clear()
            self.recent_failures.clear()
        
        # Then add new memory normally
        super().reinforce_memory(
            mem_type=mem_type,
            condition_subset=condition_subset,
            action=action,
            step=step
        )
    
    def counter_evidence(
        self,
        *,
        condition: Dict[str, str],
        action: str,
        success: bool,
        step: int,
    ) -> None:
        """Track successes for flip detection"""
        if success:
            self.recent_failures.append(False)
        
        # Call parent's counter_evidence
        super().counter_evidence(
            condition=condition,
            action=action,
            success=success,
            step=step
        )

# ============================================================
# Variant 4: CME-NoContextRouting
# ============================================================

class CME_NoContextRouting(CME):
    """
    CME without context-aware routing - ignores context distinctions.
    
    Mechanism Disabled: Context-specific rule application
    Expected Impact: Fails in multi-context environments, averages contradictions
    """
    
    def emit_bias(self, condition: Dict[str, str], actions: List[str]) -> BiasSurface:
        """
        Override: Ignore context, use ALL rules regardless of context match
        """
        bias = BiasSurface(hard_blocks={}, weights={})
        
        for m in self.mem.values():
            if m.status != "ACTIVE":
                continue
            
            # KEY CHANGE: Don't check if context matches
            # Use ALL active rules globally, regardless of condition
            
            if m.mem_type == "CONSTRAINT":
                bias.hard_blocks[m.action] = True
            elif m.mem_type == "PREFERENCE":
                bias.weights[m.action] = bias.weights.get(m.action, 0.0) + m.strength
        
        return bias
    
    def reinforce_memory(
        self,
        *,
        mem_type,
        condition_subset: Dict[str, str],
        action: str,
        step: int,
    ) -> None:
        """
        Override: Store rules without context (global rules)
        """
        # KEY CHANGE: Empty condition_subset = global rule
        super().reinforce_memory(
            mem_type=mem_type,
            condition_subset={},  # No context specificity!
            action=action,
            step=step
        )
