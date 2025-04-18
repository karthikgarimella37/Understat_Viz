### 📘 `README.md` for **Understat_Viz**


# ⚽ Understat_Viz

**Understat_Viz** is a data pipeline and visualization dashboard that extracts and analyzes soccer players' shot data from the [Understat](https://understat.com/) website. This project focuses on EPL (English Premier League) players and generates interactive shot maps to support performance analysis for players, analysts, and fans.


---

## 📊 Project Overview

This project:
- Scrapes shot data for EPL players from Understat.
- Loads and stages data using Airflow pipelines.
- Stores data in a PostgreSQL database.
- Visualizes player performance via a Streamlit dashboard.
- Uses Docker for containerization of all services.

---

## 🧱 Architecture

```plaintext
Understat.com (Scraped Data)
        |
    [Python Scraper]
        |
     [Airflow DAG]
        |
 [Staging Tables in PostgreSQL]
        |
 [Final Player Shot Table]
        |
   [Streamlit Dashboard]
```

**Tech Stack**:
- 🐍 Python
- ⛅ Airflow (for orchestration)
- 🐘 PostgreSQL (for data storage)
- 📊 Streamlit (for visualization)
- 🐳 Docker (for containerization)
- 📦 Pandas, Polars, Matplotlib

---

## 🚀 Features

- 📈 **Shot Location Maps**: Visualize where players are taking shots on the pitch.
- 🔄 **Automated Workflows**: Airflow manages scraping, processing, and loading.
- 🧪 **Modular Codebase**: Separation of concerns across scraping, transformation, and visualization.
- 🛢️ **SQL Merge Logic**: Staging → Merge → Final tables for efficient updates.

---

## ⚙️ Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/Understat_Viz.git
   cd Understat_Viz
   ```

2. **Start Docker containers**  
   Make sure Docker is installed and running.
   ```bash
   docker-compose up --build
   ```

3. **Run Airflow**  
   Access the Airflow UI at `localhost:8080`, trigger the DAG to start scraping.

4. **Launch Streamlit App**  
   Once data is loaded:
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Explore Dashboard**  
   Navigate to `localhost:8501` to view and interact with the shot maps.

---

## 🧪 Folder Structure

```plaintext
Understat_Viz/
├── airflow/
│   ├── dags/
│   ├── streamlit/
│       └── main.py  
│       └── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 📸 Slides Preview

Presentation slides from the final project demo:


<details>
<p align="center">
- Slide 2: Overview
  <img src="/images/SAT 4650 Final Project slide 2.jpg" alt="Slide 2"/>
- Slide 3–7: Data pipeline, architecture, visualizations

  <img src="/images/SAT 4650 Final Project slide 3.jpg" alt="Slide 3"/>
  <img src="/images/SAT 4650 Final Project slide 4.jpg" alt="Slide 4"/>
  <img src="/images/SAT 4650 Final Project slide 5.jpg" alt="Slide 5"/>
  <img src="/images/SAT 4650 Final Project slide 6.jpg" alt="Slide 6"/>
  <img src="/images/SAT 4650 Final Project slide 7.jpg" alt="Slide 7"/>
</p>
</details>

---


## 📝 License

MIT License. See `LICENSE` file for more details.

---
