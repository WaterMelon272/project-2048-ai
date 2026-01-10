"use client";
import { useGameStore } from "@/store/useGameStore";
import Tile from "./Tile";
import GameOver from "./GameOver";
import { useEffect, useState } from "react";
import { useSwipeable } from "react-swipeable";
import { RotateCcw } from "lucide-react";

export default function Board() {
  const { tiles, move, isAI, undo, history } = useGameStore();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const handlers = useSwipeable({
    onSwipedLeft: () => !isAI && move(0),
    onSwipedRight: () => !isAI && move(1),
    onSwipedUp: () => !isAI && move(2),
    onSwipedDown: () => !isAI && move(3),
    preventScrollOnSwipe: true,
    trackMouse: true
  });

  return (
    <div {...handlers} className="relative mt-2 touch-none select-none group">
        
        {!isAI && history.length > 0 && (
            <button 
                onClick={(e) => {
                    e.stopPropagation();
                    undo();
                }}
                className="absolute -right-14 top-4 z-30 
                hidden md:flex items-center justify-center 
                w-10 h-10 rounded-full 
                bg-white/10 hover:bg-white/20 border border-white/10 
                text-amber-200/80 hover:text-amber-200 hover:scale-110 
                transition-all backdrop-blur-md shadow-lg"
                title="Undo Move"
            >
                <RotateCcw size={20} />
            </button>
        )}
        
        {!isAI && history.length > 0 && (
            <button 
                onClick={(e) => { e.stopPropagation(); undo(); }}
                className="absolute top-2 right-2 z-30 md:hidden p-2 rounded-full bg-black/20 text-white/50"
            >
                <RotateCcw size={16} />
            </button>
        )}
        <GameOver />

        {/* NỀN BÀN CỜ */}
        <div className="relative p-3 rounded-xl w-[370px] h-[370px] grid grid-cols-4 grid-rows-4 gap-3 mx-auto 
            bg-white/5 backdrop-blur-md border border-white/10 shadow-[0_0_40px_rgba(0,0,0,0.5)]">
            {Array.from({ length: 16 }).map((_, i) => (
                <div key={i} className="w-full h-full rounded-lg bg-black/20 border border-white/5"></div>
            ))}
        </div>

        {/* TILES */}
        <div className="absolute inset-0 p-3 w-[370px] h-[370px] mx-auto pointer-events-none">
            {mounted && tiles.map((tile) => (
                <Tile key={tile.id} {...tile} />
            ))}
        </div>
    </div>
  );
}