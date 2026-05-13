import Plot from "react-plotly.js";

export default function ForecastChart({ history = [], forecast = [] }) {
  const hasHistory = history.length > 0;
  const hasForecast = forecast.length > 0;

  return (
    <Plot
      data={[
        hasHistory
          ? {
              type: "candlestick",
              name: "History",
              x: history.map((point) => point.date),
              open: history.map((point) => point.open),
              high: history.map((point) => point.high),
              low: history.map((point) => point.low),
              close: history.map((point) => point.close),
              increasing: { line: { color: "#34d399" } },
              decreasing: { line: { color: "#f97316" } },
            }
          : null,
        hasForecast
          ? {
              type: "scatter",
              mode: "lines+markers",
              name: "Forecast",
              x: forecast.map((point) => point.date),
              y: forecast.map((point) => point.value),
              line: { color: "#2dd4bf", width: 3 },
              marker: { color: "#f59e0b", size: 8 },
            }
          : null,
      ].filter(Boolean)}
      layout={{
        title: hasHistory ? "Candlestick History and Forecast Overlay" : "Forecast Path",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(15,23,42,0.2)",
        font: { color: "#e2e8f0" },
        xaxis: { rangeslider: { visible: false } },
        margin: { l: 40, r: 20, t: 50, b: 40 },
      }}
      style={{ width: "100%", height: "420px" }}
      useResizeHandler
    />
  );
}
