# StoreHQ - Small Business Inventory Manager

MISY 350 Final Project - Phase 2
Shahriar Rahman

## Live App and Repository

- **Streamlit App:** https://misy350-final-project-app-shahriar-rahman.streamlit.app
- **GitHub Repo:** https://github.com/shahriar-projects/misy350-final-project-app

## Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Shop Owner | owner1 | owner123 |
| Employee | employee1 | emp123 |

## How to Run Locally

```bash
pip install streamlit openai
python -m streamlit run app.py
```

## Project Overview

StoreHQ is a multi-page Streamlit web application for managing a small retail store's inventory. It supports two distinct user roles, full CRUD functionality backed by JSON storage, a refactored three-layer code architecture, and an AI assistant powered by OpenAI.

## User Roles and Features

**Shop Owner**
- View full inventory with stock level indicators and summary metrics
- Add new products
- Edit existing product details and restock levels
- Delete discontinued products

**Employee**
- Browse the product catalog filtered by category
- Log daily sales (automatically decrements stock)
- View recent sales history
- Use the AI assistant (live OpenAI or demo mode)

## Code Architecture

| File | Layer | Responsibility |
|------|-------|----------------|
| app.py | UI Layer | All Streamlit pages, widgets, navigation, session state |
| services.py | Service Layer | Business logic, classes (User, InventoryItem, AIAssistant), password hashing |
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

## AI Assistant

The AI assistant is available on the Employee dashboard. Enter your OpenAI API key when prompted for live AI answers, or use Demo Mode to test without a key. The API key is entered at runtime and is never stored in any file.
