import math
from abc import ABC, abstractmethod
from ..heuristics import Heuristics

# --- LOOKUP TABLES ---
_TABLES_INIT = False
_ROW_LEFT_TABLE = [0] * 65536
_ROW_RIGHT_TABLE = [0] * 65536
_SCORE_TABLE = [0] * 65536

def _init_tables():
    global _TABLES_INIT

    for row in range(65536):
        line = [(row >> (i * 4)) & 0xF for i in range(4)]

        def sim_move(l):
            res = []
            sc = 0
            non_zero = [x for x in l if x != 0]
            skip = False
            for i in range(len(non_zero)):
                if skip: skip = False; continue
                if i < len(non_zero) - 1 and non_zero[i] == non_zero[i+1]:
                    new_val = non_zero[i] + 1
                    res.append(new_val)
                    sc += (1 << new_val)
                    skip = True
                else:
                    res.append(non_zero[i])
            while len(res) < 4: res.append(0)
            return res, sc

        # Tính toán Move Left
        new_line_l, score_l = sim_move(line)
        _ROW_LEFT_TABLE[row] = (new_line_l[0] | (new_line_l[1] << 4) | 
                                (new_line_l[2] << 8) | (new_line_l[3] << 12))
        _SCORE_TABLE[row] = score_l

        # Tính toán Move Right (Reverse -> Move Left -> Reverse)
        new_line_r, _ = sim_move(line[::-1]) # Reverse input
        new_line_r = new_line_r[::-1]       # Reverse output
        _ROW_RIGHT_TABLE[row] = (new_line_r[0] | (new_line_r[1] << 4) | 
                                 (new_line_r[2] << 8) | (new_line_r[3] << 12))
    
    _TABLES_INIT = True


class BaseSolver(ABC):
    def __init__(self, depth=3, weights=None):
        self.depth = depth
        self.evaluator = Heuristics(weights)
        
        if (not _TABLES_INIT):
            _init_tables()

    @abstractmethod
    def get_best_move(self, grid):
        pass

    def simulate_move(self, board, direction):
        # 1. Chuyển Grid -> Bitboard
        old_board = board
        score = 0
        
        # 2. Thực hiện Logic trên Bitboard
        if direction == 0:   # LEFT
            board, score = self._lut_move_left(board)
        elif direction == 1: # RIGHT
            board, score = self._lut_move_right(board)
        elif direction == 2: # UP
            # Up = Transpose -> Move Left -> Transpose
            t = self._transpose(board)
            t, score = self._lut_move_left(t)
            board = self._transpose(t)
        elif direction == 3: # DOWN
            # Down = Transpose -> Move Right -> Transpose
            t = self._transpose(board)
            t, score = self._lut_move_right(t)
            board = self._transpose(t)

        # 3. Kiểm tra thay đổi
        changed = (board != old_board)

        return board, score, changed

    # --- BITBOARD HELPERS ---

    def grid_to_bitboard(self, grid):
        board = 0
        shift = 0
        for r in range(4):
            for c in range(4):
                val = grid[r][c]
                power = int(math.log2(val)) if val > 0 else 0
                board |= (power << shift)
                shift += 4
        return board

    def bitboard_to_grid(self, board):
        grid = [[0]*4 for _ in range(4)]
        for r in range(4):
            for c in range(4):
                shift = (r * 4 + c) * 4
                power = (board >> shift) & 0xF
                grid[r][c] = (1 << power) if power > 0 else 0
        return grid

    # --- INTERNAL LOOKUP LOGIC ---

    def _lut_move_left(self, board):
        r0 = board & 0xFFFF
        r1 = (board >> 16) & 0xFFFF
        r2 = (board >> 32) & 0xFFFF
        r3 = (board >> 48) & 0xFFFF
        
        new_board = (
            _ROW_LEFT_TABLE[r0] | 
            (_ROW_LEFT_TABLE[r1] << 16) | 
            (_ROW_LEFT_TABLE[r2] << 32) | 
            (_ROW_LEFT_TABLE[r3] << 48)
        )
        
        score = (
            _SCORE_TABLE[r0] + 
            _SCORE_TABLE[r1] + 
            _SCORE_TABLE[r2] + 
            _SCORE_TABLE[r3]
        )
        return new_board, score

    def _lut_move_right(self, board):
        r0 = board & 0xFFFF
        r1 = (board >> 16) & 0xFFFF
        r2 = (board >> 32) & 0xFFFF
        r3 = (board >> 48) & 0xFFFF
        
        new_board = (
            _ROW_RIGHT_TABLE[r0] | 
            (_ROW_RIGHT_TABLE[r1] << 16) | 
            (_ROW_RIGHT_TABLE[r2] << 32) | 
            (_ROW_RIGHT_TABLE[r3] << 48)
        )
        
        score = (
            _SCORE_TABLE[r0] + 
            _SCORE_TABLE[r1] + 
            _SCORE_TABLE[r2] + 
            _SCORE_TABLE[r3]
        )
        return new_board, score

    def _transpose(self, x):
        a1 = x & 0xF0F00F0FF0F00F0F;
        a2 = x & 0x0000F0F00000F0F0;
        a3 = x & 0x0F0F00000F0F0000;
        a = a1 | (a2 << 12) | (a3 >> 12);
        b1 = a & 0xFF00FF0000FF00FF;
        b2 = a & 0x00FF00FF00000000;
        b3 = a & 0x00000000FF00FF00;
        return b1 | (b2 >> 24) | (b3 << 24);


