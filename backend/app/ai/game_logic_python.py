def move_row_left(row):
    new_row = [i for i in row if i != 0]
    score = 0
    for i in range(len(new_row) - 1):
        if new_row[i] == new_row[i+1] and new_row[i] != 0:
            new_row[i] *= 2
            score += new_row[i]
            new_row[i+1] = 0
    new_row = [i for i in new_row if i != 0]
    return new_row + [0] * (4 - len(new_row)), score

def move_grid(grid, direction):
    # 0: Left, 1: Right, 2: Up, 3: Down
    new_grid = [r[:] for r in grid]
    score = 0
    changed = False

    if direction == 0: # Left
        for i in range(4):
            new_row, s = move_row_left(new_grid[i])
            score += s
            if new_row != new_grid[i]: changed = True
            new_grid[i] = new_row
            
    elif direction == 1: # Right
        for i in range(4):
            new_row, s = move_row_left(new_grid[i][::-1])
            score += s
            new_row = new_row[::-1]
            if new_row != new_grid[i]: changed = True
            new_grid[i] = new_row

    elif direction == 2: # Up
        # Transpose -> Move Left -> Transpose Back
        transposed = [[new_grid[j][i] for j in range(4)] for i in range(4)]
        for i in range(4):
            new_row, s = move_row_left(transposed[i])
            score += s
            if new_row != transposed[i]: changed = True
            transposed[i] = new_row
        new_grid = [[transposed[j][i] for j in range(4)] for i in range(4)]

    elif direction == 3: # Down
        transposed = [[new_grid[j][i] for j in range(4)] for i in range(4)]
        for i in range(4):
            new_row, s = move_row_left(transposed[i][::-1])
            score += s
            new_row = new_row[::-1]
            if new_row != transposed[i]: changed = True
            transposed[i] = new_row
        new_grid = [[transposed[j][i] for j in range(4)] for i in range(4)]
            
    return new_grid, changed, score