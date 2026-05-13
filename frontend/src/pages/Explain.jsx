import { useState } from "react";

import { getExplanation } from "../api/alphamind";
import ExplanationCard from "../components/ExplanationCard";
import StockSelector from "../components/StockSelector";

export default function Explain() {
  const [ticker, setTicker] = useState("AAPL");
  const [explanation, setExplanation] = useState(null);

  async function loadExplanation() {
    const data = await getExplanation({ ticker, horizon: 7 });
    setExplanation(data);
  }

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <StockSelector ticker={ticker} onChange={setTicker} />
          <button
            className="rounded-2xl bg-orange-500 px-5 py-3 font-semibold text-white transition hover:bg-orange-400"
            onClick={loadExplanation}
            type="button"
          >
            Generate Explanation
          </button>
        </div>
      </div>

      {explanation && <ExplanationCard explanation={explanation} />}
    </section>
  );
}
