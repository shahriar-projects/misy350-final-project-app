# StoreHQ - Small Business Inventory Manager

MISY 350 Final Project - Phase 2
Shahriar Rahman

## Project Overview

StoreHQ is a multi-page Streamlit web application for managing a small retail store's inventory. It supports two distinct user roles, full CRUD functionality backed by JSON storage, a refactored three-layer code architecture, and an AI assistant powered by OpenAI.

## Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Shop Owner | owner1 | owner123 |
| Employee | employee1 | emp123 |

## User Roles and Features

**Shop Owner**
- View full inventory with stock level indicators and summary metrics
- Add new products with name, category, price, and stock
- Edit existing product details and restock levels
- Delete discontinued products

**Employee**
- Browse the product catalog filtered by category
- Log daily sales (automatically decrements stock and saves to sales log)
- View recent sales history
- Use the AI assistant to ask natural language questions about inventory

## Code Architecture (Phase 2)

The app is separated into three layers:

| File | Layer | Responsibility |
|------|-------|----------------|
| app.py | UI Layer | All Streamlit pages, widgets, navigation, session state |
| services.py | Service Layer | Business logic, classes (User, InventoryItem, AIAssistant), functions |
| data.py | Data Layer | JSON file reads and writes with safe write patterns and error handling |

## Project Structure

```
misy350-final-project-app/
├── app.py
├── data.py
├── services.py
├── requirements.txt
└── data/
    ├── users.json
    ├── inventory.json
    └── sales.json
```

## How to Run Locally

```bash
pip install streamlit openai
streamlit run app.py
```

## Deployed Streamlit App

https://misy350-final-project-app-shahriar-rahman.streamlit.app

## GitHub Repository

https://github.com/shahriar-projects/misy350-final-project-app

## AI Assistant

The AI assistant is available on the Employee dashboard. Enter your OpenAI API key when prompted. The assistant receives the full current inventory as context and can answer questions like "what items are low on stock?" or "which products should we reorder?". The API key is entered at runtime and is never stored in any file.
