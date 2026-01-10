import multiprocessing
import time
import random
import statistics
from collections import Counter

# Import các solver của bạn (đảm bảo chúng nhận bitboard int)
from .algorithms.expectimax import ExpectimaxSolver
from .algorithms.minimax import MinimaxSolver
from .algorithms.mcts import MCTSSolver
from .algorithms.dfs import DFSSolver
from .algorithms.bfs import BFSSolver
from .algorithms.base import BaseSolver  # Để dùng hàm helper nếu cần

MAX_MOVES = 10000  # Tăng lên vì AI chơi bitboard rất nhanh

def get_max_tile(board):
    """Giải nén bitboard để tìm giá trị ô lớn nhất (2^k)"""
    max_power = 0
    temp = board
    for _ in range(16):
        # Lấy 4 bit cuối (giá trị lũy thừa)
        power = temp & 0xF
        if power > max_power:
            max_power = power
        temp >>= 4
    
    return (1 << max_power) if max_power > 0 else 0

def spawn_random_tile(board):
    """Sinh ngẫu nhiên tile (2 hoặc 4) vào ô trống trên Bitboard"""
    # 1. Tìm tất cả index ô trống (0-15)
    empty_indices = []
    temp = board
    for i in range(16):
        if (temp & 0xF) == 0:
            empty_indices.append(i)
        temp >>= 4
    
    if not empty_indices:
        return board, False  # Full board, cannot spawn

    # 2. Chọn ngẫu nhiên 1 ô
    idx = random.choice(empty_indices)
    
    # 3. Chọn giá trị (90% ra 2, 10% ra 4)
    # Power: 1 (2^1=2) hoặc 2 (2^2=4)
    val_power = 1 if random.random() < 0.9 else 2
    
    # 4. Gán vào board bằng phép OR
    # Dịch giá trị power đến đúng vị trí idx*4
    new_board = board | (val_power << (idx * 4))
    
    return new_board, True

def run_single_session(args):
    """Chạy 1 ván game trọn vẹn dùng Bitboard"""
    algo_name, depth, weights = args
    
    # Init Solver
    if algo_name == "Minimax (Classic)":
        solver = MinimaxSolver(depth, weights)
    elif algo_name == "Expectimax (Default)":
        solver = ExpectimaxSolver(depth, weights)
    elif algo_name == "Monte Carlo (MCTS)":
        solver = MCTSSolver(depth, weights)
    elif algo_name == "DFS (Greedy)":
        solver = DFSSolver(depth, weights)
    else:
        solver = BFSSolver(depth, weights)

    # Init Board (Số nguyên 0)
    board = 0
    
    # Sinh 2 ô đầu tiên
    board, _ = spawn_random_tile(board)
    board, _ = spawn_random_tile(board)

    moves = 0
    start_time = time.time()
    
    while moves < MAX_MOVES:
        # 1. AI Turn: Tìm nước đi tốt nhất
        # solver.get_best_move nhận vào bitboard int
        best_move = solver.get_best_move(board)
        
        if best_move == -1: 
            break # Game over (AI không tìm được nước đi)
        
        # 2. Simulate Move (AI đi)
        # solver.simulate_move nhận bitboard -> trả về (new_board, score, changed)
        # Lưu ý: simulate_move trong class BaseSolver của bạn đã viết cho bitboard
        new_board, _, moved = solver.simulate_move(board, best_move)
        
        if not moved: 
            break # AI bị kẹt (bug hoặc game over thực sự)
        
        board = new_board
        
        # 3. Enemy Turn (Sinh số ngẫu nhiên)
        board, spawned = spawn_random_tile(board)
        
        if not spawned: 
            break # Hết ô trống -> Game over
        
        moves += 1

    duration = time.time() - start_time
    
    # Tính điểm Heuristic cuối cùng
    # Nếu bạn có hàm tính điểm thực (Game Score) thì thay vào đây
    # Ở đây dùng hàm đánh giá Heuristic của solver
    score = solver.evaluator.get_score(board) 
    
    # Tìm Max Tile thực tế đạt được
    max_tile = get_max_tile(board)
    
    return {
        "score": score,
        "max_tile": max_tile,
        "moves": moves,
        "time": duration
    }

class BenchmarkRunner:
    @staticmethod
    def run(algo_name, depth, weights, iterations=20):
        # Chuẩn bị tham số cho pool
        tasks = [(algo_name, depth, weights)] * iterations
        
        # Sử dụng tất cả core CPU để chạy nhanh nhất
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            results = pool.map(run_single_session, tasks)
            
        # --- TỔNG HỢP THỐNG KÊ ---
        scores = [r['score'] for r in results]
        moves = [r['moves'] for r in results]
        times = [r['time'] for r in results]
        max_tiles = [r['max_tile'] for r in results]
        
        # 1. Tile Distribution (Xác suất đạt tile)
        tile_counts = Counter(max_tiles)
        tile_dist = []
        for tile in sorted(tile_counts.keys(), reverse=True):
            tile_dist.append({
                "tile": tile,
                "count": tile_counts[tile],
                "percent": (tile_counts[tile] / iterations) * 100
            })

        stats = {
            "total_games": iterations,
            "win_rate": (sum(1 for t in max_tiles if t >= 2048) / iterations) * 100,
            
            # Score
            "avg_score": statistics.mean(scores),
            "max_score": max(scores),
            "std_dev_score": statistics.stdev(scores) if iterations > 1 else 0,
            
            # Moves
            "avg_moves": statistics.mean(moves),
            
            # Time
            "avg_time_per_game": statistics.mean(times),
            "total_duration": sum(times),
            
            # Chi tiết phân bố
            "tile_distribution": tile_dist
        }
        
        return stats