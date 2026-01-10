import { NextResponse } from 'next/server';
import { Board, Direction, makeMove, getEmptyCells, cloneBoard } from '@/lib/gameLogic';

// Cấu hình AI giống file C#
const AI_DEPTH = 4; // Độ sâu (Web serverless nên để thấp hơn chút so với Local App)
const SAMPLE_CELLS = 6;
const W_EMPTY = 3.0;
const W_SMOOTH = 1.0;
const W_MONO = 1.5;
const W_MAX = 0.1;

export async function POST(req: Request) {
    const { board } = await req.json();
    
    if (!board) return NextResponse.json({ error: "No board provided" }, { status: 400 });

    const bestMove = getBestMove(board, AI_DEPTH);
    return NextResponse.json({ move: bestMove });
}

function getBestMove(board: Board, depth: number): Direction | null {
    let bestScore = -Infinity;
    let bestMove: Direction | null = null;
    const moves: Direction[] = [0, 1, 2, 3];

    for (const dir of moves) {
        const { moved, board: nextBoard } = makeMove(board, dir);
        if (moved) {
            const score = expectimax(nextBoard, depth - 1, false);
            if (score > bestScore) {
                bestScore = score;
                bestMove = dir;
            }
        }
    }
    return bestMove;
}

function expectimax(b: Board, depth: number, isMax: boolean): number {
    if (depth === 0) return evaluate(b);

    if (isMax) {
        let maxScore = -Infinity;
        let hasMove = false;
        for (const dir of [0, 1, 2, 3] as Direction[]) {
            const { moved, board: nextBoard } = makeMove(b, dir);
            if (moved) {
                hasMove = true;
                const score = expectimax(nextBoard, depth - 1, false);
                maxScore = Math.max(maxScore, score);
            }
        }
        return hasMove ? maxScore : evaluate(b);
    } else {
        let empties = getEmptyCells(b);
        if (empties.length === 0) return evaluate(b);
        
        // Optimization: Sample bớt nếu quá nhiều ô trống
        if (empties.length > SAMPLE_CELLS) {
             empties = empties.sort(() => 0.5 - Math.random()).slice(0, SAMPLE_CELLS);
        }

        let totalScore = 0;
        for (const {r, c} of empties) {
            // Trường hợp ra số 2 (90%)
            b[r][c] = 2;
            totalScore += 0.9 * expectimax(b, depth - 1, true);
            // Trường hợp ra số 4 (10%)
            b[r][c] = 4;
            totalScore += 0.1 * expectimax(b, depth - 1, true);
            b[r][c] = 0; // Backtrack
        }
        return totalScore / empties.length;
    }
}

// Hàm Heuristics (Evaluate)
function evaluate(b: Board): number {
    const empty = getEmptyCells(b).length;
    
    let maxTile = 0;
    for(let r=0; r<4; r++) for(let c=0; c<4; c++) maxTile = Math.max(maxTile, b[r][c]);

    const smooth = calcSmoothness(b);
    const mono = calcMonotonicity(b);

    return (W_EMPTY * empty) + (W_SMOOTH * smooth) + (W_MONO * mono) + (W_MAX * Math.log2(maxTile + 1));
}

function calcSmoothness(b: Board): number {
    let smooth = 0;
    for (let r=0; r<4; r++) for (let c=0; c<3; c++) {
        if (b[r][c] && b[r][c+1]) smooth -= Math.abs(Math.log2(b[r][c]) - Math.log2(b[r][c+1]));
    }
    for (let c=0; c<4; c++) for (let r=0; r<3; r++) {
        if (b[r][c] && b[r+1][c]) smooth -= Math.abs(Math.log2(b[r][c]) - Math.log2(b[r+1][c]));
    }
    return smooth;
}

function calcMonotonicity(b: Board): number {
    // Logic tương tự C# nhưng viết gọn lại
    let totals = [0, 0, 0, 0];
    
    // Left/Right
    for (let r=0; r<4; r++) for (let c=0; c<3; c++) {
        const curr = b[r][c] ? Math.log2(b[r][c]) : 0;
        const next = b[r][c+1] ? Math.log2(b[r][c+1]) : 0;
        if(curr > next) totals[0] += curr - next; else totals[1] += next - curr;
    }
    // Up/Down
    for (let c=0; c<4; c++) for (let r=0; r<3; r++) {
        const curr = b[r][c] ? Math.log2(b[r][c]) : 0;
        const next = b[r+1][c] ? Math.log2(b[r+1][c]) : 0;
        if(curr > next) totals[2] += curr - next; else totals[3] += next - curr;
    }
    return -Math.min(totals[0], totals[1]) - Math.min(totals[2], totals[3]);
}