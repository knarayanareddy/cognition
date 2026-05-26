/**
 * CL Score band colour display from F-05.
 * Bands: OPTIMAL(green), MODERATE(yellow), HIGH(orange), CRITICAL(red), BURNOUT(dark red)
 */

interface ScoreBandProps {
  score: number;
  band: string;
  size?: "sm" | "md" | "lg";
}

const BAND_COLORS: Record<string, string> = {
  OPTIMAL: "text-green-400",
  MODERATE: "text-yellow-400",
  HIGH: "text-orange-400",
  CRITICAL: "text-red-500",
  BURNOUT: "text-red-800",
};

const BAND_BG: Record<string, string> = {
  OPTIMAL: "bg-green-500/10 border-green-500/30",
  MODERATE: "bg-yellow-500/10 border-yellow-500/30",
  HIGH: "bg-orange-500/10 border-orange-500/30",
  CRITICAL: "bg-red-500/10 border-red-500/30",
  BURNOUT: "bg-red-900/10 border-red-900/30",
};

const SIZE_CLASSES = {
  sm: "text-2xl",
  md: "text-4xl",
  lg: "text-6xl",
};

export function ScoreBand({ score, band, size = "lg" }: ScoreBandProps) {
  const color = BAND_COLORS[band] || "text-gray-400";
  const bg = BAND_BG[band] || "bg-gray-800 border-gray-700";

  return (
    <div className={`rounded-xl p-4 border ${bg}`}>
      <div className={`font-bold ${color} ${SIZE_CLASSES[size]}`}>{score}</div>
      <div className={`text-sm mt-1 ${color} font-medium`}>{band}</div>
    </div>
  );
}
