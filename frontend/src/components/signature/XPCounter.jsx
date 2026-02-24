import React, { useState, useEffect, useRef } from "react";
import { cn } from "@/utils/cn";

export function XPCounter({ value, className }) {
  const [displayValue, setDisplayValue] = useState(value || 0);
  const [isAnimating, setIsAnimating] = useState(false);
  const startValueRef = useRef(displayValue);
  const endValueRef = useRef(value || 0);
  const startTimeRef = useRef(null);

  useEffect(() => {
    const val = value || 0;
    if (val !== displayValue) {
      startValueRef.current = displayValue;
      endValueRef.current = val;
      startTimeRef.current = performance.now();
      setTimeout(() => setIsAnimating(true), 0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  useEffect(() => {
    if (!isAnimating) return;

    const duration = 1500; // 1.5s total animation

    const easeOutExpo = (t) => {
      return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    };

    const animate = (time) => {
      const elapsed = time - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);

      const easedProgress = easeOutExpo(progress);

      const currentVal = Math.floor(
        startValueRef.current +
        (endValueRef.current - startValueRef.current) * easedProgress,
      );

      setDisplayValue(currentVal);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setDisplayValue(endValueRef.current);
        setIsAnimating(false);
      }
    };

    const reqId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(reqId);
  }, [isAnimating]);

  return (
    <span
      className={cn(
        "font-mono font-bold transition-all duration-300",
        isAnimating
          ? "text-primary drop-shadow-[0_0_8px_rgba(67,56,202,0.8)] scale-[1.15] inline-block"
          : "text-white scale-100",
        className,
      )}
    >
      {displayValue.toLocaleString()} XP
    </span>
  );
}
