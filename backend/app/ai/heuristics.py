import math

# --- 1. BẢNG CỐ ĐỊNH (SNAKE / GRADIENT) ---
# Trọng số cực lớn, không đổi, dùng để định hình cấu trúc
_TABLE_GRADIENT_0 = [0.0] * 65536
_TABLE_GRADIENT_1 = [0.0] * 65536
_TABLE_GRADIENT_2 = [0.0] * 65536
_TABLE_GRADIENT_3 = [0.0] * 65536

# --- 2. BẢNG TÙY CHỈNH (USER HEURISTICS) ---
# Giá trị thô (Raw), sẽ nhân với trọng số người dùng khi chạy
_TABLE_MERGES = [0.0] * 65536
_TABLE_FREE   = [0.0] * 65536
_TABLE_SMOOTH = [0.0] * 65536
_TABLE_MONO_LEFT  = [0.0] * 65536
_TABLE_MONO_RIGHT = [0.0] * 65536

# Cờ kiểm tra khởi tạo
_TABLES_INITIALIZED = False

class Heuristics:
    def __init__(self, weights=None):
        # Cấu hình trọng số từ Frontend
        # Mặc định ta để các trọng số phụ này nhỏ để không phá vỡ Snake
        if weights:
            self.w_mono   = weights.get('monotonic', 1.0)
            self.w_smooth = weights.get('smoothness', 0.1)
            self.w_free   = weights.get('free_tiles', 10.0)
            self.w_merges = weights.get('merges', 1.0)
        else:
            self.w_mono   = 1.0
            self.w_smooth = 0.1
            self.w_free   = 10.0
            self.w_merges = 1.0
            
        # Trọng số Snake cố định (Backbone) - Hệ số 1.0 vì bản thân bảng đã rất lớn
        self.w_snake = 1.0 

        global _TABLES_INITIALIZED
        if not _TABLES_INITIALIZED:
            self._init_tables()
            _TABLES_INITIALIZED = True

    def _init_tables(self):
        """
        Khởi tạo TẤT CẢ các bảng trong 1 vòng lặp duy nhất để tối ưu khởi động.
        """
        # Ma trận Snake (Cố định)
        SNAKE_W = [
            [65536, 32768, 16384, 8192], 
            [512,   1024,  2048,  4096], 
            [256,   128,   64,    32],   
            [2,     4,     8,     16]    
        ]

        for row in range(65536):
            # 1. Giải nén row 16-bit
            line = [(row >> (i*4)) & 0xF for i in range(4)]
            # Giá trị thực (2^k)
            values = [(1 << p) if p > 0 else 0 for p in line]
            
            # --- A. TÍNH GRADIENT (SNAKE) ---
            # Tính sẵn cho 4 vị trí hàng
            for r_idx in range(4):
                g_score = 0
                for c_idx in range(4):
                    g_score += values[c_idx] * SNAKE_W[r_idx][c_idx]
                
                if r_idx == 0: _TABLE_GRADIENT_0[row] = g_score
                elif r_idx == 1: _TABLE_GRADIENT_1[row] = g_score
                elif r_idx == 2: _TABLE_GRADIENT_2[row] = g_score
                elif r_idx == 3: _TABLE_GRADIENT_3[row] = g_score

            # --- B. TÍNH FREE TILES ---
            _TABLE_FREE[row] = line.count(0)

            # --- C. TÍNH SMOOTHNESS ---
            smooth = 0
            for i in range(3):
                if values[i] != 0 and values[i+1] != 0:
                    smooth -= abs(line[i] - line[i+1]) # Dùng log (line) hay value tùy bạn, ở đây dùng log cho nhẹ
            _TABLE_SMOOTH[row] = smooth

            # --- D. TÍNH MERGES (Logic của bạn) ---
            merges = 0
            prev = 0
            counter = 0
            for i in range(4):
                rank = line[i]
                if rank != 0:
                    if prev == rank:
                        counter += 1
                    elif counter > 0:
                        merges += 1 + counter
                        counter = 0
                    prev = rank
            if counter > 0: merges += 1 + counter
            _TABLE_MERGES[row] = merges

            # --- E. TÍNH MONOTONICITY ---
            mono_left = 0; mono_right = 0
            for i in range(3):
                curr = values[i]; nxt = values[i+1]
                if curr > nxt: mono_left += (nxt - curr)
                elif nxt > curr: mono_right += (curr - nxt)
            _TABLE_MONO_LEFT[row] = mono_left
            _TABLE_MONO_RIGHT[row] = mono_right

    def get_score(self, board):
        # 1. Tách hàng
        r0 = board & 0xFFFF
        r1 = (board >> 16) & 0xFFFF
        r2 = (board >> 32) & 0xFFFF
        r3 = (board >> 48) & 0xFFFF

        # 2. Transpose lấy cột
        a1 = board & 0xF0F00F0FF0F00F0F
        a2 = board & 0x0000F0F00000F0F0
        a3 = board & 0x0F0F00000F0F0000
        a = a1 | (a2 << 12) | (a3 >> 12)
        b1 = a & 0xFF00FF0000FF00FF
        b2 = a & 0x00FF00FF00000000
        b3 = a & 0x00000000FF00FF00
        t_board = b1 | (b2 >> 24) | (b3 << 24)

        c0 = t_board & 0xFFFF; c1 = (t_board >> 16) & 0xFFFF
        c2 = (t_board >> 32) & 0xFFFF; c3 = (t_board >> 48) & 0xFFFF

        # --- PHẦN 1: CORE SCORE (SNAKE) - Không nhân trọng số người dùng ---
        snake_score = (_TABLE_GRADIENT_0[r0] + _TABLE_GRADIENT_1[r1] + 
                       _TABLE_GRADIENT_2[r2] + _TABLE_GRADIENT_3[r3])

        # --- PHẦN 2: USER HEURISTICS - Nhân trọng số người dùng ---
        
        # Free Tiles (Chỉ cần tính trên hàng)
        raw_free = _TABLE_FREE[r0] + _TABLE_FREE[r1] + _TABLE_FREE[r2] + _TABLE_FREE[r3]
        
        # Merges (Hàng + Cột)
        raw_merges = (_TABLE_MERGES[r0] + _TABLE_MERGES[r1] + _TABLE_MERGES[r2] + _TABLE_MERGES[r3] +
                      _TABLE_MERGES[c0] + _TABLE_MERGES[c1] + _TABLE_MERGES[c2] + _TABLE_MERGES[c3])

        # Smoothness (Hàng + Cột)
        raw_smooth = (_TABLE_SMOOTH[r0] + _TABLE_SMOOTH[r1] + _TABLE_SMOOTH[r2] + _TABLE_SMOOTH[r3] +
                      _TABLE_SMOOTH[c0] + _TABLE_SMOOTH[c1] + _TABLE_SMOOTH[c2] + _TABLE_SMOOTH[c3])

        # Monotonicity
        m_row = max(
            _TABLE_MONO_LEFT[r0] + _TABLE_MONO_LEFT[r1] + _TABLE_MONO_LEFT[r2] + _TABLE_MONO_LEFT[r3],
            _TABLE_MONO_RIGHT[r0] + _TABLE_MONO_RIGHT[r1] + _TABLE_MONO_RIGHT[r2] + _TABLE_MONO_RIGHT[r3]
        )
        m_col = max(
            _TABLE_MONO_LEFT[c0] + _TABLE_MONO_LEFT[c1] + _TABLE_MONO_LEFT[c2] + _TABLE_MONO_LEFT[c3],
            _TABLE_MONO_RIGHT[c0] + _TABLE_MONO_RIGHT[c1] + _TABLE_MONO_RIGHT[c2] + _TABLE_MONO_RIGHT[c3]
        )
        raw_mono = m_row + m_col

        # TỔNG HỢP
        # Snake đóng vai trò chính (vì giá trị bảng nó rất lớn: 65536...)
        # Các chỉ số kia đóng vai trò phụ trợ (Tie-breaker)
        total_score = (snake_score * self.w_snake + 
                       raw_free * self.w_free + 
                       raw_merges * self.w_merges + 
                       raw_smooth * self.w_smooth + 
                       raw_mono * self.w_mono)
        
        return total_score

    # Hàm hỗ trợ cho Benchmark
    def get_empty_cells(self, grid):
        if isinstance(grid, int):
            cells = []
            temp = grid
            for i in range(16):
                if (temp & 0xF) == 0: cells.append((i // 4, i % 4))
                temp >>= 4
            return cells
        else:
            return [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]