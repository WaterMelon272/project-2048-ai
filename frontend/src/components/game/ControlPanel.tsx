"use client";
import { useState } from "react";
import { useGameStore } from "@/store/useGameStore";
import { 
  Brain, Sliders, FlaskConical, X, 
  ChevronDown, Check, Zap, Shield, Dices, 
  ArrowDownFromLine, Layers, Activity, Dna, Loader2, 
  PlayCircle, Trophy, Sigma, Move, Timer
} from "lucide-react"; 

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

// Danh sách thuật toán
const ALGO_OPTIONS = [
  { id: "Expectimax (Default)", label: "Expectimax", desc: "Balanced & Smart", icon: Zap, color: "text-yellow-400" },
  { id: "Minimax (Classic)", label: "Minimax", desc: "Defensive / Cautious", icon: Shield, color: "text-blue-400" },
  { id: "Monte Carlo (MCTS)", label: "Monte Carlo", desc: "Simulation Based", icon: Dices, color: "text-pink-400" },
  { id: "DFS (Greedy)", label: "DFS Greedy", desc: "Deep Search / Risky", icon: ArrowDownFromLine, color: "text-red-400" },
  { id: "BFS (Layered)", label: "BFS Layered", desc: "Wide Search / Slow", icon: Layers, color: "text-green-400" },
];

export default function ControlPanel({ isOpen, onClose }: Props) {
  // Tab chính: Config | Lab | Display
  const [activeTab, setActiveTab] = useState<"ai" | "game" | "lab">("ai");
  
  // State cho Dropdown chọn thuật toán
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // State cho LAB (Chế độ con: Benchmark hoặc Training)
  const [labMode, setLabMode] = useState<"bench" | "train">("bench");

  // --- STATE: BENCHMARK ---
  const [benchIter, setBenchIter] = useState(20); // Số lần chạy thử
  const [isBenching, setIsBenching] = useState(false);
  const [benchResult, setBenchResult] = useState<any>(null);

  // --- STATE: GA TRAINING ---
  const [isTraining, setIsTraining] = useState(false);
  const [gaParams, setGaParams] = useState({ pop: 4, gen: 2, mut: 0.1 });
  const [trainResult, setTrainResult] = useState<any>(null);

  const { 
    algorithm, setAlgorithm,
    aiSpeed, setAiSpeed, 
    aiDepth, setAiDepth, 
    showAnimation, toggleAnimation,
    heuristics, setHeuristic
  } = useGameStore();

  // --- API: CHẠY BENCHMARK ---
  const runBenchmark = async () => {
    setIsBenching(true);
    setBenchResult(null);
    try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/benchmark", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                algorithm: algorithm,
                depth: aiDepth, 
                weights: {
                    monotonic: heuristics.monotonic,
                    smoothness: heuristics.smoothness,
                    free_tiles: heuristics.freeTiles,
                    merges: heuristics.merges 
                },
                iterations: benchIter
            })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        setBenchResult(data);
    } catch (e) {
        alert("Benchmark Failed. Is Backend running?");
    }
    setIsBenching(false);
  };

  // --- API: CHẠY GA TRAINING ---
  const startTraining = async () => {
    setIsTraining(true);
    setTrainResult(null);
    try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/ga/train", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                population_size: gaParams.pop,
                generations: gaParams.gen,
                mutation_rate: gaParams.mut
            })
        });
        const data = await res.json();
        
        if (data.best_weights) {
            setTrainResult(data);
        }
    } catch (e) {
        alert("Training Error: Is Backend Running?");
    }
    setIsTraining(false);
  };

  // Helper render Tab Button
  const tabBtn = (id: typeof activeTab, label: string, Icon: any) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex-1 py-3 flex flex-col items-center justify-center gap-1 text-xs font-bold transition-all border-b-2 ${
        activeTab === id 
          ? "border-cyan-400 text-cyan-300 bg-cyan-900/20" 
          : "border-transparent text-gray-400 hover:text-white hover:bg-white/5"
      }`}
    >
      <Icon size={18} />
      {label}
    </button>
  );

  // Helper render Slider
  const HeuristicSlider = ({ label, field, max, colorClass }: { label: string, field: string, max: number, colorClass: string }) => {
    // @ts-ignore
    const value = heuristics[field];
    return (
      <div className="space-y-1">
        <div className="flex justify-between text-[10px] uppercase font-bold tracking-wider text-gray-400">
          <span>{label}</span>
          <span className={colorClass}>{value?.toFixed(1)}</span>
        </div>
        <input 
          type="range" min="0" max={max} step="0.1" value={value || 0}
          // @ts-ignore
          onChange={(e) => setHeuristic(field, Number(e.target.value))}
          className={`w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer hover:bg-gray-600 transition-colors [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white ${
             colorClass === "text-cyan-400" ? "[&::-webkit-slider-thumb]:bg-cyan-400" :
             colorClass === "text-purple-400" ? "[&::-webkit-slider-thumb]:bg-purple-400" :
             colorClass === "text-green-400" ? "[&::-webkit-slider-thumb]:bg-green-400" :
             "[&::-webkit-slider-thumb]:bg-yellow-400"
          }`}
        />
      </div>
    );
  };

  const currentAlgoObj = ALGO_OPTIONS.find(opt => opt.id === algorithm) || ALGO_OPTIONS[0];

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-[4000] transition-opacity duration-300 ${isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}`}
        onClick={onClose}
      />

      {/* Main Drawer */}
      <div className={`fixed top-0 right-0 h-full w-[400px] max-w-[90%] bg-slate-900/95 backdrop-blur-xl border-l border-white/10 shadow-2xl z-[5000] transition-transform duration-300 ease-in-out transform flex flex-col ${isOpen ? "translate-x-0" : "translate-x-full"}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Sliders size={20} className="text-cyan-400"/> System Config
            </h2>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full text-gray-400 hover:text-white transition-colors"><X size={20} /></button>
        </div>

        {/* Main Tabs */}
        <div className="flex border-b border-white/10 bg-black/10">
          {tabBtn("ai", "Config", Brain)}
          {tabBtn("lab", "AI Lab", FlaskConical)}
          {tabBtn("game", "Display", Sliders)}
        </div>

        {/* Content Area */}
        <div className="flex-1 p-5 overflow-y-auto custom-scrollbar space-y-6 pb-20">
          
          {/* === TAB 1: AI CONFIG === */}
          {activeTab === "ai" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              
              {/* Algorithm Select */}
              <div className="space-y-3 relative">
                <h3 className="text-cyan-400 font-bold text-sm uppercase tracking-wider flex items-center gap-2">
                  <Brain size={14}/> Core Algorithm
                </h3>
                <button 
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="w-full flex items-center justify-between bg-black/40 border border-white/10 rounded-xl p-3 text-left hover:border-cyan-500/50 transition-all group"
                >
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-white/5 ${currentAlgoObj.color}`}>
                            <currentAlgoObj.icon size={20} />
                        </div>
                        <div>
                            <div className="text-sm font-bold text-white">{currentAlgoObj.label}</div>
                            <div className="text-[10px] text-gray-400">{currentAlgoObj.desc}</div>
                        </div>
                    </div>
                    <ChevronDown size={16} className={`text-gray-500 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}/>
                </button>

                {isDropdownOpen && (
                    <div className="absolute top-full left-0 w-full mt-2 bg-slate-800/95 backdrop-blur-xl border border-cyan-500/30 rounded-xl shadow-[0_0_30px_rgba(0,0,0,0.5)] overflow-hidden z-50 animate-in fade-in zoom-in-95">
                        {ALGO_OPTIONS.map((opt) => (
                            <button key={opt.id} onClick={() => { setAlgorithm(opt.id); setIsDropdownOpen(false); }} className={`w-full flex items-center justify-between p-3 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 ${algorithm === opt.id ? "bg-cyan-500/10" : ""}`}>
                                <div className="flex items-center gap-3">
                                    <opt.icon size={18} className={opt.color} />
                                    <div className="text-left">
                                        <div className={`text-sm font-bold ${algorithm === opt.id ? "text-cyan-300" : "text-gray-300"}`}>{opt.label}</div>
                                        <div className="text-[10px] text-gray-500">{opt.desc}</div>
                                    </div>
                                </div>
                                {algorithm === opt.id && <Check size={16} className="text-cyan-400"/>}
                            </button>
                        ))}
                    </div>
                )}
                {isDropdownOpen && <div className="fixed inset-0 z-40" onClick={() => setIsDropdownOpen(false)}></div>}
              </div>

              {/* Heuristics Sliders */}
              <div className="bg-white/5 p-4 rounded-xl border border-white/10 space-y-4 shadow-inner">
                  <h3 className="text-green-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
                      <Activity size={14}/> Heuristics Tuning
                  </h3>
                  <HeuristicSlider label="Monotonicity" field="monotonic" max={100} colorClass="text-cyan-400" />
                  <HeuristicSlider label="Smoothness" field="smoothness" max={20} colorClass="text-purple-400" />
                  <HeuristicSlider label="Free Tiles" field="freeTiles" max={100} colorClass="text-green-400" />
                  <HeuristicSlider label="Merges" field="merges" max={100} colorClass="text-yellow-400" />
              </div>

              {/* Depth & Speed */}
              <div className="space-y-4 pt-2 border-t border-white/10">
                 <div className="space-y-2">
                    <div className="flex justify-between text-sm"><span className="text-gray-300">Search Depth</span><span className="text-purple-400 font-mono font-bold">{aiDepth}</span></div>
                    <input type="range" min="1" max="8" step="1" value={aiDepth} onChange={(e) => setAiDepth(Number(e.target.value))} className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"/>
                 </div>
                 <div className="space-y-2">
                    <div className="flex justify-between text-sm"><span className="text-gray-300">AI Speed</span><span className="text-blue-400 font-mono font-bold">{aiSpeed}ms</span></div>
                    <input type="range" min="10" max="1000" step="10" value={aiSpeed} onChange={(e) => setAiSpeed(Number(e.target.value))} className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"/>
                 </div>
              </div>
            </div>
          )}

          {/* === TAB 2: AI LAB (NEW) === */}
          {activeTab === "lab" && (
             <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
                 
                 {/* Sub-Tabs Switcher */}
                 <div className="flex bg-black/40 p-1 rounded-xl border border-white/10">
                     <button onClick={() => setLabMode("bench")} className={`flex-1 py-1.5 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-all ${labMode==="bench" ? "bg-cyan-600 text-white shadow" : "text-gray-400 hover:text-white"}`}>
                         <Activity size={12}/> Benchmark
                     </button>
                     <button onClick={() => setLabMode("train")} className={`flex-1 py-1.5 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-all ${labMode==="train" ? "bg-purple-600 text-white shadow" : "text-gray-400 hover:text-white"}`}>
                         <Dna size={12}/> Evolution
                     </button>
                 </div>

                 {/* --- MODE 1: BENCHMARK (MỚI) --- */}
                 {labMode === "bench" && (
                    <div className="space-y-4">
                        <div className="p-3 bg-cyan-900/10 border border-cyan-500/20 rounded-xl text-[10px] text-cyan-200">
                            Runs multiple simulations with current settings to measure reliability.
                            <br/><span className="font-bold text-yellow-400">Warning:</span> High depth ({aiDepth}) will be very slow.
                        </div>

                        {/* Iterations Selector */}
                        <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-gray-500">Iterations (Games)</label>
                            <div className="flex gap-2">
                                {[10, 20, 50, 100].map(n => (
                                    <button key={n} onClick={() => setBenchIter(n)} 
                                        className={`flex-1 py-1 text-xs rounded border ${benchIter===n ? "bg-cyan-500/20 border-cyan-500 text-cyan-300" : "border-white/10 hover:bg-white/5 text-gray-400"}`}>
                                        {n}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Run Button */}
                        <button 
                            disabled={isBenching}
                            onClick={runBenchmark}
                            className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${isBenching ? "bg-gray-700 cursor-not-allowed" : "bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-900/30"}`}
                        >
                            {isBenching ? <Loader2 size={18} className="animate-spin"/> : <PlayCircle size={18}/>}
                            {isBenching ? "Running Simulations..." : "Start Benchmark"}
                        </button>

                        {/* RESULT REPORT */}
                        {benchResult && (
                            <div className="animate-in fade-in zoom-in-95 space-y-3 pt-2">
                                {/* Grid thống kê */}
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="bg-white/5 p-2 rounded border border-white/5">
                                        <div className="text-[9px] text-gray-400 uppercase flex items-center gap-1"><Trophy size={10}/> Win Rate</div>
                                        <div className={`text-lg font-black ${benchResult.win_rate > 50 ? "text-green-400" : "text-orange-400"}`}>
                                            {benchResult.win_rate.toFixed(1)}%
                                        </div>
                                    </div>
                                    <div className="bg-white/5 p-2 rounded border border-white/5">
                                        <div className="text-[9px] text-gray-400 uppercase flex items-center gap-1"><Sigma size={10}/> Avg Score</div>
                                        <div className="text-lg font-black text-white">{Math.round(benchResult.avg_score).toLocaleString()}</div>
                                    </div>
                                    <div className="bg-white/5 p-2 rounded border border-white/5">
                                        <div className="text-[9px] text-gray-400 uppercase flex items-center gap-1"><Move size={10}/> Avg Moves</div>
                                        <div className="text-lg font-black text-white">{Math.round(benchResult.avg_moves)}</div>
                                    </div>
                                    <div className="bg-white/5 p-2 rounded border border-white/5">
                                        <div className="text-[9px] text-gray-400 uppercase flex items-center gap-1"><Timer size={10}/> Time/Game</div>
                                        <div className="text-lg font-black text-white">{benchResult.avg_time_per_game.toFixed(2)}s</div>
                                    </div>
                                </div>

                                {/* Tile Distribution Chart */}
                                <div className="bg-black/20 p-3 rounded-xl border border-white/5 space-y-2">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold mb-2">Max Tile Probability</div>
                                    {benchResult.tile_distribution.map((item: any) => (
                                        <div key={item.tile} className="flex items-center gap-2 text-[10px]">
                                            <div className={`w-8 font-bold text-right ${item.tile >= 2048 ? "text-yellow-400" : "text-gray-400"}`}>{item.tile}</div>
                                            <div className="flex-1 h-3 bg-gray-800 rounded-full overflow-hidden">
                                                <div 
                                                    className={`h-full rounded-full ${item.tile >= 2048 ? "bg-yellow-500" : "bg-cyan-600"}`} 
                                                    style={{ width: `${item.percent}%` }}
                                                />
                                            </div>
                                            <div className="w-8 text-right text-gray-300">{Math.round(item.percent)}%</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                 )}

                 {/* --- MODE 2: GENETIC EVOLUTION (TRAINING) --- */}
                 {labMode === "train" && (
                    <div className="space-y-4">
                        <div className="p-3 bg-purple-900/10 border border-purple-500/20 rounded-xl text-[10px] text-purple-200">
                             Simulate natural selection to evolve the best heuristics.
                             <br/><span className="font-bold text-pink-400">Note:</span> CPU intensive.
                        </div>

                        {/* Input Parameters */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-[10px] uppercase font-bold text-gray-500">Population</label>
                                <input type="number" min="2" value={gaParams.pop} onChange={e=>setGaParams({...gaParams, pop: Number(e.target.value)})} 
                                    className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-sm text-center focus:border-purple-500 outline-none"/>
                            </div>
                            <div className="space-y-1">
                                <label className="text-[10px] uppercase font-bold text-gray-500">Generations</label>
                                <input type="number" min="1" value={gaParams.gen} onChange={e=>setGaParams({...gaParams, gen: Number(e.target.value)})} 
                                    className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-sm text-center focus:border-purple-500 outline-none"/>
                            </div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-gray-500 flex justify-between">
                                <span>Mutation Rate</span>
                                <span className="text-purple-400">{gaParams.mut}</span>
                            </label>
                            <input type="range" min="0" max="1" step="0.05" value={gaParams.mut} onChange={e=>setGaParams({...gaParams, mut: Number(e.target.value)})} 
                                   className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"/>
                        </div>

                        {/* Start Button */}
                        <button 
                            disabled={isTraining}
                            onClick={startTraining}
                            className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
                                isTraining 
                                ? "bg-gray-700 text-gray-400 cursor-not-allowed" 
                                : "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-lg shadow-purple-900/30"
                            }`}
                        >
                            {isTraining ? <Loader2 size={18} className="animate-spin"/> : <Dna size={18}/>}
                            {isTraining ? "Evolving AI..." : "Start Evolution"}
                        </button>

                        {/* Training Results */}
                        {trainResult && (
                            <div className="animate-in fade-in zoom-in-95 p-4 rounded-xl bg-green-900/10 border border-green-500/30 space-y-3">
                                <div className="flex items-center justify-between border-b border-green-500/20 pb-2">
                                    <span className="text-green-400 font-bold text-xs uppercase flex items-center gap-2">
                                        <Check size={14}/> Training Complete
                                    </span>
                                    <span className="text-[10px] text-gray-400">{trainResult.duration_seconds}s</span>
                                </div>
                                
                                <div className="text-center border-b border-green-500/10 pb-3">
                                    <div className="text-[10px] text-gray-400 uppercase">Best Fitness Score</div>
                                    <div className="text-2xl font-black text-white">{Math.round(trainResult.best_score_achieved)}</div>
                                </div>

                                {/* HIỂN THỊ BỘ TRỌNG SỐ TÌM ĐƯỢC */}
                                <div className="space-y-1">
                                    <div className="text-[10px] text-gray-500 uppercase font-bold text-center mb-1">Recommended Weights</div>
                                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[11px]">
                                        <div className="flex justify-between items-center">
                                            <span className="text-gray-400">Monotonic</span> 
                                            <span className="text-cyan-400 font-mono font-bold">{trainResult.best_weights.monotonic.toFixed(1)}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-gray-400">Smoothness</span> 
                                            <span className="text-purple-400 font-mono font-bold">{trainResult.best_weights.smoothness.toFixed(1)}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-gray-400">Free Tiles</span> 
                                            <span className="text-green-400 font-mono font-bold">{trainResult.best_weights.free_tiles.toFixed(1)}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-gray-400">Merges</span> 
                                            <span className="text-yellow-400 font-mono font-bold">{trainResult.best_weights.merges.toFixed(1)}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                 )}

             </div>
          )}

          {/* === TAB 3: DISPLAY SETTINGS === */}
          {activeTab === "game" && (
             <div className="space-y-6 animate-in fade-in">
                 <button onClick={toggleAnimation} className="w-full flex justify-between p-3 bg-white/5 rounded-lg border border-white/5 hover:bg-white/10 transition-colors">
                    <span className="text-sm text-gray-300">Animations</span>
                    <span className={showAnimation ? "text-green-400 font-bold" : "text-gray-500"}>{showAnimation ? "ON" : "OFF"}</span>
                 </button>
             </div>
          )}

        </div>
      </div>
    </>
  );
}