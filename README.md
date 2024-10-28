# Project: Esports Team Odds Parser

## Description
This project is a parser that continuously monitors odds for esports teams and sends notifications to a Telegram bot when odds change. It also saves data to a database for further analysis and allows users to view graphs of odds changes for selected matches.

## Features
- 24/7 Monitoring: The parser tracks changes in match odds around the clock.
- Notifications: Significant changes in odds trigger notifications sent via the Telegram bot.
- Database Storage: Data is saved in database for analytical purposes.
- Odds Change Graphs: The bot provides users with odds change graphs for each match upon request.

Technologies
- Python: Programming language.
- FastAPI: Framework for building the API.
- aiogram **2.9.0**: Library for working with the Telegram Bot API.
- sqlite3: Database for storing odds data (can also use PostgreSQL if preferred).
- requests: For handling HTTP requests to fetch data.
- pandas: For data manipulation and analysis.
- numpy: For numerical operations.
- seaborn: For data visualization, particularly for plotting odds changes.

## Installation

1. Clone this repository

```bash
git clone https://github.com/tsunamicxde/bet_scraper.git
```

2. Configure environment variables in **config.py**:

```python
api_url = 'your_fast_api_url' 
bot_token = "your_bot_token"
```

3. Add your proxy servers in **raybet_scraper.py**:

```python
proxies_list = [{
    "https": "http://username:password@ip:port"
}]
```
> **Note**: The proxies provided in the repository are for example purposes and may be expired. Add your own working proxies for stable monitoring.

## Launch

To start the app, run:

```bash
uvicorn bet_api.api:app --host 127.0.0.1 --port 5432
python bot.py
python raybet_scraper.py
```

## Developers

- [tsunamicxde](https://github.com/tsunamicxde)
   
