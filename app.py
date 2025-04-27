import streamlit as st
import requests
import json
from datetime import datetime, date
import time as pytime

# -------------------------------------------------------------------
# 🔯 Jyotish Data — Vedic Divisional Charts for AI Workflows
# -------------------------------------------------------------------
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

st.markdown("## 🔯 Jyotish Data - For AI analysis")
st.markdown("---")

# --- Constants ---
API_BASE_URL          = "https://json.freeastrologyapi.com/"
GEOCODE_API_URL       = "https://geocode.maps.co/search"
GEOCODE_API_KEY       = "680561227fda9856529449uxwa70717" # Replace with your key if needed
DEFAULT_ASTRO_API_KEY = "1pK0yvcDkMaS750G6v2VA8lglgTm1bcO3thzyrTK" # Replace with your key if needed
API_CALL_DELAY        = 1.0 # Delay in seconds between API calls

SIGN_NAMES = {
  1:"Aries",2:"Taurus",3:"Gemini",4:"Cancer",5:"Leo",6:"Virgo",
  7:"Libra",8:"Scorpio",9:"Sagittarius",10:"Capricorn",
  11:"Aquarius",12:"Pisces"
}
# Add fallback for any unexpected sign numbers
for i in range(32):
  SIGN_NAMES.setdefault(i, f"UnknownSign({i})")

CHART_ENDPOINTS = {
  "D1 (Rasi Chart)":"planets",
  "Planets Extended Info":"planets/extended",
  "D2 (Hora Chart)":"d2-chart-info",
  "D3 (Drekkana Chart)":"d3-chart-info",
  "D4 (Chaturthamsa Chart)":"d4-chart-info",
  "D5 (Panchamsa Chart)":"d5-chart-info",
  "D6 (Shasthamsa Chart)":"d6-chart-info",
  "D7 (Saptamsa Chart)":"d7-chart-info",
  "D8 (Ashtamsa Chart)":"d8-chart-info",
  "D9 (Navamsa Chart)":"navamsa-chart-info",
  "D10 (Dasamsa Chart)":"d10-chart-info",
  "D11 (Rudramsa Chart)":"d11-chart-info",
  "D12 (Dwadasamsa Chart)":"d12-chart-info",
  "D16 (Shodasamsa Chart)":"d16-chart-info",
  "D20 (Vimsamsa Chart)":"d20-chart-info",
  "D24 (Siddhamsa Chart)":"d24-chart-info",
  "D27 (Nakshatramsa Chart)":"d27-chart-info",
  "D30 (Trimsamsa Chart)":"d30-chart-info",
  "D40 (Khavedamsa Chart)":"d40-chart-info",
  "D45 (Akshavedamsa Chart)":"d45-chart-info",
  "D60 (Shashtyamsa Chart)":"d60-chart-info",
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
# Helpers
# -------------------------------------------------------------------
def fetch_astro_data(key, endpoint, payload):
    """Fetches data from the astrology API."""
    if not key:
        # This scenario should ideally be handled before calling,
        # but as a safeguard:
        st.error("API key is missing. Cannot make request.")
        return {"statusCode": 400, "error": "API key missing."}
    try:
        r = requests.post(f"{API_BASE_URL}{endpoint}",
                          json=payload,
                          headers={"Content-Type": "application/json", "x-api-key": key},
                          timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as http_err:
        details = r.text
        try:
            error_json = r.json()
            details = error_json.get('message', details)
            # Check for common API key errors
            if r.status_code == 403 and 'Invalid API key' in details:
                st.error("API Error 403: Invalid API key provided. Please check your key or leave blank to use the default.")
            elif r.status_code == 429:
                 st.error("API Error 429: Rate limit exceeded. Please wait before trying again. Using your own key might help.")
            else:
                 st.error(f"API HTTP Error {r.status_code}: {details[:500]}")
        except json.JSONDecodeError:
             st.error(f"API HTTP Error {r.status_code}: {details[:500]}") # Show raw text if not JSON
        return {"statusCode": r.status_code, "error": f"HTTP {r.status_code}", "details": details}
    except requests.exceptions.Timeout:
        st.error("API request timed out. The server might be busy. Try again later.")
        return {"statusCode": 408, "error": "Request Timeout"}
    except requests.exceptions.RequestException as req_err:
        st.error(f"API Request Error: Could not connect to the API. Check your internet connection. Error: {req_err}")
        return {"statusCode": None, "error": "Request Exception", "details": str(req_err)}
    except Exception as e:
        st.error(f"An unexpected error occurred during API call: {e}")
        return {"statusCode": None, "error": "Unexpected Exception", "details": str(e)}

def fetch_coordinates(place):
    """Fetches latitude and longitude for a given place name."""
    if not place or not place.strip():
        return None, None, "Please enter a place name."
    try:
        params = {"q": place.strip()}
        if GEOCODE_API_KEY and GEOCODE_API_KEY.strip():
             params["api_key"] = GEOCODE_API_KEY
        else:
             st.warning("Geocode API key is missing. Using free tier (limited).", icon="⚠️")

        r = requests.get(GEOCODE_API_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data:
            first_result = data[0]
            lat = float(first_result["lat"])
            lon = float(first_result["lon"])
            display_name = first_result.get("display_name", place)
            return lat, lon, display_name
        else:
            return None, None, f"Could not find coordinates for '{place}'."
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"Geocode HTTP Error {r.status_code}: {r.text[:200]}"
        st.error(error_msg)
        return None, None, error_msg
    except requests.exceptions.RequestException as req_err:
        st.error(f"Geocode Request Error: {req_err}")
        return None, None, f"Geocode network error: {req_err}"
    except (ValueError, KeyError, IndexError) as parse_err:
        st.error(f"Error parsing geocode response: {parse_err}")
        return None, None, f"Error processing geocode results: {parse_err}"
    except Exception as e:
        st.error(f"An unexpected geocoding error occurred: {e}")
        return None, None, f"Geocode unexpected error: {e}"

def flatten_planet_output(raw_output):
    """Flattens the nested planet data into a simple dictionary."""
    name_map = {"1": "Sun", "2": "Moon", "3": "Mars", "4": "Mercury",
                "5": "Jupiter", "6": "Venus", "7": "Saturn",
                "8": "Rahu", "9": "Ketu"}
    planet_data = {}

    def ingest_data(data_dict):
        for key, value in data_dict.items():
            if not isinstance(value, dict): continue

            planet_name = value.get("name") or                          name_map.get(str(key)) or                          ("Ascendant" if str(key).lower() == "ascendant" else str(key))

            planet_data[planet_name] = value

    if isinstance(raw_output, dict):
        ingest_data(raw_output)
    elif isinstance(raw_output, list):
        for item in raw_output:
            if isinstance(item, dict):
                ingest_data(item)

    return planet_data

def generate_readable(birth_info, results_dict):
    """Generates a human-readable summary of birth details and chart results."""
    lines = ["="*40, "BIRTH DETAILS"]
    lines.extend([
        f"Name: {birth_info.get('name', 'N/A')}",
        f"Date: {birth_info.get('year', 'YYYY')}-{birth_info.get('month', 'MM'):02d}-{birth_info.get('date', 'DD'):02d}",
        f"Time: {birth_info.get('hours', 'HH'):02d}:{birth_info.get('minutes', 'MM'):02d}:{birth_info.get('seconds', 'SS'):02d}",
        f"Location: Lat {birth_info.get('latitude', 0.0):.4f}, Lon {birth_info.get('longitude', 0.0):.4f}",
    ])

    tz_value = birth_info.get("timezone", 0.0)
    tz_label = next((label for label, value in TIMEZONE_OPTIONS.items() if value == tz_value), f"UTC{tz_value:+g}")
    lines.extend([
        f"Timezone: {tz_label}",
        f"Ayanamsha: {birth_info.get('ayanamsha', 'N/A')}",
        f"Observation Point: {birth_info.get('observation_point', 'N/A')}",
        "="*40, ""
    ])

    preferred_order = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for chart_name, raw_result in results_dict.items():
        lines.append(f"-- {chart_name} --")

        if not isinstance(raw_result, dict) or raw_result.get("statusCode") != 200:
            error_msg = raw_result.get("error", "Unknown Error")
            details = raw_result.get("details", "")
            lines.append(f"ERROR fetching chart: {error_msg}")
            if details:
                lines.append(f"DETAILS: {details[:200]}...")
            lines.append("")
            continue

        output_data = raw_result.get("output")
        if not output_data:
            lines.append("No chart data received in 'output'.")
            lines.append("")
            continue

        planets = flatten_planet_output(output_data)
        if not planets:
            lines.append("No planet data found after processing.")
            lines.append("")
            continue

        processed_planets = set()

        for planet in preferred_order:
            info = planets.get(planet)
            if not info: continue
            processed_planets.add(planet)

            sign_num = info.get("current_sign")
            sign_name = SIGN_NAMES.get(sign_num, f"Sign {sign_num}")
            degree = info.get("normDegree")
            degree_str = f"{float(degree):.2f}°" if degree is not None else ""
            is_retro = str(info.get("isRetro", "false")).lower() in ("true", "1")
            retro_str = "Retrograde" if is_retro else "Direct"

            extras = []
            if (house := info.get("house_number")) is not None: extras.append(f"H{house}")
            if (naksh := info.get("nakshatra_name")) : extras.append(f"Nak: {naksh}")
            extras_str = f" | {', '.join(extras)}" if extras else ""

            lines.append(f"{planet}: {sign_name} ({sign_num}) {degree_str}, {retro_str}{extras_str}")

        # Process any remaining planets not in preferred order (shouldn't happen often with current API)
        for planet, info in planets.items():
            if planet in processed_planets: continue

            sign_num = info.get("current_sign")
            sign_name = SIGN_NAMES.get(sign_num, f"Sign {sign_num}")
            degree = info.get("normDegree")
            degree_str = f"{float(degree):.2f}°" if degree is not None else ""
            is_retro = str(info.get("isRetro", "false")).lower() in ("true", "1")
            retro_str = "Retrograde" if is_retro else "Direct"

            lines.append(f"{planet}: {sign_name} ({sign_num}) {degree_str}, {retro_str}")

        lines.append("")

    lines.extend([
        "="*40,
        "BIRTH JSON (for reload):",
        json.dumps(birth_info, indent=2),
        "="*40
    ])
    return "\n".join(lines)

# -------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------
def load_from_json():
    """Loads birth information from a JSON string."""
    raw_json = st.session_state.json_input.strip()
    if not raw_json:
        st.warning("JSON input is empty.")
        return
    try:
        data = json.loads(raw_json)
        # Check for core keys, allow flexibility for missing ones initially
        core_keys = ["year", "month", "date", "hours", "minutes", "seconds", "latitude", "longitude", "timezone"]
        missing_keys = [k for k in core_keys if k not in data]
        if missing_keys:
            st.warning(f"JSON might be missing some keys: {', '.join(missing_keys)}. Defaults will be used if possible.")
            # Allow loading even with missing keys, let validation happen later

        loaded_bi = {}
        # Use .get() with defaults for safety
        loaded_bi["name"] = str(data.get("name", ""))
        loaded_bi["year"] = int(data.get("year", 2000))
        loaded_bi["month"] = int(data.get("month", 1))
        loaded_bi["date"] = int(data.get("date", 1))
        loaded_bi["hours"] = int(data.get("hours", 12))
        loaded_bi["minutes"] = int(data.get("minutes", 0))
        loaded_bi["seconds"] = int(data.get("seconds", 0))
        loaded_bi["latitude"] = float(data.get("latitude", 0.0))
        loaded_bi["longitude"] = float(data.get("longitude", 0.0))
        loaded_bi["timezone"] = float(data.get("timezone", 5.5)) # Default to IST
        loaded_bi["observation_point"] = str(data.get("observation_point", "topocentric"))
        loaded_bi["ayanamsha"] = str(data.get("ayanamsha", "lahiri"))

        st.session_state.birth_info = loaded_bi
        # Update advanced settings based on loaded JSON
        st.session_state.obs_input = loaded_bi.get("observation_point", "topocentric")
        st.session_state.ayn_input = loaded_bi.get("ayanamsha", "lahiri")

        st.success("Successfully loaded birth details from JSON.")
        st.session_state.json_input = "" # Clear the input box
        st.session_state.results = None # Clear previous results
        st.session_state.readable = None

    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {e}")
    except (ValueError, TypeError) as e:
         st.error(f"Error converting JSON values: {e}. Please ensure numbers are valid.")
    except Exception as e:
        st.error(f"An unexpected error occurred during JSON loading: {e}")

def do_geocode():
    """Handles the geocoding button click."""
    place = st.session_state.get("place_input", "").strip()
    lat, lon, msg = fetch_coordinates(place)
    if lat is not None and lon is not None:
        if "birth_info" not in st.session_state:
            st.session_state.birth_info = {} # Should already exist, but safety check
        st.session_state.birth_info["latitude"] = lat
        st.session_state.birth_info["longitude"] = lon
        # Update the number input widgets directly to reflect the change
        st.session_state.latitude_input = lat
        st.session_state.longitude_input = lon
        st.success(f"Coordinates updated for {msg}: Lat {lat:.4f}, Lon {lon:.4f}")
    else:
        st.error(f"Geocoding failed: {msg}")

# -------------------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------------------
if "birth_info" not in st.session_state:   st.session_state.birth_info = {}
if "results"    not in st.session_state:   st.session_state.results = None
if "readable"   not in st.session_state:   st.session_state.readable = None
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ADDED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
if "user_api_key" not in st.session_state: st.session_state.user_api_key = ""
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END ADDED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Initialize chart selection checkboxes (default to only D1, Extended Info, D9 & D10)
default_selected_charts = {
    "D1 (Rasi Chart)",
    "Planets Extended Info",
    "D9 (Navamsa Chart)",
    "D10 (Dasamsa Chart)"
}
for k in CHART_ENDPOINTS:
    if f"cb_{k}" not in st.session_state:
        st.session_state[f"cb_{k}"] = (k in default_selected_charts)

# Initialize advanced settings from birth_info if available, else defaults
if "obs_input" not in st.session_state:
    st.session_state.obs_input = st.session_state.birth_info.get("observation_point", "topocentric")
if "ayn_input" not in st.session_state:
    st.session_state.ayn_input = st.session_state.birth_info.get("ayanamsha", "lahiri")

# -------------------------------------------------------------------
# UI: API Key Input (Moved to Top)
# -------------------------------------------------------------------
st.markdown("#### Astrology API Key (Optional)")
st.markdown("""
Sign up at [freeastrologyapi.com](https://freeastrologyapi.com/) to get your own free API key.
Using your own key is recommended for higher usage limits and reliability.
If you leave this blank, a shared default key will be used (which may encounter rate limits more often).
""")
st.text_input(
    "Enter Your FreeAstrologyAPI Key:",
    key="user_api_key",
    type="password",
    help="Paste your personal API key here. It will be used instead of the default key."
)
st.markdown("---") # Separator


# -------------------------------------------------------------------
# UI: Load JSON
# -------------------------------------------------------------------
with st.expander("Load Saved Birth JSON"):
    st.text_area("Paste JSON here:", key="json_input", height=150,
                 help="Paste the 'Birth Details JSON' saved from a previous session.")
    st.button("Load JSON", on_click=load_from_json, key="load_json_btn")
st.markdown("---")

# -------------------------------------------------------------------
# UI: Birth Details & Settings
# -------------------------------------------------------------------
st.subheader("Birth Details & Settings")
# Use st.session_state directly for default values in widgets
# This ensures widgets reflect loaded JSON or geocoding results
bi = st.session_state.birth_info # Keep for easy access below if needed

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name:", value=st.session_state.birth_info.get("name", ""), key="name_input")

    try:
        # Use values from session state for default date
        default_bd = date(
            int(st.session_state.birth_info.get("year", 2000)),
            int(st.session_state.birth_info.get("month", 1)),
            int(st.session_state.birth_info.get("date", 1))
        )
        # Clamp date to valid range
        default_bd = max(date(1800, 1, 1), min(default_bd, date.today()))
    except (ValueError, TypeError, KeyError): # Catch potential errors if session state values are bad
        default_bd = date(2000, 1, 1)

    bd = st.date_input(
        "Birth Date:",
        value=default_bd,
        min_value=date(1800, 1, 1),
        max_value=date.today(),
        key="birth_date_input",
        help="Select the date of birth."
    )

    st.markdown("**Birth Time (24-hour format)**")
    t1, t2, t3 = st.columns(3)
    # Use session state values for time defaults
    hr = t1.number_input("Hour", min_value=0, max_value=23, value=st.session_state.birth_info.get("hours", 12), format="%d", key="hour_input")
    mi = t2.number_input("Minute", min_value=0, max_value=59, value=st.session_state.birth_info.get("minutes", 0), format="%d", key="minute_input")
    se = t3.number_input("Second", min_value=0, max_value=59, value=st.session_state.birth_info.get("seconds", 0), format="%d", key="second_input")

with col2:
    st.markdown("**Lookup Coordinates by Place**")
    st.text_input("Enter Place Name (e.g., New York, USA):", key="place_input",
                  placeholder="City")
    st.button("Fetch Coordinates", on_click=do_geocode, key="geo_btn")

    st.markdown("**Location (Decimal Degrees)**")
    # Use session state values for lat/lon defaults, reflecting geocoding/JSON load
    lat = st.number_input("Latitude:", min_value=-90.0, max_value=90.0, value=st.session_state.birth_info.get("latitude", 0.0), format="%.4f", key="latitude_input")
    lon = st.number_input("Longitude:", min_value=-180.0, max_value=180.0, value=st.session_state.birth_info.get("longitude", 0.0), format="%.4f", key="longitude_input")

    st.markdown("**Timezone**")
    # Use session state value for timezone default
    current_tz_value = st.session_state.birth_info.get("timezone", 5.5) # Default to IST if not set
    try:
        # Find the index corresponding to the current value
        tz_index = TIMEZONE_LABELS.index(
            next(lbl for lbl, val in TIMEZONE_OPTIONS.items() if val == current_tz_value)
        )
    except (StopIteration, ValueError):
         # If value not found (e.g., from manual JSON edit), default to IST index
        tz_index = TIMEZONE_LABELS.index("UTC+05:30 IST")

    sel_tz_label = st.selectbox("Select Timezone:", TIMEZONE_LABELS, index=tz_index, key="timezone_select")
    tz_value = TIMEZONE_OPTIONS[sel_tz_label]

with st.expander("Advanced Calculation Settings"):
    obs_opts = ["topocentric", "geocentric"]
    try:
        # Use session state obs_input for index
        obs_index = obs_opts.index(st.session_state.obs_input)
    except ValueError:
        obs_index = 0 # Default to topocentric if value is invalid
    obs = st.selectbox("Observation Point:", obs_opts, index=obs_index, key="obs_input_widget",
                       help="Topocentric is observer on Earth's surface, Geocentric is Earth's center.")

    ay_opts = ["lahiri", "sayana"]
    try:
         # Use session state ayn_input for index
        ayn_index = ay_opts.index(st.session_state.ayn_input)
    except ValueError:
        ayn_index = 0 # Default to lahiri if value is invalid
    ayn = st.selectbox("Ayanamsha:", ay_opts, index=ayn_index, key="ayn_input_widget",
                       help="Lahiri is commonly used in Vedic astrology. Sayana uses the tropical zodiac.")
    # Update session state directly when widgets change
    st.session_state.obs_input = obs
    st.session_state.ayn_input = ayn

# Update birth_info in session state *after* all widgets are defined
# This ensures it always reflects the current UI state before fetching
st.session_state.birth_info = {
    "name": st.session_state.name_input,
    "year": bd.year, "month": bd.month, "date": bd.day,
    "hours": st.session_state.hour_input,
    "minutes": st.session_state.minute_input,
    "seconds": st.session_state.second_input,
    "latitude":  st.session_state.latitude_input,
    "longitude": st.session_state.longitude_input,
    "timezone":  tz_value,
    "observation_point": st.session_state.obs_input, # Use updated value from session state
    "ayanamsha":         st.session_state.ayn_input  # Use updated value from session state
}

st.markdown("---")
st.subheader("Select Charts to Fetch")
st.caption("ℹ️ If you encounter errors during data fetching, please wait ~5 minutes and try again. This can happen due to API rate limits or temporary service issues.")

c1, c2 = st.columns(2)
if c1.button("Select All Charts"):
    for k in CHART_ENDPOINTS: st.session_state[f"cb_{k}"] = True
    st.rerun()
if c2.button("Unselect All Charts"):
    for k in CHART_ENDPOINTS: st.session_state[f"cb_{k}"] = False
    st.rerun()

cols = st.columns(3)
selected_charts = {}
chart_options = list(CHART_ENDPOINTS.keys())
charts_per_col = (len(chart_options) + len(cols) - 1) // len(cols)

for i, chart_name in enumerate(chart_options):
    col_index = i // charts_per_col
    # Read value directly from session state checkbox key
    is_selected = cols[col_index].checkbox(chart_name,
                                           value=st.session_state.get(f"cb_{chart_name}", False),
                                           key=f"cb_{chart_name}")
    selected_charts[chart_name] = is_selected # Keep track of selections for the fetch button logic

if st.button("Fetch Astrological Data", type="primary", key="fetch_data_btn"):
    current_bi = st.session_state.birth_info # Get the latest birth info
    # Validate required fields (latitude/longitude are crucial)
    missing = []
    if current_bi.get("latitude") is None or current_bi.get("longitude") is None:
        missing.append("latitude/longitude (fetch or enter manually)")
    # You could add more checks here if needed, e.g., for date/time validity if desired

    if missing:
        st.error(f"Incomplete birth details. Please provide: {', '.join(missing)}")
    else:
        charts_to_fetch = [name for name, sel in selected_charts.items() if sel]
        if not charts_to_fetch:
            st.warning("Please select at least one chart to fetch.")
        else:
            st.session_state.results = None # Clear previous results
            st.session_state.readable = None
            st.info(f"Starting fetch for {len(charts_to_fetch)} chart(s)...")

            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MODIFIED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Determine which API key to use
            user_key = st.session_state.user_api_key.strip()
            api_key_to_use = user_key if user_key else DEFAULT_ASTRO_API_KEY

            if not user_key:
                st.info("Using the default API key. Consider adding your own key from freeastrologyapi.com for better performance.", icon="ℹ️")
            else:
                 st.info("Using your provided API key.", icon="🔑")
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END MODIFIED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            # Prepare payload using the most recent birth_info from session state
            payload = {
                "year": current_bi["year"], "month": current_bi["month"], "date": current_bi["date"],
                "hours": current_bi["hours"], "minutes": current_bi["minutes"], "seconds": current_bi["seconds"],
                "latitude": current_bi["latitude"], "longitude": current_bi["longitude"],
                "timezone": current_bi["timezone"],
                "settings": {
                    "observation_point": current_bi["observation_point"],
                    "ayanamsha": current_bi["ayanamsha"],
                    "language": "en" # Assuming English is desired
                }
            }

            results_accumulator = {}
            has_errors = False
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            for idx, chart_name in enumerate(charts_to_fetch):
                endpoint = CHART_ENDPOINTS[chart_name]
                status_text.text(f"Fetching {chart_name} ({idx+1}/{len(charts_to_fetch)})...")
                # <<<<<<<<<<<<<<<<<<<<<<<< MODIFIED: Pass the chosen key >>>>>>>>>>>>>>>>>>
                res = fetch_astro_data(api_key_to_use, endpoint, payload)
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                results_accumulator[chart_name] = res
                progress = (idx + 1) / len(charts_to_fetch)
                progress_bar.progress(progress)

                # Check for errors specifically from the API response structure
                if not isinstance(res, dict) or res.get("statusCode") != 200:
                    has_errors = True
                    # Error messages are now shown directly within fetch_astro_data
                    # status_text.warning(f"Error fetching {chart_name}. See message above.") # Optional: Keep status text updated

                # Add delay between calls
                if idx < len(charts_to_fetch) - 1:
                    pytime.sleep(API_CALL_DELAY)

            progress_bar.empty() # Remove progress bar
            status_text.empty() # Clear status text

            if has_errors:
                st.warning("Fetch completed, but some errors occurred. Results might be incomplete. Check messages above for details.", icon="⚠️")
            else:
                st.success("Fetch complete.")

            # Store results and generate readable summary
            st.session_state.results = results_accumulator
            st.session_state.readable = generate_readable(current_bi, results_accumulator)
            st.rerun() # Rerun to display results sections

st.markdown("---")

# --- Results Display Section ---
if st.session_state.get("results"):
    st.subheader("Results & Downloads")

    st.markdown("""
    <style>
      div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border: 1px solid #218838 !important;
        border-radius: 5px;
        padding: 0.4rem 0.75rem;
      }
      div.stDownloadButton > button:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
      }
    </style>
    """, unsafe_allow_html=True)

    # Generate filenames based on current birth info
    bi_for_filename = st.session_state.birth_info
    safe_name = "".join(c for c in bi_for_filename.get("name", "chart") if c.isalnum() or c in "-_").strip() or "chart"
    date_str = f"{bi_for_filename.get('date', 'DD'):02d}-{bi_for_filename.get('month', 'MM'):02d}-{bi_for_filename.get('year', 'YYYY')}"
    base_filename = f"{safe_name}-{date_str}"

    # Prepare data for download buttons
    try:
        raw_json_data = json.dumps(st.session_state.results, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not serialize results to JSON: {e}")
        raw_json_data = "{}" # Provide empty JSON as fallback

    readable_text_data = st.session_state.get("readable", "No readable summary generated.")

    try:
        birth_info_json_data = json.dumps(st.session_state.birth_info, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not serialize birth info to JSON: {e}")
        birth_info_json_data = "{}" # Provide empty JSON as fallback

    # Download Buttons
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="💾 Download Chart JSON",
            data=raw_json_data,
            file_name=f"{base_filename}-ChartData.json",
            mime="application/json",
            help="Save the raw JSON output for all fetched charts. Useful for AI analysis."
        )
    with col_dl2:
        st.download_button(
            label="💾 Download Readable TXT",
            data=readable_text_data,
            file_name=f"{base_filename}-ReadableSummary.txt",
            mime="text/plain",
            help="Save the formatted summary including birth details and chart positions."
        )

    st.markdown("---")

    # Explanations and Previews
    st.markdown(
        """
        **How to Use the Downloads:**

        *   **Chart JSON:** This file contains the detailed astrological data in a structured format.
            *   Feed this JSON directly to AI models (like ChatGPT, Claude, Gemini) for analysis.
            *   Example prompt: `Analyze the attached Vedic astrology chart data (JSON) and provide insights into... [your specific question].`
        *   **Readable TXT:** A plain text summary for quick reference.
            *   **Caution:** This file includes your birth details.
            *   You can also copy/paste this text into AI models, but the JSON is usually preferred by them for data structure.

        **💡 Tip:** Both formats can be used to ask AI about natal chart interpretations, planetary influences, basic transit effects, compatibility (if you provide two charts), etc. Remember AI interpretations are not a substitute for professional astrological consultation.
        """
    )

    with st.expander("View Readable Summary"):
        st.text_area("Summary Preview:", readable_text_data, height=350, key="readable_preview", disabled=True)

    with st.expander("View Raw Chart JSON"):
        st.json(st.session_state.results, expanded=False)

    with st.expander("View Birth Details JSON (for Reuse)"):
        st.markdown(
            "Copy the JSON below and save it. You can paste it into the **Load Saved Birth JSON** section at the top to quickly restore these birth details later."
        )
        st.text_area("Birth JSON:", birth_info_json_data, height=250, key="birth_info_preview", disabled=True)

    st.markdown("---")

# --- Advanced/Reset Section ---
# This section is now independent of whether results exist
# It also contains the API key input which was moved higher
with st.expander("App Reset Options"):
    # Moved API key input higher up in the script

    # Clear All Inputs Button
    if st.button("Clear All Inputs & Results", key="clear_all_btn",
                 help="Resets all birth details, chart selections, and results. Keeps custom API key if entered."):
        # Preserve the custom API key if it exists
        preserved_key = st.session_state.get("user_api_key", "")

        # Identify keys to keep (only the API key in this case)
        keys_to_keep = ["user_api_key"]

        # Get all current session state keys
        all_keys = list(st.session_state.keys())

        # Delete keys that are NOT in the keep list
        for k in all_keys:
            if k not in keys_to_keep:
                del st.session_state[k]

        # Re-initialize necessary states after clearing
        st.session_state.birth_info = {}
        st.session_state.results = None
        st.session_state.readable = None
        st.session_state.obs_input = "topocentric" # Reset advanced settings
        st.session_state.ayn_input = "lahiri"
        # Reset chart selections to default
        for k in CHART_ENDPOINTS:
            st.session_state[f"cb_{k}"] = (k in default_selected_charts)

        # Ensure the preserved key is still there (it should be, but belt-and-suspenders)
        if "user_api_key" not in st.session_state:
             st.session_state.user_api_key = preserved_key

        st.success("All inputs and results cleared (API key preserved).")
        st.rerun() # Rerun to reflect the cleared state

    # Full Session Reset Button
    if st.button("🔄 Clear Entire Session & Reset App", key="full_reset_btn",
                 help="Completely clears the application's memory, including any custom API key. Use if the app behaves unexpectedly."):
        # Clear everything in the session state
        st.session_state.clear()
        # Rerun the app from the very beginning
        st.rerun()

st.markdown("---")
st.caption("Built using Streamlit | Astrology data via freeastrologyapi.com | Geocoding via geocode.maps.co")
