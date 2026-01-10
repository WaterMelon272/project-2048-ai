import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers"; // Import component mới tạo

export const metadata: Metadata = {
  title: "2048 AI",
  description: "Advanced 2048 with AI Solver",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900">
        {/* Nhúng Client Logic vào đây */}
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}