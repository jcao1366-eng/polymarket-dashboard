RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "AUD": 1.53,
    "CAD": 1.36,
}
SYMBOLS = {
    "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "AUD": "A$", "CAD": "C$"
}

def convert(amount, from_currency="USD", to_currency="USD"):
    usd = amount / RATES.get(from_currency, 1.0)
    return round(usd * RATES.get(to_currency, 1.0), 2)

def format_price(amount, currency="USD"):
    return f"{SYMBOLS.get(currency, '$')}{amount:,.2f}"
