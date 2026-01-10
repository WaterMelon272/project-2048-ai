import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";

// Khởi tạo Prisma Client để kết nối DB
const prisma = new PrismaClient();

export const authOptions: NextAuthOptions = {
  // 1. Kết nối với Prisma
  adapter: PrismaAdapter(prisma),

  // 2. Cấu hình các cách đăng nhập
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // a. Kiểm tra xem người dùng có nhập đủ thông tin không
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Missing email or password");
        }

        // b. Tìm user trong database
        const user = await prisma.user.findUnique({
          where: {
            email: credentials.email,
          },
        });

        // c. Nếu không thấy user hoặc user không có password (do đăng nhập google chẳng hạn)
        if (!user || !user.password) {
          throw new Error("User not found");
        }

        // d. So sánh mật khẩu (Hash)
        const isCorrectPassword = await bcrypt.compare(
          credentials.password,
          user.password
        );

        if (!isCorrectPassword) {
          throw new Error("Invalid password");
        }

        // e. Trả về user nếu mọi thứ ok
        return user;
      }
    })
  ],

  // 3. Cấu hình Session (Dùng JWT vì Credentials Provider bắt buộc)
  session: {
    strategy: "jwt",
  },

  // 4. Secret key để mã hóa token (Lấy từ file .env)
  secret: process.env.NEXTAUTH_SECRET,

  // 5. Callbacks: Tùy chỉnh dữ liệu trả về cho Frontend
  callbacks: {
    async jwt({ token, user }) {
      // Khi đăng nhập thành công, user sẽ có dữ liệu. Ta gán ID vào token.
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      // Khi frontend gọi useSession(), ta lấy ID từ token gán vào session
      if (session.user && token) {
        // @ts-ignore
        session.user.id = token.id;
      }
      return session;
    }
  },
  
  // 6. Trang đăng nhập (Nếu muốn custom, hiện tại ta dùng Modal nên để default)
  pages: {
    signIn: "/", // Nếu lỗi sẽ quay về trang chủ
  },
  
  debug: process.env.NODE_ENV === "development",
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };