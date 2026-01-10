import ctypes
import math
import sys
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.ai.manager import AIManager
from app.ai.genetic import GeneticAlgorithm
from app.ai.benchmark import BenchmarkRunner

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GARequest(BaseModel):
    population_size: int = 10
    mutation_rate: float = 0.1
    generations: int = 5

class GameState(BaseModel):
    board: List[List[int]]
    depth: int = 3
    algorithm: str = "Expectimax (Default)"
    weights: Optional[Dict[str, float]] = None

class BenchmarkRequest(BaseModel):
    algorithm: str
    depth: int
    weights: Dict[str, float]
    iterations: int = 10

# Chuyển từ grid 2 chiều sang bitboard
def grid_to_bitboard(grid):
    board = 0
    shift = 0
    for r in range(4):
        for c in range(4):
            val = grid[r][c]
            power = int(math.log2(val)) if val > 0 else 0
            board |= (power << shift)
            shift += 4
    return board

# --- MAPPING HƯỚNG ĐI CHO LOG ---
MOVE_MAP = {
    0: "LEFT",
    1: "RIGHT",
    2: "UP",
    3: "DOWN",
    -1: "STUCK"
}

@app.post("/api/v1/move")
async def get_move(state: GameState):
    start_time = time.time()
    
    final_move = -1
    try:
        solver = AIManager.get_solver(state.algorithm, state.depth, state.weights)
        final_move = solver.get_best_move(grid_to_bitboard(state.board))
    except Exception as e:
        print(e)
        return {"move": -1, "error": str(e)}

    # === IN LOG RA TERMINAL ===
    duration = (time.time() - start_time) * 1000
    move_str = MOVE_MAP.get(final_move, "UNKNOWN ?")

    if state.weights:
        w = state.weights
        print(f"Weights: Mono={w.get('monotonic'):.1f} | Smth={w.get('smoothness'):.1f} | Free={w.get('free_tiles'):.1f} | Max={w.get('merges'):.1f}")

    print(f"[{state.algorithm[:15]:<15}] Move: {move_str} | {duration:6.2f}ms")

    return {"move": final_move, "engine": "Python"}

@app.post("/api/v1/ga/train")
async def run_ga_training(config: GARequest):
    print(f"Starting GA Training... Pop={config.population_size}, Gens={config.generations}")
    
    start_time = time.time()
    
    # Khởi tạo và chạy GA
    ga = GeneticAlgorithm(
        population_size=config.population_size,
        mutation_rate=config.mutation_rate,
        generations=config.generations
    )
    # Trong thực tế nên dùng BackgroundTasks của FastAPI, nhưng để demo ta chờ luôn
    best_weights, best_score = ga.run()
    
    duration = time.time() - start_time

    return {
        "message": "Training Completed",
        "duration_seconds": round(duration, 2),
        "best_score_achieved": best_score,
        "best_weights": best_weights
    }

@app.post("/api/v1/benchmark")
async def run_benchmark(req: BenchmarkRequest):
    print(f"Starting Benchmark: {req.algorithm} x {req.iterations} games...")
    
    try:
        stats = BenchmarkRunner.run(
            algo_name=req.algorithm,
            depth=req.depth,
            weights=req.weights,
            iterations=req.iterations
        )
        return stats
    except Exception as e:
        print(e)
        return {"error": str(e)}    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)