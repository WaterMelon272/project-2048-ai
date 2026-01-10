import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";
import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

const prisma = new PrismaClient();

export async function GET(req: Request) {
  const session = await getServerSession(authOptions);

  // Nếu chưa đăng nhập -> Trả về 0 (để frontend tự xử lý session score)
  if (!session || !session.user?.email) {
    return NextResponse.json({ score: 0 });
  }

  const user = await prisma.user.findUnique({ where: { email: session.user.email } });
  if (!user) return NextResponse.json({ score: 0 });

  // Tìm trận đấu có điểm cao nhất của user này
  const bestGame = await prisma.gameResult.findFirst({
    where: { userId: user.id },
    orderBy: { score: 'desc' }, // Sắp xếp giảm dần
    select: { score: true }     // Chỉ lấy cột score
  });

  return NextResponse.json({ score: bestGame?.score || 0 });
}