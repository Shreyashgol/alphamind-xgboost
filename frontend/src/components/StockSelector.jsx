export default function StockSelector({ ticker, onChange, options = [] }) {
  const listId = "available-tickers";

  return (
    <label className="flex min-w-[200px] flex-col gap-2">
      <span className="text-sm font-medium text-slate-300">Stock</span>
      <input
        className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
        list={listId}
        placeholder="Type any ticker, e.g. NVDA"
        value={ticker}
        onChange={(event) => onChange(event.target.value.trim().toUpperCase())}
      />
      <datalist id={listId}>
        {options.map((option) => (
          <option key={option} value={option} />
        ))}
      </datalist>
    </label>
  );
}
