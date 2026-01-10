"use client";
import { useGameStore } from "@/store/useGameStore";
import { useEffect, useState } from "react";
import { X, Trophy } from "lucide-react"; // Thêm icon

export default function GameOver() {
  const { gameOver, initGame, score, bestScore } = useGameStore();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (gameOver) {
      setIsVisible(true);
    }
  }, [gameOver]);

  if (!gameOver || !isVisible) return null;

  return (
    <div className="absolute inset-0 z-[4000] flex flex-col items-center justify-center 
        bg-black/60 backdrop-blur-md rounded-xl animate-in fade-in duration-500 border border-white/10">
      
      <button 
        onClick={() => setIsVisible(false)}
        className="absolute top-3 right-3 p-2 text-white/50 hover:text-white hover:bg-white/10 rounded-full transition-all"
        title="View Board"
      >
        <X size={24} />
      </button>

      <h2 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500 mb-2 drop-shadow-lg">
        Game Over!
      </h2>
      
      <div className="flex flex-col gap-2 items-center mb-6">
        <p className="text-white text-xl font-bold">Score: {score}</p>
        
        {score >= bestScore && score > 0 && (
           <div className="flex items-center gap-2 text-yellow-400 font-bold text-sm bg-yellow-400/10 px-3 py-1 rounded-full border border-yellow-400/20">
              <Trophy size={14} /> New Record!
           </div>
        )}
      </div>

      <button 
        onClick={initGame}
        className="px-8 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 
        text-white font-bold text-lg shadow-lg shadow-orange-900/20 transform hover:scale-105 active:scale-95 transition-all"
      >
        Try Again
      </button>
      
      <p className="mt-4 text-white/30 text-xs cursor-pointer hover:text-white/50" onClick={() => setIsVisible(false)}>
        (Close to view board)
      </p>
    </div>
  );
}