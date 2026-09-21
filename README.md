# Machine Learning-Driven Digital Asset Analytics System

This is a containerized system composed of a Spring Boot application, two FastAPI microservices, 
and a PostgreSQL database. It integrates historical market data and news sentiment analysis to provide 
machine-learning insights for digital assets.

---

## Technologies Used

[![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)](https://www.java.com/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Thymeleaf](https://img.shields.io/badge/Thymeleaf-005F0F?logo=thymeleaf&logoColor=white)](https://www.thymeleaf.org/)
[![Maven](https://img.shields.io/badge/Maven-C71A36?logo=apachemaven&logoColor=white)](https://maven.apache.org/)

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)](https://numpy.org/)

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/)

---

## Architecture

The system consists of four services:

- A **Spring Boot** application acting as the main backend and entry point
- A **FastAPI LSTM microservice** for machine-learning predictions
- A **FastAPI NLP microservice** for news sentiment analysis
- A **PostgreSQL** database for persistent storage

Services communicate internally through Docker’s network.

---

## Project Structure

```text
digital-asset-analytics-system/
│
├── analytics/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/trifunovska/analytics/
│   │   │   │   ├── model/              
│   │   │   │   ├── repository/         
│   │   │   │   ├── service/            
│   │   │   │   ├── web/                
│   │   │   │   └── AnalyticsApplication.java
│   │   │   │
│   │   │   └── resources/
│   │   │       ├── templates/           
│   │   │       ├── static/             
│   │   │       └── application.properties
│   │   │
│   │   └── test/                        
│   │
│   ├── python/
│   │   ├── lstm/
│   │   │   ├── app.py                   
│   │   │   └── lstm.py                  
│   │   │
│   │   └── nlp/
│   │       ├── app.py                 
│   │       └── nlp.py                  
│   │
│   ├── pom.xml
│   ├── mvnw
│   └── mvnw.cmd
│
├── db/
│   ├── 01_schema.sql                    
│   ├── 02_load_ohlcv.sql             
│   ├── 03_load_news.sql               
│   └── data/
│       ├── ohlcv.csv                 
│       └── news.csv                    
│
└── README.md
```

---

## Exposed Ports

| Service  | Technology   | Port |
|----------|--------------|------|
| spring   | Spring Boot  | 8080 |
| lstm     | FastAPI      | 8000 |
| nlp      | FastAPI      | 8001 |
| postgres | PostgreSQL   | 5432 |

---

## Service Description

### Spring Boot (8080)
Acts as the main application of the system.  
Handles client requests and communicates with the FastAPI microservices.

### LSTM Microservice (8000)
A Long Short-Term Memory (LSTM) neural network is trained as a univariate time-series regression problem, where sequences of past closing prices are used to predict the next time step.

A sliding window (lookback) approach is applied, and the network consists of stacked LSTM layers followed by a fully connected output layer.

Exposes REST endpoints used by the Spring application.

### NLP Microservice (8001)
News sentiment analysis is performed using a pretrained transformer natural language processing model.

Recent cryptocurrency news articles are retrieved from the database and analyzed using a DistilBERT model fine-tuned on the Stanford Sentiment Treebank (SST-2).

Each article is classified as positive or negative, along with a confidence score.

Exposes REST endpoints used by the Spring application.

### PostgreSQL (5432)
Relational database used for storing application data.

---

## API Documentation

Each service exposes interactive documentation:

| Service         | Port | Documentation |
|----------------|------|---------------|
| lstm | 8000 | `/docs` |
| nlp  | 8001 | `/docs` |

---

## Running the Project

```bash
docker compose up --build
