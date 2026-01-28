
import React, { useState } from 'react';
import { Box, FileText, Sparkles, Terminal, Check, Info, BookOpen, Target, Activity, HelpCircle, ArrowLeftCircle } from 'lucide-react';

export interface Template {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  initialPrompt: string;
  headers: string[];
  category?: string;
  details: {
    what: string;
    how: string;
    why: string;
  };
}

export const TEMPLATES: Template[] = [
  {
    id: 'standard',
    name: 'Deductive Synthesis Protocol',
    description: 'Universal reasoning loop for general problem solving and deep analysis.',
    icon: <FileText className="text-blue-500" />,
    initialPrompt: "Initialize the Deductive Synthesis v0.8 schema. Focus on extracting GIVEN facts before any derivation.",
    headers: ['STEP:', 'A) PROBLEM', 'B) GIVEN', 'C) GOAL', 'D) WORKING STATE', 'E) STEP LOG', 'F) OPEN ITEMS', 'G) NEXT STEP REQUEST'],
    category: 'Reasoning',
    details: {
      what: "A recursive state-machine designed to stabilize LLM context by forcing a fact-first derivation loop.",
      how: "Applies a 'Working Memory' canvas that the model must update before proposing any final answer.",
      why: "Standard chat suffers from context drift; this protocol anchors the engine to explicit logical milestones."
    }
  },
  {
    id: 'math',
    name: 'Formal Axiomatic Verification',
    description: 'Strict symbolic logic for proofs, verification, and mathematical derivation.',
    icon: <Sparkles className="text-amber-500" />,
    initialPrompt: "Initialize a Formal Axiomatic structure. All inferences must refer to defined AXIOMS.",
    headers: ['STEP:', 'A) AXIOMS', 'B) THEOREMS', 'C) DERIVATION', 'D) QED PROGRESS'],
    category: 'Precision',
    details: {
      what: "A high-fidelity proof-engine that maps symbolic relations into a QED-ready hierarchy.",
      how: "Separates base axioms from derived theorems, requiring manual or automated verification of each link.",
      why: "Used for high-stakes precision where hallucination is prohibited by axiomatic constraints."
    }
  },
  {
    id: 'code',
    name: 'Blueprint Component Mapping',
    description: 'Architectural dependency mapping for systems and software engineering.',
    icon: <Terminal className="text-emerald-500" />,
    initialPrompt: "Initialize a System Architecture canvas. Map component hierarchies and data flow vectors.",
    headers: ['STEP:', 'A) REQUIREMENTS', 'B) COMPONENTS', 'C) DATA FLOW', 'D) SECURITY', 'E) IMPLEMENTATION'],
    category: 'Engineering',
    details: {
      what: "A structural dependency graph for visualizing complex technical inter-relationships.",
      how: "Utilizes directional logic pins to represent execution flow and data contract boundaries.",
      why: "Engineers need to see the 'big picture' without losing the granularity of implementation details."
    }
  },
  {
    id: 'creative',
    name: 'Neural Narrative Sandbox',
    description: 'Freeform logic canvas for creative strategy, world-building, and ideation.',
    icon: <Sparkles className="text-purple-500" />,
    initialPrompt: "Initialize a Creative Strategy sandbox. Focus on [PREMISE] and [THEMATIC LOGIC].",
    headers: ['STEP:', 'A) PREMISE', 'B) WORLD LOGIC', 'C) NARRATIVE VECTORS', 'D) CONFLICTS'],
    category: 'Ideation',
    details: {
      what: "A flexible conceptual workspace designed for high-entropy creative exploration.",
      how: "Maps abstract themes and narrative beats into a persistent logical continuity.",
      why: "Creative work requires broad context retention to ensure thematic consistency across long sessions."
    }
  }
];

interface TemplateSelectorProps {
  selectedId: string;
  onSelect: (template: Template) => void;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({ selectedId, onSelect }) => {
  const [flippedId, setFlippedId] = useState<string | null>(null);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {TEMPLATES.map((t) => {
        const isSelected = t.id === selectedId;
        const isFlipped = flippedId === t.id;

        return (
          <div key={t.id} className="relative h-64 perspective-1000">
            <div 
              className={`relative w-full h-full transition-all duration-700 preserve-3d ${isFlipped ? 'rotate-y-180' : ''}`}
            >
              <button
                onClick={() => onSelect(t)}
                className={`absolute inset-0 flex flex-col p-6 rounded-[2rem] border text-left backface-hidden transition-all duration-300 group ${
                  isSelected 
                    ? 'bg-blue-600/10 border-blue-500 shadow-xl shadow-blue-900/20' 
                    : 'bg-slate-900/40 border-slate-800/60 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-start justify-between mb-4 w-full">
                  <div className={`p-3 rounded-xl shadow-inner transition-transform group-hover:scale-110 duration-500 ${isSelected ? 'bg-blue-600/20' : 'bg-slate-950'}`}>
                    {t.icon}
                  </div>
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={(e) => { e.stopPropagation(); setFlippedId(t.id); }}
                      className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-500 hover:text-white transition-colors"
                      title="View Artifact Metadata"
                    >
                      <Info size={14} />
                    </button>
                    {isSelected && (
                      <div className="p-1.5 bg-blue-500 rounded-full animate-in zoom-in duration-300">
                        <Check size={10} className="text-white" />
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="mb-2">
                  <span className="text-[7px] font-black uppercase tracking-[0.4em] text-blue-500/60 mb-1 block">
                    Protocol: {t.category}
                  </span>
                  <h3 className={`text-base font-black italic tracking-tight transition-colors ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                    {t.name}
                  </h3>
                </div>
                
                <p className="text-[11px] leading-relaxed text-slate-500 group-hover:text-slate-400 transition-colors mt-2">
                  {t.description}
                </p>

                <div className="mt-auto flex items-center gap-4">
                   <div className="h-px flex-1 bg-white/5" />
                   <span className="text-[8px] font-black uppercase tracking-widest text-slate-700">Artifact Card {t.id.slice(0,3)}</span>
                </div>
              </button>

              <div 
                className="absolute inset-0 flex flex-col p-8 rounded-[2rem] border border-blue-500/40 bg-[#0f172a] rotate-y-180 backface-hidden shadow-2xl overflow-hidden"
              >
                <div className="absolute -top-10 -right-10 opacity-5">
                   <HelpCircle size={150} />
                </div>
                <div className="flex items-center justify-between mb-6">
                  <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-400 flex items-center gap-2">
                    <BookOpen size={14} /> Artifact Schema
                  </h4>
                  <button 
                    onClick={() => setFlippedId(null)}
                    className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 transition-colors"
                  >
                    <ArrowLeftCircle size={14} />
                  </button>
                </div>
                <div className="space-y-4 relative z-10">
                  <div className="space-y-1">
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">What is it?</span>
                    <p className="text-[10px] text-slate-300 leading-relaxed font-medium">{t.details.what}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Mechanism</span>
                    <p className="text-[10px] text-slate-300 leading-relaxed font-medium">{t.details.how}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Rationale</span>
                    <p className="text-[10px] text-slate-300 leading-relaxed font-medium">{t.details.why}</p>
                  </div>
                </div>
                <div className="mt-auto pt-4 border-t border-white/5 flex items-center justify-between">
                   <span className="text-[7px] font-mono text-slate-600">ID: {t.id.toUpperCase()}</span>
                   <span className="text-[7px] font-mono text-slate-600">VER: 0.8.0</span>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default TemplateSelector;
