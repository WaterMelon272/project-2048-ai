import random
from .base import BaseSolver

# Bảng tìm ô trống (dùng chung)
_EMPTY_TABLE = [[] for _ in range(65536)]
for r in range(65536):
    line = [(r >> (i*4)) & 0xF for i in range(4)]
    _EMPTY_TABLE[r] = [i for i, val in enumerate(line) if val == 0]

class MCTSSolver(BaseSolver):
    def __init__(self, depth=3, weights=None):
        super().__init__(depth, weights)
        # Tăng số lượng mô phỏng lên vì Bitboard chạy nhanh
        self.simulations_per_move = 100 
        # Độ sâu mô phỏng (nhìn xa bao nhiêu bước trong tưởng tượng)
        self.simulation_depth = depth*2

    def get_best_move(self, grid):
        if isinstance(grid, int):
            board = grid
        else:
            board = self.grid_to_bitboard(grid)

        best_score = -float('inf')
        best_move = -1
        
        # 1. Root Expansion: Thử 4 hướng đi đầu tiên
        for direction in range(4):
            new_board, score_gained, moved = self.simulate_move(board, direction)
            
            if not moved:
                continue 

            # 2. Simulation: Chạy thử nghiệm từ trạng thái mới
            avg_score = self.run_simulations(new_board, score_gained)
            
            if avg_score > best_score:
                best_score = avg_score
                best_move = direction

        return best_move

    def run_simulations(self, start_board, initial_score):
        total_final_score = 0
        
        for _ in range(self.simulations_per_move):
            current_board = start_board
            current_score = initial_score
            is_game_over = False

            for _ in range(self.simulation_depth):
                # --- A. ENEMY TURN (Sinh số ngẫu nhiên) ---
                # 1. Tìm ô trống
                cells = []
                for idx in _EMPTY_TABLE[current_board & 0xFFFF]: cells.append(idx)
                for idx in _EMPTY_TABLE[(current_board >> 16) & 0xFFFF]: cells.append(idx + 4)
                for idx in _EMPTY_TABLE[(current_board >> 32) & 0xFFFF]: cells.append(idx + 8)
                for idx in _EMPTY_TABLE[(current_board >> 48) & 0xFFFF]: cells.append(idx + 12)

                if not cells: 
                    is_game_over = True
                    break 

                idx = random.choice(cells)
                val = 1 if random.random() < 0.9 else 2
                current_board |= (val << (idx * 4))

                # --- B. AI TURN (Greedy Walk - KHÔNG RANDOM HOÀN TOÀN) ---
                # Thay vì random, ta thử cả 4 nước, nước nào ăn điểm (score_gained > 0) thì ưu tiên
                
                best_local_move = -1
                best_local_score = -1
                best_next_board = current_board
                found_move = False

                # Danh sách các nước đi hợp lệ
                valid_moves = []

                # Thử tất cả 4 hướng
                for move in range(4):
                    next_b, s, m = self.simulate_move(current_board, move)
                    if m:
                        valid_moves.append((move, s, next_b))
                        # Ưu tiên nước đi gộp được nhiều điểm nhất
                        if s > best_local_score:
                            best_local_score = s
                            best_local_move = move
                            best_next_board = next_b

                if not valid_moves:
                    is_game_over = True
                    break # Chết

                # CHIẾN THUẬT ROLLOUT:
                # 80% chọn nước đi ăn điểm nhiều nhất (Greedy)
                # 20% chọn ngẫu nhiên trong các nước hợp lệ (để khám phá)
                if best_local_move != -1 and random.random() < 0.8:
                    current_board = best_next_board
                    current_score += best_local_score
                else:
                    # Chọn ngẫu nhiên trong các nước đi được
                    _, s, next_b = random.choice(valid_moves)
                    current_board = next_b
                    current_score += s

            # --- C. ĐÁNH GIÁ CUỐI CÙNG ---
            # Cộng điểm Heuristic Snake vào điểm tích lũy
            # Điều này giúp MCTS biết hướng về đích là cấu trúc đẹp
            final_heuristic = self.evaluator.get_score(current_board)
            
            # Nếu game over sớm, phạt nặng
            if is_game_over:
                total_final_score += (current_score * 0.5) # Bị phạt
            else:
                total_final_score += (current_score + final_heuristic)

        return total_final_score / self.simulations_per_move