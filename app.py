import json
import time as pytime
from datetime import date

import requests
import streamlit as st

# -------------------------------------------------------------------
# 🔯 Jyotish Data — Vedic Divisional Charts for AI Workflows
# -------------------------------------------------------------------
st.set_page_config(page_title="Vedic Divisional Charts", layout="centered")

# ---------- Global CSS ----------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap');
      html, body, [class*="css"] { font-family: 'Noto Sans', sans-serif; }
      #MainMenu, footer { visibility: hidden; }
      button[kind="primary"] {
        background-color: #7c5c35 !important;
        color: #f7f3ec !important;
        border-radius: 5px;
      }
      .main .block-container { max-width:900px; margin:auto; padding:2rem 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 🔯 Jyotish Data – For AI analysis")
st.markdown("---")

# -------------------------------------------------------------------
# Personal API-key input
# -------------------------------------------------------------------
st.markdown(
    """
    **Optional — use your own API key**

    • Go to <https://freeastrologyapi.com/> and sign-up (free) to get a personal key.  
    • Paste it below for higher rate-limits, or leave blank to use the demo key bundled with this app.
    - 5EIAafVray9EwCr2Lz1kB1ofbkUmzoy76kbGnRav
    """
)


def _save_api_key():
    st.session_state.user_api_key = st.session_state.api_key_widget.strip()


st.text_input(
    "FreeAstrologyAPI key (leave blank to use default)",
    key="api_key_widget",
    type="password",
    placeholder="Paste your key here",
    on_change=_save_api_key,
)

st.markdown("---")

# -------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------
API_BASE_URL = "https://json.freeastrologyapi.com/"
GEOCODE_API_URL = "https://geocode.maps.co/search"
GEOCODE_API_KEY = "680561227fda9856529449uxwa70717"
DEFAULT_ASTRO_API_KEY = "1pK0yvcDkMaS750G6v2VA8lglgTm1bcO3thzyrTK"
API_CALL_DELAY = 1.0  # seconds between successive requests

SIGN_NAMES = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer", 5: "Leo", 6: "Virgo",
    7: "Libra", 8: "Scorpio", 9: "Sagittarius", 10: "Capricorn",
    11: "Aquarius", 12: "Pisces",
}

CHART_ENDPOINTS = {
    "D1 (Rasi Chart)": "planets",
    "Planets Extended Info": "planets/extended",
    "D2 (Hora Chart)": "d2-chart-info",
    "D3 (Drekkana Chart)": "d3-chart-info",
    "D4 (Chaturthamsa Chart)": "d4-chart-info",
    "D5 (Panchamsa Chart)": "d5-chart-info",
    "D6 (Shasthamsa Chart)": "d6-chart-info",
    "D7 (Saptamsa Chart)": "d7-chart-info",
    "D8 (Ashtamsa Chart)": "d8-chart-info",
    "D9 (Navamsa Chart)": "navamsa-chart-info",
    "D10 (Dasamsa Chart)": "d10-chart-info",
    "D11 (Rudramsa Chart)": "d11-chart-info",
    "D12 (Dwadasamsa Chart)": "d12-chart-info",
    "D16 (Shodasamsa Chart)": "d16-chart-info",
    "D20 (Vimsamsa Chart)": "d20-chart-info",
    "D24 (Siddhamsa Chart)": "d24-chart-info",
    "D27 (Nakshatramsa Chart)": "d27-chart-info",
    "D30 (Trimsamsa Chart)": "d30-chart-info",
    "D40 (Khavedamsa Chart)": "d40-chart-info",
    "D45 (Akshavedamsa Chart)": "d45-chart-info",
    "D60 (Shashtyamsa Chart)": "d60-chart-info",
}

TIMEZONE_OPTIONS = {
    "UTC−12:00 Intl Date Line W": -12.0,
    "UTC−11:00 Midway/Samoa": -11.0,
    "UTC−10:00 Hawaii": -10.0,
    "UTC−09:30 Marquesas": -9.5,
    "UTC−09:00 Alaska": -9.0,
    "UTC−08:00 Pacific": -8.0,
    "UTC−07:00 Mountain": -7.0,
    "UTC−06:00 Central": -6.0,
    "UTC−05:00 Eastern": -5.0,
    "UTC±00:00 GMT": 0.0,
    "UTC+01:00 CET": 1.0,
    "UTC+02:00 EET": 2.0,
    "UTC+03:00 Moscow/Nairobi": 3.0,
    "UTC+03:30 Tehran": 3.5,
    "UTC+04:00 Abu Dhabi": 4.0,
    "UTC+04:30 Kabul": 4.5,
    "UTC+05:00 Yekaterinburg": 5.0,
    "UTC+05:30 IST": 5.5,
    "UTC+05:45 Nepal": 5.75,
    "UTC+06:00 Dhaka": 6.0,
    "UTC+06:30 Yangon": 6.5,
    "UTC+07:00 Bangkok": 7.0,
    "UTC+08:00 Beijing": 8.0,
    "UTC+08:45 Eucla": 8.75,
    "UTC+09:00 Tokyo": 9.0,
    "UTC+09:30 Adelaide": 9.5,
    "UTC+10:00 Sydney": 10.0,
    "UTC+10:30 Lord Howe": 10.5,
    "UTC+11:00 Magadan": 11.0,
    "UTC+12:00 Auckland": 12.0,
    "UTC+12:45 Chatham": 12.75,
    "UTC+13:00 Tonga": 13.0,
    "UTC+14:00 Line Islands": 14.0,
}
TIMEZONE_LABELS = list(TIMEZONE_OPTIONS.keys())

EXPECTED_BI_KEYS = [
    "name", "year", "month", "date",
    "hours", "minutes", "seconds",
    "latitude", "longitude", "timezone",
    "observation_point", "ayanamsha",
]

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def fetch_astro_data(api_key: str, endpoint: str, payload: dict) -> dict:
    if not api_key:
        return {"statusCode": 400, "error": "API key missing."}
    try:
        r = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json", "x-api-key": api_key},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        try:
            msg = r.json().get("message", r.text)
        except Exception:
            msg = r.text
        st.error(f"HTTP {r.status_code}: {msg}")
        return {"statusCode": r.status_code, "error": msg}
    except requests.exceptions.Timeout:
        st.error("API request timed out.")
        return {"statusCode": 408, "error": "timeout"}
    except Exception as ex:  # pragma: no cover
        st.error(f"Request error: {ex}")
        return {"statusCode": None, "error": str(ex)}


def fetch_coordinates(place: str):
    place = place.strip()
    if not place:
        return None, None, "Please enter a place."

    try:
        params = {"q": place, "limit": 1}
        if GEOCODE_API_KEY:
            params["api_key"] = GEOCODE_API_KEY
        r = requests.get(GEOCODE_API_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json() or []
        if isinstance(data, list) and data:
            hit = data[0]
            return float(hit["lat"]), float(hit["lon"]), hit.get("display_name", place)
        return None, None, f"No match for '{place}'."
    except Exception as ex:
        return None, None, str(ex)


def flatten_planet_output(raw):
    name_map = {"1": "Sun", "2": "Moon", "3": "Mars", "4": "Mercury",
                "5": "Jupiter", "6": "Venus", "7": "Saturn",
                "8": "Rahu", "9": "Ketu"}
    out = {}

    def ingest(d):
        for k, v in d.items():
            if isinstance(v, dict):
                pname = v.get("name") or name_map.get(str(k), str(k))
                out[pname] = v

    if isinstance(raw, dict):
        ingest(raw)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                ingest(item)
    return out


def generate_readable(bi: dict, results: dict) -> str:
    sec = f"{bi.get('seconds', 0):02d}"
    lines = [
        "========================================",
        "BIRTH DETAILS",
        f"Name: {bi.get('name','N/A')}",
        f"Date: {bi.get('year')}-{bi.get('month'):02d}-{bi.get('date'):02d}",
        f"Time: {bi.get('hours'):02d}:{bi.get('minutes'):02d}:{sec}",
        f"Location: Lat {bi.get('latitude'):.4f}, Lon {bi.get('longitude'):.4f}",
    ]
    tz_val = bi.get("timezone", 0.0)
    tz_label = next((l for l, v in TIMEZONE_OPTIONS.items() if v == tz_val),
                    f"UTC{tz_val:+g}")
    lines.append(f"Timezone: {tz_label}")
    lines.append(f"Ayanamsha: {bi.get('ayanamsha')}")
    lines.append(f"Observation Point: {bi.get('observation_point')}")
    lines.extend(["========================================", ""])

    pref = ["Ascendant", "Sun", "Moon", "Mars", "Mercury",
            "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for chart, raw in results.items():
        lines.append(f"-- {chart} --")
        if raw.get("statusCode") != 200:
            lines.append(f"ERROR: {raw.get('error', 'Unknown')}\n")
            continue
        planets = flatten_planet_output(raw.get("output", {}))
        shown = set()

        def add_line(p, info):
            deg = info.get("normDegree")
            if deg is None:
                return
            sign = SIGN_NAMES.get(info.get("current_sign"), "Unknown")
            retro = str(info.get("isRetro", "false")).lower() in ("true", "1")
            lines.append(f"{p}: {sign} {deg:.2f}°, {'Retro' if retro else 'Direct'}")

        for p in pref:
            if p in planets:
                shown.add(p)
                add_line(p, planets[p])
        for p, info in planets.items():
            if p not in shown:
                add_line(p, info)
        lines.append("")

    lines.extend([
        "========================================",
        "BIRTH JSON:",
        json.dumps(bi, indent=2),
        "========================================",
    ])
    return "\n".join(lines)


# -------------------------------------------------------------------
# Session-state defaults
# -------------------------------------------------------------------
if "birth_info" not in st.session_state:
    st.session_state.birth_info = {}
if "results" not in st.session_state:
    st.session_state.results = None
if "readable" not in st.session_state:
    st.session_state.readable = None
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
if "obs_input" not in st.session_state:
    st.session_state.obs_input = "topocentric"
if "ayn_input" not in st.session_state:
    st.session_state.ayn_input = "lahiri"

default_checked = {"D1 (Rasi Chart)", "Planets Extended Info",
                   "D9 (Navamsa Chart)", "D10 (Dasamsa Chart)"}
for chart in CHART_ENDPOINTS:
    st.session_state.setdefault(f"cb_{chart}", chart in default_checked)

# -------------------------------------------------------------------
# Load JSON expander
# -------------------------------------------------------------------
def _load_json():
    raw = st.session_state.json_input.strip()
    if not raw:
        st.warning("JSON input empty."); return
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as ex:
        st.error(f"Invalid JSON: {ex}"); return
    missing = [k for k in EXPECTED_BI_KEYS if k not in data]
    if missing:
        st.error(f"Missing keys: {', '.join(missing)}"); return

    clean = {}
    for k in EXPECTED_BI_KEYS:
        try:
            if k in ("year", "month", "date", "hours", "minutes", "seconds"):
                clean[k] = int(data[k])
            elif k in ("latitude", "longitude", "timezone"):
                clean[k] = float(data[k])
            else:
                clean[k] = str(data[k])
        except Exception as ex:
            st.error(f"Bad value for {k}: {ex}"); return

    st.session_state.birth_info = clean
    st.session_state.obs_input = clean["observation_point"]
    st.session_state.ayn_input = clean["ayanamsha"]
    st.session_state.results = st.session_state.readable = None
    st.success("Birth details loaded.")
    st.session_state.json_input = ""
    st.rerun()


with st.expander("Load Saved Birth JSON"):
    st.text_area("Paste JSON here:", key="json_input", height=150)
    st.button("Load JSON", on_click=_load_json)

st.markdown("---")

# -------------------------------------------------------------------
# Birth details UI
# -------------------------------------------------------------------
st.subheader("Birth Details & Settings")
bi = st.session_state.birth_info

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name:", bi.get("name", ""))

    try:
        default_bd = date(int(bi.get("year", 2000)),
                          int(bi.get("month", 1)),
                          int(bi.get("date", 1)))
        default_bd = max(date(1800, 1, 1), min(default_bd, date.today()))
    except Exception:
        default_bd = date(2000, 1, 1)

    bd = st.date_input("Birth Date:",
                       value=default_bd,
                       min_value=date(1800, 1, 1),
                       max_value=date.today())

    st.markdown("**Birth Time (24-hour)**")
    t1, t2, t3 = st.columns(3)
    hr = t1.number_input("Hour",   0, 23, bi.get("hours",   12), format="%d")
    mi = t2.number_input("Minute", 0, 59, bi.get("minutes",  0), format="%d")
    se = t3.number_input("Second", 0, 59, bi.get("seconds",  0), format="%d")

with col2:
    st.markdown("**Lookup Coordinates**")
    st.text_input("Place (e.g. New York, USA):", key="place_input")

    def _do_geocode():
        lat_, lon_, msg = fetch_coordinates(st.session_state.place_input)
        if lat_ is not None:
            st.session_state.birth_info["latitude"] = lat_
            st.session_state.birth_info["longitude"] = lon_
            st.success(f"Coordinates set for {msg}")
            st.rerun()
        else:
            st.error(f"Geocoding failed: {msg}")

    st.button("Fetch Coordinates", on_click=_do_geocode)

    st.markdown("**Latitude / Longitude**")
    lat = st.number_input("Latitude",  -90.0,  90.0, bi.get("latitude",  0.0), format="%.4f")
    lon = st.number_input("Longitude", -180.0, 180.0, bi.get("longitude", 0.0), format="%.4f")

    st.markdown("**Timezone**")
    current_tz = bi.get("timezone", 5.5)
    try:
        tz_idx = TIMEZONE_LABELS.index(next(lbl for lbl, v in TIMEZONE_OPTIONS.items()
                                            if v == current_tz))
    except StopIteration:
        tz_idx = TIMEZONE_LABELS.index("UTC+05:30 IST")
    tz_label = st.selectbox("Select Timezone:", TIMEZONE_LABELS, index=tz_idx)
    tz_value = TIMEZONE_OPTIONS[tz_label]

with st.expander("Advanced Calculation Settings"):
    obs_opts = ["topocentric", "geocentric"]
    ayn_opts = ["lahiri", "sayana"]
    obs = st.selectbox("Observation Point:", obs_opts,
                       index=obs_opts.index(st.session_state.obs_input))
    ayn = st.selectbox("Ayanamsha:", ayn_opts,
                       index=ayn_opts.index(st.session_state.ayn_input))
    st.session_state.obs_input = obs
    st.session_state.ayn_input = ayn

# Save back
st.session_state.birth_info = {
    "name": name,
    "year": bd.year, "month": bd.month, "date": bd.day,
    "hours": hr, "minutes": mi, "seconds": se,
    "latitude": lat, "longitude": lon, "timezone": tz_value,
    "observation_point": obs, "ayanamsha": ayn,
}

st.markdown("---")

# -------------------------------------------------------------------
# Chart selection
# -------------------------------------------------------------------
st.subheader("Select Charts to Fetch")
c1, c2 = st.columns(2)
if c1.button("Select All Charts"):
    for ch in CHART_ENDPOINTS:
        st.session_state[f"cb_{ch}"] = True
    st.rerun()
if c2.button("Unselect All Charts"):
    for ch in CHART_ENDPOINTS:
        st.session_state[f"cb_{ch}"] = False
    st.rerun()

cols = st.columns(3)
selected = {}
per = (len(CHART_ENDPOINTS) + len(cols) - 1) // len(cols)
for i, ch in enumerate(CHART_ENDPOINTS):
    col = cols[i // per]
    selected[ch] = col.checkbox(ch, st.session_state[f"cb_{ch}"], key=f"cb_{ch}")

# -------------------------------------------------------------------
# Fetch button
# -------------------------------------------------------------------
if st.button("Fetch Astrological Data", type="primary"):
    bi_now = st.session_state.birth_info
    missing = [k for k in EXPECTED_BI_KEYS if bi_now.get(k) in (None, "")]
    if missing:
        st.error(f"Missing: {', '.join(missing)}")
    else:
        charts = [c for c, v in selected.items() if v]
        if not charts:
            st.warning("Select at least one chart.")
        else:
            st.info(f"Fetching {len(charts)} chart(s)…")
            api_key = st.session_state.user_api_key or DEFAULT_ASTRO_API_KEY

            payload = {
                "year": bi_now["year"], "month": bi_now["month"], "date": bi_now["date"],
                "hours": bi_now["hours"], "minutes": bi_now["minutes"], "seconds": bi_now["seconds"],
                "latitude": bi_now["latitude"], "longitude": bi_now["longitude"],
                "timezone": bi_now["timezone"],
                "settings": {
                    "observation_point": bi_now["observation_point"],
                    "ayanamsha": bi_now["ayanamsha"],
                    "language": "en",
                },
            }

            res_all = {}
            bar = st.progress(0.0)
            for idx, ch in enumerate(charts, start=1):
                res_all[ch] = fetch_astro_data(api_key, CHART_ENDPOINTS[ch], payload)
                bar.progress(idx / len(charts))
                pytime.sleep(API_CALL_DELAY)

            st.session_state.results = res_all
            st.session_state.readable = generate_readable(bi_now, res_all)
            st.success("Fetch complete.")
            st.rerun()

# -------------------------------------------------------------------
# Display results
# -------------------------------------------------------------------
st.markdown("---")
if st.session_state.get("results"):
    st.subheader("Results & Downloads")

    safe_name = "".join(c for c in st.session_state.birth_info.get("name", "chart")
                        if c.isalnum() or c in "-_") or "chart"
    date_str = (
        f"{st.session_state.birth_info.get('date'):02d}-"
        f"{st.session_state.birth_info.get('month'):02d}-"
        f"{st.session_state.birth_info.get('year')}"
    )
    base = f"{safe_name}-{date_str}"
    raw_json = json.dumps(st.session_state.results, indent=2, ensure_ascii=False)

    cdl1, cdl2 = st.columns(2)
    with cdl1:
        st.download_button("💾 Download Chart JSON",
                           raw_json,
                           file_name=f"{base}-ChartData.json",
                           mime="application/json")
    with cdl2:
        st.download_button("💾 Download Readable TXT",
                           st.session_state.readable,
                           file_name=f"{base}-ReadableSummary.txt",
                           mime="text/plain")

    with st.expander("Readable Summary"):
        st.text_area("", st.session_state.readable, height=350, disabled=True)
    with st.expander("Raw JSON"):
        st.json(st.session_state.results)

# -------------------------------------------------------------------
# Reset
# -------------------------------------------------------------------
with st.expander("Reset Session"):
    if st.button("🔄 Clear Session & Reset"):
        keep = st.session_state.get("user_api_key", "")
        st.session_state.clear()
        st.session_state.user_api_key = keep
        st.rerun()

st.markdown("---")
st.caption("Built with Streamlit • Astrology data © freeastrologyapi.com • Geocoding by geocode.maps.co")
