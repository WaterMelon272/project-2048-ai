import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";
import { getServerSession } from "next-auth";
import { authOptions } from "../auth/[...nextauth]/route";

const prisma = new PrismaClient();

// 1. GET: Lấy Bảng xếp hạng Global (Top 20)
export async function GET(req: Request) {
  try {
    const scores = await prisma.gameResult.findMany({
      take: 20,
      orderBy: { score: 'desc' },
      include: { 
        user: { select: { name: true, email: true } } // Lấy tên người chơi
      }
    });
    return NextResponse.json(scores);
  } catch (e) {
    return NextResponse.json({ message: "Error fetching leaderboard" }, { status: 500 });
  }
}

// 2. POST: Lưu kết quả trận đấu
export async function POST(req: Request) {
  const session = await getServerSession(authOptions);
  
  // Chỉ lưu nếu đã đăng nhập (hoặc bạn có thể cho phép Guest lưu nếu muốn)
  if (!session || !session.user?.email) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  const { score, maxTile, moves, isAi, algoName } = await req.json();

  const user = await prisma.user.findUnique({ where: { email: session.user.email } });
  if (!user) return NextResponse.json({ message: "User not found" }, { status: 404 });

  const result = await prisma.gameResult.create({
    data: {
      userId: user.id,
      score: Number(score),
      maxTile: Number(maxTile),
      moves: Number(moves),
      isAi: Boolean(isAi),
      algoName: isAi ? algoName : "Human",
    }
  });

  return NextResponse.json(result);
}