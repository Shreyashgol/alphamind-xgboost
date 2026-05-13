export default function ConfidenceBadge({ confidence }) {
  const label = typeof confidence === "object" ? confidence.label : null;
  const score = typeof confidence === "object" ? confidence.score : confidence;
  const displayScore = Number.isFinite(score) ? `${(score * 100).toFixed(0)}%` : "pending";

  return (
    <span className="rounded-full border border-amber-300/30 bg-amber-300/10 px-3 py-1 text-sm font-semibold text-amber-200">
      {label ? `Confidence ${label}` : `Confidence ${displayScore}`}
    </span>
  );
}
