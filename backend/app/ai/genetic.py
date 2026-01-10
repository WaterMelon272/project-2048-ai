import random
import multiprocessing
from .algorithms.expectimax import ExpectimaxSolver

# Cấu hình training
TRAINING_DEPTH = 3
MAX_MOVES_PER_GAME = 500 # Tăng lên vì Bitboard chạy nhanh hơn

def spawn_random_tile_bitboard(board):
    """
    Sinh số ngẫu nhiên (2 hoặc 4) vào ô trống trên Bitboard.
    Trả về: (new_board, success)
    """
    # 1. Tìm các index ô trống (0-15)
    empty_indices = []
    temp = board
    for i in range(16):
        if (temp & 0xF) == 0:
            empty_indices.append(i)
        temp >>= 4
    
    if not empty_indices:
        return board, False

    # 2. Chọn ngẫu nhiên vị trí
    idx = random.choice(empty_indices)
    
    # 3. Chọn giá trị (90% ra 2 (bit=1), 10% ra 4 (bit=2))
    val = 1 if random.random() < 0.9 else 2
    
    # 4. Gán vào board
    new_board = board | (val << (idx * 4))
    return new_board, True

def play_game_simulation(weights):
    """
    Chạy 1 ván game độc lập dùng Bitboard.
    """
    # Khởi tạo bàn cờ trống (int 64-bit)
    board = 0
    
    # Sinh 2 ô đầu tiên
    board, _ = spawn_random_tile_bitboard(board)
    board, _ = spawn_random_tile_bitboard(board)

    # Init Solver
    solver = ExpectimaxSolver(depth=TRAINING_DEPTH, weights=weights)
    
    moves = 0
    total_score = 0
    
    while moves < MAX_MOVES_PER_GAME:
        # 1. AI Tìm nước đi (Input là bitboard int)
        best_move = solver.get_best_move(board)
        
        if best_move == -1: # Game Over (Không tìm thấy nước đi)
            break
            
        # 2. Thực hiện nước đi
        # simulate_move trả về: (new_board, score, moved)
        new_board, score, moved = solver.simulate_move(board, best_move)
        
        if not moved:
            break # AI bị kẹt
            
        board = new_board
        total_score += score
        
        # 3. Sinh số ngẫu nhiên (Enemy Turn)
        board, spawned = spawn_random_tile_bitboard(board)
        if not spawned:
            break # Hết ô trống -> Game Over
        
        moves += 1
        
    # Fitness = Điểm số đạt được trong game
    # Bạn có thể cộng thêm điểm thưởng nếu đạt Max Tile lớn (cần giải nén bitboard để check)
    return total_score

class GeneticAlgorithm:
    def __init__(self, population_size=10, mutation_rate=0.1, generations=5):
        self.pop_size = population_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.population = [] # List of weights dict

    def init_population(self):
        """Khởi tạo dân số ngẫu nhiên với các trọng số mới"""
        self.population = []
        for _ in range(self.pop_size):
            self.population.append({
                'monotonic': random.uniform(0, 50),
                'smoothness': random.uniform(0, 10),
                'free_tiles': random.uniform(0, 50),
                'merges': random.uniform(0, 50) # Thay max_tile bằng merges
            })

    def crossover(self, parent1, parent2):
        """Lai ghép: Lấy trung bình cộng hoặc random gen từ bố mẹ"""
        child = {}
        for key in parent1:
            if random.random() > 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child

    def mutate(self, individual):
        """Đột biến: Thay đổi nhẹ giá trị"""
        for key in individual:
            if random.random() < self.mutation_rate:
                # Biến động +/- 20%
                change = random.uniform(0.8, 1.2)
                individual[key] *= change
        return individual

    def run(self, progress_callback=None):
        """
        Chạy vòng lặp tiến hóa.
        """
        self.init_population()
        best_solution = None
        best_fitness = -1

        for gen in range(self.generations):
            scores = []
            
            # --- CHẠY SONG SONG (MULTIPROCESSING) ---
            # Lưu ý: Trên Windows, hàm được map (play_game_simulation) phải nằm ở top-level
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                scores = pool.map(play_game_simulation, self.population)
            
            # Tìm cá thể tốt nhất thế hệ này
            gen_best_idx = scores.index(max(scores))
            gen_best_score = scores[gen_best_idx]
            
            if gen_best_score > best_fitness:
                best_fitness = gen_best_score
                best_solution = self.population[gen_best_idx]
            
            print(f"Gen {gen+1}/{self.generations} | Best Score: {gen_best_score}")
            if progress_callback:
                progress_callback(gen + 1, self.generations, gen_best_score)

            # Chọn lọc tự nhiên (Giữ lại top 50%)
            sorted_pop = [x for _, x in sorted(zip(scores, self.population), key=lambda pair: pair[0], reverse=True)]
            top_half = sorted_pop[:self.pop_size // 2]
            
            # Tạo thế hệ mới
            new_pop = top_half[:] # Giữ lại tinh hoa
            
            while len(new_pop) < self.pop_size:
                # Chọn ngẫu nhiên 2 bố mẹ từ top half
                p1 = random.choice(top_half)
                p2 = random.choice(top_half)
                child = self.crossover(p1, p2)
                child = self.mutate(child)
                new_pop.append(child)
            
            self.population = new_pop
            
        return best_solution, best_fitness