import random
from .base import BaseSolver

class MinimaxSolver(BaseSolver):
    def get_best_move(self, grid):
        # 1. Convert Grid (2D Array) -> Bitboard (Int 64-bit)
        board = self.grid_to_bitboard(grid)
        
        # 2. Gọi đệ quy bắt đầu từ depth max với Bitboard
        return self.minimax(board, self.depth, True)[1]

    def minimax(self, board, depth, is_maximizing):
        # Base Case: Hết độ sâu
        if depth == 0:
            return self.evaluator.get_score(board), -1

        if is_maximizing: # Lượt của AI
            best_score = -float('inf')
            best_move = -1
            
            moves = self.get_moves_bitboard(board)
            # Nếu không đi được (Game Over)
            if not moves:
                return self.evaluator.get_score(board), -1

            for direction, new_board, move_score in moves:
                # Gọi đệ quy
                score, _ = self.minimax(new_board, depth - 1, False)
                
                # Logic cũ của bạn: So sánh score trả về từ đệ quy (Heuristic tương lai)
                # (Lưu ý: Nếu muốn AI tham ăn điểm hơn, bạn có thể cộng thêm move_score vào đây)
                if score > best_score:
                    best_score = score
                    best_move = direction
            
            return best_score, best_move
            
        else: # Lượt của Máy (Sinh số ngẫu nhiên)
            best_score = float('inf')
            
            # Tìm ô trống bằng Bitwise (Thay cho get_empty_cells)
            empty_indices = []
            temp = board
            for i in range(16):
                # Kiểm tra 4 bit cuối có bằng 0 không
                if (temp & 0xF) == 0: 
                    empty_indices.append(i)
                temp >>= 4
            
            if not empty_indices: 
                return self.evaluator.get_score(board), -1

            # Pruning: Nếu quá nhiều ô trống, chỉ check tối đa 4 ô để đỡ lag
            if len(empty_indices) > 4: 
                empty_indices = random.sample(empty_indices, 4)

            for idx in empty_indices:
                shift = idx * 4
                
                # Máy sẽ cố đặt số 2 hoặc 4 vào chỗ hiểm hóc nhất (Minimizing)
                # Bitboard: power 1 là số 2, power 2 là số 4
                for power in [1, 2]:
                    # Tạo bàn cờ mới với số đã điền (Tương đương grid[r][c] = val)
                    # Không cần backtrack thủ công vì 'board' gốc không bị đổi
                    new_board = board | (power << shift)
                    
                    score, _ = self.minimax(new_board, depth - 1, True)
                    
                    if score < best_score:
                        best_score = score
            
            return best_score, -1