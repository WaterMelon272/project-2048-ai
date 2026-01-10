import random
from .base import BaseSolver, _ROW_LEFT_TABLE, _ROW_RIGHT_TABLE, _SCORE_TABLE

_EMPTY_TABLE = [[] for _ in range(65536)]
for r in range(65536):
    line = [(r >> (i*4)) & 0xF for i in range(4)]
    _EMPTY_TABLE[r] = [i for i, val in enumerate(line) if val == 0]

class MinimaxSolver(BaseSolver):
    def get_best_move(self, grid):
        # Bắt đầu đệ quy
        return self.minimax(grid, self.depth, True)[1]

    def minimax(self, board, depth, is_maximizing):
        # Base Case
        if depth == 0:
            return self.evaluator.get_score(board), -1

        if is_maximizing:
            best_score = -float('inf')
            best_move = -1
            
            # 0: LEFT
            r0=board&0xFFFF; r1=(board>>16)&0xFFFF; r2=(board>>32)&0xFFFF; r3=(board>>48)&0xFFFF
            nb = (_ROW_LEFT_TABLE[r0] | (_ROW_LEFT_TABLE[r1]<<16) | (_ROW_LEFT_TABLE[r2]<<32) | (_ROW_LEFT_TABLE[r3]<<48))
            if nb != board:
                # Tính score heuristic cho node con
                # (Có thể cộng thêm _SCORE_TABLE[...] nếu muốn tính điểm gộp)
                sc, _ = self.minimax(nb, depth - 1, False)
                if sc > best_score:
                    best_score = sc; best_move = 0

            # 1: RIGHT
            nb = (_ROW_RIGHT_TABLE[r0] | (_ROW_RIGHT_TABLE[r1]<<16) | (_ROW_RIGHT_TABLE[r2]<<32) | (_ROW_RIGHT_TABLE[r3]<<48))
            if nb != board:
                sc, _ = self.minimax(nb, depth - 1, False)
                if sc > best_score:
                    best_score = sc; best_move = 1

            # Transpose cho Up/Down
            # Inline Transpose Logic
            a1=board&0xF0F00F0FF0F00F0F; a2=board&0x0000F0F00000F0F0; a3=board&0x0F0F00000F0F0000
            a=a1|(a2<<12)|(a3>>12)
            b1=a&0xFF00FF0000FF00FF; b2=a&0x00FF00FF00000000; b3=a&0x00000000FF00FF00
            tb=b1|(b2>>24)|(b3<<24)

            # 2: UP (Move Left trên Transpose)
            t_r0=tb&0xFFFF; t_r1=(tb>>16)&0xFFFF; t_r2=(tb>>32)&0xFFFF; t_r3=(tb>>48)&0xFFFF
            ntb = (_ROW_LEFT_TABLE[t_r0] | (_ROW_LEFT_TABLE[t_r1]<<16) | (_ROW_LEFT_TABLE[t_r2]<<32) | (_ROW_LEFT_TABLE[t_r3]<<48))
            if ntb != tb:
                # Transpose ngược lại
                a1=ntb&0xF0F00F0FF0F00F0F; a2=ntb&0x0000F0F00000F0F0; a3=ntb&0x0F0F00000F0F0000
                a=a1|(a2<<12)|(a3>>12)
                b1=a&0xFF00FF0000FF00FF; b2=a&0x00FF00FF00000000; b3=a&0x00000000FF00FF00
                final_b=b1|(b2>>24)|(b3<<24)
                
                sc, _ = self.minimax(final_b, depth - 1, False)
                if sc > best_score:
                    best_score = sc; best_move = 2

            # 3: DOWN (Move Right trên Transpose)
            ntb = (_ROW_RIGHT_TABLE[t_r0] | (_ROW_RIGHT_TABLE[t_r1]<<16) | (_ROW_RIGHT_TABLE[t_r2]<<32) | (_ROW_RIGHT_TABLE[t_r3]<<48))
            if ntb != tb:
                a1=ntb&0xF0F00F0FF0F00F0F; a2=ntb&0x0000F0F00000F0F0; a3=ntb&0x0F0F00000F0F0000
                a=a1|(a2<<12)|(a3>>12)
                b1=a&0xFF00FF0000FF00FF; b2=a&0x00FF00FF00000000; b3=a&0x00000000FF00FF00
                final_b=b1|(b2>>24)|(b3<<24)

                sc, _ = self.minimax(final_b, depth - 1, False)
                if sc > best_score:
                    best_score = sc; best_move = 3

            # Nếu không đi được nước nào
            if best_move == -1:
                return self.evaluator.get_score(board), -1
            
            return best_score, best_move

        else: # MIN Node
            # FREE CELLS 
            cells = []
            
            # Row 0
            for idx in _EMPTY_TABLE[board & 0xFFFF]: cells.append(idx)
            # Row 1 (Index + 4)
            for idx in _EMPTY_TABLE[(board >> 16) & 0xFFFF]: cells.append(idx + 4)
            # Row 2 (Index + 8)
            for idx in _EMPTY_TABLE[(board >> 32) & 0xFFFF]: cells.append(idx + 8)
            # Row 3 (Index + 12)
            for idx in _EMPTY_TABLE[(board >> 48) & 0xFFFF]: cells.append(idx + 12)

            if not cells:
                return self.evaluator.get_score(board), -1

            best_score = float('inf')

            for idx in cells:
                shift = idx * 4
                # Thử đặt 2
                sc2, _ = self.minimax(board | (1 << shift), depth - 1, True)
                if sc2 < best_score: best_score = sc2
                
                # Thử đặt 4
                sc4, _ = self.minimax(board | (2 << shift), depth - 1, True)
                if sc4 < best_score: best_score = sc4
            
            return best_score, -1