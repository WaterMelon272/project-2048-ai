import random
from .base import BaseSolver

class MinimaxSolver(BaseSolver):
    def get_best_move(self, grid):
        # Gọi đệ quy bắt đầu từ depth max
        return self.minimax(grid, self.depth, True)[1]

    def minimax(self, grid, depth, is_maximizing):
        if depth == 0:
            return self.evaluator.get_score(grid), -1

        if is_maximizing: # Lượt của AI
            best_score = -float('inf')
            best_move = -1
            # Thử 4 hướng: 0, 1, 2, 3
            for direction in range(4):
                new_grid, _, moved = self.simulate_move(grid, direction)
                if not moved: continue
                
                score, _ = self.minimax(new_grid, depth - 1, False)
                if score > best_score:
                    best_score = score
                    best_move = direction
            return best_score, best_move
            
        else: # Lượt của Máy (Sinh số ngẫu nhiên)
            best_score = float('inf')
            empty_cells = self.evaluator.get_empty_cells(grid)
            
            if not empty_cells: 
                return self.evaluator.get_score(grid), -1

            # Pruning: Nếu quá nhiều ô trống, chỉ check tối đa 4 ô để đỡ lag
            if len(empty_cells) > 4: 
                empty_cells = random.sample(empty_cells, 4)

            for r, c in empty_cells:
                # Máy sẽ cố đặt số 2 hoặc 4 vào chỗ hiểm hóc nhất (Minimizing)
                for val in [2, 4]:
                    grid[r][c] = val
                    score, _ = self.minimax(grid, depth - 1, True)
                    grid[r][c] = 0 # Backtrack (Trả lại hiện trường)
                    
                    if score < best_score:
                        best_score = score
            
            return best_score, -1