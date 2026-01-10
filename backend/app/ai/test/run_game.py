import random
import time
import os
import sys

# Import class MinimaxSolver từ file minimax.py bạn vừa lưu
try:
    from minimax import ExpectimaxSolver
except ImportError:
    print("Lỗi: Không tìm thấy file 'minimax.py'. Hãy chắc chắn 2 file ở cùng thư mục.")
    sys.exit(1)

# --- GAME ENGINE ĐƠN GIẢN (Để giả lập môi trường chơi) ---
class Game2048:
    def __init__(self):
        self.grid = [[0]*4 for _ in range(4)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.grid[r][c] == 0]
        if not empty_cells: return
        r, c = random.choice(empty_cells)
        # Tỉ lệ: 90% ra số 2, 10% ra số 4
        self.grid[r][c] = 4 if random.random() > 0.9 else 2

    def get_max_tile(self):
        return max(max(row) for row in self.grid)

    # Logic di chuyển ma trận (Giống hệt luật game gốc)
    def compress(self, grid):
        new_grid = [[0]*4 for _ in range(4)]
        for r in range(4):
            pos = 0
            for c in range(4):
                if grid[r][c] != 0:
                    new_grid[r][pos] = grid[r][c]
                    pos += 1
        return new_grid

    def merge(self, grid):
        score = 0
        for r in range(4):
            for c in range(3):
                if grid[r][c] != 0 and grid[r][c] == grid[r][c+1]:
                    grid[r][c] *= 2
                    score += grid[r][c]
                    grid[r][c+1] = 0
        return grid, score

    def reverse(self, grid):
        return [row[::-1] for row in grid]

    def transpose(self, grid):
        return [list(row) for row in zip(*grid)]

    def move(self, direction):
        """
        0: Left, 1: Right, 2: Up, 3: Down
        Trả về (grid_mới, có_thay_đổi_không)
        """
        temp_grid = [row[:] for row in self.grid]
        
        if direction == 0:   # Left
            temp_grid = self.compress(temp_grid)
            temp_grid, _ = self.merge(temp_grid)
            temp_grid = self.compress(temp_grid)
        elif direction == 1: # Right
            temp_grid = self.reverse(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid, _ = self.merge(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid = self.reverse(temp_grid)
        elif direction == 2: # Up
            temp_grid = self.transpose(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid, _ = self.merge(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid = self.transpose(temp_grid)
        elif direction == 3: # Down
            temp_grid = self.transpose(temp_grid)
            temp_grid = self.reverse(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid, _ = self.merge(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid = self.reverse(temp_grid)
            temp_grid = self.transpose(temp_grid)

        changed = (temp_grid != self.grid)
        if changed:
            self.grid = temp_grid
        return changed

    def print_board(self, move_count, last_move_dir):
        # Xóa màn hình terminal (Windows: cls, Mac/Linux: clear)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        dirs = {0: "LEFT", 1: "RIGHT", 2: "UP", 3: "DOWN", -1: "START"}
        print(f"--- MOVES: {move_count} | LAST: {dirs.get(last_move_dir, 'N/A')} ---")
        print("-" * 29)
        for row in self.grid:
            # Format căn lề cho đẹp
            print(f"| {row[0]:4} | {row[1]:4} | {row[2]:4} | {row[3]:4} |")
        print("-" * 29)
        print(f"Max Tile: {self.get_max_tile()}")

# --- HÀM MAIN CHẠY THỬ ---
def main():
    game = Game2048()
    
    # Khởi tạo AI với độ sâu mong muốn (ví dụ depth=6 để khá thông minh)
    # Trọng số có thể để None (mặc định) hoặc tự chỉnh
    ai_weights = {
        'monotonic': 15,
        'smoothness': 1.5,
        'free_tiles': 2.7,
        'max_tile': 1.0
    }
    solver = ExpectimaxSolver(depth=3, weights=ai_weights)
    
    move_count = 0
    last_move = -1
    
    print("Đang khởi động AI... (Đợi tính toán bảng Bitboard)")
    
    while True:
        # 1. In trạng thái hiện tại
        game.print_board(move_count, last_move)
        
        # 2. AI suy nghĩ
        # Truyền bản sao của grid để AI không sửa vào grid thật
        grid_copy = [row[:] for row in game.grid]
        best_move = solver.get_best_move(grid_copy)
        
        # 3. Kiểm tra kết quả
        if best_move == -1:
            print("\n=== GAME OVER ===")
            print("AI đầu hàng (Không còn nước đi hợp lệ).")
            break
            
        # 4. Thực hiện nước đi
        changed = game.move(best_move)
        
        if changed:
            game.add_random_tile()
            move_count += 1
            last_move = best_move
            # time.sleep(0.05) # Bỏ comment nếu muốn xem chậm lại
        else:
            print("\n=== GAME OVER ===")
            print("AI bị kẹt (Loop vô tận hoặc lỗi logic).")
            break

    # KẾT QUẢ CUỐI CÙNG
    print(f"\n>>> KẾT QUẢ CUỐI CÙNG: {game.get_max_tile()} <<<")

if __name__ == "__main__":
    main()