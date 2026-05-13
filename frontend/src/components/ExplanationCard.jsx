import ConfidenceBadge from "./ConfidenceBadge";

export default function ExplanationCard({ explanation }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-orange-300">Structured Explanation</p>
          <h1 className="mt-2 text-3xl font-semibold">{explanation.ticker}</h1>
        </div>
        <ConfidenceBadge confidence={explanation.confidence} />
      </div>

      <div className="mt-6 space-y-5">
        <section>
          <h2 className="text-lg font-semibold text-sand">Summary</h2>
          <p className="mt-2 text-slate-300">{explanation.narrative.summary}</p>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-sand">Trend</h2>
          <p className="mt-2 text-slate-300">{explanation.narrative.trend}</p>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-sand">Feature Insights</h2>
          <ul className="mt-2 list-disc space-y-2 pl-5 text-slate-300">
            {explanation.features.map((item) => (
              <li key={item.feature}>
                {item.feature}: {item.direction} pressure ({item.contribution})
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-sand">Context</h2>
          <p className="mt-2 text-slate-300">{explanation.narrative.context}</p>
        </section>
      </div>
    </article>
  );
}
