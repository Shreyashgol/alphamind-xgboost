import { useState } from "react";

import { sendQuery } from "../api/alphamind";
import QueryChat from "../components/QueryChat";

export default function Query() {
  const [messages, setMessages] = useState([]);

  async function handleSubmit({ ticker, question }) {
    const response = await sendQuery({ ticker, question });
    setMessages((current) => [
      ...current,
      { role: "user", content: question },
      { role: "assistant", content: response.answer, sources: response.sources },
    ]);
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
      <QueryChat messages={messages} onSubmit={handleSubmit} />
    </section>
  );
}
