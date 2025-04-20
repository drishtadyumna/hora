# 🌌 Vedic Divisional Charts Calculator

A Streamlit web application that calculates Vedic divisional charts (Vargas) based on user-provided birth details using the [Free Astrology API](https://www.freeastrologyapi.com/).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-deployed-app-url.streamlit.app) <!-- Replace with your deployment URL -->

---

## ✨ Features

*   **Easy Input:** User-friendly form for entering Name, Birth Date, Time, Location (Lat/Long), and Time Zone.
*   **API Key Management:** Securely input and use your Free Astrology API key (stored temporarily in session state).
*   **Customizable Chart Selection:** Choose which divisional charts (D1 to D60, plus extended planet info) you want to fetch. All are selected by default.
*   **API Integration:** Connects directly to the Free Astrology API endpoints.
*   **JSON Output:** Fetches astrological data in raw JSON format.
*   **Data Export:** Combines all selected chart data into a single JSON structure and provides a download button for a `.txt` file.
*   **GitHub Ready:** Includes necessary files (`requirements.txt`, `.gitignore`, `.devcontainer`) for easy cloning, setup, and potential deployment.

---

## 🛠️ Setup & Installation

**Prerequisites:**

*   Python 3.8+
*   pip (Python package installer)
*   A Free Astrology API Key ([Get one here](https://www.freeastrologyapi.com/))

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/vedic-charts-app.git # Replace with your repo URL
    cd vedic-charts-app
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Get your API Key:**
    *   Sign up or log in at [Free Astrology API](https://www.freeastrologyapi.com/).
    *   Find your API key in your account section.

5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

6.  **Open your browser:** Navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

---

## 🚀 How to Use

1.  **Enter API Key:** Paste your Free Astrology API key into the designated field at the top.
2.  **Fill Birth Details:** Complete the form with accurate birth information (Name, Date, Time, Latitude, Longitude, Time Zone).
3.  **Select Charts:** Uncheck any divisional charts you *don't* want to fetch (all are checked by default).
4.  **Fetch Data:** Click the "✨ Fetch Astrological Data" button.
5.  **Download Results:** Once processing is complete, click the "📥 Download All Chart Data (.txt)" button to save the combined JSON output.
6.  **(Optional) View Raw JSON:** Expand the "View Raw JSON Output" section to see the data directly in the app.

---

## 📸 Screenshot

*   *(Placeholder: Add a screenshot of the running application here)*
    ```
    ![App Screenshot](placeholder.png)
    ```

---

## 📝 Example Input / Output

**Example Input:**

*   **Name:** Example Person
*   **Birth Date:** 2022-08-11
*   **Birth Time:** 06:00:00
*   **Latitude:** 17.3833
*   **Longitude:** 78.4666
*   **Time Zone:** 5.5
*   **Charts:** (Default - All selected)

**Example Output (`.txt` file content):**

```json
{
    "D1 (Rasi Chart)": {
        "statusCode": 200,
        "input": { ... }, // Echoed input details
        "output": [ { ... }, { ... } ] // Planet data for Rasi
    },
    "Planets Extended Info": {
        "statusCode": 200,
        "output": {
             "Ascendant": { ... }, // Detailed planet info including Nakshatra etc.
             "Sun": { ... },
             // ... other planets
        }
    },
    "D2 (Hora Chart)": {
        "statusCode": 200,
        "output": {
            "0": { "name": "Ascendant", ... },
            "1": { "name": "Sun", ... },
            // ... other planets for D2
        }
    },
    // ... Data for other selected charts (D3, D4, ..., D60)
    "D9 (Navamsa Chart)": {
         "statusCode": 200,
         "output": { ... } // Planet data for D9
    },
     // ... etc.
}
