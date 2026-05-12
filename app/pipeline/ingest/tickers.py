# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""Ticker universes for U.S. (NYSE / Nasdaq, S&P 500 subset) and KASE (.KZ)."""

# All entries are S&P 500 constituents listed on NYSE or Nasdaq.
# Grouped by sector for readability; exchange noted in trailing comment.
US_TICKERS = [
    # Mega-cap tech / semis (Nasdaq except where noted)
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AVGO", "ADBE",
    "AMD", "INTC", "CSCO", "QCOM", "TXN", "INTU", "PANW", "MU", "AMAT", "LRCX",
    "ORCL",   # NYSE
    "CRM",    # NYSE
    "IBM",    # NYSE
    "NOW",    # NYSE
    # Financials (NYSE except where noted)
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "SCHW", "USB",
    "SPGI", "ICE", "CME", "MCO",
    # Healthcare (NYSE except where noted)
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN",   # Nasdaq
    "GILD",   # Nasdaq
    "REGN",   # Nasdaq
    "VRTX",   # Nasdaq
    # Consumer
    "WMT", "HD", "MCD", "NKE", "TGT", "LOW", "DIS",   # NYSE
    "COST", "SBUX", "NFLX", "BKNG",                    # Nasdaq
    # Industrials / Energy (NYSE)
    "BA", "CAT", "GE", "HON", "RTX", "LMT", "UPS", "DE",
    "XOM", "CVX", "COP", "SLB", "EOG",
    # Communication / Staples / Payments
    "T", "VZ", "KO", "PG", "MA", "V",   # NYSE
    "CMCSA", "PEP",                      # Nasdaq
    # Newer growth / fintech
    "UBER", "PLTR", "SNOW", "NET",       # NYSE
    "ABNB", "DDOG", "CRWD", "ZS", "MDB", "PYPL",  # Nasdaq
    "XYZ",                                # NYSE (formerly SQ / Block)
    "SHOP",                               # NYSE (Shopify, US-listed)
]

# KASE codes as used by kase.kz's TradingView UDF endpoint (no suffix).
KASE_TICKERS = [
    "AAFD", "ADLA", "ADRP", "AIRA", "AKGR", "AKRL", "AKZM", "ALMS", "ALMT",
    "ALTV", "AMAN", "AMGZp", "AMXP", "ASBN", "ASKQ", "ASKQp", "ASLF", "ASTL",
    "ATEC", "AZNO", "AZNOp", "BAST", "BSUL", "CCBN", "CCBNp", "CRMG", "CSEC",
    "EKTN", "EXCS", "EXCSp", "EXPA", "FFIN", "FHRP", "GB_ALTN", "HSBK", "IFDR",
    "INBNp", "JRES", "KASE", "KATR", "KATRp", "KCEL", "KEGC", "KMCP", "KMGD",
    "KMGZ", "KOZN", "KSNF", "KSPI", "KZAP", "KZAZ", "KZHR", "KZIK", "KZTK",
    "KZTKp", "KZTO", "LNPT", "LOGC", "LZGR", "MATN", "MKBW", "MMGZ", "MMGZp",
    "MREK", "NRBN", "NRBNp6", "PHYS", "PZVA", "RAHT", "RGBR", "RGBRp", "SABR",
    "SABRp", "SAS_", "SATC", "SATCp", "SHUP", "SHZN", "SKSL", "TMLZ", "TPIB",
    "TRRX", "TSBN", "TSBNp", "ULBS", "UTMK", "UTMKp",
]

KASE_NAMES: dict[str, str] = {
    "AAFD": "AsiaAgroFood", "ADLA": "Aidala Munai", "ADRP": "Aidarly Project",
    "AIRA": "Air Astana", "AKGR": "Akzhal Gold Resources", "AKRL": "Ai Karaauyl",
    "AKZM": "Aktobe Metalware Plant", "ALMS": "AK Altynalmas", "ALMT": "AltaMet Minerals",
    "ALTV": "AlmaTel Kazakhstan", "AMAN": "Altay Resources", "AMGZp": "Aktobe Petroleum (pref)",
    "AMXP": "Asker Munai Exploration", "ASBN": "ForteBank", "ASKQ": "ALTYN SAMRUK QAZAQSTAN",
    "ASKQp": "ALTYN SAMRUK QAZAQSTAN (pref)", "ASLF": "LIC Freedom Life", "ASTL": "ASTEL",
    "ATEC": "AltynEx", "AZNO": "Aktobe Oil Equipment Plant", "AZNOp": "Aktobe Oil Equipment Plant (pref)",
    "BAST": "BAST", "BSUL": "Bayan Sulu", "CCBN": "Bank CenterCredit",
    "CCBNp": "Bank CenterCredit (pref)", "CRMG": "Crystal Management", "CSEC": "Centras Securities",
    "EKTN": "EKOTON+", "EXCS": "EXCS", "EXCSp": "EXCS (pref)",
    "EXPA": "Green Power Generation", "FFIN": "Freedom Finance", "FHRP": "FHRP",
    "GB_ALTN": "AltynGold plc", "HSBK": "Halyk Bank", "IFDR": "Teniz Capital Investment Banking",
    "INBNp": "Bank RBK (pref)", "JRES": "Joint Resources", "KASE": "KASE",
    "KATR": "Atameken-Agro", "KATRp": "Atameken-Agro (pref)", "KCEL": "Kcell",
    "KEGC": "KEGOC", "KMCP": "Kazakhmys Copper", "KMGD": "KM GOLD",
    "KMGZ": "KazMunayGas (National Company)", "KOZN": "KoZhaN", "KSNF": "Caspi neft",
    "KSPI": "Kaspi.kz", "KZAP": "NAC Kazatomprom", "KZAZ": "KazAzot",
    "KZHR": "Karazhyra", "KZIK": "Kazakhstan Housing Company", "KZTK": "Kazakhtelecom",
    "KZTKp": "Kazakhtelecom (pref)", "KZTO": "KazTransOil", "LNPT": "KMK Munai",
    "LOGC": "LOGYCOM", "LZGR": "Leasing Group", "MATN": "Maten Petroleum",
    "MKBW": "Maikuben-West", "MMGZ": "Mangistaumunaigaz", "MMGZp": "Mangistaumunaigaz (pref)",
    "MREK": "MRENC", "NRBN": "Nurbank", "NRBNp6": "Nurbank (pref, series 6)",
    "PHYS": "Phystech II", "PZVA": "PZVA", "RAHT": "LOTTE Rakhat",
    "RGBR": "RG Brands", "RGBRp": "RG Brands (pref)", "SABR": "Sinoasia B&R Insurance",
    "SABRp": "Sinoasia B&R Insurance (pref)", "SAS_": "S.A.S.", "SATC": "Fincraft Resources",
    "SATCp": "Fincraft Resources (pref)", "SHUP": "Shubarkol Premium", "SHZN": "ShalkiyaZinc",
    "SKSL": "LIC Standard Life", "TMLZ": "ForteLeasing", "TPIB": "Tengri Partners Investment Banking",
    "TRRX": "Terrox Metals", "TSBN": "Alatau City Bank", "TSBNp": "Alatau City Bank (pref)",
    "ULBS": "ULMUS BESSHOKY", "UTMK": "Ust-Kamenogorsk Titanium Magnesium Plant",
    "UTMKp": "Ust-Kamenogorsk Titanium Magnesium Plant (pref)",
}
