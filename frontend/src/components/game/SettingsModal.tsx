// frontend/src/components/game/SettingsModal.tsx
import { useGameStore } from "@/store/useGameStore";
import { X, Minus, Plus, Gauge, Layers } from "lucide-react"; 

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export default function SettingsModal({ isOpen, onClose }: Props) {
  const { aiSpeed, setAiSpeed, aiDepth, setAiDepth } = useGameStore();

  if (!isOpen) return null;

  // Class cho nút cộng trừ
  const actionBtn = "w-10 h-10 rounded-full flex items-center justify-center bg-white/10 hover:bg-white/20 border border-white/10 transition-colors active:scale-90";

  return (
    <div className="absolute inset-0 z-[5000] flex flex-col items-center justify-center bg-slate-900/90 backdrop-blur-xl animate-in fade-in zoom-in duration-200 rounded-xl border border-white/10 shadow-2xl">
        {/* Nút tắt X ở góc */}
        <button onClick={onClose} className="absolute top-4 right-4 text-white/50 hover:text-white transition-colors">
            <X size={24} />
        </button>

        <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-8 uppercase tracking-widest drop-shadow-lg">
            Settings
        </h2>
        
        {/* === Setting 1: Tốc độ === */}
        <div className="w-72 mb-8">
            <div className="flex justify-between mb-3 items-center">
                <div className="flex items-center gap-2 text-cyan-300 font-bold">
                    <Gauge size={18} /> AI Delay
                </div>
                <span className="text-white font-mono bg-cyan-900/50 px-2 py-1 rounded text-sm border border-cyan-500/30">
                    {aiSpeed} ms
                </span>
            </div>
            
            <div className="flex items-center gap-4 bg-black/20 p-2 rounded-full border border-white/5">
                <button onClick={() => setAiSpeed(Math.max(10, aiSpeed - 10))} className={`${actionBtn} text-cyan-300`}>
                    <Minus size={16} />
                </button>
                
                {/* Custom Range Slider */}
                <input 
                    type="range" min="10" max="1000" step="10" 
                    value={aiSpeed} 
                    onChange={(e) => setAiSpeed(Number(e.target.value))}
                    className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:accent-cyan-400"
                />

                <button onClick={() => setAiSpeed(Math.min(2000, aiSpeed + 10))} className={`${actionBtn} text-cyan-300`}>
                    <Plus size={16} />
                </button>
            </div>
        </div>

        {/* === Setting 2: Độ sâu (Depth) === */}
        <div className="w-72 mb-10">
            <div className="flex justify-between mb-3 items-center">
                <div className="flex items-center gap-2 text-purple-300 font-bold">
                    <Layers size={18} /> Search Depth
                </div>
                <span className="text-white font-mono bg-purple-900/50 px-2 py-1 rounded text-sm border border-purple-500/30">
                    Depth: {aiDepth}
                </span>
            </div>
            
            <div className="flex items-center justify-between bg-black/20 p-2 rounded-xl border border-white/5">
                <button onClick={() => setAiDepth(Math.max(1, aiDepth - 1))} className={`${actionBtn} text-purple-300`}>
                    <Minus size={16} />
                </button>
                
                {/* Visual hiển thị độ sâu bằng các vạch */}
                <div className="flex gap-1 h-2">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                        <div key={i} className={`w-3 rounded-full transition-all ${i <= aiDepth ? "bg-purple-500 shadow-[0_0_8px_#a855f7]" : "bg-gray-700"}`}></div>
                    ))}
                </div>

                <button onClick={() => setAiDepth(Math.min(8, aiDepth + 1))} className={`${actionBtn} text-purple-300`}>
                    <Plus size={16} />
                </button>
            </div>
            <p className="text-xs text-center mt-2 text-white/40 italic">Higher depth = Smarter but Slower</p>
        </div>
    </div>
  );
}