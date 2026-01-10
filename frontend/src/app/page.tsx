"use client";
import { useEffect, useState } from "react";
import { useGameStore } from "@/store/useGameStore";
import Board from "@/components/game/Board";
import Header from "@/components/game/Header";
import Controls from "@/components/game/Controls";
import ControlPanel from "@/components/game/ControlPanel"; 
import Navbar from "@/components/Navbar"; 
import Stars from "@/components/Stars";
import { useSession } from "next-auth/react";

export default function Home() {
  const { initGame, isAI, runAITurn, move, syncPersonalBest} = useGameStore();
  const [isPanelOpen, setIsPanelOpen] = useState(false); // State quản lý Panel
  const { data: session } = useSession();

  useEffect(() => { initGame(); }, []);
  useEffect(() => { if (isAI) runAITurn(); }, [isAI]);
  useEffect(() => {
    if (session) {
        syncPersonalBest();
    }
  }, [session]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
        if (isAI || isPanelOpen) return;
        if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
            e.preventDefault();
            if (e.key === "ArrowLeft") move(0);
            if (e.key === "ArrowRight") move(1);
            if (e.key === "ArrowUp") move(2);
            if (e.key === "ArrowDown") move(3);
        }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isAI, move, isPanelOpen]);

  return (
    <main className="min-h-screen font-sans bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-900 to-slate-900 text-white relative overflow-hidden selection:bg-cyan-500/30">
        <Stars />
        
        {/* Truyền hàm mở Panel vào Navbar */}
        <Navbar onOpenSettings={() => setIsPanelOpen(true)} />

        {/* CONTAINER CHÍNH */}
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-4">
            <div className="w-full max-w-[420px] flex flex-col items-center">
                <Header />
                <Board />
                <Controls /> 
            </div>
        </div>

        {/* Control Panel (Drawer) */}
        <ControlPanel isOpen={isPanelOpen} onClose={() => setIsPanelOpen(false)} />
    </main>
  );
}