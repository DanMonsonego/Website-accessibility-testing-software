# SI5568 Accessibility Checker

A Streamlit-based web application to audit web pages (or local HTML files) against the SI 5568 accessibility standard.  
Runs a suite of automated checks and generates CSV/PDF reports and interactive charts (pie and bar) showing pass/fail results.

---

## Features

- **Automated Accessibility Checks**  
  - HTML `<html lang>` attribute  
  - `<title>` presence  
  - Meta viewport  
  - Skip links  
  - ARIA landmarks  
  - Empty link detection  
  - Heading sequence  
  - `<img alt>` presence  
  - Video captions  
  - Color contrast (WCAG 4.5:1)  
  - Form labels  
  - ARIA labels  
  - Accessibility statement  

- **Interactive Streamlit UI**  
  - Enter a URL or upload a local HTML file  
  - Sidebar navigation: “Accessibility Check”, “Show Standard” (embed PDF), “Search Clauses”  
  - Charts: pass/fail pie chart and bar chart  
  - Metrics: counts of passed vs failed checks  
  - Downloadable CSV & PDF reports  

---

## 🛠️ Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/youruser/si5568-accessibility-checker.git
   cd si5568-accessibility-checker
