export default function PipelineStatus({ status }) {
  return (
    <div className="rounded-2xl border border-teal-400/20 bg-teal-400/10 px-4 py-3 text-sm text-teal-100">
      Pipeline status: <span className="font-semibold">{status}</span>
    </div>
  );
}
