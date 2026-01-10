# File: backend/app/ai/solver.py
import random
from .heuristics import calculate_score
from .game_logic_python import move_grid

# Mapping: 0: Left, 1: Right, 2: Up, 3: Down
MOVES = [0, 1, 2, 3]

def get_best_move_python(grid, depth=3):
    best_score = -float('inf')
    best_move = -1
    
    # Danh sách các nước đi hợp lệ (làm thay đổi bàn cờ)
    valid_moves = []
    
    # Bước 1: Tìm tất cả các nước đi hợp lệ trước
    for move in MOVES:
        new_grid, changed, score_gained = move_grid(grid, move)
        if changed:
            valid_moves.append(move)
            
            # Bước 2: Chạy Expectimax (hoặc Maximax đơn giản hóa)
            # Tính điểm của trạng thái sau khi đi
            current_score = expectimax(new_grid, depth - 1, False)
            
            # Cộng thêm điểm thu được từ việc gộp số (score_gained)
            # AI sẽ thích các nước đi ăn điểm ngay lập tức
            total_score = current_score + (score_gained * 1.5) 
            
            if total_score > best_score:
                best_score = total_score
                best_move = move
    
    # Bước 3: Cơ chế chống kẹt (Fallback)
    # Nếu thuật toán không tìm ra nước đi tốt nhất (best_move vẫn là -1)
    # NHƯNG vẫn còn nước đi hợp lệ (valid_moves không rỗng)
    # -> Bắt buộc chọn ngẫu nhiên một nước đi hợp lệ để game tiếp tục.
    if best_move == -1 and len(valid_moves) > 0:
        return random.choice(valid_moves)
        
    return best_move

def expectimax(grid, depth, is_player_turn):
    # Điều kiện dừng đệ quy
    if depth == 0:
        return calculate_score(grid)
    
    if is_player_turn:
        # Lượt của người chơi (AI): Tìm nước đi Max (tốt nhất)
        max_score = -float('inf')
        can_move = False
        
        for move in MOVES:
            new_grid, changed, _ = move_grid(grid, move)
            if changed:
                can_move = True
                score = expectimax(new_grid, depth - 1, False)
                if score > max_score:
                    max_score = score
        
        # Nếu không đi được nữa (Game Over), trả về điểm rất thấp
        return max_score if can_move else -100000

    else:
        # Lượt của máy (Sinh số ngẫu nhiên): Tính trung bình (Average)
        # Vì ta không biết số 2/4 sẽ hiện ở đâu, ta tính xác suất
        # Để đơn giản và nhanh cho Python, ta chỉ xét các ô trống
        empty_cells = []
        for r in range(4):
            for c in range(4):
                if grid[r][c] == 0:
                    empty_cells.append((r, c))
        
        if not empty_cells:
            return calculate_score(grid)
            
        # Tối ưu hiệu năng: Nếu quá nhiều ô trống, chỉ lấy mẫu vài ô để tính
        # (Giúp AI chạy nhanh hơn, không bị timeout)
        if len(empty_cells) > 4:
            empty_cells = random.sample(empty_cells, 4)
            
        avg_score = 0
        for r, c in empty_cells:
            # Giả sử sinh ra số 2 (xác suất 90% trong game thật)
            # Ta bỏ qua trường hợp số 4 để giảm nhánh tính toán
            grid[r][c] = 2
            avg_score += expectimax(grid, depth - 1, True)
            grid[r][c] = 0 # Backtrack (trả lại ô trống)
            
        return avg_score / len(empty_cells)