import streamlit as st
import requests
import json
from datetime import datetime, date
import time as pytime

# -------------------------------------------------------------------
# 🔯 Jyotish Data — Vedic Divisional Charts for AI Workflows
#
# Purpose:
#   This app generates structured JSON and plain‑text exports of
#   Vedic divisional (Varga) charts (D1–D60 + extended planet info)
#   ready to feed into any AI LLM (ChatGPT, Claude, etc.) for analysis.
#
# Geocoding API (Maps.co):
#   API Key: 680561227fda9856529449uxwa70717
# -------------------------------------------------------------------

# --- Page config & global CSS ---
st.set_page_config(page_title="Vedic Divisional Charts", layout="centered")
st.markdown("""
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
""", unsafe_allow_html=True)

# --- Header with Shatkona Emoji 🔯 ---
st.markdown("## 🔯 Jyotish Data")
st.markdown("---")

# --- Constants ---
API_BASE_URL          = "https://json.freeastrologyapi.com/"
GEOCODE_API_URL       = "https://geocode.maps.co/search"
GEOCODE_API_KEY       = "680561227fda9856529449uxwa70717"
DEFAULT_ASTRO_API_KEY = "DLqLK8YIvw8evOKHCExxB5UD146lcAsa69vd6Oqy"
API_CALL_DELAY        = 1.0

SIGN_NAMES = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer", 5: "Leo", 6: "Virgo",
    7: "Libra", 8: "Scorpio", 9: "Sagittarius", 10: "Capricorn",
    11: "Aquarius", 12: "Pisces"
}
for i in range(32):
    SIGN_NAMES.setdefault(i, f"Unknown({i})")

CHART_ENDPOINTS = {
    "D1 (Rasi Chart)":           "planets",
    "Planets Extended Info":     "planets/extended",
    "D2 (Hora Chart)":           "d2-chart-info",
    "D3 (Drekkana Chart)":       "d3-chart-info",
    "D4 (Chaturthamsa Chart)":   "d4-chart-info",
    "D5 (Panchamsa Chart)":      "d5-chart-info",
    "D6 (Shasthamsa Chart)":     "d6-chart-info",
    "D7 (Saptamsa Chart)":       "d7-chart-info",
    "D8 (Ashtamsa Chart)":       "d8-chart-info",
    "D9 (Navamsa Chart)":        "navamsa-chart-info",
    "D10 (Dasamsa Chart)":       "d10-chart-info",
    "D11 (Rudramsa Chart)":      "d11-chart-info",
    "D12 (Dwadasamsa Chart)":    "d12-chart-info",
    "D16 (Shodasamsa Chart)":    "d16-chart-info",
    "D20 (Vimsamsa Chart)":      "d20-chart-info",
    "D24 (Siddhamsa Chart)":     "d24-chart-info",
    "D27 (Nakshatramsa Chart)":  "d27-chart-info",
    "D30 (Trimsamsa Chart)":     "d30-chart-info",
    "D40 (Khavedamsa Chart)":    "d40-chart-info",
    "D45 (Akshavedamsa Chart)":  "d45-chart-info",
    "D60 (Shashtyamsa Chart)":   "d60-chart-info",
}

TIMEZONE_OPTIONS = {
    "UTC−12:00 International Date Line West": -12.0,
    "UTC−11:00 Midway Island, Samoa":        -11.0,
    "UTC−10:00 Hawaii":                      -10.0,
    "UTC−09:30 Marquesas Islands":           -9.5,
    "UTC−09:00 Alaska":                      -9.0,
    "UTC−08:00 Pacific Time (US & Canada)":  -8.0,
    "UTC−07:00 Mountain Time (US & Canada)": -7.0,
    "UTC−06:00 Central Time (US & Canada)":  -6.0,
    "UTC−05:00 Eastern Time (US & Canada)":  -5.0,
    "UTC±00:00 GMT":                          0.0,
    "UTC+01:00 CET":                          1.0,
    "UTC+02:00 EET":                          2.0,
    "UTC+03:00 Moscow, Nairobi":              3.0,
    "UTC+03:30 Tehran":                       3.5,
    "UTC+04:00 Abu Dhabi":                    4.0,
    "UTC+04:30 Kabul":                        4.5,
    "UTC+05:00 Yekaterinburg":                5.0,
    "UTC+05:30 IST":                          5.5,
    "UTC+05:45 Nepal":                        5.75,
    "UTC+06:00 Dhaka":                        6.0,
    "UTC+06:30 Yangon":                       6.5,
    "UTC+07:00 Bangkok":                      7.0,
    "UTC+08:00 Beijing":                      8.0,
    "UTC+08:45 Eucla":                        8.75,
    "UTC+09:00 Tokyo":                        9.0,
    "UTC+09:30 Adelaide":                     9.5,
    "UTC+10:00 Sydney":                      10.0,
    "UTC+10:30 Lord Howe Island":            10.5,
    "UTC+11:00 Magadan":                     11.0,
    "UTC+12:00 Auckland":                    12.0,
    "UTC+12:45 Chatham Islands":             12.75,
    "UTC+13:00 Tonga":                       13.0,
    "UTC+14:00 Line Islands":                14.0,
}
TIMEZONE_LABELS = list(TIMEZONE_OPTIONS.keys())

EXPECTED_BI_KEYS = [
    "name","year","month","date","hours","minutes","seconds",
    "latitude","longitude","timezone","observation_point","ayanamsha"
]

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def fetch_astro_data(api_key: str, endpoint: str, payload: dict) -> dict:
    if not api_key:
        return {"statusCode":400, "error":"API key missing."}
    try:
        r = requests.post(
            API_BASE_URL + endpoint,
            json=payload,
            headers={"Content-Type":"application/json", "x-api-key":api_key},
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        return {"statusCode": r.status_code,
                "error": f"HTTP {r.status_code}",
                "details": r.text}
    except Exception as e:
        return {"statusCode": None, "error":"Exception", "details": str(e)}

def fetch_coordinates(place: str):
    """Forward‑geocode a place name into (lat, lon, display_name)."""
    if not place.strip():
        return None, None, "Empty place name."
    try:
        resp = requests.get(
            GEOCODE_API_URL,
            params={"q": place, "api_key": GEOCODE_API_KEY},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            first = data[0]
            return float(first["lat"]), float(first["lon"]), first.get("display_name", place)
        return None, None, f"No results for '{place}'"
    except Exception as e:
        return None, None, f"Geocode error: {e}"

def flatten_planet_output(raw):
    name_map = {
        "1":"Sun","2":"Moon","3":"Mars","4":"Mercury",
        "5":"Jupiter","6":"Venus","7":"Saturn",
        "8":"Rahu","9":"Ketu"
    }
    planet_dict = {}
    def ingest(d):
        for k,v in d.items():
            if not isinstance(v, dict): continue
            nm = v.get("name") or name_map.get(str(k)) or \
                 ("Ascendant" if k.lower()=="ascendant" else str(k))
            planet_dict[nm] = v
    if isinstance(raw, dict):
        ingest(raw)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                ingest(item)
    return planet_dict

def generate_readable(bi, results):
    lines = []
    lines.append("="*40)
    lines.append("BIRTH DETAILS")
    lines.append(f"Name: {bi.get('name','')}")
    lines.append(f"Date: {bi['year']}-{bi['month']:02d}-{bi['date']:02d}")
    lines.append(f"Time: {bi['hours']:02d}:{bi['minutes']:02d}:{bi['seconds']:02d}")
    lines.append(f"Location: {bi['latitude']:.4f}, {bi['longitude']:.4f}")
    tzv   = bi.get("timezone",0)
    tzlbl = next((lbl for lbl,v in TIMEZONE_OPTIONS.items() if v==tzv), str(tzv))
    lines.append(f"Timezone: {tzlbl}")
    lines.append(f"Ayanamsha: {bi.get('ayanamsha','')}")
    lines.append(f"Observation: {bi.get('observation_point','')}")
    lines.append("="*40); lines.append("")

    preferred = ["Ascendant","Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
    for chart, raw in results.items():
        lines.append(f"-- {chart} --")
        if not isinstance(raw, dict) or raw.get("statusCode")!=200 or "output" not in raw:
            lines.append("ERROR: " + raw.get("error","unknown"))
            if raw.get("details"): lines.append("DETAILS: " + raw["details"])
            lines.append("")
            continue

        pl = flatten_planet_output(raw["output"])
        if not pl:
            lines.append("No planet data."); lines.append(""); continue

        seen = set()
        for p in preferred:
            info = pl.get(p)
            if not info: continue
            seen.add(p)
            num    = info.get("current_sign")
            nm     = SIGN_NAMES.get(num, f"Sign{num}")
            deg    = info.get("normDegree")
            dstr   = f"{float(deg):.2f}°" if deg is not None else ""
            retro  = "Retrograde" if str(info.get("isRetro",False)).lower() in ("true","1") else "Direct"
            extras = []
            if hn:=info.get("house_number"):   extras.append(f"H{hn}")
            if nk:=info.get("nakshatra_name"): extras.append(f"Nak:{nk}")
            ex = " | " + " | ".join(extras) if extras else ""
            lines.append(f"{p}: {nm} ({num}) {dstr}, {retro}{ex}")
        for p, info in pl.items():
            if p in seen: continue
            num   = info.get("current_sign")
            nm    = SIGN_NAMES.get(num, f"Sign{num}")
            deg   = info.get("normDegree")
            dstr  = f"{float(deg):.2f}°" if deg is not None else ""
            retro = "Retrograde" if str(info.get("isRetro",False)).lower() in ("true","1") else "Direct"
            lines.append(f"{p}: {nm} ({num}) {dstr}, {retro}")
        lines.append("")

    lines.append("="*40)
    lines.append("BIRTH JSON (for reload)")
    lines.append(json.dumps(bi, indent=2))
    lines.append("="*40)
    return "\n".join(lines)


# -------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------

def load_from_json():
    raw = st.session_state.json_input.strip()
    try:
        data = json.loads(raw)
        missing = [k for k in EXPECTED_BI_KEYS if k not in data]
        if missing:
            st.error("Missing keys: " + ", ".join(missing)); return
        bi = {}
        for k in EXPECTED_BI_KEYS:
            if k in ("year","month","date","hours","minutes","seconds"):
                bi[k] = int(data[k])
            elif k in ("latitude","longitude","timezone"):
                bi[k] = float(data[k])
            else:
                bi[k] = data[k]
        st.session_state.birth_info = bi
        st.success("Birth details loaded.")
        st.session_state.json_input = ""
    except Exception as e:
        st.error("Invalid JSON: " + str(e))


def do_geocode():
    place = st.session_state.place_input.strip()
    lat, lon, msg = fetch_coordinates(place)
    if lat is not None:
        bi = st.session_state.get("birth_info", {})
        bi["latitude"], bi["longitude"] = lat, lon
        st.session_state.birth_info = bi
        st.success("Coordinates set: " + msg)
        st.session_state.place_input = ""
    else:
        st.error(msg)


# -------------------------------------------------------------------
# Session State Init
# -------------------------------------------------------------------

if "birth_info" not in st.session_state:
    st.session_state.birth_info = {}
if "results" not in st.session_state:
    st.session_state.results = None
if "readable" not in st.session_state:
    st.session_state.readable = None
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
for k in CHART_ENDPOINTS:
    st.session_state.setdefault(f"cb_{k}", True)


# -------------------------------------------------------------------
# UI: Load JSON
# -------------------------------------------------------------------

with st.expander("Load Saved Birth JSON"):
    st.text_area("Paste JSON here", key="json_input", height=150)
    st.button("Load JSON", on_click=load_from_json)

st.markdown("---")


# -------------------------------------------------------------------
# UI: Geocode
# -------------------------------------------------------------------

with st.form("geo"):
    st.markdown("### Lookup Coordinates by Place")
    st.text_input("Place name:", key="place_input", placeholder="e.g. London, UK")
    st.form_submit_button("Fetch Coordinates", on_click=do_geocode)

st.markdown("---")


# -------------------------------------------------------------------
# UI: Birth Details Form
# -------------------------------------------------------------------

with st.form("birth"):
    st.markdown("### Birth Details")
    bi = st.session_state.birth_info
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Name", value=bi.get("name",""))
        default_date = date(bi.get("year",2000), bi.get("month",1), bi.get("date",1))
        bd = st.date_input("Date", value=default_date, min_value=date(1800,1,1), max_value=date.today())
        st.markdown("#### Time (24h)")
        hr = st.number_input("Hour",0,23, value=bi.get("hours",12), format="%d")
        mi = st.number_input("Minute",0,59, value=bi.get("minutes",0), format="%d")
        se = st.number_input("Second",0,59, value=bi.get("seconds",0), format="%d")
    with c2:
        st.markdown("#### Location")
        lat = st.number_input("Latitude",-90.0,90.0, value=bi.get("latitude",0.0), format="%.4f")
        lon = st.number_input("Longitude",-180.0,180.0, value=bi.get("longitude",0.0), format="%.4f")
        tz_lbl = next((lbl for lbl,v in TIMEZONE_OPTIONS.items() if v==bi.get("timezone",5.5)), "UTC+05:30 IST")
        tz = st.selectbox("Timezone", TIMEZONE_LABELS, index=TIMEZONE_LABELS.index(tz_lbl))
        obs = st.selectbox("Observation", ["topocentric","geocentric"], index=["topocentric","geocentric"].index(bi.get("observation_point","topocentric")))
        ayn = st.selectbox("Ayanamsha", ["lahiri","sayana"], index=["lahiri","sayana"].index(bi.get("ayanamsha","lahiri")))
    if st.form_submit_button("Save Details"):
        st.session_state.birth_info = {
            "name": name,
            "year": bd.year, "month": bd.month, "date": bd.day,
            "hours": hr, "minutes": mi, "seconds": se,
            "latitude": lat, "longitude": lon,
            "timezone": TIMEZONE_OPTIONS[tz],
            "observation_point": obs,
            "ayanamsha": ayn
        }
        st.success("Birth details saved.")

st.markdown("---")


# -------------------------------------------------------------------
# UI: Chart Selection
# -------------------------------------------------------------------

st.subheader("Select Charts to Fetch")
c1, c2 = st.columns(2)
if c1.button("Select All"):
    for k in CHART_ENDPOINTS:
        st.session_state[f"cb_{k}"] = True
if c2.button("Unselect All"):
    for k in CHART_ENDPOINTS:
        st.session_state[f"cb_{k}"] = False

cols = st.columns(3)
sel = {}
opts = list(CHART_ENDPOINTS.keys())
per = (len(opts)+2)//3
for i,opt in enumerate(opts):
    sel[opt] = cols[i//per].checkbox(opt, value=st.session_state[f"cb_{opt}"], key=f"cb_{opt}")

st.markdown("---")


# -------------------------------------------------------------------
# UI: Fetch Data
# -------------------------------------------------------------------

if st.button("Fetch Astrological Data", type="primary"):
    bi = st.session_state.birth_info or {}
    missing = [k for k in EXPECTED_BI_KEYS if k not in bi]
    if missing:
        st.error("Incomplete birth details. Missing: " + ", ".join(missing))
    else:
        chosen = [k for k,v in sel.items() if v]
        if not chosen:
            st.warning("Select at least one chart.")
        else:
            st.session_state.results  = None
            st.session_state.readable = None

            api_key = st.session_state.user_api_key.strip() or DEFAULT_ASTRO_API_KEY
            payload = {
                "year": bi["year"], "month": bi["month"], "date": bi["date"],
                "hours": bi["hours"], "minutes": bi["minutes"], "seconds": bi["seconds"],
                "latitude": bi["latitude"], "longitude": bi["longitude"],
                "timezone": bi["timezone"],
                "settings": {
                    "observation_point": bi["observation_point"],
                    "ayanamsha": bi["ayanamsha"],
                    "language": "en"
                }
            }

            results = {}
            prog = st.progress(0)
            for idx, chart in enumerate(chosen):
                st.write(f"Fetching {chart} ({idx+1}/{len(chosen)})…")
                res = fetch_astro_data(api_key, CHART_ENDPOINTS[chart], payload)
                results[chart] = res
                prog.progress((idx+1)/len(chosen))
                if idx < len(chosen)-1:
                    pytime.sleep(API_CALL_DELAY)

            st.success("Fetch complete.")
            st.session_state.results  = results
            st.session_state.readable = generate_readable(bi, results)

# -------------------------------------------------------------------
# UI: Display & Download
# -------------------------------------------------------------------

if st.session_state.get("results"):
    st.subheader("Results & Downloads")
    now  = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c for c in st.session_state.birth_info.get("name","chart") if c.isalnum()) or "chart"
    base = f"{safe}_{now}"
    raw  = json.dumps(st.session_state.results, indent=2)
    txt  = st.session_state.readable

    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Download Raw JSON", raw, file_name=f"{base}_raw.json")
    with d2:
        st.download_button("Download Readable TXT", txt, file_name=f"{base}_readable.txt")

    with st.expander("Readable Summary"):
        st.text_area("Summary", txt, height=400)
    with st.expander("Raw JSON"):
        st.json(st.session_state.results)

st.markdown("---")

# -------------------------------------------------------------------
# UI: Advanced Settings & Clear
# -------------------------------------------------------------------

with st.expander("Advanced Settings"):
    st.text_input("Custom API Key (optional)", key="user_api_key", type="password")

if st.button("Clear All & Start Over"):
    preserved = st.session_state.get("user_api_key", "")
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state.user_api_key = preserved
    # No experimental rerun or memo calls needed

st.markdown("---")
st.caption("Built with Streamlit | Free Astrology API | Geocoding by Maps.co")
