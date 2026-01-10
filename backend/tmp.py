import numpy
import math

def grid_to_bitboard(grid):
        board = 0
        for r in range(4):
            for c in range(4):
                val = grid[r][c]
                power = int(math.log2(val)) if val > 0 else 0
                board |= (power << ((r * 4 + c) * 4))
        return board

# --- KHAI BÁO BIẾN TOÀN CỤC ---
ROW_LEFT_TABLE = [0] * 65536
ROW_RIGHT_TABLE = [0] * 65536

# col_up thực chất logic y hệt row_left (dồn về phía chỉ số nhỏ)
# col_down thực chất logic y hệt row_right (dồn về phía chỉ số lớn)
# Ta gán tham chiếu để code dễ đọc mà không tốn thêm RAM
COL_UP_TABLE = ROW_LEFT_TABLE
COL_DOWN_TABLE = ROW_RIGHT_TABLE

TABLES_INITIALIZED = False

# --- HÀM HELPER (CHỈ DÙNG ĐỂ TẠO BẢNG) ---
def _calculate_single_row_left(row):
    """Logic dồn bit thủ công (như bạn đã duyệt ở bước trước)"""
    p0 = (row >> 0)  & 0xF
    p1 = (row >> 4)  & 0xF
    p2 = (row >> 8)  & 0xF
    p3 = (row >> 12) & 0xF

    # DỒN SỐ (Compact)
    if p0 == 0: p0, p1, p2, p3 = p1, p2, p3, 0
    if p1 == 0: p1, p2, p3     = p2, p3, 0
    if p2 == 0: p2, p3         = p3, 0
    if p0 == 0: p0, p1, p2, p3 = p1, p2, p3, 0
    if p1 == 0: p1, p2, p3     = p2, p3, 0
    if p0 == 0: p0, p1, p2, p3 = p1, p2, p3, 0

    # GỘP SỐ (Merge)
    if p0 != 0 and p0 == p1:
        if p0 < 15: p0 += 1
        p1, p2, p3 = p2, p3, 0
        if p1 != 0 and p1 == p2:
            if p1 < 15: p1 += 1
            p2 = 0
    elif p1 != 0 and p1 == p2:
        if p1 < 15: p1 += 1
        p2, p3 = p3, 0
    elif p2 != 0 and p2 == p3:
        if p2 < 15: p2 += 1
        p3 = 0

    return (p0) | (p1 << 4) | (p2 << 8) | (p3 << 12)

def _reverse_row_bits(row):
    """Đảo ngược hàng: [p3, p2, p1, p0] -> [p0, p1, p2, p3]"""
    return ((row & 0xF) << 12) | ((row & 0xF0) << 4) | ((row & 0xF00) >> 4) | ((row & 0xF000) >> 12)

# --- HÀM KHỞI TẠO CHÍNH ---
def init_lookup_tables():
    global TABLES_INITIALIZED
    if TABLES_INITIALIZED:
        return

    print("Dang khoi tao bang tra cuu (Transposition Tables)...")
    
    for row in range(65536):
        # 1. Tính toán Move Left
        left_result = _calculate_single_row_left(row)
        ROW_LEFT_TABLE[row] = left_result
        
        # 2. Tính toán Move Right
        # Logic: Đảo ngược hàng -> Move Left -> Đảo ngược lại
        reversed_row = _reverse_row_bits(row)
        left_on_reversed = _calculate_single_row_left(reversed_row)
        right_result = _reverse_row_bits(left_on_reversed)
        ROW_RIGHT_TABLE[row] = right_result
        
    TABLES_INITIALIZED = True
    print("Khoi tao xong!")

# Gọi hàm này 1 lần duy nhất khi chương trình bắt đầu
init_lookup_tables()

def transpose_grid(board):
    """Chuyển vị bàn cờ (Hàng <-> Cột)"""
    # Giải nén
    c0 = (board >> 0)  & 0xF; c1 = (board >> 4)  & 0xF; c2 = (board >> 8)  & 0xF; c3 = (board >> 12) & 0xF
    c4 = (board >> 16) & 0xF; c5 = (board >> 20) & 0xF; c6 = (board >> 24) & 0xF; c7 = (board >> 28) & 0xF
    c8 = (board >> 32) & 0xF; c9 = (board >> 36) & 0xF; c10= (board >> 40) & 0xF; c11= (board >> 44) & 0xF
    c12= (board >> 48) & 0xF; c13= (board >> 52) & 0xF; c14= (board >> 56) & 0xF; c15= (board >> 60) & 0xF
    
    # Sắp xếp lại
    return (
        c0 | (c4<<4) | (c8<<8) | (c12<<12) |
        (c1<<16) | (c5<<20) | (c9<<24) | (c13<<28) |
        (c2<<32) | (c6<<36) | (c10<<40) | (c14<<44) |
        (c3<<48) | (c7<<52) | (c11<<56) | (c15<<60)
    )

def move_grid_left(board):
    """Tra bảng ROW_LEFT_TABLE"""
    # Tách 4 hàng (mỗi hàng 16 bit)
    r0 = board & 0xFFFF
    r1 = (board >> 16) & 0xFFFF
    r2 = (board >> 32) & 0xFFFF
    r3 = (board >> 48) & 0xFFFF
    
    # Tra bảng O(1)
    return (
        ROW_LEFT_TABLE[r0] |
        (ROW_LEFT_TABLE[r1] << 16) |
        (ROW_LEFT_TABLE[r2] << 32) |
        (ROW_LEFT_TABLE[r3] << 48)
    )

def move_grid_right(board):
    """Tra bảng ROW_RIGHT_TABLE"""
    r0 = board & 0xFFFF
    r1 = (board >> 16) & 0xFFFF
    r2 = (board >> 32) & 0xFFFF
    r3 = (board >> 48) & 0xFFFF
    
    return (
        ROW_RIGHT_TABLE[r0] |
        (ROW_RIGHT_TABLE[r1] << 16) |
        (ROW_RIGHT_TABLE[r2] << 32) |
        (ROW_RIGHT_TABLE[r3] << 48)
    )

def move_grid_up(board):
    """
    Chuyển vị -> Tra bảng COL_UP (thực ra là ROW_LEFT) -> Chuyển vị ngược
    """
    # 1. Biến cột thành hàng
    t_board = transpose_grid(board)
    
    # 2. Xử lý như move_left (vì cột đã nằm ngang)
    r0 = t_board & 0xFFFF
    r1 = (t_board >> 16) & 0xFFFF
    r2 = (t_board >> 32) & 0xFFFF
    r3 = (t_board >> 48) & 0xFFFF
    
    moved_t_board = (
        COL_UP_TABLE[r0] | # Dùng COL_UP_TABLE (alias của ROW_LEFT)
        (COL_UP_TABLE[r1] << 16) |
        (COL_UP_TABLE[r2] << 32) |
        (COL_UP_TABLE[r3] << 48)
    )
    
    # 3. Chuyển vị ngược lại
    return transpose_grid(moved_t_board)

def move_grid_down(board):
    """
    Chuyển vị -> Tra bảng COL_DOWN (thực ra là ROW_RIGHT) -> Chuyển vị ngược
    """
    t_board = transpose_grid(board)
    
    r0 = t_board & 0xFFFF
    r1 = (t_board >> 16) & 0xFFFF
    r2 = (t_board >> 32) & 0xFFFF
    r3 = (t_board >> 48) & 0xFFFF
    
    moved_t_board = (
        COL_DOWN_TABLE[r0] | # Dùng COL_DOWN_TABLE (alias của ROW_RIGHT)
        (COL_DOWN_TABLE[r1] << 16) |
        (COL_DOWN_TABLE[r2] << 32) |
        (COL_DOWN_TABLE[r3] << 48)
    )
    
    return transpose_grid(moved_t_board)

def print_bitboard(board):
    """
    In Bitboard 64-bit ra màn hình dưới dạng bảng 4x4.
    """
    print("-" * 29)
    # Duyệt qua 4 hàng (Mỗi hàng 16 bit)
    for r in range(4):
        # r=0: 16 bit thấp nhất (Hàng 0)
        row_bits = (board >> (r * 16)) & 0xFFFF
        
        row_values = []
        # Duyệt qua 4 ô trong hàng (Mỗi ô 4 bit)
        for c in range(4):
            # c=0: 4 bit thấp nhất của hàng (Cột 0 - Trái)
            power = (row_bits >> (c * 4)) & 0xF
            
            # Chuyển từ Số mũ (Power) sang Giá trị (Value)
            # Ví dụ: 1 -> 2, 2 -> 4, 10 -> 1024
            val = (1 << power) if power > 0 else 0
            row_values.append(val)
            
        # In ra định dạng bảng căn lề phải
        print(f"| {row_values[0]:4} | {row_values[1]:4} | {row_values[2]:4} | {row_values[3]:4} |")
        
    print("-" * 29)

print(([[2, 2, 0, 0], [0, 4, 32768, 0], [0, 8, 16, 0], [2, 2, 2, 2]]))
print_bitboard(move_grid_right(grid_to_bitboard([[2, 2, 0, 0], [0, 4, 32768, 0], [0, 8, 16, 0], [2, 2, 2, 2]])))


def _transpose(x):
    a1 = x & 0xF0F00F0FF0F00F0F;
    a2 = x & 0x0000F0F00000F0F0;
    a3 = x & 0x0F0F00000F0F0000;
    a = a1 | (a2 << 12) | (a3 >> 12);
    b1 = a & 0xFF00FF0000FF00FF;
    b2 = a & 0x00FF00FF00000000;
    b3 = a & 0x00000000FF00FF00;
    return b1 | (b2 >> 24) | (b3 << 24);

print(_transpose(33563649))

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

l = [0, 0, 0, 0]
new_l, _ = sim_move(l)
print(new_l)
print((new_l[0] | (new_l[1] << 4) | 
                                (new_l[2] << 8) | (new_l[3] << 12)))
