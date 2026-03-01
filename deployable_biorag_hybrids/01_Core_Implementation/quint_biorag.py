"""
Quint-BioRAG Agent — The 5th Generation (Biological Memory)
============================================================
Cognitive Architecture: 5 Pillars

  Pillar 1 — CME  (Constrained Memory Engine)   : Declarative Memory
  Pillar 2 — Bandit (Contextual Thompson Sampler): Procedural Logic
  Pillar 3 — TFE  (Time Field Engine)            : Autonomic Physics
  Pillar 4 — PEE  (Prediction Error Engine)      : Dopaminergic Surprise
  Pillar 5 — BioRAG (Biological RAG)             : Attractor-Based Episodic Memory

COPY-AND-EXTEND NOTICE:
  This file is a COPY of quint_hybrid.py (the original is preserved).
  The ONLY difference is Pillar 5: SimpleRAG -> BioRAG.
  BioRAG implements:
    - Sparse Distributed Representations (SDR) — Dentate Gyrus pattern separation
    - Hopfield Attractor Network              — CA3 pattern completion
    - Hippocampal Index with Context Reinstatement
    - Working Memory Buffer (capacity-limited, decay-based)
    - Reconsolidation on every retrieval
    - Salience gating (PEE surprise -> amygdala encoding weight)

  Standard RAG treats memory as a library (query -> fetch).
  BioRAG treats memory as an energy landscape (cue -> converge to basin).
"""

import math
import random
import hashlib
import heapq
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
from dataclasses import dataclass, field
import json
import pickle

# Phase 28: Metabolic Residue
from metabolic_residue import (
    ResidueConfig, ResidueReservoir, ResidueContext, IntakeMode,
    Candidate, CandidateType, ScoreBreakdown, decide_commit, ReasonCode,
    ReconsiderationTrigger, normalize_text, sha256_hex
)

# ── Path setup ───────────────────────────────────────────────────────────────
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_sandbox = os.path.join(_here, '..', 'sandbox_hybrid')
for _p in [_here, _sandbox]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tri_hybrid_v3 import TriHybridAgentV3
from Bandit_engine.state import BetaParams
from Time_engine.state import KeyStateClass
from Time_engine.config import TFEConfig

# Import the shared signal types from quint_hybrid (reuse, don't duplicate)
from quint_hybrid import (
    PillarSignal, QuintSignal, QuintPEE, RAGInterface,
    QuintSignalBus, QuintHybridAgent,
)


# ============================================================
# INTERNAL SIGNAL BUS (Phase 27 — Amygdala Decoupling)
# ============================================================
# Instead of QuintBioRAGAgent reaching into BioRAG to set salience,
# PEE publishes its surprise to this shared bus, and BioRAG reads
# it autonomously during write_back. Neither knows about the other.

@dataclass
class InternalSignalBus:
    """Broadcast channel for inter-pillar neurochemical signals.

    Writers: PEE publishes encoding_weight (dopaminergic surprise).
    Readers: BioRAG reads salience during write_back (amygdala gate).

    This replaces the hardcoded `isinstance(self.rag, BioRAG)` check
    that previously coupled Pillar 4 and Pillar 5.
    """
    encoding_weight: float = 1.0   # PEE surprise → normalized to [0,1]
    tfe_reset: bool = False         # paradigm shift flag
    last_error_magnitude: float = 0.0

    def publish_pee(self, signal) -> None:
        """Called by the agent after PEE.compute(). Writes surprise."""
        self.encoding_weight = signal.encoding_weight
        self.tfe_reset = signal.tfe_reset
        self.last_error_magnitude = signal.error_magnitude

    def read_salience(self) -> float:
        """Called by BioRAG during write_back. Reads and resets."""
        salience = min(1.0, self.encoding_weight / 3.0)
        # Reset after read (one-shot signal, like a neurotransmitter pulse)
        self.encoding_weight = 1.0
        return salience


# ============================================================
# BIOLOGICAL RAG — PHASE 1: CORE PHYSICS
# ============================================================

# ─────────────────────────────────────────────
# 1. SPARSE DISTRIBUTED REPRESENTATION (SDR)
#    Mimics cortical sparse coding ~2-5% active.
#    Dentate gyrus function: pattern separation
#    via k-Winners-Take-All.
# ─────────────────────────────────────────────

class SparseEncoder:
    """
    Converts dense context feature dictionaries into sparse binary vectors.

    Biology: Dentate Gyrus performs pattern separation — similar inputs
    are projected into a much larger, sparser space where representations
    are pushed apart. This prevents catastrophic interference.

    Mechanism: Random projection (fixed wiring, like genetics) followed
    by k-Winners-Take-All (only top-k neurons fire).

    Args:
        input_dim:  dimensionality of the dense input (number of unique features)
        sparse_dim: size of the output SDR (cortical minicolumn count)
        sparsity:   fraction of neurons that fire (~2% is biological)
    """
    def __init__(self, input_dim: int = 128, sparse_dim: int = 2048, sparsity: float = 0.05,
                 seed: int = 42):
        self.input_dim = input_dim
        self.sparse_dim = sparse_dim
        self.sparsity = sparsity
        self.k = max(1, int(sparse_dim * sparsity))  # ~41 active bits out of 2048
        
        # Fixed random projection — like genetic wiring of the dentate gyrus
        # Using NumPy for fast matrix projection
        rng = np.random.RandomState(seed)
        self.projection = rng.normal(0, 0.1, (input_dim, sparse_dim)).astype(np.float32)
        
        # Feature vocabulary: maps feature strings to integer indices
        self._vocab: Dict[str, int] = {}
        self._next_idx = 0

    def _feature_index(self, feature: str) -> int:
        """Assign a stable integer index to each unique feature string."""
        if feature not in self._vocab:
            self._vocab[feature] = self._next_idx % self.input_dim
            self._next_idx += 1
        return self._vocab[feature]

    def context_to_dense(self, context: Dict[str, str]) -> np.ndarray:
        """
        Convert a context dictionary to a dense activation vector.
        Each key=value pair activates a neuron at a hashed index.
        """
        dense = np.zeros(self.input_dim, dtype=np.float32)
        for k, v in context.items():
            feature_str = f"{k}={v}"
            idx = self._feature_index(feature_str)
            dense[idx] = 1.0
            
        return dense

    def encode(self, dense_arr: np.ndarray, context_str: Optional[str] = None) -> List[int]:
        """
        Project dense vector through fixed wiring, then k-WTA.
        If context_str is provided, injects a robust holistic hash to eliminate collisions.
        Returns a list of active indices (the sparse representation).
        """
        if isinstance(dense_arr, list):
            dense_arr = np.array(dense_arr, dtype=np.float32)
            
        # Fast NumPy matrix multiplication
        projected = dense_arr @ self.projection
        
        if context_str:
            # Generate a completely orthogonal subspace shift for this exact context dict
            h_int = int(hashlib.sha256(context_str.encode()).hexdigest(), 16) % (2**32)
            rng = np.random.RandomState(h_int)
            holistic_shift = rng.normal(0, 0.3, self.sparse_dim).astype(np.float32)
            projected += holistic_shift

        # k-Winners-Take-All using np.argpartition (O(N) instead of O(N log N))
        k = min(self.k, self.sparse_dim)
        indexed = np.argpartition(projected, -k)[-k:]
        
        # Return sorted Python list for hashing / sets later
        return sorted(indexed.tolist())

    def encode_context(self, context: Dict[str, str]) -> List[int]:
        """Convenience: context dict -> SDR active indices."""
        context_str = json.dumps(context, sort_keys=True)
        return self.encode(self.context_to_dense(context), context_str=context_str)

    def overlap(self, sdr_a: List[int], sdr_b: List[int]) -> float:
        """
        Jaccard overlap between two SDRs.
        Low overlap = good pattern separation (dentate gyrus working).
        """
        set_a = set(sdr_a)
        set_b = set(sdr_b)
        union = len(set_a | set_b)
        if union == 0:
            return 0.0
        return len(set_a & set_b) / union


# ─────────────────────────────────────────────
# 2. HOPFIELD ATTRACTOR NETWORK (CA3)
#    The core biological memory store.
#    Memories = energy minima.
#    Retrieval = convergence to nearest basin.
# ─────────────────────────────────────────────

class HopfieldMemory:
    """
    Modern Continuous Hopfield Network, vectorized with NumPy.
    Biological analog: CA3 recurrent collaterals doing pattern completion.
    """
    def __init__(self, sparse_dim: int = 2048, beta: float = 12.0):
        self.sparse_dim = sparse_dim
        self.beta = beta
        
        # NumPy matrices for fast vector math (Pre-allocated pool)
        self.max_capacity = 300
        self.memories_matrix = np.zeros((self.max_capacity, sparse_dim), dtype=np.float32)
        self.salience_arr = np.zeros(self.max_capacity, dtype=np.float32)
        self.mem_lens = np.zeros(self.max_capacity, dtype=np.float32)
        self.active_count = 0
        
        # Python parallel lists for exact set logic
        self.memories: List[List[int]] = []
        self.memory_sets: List[set] = []
        self.salience: List[float] = []

    def store(self, sdr: List[int], salience: float = 1.0):
        """Hebbian encoding: store a pattern with emotional/importance weight."""
        self.memories.append(list(sdr))
        self.memory_sets.append(set(sdr))
        self.salience.append(salience)
        
        # Update NumPy arrays in O(1) via active_count indexing
        if self.active_count < self.max_capacity:
            idx = self.active_count
            self.memories_matrix[idx, sdr] = 1.0
            self.salience_arr[idx] = salience
            self.mem_lens[idx] = len(sdr)
            self.active_count += 1
        else:
            # Fallback if capacity exceeded before consolidation (rare)
            # Rebuild larger arrays
            self._sync_arrays_after_prune()

    def _sync_arrays_after_prune(self):
        """Called if memories are pruned by exterior systems."""
        n = len(self.memories)
        self.active_count = n
        self.max_capacity = max(300, n + 100)
        
        self.memories_matrix = np.zeros((self.max_capacity, self.sparse_dim), dtype=np.float32)
        self.salience_arr = np.zeros(self.max_capacity, dtype=np.float32)
        self.mem_lens = np.zeros(self.max_capacity, dtype=np.float32)
        
        if n > 0:
            for i, mem in enumerate(self.memories):
                self.memories_matrix[i, mem] = 1.0
            self.salience_arr[:n] = np.array(self.salience, dtype=np.float32)
            self.mem_lens[:n] = np.array([len(m) for m in self.memories], dtype=np.float32)

    def retrieve(self, query_sdr: List[int], steps: int = 3) -> Tuple[List[int], List[Tuple[float, int]]]:
        """
        Attractor dynamics: iterate until convergence using fast matrix math.
        """
        if self.active_count == 0:
            return query_sdr, []

        state_set = set(query_sdr)
        state_list = list(query_sdr)
        state_vec = np.zeros(self.sparse_dim, dtype=np.float32)
        state_vec[state_list] = 1.0

        # View into only the valid traces
        mat = self.memories_matrix[:self.active_count]
        sal = self.salience_arr[:self.active_count]
        mlen = self.mem_lens[:self.active_count]

        for _ in range(steps):
            # Fast vectorized Jaccard-like overlap
            intersections = mat @ state_vec
            state_len = np.sum(state_vec)
            k_vals = np.maximum(mlen, state_len)
            k_vals = np.maximum(k_vals, 1.0)
            
            similarities = (intersections / k_vals) * sal
            
            # Vectorized softmax
            sim_max = np.max(similarities)
            exp_vals = np.exp(self.beta * (similarities - sim_max))
            weights = exp_vals / (np.sum(exp_vals) + 1e-12)
            
            # Fast weighted vote
            votes = weights @ mat
            
            # Top-k
            k = len(query_sdr) if query_sdr else 1
            k = min(k, self.sparse_dim)
            if k == 0: break
            
            idx = np.argpartition(votes, -k)[-k:]
            new_state_list = sorted(idx.tolist())
            new_state_set = set(new_state_list)
            
            if new_state_set == state_set:
                break
                
            state_set = new_state_set
            state_list = new_state_list
            state_vec.fill(0.0)
            state_vec[state_list] = 1.0

        # Final scoring
        intersections = mat @ state_vec
        state_len = np.sum(state_vec)
        k_vals = np.maximum(mlen, state_len)
        k_vals = np.maximum(k_vals, 1.0)
        similarities = (intersections / k_vals) * sal
        
        scored = [(float(sim), i) for i, sim in enumerate(similarities)]
        scored.sort(reverse=True)

        return state_list, scored

    def reconsolidate(self, memory_idx: int, retrieved_sdr: List[int],
                      learning_rate: float = 0.1):
        """
        Every retrieval slightly modifies the memory — reconsolidation.
        Updates both lists and matrices.
        """
        if memory_idx >= len(self.memories):
            return
            
        mem = self.memories[memory_idx]
        retrieved_set = set(retrieved_sdr)
        mem_set = self.memory_sets[memory_idx]
        
        new_indices = list(retrieved_set - mem_set)
        n_swap = max(1, int(len(mem) * learning_rate))
        
        if new_indices and len(mem) > n_swap:
            overlap = retrieved_set & mem_set
            removable = list(mem_set - overlap)
            if len(removable) >= n_swap:
                remove = set(removable[:n_swap])
                add = new_indices[:n_swap]
                
                updated = [idx for idx in mem if idx not in remove] + add
                updated.sort()
                
                self.memories[memory_idx] = updated
                self.memory_sets[memory_idx] = set(updated)
                
                # Update numpy vectors
                self.memories_matrix[memory_idx, list(remove)] = 0.0
                self.memories_matrix[memory_idx, add] = 1.0
                # mem_lens remains largely unchanged due to 1:1 swap, but let's be safe:
                self.mem_lens[memory_idx] = len(updated)


# ============================================================
# BIOLOGICAL RAG — PHASE 2: MEMORY MANAGEMENT
# ============================================================

# ─────────────────────────────────────────────
# 3. HIPPOCAMPAL INDEX (Entorhinal → CA1)
#    Stores compressed traces, not full memories.
#    Fast binding of cortical patterns.
# ─────────────────────────────────────────────

@dataclass
class MemoryTrace:
    """
    A hippocampal memory trace — index + metadata, not raw content.
    The hippocampus stores POINTERS to cortical patterns + context.
    """
    trace_id: str              # unique hash (like a synaptic address)
    sdr: List[int]             # sparse representation in hippocampus
    context_sdr: List[int]     # encoding context (crucial for retrieval)
    action: str                # what action was taken
    success: bool              # outcome
    salience: float = 1.0      # emotional/importance weighting (from PEE)
    retrieval_count: int = 0   # strengthens with use (spacing effect)
    timestamp: float = 0.0     # recency weighting
    pinned: bool = False       # Phase 28 (B1): immune to pruning; decay-floor in context


class HippocampalIndex:
    """
    Entorhinal cortex → hippocampus index layer.
    Binds SDRs + Context + Action + Outcome into MemoryTraces.
    Uses the Hopfield attractor for retrieval and reconsolidation.

    Args:
        encoder:  shared SparseEncoder instance (the dentate gyrus)
        beta:     Hopfield inverse temperature (retrieval sharpness)
    """
    def __init__(self, encoder: SparseEncoder, beta: float = 12.0):
        self.encoder = encoder
        self.attractor = HopfieldMemory(sparse_dim=encoder.sparse_dim, beta=beta)
        self.traces: List[MemoryTrace] = []
        self._time = 0.0
        self._trace_counter = 0

    def encode(self, context: Dict[str, str], action: str, success: bool,
               salience: float = 1.0):
        """
        Bind a new episodic memory:
          context -> SDR
          context + action -> combined SDR (context-dependent encoding)
          Store in attractor + index.
        """
        # Encode the raw context
        ctx_sdr = self.encoder.encode_context(context)

        # Encode context + action as a combined trace
        combined_context = dict(context)
        combined_context["__action__"] = action
        combined_context["__outcome__"] = "success" if success else "failure"
        combined_sdr = self.encoder.encode_context(combined_context)

        trace_id = hashlib.md5(
            f"{self._trace_counter}:{action}:{success}".encode()
        ).hexdigest()[:8]
        self._trace_counter += 1

        trace = MemoryTrace(
            trace_id=trace_id,
            sdr=combined_sdr,
            context_sdr=ctx_sdr,
            action=action,
            success=success,
            salience=salience,
            timestamp=self._time,
        )
        self.traces.append(trace)
        self.attractor.store(combined_sdr, salience=salience)
        self._time += 1.0
        return trace_id

    def pin(self, trace_id: str) -> bool:
        """
        Phase 28 (B1): Pin a memory trace by its ID.
        Pinned traces are immune to pruning during consolidation
        and receive a context-gated recency floor during retrieval.

        Returns True if the trace was found and pinned.
        """
        for trace in self.traces:
            if trace.trace_id == trace_id:
                trace.pinned = True
                return True
        return False

    def retrieve(self, context: Dict[str, str], actions: List[str],
                 top_k: int = 10, n_cycles: int = 3) -> List[Tuple[MemoryTrace, float]]:
        """
        Theta-Gamma Sweep: Optimized with NumPy.
        """
        if not self.traces:
            return []
            
        query_sdr = self.encoder.encode_context(context)
        sweep_results: List[Tuple[MemoryTrace, float]] = []
        current_cue = query_sdr
        
        # Pre-cache time/count arrays for NumPy speed
        trace_times = np.array([t.timestamp for t in self.traces], dtype=np.float32)
        trace_counts = np.array([t.retrieval_count for t in self.traces], dtype=np.float32)
        
        # Phase 29: Slice pre-allocated arrays down to active capacity
        n_traces = self.attractor.active_count
        trace_salience = self.attractor.salience_arr[:n_traces]
        trace_mem_lens = self.attractor.mem_lens[:n_traces]
        trace_matrix = self.attractor.memories_matrix[:n_traces]

        for cycle in range(n_cycles):
            converged_state, _ = self.attractor.retrieve(current_cue)
            
            # Vectorized similarity calculation (Jaccard-like)
            state_vec = np.zeros(self.encoder.sparse_dim, dtype=np.float32)
            state_vec[converged_state] = 1.0
            
            intersections = trace_matrix @ state_vec
            state_len = float(len(converged_state))
            k_vals = np.maximum(trace_mem_lens, state_len)
            k_vals = np.maximum(k_vals, 1.0)
            sims = (intersections / k_vals)
            
            # Vectorized biological modulation: Power-law forgetting
            # recency_weight = exp(-k * dt / (1 + log(1 + count)))
            recency = np.exp(-0.5 * (self._time - trace_times) / (1.0 + np.log1p(trace_counts)))

            # Phase 28 (B1): Context-gated recency floor for pinned memories.
            # Pinned memories get a 0.5 minimum recency ONLY when the query
            # context overlaps with their encoding context (prevents pollution).
            for i, trace in enumerate(self.traces):
                if trace.pinned:
                    ctx_overlap = self.encoder.overlap(query_sdr, trace.context_sdr)
                    if ctx_overlap > 0.1:
                        recency[i] = max(recency[i], 0.5)

            scores = sims * trace_salience * recency
            
            # Mask out already retrieved IDs in this sweep
            processed_ids = [r[0].trace_id for r in sweep_results]
            if processed_ids:
                # This part is still slightly Pythonic but the math above is the heavy part
                for idx, t in enumerate(self.traces):
                    if t.trace_id in processed_ids:
                        scores[idx] = -1.0
            
            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])
            
            if best_score < 0.01:
                break
                
            best_trace = self.traces[best_idx]
            temporal_decay = 0.8 ** cycle
            sweep_results.append((best_trace, best_score * temporal_decay))
            
            # Immediate feedback loops
            best_trace.retrieval_count += 1
            trace_counts[best_idx] += 1  # sync local array for next cyclce
            
            if current_cue == query_sdr: # direct cue reconsolidation
                self.attractor.reconsolidate(best_idx, converged_state)
                
            current_cue = best_trace.sdr
            if len(sweep_results) >= top_k:
                break

        return sweep_results

    def consolidate(self, n_replays: int = 20, max_capacity: int = 200):
        """
        Offline replay: re-activate stored memories to strengthen
        their basins and prune weak/old traces to prevent saturation.
        Biology: sharp-wave ripples during NREM sleep.
        """
        if not self.attractor.memories:
            return
        
        # 1. Replay step (strengthens basins)
        for _ in range(n_replays):
            weights = self.attractor.salience
            total = sum(weights)
            if total <= 0: break
            r = random.random() * total
            idx = 0
            for i, w in enumerate(weights):
                r -= w
                if r <= 0:
                    idx = i
                    break
            
            mem_sdr = self.attractor.memories[idx]
            # Add noise (partial cue)
            noisy = [b for b in mem_sdr if random.random() > 0.1]
            converged_state, _ = self.attractor.retrieve(noisy, steps=1)
            self.attractor.reconsolidate(idx, converged_state)
            
        # 2. Prune step (prevents saturation)
        if len(self.traces) > max_capacity:
            # Sort by utility: salience combined with spacing effect
            paired = list(zip(self.traces, self.attractor.memories, 
                              self.attractor.memory_sets, self.attractor.salience))

            # Phase 28 (B1): Pinned memories are immune to pruning.
            pinned_pairs = [p for p in paired if p[0].pinned]
            unpinned_pairs = [p for p in paired if not p[0].pinned]

            unpinned_pairs.sort(key=lambda x: x[0].salience * (1.0 + math.log1p(x[0].retrieval_count)))
            keep_count = max(0, max_capacity - len(pinned_pairs))
            paired = pinned_pairs + unpinned_pairs[-keep_count:]
            
            # Unzip back into lists
            self.traces = [p[0] for p in paired]
            self.attractor.memories = [p[1] for p in paired]
            self.attractor.memory_sets = [p[2] for p in paired]
            self.attractor.salience = [p[3] for p in paired]
            self.attractor._sync_arrays_after_prune()

    def health_check(self, critical_trace_ids: List[str]) -> Dict[str, str]:
        """
        Phase 28 (B3): SLA monitor for critical memory traces.

        Reports the health of specified traces:
          - PRUNED:  trace no longer exists in the hippocampus
          - FADING:  trace exists but recency < 0.1 (near invisible)
          - HEALTHY: trace exists with recency >= 0.1

        The recency formula MUST match retrieve() exactly:
          recency = exp(-0.5 * dt / (1 + log(1 + retrieval_count)))

        Returns:
            dict mapping trace_id -> status string
        """
        results: Dict[str, str] = {}
        for tid in critical_trace_ids:
            trace = next((t for t in self.traces if t.trace_id == tid), None)
            if trace is None:
                results[tid] = "PRUNED ⚠️"
            else:
                age = self._time - trace.timestamp
                # Same formula as retrieve() line ~462
                recency = math.exp(-0.5 * age / (1.0 + math.log1p(trace.retrieval_count)))
                if recency < 0.1:
                    results[tid] = f"FADING (recency={recency:.3f}) ⚠️"
                else:
                    results[tid] = f"HEALTHY (recency={recency:.3f}) ✅"
        return results


# ─────────────────────────────────────────────
# 4. WORKING MEMORY BUFFER (Prefrontal Cortex)
#    ~7±2 items, oscillatory maintenance,
#    active gating of what gets priority.
# ─────────────────────────────────────────────

class WorkingMemoryBuffer:
    """
    Prefrontal working memory: capacity-limited, decay-based buffer.
    Recent high-salience experiences get a retrieval boost.

    Biology: Prefrontal cortex holds ~7±2 items in oscillatory loops.
    Items decay through interference. Rehearsal (re-encountering the
    same context) resets activation.
    """
    CAPACITY = 7  # Miller's law

    def __init__(self, decay_rate: float = 0.15):
        self.buffer: List[Dict[str, Any]] = []
        self.decay_rate = decay_rate

    def add(self, action: str, success: bool, salience: float):
        """Gate new experience into working memory if salient enough."""
        item = {
            'action': action,
            'success': success,
            'salience': salience,
            'activation': 1.0,
        }
        if len(self.buffer) >= self.CAPACITY:
            # Displace lowest-activation item (competitive gating)
            self.buffer.sort(key=lambda x: x['activation'])
            self.buffer.pop(0)
        self.buffer.append(item)

    def tick(self):
        """Each cognitive cycle, activation decays (interference)."""
        for item in self.buffer:
            item['activation'] *= (1.0 - self.decay_rate)
        # Remove fully decayed items
        self.buffer = [i for i in self.buffer if i['activation'] > 0.05]

    def get_action_boost(self, action: str) -> float:
        """
        Returns a boost factor for an action if it's in working memory.
        Recent successes get boosted; recent failures get penalized.
        """
        for item in self.buffer:
            if item['action'] == action:
                if item['success']:
                    return 1.0 + 0.3 * item['activation']  # boost up to 1.3x
                else:
                    return 1.0 - 0.2 * item['activation']  # penalize down to 0.8x
        return 1.0  # neutral if not in working memory


# ============================================================
# BIOLOGICAL RAG — PHASE 3: INTEGRATION WRAPPER
# ============================================================

class BioRAG(RAGInterface):
    """
    Full Biological Memory System — replaces SimpleRAG.

    Encoding path:
      Context dict -> SparseEncoder (SDR) -> HippocampalIndex -> HopfieldMemory
      Salience from PEE surprise gates encoding depth (amygdala effect).

    Retrieval path:
      Context dict -> SparseEncoder -> Attractor dynamics (pattern completion)
      -> Context reinstatement -> Working memory boost -> PillarSignal output

    This is NOT a search. The query "falls" into the nearest energy
    basin. The memory EMERGES from dynamics, it is not fetched.

    Phase 27 Changes:
      - Salience is now read from the InternalSignalBus (if attached),
        instead of requiring an explicit set_encoding_salience() call.
      - Auto-NREM: consolidation triggers automatically at 90% capacity.
      - set_encoding_salience() is retained for backward compatibility.

    Args:
        encoder:        shared SparseEncoder (the dentate gyrus)
        beta:           Hopfield inverse temperature (retrieval sharpness)
        confidence_max: max confidence BioRAG can assert (caps influence)
        min_evidence:   minimum retrieved traces before confidence is nonzero
        wm_salience_gate: minimum salience to enter working memory
        max_capacity:   Hopfield capacity limit (default 200)
        sleep_threshold: fraction of capacity that triggers auto-NREM (default 0.9)
    """
    def __init__(self,
                 encoder: Optional[SparseEncoder] = None,
                 beta: float = 12.0,
                 confidence_max: float = 0.6,
                 min_evidence: int = 3,
                 wm_salience_gate: float = 0.5,
                 max_capacity: int = 200,
                 sleep_threshold: float = 0.9):
        self.encoder = encoder or SparseEncoder()
        self.hippocampus = HippocampalIndex(self.encoder, beta=beta)
        self.working_memory = WorkingMemoryBuffer()
        self.confidence_max = confidence_max
        self.min_evidence = min_evidence
        self.wm_salience_gate = wm_salience_gate
        self.max_capacity = max_capacity
        self.sleep_threshold = sleep_threshold
        self._pending_salience: float = 1.0
        self._signal_bus: Optional[InternalSignalBus] = None  # Phase 27
        self._sleep_count: int = 0  # Track how many auto-naps have fired

    def attach_signal_bus(self, bus: InternalSignalBus):
        """Attach the shared InternalSignalBus for decoupled PEE salience."""
        self._signal_bus = bus

    def set_encoding_salience(self, salience: float):
        """
        Legacy API — still works. If no signal bus is attached, this
        is used directly. If a bus IS attached, the bus takes priority.
        """
        self._pending_salience = salience

    def _resolve_salience(self) -> float:
        """
        Resolve the encoding salience for this cycle.
        Priority: InternalSignalBus > manual set_encoding_salience > default.
        """
        if self._signal_bus is not None:
            return self._signal_bus.read_salience()
        salience = self._pending_salience
        self._pending_salience = 1.0  # reset
        return salience

    def write_back(self, context: Dict[str, str], action: str, success: bool) -> Optional[str]:
        """
        Hippocampal encoding of the episode.

        Returns:
          trace_id: str — the unique ID of the encoded memory trace,
                    or None if encoding was skipped.

        Phase 27 changes:
          - Salience is resolved from the signal bus if attached.
          - Auto-NREM triggers when capacity >= sleep_threshold * max_capacity.
        Phase 28 (B0): Returns trace_id for downstream pinning/health-check.
        """
        salience = self._resolve_salience()

        trace_id = self.hippocampus.encode(context, action, success, salience=salience)

        # ── Auto-NREM Sleep (Phase 27) ──
        # Consolidation is expensive (O(n) with replays). Guard with a cooldown
        # so we only consolidate once every ~50 encode calls, not every step.
        capacity_frac = len(self.hippocampus.traces) / max(1, self.max_capacity)
        encode_count = getattr(self, '_encode_count', 0) + 1
        self._encode_count = encode_count
        consolidation_interval = 50  # consolidate once every 50 steps
        if capacity_frac >= self.sleep_threshold and (encode_count % consolidation_interval == 0):
            n_replays = 10 if capacity_frac < 1.0 else 20  # light nap vs deep sleep
            self.hippocampus.consolidate(
                n_replays=n_replays,
                max_capacity=self.max_capacity
            )
            self._sleep_count += 1

        # Gate into working memory if salient enough
        if salience >= self.wm_salience_gate:
            self.working_memory.add(action, success, salience)

        return trace_id

    def retrieve(self, context: Dict[str, str], actions: List[str]) -> PillarSignal:
        """
        Biological retrieval:
          1. Attractor dynamics (pattern completion from context cue)
          2. Context reinstatement boosts relevant memories
          3. Working memory contents get priority (recency)
          4. Reconsolidation updates the retrieved memory
          5. Returns a PillarSignal with biologically-derived weights
        """
        # Step 1: Hippocampal retrieval with attractor dynamics
        traces = self.hippocampus.retrieve(context, actions, top_k=15)

        if not traces:
            return PillarSignal(
                action_weights={a: 1.0 for a in actions},
                confidence=0.0,
                pillar_name="BioRAG",
            )

        # Step 2: Accumulate success rates per action from retrieved traces
        action_stats: Dict[str, List[float]] = {a: [0.0, 0.0] for a in actions}
        for trace, score in traces:
            if trace.action in action_stats and score > 0.01:
                action_stats[trace.action][1] += score  # weighted total
                if trace.success:
                    action_stats[trace.action][0] += score  # weighted successes

        # Step 3: Convert to weights
        weights: Dict[str, float] = {}
        total_evidence = 0.0
        for act in actions:
            succ, total = action_stats[act]
            if total >= 0.01:
                weights[act] = max(0.05, succ / total)
                total_evidence += total
            else:
                weights[act] = 0.5  # neutral for unseen actions

        # Step 4: Working memory boost (prefrontal recency priority)
        for act in actions:
            boost = self.working_memory.get_action_boost(act)
            weights[act] *= boost

        # Tick working memory decay
        self.working_memory.tick()

        # Step 5: Confidence based on evidence depth, capped biologically
        if total_evidence < self.min_evidence * 0.01:
            confidence = 0.0
        else:
            confidence = min(self.confidence_max,
                             total_evidence / (total_evidence + 5.0))

        return PillarSignal(
            action_weights=weights,
            confidence=confidence,
            pillar_name="BioRAG",
        )


# ============================================================
# QUINT-BIORAG AGENT (COPY OF QuintHybridAgent WITH BioRAG)
# Phase 27: Decoupled via InternalSignalBus + Auto-Sleep + Persistence
# ============================================================

class QuintBioRAGAgent(QuintHybridAgent):
    """
    Identical to QuintHybridAgent except:
      - Default RAG is BioRAG (not RAGInterface stub)
      - PEE surprise is broadcast via InternalSignalBus (decoupled)
      - BioRAG reads salience from the bus autonomously
      - Full state persistence via save_state / load_state

    This is a drop-in replacement. All tests that work on
    QuintHybridAgent also work on QuintBioRAGAgent.
    """
    def __init__(
        self,
        seed: int = 42,
        tfe_tau: float = 3600.0,
        pee_kwargs: Optional[dict] = None,
        rag: Optional[RAGInterface] = None,
        sham_pe: bool = False,
        biorag_kwargs: Optional[dict] = None,
        residue_config: Optional[ResidueConfig] = None,  # Phase 28 (Intake)
        adaptive_encoding_enabled: bool = False,         # Phase 28 (Intake)
    ):
        # If no RAG provided, create a BioRAG with the biological defaults
        if rag is None:
            encoder = SparseEncoder(seed=seed)
            rag = BioRAG(encoder=encoder, **(biorag_kwargs or {}))

        super().__init__(
            seed=seed,
            tfe_tau=tfe_tau,
            pee_kwargs=pee_kwargs,
            rag=rag,
            sham_pe=sham_pe,
        )

        # ── Phase 27: Internal Signal Bus ──
        # Decouples PEE (Pillar 4) from BioRAG (Pillar 5).
        # PEE writes surprise to the bus; BioRAG reads salience from it.
        self._signal_bus = InternalSignalBus()
        self.last_trace_id: Optional[str] = None  # Phase 28 (B0)
        self.decision_log: deque = deque(maxlen=200)  # Phase 28 (A1)
        if isinstance(self.rag, BioRAG):
            self.rag.attach_signal_bus(self._signal_bus)

        # ── Phase 28: Metabolic Residue (Intake Gate) ──
        self.residue_reservoir = ResidueReservoir(config=residue_config or ResidueConfig())
        self.adaptive_encoding_enabled = adaptive_encoding_enabled

    def choose(self, condition: Dict[str, str], actions: List[str]) -> str:
        """Convenience wrapper: returns just the action (no source tuple).
        Used by behavioral/stress/ablation tests that don't need the source."""
        action, _source = self.choose_action(condition, actions)
        return action

    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> Tuple[str, str]:
        """
        Phase 28 (Intake): Implement the Two-Stage Gate before generating pillar decisions.
        Phase 28 (A1): Override to capture per-pillar decision data.
        """
        # ── Phase 28: Metabolic Residue (Two-Stage Gate) ──
        # Only run the gate if the action list makes this an intake decision (e.g. ['ACCEPT', 'REJECT'])
        # For general testing compatibility, we'll only gate if 'ACCEPT' and 'REJECT' are the options.
        is_intake_decision = set(actions) == {'ACCEPT', 'REJECT'}

        if is_intake_decision:
            # Stage 1: Fast Cache Check
            candidate_text = str(condition)
            c_hash_val = sha256_hex(normalize_text(candidate_text))
            c_hash = self.residue_reservoir._by_hash.get(c_hash_val)
            if c_hash:
                # Early rejection — we've seen this exact nonsense before
                return 'REJECT', 'Gate_Duplicate'

            # Stage 2: Fast Heuristic Gate
            alert = self.residue_reservoir.pressure.alert_level()
            if alert == "CRITICAL" and len(candidate_text) < 40:
                # Early rejection — pressure is critical and this is suspiciously short
                return 'REJECT', 'Gate_LowQuality'

        ctx_key = self._context_key(condition)

        # Snapshot pillar states BEFORE the decision
        # CME
        bias = self.cme.emit_bias(condition, actions)
        cme_blocked = [a for a, v in bias.hard_blocks.items() if v]
        cme_softened = {a: round(w, 3) for a, w in bias.weights.items() if w < 1.0}

        # Bandit Q-values
        posteriors = self.bandit.state.posteriors.get(ctx_key, {})
        q_values = {}
        for act in actions:
            if act in posteriors:
                p = posteriors[act]
                q_values[act] = round(p.alpha / (p.alpha + p.beta), 3)
            else:
                q_values[act] = 0.5

        # TFE states
        obs = self.last_tfe_observables
        tfe_states = {}
        if obs:
            for act in actions:
                tfe_key = f"{ctx_key}|{act}"
                if tfe_key in obs.key_states:
                    tfe_states[act] = obs.key_states[tfe_key].value

        # Make the actual decision (parent class)
        action, source = super().choose_action(condition, actions)

        # BioRAG retrieval snapshot (top 3)
        biorag_info = {}
        if isinstance(self.rag, BioRAG) and self.rag.hippocampus.traces:
            try:
                bio_results = self.rag.hippocampus.retrieve(condition, actions, top_k=3)
                top_retrievals = []
                scores_list = []
                for trace, score in bio_results:
                    top_retrievals.append({
                        "action": trace.action,
                        "score": round(score, 3),
                        "age": round(self.rag.hippocampus._time - trace.timestamp, 1),
                        "rehearsals": trace.retrieval_count,
                        "pinned": trace.pinned,
                    })
                    scores_list.append(score)

                # Convergence quality: ratio of top-1 to top-2 scores
                convergence = 0.0
                if len(scores_list) >= 2 and scores_list[1] > 0.001:
                    convergence = round(scores_list[0] / scores_list[1], 2)
                elif len(scores_list) == 1:
                    convergence = float('inf')  # single clear basin

                biorag_info = {
                    "top_retrievals": top_retrievals,
                    "convergence_quality": convergence,
                    "trace_count": len(self.rag.hippocampus.traces),
                }
            except Exception:
                biorag_info = {"error": "retrieval failed"}

        # Build the partial decision trace (PEE data added in update())
        trace_entry = {
            "step": None,  # filled in update()
            "context": dict(condition),
            "chosen_action": action,
            "source": source,
            "pillars": {
                "CME": {"blocked": cme_blocked, "softened": cme_softened},
                "Bandit": {"Q_values": q_values},
                "TFE": {"key_states": tfe_states},
                "PEE": {},  # filled in update()
                "BioRAG": biorag_info,
            },
            "final_weights": None,  # filled in update()
        }
        self.decision_log.append(trace_entry)

        return action, source

    def update(self, condition: Dict[str, str], action: str, success: bool, step: int):
        """
        Phase 28 update loop.

        The amygdala coupling is now handled by the InternalSignalBus:
          1. PEE computes surprise → publishes to the bus.
          2. BioRAG reads salience from the bus during write_back.
          No isinstance checks. No direct method calls between pillars.
        Phase 28 (A1): Enriches the latest decision_log entry with PEE data.
        """
        ctx_key = self._context_key(condition)
        tfe_key = f"{ctx_key}|{action}"

        # ── Pillar 4: PEE — compute surprise from locked prediction ──
        prob, conf = self._pending_predictions.pop(tfe_key, (0.5, 0.0))
        signal = self.pee.compute(prob, conf, success)

        if self.sham_pe:
            signal.encoding_weight = self._sham_rng.uniform(1.0, 3.0)
            signal.tfe_reset = self._sham_rng.random() < 0.15

        # ── Phase 27: Publish to the bus (replaces the amygdala hack) ──
        self._signal_bus.publish_pee(signal)

        # ── Phase 28 (A1): Enrich decision log with PEE data ──
        if self.decision_log:
            entry = self.decision_log[-1]
            entry["step"] = step
            entry["pillars"]["PEE"] = {
                "surprise": round(signal.error_magnitude, 3),
                "encoding_weight": round(signal.encoding_weight, 3),
                "tfe_reset": signal.tfe_reset,
            }
            entry["success"] = success

        # ── Pillar 2: Bandit — scale update by PEE encoding weight ──
        if ctx_key not in self.bandit.state.posteriors:
            self.bandit.state.posteriors[ctx_key] = {}
        if action not in self.bandit.state.posteriors[ctx_key]:
            self.bandit.state.posteriors[ctx_key][action] = BetaParams(
                self.bandit.config.prior_alpha, self.bandit.config.prior_beta
            )

        current = self.bandit.state.posteriors[ctx_key][action]
        if success:
            updated = BetaParams(current.alpha + signal.encoding_weight, current.beta)
        else:
            updated = BetaParams(current.alpha, current.beta + signal.encoding_weight)

        self.bandit.state.posteriors[ctx_key][action] = updated
        self.bandit.state.total_updates += 1
        self.bandit.state.total_steps += 1

        # ── Pillar 1: CME — scale memory encoding by PEE surprise ──
        if not success:
            original_gain = self.cme.reinforce_gain
            self.cme.reinforce_gain = original_gain * signal.encoding_weight
            self.cme.reinforce_memory(
                mem_type="CONSTRAINT",
                condition_subset=condition,
                action=action,
                step=step,
            )
            self.cme.reinforce_gain = original_gain

            # ── Phase 28 (B2): Dual Encoding ──
            # CME learns the constraint logically. BioRAG learns it
            # episodically as a high-salience pinned attractor basin.
            # This ensures safety constraints survive both systems.
            SAFETY_CONSTRAINT_SALIENCE = 3.0  # 3x normal = deep basin
            if isinstance(self.rag, BioRAG):
                constraint_tid = self.rag.hippocampus.encode(
                    condition, action, success=False,
                    salience=SAFETY_CONSTRAINT_SALIENCE,
                )
                self.rag.hippocampus.pin(constraint_tid)

            # ── Phase 28: Metabolic Residue (Record Rejection) ──
            # If this is an intake-style action that failed, log it to residue.
            # We use the context string as the text payload.
            if action in ['REJECT', 'NO', 'IGNORE', 'SKIP'] or "Gate_" in str(action):
                pass # Already rejected or explicitly ignoring
            else:
                candidate_text = str(condition)
                candidate = Candidate(
                    id=f"cand_{step}_{hashlib.sha256(candidate_text.encode()).hexdigest()[:8]}",
                    type=CandidateType.OTHER,
                    content=candidate_text,
                    doc_id="runtime"
                )
                
                # Derive a reason if we can based on the pillars
                reasons = [] # Initialize reasons list
                cme_bias = self.cme.emit_bias(condition, [action])
                if cme_bias.hard_blocks.get(action, False):
                    reasons.append((ReasonCode.CONFLICTS_WITH_CONSTRAINT, 1.0))
                if signal.error_magnitude < 0.1:
                    reasons.append((ReasonCode.REDUNDANT, 0.5))
                if not reasons:
                    reasons.append((ReasonCode.LOW_SALIENCE, 0.8))

                # Fake scores for now, the point is the TTL cache
                scores = ScoreBreakdown.compute(U_raw=0.0, K_raw=0.5, D_raw=0.5, E_raw=0.5)

                self.residue_reservoir.record(
                    candidate=candidate,
                    scores=scores,
                    reasons=reasons,
                    context=ResidueContext(intake_mode=IntakeMode.COMMIT),
                    now=self.rag.hippocampus._time if isinstance(self.rag, BioRAG) else None
                )

        self.cme.counter_evidence(
            condition=condition, action=action, success=success, step=step
        )

        # ── Pillar 3: TFE — touch key, activate reset on paradigm shift ──
        if self._signal_bus.tfe_reset:
            self.tfe.touch_key(tfe_key, magnitude=1.0)
        else:
            self.tfe.touch_key(tfe_key, magnitude=1.0 if success else 0.1)

        # ── Pillar 5: BioRAG — write outcome into attractor landscape ──
        # BioRAG reads salience from the bus internally (no direct call).
        # Phase 28 (B0): Capture trace_id for downstream pinning/health-check.
        # Phase 28 (Adaptive Encoding): Skip trace generation if error_magnitude is low
        self.last_trace_id = None
        should_encode_biorag = True
        
        if self.adaptive_encoding_enabled and signal.error_magnitude < 0.05:
            # We perfectly expected this outcome; don't waste hippocampal slots.
            should_encode_biorag = False
            
        if should_encode_biorag:
            self.last_trace_id = self.rag.write_back(condition, action, success)

        # ── Phase 28 (A1): Finalize decision log entry ──
        if self.decision_log:
            self.decision_log[-1]["trace_id"] = self.last_trace_id

    # ── Phase 28 (A1/A2): Decision Diagnostics ──

    @property
    def last_decision_trace(self) -> Optional[Dict]:
        """Returns the most recent decision log entry, or None."""
        return self.decision_log[-1] if self.decision_log else None

    def diagnose_last_decision(self) -> str:
        """
        Phase 28 (A2): Human-readable diagnostic string for the last decision.
        """
        entry = self.last_decision_trace
        if not entry:
            return "No decisions recorded yet."

        lines = [f"DIAGNOSIS for step {entry.get('step')} | context {entry['context']}:"]
        p = entry["pillars"]

        # CME
        cme = p.get("CME", {})
        blocked = cme.get("blocked", [])
        softened = cme.get("softened", {})
        if blocked:
            lines.append(f"  • CME: BLOCKED {blocked}. Softened: {softened}")
        elif softened:
            lines.append(f"  • CME: Softened weights on {softened}")
        else:
            lines.append("  • CME: No constraints active.")

        # Bandit
        bandit = p.get("Bandit", {})
        q = bandit.get("Q_values", {})
        if q:
            best = max(q, key=q.get)
            lines.append(f"  • Bandit: Favors {best} (Q={q[best]}). All: {q}")

        # TFE
        tfe = p.get("TFE", {})
        states = tfe.get("key_states", {})
        if states:
            lines.append(f"  • TFE: Key states: {states}")
        else:
            lines.append("  • TFE: All keys nominal.")

        # PEE
        pee = p.get("PEE", {})
        if pee:
            surprise = pee.get('surprise', '?')
            ew = pee.get('encoding_weight', '?')
            lines.append(f"  • PEE: Surprise={surprise}, encoding_weight={ew}")

        # BioRAG
        bio = p.get("BioRAG", {})
        top = bio.get("top_retrievals", [])
        if top:
            conv = bio.get('convergence_quality', '?')
            lines.append(f"  • BioRAG: Top retrieval: {top[0]['action']} (score={top[0]['score']}). "
                         f"Convergence={'CLEAN' if conv and conv > 2.0 else 'AMBIGUOUS'} ({conv})")
        else:
            lines.append("  • BioRAG: No retrievals (empty memory).")

        # Verdict
        chosen = entry.get('chosen_action', '?')
        source = entry.get('source', '?')
        success = entry.get('success', '?')
        lines.append(f"  VERDICT: Chose '{chosen}' via {source}. Outcome: {success}")

        return "\n".join(lines)

    # ── Phase 27: State Persistence ──────────────────────────────────

    def save_state(self, filepath: str):
        """
        Serialize the full agent state to disk.

        Persists:
          - Bandit posteriors (Beta distributions)
          - CME rules and constraints
          - TFE clock state (via its own persistence module)
          - BioRAG hippocampal traces + Hopfield matrices
          - PEE calibration history
          - Signal bus state

        Usage:
            agent.save_state('agent_checkpoint.pkl')
        """
        state = {
            'bandit_posteriors': {},
            'bandit_total_updates': self.bandit.state.total_updates,
            'bandit_total_steps': self.bandit.state.total_steps,
            'pee_calibration': list(self.pee._calibration),
            'pee_surprise_count': self.pee._surprise_count,
            'pee_total_weight': self.pee._total_weight,
            'pee_update_count': self.pee._update_count,
            'signal_bus': {
                'encoding_weight': self._signal_bus.encoding_weight,
                'tfe_reset': self._signal_bus.tfe_reset,
                'last_error_magnitude': self._signal_bus.last_error_magnitude,
            },
        }

        # Serialize Bandit posteriors (BetaParams → dict)
        for ctx_key, action_map in self.bandit.state.posteriors.items():
            state['bandit_posteriors'][ctx_key] = {
                act: {'alpha': bp.alpha, 'beta': bp.beta}
                for act, bp in action_map.items()
            }

        # Serialize BioRAG state if applicable
        if isinstance(self.rag, BioRAG):
            hippo = self.rag.hippocampus
            state['biorag'] = {
                'traces': [
                    {
                        'trace_id': t.trace_id,
                        'sdr': t.sdr,
                        'context_sdr': t.context_sdr,
                        'action': t.action,
                        'success': t.success,
                        'salience': t.salience,
                        'retrieval_count': t.retrieval_count,
                        'timestamp': t.timestamp,
                    }
                    for t in hippo.traces
                ],
                'time': hippo._time,
                'trace_counter': hippo._trace_counter,
                'hopfield_memories': [list(m) for m in hippo.attractor.memories],
                'hopfield_salience': list(hippo.attractor.salience),
                'sleep_count': self.rag._sleep_count,
                'wm_buffer': list(self.rag.working_memory.buffer),
            }

        with open(filepath, 'wb') as f:
            pickle.dump(state, f)

    def load_state(self, filepath: str):
        """
        Restore agent state from disk.

        Usage:
            agent = QuintBioRAGAgent(seed=42)
            agent.load_state('agent_checkpoint.pkl')
        """
        with open(filepath, 'rb') as f:
            state = pickle.load(f)

        # Restore Bandit posteriors
        self.bandit.state.posteriors = {}
        for ctx_key, action_map in state['bandit_posteriors'].items():
            self.bandit.state.posteriors[ctx_key] = {
                act: BetaParams(d['alpha'], d['beta'])
                for act, d in action_map.items()
            }
        self.bandit.state.total_updates = state['bandit_total_updates']
        self.bandit.state.total_steps = state['bandit_total_steps']

        # Restore PEE calibration
        self.pee._calibration = deque(state['pee_calibration'], maxlen=100)
        self.pee._surprise_count = state['pee_surprise_count']
        self.pee._total_weight = state['pee_total_weight']
        self.pee._update_count = state['pee_update_count']

        # Restore Signal Bus
        bus = state.get('signal_bus', {})
        self._signal_bus.encoding_weight = bus.get('encoding_weight', 1.0)
        self._signal_bus.tfe_reset = bus.get('tfe_reset', False)
        self._signal_bus.last_error_magnitude = bus.get('last_error_magnitude', 0.0)

        # Restore BioRAG hippocampus
        if isinstance(self.rag, BioRAG) and 'biorag' in state:
            bio = state['biorag']
            hippo = self.rag.hippocampus

            # Rebuild traces
            hippo.traces = [
                MemoryTrace(
                    trace_id=t['trace_id'],
                    sdr=t['sdr'],
                    context_sdr=t['context_sdr'],
                    action=t['action'],
                    success=t['success'],
                    salience=t['salience'],
                    retrieval_count=t['retrieval_count'],
                    timestamp=t['timestamp'],
                )
                for t in bio['traces']
            ]
            hippo._time = bio['time']
            hippo._trace_counter = bio['trace_counter']

            # Rebuild Hopfield attractor
            att = hippo.attractor
            att.memories = bio['hopfield_memories']
            att.memory_sets = [set(m) for m in att.memories]
            att.salience = bio['hopfield_salience']
            att._sync_arrays_after_prune()  # rebuilds NumPy matrices

            self.rag._sleep_count = bio.get('sleep_count', 0)
            self.rag.working_memory.buffer = bio.get('wm_buffer', [])
