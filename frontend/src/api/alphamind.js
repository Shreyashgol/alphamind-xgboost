import axios from "axios";

const configuredBaseUrl = (import.meta.env.VITE_API_URL || "").trim();

const client = axios.create({
  baseURL: configuredBaseUrl || (import.meta.env.DEV ? "http://127.0.0.1:8000" : ""),
});

export function formatApiError(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item?.msg) {
          const location = Array.isArray(item.loc) ? item.loc.join(".") : item.loc;
          return location ? `${location}: ${item.msg}` : item.msg;
        }
        return JSON.stringify(item);
      })
      .join(" ");
  }
  if (detail && typeof detail === "object") {
    return detail.msg || JSON.stringify(detail);
  }
  return error?.message || fallback;
}

export async function trainModels(payload) {
  const { data } = await client.post("/api/train", payload);
  return data;
}

export async function getTickers() {
  const { data } = await client.get("/api/tickers");
  return data.tickers || [];
}

export async function getForecast(payload) {
  const { data } = await client.get("/api/forecast", {
    params: payload,
  });
  return data;
}

export async function getExplanation(payload) {
  const { data } = await client.get("/api/explain", {
    params: payload,
  });
  return data;
}

export async function sendQuery(payload) {
  const { data } = await client.post("/api/query", payload);
  return data;
}
