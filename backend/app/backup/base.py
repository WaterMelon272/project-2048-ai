import math
from abc import ABC, abstractmethod
from ..heuristics import Heuristics

# --- GLOBAL LOOKUP TABLES (CACHE) ---
# Được tính toán 1 lần duy nhất khi chạy chương trình
_TABLES_INIT = False
_ROW_LEFT_TABLE = [0] * 65536
_ROW_RIGHT_TABLE = [0] * 65536
_SCORE_TABLE = [0] * 65536

def _init_tables():
    """Khởi tạo bảng tra cứu nước đi (Move Tables)"""
    global _TABLES_INIT
    if _TABLES_INIT: return

    for row in range(65536):
        # 1. Giải nén hàng 16-bit thành list 4 phần tử (số mũ)
        line = [(row >> (i * 4)) & 0xF for i in range(4)]

        # 2. Logic Move Left (Dồn trái & Gộp)
        # Input: [1, 1, 0, 2] (tức là 2, 2, 0, 4)
        # Output: [2, 2, 0, 0] (tức là 4, 4, 0, 0)
        def sim_move(l):
            res = []
            sc = 0
            non_zero = [x for x in l if x != 0]
            skip = False
            for i in range(len(non_zero)):
                if skip: skip = False; continue
                if i < len(non_zero) - 1 and non_zero[i] == non_zero[i+1]:
                    # Gộp: power tăng lên 1 (2^k + 2^k = 2^(k+1))
                    new_val = non_zero[i] + 1
                    res.append(new_val)
                    # Điểm cộng = Giá trị mới (2^new_val)
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
        
        # Đảm bảo bảng tra cứu đã sẵn sàng
        _init_tables()

    @abstractmethod
    def get_best_move(self, grid):
        """
        Các class con (Minimax, Expectimax) BẮT BUỘC phải override hàm này.
        """
        pass

    def simulate_move(self, grid, direction):
        """
        Giả lập nước đi trên bàn cờ.
        Input: Grid 2D (List[List[int]])
        Logic: Convert -> Bitboard -> Lookup Tables -> Re-convert
        Output: (new_grid, score_gained, changed)
        """
        # 1. Chuyển Grid -> Bitboard
        old_board = board
        score = 0
        
        # 2. Thực hiện Logic trên Bitboard (Tra bảng cực nhanh)
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

    # --- BITBOARD HELPERS (Public cho class con dùng) ---

    def grid_to_bitboard(self, grid):
        """Convert Grid 2D sang số nguyên 64-bit"""
        board = 0
        shift = 0
        for r in range(4):
            for c in range(4):
                val = grid[r][c]
                # Log2: 2->1, 4->2, 0->0
                power = int(math.log2(val)) if val > 0 else 0
                board |= (power << shift)
                shift += 4
        return board

    def bitboard_to_grid(self, board):
        """Convert số nguyên 64-bit sang Grid 2D"""
        grid = [[0]*4 for _ in range(4)]
        for r in range(4):
            for c in range(4):
                shift = (r * 4 + c) * 4
                power = (board >> shift) & 0xF
                grid[r][c] = (1 << power) if power > 0 else 0
        return grid

    # --- INTERNAL LOOKUP LOGIC ---

    def _lut_move_left(self, board):
        """Tra bảng để di chuyển sang trái cho cả 4 hàng cùng lúc"""
        # Tách 4 hàng (mỗi hàng 16 bit)
        r0 = board & 0xFFFF
        r1 = (board >> 16) & 0xFFFF
        r2 = (board >> 32) & 0xFFFF
        r3 = (board >> 48) & 0xFFFF
        
        # Tra bảng Move
        new_board = (
            _ROW_LEFT_TABLE[r0] | 
            (_ROW_LEFT_TABLE[r1] << 16) | 
            (_ROW_LEFT_TABLE[r2] << 32) | 
            (_ROW_LEFT_TABLE[r3] << 48)
        )
        
        # Tra bảng Score
        score = (
            _SCORE_TABLE[r0] + 
            _SCORE_TABLE[r1] + 
            _SCORE_TABLE[r2] + 
            _SCORE_TABLE[r3]
        )
        return new_board, score

    def _lut_move_right(self, board):
        """Tra bảng để di chuyển sang phải cho cả 4 hàng cùng lúc"""
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

    def get_moves_bitboard(self, board):
        """
        Trả về danh sách các nước đi hợp lệ dưới dạng Bitboard.
        Dùng cho Minimax/Expectimax để không phải convert qua lại.
        Output: [(direction, new_board_int, score), ...]
        """
        moves = []

        # Left (0)
        nb, sc = self._lut_move_left(board)
        if nb != board: moves.append((0, nb, sc))
        
        # Right (1)
        nb, sc = self._lut_move_right(board)
        if nb != board: moves.append((1, nb, sc))
        
        # Up (2) & Down (3) cần Transpose
        tb = self._transpose(board)
        
        # Up -> Move Left trên Transpose
        ntb, sc = self._lut_move_left(tb)

        if ntb != tb:
            moves.append((2, self._transpose(ntb), sc))
            
        # Down -> Move Right trên Transpose
        ntb, sc = self._lut_move_right(tb)
        if ntb != tb:
            moves.append((3, self._transpose(ntb), sc))

        return moves

