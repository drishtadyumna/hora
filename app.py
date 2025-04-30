import json
import time as pytime
from datetime import date

import requests
import streamlit as st

# -------------------------------------------------------------------
#  🔯  Jyotish Data — Vedic Divisional Charts for AI Workflows
# -------------------------------------------------------------------
st.set_page_config(page_title="Vedic Divisional Charts", layout="centered")

# ----------  Global CSS  ----------
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

st.markdown("## 🔯 Jyotish Data - For AI analysis")
st.markdown("---")

# -------------------------------------------------------------------
# Personal API-key input
# -------------------------------------------------------------------
st.markdown(
    """
    **Optional — use your own API key**

    • Go to <https://freeastrologyapi.com/> and sign-up (free) to get a personal key.  
    • Paste it below for a higher rate-limit or leave blank to use the demo key that
      ships with this app.
    """
)

def _save_api_key():
    """Keeps st.session_state.user_api_key in sync with the widget value."""
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
API_BASE_URL          = "https://json.freeastrologyapi.com/"
GEOCODE_API_URL       = "https://geocode.maps.co/search"
GEOCODE_API_KEY       = "680561227fda9856529449uxwa70717"
DEFAULT_ASTRO_API_KEY = "1pK0yvcDkMaS750G6v2VA8lglgTm1bcO3thzyrTK"
API_CALL_DELAY        = 1.0  # seconds between successive API calls

SIGN_NAMES = {
    1: "Aries",        2: "Taurus",       3: "Gemini",      4: "Cancer",
    5: "Leo",          6: "Virgo",        7: "Libra",       8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn",   11: "Aquarius",   12: "Pisces",
}

CHART_ENDPOINTS = {
    "D1 (Rasi Chart)"          : "planets",
    "Planets Extended Info"    : "planets/extended",
    "D2 (Hora Chart)"          : "d2-chart-info",
    "D3 (Drekkana Chart)"      : "d3-chart-info",
    "D4 (Chaturthamsa Chart)"  : "d4-chart-info",
    "D5 (Panchamsa Chart)"     : "d5-chart-info",
    "D6 (Shasthamsa Chart)"    : "d6-chart-info",
    "D7 (Saptamsa Chart)"      : "d7-chart-info",
    "D8 (Ashtamsa Chart)"      : "d8-chart-info",
    "D9 (Navamsa Chart)"       : "navamsa-chart-info",
    "D10 (Dasamsa Chart)"      : "d10-chart-info",
    "D11 (Rudramsa Chart)"     : "d11-chart-info",
    "D12 (Dwadasamsa Chart)"   : "d12-chart-info",
    "D16 (Shodasamsa Chart)"   : "d16-chart-info",
    "D20 (Vimsamsa Chart)"     : "d20-chart-info",
    "D24 (Siddhamsa Chart)"    : "d24-chart-info",
    "D27 (Nakshatramsa Chart)" : "d27-chart-info",
    "D30 (Trimsamsa Chart)"    : "d30-chart-info",
    "D40 (Khavedamsa Chart)"   : "d40-chart-info",
    "D45 (Akshavedamsa Chart)" : "d45-chart-info",
    "D60 (Shashtyamsa Chart)"  : "d60-chart-info",
}

TIMEZONE_OPTIONS = {
    "UTC−12:00 Intl Date Line West": -12.0,
    "UTC−11:00 Midway Island, Samoa": -11.0,
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
    "name","year","month","date","hours","minutes","seconds",
    "latitude","longitude","timezone","observation_point","ayanamsha"
]

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def fetch_astro_data(key: str, endpoint: str, payload: dict) -> dict:
    """Call FreeAstrologyAPI and return its JSON or a structured error."""
    if not key:
        return {"statusCode": 400, "error": "API key missing."}

    try:
        r = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json", "x-api-key": key},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        try:
            details = r.json().get("message", r.text)
        except Exception:
            details = r.text
        st.error(f"API HTTP Error {r.status_code}: {details[:500]}")
        return {"statusCode": r.status_code, "error": f"HTTP {r.status_code}", "details": details}
    except requests.exceptions.Timeout:
        st.error("API request timed out.")
        return {"statusCode": 408, "error": "Request Timeout"}
    except requests.exceptions.RequestException as ex:
        st.error(f"API Request Error: {ex}")
        return {"statusCode": None, "error": "Request Exception", "details": str(ex)}
    except Exception as ex:  # pragma: no cover
        st.error(f"Unexpected error: {ex}")
        return {"statusCode": None, "error": "Unexpected Exception", "details": str(ex)}


def fetch_coordinates(place: str):
    """Simple wrapper around geocode.maps.co."""
    place = place.strip()
    if not place:
        return None, None, "Please enter a place name."

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
        return None, None, f"Could not find coordinates for '{place}'."
    except Exception as ex:
        st.error(f"Geocode error: {ex}")
        return None, None, str(ex)


def flatten_planet_output(raw_output):
    """Flattens the sometimes nested structure that FreeAstrologyAPI returns."""
    name_map = {"1": "Sun", "2": "Moon", "3": "Mars", "4": "Mercury", "5": "Jupiter",
                "6": "Venus", "7": "Saturn", "8": "Rahu", "9": "Ketu"}
    out = {}

    def ingest(d: dict):
        for k, v in d.items():
            if isinstance(v, dict):
                pname = v.get("name") or name_map.get(str(k), str(k))
                out[pname] = v

    if isinstance(raw_output, dict):
        ingest(raw_output)
    elif isinstance(raw_output, list):
        for chunk in raw_output:
            if isinstance(chunk, dict):
                ingest(chunk)
    return out


def generate_readable(birth_info: dict, results_dict: dict) -> str:
    """Create the human friendly TXT summary that can be downloaded."""
    sec = f"{birth_info.get('seconds', 0):02d}"
    lines = [
        "========================================",
        "BIRTH DETAILS",
        f"Name: {birth_info.get('name','N/A')}",
        f"Date: {birth_info.get('year')}-{birth_info.get('month'):02d}-{birth_info.get('date'):02d}",
        f"Time: {birth_info.get('hours'):02d}:{birth_info.get('minutes'):02d}:{sec}",
        f"Location: Lat {birth_info.get('latitude'):.4f}, Lon {birth_info.get('longitude'):.4f}",
    ]

    tz_val = birth_info.get("timezone", 0.0)
    tz_label = next((lbl for lbl, val in TIMEZONE_OPTIONS.items() if val == tz_val),
                    f"UTC{tz_val:+g}")
    lines.append(f"Timezone: {tz_label}")
    lines.append(f"Ayanamsha: {birth_info.get('ayanamsha')}")
    lines.append(f"Observation Point: {birth_info.get('observation_point')}")
    lines.extend(["========================================", ""])

    preferred = ["Ascendant", "Sun", "Moon", "Mars", "Mercury",
                 "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for chart_name, raw in results_dict.items():
        lines.append(f"-- {chart_name} --")
        if raw.get("statusCode") != 200:
            lines.append(f"ERROR: {raw.get('error', 'Unknown')}\n")
            continue

        planets = flatten_planet_output(raw.get("output", {}))
        shown = set()

        def _append_line(pname: str, info: dict):
            csign = SIGN_NAMES.get(info.get("current_sign"), "Unknown")
            deg = info.get("normDegree")
            # The API sometimes omits normDegree for certain bodies
            if deg is None:
                return
            retro = str(info.get("isRetro", "false")).lower() in ("true", "1")
            lines.append(f"{pname}: {csign} {deg:.2f}°, {'Retro' if retro else 'Direct'}")

        for p in preferred:
            if p in planets:
                shown.add(p)
                _append_line(p, planets[p])

        for p, dat in planets.items():
            if p not in shown:
                _append_line(p, dat)

        lines.append("")

    lines.extend([
        "========================================",
        "BIRTH JSON:",
        json.dumps(birth_info, indent=2),
        "========================================",
    ])
    return "\n".join(lines)


# -------------------------------------------------------------------
# Session State (initialisation)
# -------------------------------------------------------------------
if "birth_info"      not in st.session_state: st.session_state.birth_info = {}
if "results"         not in st.session_state: st.session_state.results    = None
if "readable"        not in st.session_state: st.session_state.readable   = None
if "user_api_key"    not in st.session_state: st.session_state.user_api_key = ""
if "obs_input"       not in st.session_state: st.session_state.obs_input  = "topocentric"
if "ayn_input"       not in st.session_state: st.session_state.ayn_input  = "lahiri"

# initialise check-boxes for every chart
default_selected = {"D1 (Rasi Chart)", "Planets Extended Info",
                    "D9 (Navamsa Chart)", "D10 (Dasamsa Chart)"}
for c in CHART_ENDPOINTS:
    st.session_state.setdefault(f"cb_{c}", c in default_selected)

# -------------------------------------------------------------------
# EXPANDER: load saved JSON
# -------------------------------------------------------------------
def _load_from_json():
    raw = st.session_state.json_input.strip()
    if not raw:
        st.warning("JSON input empty."); return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as ex:
        st.error(f"Invalid JSON: {ex}"); return

    missing = [k for k in EXPECTED_BI_KEYS if k not in data]
    if missing:
        st.error(f"JSON missing keys: {', '.join(missing)}"); return

    clean = {}
    try:
        for k in EXPECTED_BI_KEYS:
            if k in ("year", "month", "date", "hours", "minutes", "seconds"):
                clean[k] = int(data[k])
            elif k in ("latitude", "longitude", "timezone"):
                clean[k] = float(data[k])
            else:
                clean[k] = str(data[k])
    except Exception as ex:
        st.error(f"Value conversion error: {ex}"); return

    st.session_state.birth_info = clean
    st.session_state.obs_input  = clean.get("observation_point", "topocentric")
    st.session_state.ayn_input  = clean.get("ayanamsha", "lahiri")
    st.session_state.results = st.session_state.readable = None
    st.success("Birth details loaded.")
    st.session_state.json_input = ""
    st.experimental_rerun()


with st.expander("Load Saved Birth JSON"):
    st.text_area("Paste JSON here:", key="json_input", height=150)
    st.button("Load JSON", on_click=_load_from_json)

st.markdown("---")

# -------------------------------------------------------------------
# Birth Details & Settings
# -------------------------------------------------------------------
st.subheader("Birth Details & Settings")
bi = st.session_state.birth_info

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name:", bi.get("name", ""), key="name_input")

    try:
        default_bd = date(int(bi.get("year", 2000)),
                          int(bi.get("month", 1)),
                          int(bi.get("date", 1)))
        default_bd = max(date(1800, 1, 1), min(default_bd, date.today()))
    except Exception:
        default_bd = date(2000, 1, 1)

    bd = st.date_input("Birth Date:", value=default_bd,
                       min_value=date(1800, 1, 1), max_value=date.today())

    st.markdown("**Birth Time (24-hour)**")
    t1, t2, t3 = st.columns(3)
    hr = t1.number_input("Hour",    0, 23, bi.get("hours",   12), format="%d")
    mi = t2.number_input("Minute",  0, 59, bi.get("minutes",  0), format="%d")
    se = t3.number_input("Second",  0, 59, bi.get("seconds",  0), format="%d")

with col2:
    st.markdown("**Lookup Coordinates**")
    st.text_input("Place (e.g. New York, USA):", key="place_input")
    def _do_geocode():
        place = st.session_state.place_input
        lat_, lon_, msg = fetch_coordinates(place)
        if lat_ is not None:
            st.session_state.birth_info["latitude"]  = lat_
            st.session_state.birth_info["longitude"] = lon_
            st.success(f"Coordinates set for {msg}")
            st.experimental_rerun()
        else:
            st.error(f"Geocoding failed: {msg}")

    st.button("Fetch Coordinates", on_click=_do_geocode)

    st.markdown("**Latitude / Longitude**")
    lat = st.number_input("Latitude",  -90.0,  90.0,
                          bi.get("latitude", 0.0),  format="%.4f")
    lon = st.number_input("Longitude", -180.0, 180.0,
                          bi.get("longitude", 0.0), format="%.4f")

    st.markdown("**Timezone**")
    current_tz = bi.get("timezone", 5.5)
    try:
        tz_idx = TIMEZONE_LABELS.index(next(lbl for lbl,val in TIMEZONE_OPTIONS.items()
                                            if val == current_tz))
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

# write back into session
st.session_state.birth_info = {
    "name": name,
    "year": bd.year,   "month": bd.month, "date": bd.day,
    "hours": hr,       "minutes": mi,     "seconds": se,
    "latitude": lat,   "longitude": lon,  "timezone": tz_value,
    "observation_point": obs,  "ayanamsha": ayn
}

st.markdown("---")

# -------------------------------------------------------------------
# Chart selection
# -------------------------------------------------------------------
st.subheader("Select Charts to Fetch")
c1, c2 = st.columns(2)
if c1.button("Select All Charts"):
    for c in CHART_ENDPOINTS: st.session_state[f"cb_{c}"] = True
    st.experimental_rerun()
if c2.button("Unselect All Charts"):
    for c in CHART_ENDPOINTS: st.session_state[f"cb_{c}"] = False
    st.experimental_rerun()

cols = st.columns(3)
selection = {}
per_col = (len(CHART_ENDPOINTS) + len(cols) - 1) // len(cols)
for i, chart in enumerate(CHART_ENDPOINTS):
    col = cols[i // per_col]
    selection[chart] = col.checkbox(chart, st.session_state[f"cb_{chart}"],
                                    key=f"cb_{chart}")

# -------------------------------------------------------------------
# Fetch API data
# -------------------------------------------------------------------
if st.button("Fetch Astrological Data", type="primary"):
    bi_now = st.session_state.birth_info
    missing = [k for k in EXPECTED_BI_KEYS if bi_now.get(k) in (None, "")]
    if missing:
        st.error(f"Missing: {', '.join(missing)}")
    else:
        charts = [c for c, sel in selection.items() if sel]
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
                }
            }

            res_all = {}
            bar = st.progress(0.0)
            for idx, ch in enumerate(charts, start=1):
                res_all[ch] = fetch_astro_data(api_key, CHART_ENDPOINTS[ch], payload)
                bar.progress(idx / len(charts))
                pytime.sleep(API_CALL_DELAY)

            st.session_state.results  = res_all
            st.session_state.readable = generate_readable(bi_now, res_all)
            st.success("Fetch complete.")
            st.experimental_rerun()

# -------------------------------------------------------------------
# Display results & download
# -------------------------------------------------------------------
st.markdown("---")
if st.session_state.get("results"):
    st.subheader("Results & Downloads")

    safe_name = "".join(c for c in st.session_state.birth_info.get("name", "chart")
                        if c.isalnum() or c in "-_") or "chart"
    date_str  = (
        f"{st.session_state.birth_info.get('date'):02d}-"
        f"{st.session_state.birth_info.get('month'):02d}-"
        f"{st.session_state.birth_info.get('year')}"
    )
    base_name = f"{safe_name}-{date_str}"
    raw_json  = json.dumps(st.session_state.results, indent=2, ensure_ascii=False)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button("💾 Download Chart JSON",
                           raw_json,
                           file_name=f"{base_name}-ChartData.json",
                           mime="application/json")
    with col_dl2:
        st.download_button("💾 Download Readable TXT",
                           st.session_state.readable,
                           file_name=f"{base_name}-ReadableSummary.txt",
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
        keep_api = st.session_state.get("user_api_key", "")
        st.session_state.clear()
        st.session_state.user_api_key = keep_api
        st.experimental_rerun()

st.markdown("---")
st.caption("Built with Streamlit • Astrology data © freeastrologyapi.com • Geocoding by geocode.maps.co")
