import math

class Heuristics:
    def __init__(self, weights=None):
        # 1. Cấu hình trọng số
        if weights:
            self.w_mono = weights.get('monotonic', 1.0)
            self.w_smooth = weights.get('smoothness', 0.1)
            self.w_free = weights.get('free_tiles', 2.7)
            self.w_max = weights.get('max_tile', 1.0)
        else:
            self.w_mono = 1.0
            self.w_smooth = 0.1
            self.w_free = 2.7
            self.w_max = 1.0

        # 2. Bảng tra cứu (Pre-computed Lookup Table)
        # Mỗi phần tử trong mảng 65536 sẽ lưu tuple:
        # (smoothness, mono_inc, mono_dec, empty_count, max_val)
        self.row_table = [None] * 65536 
        
        # 3. Tính toán bảng ngay khi khởi tạo
        self._init_tables()

    def _init_tables(self):
        """
        Tính toán trước các chỉ số Heuristic cho mọi trường hợp hàng (0 -> 65535)
        """
        for row in range(65536):
            # Giải nén 16-bit int thành 4 ô (mỗi ô 4 bit đại diện số mũ)
            # Ví dụ: row=0x1234 -> line=[4, 3, 2, 1] (Thứ tự bit thấp đến cao)
            line = [
                (row >> 0) & 0xF,
                (row >> 4) & 0xF,
                (row >> 8) & 0xF,
                (row >> 12) & 0xF
            ]
            
            # Chuyển từ Power (số mũ) sang Value (giá trị thực)
            # 0->0, 1->2, 2->4, ...
            values = [(1 << p) if p > 0 else 0 for p in line]

            # --- 1. Max Tile ---
            max_val = max(values)
            
            # --- 2. Empty Cells ---
            empty = line.count(0)

            # --- 3. Smoothness (Theo logic log2 của code cũ) ---
            smooth = 0
            for i in range(3):
                if values[i] != 0 and values[i+1] != 0:
                    # Vì line lưu số mũ (log2) nên trừ trực tiếp line
                    smooth -= abs(line[i] - line[i+1])

            # --- 4. Monotonicity (Theo Value thực) ---
            mono_left = 0  # Giảm dần (Totals[0])
            mono_right = 0 # Tăng dần (Totals[1])
            
            for i in range(3):
                curr = values[i]
                nxt = values[i+1]
                if curr > nxt:
                    mono_left += nxt - curr # Điểm phạt (số âm hoặc dương tùy logic, ở code cũ là cộng vào totals)
                elif nxt > curr:
                    mono_right += curr - nxt

            # Lưu vào bảng
            self.row_table[row] = (smooth, mono_left, mono_right, empty, max_val)

    def get_score(self, board):

        # 1. Tách các hàng (Rows)
        r0 = board & 0xFFFF
        r1 = (board >> 16) & 0xFFFF
        r2 = (board >> 32) & 0xFFFF
        r3 = (board >> 48) & 0xFFFF

        # 2. Xoay bàn cờ để lấy các cột (Cols)
        t_board = self._transpose_bitboard(board)
        c0 = t_board & 0xFFFF
        c1 = (t_board >> 16) & 0xFFFF
        c2 = (t_board >> 32) & 0xFFFF
        c3 = (t_board >> 48) & 0xFFFF

        # 3. Tra bảng (Lấy dữ liệu thô)
        d_r0 = self.row_table[r0]; d_c0 = self.row_table[c0]
        d_r1 = self.row_table[r1]; d_c1 = self.row_table[c1]
        d_r2 = self.row_table[r2]; d_c2 = self.row_table[c2]
        d_r3 = self.row_table[r3]; d_c3 = self.row_table[c3]

        # 4. TỔNG HỢP ĐIỂM (THEO LOGIC BẠN YÊU CẦU)

        # Smoothness: Tổng Hàng + Tổng Cột
        smooth_score = (d_r0[0] + d_r1[0] + d_r2[0] + d_r3[0] + 
                        d_c0[0] + d_c1[0] + d_c2[0] + d_c3[0])

        # Monotonicity: max(L, R) + max(U, D)
        # Hàng (Left/Right)
        tot_mono_l = d_r0[1] + d_r1[1] + d_r2[1] + d_r3[1]
        tot_mono_r = d_r0[2] + d_r1[2] + d_r2[2] + d_r3[2]
        # Cột (Up/Down)
        tot_mono_u = d_c0[1] + d_c1[1] + d_c2[1] + d_c3[1]
        tot_mono_d = d_c0[2] + d_c1[2] + d_c2[2] + d_c3[2]
        
        mono_score = max(tot_mono_l, tot_mono_r) + max(tot_mono_u, tot_mono_d)

        # Empty Cells: Tổng các hàng (Cột cũng vậy, chỉ cần lấy 1 chiều)
        empty_score = d_r0[3] + d_r1[3] + d_r2[3] + d_r3[3]

        # Max Tile: Max của các hàng
        max_tile_score = max(d_r0[4], d_r1[4], d_r2[4], d_r3[4])

        return (mono_score * self.w_mono +
                smooth_score * self.w_smooth +
                empty_score * self.w_free +
                max_tile_score * self.w_max)

    def _transpose_bitboard(self, x):
        a1 = x & 0xF0F00F0FF0F00F0F;
        a2 = x & 0x0000F0F00000F0F0;
        a3 = x & 0x0F0F00000F0F0000;
        a = a1 | (a2 << 12) | (a3 >> 12);
        b1 = a & 0xFF00FF0000FF00FF;
        b2 = a & 0x00FF00FF00000000;
        b3 = a & 0x00000000FF00FF00;
        return b1 | (b2 >> 24) | (b3 << 24);
