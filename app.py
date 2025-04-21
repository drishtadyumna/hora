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
DEFAULT_ASTRO_API_KEY = "5EIAafVray9EwCr2Lz1kB1ofbkUmzoy76kbGnRav" # Replace with your key if needed
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
        return {"statusCode": 400, "error": "API key missing."}
    try:
        r = requests.post(f"{API_BASE_URL}{endpoint}",
                          json=payload,
                          headers={"Content-Type": "application/json", "x-api-key": key},
                          timeout=15) # Increased timeout slightly
        r.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        return r.json()
    except requests.exceptions.HTTPError as http_err:
        # Try to parse error details from response if possible
        details = r.text
        try:
            error_json = r.json()
            details = error_json.get('message', details) # Use message if available
        except json.JSONDecodeError:
            pass # Keep r.text if not JSON
        st.error(f"API HTTP Error {r.status_code}: {details[:500]}") # Show error in UI
        return {"statusCode": r.status_code, "error": f"HTTP {r.status_code}", "details": details}
    except requests.exceptions.Timeout:
        st.error("API request timed out.")
        return {"statusCode": 408, "error": "Request Timeout"}
    except requests.exceptions.RequestException as req_err:
        st.error(f"API Request Error: {req_err}")
        return {"statusCode": None, "error": "Request Exception", "details": str(req_err)}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {"statusCode": None, "error": "Unexpected Exception", "details": str(e)}

def fetch_coordinates(place):
    """Fetches latitude and longitude for a given place name."""
    if not place or not place.strip():
        return None, None, "Please enter a place name."
    try:
        params = {"q": place.strip()}
        # Conditionally add API key if it's not empty
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
        error_msg = f"Geocode HTTP Error {r.status_code}: {r.text[:200]}" # Limit error text length
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
            if not isinstance(value, dict): continue # Skip non-dict items

            # Determine planet name
            planet_name = value.get("name") or \
                          name_map.get(str(key)) or \
                          ("Ascendant" if str(key).lower() == "ascendant" else str(key))

            planet_data[planet_name] = value

    if isinstance(raw_output, dict):
        ingest_data(raw_output)
    elif isinstance(raw_output, list):
        for item in raw_output:
            if isinstance(item, dict):
                ingest_data(item) # Handle cases where output might be a list of planet dicts

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

    # Find timezone label
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

        # Check for API errors first
        if not isinstance(raw_result, dict) or raw_result.get("statusCode") != 200:
            error_msg = raw_result.get("error", "Unknown Error")
            details = raw_result.get("details", "")
            lines.append(f"ERROR fetching chart: {error_msg}")
            if details:
                lines.append(f"DETAILS: {details[:200]}...") # Truncate long details
            lines.append("")
            continue

        # Check if 'output' key exists and is not empty
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

        # Print preferred planets first
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

        # Print any remaining planets/points
        for planet, info in planets.items():
            if planet in processed_planets: continue

            sign_num = info.get("current_sign")
            sign_name = SIGN_NAMES.get(sign_num, f"Sign {sign_num}")
            degree = info.get("normDegree")
            degree_str = f"{float(degree):.2f}°" if degree is not None else ""
            is_retro = str(info.get("isRetro", "false")).lower() in ("true", "1")
            retro_str = "Retrograde" if is_retro else "Direct"

            lines.append(f"{planet}: {sign_name} ({sign_num}) {degree_str}, {retro_str}")

        lines.append("") # Add space after each chart

    # Add the reloadable JSON at the end
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
        # Validate presence of expected keys
        missing_keys = [k for k in EXPECTED_BI_KEYS if k not in data]
        if missing_keys:
            st.error(f"JSON is missing required keys: {', '.join(missing_keys)}")
            return

        # Basic type validation and conversion
        loaded_bi = {}
        try:
            for k in EXPECTED_BI_KEYS:
                if k in ("year", "month", "date", "hours", "minutes", "seconds"):
                    loaded_bi[k] = int(data[k])
                elif k in ("latitude", "longitude", "timezone"):
                    loaded_bi[k] = float(data[k])
                else: # name, observation_point, ayanamsha
                    loaded_bi[k] = str(data[k])
        except (ValueError, TypeError) as e:
             st.error(f"Error converting JSON values: {e}")
             return

        # Update session state
        st.session_state.birth_info = loaded_bi
        # Update advanced settings in session state too
        st.session_state.obs_input = loaded_bi.get("observation_point", "topocentric")
        st.session_state.ayn_input = loaded_bi.get("ayanamsha", "lahiri")
        st.success("Successfully loaded birth details from JSON.")
        st.session_state.json_input = "" # Clear input area
        st.session_state.results = None # Clear previous results
        st.session_state.readable = None

    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred during JSON loading: {e}")

def do_geocode():
    """Handles the geocoding button click."""
    place = st.session_state.get("place_input", "").strip()
    lat, lon, msg = fetch_coordinates(place)
    if lat is not None and lon is not None:
        # Ensure birth_info exists before modifying
        if "birth_info" not in st.session_state:
            st.session_state.birth_info = {}
        st.session_state.birth_info["latitude"] = lat
        st.session_state.birth_info["longitude"] = lon
        # Optionally update the input fields if they exist (handled by number_input value binding)
        st.success(f"Coordinates updated for {msg}: Lat {lat:.4f}, Lon {lon:.4f}")
    else:
        st.error(f"Geocoding failed: {msg}") # Error message already shown by fetch_coordinates, this is redundant but ok

# -------------------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------------------
# Initialize only if keys are completely absent
if "birth_info" not in st.session_state:   st.session_state.birth_info = {}
if "results"    not in st.session_state:   st.session_state.results = None
if "readable"   not in st.session_state:   st.session_state.readable = None
if "user_api_key" not in st.session_state: st.session_state.user_api_key = ""

# Initialize chart selection checkboxes (default to True)
for k in CHART_ENDPOINTS:
    if f"cb_{k}" not in st.session_state:
        st.session_state[f"cb_{k}"] = True

# Initialize advanced settings based on birth_info or defaults
if "obs_input" not in st.session_state:
    st.session_state.obs_input = st.session_state.birth_info.get("observation_point", "topocentric")
if "ayn_input" not in st.session_state:
    st.session_state.ayn_input = st.session_state.birth_info.get("ayanamsha", "lahiri")

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
bi = st.session_state.birth_info # Use the potentially loaded/updated info

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name:", value=bi.get("name", ""), key="name_input")

    # Date Input - handle potential invalid dates from state gracefully
    try:
        default_bd = date(
            int(bi.get("year", 2000)),
            int(bi.get("month", 1)),
            int(bi.get("date", 1))
        )
        # Ensure default date is not in the future or before reasonable min
        default_bd = max(date(1800, 1, 1), min(default_bd, date.today()))
    except (ValueError, TypeError):
        default_bd = date(2000, 1, 1) # Fallback default

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
    # Use min/max directly in number_input for validation
    hr = t1.number_input("Hour", min_value=0, max_value=23, value=bi.get("hours", 12), format="%d", key="hour_input")
    mi = t2.number_input("Minute", min_value=0, max_value=59, value=bi.get("minutes", 0), format="%d", key="minute_input")
    se = t3.number_input("Second", min_value=0, max_value=59, value=bi.get("seconds", 0), format="%d", key="second_input")

with col2:
    st.markdown("**Lookup Coordinates by Place**")
    st.text_input("Enter Place Name (e.g., New York, USA):", key="place_input",
                  placeholder="City, Country or City, State, Country")
    st.button("Fetch Coordinates", on_click=do_geocode, key="geo_btn")

    st.markdown("**Location (Decimal Degrees)**")
    # Latitude/Longitude directly reflect changes from geocoding via session state
    lat = st.number_input("Latitude:", min_value=-90.0, max_value=90.0, value=bi.get("latitude", 0.0), format="%.4f", key="latitude_input")
    lon = st.number_input("Longitude:", min_value=-180.0, max_value=180.0, value=bi.get("longitude", 0.0), format="%.4f", key="longitude_input")

    st.markdown("**Timezone**")
    # Find index for current timezone value
    current_tz_value = bi.get("timezone", 5.5) # Default to IST if not set
    try:
        tz_index = TIMEZONE_LABELS.index(
            next(lbl for lbl, val in TIMEZONE_OPTIONS.items() if val == current_tz_value)
        )
    except (StopIteration, ValueError):
        tz_index = TIMEZONE_LABELS.index("UTC+05:30 IST") # Fallback index

    sel_tz_label = st.selectbox("Select Timezone:", TIMEZONE_LABELS, index=tz_index, key="timezone_select")
    tz_value = TIMEZONE_OPTIONS[sel_tz_label]

# Advanced Calculation Settings (initially collapsed)
with st.expander("Advanced Calculation Settings"):
    obs_opts = ["topocentric", "geocentric"]
    # Use session state keys directly for selectbox index finding
    try:
        obs_index = obs_opts.index(st.session_state.obs_input)
    except ValueError:
        obs_index = 0 # Default to topocentric
    obs = st.selectbox("Observation Point:", obs_opts, index=obs_index, key="obs_input_widget",
                       help="Topocentric is observer on Earth's surface, Geocentric is Earth's center.")

    ay_opts = ["lahiri", "sayana"]
    try:
        ayn_index = ay_opts.index(st.session_state.ayn_input)
    except ValueError:
        ayn_index = 0 # Default to lahiri
    ayn = st.selectbox("Ayanamsha:", ay_opts, index=ayn_index, key="ayn_input_widget",
                       help="Lahiri is commonly used in Vedic astrology. Sayana uses the tropical zodiac.")
    # Update session state based on widget selection immediately
    st.session_state.obs_input = obs
    st.session_state.ayn_input = ayn


# Consolidate UI inputs into session_state.birth_info before fetching
# This ensures the latest values from the UI are used
st.session_state.birth_info = {
    "name": st.session_state.name_input,
    "year": bd.year, "month": bd.month, "date": bd.day,
    "hours": st.session_state.hour_input,
    "minutes": st.session_state.minute_input,
    "seconds": st.session_state.second_input,
    "latitude":  st.session_state.latitude_input,
    "longitude": st.session_state.longitude_input,
    "timezone":  tz_value, # Get value from selected label
    "observation_point": st.session_state.obs_input, # Directly from advanced settings state
    "ayanamsha":         st.session_state.ayn_input  # Directly from advanced settings state
}

st.markdown("---")
# -------------------------------------------------------------------
# UI: Chart Selection & Fetch
# -------------------------------------------------------------------
st.subheader("Select Charts to Fetch")
# --- ADDED NOTICE ---
st.caption("ℹ️ If you encounter errors during data fetching, please wait ~5 minutes and try again. This can happen due to API rate limits or temporary service issues.")
# --- END NOTICE ---

c1, c2 = st.columns(2)
if c1.button("Select All Charts"):
    for k in CHART_ENDPOINTS: st.session_state[f"cb_{k}"] = True
    st.rerun() # Rerun to reflect checkbox changes immediately
if c2.button("Unselect All Charts"):
    for k in CHART_ENDPOINTS: st.session_state[f"cb_{k}"] = False
    st.rerun() # Rerun to reflect checkbox changes immediately

# Display checkboxes in columns
cols = st.columns(3)
selected_charts = {} # Dictionary to store user's selection status
chart_options = list(CHART_ENDPOINTS.keys())
charts_per_col = (len(chart_options) + len(cols) - 1) // len(cols) # Calculate items per column

for i, chart_name in enumerate(chart_options):
    col_index = i // charts_per_col
    # Use the session state key for the checkbox value and key
    is_selected = cols[col_index].checkbox(chart_name,
                                           value=st.session_state.get(f"cb_{chart_name}", True),
                                           key=f"cb_{chart_name}")
    selected_charts[chart_name] = is_selected # Store the current status

# Main Fetch Button
if st.button("Fetch Astrological Data", type="primary", key="fetch_data_btn"):
    # Use the consolidated birth_info from session state
    current_bi = st.session_state.birth_info

    # Re-validate required fields before attempting API call
    missing = [k for k in EXPECTED_BI_KEYS if k not in current_bi or current_bi[k] is None]
    # Also check for potentially empty strings that are required numerically
    if not current_bi.get("latitude") is not None: missing.append("latitude")
    if not current_bi.get("longitude") is not None: missing.append("longitude")

    if missing:
        st.error(f"Incomplete birth details. Please provide: {', '.join(sorted(list(set(missing))))}")
    else:
        # Get the list of charts the user actually selected NOW
        charts_to_fetch = [name for name, selected in selected_charts.items() if selected]

        if not charts_to_fetch:
            st.warning("Please select at least one chart to fetch.")
        else:
            # Clear previous results before starting new fetch
            st.session_state.results = None
            st.session_state.readable = None
            st.info(f"Starting fetch for {len(charts_to_fetch)} chart(s)...")

            api_key = st.session_state.user_api_key.strip() or DEFAULT_ASTRO_API_KEY
            # Construct the payload from the validated birth_info
            payload = {
                "year": current_bi["year"], "month": current_bi["month"], "date": current_bi["date"],
                "hours": current_bi["hours"], "minutes": current_bi["minutes"], "seconds": current_bi["seconds"],
                "latitude": current_bi["latitude"], "longitude": current_bi["longitude"],
                "timezone": current_bi["timezone"],
                "settings": {
                    "observation_point": current_bi["observation_point"],
                    "ayanamsha": current_bi["ayanamsha"],
                    "language": "en" # Keep language fixed for now
                }
            }

            results_accumulator = {}
            has_errors = False
            progress_bar = st.progress(0.0)
            status_text = st.empty() # Placeholder for status updates

            for idx, chart_name in enumerate(charts_to_fetch):
                endpoint = CHART_ENDPOINTS[chart_name]
                status_text.text(f"Fetching {chart_name} ({idx+1}/{len(charts_to_fetch)})...")

                # Fetch data for the current chart
                res = fetch_astro_data(api_key, endpoint, payload)
                results_accumulator[chart_name] = res

                # Update progress bar
                progress = (idx + 1) / len(charts_to_fetch)
                progress_bar.progress(progress)

                # Check if the result indicates an error
                if not isinstance(res, dict) or res.get("statusCode") != 200:
                    has_errors = True
                    # Error message is already displayed by fetch_astro_data
                    status_text.warning(f"Error fetching {chart_name}. Check error message above.")
                    # Optionally break or continue based on desired behavior for errors
                    # break # Uncomment to stop fetching on first error

                # Wait before the next call (if not the last one)
                if idx < len(charts_to_fetch) - 1:
                    pytime.sleep(API_CALL_DELAY)

            progress_bar.empty() # Remove progress bar on completion
            status_text.empty()  # Clear status text

            # Final status message
            if has_errors:
                st.warning("Fetch completed with some errors. Results might be incomplete.")
            else:
                st.success("Fetch complete.")

            # Store results and generate readable output
            st.session_state.results = results_accumulator
            # Generate readable summary using the *used* birth info and the fetched results
            st.session_state.readable = generate_readable(current_bi, results_accumulator)
            # Rerun to display results section
            st.rerun()


st.markdown("---")

# -------------------------------------------------------------------
# UI: Display & Download Results
# -------------------------------------------------------------------
# This section only shows if results are present in session state
if st.session_state.get("results"):
    st.subheader("Results & Downloads")

    # Apply custom styling for green download buttons
    st.markdown("""
    <style>
      div.stDownloadButton > button {
        background-color: #28a745 !important; /* Green */
        color: white !important;
        border: 1px solid #218838 !important; /* Darker green border */
        border-radius: 5px;
        padding: 0.4rem 0.75rem;
      }
      div.stDownloadButton > button:hover {
        background-color: #218838 !important; /* Darker green on hover */
        border-color: #1e7e34 !important;
      }
    </style>
    """, unsafe_allow_html=True)

    # Generate filename base (using potentially updated name)
    bi_for_filename = st.session_state.birth_info
    safe_name = "".join(c for c in bi_for_filename.get("name", "chart") if c.isalnum() or c in "-_").strip() or "chart"
    date_str = f"{bi_for_filename.get('date', 'DD'):02d}-{bi_for_filename.get('month', 'MM'):02d}-{bi_for_filename.get('year', 'YYYY')}"
    base_filename = f"{safe_name}-{date_str}"

    # Prepare data for download
    try:
        raw_json_data = json.dumps(st.session_state.results, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not serialize results to JSON: {e}")
        raw_json_data = "{}" # Provide empty JSON on error

    readable_text_data = st.session_state.get("readable", "No readable summary generated.")

    try:
        birth_info_json_data = json.dumps(st.session_state.birth_info, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not serialize birth info to JSON: {e}")
        birth_info_json_data = "{}"

    # Download Buttons in columns
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

    # Usage Instructions
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

    # Expanders for inline preview
    with st.expander("View Readable Summary"):
        st.text_area("Summary Preview:", readable_text_data, height=350, key="readable_preview", disabled=True)

    with st.expander("View Raw Chart JSON"):
        st.json(st.session_state.results, expanded=False) # Keep it collapsed by default

    # Expander for Birth Details JSON (for reloading)
    with st.expander("View Birth Details JSON (for Reuse)"):
        st.markdown(
            "Copy the JSON below and save it. You can paste it into the **Load Saved Birth JSON** section at the top to quickly restore these birth details later."
        )
        st.text_area("Birth JSON:", birth_info_json_data, height=250, key="birth_info_preview", disabled=True)

    st.markdown("---")

# -------------------------------------------------------------------
# UI: Advanced Settings & Clear
# -------------------------------------------------------------------
with st.expander("Advanced Settings & App Reset"):
    st.text_input("Custom Astrology API Key (Optional)", key="user_api_key", type="password",
                  help="Enter your personal API key from freeastrologyapi.com if you have one. Otherwise, a default key is used.")

    if st.button("Clear All Inputs & Results", key="clear_all_btn",
                 help="Resets all birth details, chart selections, and results. Keeps custom API key if entered."):
        # Preserve API key if user entered one
        preserved_key = st.session_state.get("user_api_key", "")
        # Get list of keys to delete (avoid modifying dict while iterating)
        keys_to_delete = [k for k in st.session_state.keys() if k != 'user_api_key']
        for k in keys_to_delete:
            del st.session_state[k]
        # Restore the key
        st.session_state.user_api_key = preserved_key
        # Re-initialize essential states after clearing
        st.session_state.birth_info = {}
        st.session_state.results = None
        st.session_state.readable = None
        st.session_state.obs_input = "topocentric" # Reset advanced settings state
        st.session_state.ayn_input = "lahiri"
        for k in CHART_ENDPOINTS: # Reset checkboxes
            st.session_state[f"cb_{k}"] = True
        st.success("All inputs and results cleared.")
        st.rerun() # Rerun to reflect the cleared state


st.markdown("---")
st.caption("Built using Streamlit | Astrology data via freeastrologyapi.com | Geocoding via geocode.maps.co")
