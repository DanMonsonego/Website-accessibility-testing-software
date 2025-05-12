🧪 Usage
Accessibility Check

Select “Accessibility Check” in the sidebar.

Enter a web page URL or upload an .html file.

Click Start Check.

View metrics, tables, pie & bar charts.

Download CSV and PDF reports.

Show Standard

Select “Show Standard” to view the embedded SI 5568 PDF.

Search Clauses

Select “Search Clauses” and type a keyword to filter the SI 5568 clause list.

📂 Project Structure
yaml
Copy
Edit
.
├── .venv/                         # Python virtual environment
├── app.py                         # Main Streamlit application
├── requirements.txt               # Python dependencies
├── DejaVuSans.ttf                 # Unicode font for PDF generation
├── IP5568/
│   └── 5568.pdf                   # Official SI 5568 standard PDF
└── README.md                      # This file
⚙️ Configuration
Page Settings:
In app.py, st.set_page_config(page_title="SI5568 Accessibility Checker", layout="wide")

Logging & Caching:
The fetch & parse function is cached (@st.cache_data) to avoid repeated network calls during a session.

🐛 Troubleshooting
“WebDriver” errors:
Ensure you’re using Selenium 4.6+ so that Selenium Manager can auto-download ChromeDriver.
Make sure Google Chrome is installed and up to date.

Font not found:
Confirm DejaVuSans.ttf exists in the project root.

Permission errors on Windows:
If PowerShell blocks script execution, run:

powershell
Copy
Edit
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
📜 License
MIT License © 2025 Your Name
