import { useGameStore } from "@/store/useGameStore";

export default function Header() {
  const { score, bestScore } = useGameStore();

  return (
    <div className="flex justify-between items-center w-full mb-8 px-1">
      <h1 className="text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 drop-shadow-[0_0_10px_rgba(168,85,247,0.5)]">
        2048
      </h1>
      <div className="flex gap-2 text-white">
        <div className="bg-white/10 backdrop-blur-md border border-white/10 p-3 rounded-lg text-center min-w-[80px]">
          <div className="text-xs font-bold text-gray-300 uppercase">Score</div>
          <div className="font-bold text-xl text-white">{score}</div>
        </div>
        <div className="bg-white/10 backdrop-blur-md border border-white/10 p-3 rounded-lg text-center min-w-[80px]">
          <div className="text-xs font-bold text-gray-300 uppercase">Best</div>
          <div className="font-bold text-xl text-white">{bestScore}</div>
        </div>
      </div>
    </div>
  );
}