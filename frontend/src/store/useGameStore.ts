import { create } from 'zustand';
import { Tile as TileType, generateTile, moveTiles, tilesToGrid, checkGameOver } from '@/lib/gameLogic';

interface GameState {
  tiles: TileType[];
  score: number;
  bestScore: number;
  gameOver: boolean;
  isAI: boolean;
  gameId: number;
  history: TileType[][];
  showAnimation: boolean;

  // --- Queue Processing ---
  isProcessing: boolean;
  moveQueue: number[];
  processQueue: () => Promise<void>;
  executeMoveImmediate: (dir: number) => void; // Hàm thực thi logic game
  
  // Settings
  aiSpeed: number;
  aiDepth: number;
  algorithm: string;
  setAlgorithm: (name: string) => void;

  // Heuristics Tuning
  heuristics: {
    monotonic: number;
    smoothness: number;
    freeTiles: number;
    merges: number;
  };
  setHeuristic: (key: string, val: number) => void;

  // Stats & Database
  movesCount: number;
  saveScoreToDb: () => Promise<void>;
  
  // Notification
  notification: string | null;
  showNotification: (msg: string) => void;

  // Actions
  initGame: () => void;
  move: (dir: 0 | 1 | 2 | 3) => void;
  toggleAI: () => void;
  setAiSpeed: (speed: number) => void;
  setAiDepth: (depth: number) => void;
  runAITurn: () => Promise<void>;
  undo: () => void;
  toggleAnimation: () => void;
  syncPersonalBest: () => Promise<void>;
}

export const useGameStore = create<GameState>((set, get) => ({
  tiles: [],
  score: 0,
  bestScore: 0,
  gameOver: false,
  isAI: false,
  gameId: 0,
  aiSpeed: 150,
  aiDepth: 3,
  history: [],
  showAnimation: true,
  movesCount: 0,
  algorithm: "Expectimax (Default)",
  notification: null,
  
  // State cho Queue
  isProcessing: false,
  moveQueue: [],

  heuristics: {
    monotonic: 1.0,
    smoothness: 0.1,
    freeTiles: 10,
    merges: 1.0
  },

  initGame: () => {
    let newTiles = generateTile([]);
    newTiles = generateTile(newTiles);
    const currentBest = get().bestScore;

    set((state) => ({
        gameId: state.gameId + 1, 
        tiles: newTiles, 
        score: 0, 
        gameOver: false, 
        isAI: false, 
        bestScore: currentBest, 
        history: [], 
        movesCount: 0,
        moveQueue: [], // Reset queue khi new game
        isProcessing: false
    }));
  },

  // 1. Hàm MOVE: Chỉ có nhiệm vụ đẩy vào hàng đợi
  move: (dir) => {
    const { moveQueue, processQueue, gameOver } = get();
    if (gameOver) return;

    // Đẩy lệnh vào hàng đợi
    // (Bạn có thể giới hạn length < 5 để tránh spam phím nếu muốn, nhưng để tự do cho mượt)
    set({ moveQueue: [...moveQueue, dir] });
    
    // Kích hoạt bộ xử lý
    processQueue();
  },

  // 2. Hàm Xử lý hàng đợi: Tuần tự và có Delay
  processQueue: async () => {
    const { isProcessing, moveQueue, executeMoveImmediate, isAI, aiSpeed } = get();

    // Nếu đang bận hoặc hết lệnh thì dừng
    if (isProcessing || moveQueue.length === 0) return;

    // Khóa lại
    set({ isProcessing: true });

    // Lấy lệnh đầu tiên
    const dir = moveQueue[0];
    set({ moveQueue: moveQueue.slice(1) }); // Xóa lệnh vừa lấy khỏi queue

    // Thực thi Logic Game
    executeMoveImmediate(dir);

    // --- QUẢN LÝ THỜI GIAN CHỜ (QUAN TRỌNG) ---
    // Mặc định chờ 100ms (khớp với CSS animation duration)
    let delay = 100;

    // Nếu là AI và đang chạy chế độ siêu tốc (<100ms)
    // Thì Delay = 0 để animation trở thành tức thì (tránh lag queue)
    if (isAI && aiSpeed < 100) {
        delay = 0;
    }

    // Chờ animation hoàn tất
    if (delay > 0) {
        await new Promise((resolve) => setTimeout(resolve, delay));
    }

    // Mở khóa
    set({ isProcessing: false });

    // Đệ quy: Nếu còn lệnh trong hàng đợi thì xử lý tiếp ngay
    if (get().moveQueue.length > 0) {
        get().processQueue();
    }
  },

  // 3. Hàm Logic Game (Được tách ra từ hàm move cũ)
  executeMoveImmediate: (dir) => {
    const { tiles, score, bestScore, history, saveScoreToDb } = get();
    
    const { tiles: nextTiles, score: addedScore, moved } = moveTiles(tiles, dir as 0|1|2|3);

    if (moved) {
        const newHistory = [...history, tiles].slice(-3);
        const newScore = score + addedScore;
        const newTilesWithRandom = generateTile(nextTiles);
        const isOver = checkGameOver(newTilesWithRandom);
        
        if (newScore > bestScore) set({ bestScore: newScore });

        set((state) => ({ 
            tiles: newTilesWithRandom, 
            score: newScore,
            bestScore: Math.max(newScore, bestScore),
            gameOver: isOver,
            history: newHistory,
            movesCount: state.movesCount + 1
        }));

        if (isOver) {
            saveScoreToDb();
        }
    }
  },

  toggleAI: () => set((state) => ({ isAI: !state.isAI, moveQueue: [] })), // Xóa queue khi toggle AI để tránh lệnh tồn đọng
  setAiSpeed: (speed) => set({ aiSpeed: speed }),
  setAiDepth: (depth) => set({ aiDepth: depth }),
  setAlgorithm: (name) => set({ algorithm: name }),

  setHeuristic: (key, val) => set((state) => ({
    heuristics: { ...state.heuristics, [key]: val }
  })),

  showNotification: (msg) => {
    set({ notification: msg });
    setTimeout(() => set({ notification: null }), 2000);
  },

  saveScoreToDb: async () => {
    const { score, tiles, movesCount, isAI, algorithm, showNotification, syncPersonalBest} = get();
    const maxTile = tiles.reduce((max, t) => (t.val > max ? t.val : max), 0);

    try {
        const res = await fetch("/api/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                score,
                maxTile,
                moves: movesCount,
                isAi: isAI,
                algoName: algorithm
            })
        });

        if (res.ok) {
          showNotification("Score Saved!");
          syncPersonalBest();
        }
    } catch (e) { console.error("Save failed"); }
  },

  syncPersonalBest: async () => {
      try {
          const res = await fetch("/api/user/best");
          if (res.ok) {
              const data = await res.json();
              const { bestScore } = get();
              if (data.score > bestScore) {
                  set({ bestScore: data.score });
              }
          }
      } catch (e) { console.error("Sync best score failed"); }
  },

  runAITurn: async () => {
    const { isAI, gameOver, tiles, move, aiSpeed, aiDepth, gameId: sendingGameId, algorithm, heuristics } = get();
    if (!isAI || gameOver) return;

    const grid = tilesToGrid(tiles);
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    try {
      const res = await fetch(`${API_URL}/api/v1/move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            board: grid, 
            depth: aiDepth, 
            algorithm: algorithm,
            weights: {
                monotonic: heuristics.monotonic,
                smoothness: heuristics.smoothness,
                free_tiles: heuristics.freeTiles,
                merges: heuristics.merges
            }
        }), 
      });
      
      const data = await res.json();
      const { gameId: currentGameId, isAI: currentIsAI } = get();

      if (sendingGameId !== currentGameId || !currentIsAI) return;

      if (data.move !== -1) {
         // AI cũng gọi hàm move như người thường -> Vào Queue
         move(data.move); 
         
         // Đợi đến lượt tiếp theo
         setTimeout(() => {
             if (get().isAI) get().runAITurn();
         }, aiSpeed); 
      } else {
         set({ isAI: false });
      }
    } catch (error) {
      console.error("AI Error:", error);
      set({ isAI: false });
    }
  }, 

  undo: () => {
    const { history, isAI } = get();
    if (isAI || history.length === 0) return;

    const previousTiles = history[history.length - 1];
    const newHistory = history.slice(0, -1);

    set((state) => ({
        tiles: previousTiles,
        history: newHistory,
        gameOver: false,
        score: state.score - 2,
        movesCount: state.movesCount > 0 ? state.movesCount - 1 : 0,
        moveQueue: [] // Clear queue khi undo để tránh xung đột
    }));
  }, 

  toggleAnimation: () => set((state) => ({ showAnimation: !state.showAnimation }))
}));