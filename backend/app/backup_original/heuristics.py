import math

class Heuristics:
    def __init__(self, weights=None):
        # Trọng số mặc định nếu không truyền vào
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

    def get_score(self, grid):
        return (self.calculate_monotonicity(grid) * self.w_mono +
                self.calculate_smoothness(grid) * self.w_smooth +
                len(self.get_empty_cells(grid)) * self.w_free +
                self.get_max_tile(grid) * self.w_max)

    # ---UTILITIES---
    
    def get_empty_cells(self, grid):
        cells = []
        for r in range(4):
            for c in range(4):
                if grid[r][c] == 0:
                    cells.append((r, c))
        return cells

    def get_max_tile(self, grid):
        return max(max(row) for row in grid)

    def calculate_smoothness(self, grid):
        smoothness = 0
        for r in range(4):
            for c in range(4):
                if grid[r][c] != 0:
                    val = math.log2(grid[r][c])
                    # Check phải
                    if c < 3 and grid[r][c+1] != 0:
                        target = math.log2(grid[r][c+1])
                        smoothness -= abs(val - target)
                    # Check dưới
                    if r < 3 and grid[r+1][c] != 0:
                        target = math.log2(grid[r+1][c])
                        smoothness -= abs(val - target)
        return smoothness

    def calculate_monotonicity(self, grid):
        totals = [0, 0, 0, 0] # Up, Down, Left, Right

        # Trái/Phải
        for r in range(4):
            current = 0
            next_val = 0
            for c in range(3):
                current = grid[r][c]
                next_val = grid[r][c+1]
                if current > next_val:
                    totals[0] += next_val - current # Giảm dần
                elif next_val > current:
                    totals[1] += current - next_val # Tăng dần

        # Lên/Xuống
        for c in range(4):
            for r in range(3):
                current = grid[r][c]
                next_val = grid[r+1][c]
                if current > next_val:
                    totals[2] += next_val - current
                elif next_val > current:
                    totals[3] += current - next_val

        return max(totals[0], totals[1]) + max(totals[2], totals[3])