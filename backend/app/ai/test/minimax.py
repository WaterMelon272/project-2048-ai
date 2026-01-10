import math
import random

# --- GLOBAL TABLES ---
_TABLES_INIT = False
_ROW_LEFT_TABLE = [0] * 65536
_ROW_RIGHT_TABLE = [0] * 65536
_SCORE_TABLE = [0] * 65536
_HEURISTIC_TABLE = [None] * 65536


class ExpectimaxSolver:
    def __init__(self, depth=3, weights=None):
        self.depth = depth

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

        self._init_tables()

        # Transposition Table: chỉ cache MAX node
        self.tt = {}

    # ============================================================
    # PUBLIC API
    # ============================================================
    def get_best_move(self, grid):
        self.tt.clear()

        board = self._grid_to_bitboard(grid)
        moves = self._get_valid_moves(board)

        if not moves:
            return -1

        moves.sort(key=lambda x: x[2], reverse=True)

        best_move = moves[0][0]
        best_score = -float('inf')

        for direction, new_board, move_score in moves:
            val = self._expectimax(new_board, self.depth - 1, False)
            total = val + move_score

            if total > best_score:
                best_score = total
                best_move = direction

        return best_move

    # ============================================================
    # EXPECTIMAX CORE
    # ============================================================
    def _expectimax(self, board, depth, is_max):
        if depth == 0:
            return self._get_heuristic_score(board)

        # -------- MAX NODE (PLAYER) --------
        if is_max:
            key = (board, depth)
            if key in self.tt:
                return self.tt[key]

            best_val = -float('inf')
            moves = self._get_valid_moves(board)

            if not moves:
                return self._get_heuristic_score(board)

            for _, new_board, move_score in moves:
                val = self._expectimax(new_board, depth - 1, False)
                best_val = max(best_val, val + move_score)

            self.tt[key] = best_val
            return best_val

        # -------- CHANCE NODE (RANDOM TILE) --------
        empty = self._get_empty_indices(board)
        if not empty:
            return self._get_heuristic_score(board)

        if len(empty) > 6:
            empty = random.sample(empty, 6)

        total = 0.0
        for idx in empty:
            shift = idx * 4

            board_2 = board | (1 << shift)
            v2 = self._expectimax(board_2, depth - 1, True)

            board_4 = board | (2 << shift)
            v4 = self._expectimax(board_4, depth - 1, True)

            total += 0.9 * v2 + 0.1 * v4

        return total / len(empty)

    # ============================================================
    # BITBOARD OPERATIONS
    # ============================================================
    def _get_empty_indices(self, board):
        res = []
        for i in range(16):
            if (board & 0xF) == 0:
                res.append(i)
            board >>= 4
        return res

    def _get_valid_moves(self, board):
        moves = []

        r0 = board & 0xFFFF
        r1 = (board >> 16) & 0xFFFF
        r2 = (board >> 32) & 0xFFFF
        r3 = (board >> 48) & 0xFFFF

        # LEFT
        nb = (
            _ROW_LEFT_TABLE[r0]
            | (_ROW_LEFT_TABLE[r1] << 16)
            | (_ROW_LEFT_TABLE[r2] << 32)
            | (_ROW_LEFT_TABLE[r3] << 48)
        )
        if nb != board:
            sc = _SCORE_TABLE[r0] + _SCORE_TABLE[r1] + _SCORE_TABLE[r2] + _SCORE_TABLE[r3]
            moves.append((0, nb, sc))

        # RIGHT
        nb = (
            _ROW_RIGHT_TABLE[r0]
            | (_ROW_RIGHT_TABLE[r1] << 16)
            | (_ROW_RIGHT_TABLE[r2] << 32)
            | (_ROW_RIGHT_TABLE[r3] << 48)
        )
        if nb != board:
            sc = _SCORE_TABLE[r0] + _SCORE_TABLE[r1] + _SCORE_TABLE[r2] + _SCORE_TABLE[r3]
            moves.append((1, nb, sc))

        # UP / DOWN
        tb = self._transpose(board)
        r0 = tb & 0xFFFF
        r1 = (tb >> 16) & 0xFFFF
        r2 = (tb >> 32) & 0xFFFF
        r3 = (tb >> 48) & 0xFFFF

        ntb = (
            _ROW_LEFT_TABLE[r0]
            | (_ROW_LEFT_TABLE[r1] << 16)
            | (_ROW_LEFT_TABLE[r2] << 32)
            | (_ROW_LEFT_TABLE[r3] << 48)
        )
        if ntb != tb:
            sc = _SCORE_TABLE[r0] + _SCORE_TABLE[r1] + _SCORE_TABLE[r2] + _SCORE_TABLE[r3]
            moves.append((2, self._transpose(ntb), sc))

        ntb = (
            _ROW_RIGHT_TABLE[r0]
            | (_ROW_RIGHT_TABLE[r1] << 16)
            | (_ROW_RIGHT_TABLE[r2] << 32)
            | (_ROW_RIGHT_TABLE[r3] << 48)
        )
        if ntb != tb:
            sc = _SCORE_TABLE[r0] + _SCORE_TABLE[r1] + _SCORE_TABLE[r2] + _SCORE_TABLE[r3]
            moves.append((3, self._transpose(ntb), sc))

        return moves

    # ============================================================
    # HEURISTICS
    # ============================================================
    def _get_heuristic_score(self, board):
        r = [(board >> (i * 16)) & 0xFFFF for i in range(4)]
        t = self._transpose(board)
        c = [(t >> (i * 16)) & 0xFFFF for i in range(4)]

        dr = [_HEURISTIC_TABLE[x] for x in r]
        dc = [_HEURISTIC_TABLE[x] for x in c]

        smooth = sum(d[0] for d in dr + dc)
        mono = max(sum(d[1] for d in dr), sum(d[2] for d in dr)) + \
               max(sum(d[1] for d in dc), sum(d[2] for d in dc))
        free = sum(d[3] for d in dr)
        maxv = max(d[4] for d in dr + dc)

        return (
            mono * self.w_mono +
            smooth * self.w_smooth +
            free * self.w_free +
            maxv * self.w_max
        )

    # ============================================================
    # UTILITIES
    # ============================================================
    def _grid_to_bitboard(self, grid):
        board = 0
        for r in range(4):
            for c in range(4):
                v = grid[r][c]
                p = int(math.log2(v)) if v > 0 else 0
                board |= p << ((r * 4 + c) * 4)
        return board

    def _transpose(self, x):
        n = [(x >> (i * 4)) & 0xF for i in range(16)]
        return (
            n[0] | (n[4] << 4) | (n[8] << 8) | (n[12] << 12) |
            (n[1] << 16) | (n[5] << 20) | (n[9] << 24) | (n[13] << 28) |
            (n[2] << 32) | (n[6] << 36) | (n[10] << 40) | (n[14] << 44) |
            (n[3] << 48) | (n[7] << 52) | (n[11] << 56) | (n[15] << 60)
        )

    # ============================================================
    # TABLE INITIALIZATION
    # ============================================================
    def _init_tables(self):
        global _TABLES_INIT
        if _TABLES_INIT:
            return

        for row in range(65536):
            powers = [(row >> (i * 4)) & 0xF for i in range(4)]
            values = [(1 << p) if p else 0 for p in powers]

            def sim(line):
                res, score = [], 0
                nz = [x for x in line if x]
                skip = False
                for i in range(len(nz)):
                    if skip:
                        skip = False
                        continue
                    if i + 1 < len(nz) and nz[i] == nz[i + 1]:
                        res.append(nz[i] + 1)
                        score += 1 << (nz[i] + 1)
                        skip = True
                    else:
                        res.append(nz[i])
                res += [0] * (4 - len(res))
                return res, score

            nl, sc = sim(powers)
            _ROW_LEFT_TABLE[row] = nl[0] | (nl[1] << 4) | (nl[2] << 8) | (nl[3] << 12)
            _SCORE_TABLE[row] = sc

            nr, _ = sim(powers[::-1])
            nr = nr[::-1]
            _ROW_RIGHT_TABLE[row] = nr[0] | (nr[1] << 4) | (nr[2] << 8) | (nr[3] << 12)

            inc = dec = sm = 0
            for i in range(3):
                if values[i] > values[i + 1]:
                    dec += values[i + 1] - values[i]
                elif values[i + 1] > values[i]:
                    inc += values[i] - values[i + 1]
                if values[i] and values[i + 1]:
                    sm -= abs(powers[i] - powers[i + 1])

            _HEURISTIC_TABLE[row] = (sm, inc, dec, powers.count(0), max(values))

        _TABLES_INIT = True
