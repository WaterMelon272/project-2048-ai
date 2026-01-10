from .algorithms.minimax import MinimaxSolver
from .algorithms.expectimax import ExpectimaxSolver
from .algorithms.mcts import MCTSSolver
from .algorithms.dfs import DFSSolver
from .algorithms.bfs import BFSSolver

class AIManager:
    @staticmethod
    def get_solver(algo_name, depth, weights):
        
        if algo_name == "Minimax (Classic)":
            return MinimaxSolver(depth, weights)
        
        elif algo_name == "Expectimax (Default)":
            return ExpectimaxSolver(depth, weights)
            
        elif algo_name == "Monte Carlo (MCTS)":
            return MCTSSolver(depth, weights)
            
        elif algo_name == "DFS (Greedy)":
            return DFSSolver(depth, weights)
            
        elif algo_name == "BFS (Layered)":
            return BFSSolver(depth, weights)
            
        else:
            return ExpectimaxSolver(depth, weights)