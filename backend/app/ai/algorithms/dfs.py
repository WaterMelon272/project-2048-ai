from .base import BaseSolver

class DFSSolver(BaseSolver):
    def get_best_move(self, board):

        # --- 2. GỌI ĐỆ QUY ---
        # Hàm dfs trả về (score, move), ta chỉ cần lấy move
        return self.dfs(board, self.depth)[1]

    def dfs(self, board, depth):
        # Base Case: Hết độ sâu cần tìm kiếm
        if depth == 0:
            return self.evaluator.get_score(board), -1

        best_score = -float('inf')
        best_move = -1
        has_valid_move = False

        # Thử 4 hướng di chuyển
        for direction in range(4):
            # simulate_move trong BaseSolver đã hỗ trợ Bitboard
            # Trả về: (new_board_int, score_gained, is_moved)
            new_board, score_gained, moved = self.simulate_move(board, direction)
            
            if not moved: 
                continue

            has_valid_move = True

            # --- LOGIC DFS (Greedy Lookahead) ---
            # DFS cho 2048 thường bỏ qua bước Chance (sinh số ngẫu nhiên) 
            # để có thể duyệt rất sâu (Depth 10-20) mà không bị bùng nổ tổ hợp.
            # Nó giả định rằng "sau khi mình đi, bàn cờ giữ nguyên để mình đi tiếp".
            
            future_heuristic, _ = self.dfs(new_board, depth - 1)
            
            # Tổng điểm = Điểm Heuristic tương lai + Điểm thực nhận được (score_gained)
            # Việc cộng score_gained giúp AI ưu tiên các nước đi ăn điểm ngay lập tức
            # trong khi vẫn nhìn về tương lai.
            total_score = future_heuristic + score_gained

            if total_score > best_score:
                best_score = total_score
                best_move = direction

        # Nếu tại node này không đi được hướng nào (Game Over hoặc Kẹt)
        if not has_valid_move:
            return self.evaluator.get_score(board), -1

        return best_score, best_move