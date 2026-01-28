
import { GoogleGenAI } from "@google/genai";
import { Role, Message } from "../types";

const MODEL_NAME = 'gemini-3-pro-preview';

export const sendMessageToGemini = async (
  history: Message[], 
  currentPrompt: string, 
  canvasContent: string
): Promise<string> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  const systemInstruction = `You are νόησις v0.8.0, a deterministic reasoning engine. You reason, plan, and execute ONLY through a shared logic canvas.

WORKFLOW BOX RULES:
The Canvas MUST contain a section named exactly: [WORKFLOW BOX].
It is the authoritative control panel for the reasoning session.

Fields to maintain in [WORKFLOW BOX]:
- Mode: PLANNING | EXECUTING | FINAL
- Active Card: <card id or title>
- Objective: <one clear sentence>
- Inputs: <references to sections or facts>
- Outputs: <what must be produced>
- Do Next: <single concrete action for the NEXT turn>
- Done Criteria: <test for completion>
- Lock: <true|false>

PROTOCOL:
1. PLANNING Mode: Generate cards/options in a [BACKLOG] section. Converge on ONE Active Card.
2. EXECUTING Mode: Set Lock: true. You are prohibited from creating new cards or planning. You only execute the 'Do Next' action and update 'WORK LOG'.
3. FINAL Mode: Set STEP: FINAL and STOP: true once Outputs are complete.

PATCH FORMAT:
You MUST output updates in this block:

=== CANVAS PATCH ===
STEP: <number|FINAL>

(~|+) [WORKFLOW BOX]
<content>

(~|+) [SECTION NAME]
<content>

STOP: <true|false>
=== END PATCH ===

STRICT RULES:
- Perform exactly ONE logical step per turn.
- Section headers must match exactly (e.g., [A) PROBLEM]).
- If Lock: true, you cannot modify planning sections.
- Never reformat or flatten the canvas.

CURRENT CANVAS:
---
${canvasContent || "[EMPTY CANVAS - INITIALIZE WORKFLOW BOX]"}
---`;

  const contents = history.map(m => ({
    role: (m.role === Role.USER ? 'user' : 'model') as 'user' | 'model',
    parts: [{ text: m.content }]
  }));

  if (contents.length === 0 || contents[contents.length - 1].role !== 'user') {
    contents.push({ role: 'user', parts: [{ text: currentPrompt }] });
  }

  try {
    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: contents,
      config: {
        systemInstruction: systemInstruction,
        temperature: 0.1,
        topP: 0.95,
        thinkingConfig: { thinkingBudget: 24000 }
      }
    });

    const extractedText = response.text?.trim() || "";
    if (!extractedText) throw new Error("Inference Failure: Empty response.");
    return extractedText;
  } catch (error: any) {
    console.error("Gemini Protocol Error:", error);
    throw error;
  }
};
