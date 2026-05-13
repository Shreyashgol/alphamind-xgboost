import { useEffect, useState } from "react";

import { getForecast, getTickers } from "../api/alphamind";
import ConfidenceBadge from "../components/ConfidenceBadge";
import ForecastChart from "../components/ForecastChart";
import StockSelector from "../components/StockSelector";

export default function Forecast() {
  const [ticker, setTicker] = useState("AAPL");
  const [forecast, setForecast] = useState(null);
  const [availableTickers, setAvailableTickers] = useState([]);

  async function loadForecast() {
    const data = await getForecast({ ticker, horizon: 7 });
    setForecast(data);
  }

  useEffect(() => {
    getTickers()
      .then(setAvailableTickers)
      .catch(() => setAvailableTickers(["AAPL", "MSFT", "GOOGL", "TSLA"]));
  }, []);

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <StockSelector ticker={ticker} onChange={setTicker} options={availableTickers} />
          <button
            className="rounded-2xl bg-amber-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-amber-300"
            onClick={loadForecast}
            type="button"
          >
            Load Forecast
          </button>
        </div>
      </div>

      {forecast && (
        <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-semibold">{forecast.ticker} Forecast</h1>
              <p className="text-slate-400">Selected model: {forecast.model.selected}</p>
            </div>
            <ConfidenceBadge confidence={forecast.confidence} />
          </div>
          <ForecastChart history={forecast.history} forecast={forecast.forecast} />
        </div>
      )}
    </section>
  );
}
