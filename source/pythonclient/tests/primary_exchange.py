SUFFIX_MAP = {
    # Canada
    "TO": {"primaryExchange": "TSE", "currency": "CAD"},
    # Espagne
    "MC": {"primaryExchange": "BM", "currency": "EUR"},
    # Italie
    "MI": {"primaryExchange": "BVME", "currency": "EUR"},
    # Allemagne
    "DE": {"primaryExchange": "IBIS", "currency": "EUR"},   # Xetra
    "F":  {"primaryExchange": "FWB",  "currency": "EUR"},   # Frankfurt
    # Pays-Bas
    "AS": {"primaryExchange": "AEB", "currency": "EUR"},
    # Belgique
    "BR": {"primaryExchange": "ENEXT.BE", "currency": "EUR"},
    # France
    "PA": {"primaryExchange": "SBF", "currency": "EUR"},
    # Suisse
    "SW": {"primaryExchange": "EBS", "currency": "CHF"},
    # Royaume-Uni
    "L": {"primaryExchange": "LSE", "currency": "GBP"},
    # Suède
    "ST": {"primaryExchange": "SFB", "currency": "SEK"},
    # Norvège
    "OL": {"primaryExchange": "OSE", "currency": "NOK"},
    # Danemark
    "CO": {"primaryExchange": "CPH", "currency": "DKK"},
    # Finlande
    "HE": {"primaryExchange": "HEX", "currency": "EUR"},
    # Portugal
    "LS": {"primaryExchange": "BVLP", "currency": "EUR"},
    # États-Unis (souvent pas de suffixe dans ton flux)
    "US": {"primaryExchange": None, "currency": "USD"},
}

def parse_stock_and_suffix(raw_stock: str):
    raw_stock = str(raw_stock).strip().upper()
    if "." in raw_stock:
        symbol, suffix = raw_stock.rsplit(".", 1)
    else:
        symbol, suffix = raw_stock, None
    return symbol, suffix


def get_expected_contract_info(raw_stock: str):
    symbol, suffix = parse_stock_and_suffix(raw_stock)

    info = {
        "raw_stock": raw_stock,
        "symbol": symbol,
        "suffix": suffix,
        "primaryExchange": None,
        "currency": None,
    }

    if suffix in SUFFIX_MAP:
        info["primaryExchange"] = SUFFIX_MAP[suffix]["primaryExchange"]
        info["currency"] = SUFFIX_MAP[suffix]["currency"]

    return info