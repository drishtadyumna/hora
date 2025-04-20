# 🔯 Vedic Divisional Charts App

A Streamlit web application that computes Vedic divisional (Varga) charts D1–D60 (plus extended planetary info) based on your birth details, using the [Free Astrology API](https://www.freeastrologyapi.com/) and geocoding via [Maps.co](https://geocode.maps.co/).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://jyotish.streamlit.app/)  

---

## ✨ Features

- **User‑Friendly Input**  
  • Name, Date, Time (24h), Latitude & Longitude (decimal°), Time Zone  
  • Dropdowns for Ayanamsha (Lahiri/Sayana) and Observation point (topocentric/geocentric)  

- **Geocoding by Place Name**  
  • Type a city/place and fetch coordinates automatically  

- **Load/Save JSON**  
  • Paste previously exported birth‑info JSON to reload your data in one click  

- **Selective Fetch**  
  • All 20+ divisional charts (D1–D60) plus “Planets Extended Info” are pre‑selected  
  • Uncheck any charts you don’t need  

- **API Integration**  
  • Uses your Free Astrology API Key (or a default key) to retrieve each chart  
  • Rate‑limits built‑in with configurable delay  

- **Multi‑Format Output**  
  • Raw JSON structure with full API responses  
  • Plain‑text “Readable Summary” combining all chart positions, signs, degrees, retrograde flags, houses & nakshatras  
  • Download buttons for both `.json` and `.txt`  

- **Clear & Restart**  
  • One‑click “Clear All & Start Over” preserves only your custom API key  

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+  
- pip (or conda)  
- A Free Astrology API Key (register at https://www.freeastrologyapi.com/)

### Steps

1. **Clone the repo**  
   ```
   git clone https://github.com/your‑username/vedic-charts-app.git
   cd vedic-charts-app
   ```

2. **Create & activate a virtual environment** (highly recommended)  
   ```
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**  
   ```
   pip install -r requirements.txt
   ```

4. **Run the app**  
   ```
   streamlit run app.py
   ```
   Then open http://localhost:8501 in your browser.

---

## 🚀 How to Use

1. **(Optional) Paste your API key**  
   Expand **Advanced Settings** and paste your Free Astrology API Key.  
   If left blank, the app will use a public demo key.

2. **(Optional) Load saved birth JSON**  
   Expand **Load Saved Birth JSON**, paste the JSON export from a previous session, and click **Load JSON**.

3. **(Optional) Geocode a place**  
   In **Lookup Coordinates by Place**, enter e.g. “New York, USA” and click **Fetch Coordinates** to auto‑fill latitude/longitude.

4. **Fill in Birth Details**  
   - Name  
   - Date (calendar picker)  
   - Time (Hour/Minute/Second)  
   - Latitude & Longitude (decimal degrees)  
   - Time Zone (select from friendly labels)  
   - Ayanamsha & Observation point  
   Click **Save Details**.

5. **Select Charts**  
   All divisional charts are checked by default. Un‐check any you don’t need.

6. **Fetch Data**  
   Click **Fetch Astrological Data**. A progress bar and status messages will show API calls in flight.

7. **Download & View**  
   - **Download Raw JSON**: full API responses  
   - **Download Readable TXT**: combined plain‑text summary  
   - Expand **Readable Summary** or **Raw JSON** to preview in‑app.

8. **Start Over**  
   Click **Clear All & Start Over** to reset everything (your custom API key is preserved).

---

## 📸 Screenshot

![App Screenshot](placeholder.png)  
*(Replace `placeholder.png` with an actual screenshot of your app.)*

---

## 📝 Example Input / Output

**Example Input**  
- Name: *Example Person*  
- Date: 1990‑04‑15  
- Time: 06:30:00  
- Lat/Lon: 28.6139, 77.2090 (New Delhi)  
- Time Zone: UTC+05:30 IST  
- Ayanamsha: lahiri  
- Observation: topocentric  
- Charts: all selected  

**Example Readable TXT Output**  
```
========================================
BIRTH DETAILS
Name: Example Person
Date: 1990-04-15
Time: 06:30:00
Location: 28.6139, 77.2090
Timezone: UTC+05:30 IST
Ayanamsha: lahiri
Observation: topocentric
========================================

-- D1 (Rasi Chart) --
Ascendant: Aries (1) 14.23°, Direct | H1 | Nak:Ashwini
Sun: Pisces (12) 29.17°, Direct | H12 | Nak:Revati
Moon: Libra (7) 03.45°, Direct | H7  | Nak:Chitra
Mars: Taurus (2) 18.56°, Direct | H2  | Nak:Rohini
Mercury: Pisces (12) 02.11°, Direct
Jupiter: Cancer (4) 10.37°, Direct | H4  | Nak:Ashlesha
Venus: Aries (1) 25.89°, Direct | H1  | Nak:Savitha
Saturn: Capricorn (10) 05.12°, Direct | H10 | Nak:Uttara
Rahu: Cancer (4) 20.77°, Direct
Ketu: Capricorn (10) 20.77°, Direct

-- Planets Extended Info --
Sun: Pisces (12) 29.17°, Direct | H12 | Nak:Revati
…  
----------------------------------------
BIRTH JSON (for reload)
{
  "name": "Example Person",
  "year": 1990,
  "month": 4,
  "date": 15,
  "hours": 6,
  "minutes": 30,
  "seconds": 0,
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": 5.5,
  "observation_point": "topocentric",
  "ayanamsha": "lahiri"
}
========================================
```

---

## 📄 License

[MIT License](LICENSE)  

---

## ❤️ Acknowledgments

- [Streamlit](https://streamlit.io/)  
- [Free Astrology API](https://www.freeastrologyapi.com/)  
- [Maps.co Geocoding](https://geocode.maps.co/)  

Feel free to ⭐ the repo if you find it useful!
