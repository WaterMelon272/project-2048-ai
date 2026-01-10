export type Tile = {
  id: number;
  val: number;
  r: number;
  c: number;
  isNew?: boolean;
  isMerged?: boolean;
};

let idCounter = Date.now();

export const getEmptyCells = (tiles: Tile[]) => {
  const cells: { r: number; c: number }[] = [];
  const occupied = new Set(tiles.map(t => `${t.r}-${t.c}`));
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      if (!occupied.has(`${r}-${c}`)) cells.push({ r, c });
    }
  }
  return cells;
};

export const generateTile = (tiles: Tile[]): Tile[] => {
  const empty = getEmptyCells(tiles);
  if (empty.length === 0) return tiles;
  const { r, c } = empty[Math.floor(Math.random() * empty.length)];
  return [...tiles, { 
    id: idCounter++, 
    val: Math.random() < 0.9 ? 2 : 4, 
    r, c, 
    isNew: true 
  }];
};

export const tilesToGrid = (tiles: Tile[]): number[][] => {
  const grid = Array.from({ length: 4 }, () => Array(4).fill(0));
  tiles.forEach(t => grid[t.r][t.c] = t.val);
  return grid;
};

export const checkGameOver = (tiles: Tile[]): boolean => {
  if (tiles.length < 16) return false;
  
  // Convert sang grid
  const grid = tilesToGrid(tiles);
  
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      const val = grid[r][c];
      // Check bên phải
      if (c < 3 && val === grid[r][c + 1]) return false;
      // Check bên dưới
      if (r < 3 && val === grid[r + 1][c]) return false;
    }
  }
  return true;
};

// --- MOVE LOGIC---
export const moveTiles = (tiles: Tile[], dir: 0 | 1 | 2 | 3) => {
  const vector = {
    0: { r: 0, c: -1 }, // Left
    1: { r: 0, c: 1 },  // Right
    2: { r: -1, c: 0 }, // Up
    3: { r: 1, c: 0 }   // Down
  }[dir];

  let newTiles = tiles.map(t => ({ ...t, isNew: false, isMerged: false }));
  let moved = false;
  let scoreAdd = 0;
  
  let gridMap = new Map<string, Tile>();
  newTiles.forEach(t => gridMap.set(`${t.r}-${t.c}`, t));

  const mergedIds = new Set<number>();

  const traversals = { r: [] as number[], c: [] as number[] };
  for (let pos = 0; pos < 4; pos++) {
    traversals.r.push(pos);
    traversals.c.push(pos);
  }
  if (dir === 1) traversals.c.reverse(); // Right -> Reverse C
  if (dir === 3) traversals.r.reverse(); // Down -> Reverse R

  traversals.r.forEach(r => {
    traversals.c.forEach(c => {
      const tile = gridMap.get(`${r}-${c}`);
      if (!tile) return; 

      gridMap.delete(`${tile.r}-${tile.c}`);

      let f = { r: tile.r, c: tile.c };
      let next = { r: f.r + vector.r, c: f.c + vector.c };

      while (
        next.r >= 0 && next.r < 4 && 
        next.c >= 0 && next.c < 4 && 
        !gridMap.has(`${next.r}-${next.c}`)
      ) {
        f = next;
        next = { r: f.r + vector.r, c: f.c + vector.c };
      }

      const nextTile = gridMap.get(`${next.r}-${next.c}`);
      
      if (
        nextTile && 
        nextTile.val === tile.val && 
        !nextTile.isMerged 
      ) {
        tile.r = nextTile.r;
        tile.c = nextTile.c;
        mergedIds.add(tile.id); 
        
        nextTile.val *= 2;
        nextTile.isMerged = true;
        scoreAdd += nextTile.val;
        
        moved = true;
      } else {
        tile.r = f.r;
        tile.c = f.c;
        
        gridMap.set(`${tile.r}-${tile.c}`, tile);
        
        if (r !== tile.r || c !== tile.c) moved = true;
      }
    });
  });

  const finalTiles = newTiles.filter(t => !mergedIds.has(t.id));

  return { tiles: finalTiles, score: scoreAdd, moved };
};