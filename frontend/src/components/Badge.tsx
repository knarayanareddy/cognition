/**
 * Badge component for LIVE/MOCK and LIVE/DRY-RUN indicators.
 * Required by F-06 and F-02: UI must display badges on every card.
 */

interface BadgeProps {
  type: "live" | "mock" | "dry-run";
}

export function Badge({ type }: BadgeProps) {
  const styles = {
    live: "bg-green-500/20 text-green-400 border-green-500/30",
    mock: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    "dry-run": "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  };

  return (
    <span
      className={`px-2 py-0.5 text-xs font-semibold rounded border uppercase ${styles[type]}`}
    >
      {type}
    </span>
  );
}
