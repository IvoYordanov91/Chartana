# 📊 Chartana – Accelerate Your Data Analysis

Chartana is a web-based data analytics platform designed to speed up exploratory data analysis (EDA), automate preprocessing, and generate insights and reports from CSV datasets with minimal effort. It’s perfect for marketing teams, analysts, and data-driven decision makers.

## 🚀 Features

- 🔐 **User Authentication** – Register/login securely with password hashing and session handling
- 📂 **Dataset Upload** – Upload `.csv` files with customizable separators
- 🧹 **Data Preprocessing** –
  - Column type mapping
  - Missing value detection
  - Duplicate removal and merging
  - Intelligent default filling based on column logic
- 👁️ **Data Preview** – Visual inspection of uploaded data, missing data summaries, and duplicates
- 📈 **Interactive Dashboard** –
  - ROI and performance KPIs by channel and time period
  - Visualized seasonal trends
  - Campaign comparisons by audience and efficiency
- 🧠 **Recommendations Engine** –
  - Automatically surfaces actionable insights
  - Detects anomalies and highlights top & underperforming campaigns
- 🖼️ **Custom Visualizations** – Built-in Chart.js graphs for ROI, net profit, campaign duration analysis, and more

---

## 🛠️ Tech Stack

| Component         | Tech                          |
|------------------|-------------------------------|
| Backend          | Flask (Python 3.13)           |
| Frontend         | Bootstrap 5 + Chart.js        |
| Forms            | Flask-WTF                     |
| Database         | SQLite (for dev), PostgreSQL (planned) |
| Data Processing  | Pandas, NumPy                 |
| Deployment       | Vercel / Render / Custom VPS  |

---

## 📦 Project Structure

Chartana/
    │ ├── init.py
    │ ├── routes.py
    │ ├── forms.py
    │ ├── models.py
    │ ├── preprocessing.py
    │ ├── static/
    │ └── templates/
        │ ├── base.html
        │ ├── index.html
        │ ├── loginForm.html
        │ ├── registrationForm.html
        │ ├── dashboard.html
        │ └── ...
    │ ├── cleaned_marketing_campaigns.csv
    | ├── run.py
    | ├── config.py
    | ├── requirements.txt
    | └── README.md

## ✅ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/IvoYordanov91/Chartana
cd chartana
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
flask run
```

## Demo Dataset

A sample marketing campaign dataset (cleaned_marketing_campaigns.csv) is included for demo purposes. It has been fully cleaned, preprocessed, and is used in the default dashboard to showcase insights.

## 📅 Roadmap

- [ ] Support for `.sql` and database ingestion
- [ ] Save user-specific datasets & dashboards
- [ ] Export charts and insights as PDF reports
- [ ] Drag-and-drop dashboard builder
- [ ] Team collaboration features

## Contribution

Want to contribute? Open and Issue or submit a PR. All contributions are welcome!

## Acknowledgements

Big thanks to open-source libraries like:
- Flask
- Pandas
- Chart.js
- Bootstrap
- Jinja2