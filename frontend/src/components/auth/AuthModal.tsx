"use client";
import { useState } from "react";
import { signIn } from "next-auth/react";
import { X, Mail, Lock, User as UserIcon, ArrowRight } from "lucide-react";

type Props = { isOpen: boolean; onClose: () => void; };

export default function AuthModal({ isOpen, onClose }: Props) {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (isLogin) {
      // ĐĂNG NHẬP
      const res = await signIn("credentials", {
        redirect: false,
        email: form.email,
        password: form.password,
      });
      if (res?.error) setError("Invalid email or password");
      else onClose();
    } else {
      // ĐĂNG KÝ
      try {
        const res = await fetch("/api/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        if (!res.ok) throw new Error(await res.text());
        
        await signIn("credentials", { redirect: false, email: form.email, password: form.password });
        onClose();
      } catch (err) {
        setError("Registration failed. Email might be taken.");
      }
    }
    setLoading(false);
  };

  const inputClass = "w-full bg-black/40 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all placeholder:text-gray-500";

  return (
    <div className="fixed inset-0 z-[6000] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in">
      <div className="w-full max-w-md bg-slate-900/90 border border-white/10 rounded-2xl shadow-2xl p-8 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white"><X size={20}/></button>
        
        <h2 className="text-3xl font-black text-center mb-2 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400 uppercase">
            {isLogin ? "Welcome Back" : "Join the Grid"}
        </h2>
        <p className="text-center text-gray-400 text-sm mb-6">
            {isLogin ? "Login to sync your heuristics & scores." : "Create an account to climb the leaderboard."}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
             <div className="relative">
                <UserIcon className="absolute left-3 top-3.5 text-gray-500" size={18} />
                <input required placeholder="Username" className={inputClass} 
                       value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
             </div>
          )}
          
          <div className="relative">
             <Mail className="absolute left-3 top-3.5 text-gray-500" size={18} />
             <input required type="email" placeholder="Email Address" className={inputClass}
                    value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          </div>

          <div className="relative">
             <Lock className="absolute left-3 top-3.5 text-gray-500" size={18} />
             <input required type="password" placeholder="Password" className={inputClass}
                    value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
          </div>

          {error && <p className="text-red-400 text-xs text-center font-bold">{error}</p>}

          <button disabled={loading} type="submit" className="w-full py-3 mt-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-cyan-900/20">
             {loading ? "Processing..." : (isLogin ? "Login System" : "Initialize Account")} 
             {!loading && <ArrowRight size={18} />}
          </button>
        </form>

        <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button onClick={() => setIsLogin(!isLogin)} className="text-cyan-400 font-bold hover:underline">
                    {isLogin ? "Register Now" : "Login Here"}
                </button>
            </p>
        </div>
      </div>
    </div>
  );
}