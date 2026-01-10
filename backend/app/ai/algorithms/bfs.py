from collections import deque
from .base import BaseSolver

class BFSSolver(BaseSolver):
    def get_best_move(self, board):


        # --- 2. KHỞI TẠO QUEUE ---
        # Sử dụng deque để popleft nhanh hơn list thường
        # Cấu trúc: (current_board, first_move_index, current_depth, accumulated_score)
        queue = deque([(board, -1, 0, 0)])
        
        # Dictionary lưu điểm tốt nhất cho mỗi nhánh khởi đầu (0, 1, 2, 3)
        move_scores = {0: -float('inf'), 1: -float('inf'), 2: -float('inf'), 3: -float('inf')}

        # --- 3. VÒNG LẶP BFS ---
        while queue:
            c_board, f_move, depth, acc_score = queue.popleft()

            # Điều kiện dừng: Đạt độ sâu giới hạn
            if depth >= self.depth:
                # Điểm cuối cùng = Heuristic hiện tại + Điểm tích lũy trên đường đi
                final_score = self.evaluator.get_score(c_board) + acc_score
                
                # Cập nhật điểm cho nhánh khởi đầu tương ứng
                if f_move != -1:
                    if final_score > move_scores[f_move]:
                        move_scores[f_move] = final_score
                continue

            # Mở rộng trạng thái (Branching)
            is_leaf = True
            for direction in range(4):
                # simulate_move đã hỗ trợ bitboard, trả về (new_board, score, moved)
                new_board, move_score, moved = self.simulate_move(c_board, direction)
                
                if moved:
                    is_leaf = False
                    # Xác định nhánh khởi đầu (nếu chưa có)
                    next_first_move = f_move if f_move != -1 else direction
                    
                    # Đẩy vào queue
                    # Lưu ý: BFS này bỏ qua bước sinh Random Tile (Enemy Turn) 
                    # để tránh bùng nổ tổ hợp (Branching factor quá lớn), 
                    # nên nó hoạt động như một thuật toán Greedy Lookahead.
                    queue.append((new_board, next_first_move, depth + 1, acc_score + move_score))

            # Xử lý trường hợp là lá (Game Over hoặc kẹt) trước khi hết depth
            if is_leaf and f_move != -1:
                final_score = self.evaluator.get_score(c_board) + acc_score
                if final_score > move_scores[f_move]:
                    move_scores[f_move] = final_score

        # --- 4. TÌM NƯỚC ĐI TỐT NHẤT ---
        best_move = max(move_scores, key=move_scores.get)
        
        # Nếu tất cả các hướng đều -inf (không đi được nước nào)
        if move_scores[best_move] == -float('inf'):
            return -1
            
        return best_move