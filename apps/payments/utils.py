CITY_COMMISSION_RATES = {
    "Berlin": 0.25,
    "Hamburg": 0.23,
    "Munich": 0.25,
    "Rostock": 0.15,
    "Leipzig": 0.17,
    # Default fallback
    "default": 0.20
}

def calculate_commission(city, base_rent):
    rate = CITY_COMMISSION_RATES.get(city, CITY_COMMISSION_RATES["default"])
    commission = base_rent * rate
    return commission, rate
