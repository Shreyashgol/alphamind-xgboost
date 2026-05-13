import { useState } from "react";

const defaultSuggestions = [
  "What are the strongest upside drivers?",
  "What risks could weaken the forecast?",
  "Which sources support this answer?",
  "How does the retrieved context align with the forecast?",
];

export default function QueryChat({ messages, onSubmit, ticker: activeTicker, availableTickers = [] }) {
  const [ticker, setTicker] = useState("AAPL");
  const [question, setQuestion] = useState("");
  const [isSending, setIsSending] = useState(false);
  const selectedTicker = activeTicker || ticker;

  async function handleSubmit(event) {
    event.preventDefault();
    if (!question.trim()) {
      return;
    }
    if (!selectedTicker.trim()) {
      setQuestion("Please enter a ticker first.");
      return;
    }
    setIsSending(true);
    try {
      await onSubmit({ ticker: selectedTicker.trim().toUpperCase(), question });
      setQuestion("");
    } finally {
      setIsSending(false);
    }
  }

  function askSuggestion(nextQuestion) {
    setQuestion(nextQuestion);
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">RAG Chat</p>
        <h1 className="mt-2 text-3xl font-semibold">Knowledge Query</h1>
      </div>

      <form className="grid gap-4 rounded-3xl border border-white/10 bg-white/5 p-4" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-2">
          <span className="text-sm text-slate-300">Ticker</span>
          <input
            className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white"
            list="chat-tickers"
            placeholder="Type any ticker"
            value={selectedTicker}
            onChange={(event) => setTicker(event.target.value.trim().toUpperCase())}
          />
          <datalist id="chat-tickers">
            {availableTickers.map((option) => (
              <option key={option} value={option} />
            ))}
          </datalist>
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm text-slate-300">Question</span>
          <textarea
            className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white"
            placeholder="Ask what is driving the stock or what the market backdrop looks like."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
        </label>

        <div className="flex flex-wrap gap-2">
          {defaultSuggestions.map((suggestion) => (
            <button
              className="rounded-full border border-cyan-300/30 px-3 py-2 text-left text-sm text-cyan-100 transition hover:bg-cyan-300/10"
              key={suggestion}
              onClick={() => askSuggestion(`${suggestion} for ${selectedTicker}?`)}
              type="button"
            >
              {suggestion}
            </button>
          ))}
        </div>

        <button
          className="w-fit rounded-2xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isSending}
          type="submit"
        >
          {isSending ? "Thinking..." : "Ask"}
        </button>
      </form>

      <div className="space-y-4">
        {messages.length === 0 ? (
          <p className="text-slate-400">No messages yet. Ask a question to query the local knowledge base.</p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`rounded-3xl p-4 ${
                message.role === "user" ? "bg-white/5 text-white" : "bg-cyan-400/10 text-cyan-50"
              }`}
            >
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">{message.role}</p>
              <p className="mt-2">{message.content}</p>
              {message.sources?.length ? (
                <p className="mt-3 text-sm text-cyan-200">Sources: {message.sources.join(", ")}</p>
              ) : null}
              {message.suggestions?.length ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  {message.suggestions.map((suggestion) => (
                    <button
                      className="rounded-full border border-white/10 px-3 py-2 text-left text-xs text-cyan-100 transition hover:bg-white/10"
                      key={suggestion}
                      onClick={() => askSuggestion(suggestion)}
                      type="button"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
