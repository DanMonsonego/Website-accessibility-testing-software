````markdown
# SI5568 Accessibility Checker

A Streamlit-based web application that audits web pages (or local HTML files) against the Israeli SI 5568 accessibility standard.  
It runs a suite of automated checks and produces interactive charts, plus downloadable CSV and PDF reports summarizing pass/fail results.

---

## 🚀 Features

- **Automated Accessibility Checks**  
  - `<html lang>` attribute  
  - `<title>` tag  
  - Meta viewport  
  - Skip links  
  - ARIA landmarks  
  - Empty link detection  
  - Heading sequence  
  - `<img alt>` attributes  
  - Video captions  
  - Color contrast (WCAG 4.5:1)  
  - Form field labels  
  - ARIA labels  
  - Accessibility statement  

- **Interactive UI**  
  - Enter a URL or upload an HTML file  
  - Sidebar navigation:  
    - **Accessibility Check**  
    - **Show Standard** (embed SI 5568 PDF)  
    - **Search Clauses**  
  - Pass/Fail **pie chart** and **bar chart**  
  - Metrics: number of passed vs failed checks  
  - Download **CSV** & **PDF** reports  

---

## 📥 Clone & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/DanMonsonego/Website-accessibility-testing-software.git
   cd Website-accessibility-testing-software
````

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   ```

3. **Activate the environment**

   * **Windows (PowerShell):**

     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD):**

     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   * **macOS / Linux:**

     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Place required assets**

   * Copy `DejaVuSans.ttf` into the project root (for full Unicode PDF support).
   * Ensure the official standard PDF is at `IP5568/5568.pdf` if you want the “Show Standard” view.

---

## ▶️ Running the App

With the virtual environment active:

```bash
streamlit run app.py
```

After a moment, Streamlit will display something like:

```
Local URL: http://localhost:8501
```

Open that URL in your browser to interact with the application.

---

## 🧪 Usage Guide

1. **Accessibility Check**

   * Select **Accessibility Check** in the sidebar.
   * Enter a web page URL **or** click **Upload HTML** to choose a local `.html` file.
   * Click **Start Check**.
   * View:

     * Metrics (passed vs failed counts)
     * Detailed table of each rule
     * Pie chart (pass/fail ratio)
     * Bar chart (count of checks)
   * Download results as CSV or PDF.

2. **Show Standard**

   * Select **Show Standard** to view the embedded SI 5568 PDF document.

3. **Search Clauses**

   * Select **Search Clauses**, type a keyword to filter the list of SI 5568 clauses, and view matching keys and descriptions.

---

## 📂 Project Structure

```
.
├── .venv/                      # Python virtual environment
├── app.py                      # Main Streamlit application
├── requirements.txt            # Project dependencies
├── README.md                   # This file
├── DejaVuSans.ttf              # Font for PDF generation
├── IP5568/                     # Folder for standard PDF
│   └── 5568.pdf  
└── .gitignore                  # Ignore patterns for Git
```

---

## ⚙️ Configuration & Customization

* **Page settings** are defined at the top of `app.py` via:

  ```python
  st.set_page_config(page_title="SI5568 Accessibility Checker", layout="wide")
  ```
* **CSS overrides** live in `app.py` under the `st.markdown` block.
* **Caching** with `@st.cache_data` ensures repeat runs on the same URL are fast.

---

## 🐞 Troubleshooting

* **WebDriver errors**

  * Ensure you have Selenium 4.6+ installed so that Selenium Manager can auto-download ChromeDriver.
  * Verify Google Chrome is installed and up to date.

* **Font issues**

  * If PDF output is garbled, confirm `DejaVuSans.ttf` is in the project root.

* **Permission errors on Windows (PowerShell)**

  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

* **Git push conflicts**
  Fetch and merge remote changes before pushing:

  ```bash
  git fetch origin
  git merge origin/main
  git push origin main
  ```

---

## 📜 License

This project is licensed under the MIT License. © 2025 Dan Monsonego

---

```
```
