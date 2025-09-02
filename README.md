# Zillow Bot

Automated property search bot that scrapes Zillow listings and emails CSV reports to specified recipients.

## Setup

```bash
pip install -r requirements.txt
python src/bot.py
```

## Sample Config (`config.json`)

```json
{
  "api": {
    "host": "zillow-com1.p.rapidapi.com",
    "key": "your-rapidapi-key-here",
    "endpoint_path": "/propertyExtendedSearch"
  },
  "email_list": [
    "buyer1@email.com",
    "buyer2@email.com"
  ],
  "email_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "bot@email.com",
    "sender_password": "your-app-password"
  },
  "search_params": {
    "locations": "San Mateo, CA; Redwood City, CA; Sunnyvale, CA",
    "status_type": "ForSale",
    "home_type": "Houses",
    "max_price": "2000000",
    "days_on": "90"
  }
}
```

## Sample Report Output

| address | price | zestimate | bedrooms | bathrooms | days_on_zillow | sqft |
|---------|-------|-----------|----------|-----------|----------------|------|
| 123 Oak St, San Mateo, CA | 1250000 | 1275000 | 3 | 2 | 15 | 1850 |
| 456 Pine Ave, Redwood City, CA | 1800000 | 1750000 | 4 | 3 | 7 | 2400 |
| 789 Elm Dr, Sunnyvale, CA | 1950000 | 1900000 | 4 | 2.5 | 32 | 2200 |
