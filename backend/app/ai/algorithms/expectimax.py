import random
from .base import BaseSolver, _ROW_LEFT_TABLE, _ROW_RIGHT_TABLE, _SCORE_TABLE

# Ngưỡng cắt nhánh: 0.0001 (0.01%)
CUTOFF_THRESHOLD = 0.0001

_EMPTY_TABLE = [[] for _ in range(65536)]
for r in range(65536):
    line = [(r >> (i*4)) & 0xF for i in range(4)]
    _EMPTY_TABLE[r] = [i for i, val in enumerate(line) if val == 0]

class ExpectimaxSolver(BaseSolver):
    def get_best_move(self, grid):
        # Chuẩn hóa đầu vào (Bitboard vs Grid)
        if isinstance(grid, int):
            board = grid
        else:
            board = self.grid_to_bitboard(grid)
            
        # Bắt đầu đệ quy với xác suất ban đầu là 1.0 (100%)
        return self.expectimax(board, self.depth, True, 1.0)[1]

    def expectimax(self, board, depth, is_maximizing, cumulative_prob):
        # 1. Pruning theo xác suất (Quan trọng)
        # Nếu xác suất xảy ra trường hợp này quá nhỏ, dừng luôn
        if cumulative_prob < CUTOFF_THRESHOLD:
             return self.evaluator.get_score(board), -1

        # 2. Base Case (Hết độ sâu)
        if depth == 0:
            return self.evaluator.get_score(board), -1

        if is_maximizing: # Lượt AI (Max Node)
            best_score = -float('inf')
            best_move = -1
            
            # --- 0: LEFT ---
            r0=board&0xFFFF; r1=(board>>16)&0xFFFF; r2=(board>>32)&0xFFFF; r3=(board>>48)&0xFFFF
            nb = (_ROW_LEFT_TABLE[r0] | (_ROW_LEFT_TABLE[r1]<<16) | (_ROW_LEFT_TABLE[r2]<<32) | (_ROW_LEFT_TABLE[r3]<<48))
            if nb != board:
                # Max node không làm giảm xác suất, truyền nguyên cumulative_prob
                sc, _ = self.expectimax(nb, depth - 1, False, cumulative_prob)
                if sc > best_score: best_score = sc; best_move = 0

            # --- 1: RIGHT ---
            nb = (_ROW_RIGHT_TABLE[r0] | (_ROW_RIGHT_TABLE[r1]<<16) | (_ROW_RIGHT_TABLE[r2]<<32) | (_ROW_RIGHT_TABLE[r3]<<48))
            if nb != board:
                sc, _ = self.expectimax(nb, depth - 1, False, cumulative_prob)
                if sc > best_score: best_score = sc; best_move = 1

            # --- Transpose ---
            a1=board&0xF0F00F0FF0F00F0F; a2=board&0x0000F0F00000F0F0; a3=board&0x0F0F00000F0F0000
            a=a1|(a2<<12)|(a3>>12)
            b1=a&0xFF00FF0000FF00FF; b2=a&0x00FF00FF00000000; b3=a&0x00000000FF00FF00
            tb=b1|(b2>>24)|(b3<<24)

            # --- 2: UP ---
            t_r0=tb&0xFFFF; t_r1=(tb>>16)&0xFFFF; t_r2=(tb>>32)&0xFFFF; t_r3=(tb>>48)&0xFFFF
            ntb = (_ROW_LEFT_TABLE[t_r0] | (_ROW_LEFT_TABLE[t_r1]<<16) | (_ROW_LEFT_TABLE[t_r2]<<32) | (_ROW_LEFT_TABLE[t_r3]<<48))
            if ntb != tb:
                a1=ntb&0xF0F00F0FF0F00F0F; a2=ntb&0x0000F0F00000F0F0; a3=ntb&0x0F0F00000F0F0000
                a=a1|(a2<<12)|(a3>>12)
                b1=a&0xFF00FF0000FF00FF; b2=a&0x00FF00FF00000000; b3=a&0x00000000FF00FF00
                final_b=b1|(b2>>24)|(b3<<24)
                
                sc, _ = self.expectimax(final_b, depth - 1, False, cumulative_prob)
                if sc > best_score: best_score = sc; best_move = 2

            # --- 3: DOWN ---
            ntb = (_ROW_RIGHT_TABLE[t_r0] | (_ROW_RIGHT_TABLE[t_r1]<<16) | (_ROW_RIGHT_TABLE[t_r2]<<32) | (_ROW_RIGHT_TABLE[t_r3]<<48))
            if ntb != tb:
                a1=ntb&0xF0F00F0FF0F00F0F; a2=ntb&0x0000F0F00000F0F0; a3=ntb&0x0F0F00000F0F0000
                a=a1|(a2<<12)|(a3>>12)
                b1=a&0xFF00FF0000FF00FF; b2=a&0x00FF00FF00000000; b3=a&0x00000000FF00FF00
                final_b=b1|(b2>>24)|(b3<<24)

                sc, _ = self.expectimax(final_b, depth - 1, False, cumulative_prob)
                if sc > best_score: best_score = sc; best_move = 3

            if best_move == -1:
                return self.evaluator.get_score(board), -1
            
            return best_score, best_move

        else: # Chance Node (Lượt máy)
            cells = []
            for idx in _EMPTY_TABLE[board & 0xFFFF]: cells.append(idx)
            for idx in _EMPTY_TABLE[(board >> 16) & 0xFFFF]: cells.append(idx + 4)
            for idx in _EMPTY_TABLE[(board >> 32) & 0xFFFF]: cells.append(idx + 8)
            for idx in _EMPTY_TABLE[(board >> 48) & 0xFFFF]: cells.append(idx + 12)

            count = len(cells)
            if count == 0:
                return self.evaluator.get_score(board), -1

            total_expect = 0
            
            # Xác suất rơi vào mỗi ô là 1/count
            prob_per_cell = 1.0 / count 

            for idx in cells:
                shift = idx * 4
                
                # --- Trường hợp ra số 2 (Xác suất 0.9) ---
                # Prob mới = Prob cũ * (1/count) * 0.9
                new_prob_2 = cumulative_prob * prob_per_cell * 0.9
                
                # Chỉ gọi đệ quy nếu xác suất này đủ lớn
                if new_prob_2 >= CUTOFF_THRESHOLD:
                    val2, _ = self.expectimax(board | (1 << shift), depth - 1, True, new_prob_2)
                    total_expect += val2 * 0.9
                
                # --- Trường hợp ra số 4 (Xác suất 0.1) ---
                # Prob mới = Prob cũ * (1/count) * 0.1
                new_prob_4 = cumulative_prob * prob_per_cell * 0.1
                
                if new_prob_4 >= CUTOFF_THRESHOLD:
                    val4, _ = self.expectimax(board | (2 << shift), depth - 1, True, new_prob_4)
                    total_expect += val4 * 0.1
            
            # Chia trung bình cho số ô trống (theo đúng công thức Expectimax)
            # Tổng quát: Sum(Value * Prob) = (Sum(val2*0.9 + val4*0.1)) / count
            return total_expect / count, -1