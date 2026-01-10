import { motion } from "framer-motion";
import { useGameStore } from "@/store/useGameStore";
import clsx from "clsx";

const getTileStyle = (val: number) => {
  switch (val) {
    case 2:    return "bg-gradient-to-br from-slate-200 to-slate-400 text-slate-800";
    case 4:    return "bg-gradient-to-br from-indigo-200 to-indigo-300 text-slate-800";
    case 8:    return "bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow-[0_0_10px_#f97316]";
    case 16:   return "bg-gradient-to-br from-orange-500 to-red-600 text-white shadow-[0_0_15px_#ea580c]";
    case 32:   return "bg-gradient-to-br from-red-500 to-rose-600 text-white shadow-[0_0_20px_#e11d48]";
    case 64:   return "bg-gradient-to-br from-rose-600 to-pink-600 text-white shadow-[0_0_25px_#db2777]";
    case 128:  return "bg-gradient-to-br from-purple-500 to-indigo-600 text-white shadow-[0_0_30px_#7c3aed] border border-purple-300";
    case 256:  return "bg-gradient-to-br from-blue-500 to-cyan-500 text-white shadow-[0_0_35px_#06b6d4] border border-cyan-300";
    case 512:  return "bg-gradient-to-br from-cyan-500 to-teal-500 text-white shadow-[0_0_40px_#14b8a6] ring-2 ring-cyan-200";
    case 1024: return "bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-[0_0_45px_#10b981] ring-2 ring-emerald-200";
    case 2048: return "bg-gradient-to-br from-yellow-400 to-amber-600 text-white shadow-[0_0_50px_#f59e0b] ring-2 ring-yellow-200 animate-pulse";
    case 4096: return "bg-[conic-gradient(at_top_right,_var(--tw-gradient-stops))] from-red-600 via-rose-700 to-black text-white shadow-[0_0_60px_#e11d48] ring-2 ring-red-400 border-2 border-red-500";
    case 8192: return "bg-[conic-gradient(at_bottom_left,_var(--tw-gradient-stops))] from-fuchsia-500 via-purple-800 to-black text-white shadow-[0_0_65px_#d946ef] ring-2 ring-fuchsia-300 border-2 border-fuchsia-400";
    case 16384: return "bg-[conic-gradient(at_top,_var(--tw-gradient-stops))] from-lime-400 via-green-700 to-black text-white shadow-[0_0_70px_#84cc16] ring-2 ring-lime-300 border-2 border-lime-400";
    case 32768: return "bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white via-blue-900 to-black text-white shadow-[0_0_80px_#ffffff] ring-2 ring-white border-2 border-white animate-[pulse_3s_ease-in-out_infinite]";
    default: return "bg-black text-white border-2 border-white shadow-[0_0_100px_white]"; 
  }
};

type Props = {
  val: number;
  r: number;
  c: number;
  isNew?: boolean;
  isMerged?: boolean;
};

export default function Tile({ val, r, c, isNew, isMerged }: Props) {
  const { showAnimation } = useGameStore();
  const GAP = 12;
  const SIZE = 77.5;
  
  const x = c * (SIZE + GAP);
  const y = r * (SIZE + GAP);

  const transitionConfig = showAnimation ? {
    x: { type: "spring", stiffness: 500, damping: 30 },
    y: { type: "spring", stiffness: 500, damping: 30 },
    scale: isNew ? { type: "spring", stiffness: 400, damping: 20 } : { duration: 0.1 },
    opacity: { duration: 0.1 } 
  } : { duration: 0 };

let zIndex = 10; 
if (isMerged) zIndex = 50; 
else if (isNew) zIndex = 5; 
else zIndex = 10 + (val > 2048 ? 2 : 0);

return (
    <motion.div
      animate={{ x, y, scale: (isMerged && showAnimation) ? [1, 1.1, 1] : 1, opacity: 1 }}
      initial={isNew && showAnimation ? { scale: 0, opacity: 0, x, y } : false} 
      transition={transitionConfig}
      className={clsx(
        "absolute w-[77.5px] h-[77.5px] rounded-lg flex items-center justify-center font-bold select-none",
        "backdrop-blur-sm", // Thêm chút kính cho tile
        getTileStyle(val)   // Gọi hàm lấy màu ở đây
      )}
      style={{
        // Xóa phần backgroundColor và color cũ đi
        fontSize: val > 1000 ? "28px" : val > 100 ? "36px" : "44px",
        zIndex: zIndex,
        textShadow: "0 2px 4px rgba(0,0,0,0.3)" // Đổ bóng chữ cho dễ đọc
      }}
    >
      {val}
    </motion.div>
  );
}