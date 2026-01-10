import { useGameStore } from "@/store/useGameStore";
import { RotateCcw, Zap, ZapOff, Play, Square, RefreshCw } from "lucide-react";

export default function Controls() {
  const { initGame, toggleAI, isAI} = useGameStore();
  const glassBtn = "relative overflow-hidden transition-all duration-300 backdrop-blur-md border shadow-lg active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed";

  return (
    <div className="mt-8 flex flex-col gap-4 w-full">
      {/* Hàng nút chính */}
      <div className="flex gap-4">
        <button 
          onClick={toggleAI}
          className={`flex-1 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 group ${glassBtn} ${
            isAI ? "bg-red-500/20 border-red-500/50 text-red-100 hover:shadow-[0_0_20px_rgba(239,68,68,0.6)] hover:bg-red-500/40" : "bg-cyan-500/20 border-cyan-500/50 text-cyan-100 hover:shadow-[0_0_20px_rgba(6,182,212,0.6)] hover:bg-cyan-500/40"
          }`}
        >
          {isAI ? "STOP AI" : "AI PLAY"}
        </button>
        
        <button 
          onClick={initGame}
          className={`flex-1 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 group ${glassBtn}
            bg-fuchsia-500/20 border-fuchsia-500/50 text-fuchsia-100 
            hover:shadow-[0_0_20px_rgba(217,70,239,0.6)] hover:bg-fuchsia-500/40`}
        >
        <RefreshCw size={20} className="group-hover:rotate-180 transition-transform duration-500"/>
          NEW GAME
        </button>
      </div>
    </div>
  );
}