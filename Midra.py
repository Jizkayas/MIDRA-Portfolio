#!/usr/bin/env python3
"""
MIDRA Portfolio Tracker – Blockfrost
- Token namen + iconen
- NFTs verborgen
- Waarde in EUR / USD / ADA
- Automatische refresh
- Rood/groen bij prijsdaling/stijging
- Meertalig: NL / EN / DE
- Altijd-tonen tokens met prijzen + iconen
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="MIDRA Portfolio", page_icon="₳", layout="wide")

# ==================== VERTALINGEN ====================
TRANSLATIONS = {
    "nl": {
        "settings": "Instellingen",
        "blockfrost_key": "Blockfrost Project ID",
        "address": "Payment Address (addr1...)",
        "hide_nfts": "NFTs verbergen",
        "currency": "Valuta",
        "language": "Taal",
        "fetch_button": "🔄 Portfolio ophalen",
        "auto_refresh": "Auto refresh",
        "refresh_every": "Ververs elke",
        "off": "Uit",
        "seconds": "seconden",
        "free_key": "Gratis key: [blockfrost.io](https://blockfrost.io)",
        "total_value": "Totale portfolio waarde",
        "ada_balance": "ADA Balance",
        "ada_value": "ADA waarde",
        "ada_in": "ADA in",
        "ada_price": "ADA prijs",
        "ada_price_curr": "ADA prijs",
        "stake": "Stake",
        "fungible_tokens": "🪙 Fungible Tokens",
        "no_tokens": "Geen native tokens gevonden op dit address.",
        "only_nfts": "Alleen NFTs gevonden (of geen fungible tokens).",
        "nfts_hidden": "NFT(s) verborgen",
        "token": "Token",
        "amount": "Aantal",
        "price": "Prijs",
        "value": "Waarde",
        "tokens_found": "fungible token(s)",
        "value_ada": "Waarde ADA",
        "value_tokens": "Waarde Tokens",
        "total_portfolio": "Totaal Portfolio",
        "download_csv": "📥 Download CSV",
        "warning_fill": "Vul Blockfrost key + address in.",
        "error_address": "Gebruik een payment address dat begint met `addr1...`",
        "error_fetch": "Kon address niet ophalen. Controleer key en address.",
        "spinner": "Balances, metadata en prijzen ophalen...",
        "info_start": "Vul links je Blockfrost key + `addr1...` address in. Kies een valuta en klik op de knop (of zet auto-refresh aan).",
        "refresh_count": "Refresh",
    },
    "en": {
        "settings": "Settings",
        "blockfrost_key": "Blockfrost Project ID",
        "address": "Payment Address (addr1...)",
        "hide_nfts": "Hide NFTs",
        "currency": "Currency",
        "language": "Language",
        "fetch_button": "🔄 Fetch Portfolio",
        "auto_refresh": "Auto refresh",
        "refresh_every": "Refresh every",
        "off": "Off",
        "seconds": "seconds",
        "free_key": "Free key: [blockfrost.io](https://blockfrost.io)",
        "total_value": "Total portfolio value",
        "ada_balance": "ADA Balance",
        "ada_value": "ADA value",
        "ada_in": "ADA in",
        "ada_price": "ADA price",
        "ada_price_curr": "ADA price",
        "stake": "Stake",
        "fungible_tokens": "🪙 Fungible Tokens",
        "no_tokens": "No native tokens found on this address.",
        "only_nfts": "Only NFTs found (or no fungible tokens).",
        "nfts_hidden": "NFT(s) hidden",
        "token": "Token",
        "amount": "Amount",
        "price": "Price",
        "value": "Value",
        "tokens_found": "fungible token(s)",
        "value_ada": "ADA Value",
        "value_tokens": "Tokens Value",
        "total_portfolio": "Total Portfolio",
        "download_csv": "📥 Download CSV",
        "warning_fill": "Please enter Blockfrost key + address.",
        "error_address": "Use a payment address starting with `addr1...`",
        "error_fetch": "Could not fetch address. Check key and address.",
        "spinner": "Fetching balances, metadata and prices...",
        "info_start": "Enter your Blockfrost key + `addr1...` address on the left. Choose a currency and click the button (or enable auto-refresh).",
        "refresh_count": "Refresh",
    },
    "de": {
        "settings": "Einstellungen",
        "blockfrost_key": "Blockfrost Project ID",
        "address": "Payment Address (addr1...)",
        "hide_nfts": "NFTs ausblenden",
        "currency": "Währung",
        "language": "Sprache",
        "fetch_button": "🔄 Portfolio abrufen",
        "auto_refresh": "Auto-Aktualisierung",
        "refresh_every": "Aktualisieren alle",
        "off": "Aus",
        "seconds": "Sekunden",
        "free_key": "Kostenloser Key: [blockfrost.io](https://blockfrost.io)",
        "total_value": "Gesamter Portfoliowert",
        "ada_balance": "ADA Guthaben",
        "ada_value": "ADA Wert",
        "ada_in": "ADA in",
        "ada_price": "ADA Preis",
        "ada_price_curr": "ADA Preis",
        "stake": "Stake",
        "fungible_tokens": "🪙 Fungible Tokens",
        "no_tokens": "Keine nativen Tokens auf dieser Adresse gefunden.",
        "only_nfts": "Nur NFTs gefunden (oder keine fungible Tokens).",
        "nfts_hidden": "NFT(s) ausgeblendet",
        "token": "Token",
        "amount": "Menge",
        "price": "Preis",
        "value": "Wert",
        "tokens_found": "fungible Token(s)",
        "value_ada": "ADA Wert",
        "value_tokens": "Token Wert",
        "total_portfolio": "Gesamtportfolio",
        "download_csv": "📥 CSV herunterladen",
        "warning_fill": "Bitte Blockfrost-Key + Adresse eingeben.",
        "error_address": "Verwende eine Payment-Adresse die mit `addr1...` beginnt",
        "error_fetch": "Adresse konnte nicht abgerufen werden. Key und Adresse prüfen.",
        "spinner": "Guthaben, Metadaten und Preise werden geladen...",
        "info_start": "Gib links deinen Blockfrost-Key + `addr1...` Adresse ein. Wähle eine Währung und klicke auf den Button (oder aktiviere Auto-Refresh).",
        "refresh_count": "Aktualisierung",
    },
}

def t(key: str) -> str:
    lang = st.session_state.get("lang", "nl")
    return TRANSLATIONS.get(lang, TRANSLATIONS["nl"]).get(key, key)

# ==================== BANNER ====================
components.html("""
<div style="
    background: linear-gradient(135deg, #0a0e27 0%, #0f172a 40%, #1e1b4b 100%);
    border-radius: 16px;
    padding: 36px 32px;
    margin-bottom: 10px;
    border: 1px solid rgba(99, 102, 241, 0.25);
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.15);
    position: relative;
    overflow: hidden;
    font-family: 'Segoe UI', system-ui, sans-serif;
    text-align: center;
">
    <div style="
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
        border-radius: 50%;
    "></div>
    
    <div style="
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #e0e7ff, #c4b5fd, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
    ">
        MIDRA Portfolio
    </div>
</div>
""", height=110)

# Bekende CoinGecko IDs (vaste IDs = betrouwbare prijzen)
COINGECKO_IDS = {
    "ADA": "cardano",
    "WMTX": "world-mobile-token",
    "WMT": "world-mobile-token",
    "MIN": "minswap",
    "SNEK": "snek",
    "NIGHT": "midnight-3",
    "STRIKE": "strike-2",
    "SURGE": "surge-3",
    "BODEGA": "bodega",
    "HOSKY": "hosky",
    "IUSD": "iusd",
    "USDM": "usdm",
    "DJED": "djed",
    "ATLAS": "atlas-2",
}

# Tokens die altijd in het overzicht moeten staan (ook bij saldo 0)
ALWAYS_SHOW_TICKERS = [
    "STRIKE", "SURF", "SURGE", "MIN", "NIGHT",
    "WMTX", "BODEGA", "PALM", "PULSE", "SNEK"
]

# Volledige asset units (policy + asset name hex) voor iconen via Blockfrost
TOKEN_UNITS = {
    "NIGHT":  "0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa4e49474854",
    "SURGE":  "e992ef75f2367e6ecd93716ae88eba0d005dd91fd3a21f650b6496b55355524745",
    "BODEGA": "5deab590a137066fef0e56f06ef1b830f21bc5d544661ba570bdd2ae424f44454741",
    "MIN":    "29d222ce763455e3d7a09a665ce554f00ac89d2e99a1a83d267170c64d494e",
    "SNEK":   "279c909f348e533da5808898f87f9a14bb2c3dfbbacccd631d927a3f534e454b",
    "WMTX":   "e5a42a1a1d3d1da71b0449663c32798725888d2eb0843c4dabeca05a576f726c644d6f62696c65546f6b656e58",
    "STRIKE": "f13ac4d66b3ee19a6aa0f2a22298737bd907cc95121662fc971b5275535452494b45",
    "SURF":   "2d9db8a89f074aa045eab177f23a3395f62ced8b53499a9e4ad46c80464c4f57",
    "PALM":   "b7c5cd554f3e83c8aa0900a0c9053284a5348244d23d0406c28eaf4d50414c4d0a",
    "PULSE":  "2da97f55d49be13dabc8450a2eabab0412f3075a03f7519d32d469250014df1050554c5345",
    # Voeg hier meer units toe (STRIKE, SURF, PALM, PULSE, MIN, SNEK, WMTX)
    # → iconen verschijnen ook bij saldo 0
}

CURRENCY_SYMBOL = {
    "EUR": "€",
    "USD": "$",
    "ADA": "₳",
}

# ==================== SIDEBAR ====================
with st.sidebar:
    lang_options = {"Nederlands": "nl", "English": "en", "Deutsch": "de"}
    selected_lang_label = st.selectbox(
        "🌐 Language / Taal / Sprache",
        options=list(lang_options.keys()),
        index=0
    )
    st.session_state["lang"] = lang_options[selected_lang_label]

    st.header(t("settings"))
    blockfrost_key = st.text_input(
        t("blockfrost_key"),
        type="password",
        placeholder="mainnetxxxxxxxx"
    )
    address = st.text_input(
        t("address"),
        placeholder="addr1q..."
    )
    hide_nfts = st.checkbox(t("hide_nfts"), value=True)

    currency = st.selectbox(
        t("currency"),
        options=["EUR", "USD", "ADA"],
        index=0
    )

    st.markdown("---")

    fetch_button = st.button(t("fetch_button"), type="primary", use_container_width=True)

    st.markdown("---")
    st.subheader(t("auto_refresh"))
    refresh_sec = st.selectbox(
        t("refresh_every"),
        options=[0, 30, 60, 120, 300, 600],
        format_func=lambda x: t("off") if x == 0 else f"{x} {t('seconds')}",
        index=2
    )
    st.caption(t("free_key"))

if refresh_sec > 0:
    count = st_autorefresh(interval=refresh_sec * 1000, key="portfolio_refresh")
    st.sidebar.caption(f"{t('refresh_count')} #{count}")

symbol = CURRENCY_SYMBOL[currency]

# ==================== HELPERS ====================
def bf_get(path: str, key: str):
    url = f"https://cardano-mainnet.blockfrost.io/api/v0/{path}"
    headers = {"project_id": key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def hex_to_text(h: str) -> str:
    if not h:
        return ""
    try:
        return bytes.fromhex(h).decode("utf-8")
    except Exception:
        return h

@st.cache_data(ttl=90)
def get_prices(tickers: tuple, vs_currency: str = "eur") -> dict:
    result = {}
    vs = vs_currency.lower()

    def fetch_ids(ids: list):
        if not ids:
            return {}
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": ",".join(ids),
                    "vs_currencies": vs,
                    "include_24hr_change": "true"
                },
                timeout=10
            )
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return {}

    # ADA
    data = fetch_ids(["cardano"])
    if "cardano" in data:
        result["ADA"] = {
            "price": data["cardano"].get(vs, 0),
            "change": data["cardano"].get(f"{vs}_24h_change", 0) or 0
        }
    else:
        result["ADA"] = {"price": 0, "change": 0}

    # Bekende tokens via vaste CoinGecko IDs
    ids_to_fetch = []
    ticker_to_id = {}
    for t_ticker in tickers:
        t_up = t_ticker.upper().strip()
        if t_up in COINGECKO_IDS:
            cg_id = COINGECKO_IDS[t_up]
            ids_to_fetch.append(cg_id)
            ticker_to_id[cg_id] = t_up

    data = fetch_ids(list(set(ids_to_fetch)))
    for cg_id, ticker in ticker_to_id.items():
        if cg_id in data:
            result[ticker] = {
                "price": data[cg_id].get(vs, 0),
                "change": data[cg_id].get(f"{vs}_24h_change", 0) or 0
            }

    # Onbekende tickers via search (max 8)
    unknown = [
        t_ticker for t_ticker in tickers
        if t_ticker.upper() not in result and t_ticker.upper() != "ADA"
    ]
    for t_ticker in unknown[:8]:
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/search",
                params={"query": t_ticker},
                timeout=8
            )
            if r.status_code == 200:
                coins = r.json().get("coins", [])
                if coins:
                    cg_id = coins[0]["id"]
                    data = fetch_ids([cg_id])
                    if cg_id in data:
                        result[t_ticker.upper()] = {
                            "price": data[cg_id].get(vs, 0),
                            "change": data[cg_id].get(f"{vs}_24h_change", 0) or 0
                        }
        except Exception:
            continue

    return result

def get_asset_info(unit: str, key: str) -> dict:
    data = bf_get(f"assets/{unit}", key)
    if not data:
        return {}

    onchain = data.get("onchain_metadata") or {}
    metadata = data.get("metadata") or {}

    name = (
        metadata.get("name")
        or onchain.get("name")
        or hex_to_text(data.get("asset_name", ""))
        or "Unknown token"
    )
    ticker = metadata.get("ticker") or onchain.get("ticker") or ""
    decimals = metadata.get("decimals")
    if decimals is None:
        decimals = 0

    logo = None
    if metadata.get("logo"):
        logo_data = metadata["logo"]
        if str(logo_data).startswith("http"):
            logo = logo_data
        else:
            logo = f"data:image/png;base64,{logo_data}"
    elif onchain.get("image"):
        img = onchain["image"]
        if isinstance(img, str):
            if img.startswith("ipfs://"):
                logo = img.replace("ipfs://", "https://ipfs.io/ipfs/")
            elif img.startswith("http"):
                logo = img

    return {
        "name": str(name)[:60],
        "ticker": str(ticker)[:15] if ticker else "",
        "decimals": int(decimals),
        "logo": logo,
        "fingerprint": data.get("fingerprint", ""),
        "total_supply": data.get("quantity", "0"),
        "policy_id": data.get("policy_id", unit[:56]),
    }

def format_amount(qty: int, decimals: int) -> str:
    if decimals == 0:
        return f"{qty:,}"
    val = qty / (10 ** decimals)
    return f"{val:,.6f}".rstrip("0").rstrip(".")

def is_likely_nft(qty: int, decimals: int, total_supply: str, ticker: str) -> bool:
    try:
        supply = int(total_supply)
    except Exception:
        supply = 0
    if qty == 1 and decimals == 0 and supply <= 1:
        return True
    if qty == 1 and decimals == 0 and not ticker:
        return True
    return False

def format_value(value: float, change: float = 0, symbol: str = "€") -> str:
    if value == 0:
        return '<span style="color:#888;">—</span>'
    color = "#00c853" if change >= 0 else "#ff1744"
    arrow = " ▲" if change > 0 else (" ▼" if change < 0 else "")
    if symbol == "₳":
        return f'<span style="color:{color}; font-weight:600;">{symbol}{value:,.4f}{arrow}</span>'
    return f'<span style="color:{color}; font-weight:600;">{symbol}{value:,.2f}{arrow}</span>'

def format_price(price: float, change: float = 0, symbol: str = "€") -> str:
    if not price:
        return '<span style="color:#888;">n.b.</span>'
    color = "#00c853" if change >= 0 else "#ff1744"
    txt = f"{symbol}{price:.6f}".rstrip("0").rstrip(".")
    return f'<span style="color:{color};">{txt}</span>'

# ==================== HOOFD ====================
should_fetch = fetch_button or (
    blockfrost_key.strip()
    and address.strip()
    and refresh_sec > 0
)

if should_fetch:

    if not blockfrost_key.strip() or not address.strip():
        st.warning(t("warning_fill"))
        st.stop()

    address = address.strip()
    if not address.startswith(("addr1", "addr_test1")):
        st.error(t("error_address"))
        st.stop()

    with st.spinner(t("spinner")):

        addr_data = bf_get(f"addresses/{address}", blockfrost_key)
        if not addr_data:
            st.error(t("error_fetch"))
            st.stop()

        ada = 0.0
        raw_assets = []

        for amount in addr_data.get("amount", []):
            unit = amount.get("unit", "")
            qty = int(amount.get("quantity", 0))
            if unit == "lovelace":
                ada = qty / 1_000_000
            else:
                raw_assets.append((unit, qty))

        extra = bf_get(f"addresses/{address}/assets", blockfrost_key)
        if extra:
            seen = {u for u, _ in raw_assets}
            for a in extra:
                unit = a.get("unit", "")
                qty = int(a.get("quantity", 0))
                if unit and unit not in seen:
                    raw_assets.append((unit, qty))

        metadata_map = {}
        if raw_assets:
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {
                    executor.submit(get_asset_info, unit, blockfrost_key): (unit, qty)
                    for unit, qty in raw_assets
                }
                for future in as_completed(futures):
                    unit, qty = futures[future]
                    meta = future.result()
                    metadata_map[unit] = {**meta, "quantity": qty}

        # Tickers van holdings + altijd-tonen tokens
        tickers = list(ALWAYS_SHOW_TICKERS)
        for info in metadata_map.values():
            tk = info.get("ticker") or info.get("name", "")[:10]
            if tk and tk.upper() not in [x.upper() for x in tickers]:
                tickers.append(tk)

        vs = "usd" if currency == "USD" else "eur"
        prices = get_prices(tuple(set(tickers)), vs_currency=vs)

        ada_info = prices.get("ADA", {"price": 0, "change": 0})
        ada_price = ada_info.get("price", 0)
        ada_change = ada_info.get("change", 0)

    # ========== WEERGAVE ==========
    if currency == "ADA":
        ada_value = ada
        ada_display_price = 1.0
    else:
        ada_value = ada * ada_price
        ada_display_price = ada_price

    total_tokens_value = 0.0
    tokens = []
    nfts_hidden = 0

    if metadata_map:
        for unit, info in metadata_map.items():
            qty = info.get("quantity", 0)
            decimals = info.get("decimals", 0)
            ticker = (info.get("ticker") or "").upper()
            name = info.get("name", "Unknown")
            total_supply = info.get("total_supply", "0")

            if hide_nfts and is_likely_nft(qty, decimals, total_supply, ticker):
                nfts_hidden += 1
                continue

            human_amount = qty / (10 ** decimals) if decimals else qty

            price = 0.0
            change = 0.0
            if ticker and ticker in prices:
                price = prices[ticker].get("price", 0)
                change = prices[ticker].get("change", 0)
            else:
                for k, v in prices.items():
                    if k.upper() in name.upper() or name.upper() in k.upper():
                        price = v.get("price", 0)
                        change = v.get("change", 0)
                        break

            if currency == "ADA" and ada_price > 0:
                price = price / ada_price
                value = human_amount * price
            else:
                value = human_amount * price

            total_tokens_value += value

            tokens.append({
                "logo": info.get("logo"),
                "name": name,
                "ticker": ticker or "—",
                "amount": format_amount(qty, decimals),
                "price": price,
                "value": value,
                "change": change,
                "fingerprint": info.get("fingerprint", ""),
                "policy": info.get("policy_id", unit[:56]),
            })

    # Altijd-tonen tokens toevoegen als ze nog niet in de lijst staan
    held_tickers = {tok["ticker"].upper() for tok in tokens if tok["ticker"] != "—"}

    missing_units = []
    for ticker in ALWAYS_SHOW_TICKERS:
        if ticker.upper() not in held_tickers and ticker in TOKEN_UNITS:
            missing_units.append((ticker, TOKEN_UNITS[ticker]))

    extra_meta = {}
    if missing_units and blockfrost_key.strip():
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(get_asset_info, unit, blockfrost_key): ticker
                for ticker, unit in missing_units
            }
            for future in as_completed(futures):
                ticker = futures[future]
                meta = future.result()
                if meta:
                    extra_meta[ticker] = meta

    for ticker in ALWAYS_SHOW_TICKERS:
        if ticker.upper() in held_tickers:
            continue

        price = 0.0
        change = 0.0
        if ticker in prices:
            price = prices[ticker].get("price", 0)
            change = prices[ticker].get("change", 0)

        if currency == "ADA" and ada_price > 0 and price > 0:
            price = price / ada_price

        meta = extra_meta.get(ticker, {})
        tokens.append({
            "logo": meta.get("logo"),
            "name": meta.get("name") or ticker,
            "ticker": ticker,
            "amount": "0",
            "price": price,
            "value": 0.0,
            "change": change,
            "fingerprint": meta.get("fingerprint", ""),
            "policy": meta.get("policy_id", ""),
        })

    # Sorteren: waarde hoog → laag, daarna alfabetisch
    tokens.sort(key=lambda x: (-x["value"], (x["name"] or x["ticker"]).lower()))

    total_portfolio = ada_value + total_tokens_value
    total_color = "#00c853" if ada_change >= 0 else "#ff1744"

    if currency == "ADA":
        total_str = f"{symbol}{total_portfolio:,.4f}"
    else:
        total_str = f"{symbol}{total_portfolio:,.2f}"

    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px 0 30px 0;">
            <div style="font-size: 28px; color: #888; margin-bottom: 6px;">{t("total_value")}</div>
            <div style="font-size: 56px; font-weight: 700; color: {total_color};">
                {total_str}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    c1.metric(t("ada_balance"), f"{ada:,.6f} ₳")

    if currency == "ADA":
        c2.metric(t("ada_value"), f"{symbol}{ada_value:,.4f}")
        c3.metric(t("ada_price"), "1 ₳")
    else:
        c2.metric(
            f"{t('ada_in')} {currency}",
            f"{symbol}{ada_value:,.2f}" if ada_price else "—",
            delta=f"{ada_change:+.2f}%" if ada_price else None
        )
        c3.metric(
            f"{t('ada_price_curr')} ({currency})",
            f"{symbol}{ada_display_price:.4f}" if ada_price else "—",
            delta=f"{ada_change:+.2f}%" if ada_price else None
        )

    st.caption(f"{t('stake')}: `{addr_data.get('stake_address') or '—'}`")
    st.divider()
    st.subheader(t("fungible_tokens"))

    if not tokens:
        st.info(t("no_tokens"))
    else:
        h = st.columns([1, 4, 2, 2, 2])
        h[1].markdown(f"**{t('token')}**")
        h[2].markdown(f"**{t('amount')}**")
        h[3].markdown(f"**{t('price')} ({currency})**")
        h[4].markdown(f"**{t('value')} ({currency})**")

        for tok in tokens:
            cols = st.columns([1, 4, 2, 2, 2])
            with cols[0]:
                if tok["logo"]:
                    try:
                        st.image(tok["logo"], width=36)
                    except Exception:
                        st.write("🪙")
                else:
                    st.write("🪙")
            with cols[1]:
                st.markdown(f"**{tok['name']}**")
                if tok["ticker"] != "—":
                    st.caption(tok["ticker"])
            with cols[2]:
                st.markdown(f"**{tok['amount']}**")
            with cols[3]:
                st.markdown(
                    format_price(tok["price"], tok.get("change", 0), symbol),
                    unsafe_allow_html=True
                )
            with cols[4]:
                st.markdown(
                    format_value(tok["value"], tok.get("change", 0), symbol),
                    unsafe_allow_html=True
                )

        st.success(f"**{len(tokens)}** {t('tokens_found')}")
        if nfts_hidden:
            st.caption(f"{nfts_hidden} {t('nfts_hidden')}")

        st.divider()
        tc1, tc2, tc3 = st.columns(3)

        if currency == "ADA":
            tc1.metric(t("value_ada"), f"{symbol}{ada_value:,.4f}")
            tc2.metric(t("value_tokens"), f"{symbol}{total_tokens_value:,.4f}")
            tc3.metric(t("total_portfolio"), f"{symbol}{total_portfolio:,.4f}")
        else:
            tc1.metric(t("value_ada"), f"{symbol}{ada_value:,.2f}")
            tc2.metric(t("value_tokens"), f"{symbol}{total_tokens_value:,.2f}")
            tc3.metric(t("total_portfolio"), f"{symbol}{total_portfolio:,.2f}")

        df = pd.DataFrame([{
            t("token"): tok["name"],
            "Ticker": tok["ticker"],
            t("amount"): tok["amount"],
            f"{t('price')} {currency}": tok["price"],
            "24h %": round(tok.get("change", 0), 2),
            f"{t('value')} {currency}": round(tok["value"], 6 if currency == "ADA" else 2),
            "Policy ID": tok["policy"],
        } for tok in tokens])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            t("download_csv"),
            data=csv,
            file_name=f"cardano_portfolio_{currency.lower()}.csv",
            mime="text/csv"
        )

else:
    st.info(t("info_start"))