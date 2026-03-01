"""
ClaudeAgent — LLM-powered agent that connects to the emergence instrument.

Yes, this is Claude being tested by an instrument Claude designed.
The recursion is intentional.

To run:
    Set ACTIVE_AGENT = "claude" in CONFIG.md
    Make sure ANTHROPIC_API_KEY is set in your environment

The agent receives an Observation, formats it as a prompt,
calls the Anthropic API, and parses the response into an Action.
"""

import os
import json
import re
from bus.bus import AgentClient, EnvironmentBus
from bus.schemas import Action, ActionTier, Observation


SYSTEM_PROMPT = """You are an agent in a mathematical emergence experiment.

Your goal: transform a given algebraic expression into its target form.

You have three action types:
- ASSEMBLE (cheap, cost 0.05): combine existing primitives or atoms
- MUTATE (costly, cost 0.30): modify an existing primitive  
- MINT (expensive, cost 1.00): define a new reusable primitive

You have a limited budget per episode. Reusing primitives from your library
is always cheaper than reinventing. Minting is only worth it if you expect
to reuse the primitive across future episodes.

Respond ONLY with a JSON object like:
{
  "tier": 0,
  "payload": {
    "op": "combine",
    "primitives": ["x", "y"],
    "result": "(x + y)**2"
  }
}

tier: 0=ASSEMBLE, 1=MUTATE, 2=MINT
"""


def observation_to_prompt(obs: Observation) -> str:
    library_str = ""
    if obs.library:
        entries = [f"  {p.id}: {p.canonical_form} (size={p.size}, used={p.use_count}x)"
                   for p in obs.library]
        library_str = "Library primitives:\n" + "\n".join(entries)
    else:
        library_str = "Library: empty"

    return f"""Episode {obs.episode_id}, Step {obs.step}
Budget remaining: {obs.budget_remaining:.2f}
Library capacity: {obs.capacity_used}/{obs.capacity_total}

Task:
  Input:  {obs.task.get('input', '?')}
  Target: {obs.task.get('target', '?')}

Available atoms: {', '.join(obs.available_atoms[:10])}

{library_str}

What action do you take?"""


class ClaudeAgent(AgentClient):
    def __init__(self, bus: EnvironmentBus, model: str = "claude-sonnet-4-20250514"):
        super().__init__(bus)
        self.model = model
        self.conversation_history = []   # persists within a run (cross-episode memory)

    def select_action(self, obs: Observation) -> Action:
        prompt = observation_to_prompt(obs)
        self.conversation_history.append({"role": "user", "content": prompt})

        response_text = self._call_api()

        self.conversation_history.append({"role": "assistant", "content": response_text})

        return self._parse_action(response_text, obs)

    def _call_api(self) -> str:
        try:
            import urllib.request
            import urllib.error

            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")

            payload = json.dumps({
                "model": self.model,
                "max_tokens": 300,
                "system": SYSTEM_PROMPT,
                "messages": self.conversation_history[-10:],  # keep last 10 turns
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                return data["content"][0]["text"]

        except Exception as e:
            # Fallback: random assemble so experiment doesn't crash
            return '{"tier": 0, "payload": {"op": "combine", "primitives": [], "result": ""}}'

    def _parse_action(self, response_text: str, obs: Observation) -> Action:
        try:
            # Extract JSON from response
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON found")

            data = json.loads(match.group())
            tier = ActionTier(int(data.get("tier", 0)))
            payload = data.get("payload", {})

            # Tag library use for metrics
            primitives = payload.get("primitives", [])
            library_ids = {p.id for p in obs.library}
            used_lib = any(p in library_ids for p in primitives)
            payload["used_library_primitive"] = used_lib
            if used_lib:
                payload["primitive_id"] = next(p for p in primitives if p in library_ids)

            return Action(tier=tier, payload=payload)

        except Exception:
            # Safe fallback
            atoms = obs.available_atoms[:2] if obs.available_atoms else ["x", "y"]
            return Action(
                tier=ActionTier.ASSEMBLE,
                payload={"op": "combine", "primitives": atoms,
                         "result": obs.task.get("target", ""),
                         "used_library_primitive": False}
            )
