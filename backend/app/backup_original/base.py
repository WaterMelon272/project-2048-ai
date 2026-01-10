from abc import ABC, abstractmethod
from ..heuristics import Heuristics

class BaseSolver(ABC):
    def __init__(self, depth=3, weights=None):
        self.depth = depth
        self.evaluator = Heuristics(weights)

    @abstractmethod
    def get_best_move(self, grid):
        """
        Các class con (Minimax, Expectimax) BẮT BUỘC phải override hàm này.
        """
        pass

    def simulate_move(self, grid, direction):
        """
        Giả lập nước đi trên bàn cờ.
        Input: 
            grid: Bàn cờ hiện tại (List[List[int]])
            direction: 0 (Left), 1 (Right), 2 (Up), 3 (Down) - (Theo quy ước của frontend bạn)
        Output: 
            (new_grid, score_gained, changed)
        """
        # 1. Tạo bản sao bàn cờ để không ảnh hưởng dữ liệu thật
        temp_grid = [row[:] for row in grid]
        score = 0
        changed = False

        # 2. Xử lý theo hướng (Dùng ma trận để tái sử dụng logic dồn sang trái)
        if direction == 0:   # LEFT
            temp_grid, score, changed = self._move_left(temp_grid)
        elif direction == 1: # RIGHT
            temp_grid = self._reverse(temp_grid)
            temp_grid, score, changed = self._move_left(temp_grid)
            temp_grid = self._reverse(temp_grid)
        elif direction == 2: # UP
            temp_grid = self._transpose(temp_grid)
            temp_grid, score, changed = self._move_left(temp_grid)
            temp_grid = self._transpose(temp_grid)
        elif direction == 3: # DOWN
            temp_grid = self._transpose(temp_grid)
            temp_grid = self._reverse(temp_grid)
            temp_grid, score, changed = self._move_left(temp_grid)
            temp_grid = self._reverse(temp_grid)
            temp_grid = self._transpose(temp_grid)

        return temp_grid, score, changed

    # --- CÁC HÀM XỬ LÝ MA TRẬN (HELPER) ---

    def _move_left(self, grid):
        """Logic cốt lõi: Dồn tất cả sang trái và gộp số"""
        new_grid = []
        total_score = 0
        changed = False

        for row in grid:
            new_row, row_score, row_changed = self._merge_row(row)
            new_grid.append(new_row)
            total_score += row_score
            if row_changed:
                changed = True
        
        return new_grid, total_score, changed

    def _merge_row(self, row):
        """Xử lý gộp 1 hàng đơn lẻ"""
        # Bước 1: Loại bỏ số 0 (Dồn số lại gần nhau)
        non_zero = [x for x in row if x != 0]
        
        new_row = []
        score = 0
        skip = False
        
        # Bước 2: Gộp các số giống nhau
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
                
            # Nếu chưa phải phần tử cuối và bằng phần tử kế tiếp
            if i < len(non_zero) - 1 and non_zero[i] == non_zero[i+1]:
                merged_val = non_zero[i] * 2
                new_row.append(merged_val)
                score += merged_val
                skip = True # Bỏ qua phần tử kế tiếp vì đã gộp
            else:
                new_row.append(non_zero[i])
        
        # Bước 3: Điền lại số 0 vào bên phải cho đủ độ dài 4
        while len(new_row) < 4:
            new_row.append(0)
            
        # Kiểm tra xem hàng có thay đổi không
        changed = (new_row != row)
        
        return new_row, score, changed

    def _transpose(self, grid):
        "Ma trận chuyển vị"
        return [list(row) for row in zip(*grid)]

    def _reverse(self, grid):
        """Đảo ngược hàng (Cho Right/Down)"""
        return [row[::-1] for row in grid]