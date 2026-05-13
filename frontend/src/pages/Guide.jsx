const steps = [
  {
    title: "Prepare Stock Data",
    body: "Add a CSV named like TICKER.csv inside backend/data/uploads. It must include date, open, high, low, close, and volume columns.",
  },
  {
    title: "Add Knowledge",
    body: "Drop PDF or TXT reports, earnings notes, analyst summaries, or company documents into backend/data/knowledge. AlphaMind retrieves this context for explanations and chat.",
  },
  {
    title: "Run Forecast",
    body: "Open the dashboard, type any ticker, choose a horizon from 1 to 30 trading days, and refresh the pipeline.",
  },
  {
    title: "Ask Better Questions",
    body: "Use the chat to ask about drivers, risks, supporting sources, context alignment, and what extra documents would improve an answer.",
  },
];

const questionIdeas = [
  "What are the strongest upside drivers for NVDA?",
  "What risks could weaken the forecast for AAPL?",
  "Which retrieved sources support this answer?",
  "How does the forecast align with the retrieved context?",
  "What files should I add to analyze this ticker better?",
];

export default function Guide() {
  return (
    <section className="grid gap-6">
      <div className="border-b border-white/10 pb-6">
        <p className="text-sm uppercase tracking-[0.3em] text-teal-300">User Guide</p>
        <h1 className="mt-3 text-4xl font-semibold text-sand">How to Use AlphaMind</h1>
        <p className="mt-3 max-w-3xl text-slate-300">
          AlphaMind forecasts from local stock CSVs, retrieves local financial documents, and turns both into
          explainable answers. Add your data first, then use any ticker symbol in the dashboard.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {steps.map((step, index) => (
          <article className="rounded-2xl border border-white/10 bg-slate-900/70 p-5" key={step.title}>
            <p className="text-sm font-semibold text-amber-200">Step {index + 1}</p>
            <h2 className="mt-2 text-xl font-semibold text-white">{step.title}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">{step.body}</p>
          </article>
        ))}
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 className="text-2xl font-semibold text-white">Good Chat Questions</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          {questionIdeas.map((question) => (
            <span className="rounded-full border border-cyan-300/30 px-4 py-2 text-sm text-cyan-100" key={question}>
              {question}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
        <h2 className="text-2xl font-semibold text-white">Data Format</h2>
        <pre className="mt-4 overflow-x-auto rounded-2xl bg-slate-950/80 p-4 text-sm text-slate-200">
          <code>{`Date,Open,High,Low,Close,Volume
2026-04-20,188.10,191.50,186.80,190.24,58200000`}</code>
        </pre>
      </div>
    </section>
  );
}
