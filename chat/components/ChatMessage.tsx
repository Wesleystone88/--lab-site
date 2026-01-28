
import React from 'react';
import { Message, Role } from '../types';
import { Check, X, FileDiff, Cpu, User, FastForward } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface ChatMessageProps {
  message: Message;
  onAcceptProposal?: (id: string, patch: string) => void;
  onRejectProposal?: (id: string) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onAcceptProposal, onRejectProposal }) => {
  const isUser = message.role === Role.USER;
  
  // Clean text from patch markers for display
  const displayContent = message.content.replace(/=== CANVAS PATCH ===[\s\S]*?=== END PATCH ===/gi, '').trim();

  return (
    <div className={`flex flex-col gap-2.5 ${isUser ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      <div className="flex items-center gap-2 px-1 text-[8px] font-black uppercase tracking-[0.25em] text-slate-500">
        {isUser ? <>USER_NODE <User size={10} /></> : <><Cpu size={10} className="text-blue-500" /> NEURAL_PROCESS</>}
      </div>

      <div className={`max-w-[95%] rounded-2xl px-5 py-3 shadow-xl ${isUser ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-[#0f172a] border border-slate-800 rounded-tl-none'}`}>
        <div className="prose prose-invert prose-xs max-w-none prose-p:my-1 prose-headings:my-2">
          {displayContent ? (
            <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
              {displayContent}
            </ReactMarkdown>
          ) : (
            message.proposal ? (
              <p className="text-slate-500 italic text-[10px] font-black uppercase tracking-widest">Proposing state update...</p>
            ) : null
          )}
        </div>
      </div>

      {message.proposal && !message.proposalAccepted && !message.proposalRejected && (
        <div className="mt-1 w-full bg-[#020617] border border-amber-500/20 rounded-xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-400">
          <div className="bg-amber-500/5 px-4 py-1.5 border-b border-amber-500/10 flex items-center justify-between">
            <span className="text-[8px] font-black text-amber-500 uppercase tracking-widest flex items-center gap-2">
              <FileDiff size={12} /> Pending Logic Patch
            </span>
          </div>
          <div className="p-3 bg-black/40 overflow-x-auto max-h-40 custom-scrollbar">
            <pre className="text-[10px] font-mono leading-relaxed">
              {message.proposal.split('\n').map((line, i) => {
                const isAdd = line.startsWith('+ ');
                const isRem = line.startsWith('- ');
                const isRep = line.startsWith('~ ');
                const color = isAdd ? 'text-emerald-400/80' : isRem ? 'text-rose-400/80' : isRep ? 'text-amber-400/80' : 'text-slate-500';
                return <div key={i} className={`${color}`}>{line}</div>;
              })}
            </pre>
          </div>
          <div className="flex border-t border-slate-800 divide-x divide-slate-800">
            <button 
              onClick={() => onAcceptProposal?.(message.id, message.proposal!)} 
              className="flex-1 py-2 text-[9px] font-black text-emerald-400 hover:bg-emerald-500/10 transition-all uppercase tracking-widest flex items-center justify-center gap-2"
            >
              Verify <Check size={10} />
            </button>
            <button onClick={() => onRejectProposal?.(message.id)} className="flex-1 py-2 text-[9px] font-black text-rose-400 hover:bg-rose-500/10 transition-all uppercase tracking-widest">Reject</button>
          </div>
        </div>
      )}

      {message.proposalAccepted && (
        <div className="flex items-center gap-2 text-[8px] text-emerald-500 font-black uppercase tracking-[0.2em] px-3 py-1 bg-emerald-500/5 rounded-full border border-emerald-500/20">
          <Check size={10} /> Memory State Synced
        </div>
      )}

      {message.proposalRejected && (
        <div className="flex items-center gap-2 text-[8px] text-slate-500 font-black uppercase tracking-[0.2em] px-3 py-1 bg-slate-500/5 rounded-full border border-slate-500/20">
          <X size={10} /> State Branch Omitted
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
