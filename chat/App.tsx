
import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { 
  Send, BrainCircuit, Layout, MessageSquare, FastForward, 
  RotateCcw, Copy, Check, Terminal, Cpu, History, X, 
  Eye, Flag, Square, Library, Sparkles, Box, FileText,
  Plus, AlertCircle, FileCode, List, ArrowLeftCircle,
  Pencil, Layers, Zap, Maximize2, PanelLeftOpen, PanelLeftClose,
  Save, ChevronRight, CloudUpload, Clock, Workflow,
  GitCommit, Activity, Target, Trash2, Info, Share2, Play,
  Download, Search, Filter, ZoomIn, ZoomOut, MousePointer2,
  GripHorizontal, PanelRightOpen, PanelRightClose,
  Network, Share, GitMerge, ListTree, BoxSelect,
  Database, ZapOff, ChevronDown, Anchor, Hexagon, ShieldAlert,
  Globe, Rocket, PlayCircle, Settings, HelpCircle, BookOpen,
  Code, HardDrive, ShieldCheck, Gauge, Wifi, Radio,
  ArrowRightCircle
} from 'lucide-react';
import { Message, Role, ChatState, CanvasSnapshot } from './types';
import { sendMessageToGemini } from './services/geminiService';
import ChatMessage from './components/ChatMessage';
import TemplateSelector, { TEMPLATES, Template } from './components/TemplateSelector';

declare global {
  interface AIStudio {
    hasSelectedApiKey: () => Promise<boolean>;
    openSelectKey: () => Promise<void>;
  }
}

type View = 'session' | 'init';
type NodeCategory = 'objective' | 'constraints' | 'pipeline' | 'status' | 'workflow';

interface GraphNode {
  id: string;
  header: string;
  title: string;
  content: string;
  type: 'io' | 'logic' | 'step' | 'result' | 'control';
  category: NodeCategory;
  column: number; 
  order: number;
  x: number;
  y: number;
}

interface Connection {
  fromId: string;
  toId: string;
  type: 'execution' | 'data';
}

interface CategoryGroup {
  id: NodeCategory;
  name: string;
  icon: React.ReactNode;
  color: string;
  glow: string;
  what: string;
  how: string;
  why: string;
}

const CATEGORIES: CategoryGroup[] = [
  { 
    id: 'objective', 
    name: 'ENTRY POINTS', 
    icon: <PlayCircle size={16} />, 
    color: '#ea580c', 
    glow: 'rgba(234, 88, 12, 0.4)',
    what: "The primary intent and problem statement defining the session boundaries.",
    how: "Acts as the root node of the graph, feeding initial constraints into the Logic Engine.",
    why: "Without a clear entry point, the LLM suffers from goal-drift; this anchors the entire reasoning tree."
  },
  { 
    id: 'workflow', 
    name: 'CONTROL ENGINE', 
    icon: <Activity size={16} />, 
    color: '#8b5cf6', 
    glow: 'rgba(139, 92, 246, 0.4)',
    what: "The state machine (Workflow Box) that manages planning vs execution phases.",
    how: "Tracks 'Active Cards' and 'Lock' states to prevent the model from hallucinating new goals mid-derivation.",
    why: "Ensures the engine follows a deterministic path rather than wandering through infinite logical branches."
  },
  { 
    id: 'constraints', 
    name: 'CONSTANTS & PARAMS', 
    icon: <Database size={16} />, 
    color: '#059669', 
    glow: 'rgba(5, 150, 105, 0.4)',
    what: "The immutable facts, axioms, or parameters provided by the user or extracted from the prompt.",
    how: "Data pins connect these constants to the Logic Graph to serve as ground-truth inputs.",
    why: "Deductive reasoning requires stable inputs; this section prevents the 'forgotten fact' phenomenon."
  },
  { 
    id: 'pipeline', 
    name: 'LOGIC GRAPH', 
    icon: <Workflow size={16} />, 
    color: '#2563eb', 
    glow: 'rgba(37, 99, 235, 0.4)',
    what: "The transformational steps where inferences are derived from constraints.",
    how: "A series of interconnected logic nodes linked via execution pins (flow) and data pins (state).",
    why: "Visualizing the derivation path allows human collaborators to spot logical fallacies at a glance."
  },
  { 
    id: 'status', 
    name: 'TERMINATION', 
    icon: <Target size={16} />, 
    color: '#e11d48', 
    glow: 'rgba(225, 29, 72, 0.4)',
    what: "The conclusion, final result, or stopping condition of the reasoning session.",
    how: "Emits a 'STOP' signal to the model once the success criteria in the Workflow Box are met.",
    why: "Provides a definitive logical exit, preventing the model from loop-reasoning unnecessarily."
  },
];

const NODE_WIDTH = 380;
const NODE_HEADER_HEIGHT = 44;
const PIN_OFFSET_X = 12;

const App: React.FC = () => {
  const [view, setView] = useState<View>('init');
  const [showAbout, setShowAbout] = useState(false);
  const [flippedArtifactId, setFlippedArtifactId] = useState<string | null>(null);
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    canvas: "",
    sessionStarted: false,
    snapshots: [],
    lastSavedAt: null
  });
  const [input, setInput] = useState('');
  const [problemInput, setProblemInput] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<Template>(TEMPLATES[0]);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [canvasMode, setCanvasMode] = useState<'graph' | 'source'>('graph');
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [editingNode, setEditingNode] = useState<GraphNode | null>(null);
  const [zoomLevel, setZoomLevel] = useState(0.5);
  const [visibleNodeTypes, setVisibleNodeTypes] = useState<Set<GraphNode['type']>>(new Set(['io', 'logic', 'step', 'result', 'control']));
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const dragStartPos = useRef({ x: 0, y: 0 });
  const nodeStartPos = useRef({ x: 0, y: 0 });
  const scrollRef = useRef<HTMLDivElement>(null);

  // --- Robust Patch Applier (Preserved) ---
  const applyPatchSafely = (current: string, patchText: string): string => {
    let canvasLines = current ? current.split('\n') : [];
    const patchLines = patchText.split('\n');
    interface Section { header: string; body: string[]; }
    const parseSections = (lines: string[]): Section[] => {
      const sections: Section[] = [];
      let currentSection: Section | null = null;
      lines.forEach((line) => {
        const isHeader = line.match(/^[A-Z]\)\s|^\[.*?\]|^STEP:\s|^STOP:\s|^WORKFLOW BOX/i);
        if (isHeader) {
          if (currentSection) sections.push(currentSection);
          currentSection = { header: line.trim(), body: [] };
        } else if (currentSection) {
          currentSection.body.push(line);
        }
      });
      if (currentSection) sections.push(currentSection);
      return sections;
    };
    let sections = parseSections(canvasLines);
    let i = 0;
    while (i < patchLines.length) {
      const line = patchLines[i].trim();
      if (!line) { i++; continue; }
      const stepMatch = line.match(/^STEP:\s*(.*)$/i);
      const stopMatch = line.match(/^STOP:\s*(.*)$/i);
      const opMatch = line.match(/^([+~-])\s*\[(.*?)\]/);
      if (stepMatch) {
        const existing = sections.find(s => s.header.startsWith('STEP:'));
        if (existing) existing.header = `STEP: ${stepMatch[1]}`;
        else sections.unshift({ header: `STEP: ${stepMatch[1]}`, body: [] });
      } else if (stopMatch) {
        const existing = sections.find(s => s.header.startsWith('STOP:'));
        if (existing) existing.header = `STOP: ${stopMatch[1]}`;
        else sections.push({ header: `STOP: ${stopMatch[1]}`, body: [] });
      } else if (opMatch) {
        const [_, op, targetHeader] = opMatch;
        const section = sections.find(s => s.header.toLowerCase().includes(targetHeader.toLowerCase()));
        let contentBlock: string[] = [];
        i++;
        while (i < patchLines.length && !patchLines[i].match(/^([+~-])\s*\[/) && !patchLines[i].match(/^STOP:/) && !patchLines[i].match(/^STEP:/)) {
          contentBlock.push(patchLines[i]); i++;
        }
        i--;
        if (section) {
          if (op === '+') section.body.push(...contentBlock);
          else if (op === '~') section.body = contentBlock;
        } else if (op === '+') {
          sections.push({ header: `[${targetHeader}]`, body: contentBlock });
        }
      }
      i++;
    }
    return sections.map(s => [s.header, ...s.body].join('\n')).join('\n');
  };

  const isStopped = useMemo(() => state.canvas.includes('STOP: true') || state.canvas.includes('STEP: FINAL'), [state.canvas]);

  const pendingProposal = useMemo(() => {
    return [...state.messages].reverse().find(m => 
      m.role === Role.MODEL && m.proposal && !m.proposalAccepted && !m.proposalRejected
    );
  }, [state.messages]);

  const filteredNodes = useMemo(() => nodes.filter(n => visibleNodeTypes.has(n.type)), [nodes, visibleNodeTypes]);
  const filteredConnections = useMemo(() => connections.filter(conn => {
    const f = nodes.find(n => n.id === conn.fromId);
    const t = nodes.find(n => n.id === conn.toId);
    return f && t && visibleNodeTypes.has(f.type) && visibleNodeTypes.has(t.type);
  }), [connections, nodes, visibleNodeTypes]);

  const categoryBounds = useMemo(() => {
    const bounds: Record<string, { x: number; y: number; w: number; h: number }> = {};
    CATEGORIES.forEach(cat => {
      const catNodes = filteredNodes.filter(n => n.category === cat.id);
      if (catNodes.length === 0) return;
      const minX = Math.min(...catNodes.map(n => n.x)) - 80;
      const minY = Math.min(...catNodes.map(n => n.y)) - 100;
      const maxX = Math.max(...catNodes.map(n => n.x + NODE_WIDTH)) + 80;
      const maxY = Math.max(...catNodes.map(n => n.y + 300)) + 60;
      bounds[cat.id] = { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
    });
    return bounds;
  }, [filteredNodes]);

  const autoAlignBlueprint = useCallback(() => {
    setNodes(prev => {
      const sorted = [...prev].sort((a, b) => a.order - b.order);
      let yp: Record<NodeCategory, number> = { objective: 200, workflow: 200, constraints: 200, pipeline: 200, status: 1400 };
      let xp: Record<NodeCategory, number> = { objective: 200, workflow: 650, constraints: 1100, pipeline: 1550, status: 200 };
      return sorted.map(node => {
        const x = xp[node.category], y = yp[node.category];
        if (node.category === 'pipeline') xp.pipeline += 500;
        else if (node.category === 'status') xp.status += 500;
        else yp[node.category] += 420;
        return { ...node, x, y };
      });
    });
  }, []);

  const handleSend = useCallback(async (overridePrompt?: string, forceCanvas?: string) => {
    const prompt = (overridePrompt || input).trim();
    if (!prompt && !overridePrompt) return;
    if (state.isLoading) return;
    const canvas = forceCanvas !== undefined ? forceCanvas : state.canvas;
    const userMsg: Message = { id: Date.now().toString(), role: Role.USER, content: prompt || "(Advancing logic)", timestamp: Date.now() };
    setState(prev => ({ ...prev, messages: [...prev.messages, userMsg], isLoading: true, error: null }));
    if (!overridePrompt) setInput('');
    try {
      const aiResponse = await sendMessageToGemini([...state.messages, userMsg], prompt, canvas);
      const patch = aiResponse.match(/===?\s*CANVAS\s*PATCH\s*===?\s*([\s\S]*?)\s*===?\s*END\s*PATCH\s*===?/i)?.[1].trim() || null;
      const modelMsg: Message = { id: (Date.now() + 1).toString(), role: Role.MODEL, content: aiResponse, timestamp: Date.now(), proposal: patch };
      setState(prev => ({ ...prev, messages: [...prev.messages, modelMsg], isLoading: false }));
    } catch (err: any) {
      setState(prev => ({ ...prev, isLoading: false, error: err.message || "Logic failure." }));
    }
  }, [input, state.messages, state.isLoading, state.canvas]);

  const handleAcceptProposal = (messageId: string, patch: string) => {
    const newCanvas = applyPatchSafely(state.canvas, patch);
    setState(prev => ({ 
      ...prev, 
      canvas: newCanvas, 
      messages: prev.messages.map(m => m.id === messageId ? { ...m, proposalAccepted: true } : m) 
    }));
    if (!newCanvas.includes('STOP: true') && !newCanvas.includes('STEP: FINAL')) {
      setTimeout(() => handleSend("Step verified.", newCanvas), 600);
    }
  };

  const resetState = useCallback(() => {
    if (confirm("Reset neural workspace?")) {
      setState({ messages: [], isLoading: false, error: null, canvas: "", sessionStarted: false, snapshots: [], lastSavedAt: null });
      setNodes([]); setConnections([]); setView('init'); setProblemInput('');
    }
  }, []);

  const loadDemo = (type: 'tech' | 'creative') => {
    const techCanvas = `STEP: 0\n[WORKFLOW BOX]\nMode: PLANNING\nActive Card: None\nObjective: Optimize distributed consensus.\nLock: false\n\n[A) PROBLEM]\nDesign low-latency ledger sync.\n\n[B) GIVEN]\n- Nodes: 10,000\n- Latency: < 100ms\n\nSTOP: false`;
    const creativeCanvas = `STEP: 0\n[WORKFLOW BOX]\nMode: PLANNING\nActive Card: None\nObjective: Define brand luxury logic.\nLock: false\n\n[A) PROBLEM]\nVisual identity for coffee brand.\n\n[B) GIVEN]\n- Target: Urbanites\n- Palette: Earth + Gold\n\nSTOP: false`;
    const canvas = type === 'tech' ? techCanvas : creativeCanvas;
    setState(p => ({ ...p, canvas, sessionStarted: true, messages: [{ id: 'm1', role: Role.USER, content: "Load demo snapshot.", timestamp: Date.now() }, { id: 'm2', role: Role.MODEL, content: "Memory snapshot restored. Workspace active.", timestamp: Date.now()+100 }] }));
    setView('session');
    setZoomLevel(0.45);
    setTimeout(() => autoAlignBlueprint(), 200);
  };

  useEffect(() => {
    if (view === 'session' && state.canvas) {
      const newNodes: GraphNode[] = [];
      const newConnections: Connection[] = [];
      const sections = state.canvas.split(/(?=[A-Z]\)\s|^\[.*?\]|STEP:\s|STOP:\s|WORKFLOW BOX)/im);
      let stepId: string | null = null, rootId: string | null = null, workflowId: string | null = null;
      sections.forEach((s, idx) => {
        if (!s.trim()) return;
        const lines = s.split('\n');
        const marker = lines[0].match(/^([A-Z]\)\s?|\[.*?\]|STEP:\s?|STOP:\s?|WORKFLOW BOX)(.*)/im);
        const header = marker ? marker[1] : "";
        const title = marker ? marker[2].trim() : lines[0].trim();
        const content = lines.slice(1).join('\n').trim();
        const id = `node-${idx}`;
        let type: GraphNode['type'] = 'logic';
        let category: NodeCategory = 'constraints';
        if (header.toUpperCase().includes('WORKFLOW') || title.toUpperCase().includes('WORKFLOW')) {
           category = 'workflow'; type = 'control'; workflowId = id;
        } else if (title.toUpperCase().includes('PROBLEM') || title.toUpperCase().includes('GOAL')) { 
          category = 'objective'; type = 'io'; if (title.toUpperCase().includes('PROBLEM')) rootId = id;
        } else if (title.toUpperCase().includes('GIVEN') || title.toUpperCase().includes('AXIOMS')) { 
          category = 'constraints'; type = 'io';
        } else if (header.startsWith('STEP:')) { 
          category = 'pipeline'; type = 'step'; 
        } else if (header.startsWith('STOP:')) {
          category = 'status'; type = 'result';
        }
        const existing = nodes.find(n => n.id === id);
        newNodes.push({ id, header, title, content, type, category, column: 0, order: idx, x: existing?.x || 0, y: existing?.y || 0 });
        if (category === 'pipeline' || category === 'status') {
          if (stepId) newConnections.push({ fromId: stepId, toId: id, type: 'execution' });
          else if (workflowId) newConnections.push({ fromId: workflowId, toId: id, type: 'execution' });
          else if (rootId) newConnections.push({ fromId: rootId, toId: id, type: 'execution' });
          stepId = id;
        } else if (workflowId && id !== workflowId) {
          newConnections.push({ fromId: id, toId: workflowId, type: 'data' });
        }
      });
      setNodes(newNodes);
      setConnections(newConnections);
    }
  }, [state.canvas, view]);

  return (
    <div className="flex flex-col h-screen bg-[#09090b] text-slate-200 font-sans overflow-hidden">
      <header className="flex items-center justify-between px-6 py-3 bg-[#18181b] border-b border-white/10 z-50">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-600 rounded-lg"><Workflow size={18} className="text-white" /></div>
            <h1 className="text-sm font-black tracking-tight"><span className="text-blue-500 italic">νόησις</span> Blueprint</h1>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <button onClick={() => setShowAbout(true)} className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-white transition-all"><HelpCircle size={14} /> System Info</button>
          {view === 'session' && (
            <div className="flex items-center gap-3">
               <button onClick={() => setCanvasMode(canvasMode === 'graph' ? 'source' : 'graph')} className="px-4 py-1.5 text-[9px] font-black uppercase tracking-widest text-slate-500">Toggle View</button>
               <button onClick={() => handleSend("Step verified.")} disabled={state.isLoading || isStopped} className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-[9px] font-black uppercase tracking-widest transition-all shadow-lg active:scale-95 disabled:opacity-30 flex items-center gap-2"><FastForward size={14} /> Advance</button>
               <button onClick={resetState} className="p-2 text-slate-500 hover:text-rose-500 transition-colors"><RotateCcw size={16} /></button>
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {view === 'init' && (
          <div className="flex-1 flex flex-col bg-[#09090b] overflow-hidden blueprint-grid relative">
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
              <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[50%] bg-blue-600/5 blur-[120px] rounded-full" />
              <div className="absolute bottom-[-10%] left-[-5%] w-[40%] h-[50%] bg-purple-600/5 blur-[120px] rounded-full" />
            </div>

            <div className="flex flex-1 overflow-hidden z-10">
              <aside className="w-80 border-r border-white/5 bg-black/40 p-6 flex flex-col gap-6 animate-in slide-in-from-left duration-700">
                <div>
                  <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-4 flex items-center gap-2"><Gauge size={14}/> Core Diagnostics</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Neural Link', value: 'Operational', icon: <Wifi size={12} className="text-emerald-500"/>, color: 'text-emerald-500' },
                      { label: 'Engine', value: 'Gemini 3 Pro', icon: <Cpu size={12} className="text-blue-500"/>, color: 'text-blue-500' },
                      { label: 'Latency', value: '42ms', icon: <Radio size={12} className="text-amber-500"/>, color: 'text-amber-500' },
                      { label: 'Buffer', value: '24k Tokens', icon: <HardDrive size={12} className="text-slate-400"/>, color: 'text-slate-400' },
                    ].map((stat, i) => (
                      <div key={i} className="bg-white/5 border border-white/5 rounded-xl p-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="p-1.5 bg-black/40 rounded-lg">{stat.icon}</span>
                          <span className="text-[9px] font-black uppercase tracking-widest text-slate-400">{stat.label}</span>
                        </div>
                        <span className={`text-[10px] font-black ${stat.color}`}>{stat.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-4 flex items-center gap-2"><ShieldCheck size={14}/> Pre-Flight Integrity</h3>
                  <div className="space-y-2">
                    {['Auth Protocol Verified', 'Graph Schema Loaded', 'Session Persistence Active'].map((item, i) => (
                      <div key={i} className="flex items-center gap-2 text-[9px] text-slate-500 font-bold uppercase tracking-widest">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                        {item}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-auto pt-6 border-t border-white/5">
                  <div className="bg-blue-600/10 border border-blue-500/20 rounded-2xl p-4 flex items-center gap-4">
                    <Rocket size={24} className="text-blue-500" />
                    <div>
                      <p className="text-[10px] font-black text-white uppercase tracking-widest">v0.8.0 Release</p>
                      <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Stability Upgrade</p>
                    </div>
                  </div>
                </div>
              </aside>

              <main className="flex-1 overflow-y-auto custom-scrollbar p-12">
                <div className="max-w-4xl mx-auto space-y-12 animate-in fade-in zoom-in-95 duration-700">
                  <div className="text-left space-y-2">
                     <div className="flex items-center gap-3 mb-4">
                       <div className="h-px flex-1 bg-white/5" />
                       <span className="text-[10px] font-black uppercase tracking-[0.6em] text-blue-500">Initialization Hub</span>
                       <div className="h-px flex-1 bg-white/5" />
                     </div>
                     <h1 className="text-6xl font-black italic tracking-tighter uppercase text-white leading-none">Command Center</h1>
                     <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500 font-bold max-w-lg">Configure neural logic protocols and mission parameters to begin a new reasoning session.</p>
                  </div>

                  <div className="space-y-8">
                    <section className="bg-[#111113] border border-white/5 rounded-[2rem] p-8 shadow-2xl relative overflow-hidden group">
                      <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                         <Layers size={120} />
                      </div>
                      <div className="flex items-center justify-between mb-8">
                        <h2 className="text-[11px] font-black uppercase tracking-[0.3em] text-blue-500 flex items-center gap-3"><Layers size={16}/> Select Reasoning Schema</h2>
                        <span className="text-[9px] font-black px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full border border-blue-500/20 uppercase tracking-widest">Protocol Required</span>
                      </div>
                      <TemplateSelector selectedId={selectedTemplate.id} onSelect={setSelectedTemplate} />
                    </section>

                    <section className="bg-[#111113] border border-white/5 rounded-[2rem] p-8 shadow-2xl relative">
                      <div className="flex items-center justify-between mb-8">
                        <h2 className="text-[11px] font-black uppercase tracking-[0.3em] text-emerald-500 flex items-center gap-3"><Target size={16}/> Objective Parameters</h2>
                        <span className="text-[9px] font-black px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20 uppercase tracking-widest">Input Authored</span>
                      </div>
                      <div className="relative">
                        <textarea 
                          value={problemInput} 
                          onChange={e => setProblemInput(e.target.value)} 
                          placeholder="Describe the logic challenge, constraints, and target outcomes..." 
                          className="w-full bg-black/40 border border-white/10 rounded-2xl p-6 text-slate-200 font-mono text-sm focus:outline-none focus:border-blue-500/50 h-48 resize-none mb-8 shadow-inner" 
                        />
                      </div>
                      <button 
                        onClick={() => { 
                          setView('session'); 
                          setState(p => ({ ...p, sessionStarted: true, canvas: `STEP: 0\n[WORKFLOW BOX]\nMode: PLANNING\nObjective: ${problemInput.slice(0, 50)}...\nLock: false\n\n[A) PROBLEM]\n${problemInput}\n\nSTOP: false` })); 
                          handleSend(`${selectedTemplate.initialPrompt}\n\nObjective:\n${problemInput}`); 
                        }} 
                        disabled={!problemInput.trim()} 
                        className="w-full py-6 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black uppercase tracking-[0.3em] text-sm active:scale-95 transition-all shadow-2xl shadow-blue-600/20 disabled:opacity-20 flex items-center justify-center gap-4 group"
                      >
                        <Zap size={20} className="group-hover:animate-pulse" /> Launch Neural Instance
                      </button>
                    </section>
                  </div>
                </div>
              </main>

              <aside className="w-96 border-l border-white/5 bg-black/40 p-8 flex flex-col gap-8 animate-in slide-in-from-right duration-700 overflow-y-auto custom-scrollbar">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 flex items-center gap-2">
                      <History size={14}/> Session Artifacts
                    </h3>
                  </div>
                  <div className="space-y-6">
                    {/* ARTIFACT 1 */}
                    <div className="relative h-44 perspective-1000">
                      <div className={`relative w-full h-full transition-all duration-700 preserve-3d ${flippedArtifactId === 'demo-tech' ? 'rotate-y-180' : ''}`}>
                        <div className="absolute inset-0 bg-[#18181b] border border-white/5 rounded-2xl p-4 backface-hidden flex flex-col group overflow-hidden">
                           <div className="flex items-start justify-between mb-3">
                             <div className="p-2 bg-blue-600/10 rounded-lg text-blue-500"><Cpu size={18} /></div>
                             <button onClick={() => setFlippedArtifactId('demo-tech')} className="p-1 text-slate-600 hover:text-white transition-colors"><Info size={14}/></button>
                           </div>
                           <h4 className="text-[11px] font-black text-white uppercase tracking-widest mb-1">Distributed Sync</h4>
                           <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-3">Ledger Logic Snapshot</p>
                           <button onClick={() => loadDemo('tech')} className="mt-auto py-2 bg-blue-600/10 border border-blue-500/20 rounded-lg text-[9px] font-black text-blue-400 uppercase tracking-widest hover:bg-blue-600/20 transition-all flex items-center justify-center gap-2">Restore Instance <ArrowRightCircle size={12}/></button>
                        </div>
                        <div className="absolute inset-0 bg-[#0f172a] border border-blue-500/40 rounded-2xl p-5 backface-hidden rotate-y-180 flex flex-col">
                           <div className="flex items-center justify-between mb-3">
                             <span className="text-[8px] font-black text-blue-400 uppercase tracking-widest">Metadata Artifact</span>
                             <button onClick={() => setFlippedArtifactId(null)} className="text-slate-500"><X size={12}/></button>
                           </div>
                           <div className="space-y-2">
                             <div><span className="text-[7px] font-black text-slate-600 uppercase">What</span><p className="text-[8px] text-slate-400">Optimization of low-latency consensus protocols.</p></div>
                             <div><span className="text-[7px] font-black text-slate-600 uppercase">How</span><p className="text-[8px] text-slate-400">Uses coordinate geometry to map node latencies.</p></div>
                             <div><span className="text-[7px] font-black text-slate-600 uppercase">Why</span><p className="text-[8px] text-slate-400">Verifying synchronization stability in distributed ledgers.</p></div>
                           </div>
                        </div>
                      </div>
                    </div>

                    {/* ARTIFACT 2 */}
                    <div className="relative h-44 perspective-1000">
                      <div className={`relative w-full h-full transition-all duration-700 preserve-3d ${flippedArtifactId === 'demo-creative' ? 'rotate-y-180' : ''}`}>
                        <div className="absolute inset-0 bg-[#18181b] border border-white/5 rounded-2xl p-4 backface-hidden flex flex-col group overflow-hidden">
                           <div className="flex items-start justify-between mb-3">
                             <div className="p-2 bg-purple-600/10 rounded-lg text-purple-500"><Sparkles size={18} /></div>
                             <button onClick={() => setFlippedArtifactId('demo-creative')} className="p-1 text-slate-600 hover:text-white transition-colors"><Info size={14}/></button>
                           </div>
                           <h4 className="text-[11px] font-black text-white uppercase tracking-widest mb-1">Luxury Identity</h4>
                           <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-3">Brand Arch Snapshot</p>
                           <button onClick={() => loadDemo('creative')} className="mt-auto py-2 bg-purple-600/10 border border-purple-500/20 rounded-lg text-[9px] font-black text-purple-400 uppercase tracking-widest hover:bg-purple-600/20 transition-all flex items-center justify-center gap-2">Restore Instance <ArrowRightCircle size={12}/></button>
                        </div>
                        <div className="absolute inset-0 bg-[#0f172a] border border-purple-500/40 rounded-2xl p-5 backface-hidden rotate-y-180 flex flex-col">
                           <div className="flex items-center justify-between mb-3">
                             <span className="text-[8px] font-black text-purple-400 uppercase tracking-widest">Metadata Artifact</span>
                             <button onClick={() => setFlippedArtifactId(null)} className="text-slate-500"><X size={12}/></button>
                           </div>
                           <div className="space-y-2">
                             <div><span className="text-[7px] font-black text-slate-600 uppercase">What</span><p className="text-[8px] text-slate-400">Thematic logic for a boutique coffee experience.</p></div>
                             <div><span className="text-[7px] font-black text-slate-600 uppercase">How</span><p className="text-[8px] text-slate-400">Mapping sensory attributes to visual vectors.</p></div>
                             <div><span className="text-[7px] font-black text-slate-600 uppercase">Why</span><p className="text-[8px] text-slate-400">Ensuring narrative consistency across all touchpoints.</p></div>
                           </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-auto">
                  <div className="bg-[#111113] border border-white/5 rounded-2xl p-6 space-y-4 shadow-inner">
                     <h4 className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-400 border-b border-white/5 pb-2">Artifact Registry Log</h4>
                     <div className="font-mono text-[9px] space-y-2 opacity-50">
                        <p className="text-emerald-500">[SYSTEM] Session IDs verified</p>
                        <p className="text-blue-500">[CACHE] Snapshot-082 Ready</p>
                        <p className="text-slate-500">[AUTH] Signature matching...</p>
                        <p className="text-amber-500 animate-pulse">[INIT] Awaiting Mission Data...</p>
                     </div>
                  </div>
                </div>
              </aside>
            </div>

            {showAbout && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-12 bg-black/98 backdrop-blur-2xl animate-in fade-in duration-500">
                <div className="bg-[#18181b] border-2 border-white/5 rounded-[3.5rem] w-full max-w-4xl shadow-2xl flex flex-col overflow-hidden max-h-[85vh]">
                  <header className="px-14 py-10 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-4"><BookOpen size={28} className="text-blue-500" /><h2 className="text-2xl font-black uppercase italic text-white tracking-tight">System Specification</h2></div>
                    <button onClick={() => setShowAbout(false)} className="p-3 hover:bg-white/5 rounded-full text-slate-500 transition-all"><X size={32} /></button>
                  </header>
                  <div className="p-14 overflow-y-auto custom-scrollbar space-y-12">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
                      <div className="space-y-6">
                        <h3 className="text-xs font-black uppercase tracking-[0.4em] text-blue-500">Persistent Canvas</h3>
                        <p className="text-slate-400 text-sm leading-relaxed">Reasoning is not a chat bubble. It is a shared working state. Noesis enforces a persistent canvas where the model stores derived facts, constants, and working memory, preventing logical decay.</p>
                      </div>
                      <div className="space-y-6">
                        <h3 className="text-xs font-black uppercase tracking-[0.4em] text-emerald-500">Workflow Box Control</h3>
                        <p className="text-slate-400 text-sm leading-relaxed">The reasoning path is governed by a state machine (Workflow Box). Transitions between planning and execution are explicit, ensuring every inference turn is directed toward a concrete objective.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {view === 'session' && (
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 relative flex flex-col bg-[#09090b]">
              <div className="flex-1 relative overflow-hidden blueprint-grid">
                {canvasMode === 'source' ? (
                  <textarea value={state.canvas} onChange={e => setState(p => ({ ...p, canvas: e.target.value }))} className="w-full h-full p-12 bg-transparent font-mono text-sm text-blue-400 focus:outline-none resize-none" spellCheck={false} />
                ) : (
                  <div className="absolute inset-0 overflow-auto custom-scrollbar p-20">
                    <div className="min-w-[10000px] min-h-[6000px] relative origin-top-left" style={{ transform: `scale(${zoomLevel})` }}>
                      {CATEGORIES.map(cat => {
                        const b = categoryBounds[cat.id];
                        if (!b) return null;
                        return (
                          <div key={cat.id} className="absolute rounded-[2rem] border pointer-events-none transition-all duration-700" style={{ left: b.x, top: b.y, width: b.w, height: b.h, backgroundColor: `${cat.color}03`, borderColor: `${cat.color}15` }}>
                             <div className="absolute top-[-36px] left-8 px-5 py-2 rounded-t-xl flex items-center gap-3 group/header pointer-events-auto cursor-help" style={{ backgroundColor: `${cat.color}cc`, color: 'white' }}>
                               {cat.icon} <span className="text-[10px] font-black tracking-[0.2em]">{cat.name}</span>
                               <div className="absolute bottom-full left-0 mb-4 w-80 bg-[#18181b] border-2 border-white/10 rounded-2xl p-6 opacity-0 group-hover/header:opacity-100 transition-opacity pointer-events-none shadow-2xl z-[1000]">
                                 <h5 className="text-[9px] font-black uppercase text-white mb-4 border-b border-white/5 pb-2 flex items-center gap-2">{cat.icon} Artifact Definition: {cat.name}</h5>
                                 <div className="space-y-4">
                                   <div><span className="text-[7px] font-black text-slate-500 uppercase">What is it?</span><p className="text-[10px] text-slate-400 leading-relaxed font-medium">{cat.what}</p></div>
                                   <div><span className="text-[7px] font-black text-slate-500 uppercase">Mechanism</span><p className="text-[10px] text-slate-400 leading-relaxed font-medium">{cat.how}</p></div>
                                   <div><span className="text-[7px] font-black text-slate-500 uppercase">Rationale</span><p className="text-[10px] text-slate-400 leading-relaxed font-medium">{cat.why}</p></div>
                                 </div>
                               </div>
                             </div>
                             <div className="absolute inset-0 rounded-[2rem]" style={{ boxShadow: `0 0 50px ${cat.glow}` }} />
                          </div>
                        );
                      })}
                      <svg className="absolute inset-0 pointer-events-none w-full h-full">
                        <defs><marker id="arrow-exec" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" /></marker></defs>
                        {filteredConnections.map((conn, idx) => {
                          const f = nodes.find(n => n.id === conn.fromId), t = nodes.find(n => n.id === conn.toId);
                          if (!f || !t) return null;
                          const isE = conn.type === 'execution';
                          const y1 = f.y + NODE_HEADER_HEIGHT + (isE ? 30 : 140), y2 = t.y + NODE_HEADER_HEIGHT + (isE ? 30 : 140);
                          const x1 = f.x + NODE_WIDTH - PIN_OFFSET_X, x2 = t.x + PIN_OFFSET_X;
                          const d = Math.abs(x2 - x1), off = Math.min(d * 0.5, 150);
                          return <path key={idx} d={`M ${x1} ${y1} C ${x1 + off} ${y1}, ${x2 - off} ${y2}, ${x2} ${y2}`} stroke={isE ? "#3b82f6" : "#475569"} strokeWidth={isE ? 4 : 2} fill="none" markerEnd={isE ? "url(#arrow-exec)" : ""} opacity={isE ? 0.9 : 0.4} />;
                        })}
                      </svg>
                      {filteredNodes.map(node => (
                        <div key={node.id} className="absolute group select-none" style={{ left: node.x, top: node.y }}>
                           <div className="bg-[#18181b] border-2 border-black rounded-2xl overflow-hidden shadow-2xl" style={{ width: NODE_WIDTH }}>
                              <div className="px-5 py-3 flex items-center justify-between border-b border-black" style={{ background: `linear-gradient(90deg, ${CATEGORIES.find(c => c.id === node.category)?.color}77, #18181b)` }}>
                                 <span className="text-[11px] font-black uppercase text-white tracking-widest">{node.title}</span>
                                 <GripHorizontal size={14} className="text-white/20" />
                              </div>
                              <div className="p-6 bg-black/40 min-h-[140px]" onClick={() => setEditingNode(node)}>
                                 <p className="text-[13px] font-mono text-slate-400 whitespace-pre-wrap leading-relaxed">{node.content}</p>
                              </div>
                           </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </main>
            <aside className={`flex flex-col bg-[#18181b] border-l border-white/10 transition-all duration-300 ${isChatOpen ? 'w-[500px]' : 'w-0 overflow-hidden'}`}>
              <div className="flex items-center justify-between px-8 py-5 bg-black/40 border-b border-white/5 min-w-[500px]">
                <div className="flex items-center gap-3 text-slate-400 font-bold uppercase tracking-widest text-[10px]"><MessageSquare size={16} className="text-blue-400" /> Neural Inference</div>
                <button onClick={() => setIsChatOpen(false)} className="text-slate-500 hover:text-white transition-all"><PanelRightClose size={18} /></button>
              </div>
              <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-10 custom-scrollbar space-y-10 min-w-[500px]">
                {state.messages.map(m => <ChatMessage key={m.id} message={m} onAcceptProposal={handleAcceptProposal} onRejectProposal={id => setState(p => ({ ...p, messages: p.messages.map(m => m.id === id ? { ...m, proposalRejected: true } : m) }))} />)}
                {state.isLoading && <div className="flex justify-start animate-pulse text-[10px] font-black text-blue-500 uppercase tracking-widest">Compiling neural state...</div>}
              </div>
              <footer className="p-8 border-t border-white/5 bg-black/20 min-w-[500px]">
                <div className="relative group">
                  <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }} placeholder="Direct logic input..." className="w-full bg-black/60 border border-white/10 rounded-2xl px-6 py-5 pr-16 text-slate-200 focus:outline-none focus:border-blue-500/50 resize-none h-24 font-mono text-sm shadow-2xl" />
                  <button onClick={() => handleSend()} disabled={!input.trim() || state.isLoading} className="absolute right-4 bottom-4 p-4 bg-blue-600 text-white rounded-xl hover:bg-blue-500 disabled:opacity-5 transition-all"><Send size={20} /></button>
                </div>
              </footer>
            </aside>
          </div>
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
        .blueprint-grid {
          background-size: 20px 20px, 100px 100px;
          background-image: 
            linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px);
        }
        .perspective-1000 { perspective: 1000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
      `}</style>
    </div>
  );
};

export default App;
