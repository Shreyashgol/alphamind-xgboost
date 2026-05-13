from pathlib import Path
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA"]

def generate_csv_data():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range(end="2026-04-24", periods=1000)
    
    np.random.seed(42)
    for ticker in TICKERS:
        start_price = np.random.uniform(100, 300)
        returns = np.random.normal(0, 0.02, size=1000)
        close_prices = start_price * np.exp(np.cumsum(returns))
        
        high_prices = close_prices * np.random.uniform(1.0, 1.05, size=1000)
        low_prices = close_prices * np.random.uniform(0.95, 1.0, size=1000)
        open_prices = close_prices * np.random.uniform(0.98, 1.02, size=1000)
        volumes = np.random.randint(1000000, 50000000, size=1000)
        
        frame = pd.DataFrame({
            "Date": dates.date.astype(str),
            "Open": open_prices,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volumes
        })
        frame.to_csv(UPLOADS_DIR / f"{ticker}.csv", index=False)
        print(f"Generated data for {ticker}")

def generate_pdf_data():
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    
    documents = {
        "AAPL": "Apple (AAPL) continues to expand its Services revenue and iPhone sales globally. The new AI integration is expected to boost margins.",
        "MSFT": "Microsoft (MSFT) Azure cloud growth remains strong, driven by enterprise AI adoption and Copilot subscriptions.",
        "GOOGL": "Alphabet (GOOGL) search advertising revenue is stable, while Google Cloud is seeing accelerated growth.",
        "TSLA": "Tesla (TSLA) is facing pricing pressure but its EV delivery volumes remain high. The energy storage business is growing rapidly."
    }
    
    for ticker, content in documents.items():
        pdf_path = KNOWLEDGE_DIR / f"{ticker}_Q1_Report.pdf"
        c = canvas.Canvas(str(pdf_path))
        c.drawString(100, 750, f"{ticker} Q1 Financial Report")
        c.drawString(100, 700, content)
        c.save()
        print(f"Generated PDF for {ticker}")

def main() -> None:
    generate_csv_data()
    generate_pdf_data()

if __name__ == "__main__":
    main()
