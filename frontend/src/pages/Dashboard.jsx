import { useEffect, useRef, useState } from "react";

import { formatApiError, getExplanation, getForecast, getTickers, sendQuery, trainModels } from "../api/alphamind";
import ConfidenceBadge from "../components/ConfidenceBadge";
import ExplanationCard from "../components/ExplanationCard";
import ForecastChart from "../components/ForecastChart";
import PipelineStatus from "../components/PipelineStatus";
import QueryChat from "../components/QueryChat";
import StockSelector from "../components/StockSelector";

export default function Dashboard() {
  const [ticker, setTicker] = useState("AAPL");
  const [horizon, setHorizon] = useState(7);
  const [status, setStatus] = useState("Booting pipeline");
  const [forecast, setForecast] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [availableTickers, setAvailableTickers] = useState([]);
  const [error, setError] = useState("");
  const initialPipelineRun = useRef(false);

  async function runPipeline() {
    const selectedTicker = ticker.trim().toUpperCase();
    if (!selectedTicker) {
      setStatus("Waiting for ticker");
      setError("Enter a ticker symbol before running the pipeline.");
      return;
    }

    try {
      setError("");
      setTicker(selectedTicker);
      setStatus("Training candidate models...");
      await trainModels({ ticker: selectedTicker });

      setStatus("Scoring forecast...");
      const nextForecast = await getForecast({ ticker: selectedTicker, horizon });
      setForecast(nextForecast);

      setStatus("Generating explanation...");
      const nextExplanation = await getExplanation({ ticker: selectedTicker, horizon });
      setExplanation(nextExplanation);
      setStatus("Pipeline complete");
    } catch (nextError) {
      setStatus("Pipeline failed");
      setError(formatApiError(nextError, "Pipeline failed."));
    }
  }

  async function handleQuery({ ticker: selectedTicker, question }) {
    try {
      const response = await sendQuery({ ticker: selectedTicker, question, recency_days: 90 });
      setMessages((current) => [
        ...current,
        { role: "user", content: `${selectedTicker}: ${question}` },
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
          suggestions: response.suggestions,
        },
      ]);
    } catch (nextError) {
      setMessages((current) => [
        ...current,
        { role: "user", content: `${selectedTicker}: ${question}` },
        {
          role: "assistant",
          content: formatApiError(nextError, "I could not answer that query."),
        },
      ]);
    }
  }

  useEffect(() => {
    if (initialPipelineRun.current) {
      return;
    }
    initialPipelineRun.current = true;
    runPipeline();
  }, []);

  useEffect(() => {
    getTickers()
      .then(setAvailableTickers)
      .catch(() => setAvailableTickers(["AAPL", "MSFT", "GOOGL", "TSLA"]));
  }, []);

  return (
    <section className="grid gap-6">
      <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-cyan-950/30">
          <p className="text-sm uppercase tracking-[0.3em] text-teal-300">Auto Pipeline</p>
          <h1 className="mt-3 text-4xl font-semibold text-sand">AlphaMind Dashboard</h1>
          <p className="mt-3 max-w-2xl text-slate-300">
            Type any stock ticker, then refresh the pipeline. Forecasting works when a matching CSV exists in the
            backend uploads folder.
          </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-[minmax(0,220px)_160px_auto] sm:items-end">
            <StockSelector ticker={ticker} onChange={setTicker} options={availableTickers} />
            <label className="flex flex-col gap-2">
              <span className="text-sm font-medium text-slate-300">Horizon</span>
              <input
                className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                type="number"
                min="1"
                max="30"
                value={horizon}
                onChange={(event) => setHorizon(Number(event.target.value))}
              />
            </label>
            <button
              className="rounded-2xl bg-teal-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-teal-400"
              onClick={runPipeline}
              type="button"
            >
              Refresh Pipeline
            </button>
          </div>

          <div className="mt-6">
            <PipelineStatus status={status} />
            {error ? <p className="mt-3 text-sm text-rose-300">{error}</p> : null}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-amber-300">Latest Result</p>
          {forecast ? (
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold">{forecast.ticker}</h2>
                <ConfidenceBadge confidence={forecast.confidence} />
              </div>
              <p className="text-slate-300">
                Predicted price: <span className="font-medium text-white">{forecast.predicted_price}</span>
              </p>
              <p className="text-slate-300">
                Change: <span className="font-medium text-white">{forecast.prediction_percent}%</span>
              </p>
              <p className="text-slate-300">
                Trend: <span className="font-medium capitalize text-white">{forecast.trend}</span>
              </p>
              <p className="text-slate-300">
                Model: <span className="font-medium text-white">{forecast.model.selected}</span>
              </p>
            </div>
          ) : (
            <p className="mt-4 text-slate-400">No pipeline run yet.</p>
          )}
        </div>
      </div>

      {forecast ? (
        <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
          <ForecastChart history={forecast.history} forecast={forecast.forecast} />
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        {explanation ? <ExplanationCard explanation={explanation} /> : null}

        <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Evidence</p>
          <div className="mt-5 space-y-4">
            {(forecast?.context || []).map((item) => (
              <article key={`${item.source}-${item.date}`} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-semibold text-white">{item.source}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.25em] text-slate-400">
                  {item.ticker || "Market"} • {item.date || "Undated"} • score {item.score}
                </p>
                <p className="mt-3 text-sm text-slate-300">{item.summary}</p>
              </article>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
        <QueryChat availableTickers={availableTickers} messages={messages} onSubmit={handleQuery} />
      </div>
    </section>
  );
}
