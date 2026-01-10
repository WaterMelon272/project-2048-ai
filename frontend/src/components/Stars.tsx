"use client";
import { useEffect, useState } from "react";

export default function Stars() {
  const [stars, setStars] = useState<Array<{ id: number; top: number; left: number; size: number; duration: number }>>([]);

  useEffect(() => {
    const count = 100;
    const newStars = Array.from({ length: count }).map((_, i) => ({
      id: i,
      top: Math.random() * 100,      // Vị trí top (0-100%)
      left: Math.random() * 100,     // Vị trí left (0-100%)
      size: Math.random() * 2 + 1,   // Kích thước từ 1px đến 3px
      duration: Math.random() * 3 + 2, // Tốc độ nhấp nháy ngẫu nhiên (2s - 5s)
    }));
    setStars(newStars);
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
      {stars.map((star) => (
        <div
          key={star.id}
          className="absolute bg-white rounded-full opacity-80 animate-pulse"
          style={{
            top: `${star.top}%`,
            left: `${star.left}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            animationDuration: `${star.duration}s`,
          }}
        />
      ))}
    </div>
  );
}