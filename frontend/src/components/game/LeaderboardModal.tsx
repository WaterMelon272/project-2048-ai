"use client";
import { useEffect, useState } from "react";
import { X, Trophy, Cpu, User } from "lucide-react";

type Props = { isOpen: boolean; onClose: () => void };

export default function LeaderboardModal({ isOpen, onClose }: Props) {
  const [scores, setScores] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch("/api/score")
        .then(res => res.json())
        .then(data => {
            setScores(data);
            setLoading(false);
        });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[6000] flex items-center justify-center bg-black/80 backdrop-blur-md animate-in fade-in">
      <div className="w-full max-w-lg bg-slate-900 border border-yellow-500/30 rounded-2xl shadow-[0_0_50px_rgba(234,179,8,0.2)] overflow-hidden flex flex-col max-h-[80vh]">
        
        {/* Header */}
        <div className="p-5 border-b border-white/10 bg-gradient-to-r from-yellow-900/20 to-transparent flex justify-between items-center">
            <h2 className="text-2xl font-black text-yellow-400 uppercase tracking-widest flex items-center gap-2">
                <Trophy className="text-yellow-400" /> Hall of Fame
            </h2>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors"><X/></button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
            {loading ? (
                <div className="text-center py-10 text-gray-500 animate-pulse">Syncing Database...</div>
            ) : scores.length === 0 ? (
                <div className="text-center py-10 text-gray-500">No records yet. Be the first!</div>
            ) : (
                scores.map((item, idx) => (
                    <div key={item.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all group">
                        
                        {/* Rank & Info */}
                        <div className="flex items-center gap-4">
                            <div className={`w-8 h-8 flex items-center justify-center rounded-full font-black text-sm
                                ${idx === 0 ? "bg-yellow-400 text-black shadow-lg shadow-yellow-400/50" : 
                                  idx === 1 ? "bg-slate-300 text-black" : 
                                  idx === 2 ? "bg-amber-700 text-white" : "bg-white/10 text-gray-400"}`}>
                                {idx + 1}
                            </div>
                            
                            <div>
                                <div className="font-bold text-white flex items-center gap-2">
                                    {item.user?.name || "Anonymous"}
                                    {item.isAi && <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-500/30">BOT</span>}
                                </div>
                                <div className="text-xs text-gray-500 flex items-center gap-3">
                                    <span className="flex items-center gap-1">
                                        {item.isAi ? <Cpu size={10}/> : <User size={10}/>}
                                        {item.algoName}
                                    </span>
                                    <span>•</span>
                                    <span>{new Date(item.createdAt).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>

                        {/* Score */}
                        <div className="text-right">
                            <div className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500">
                                {item.score.toLocaleString()}
                            </div>
                            <div className="text-[10px] text-gray-400 uppercase tracking-wider">
                                Max {item.maxTile}
                            </div>
                        </div>
                    </div>
                ))
            )}
        </div>
      </div>
    </div>
  );
}