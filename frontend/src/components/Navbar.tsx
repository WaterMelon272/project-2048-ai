"use client";
import { User, Trophy, LogIn, Settings, LogOut } from "lucide-react";
import { useState } from "react";
import { useSession, signOut } from "next-auth/react";
import AuthModal from "@/components/auth/AuthModal"; 
import LeaderboardModal from "@/components/game/LeaderboardModal";

type Props = { onOpenSettings: () => void; };

export default function Navbar({ onOpenSettings }: Props) {
  const { data: session } = useSession(); // Lấy thông tin user
  const [showAuth, setShowAuth] = useState(false);
  const [showRank, setShowRank] = useState(false);

  return (
    <>
    <nav className="w-full h-16 flex items-center justify-between px-4 md:px-8 fixed top-0 left-0 z-50 pointer-events-none">
      
      {/* GÓC TRÁI: System Config */}
      <div className="pointer-events-auto">
         <button onClick={onOpenSettings} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white transition-all backdrop-blur-md group" title="System Config">
            <Settings size={20} className="group-hover:rotate-90 transition-transform duration-500 text-cyan-400"/>
            <span className="hidden md:inline text-xs font-bold uppercase tracking-wider">System</span>
         </button>
      </div>

      {/* GÓC PHẢI: Leaderboard & User */}
      <div className="flex items-center gap-3 pointer-events-auto">
        <button 
           onClick={() => setShowRank(true)}
           className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-yellow-500/10 border border-yellow-500/30 text-yellow-200 hover:bg-yellow-500/20 transition-all text-sm font-bold backdrop-blur-md"
        >
           <Trophy size={14} /> <span className="hidden md:inline">Rank</span>
        </button>
        
        {session ? (
            // NẾU ĐÃ LOGIN: Hiện tên và nút Logout
            <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-200 backdrop-blur-md">
                    <User size={14} />
                    <span className="text-sm font-bold max-w-[100px] truncate">{session.user?.name}</span>
                </div>
                <button onClick={() => signOut()} className="p-1.5 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-300 transition-colors" title="Logout">
                    <LogOut size={16}/>
                </button>
            </div>
        ) : (
            // CHƯA LOGIN: Nút Login
            <button onClick={() => setShowAuth(true)} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-200 hover:bg-cyan-500/20 transition-all text-sm font-bold backdrop-blur-md">
                <LogIn size={14} /> <span className="hidden md:inline">Login</span>
            </button>
        )}
      </div>
    </nav>

    {/* Modal Đăng nhập */}
    <AuthModal isOpen={showAuth} onClose={() => setShowAuth(false)} />
        <LeaderboardModal isOpen={showRank} onClose={() => setShowRank(false)} />
    </>
  );
}