The module allows you to retrieve inflation data from the Central Bank of the Russian Federation website

Example code for retrieving a value for the current date:
from cbr_inflation import get_inflation
df = get_inflation()
inf = df.iloc[-1]
print(f"Инфляция: {inf:.2f}%")
The get_latest_inflation function allows you to retrieve the latest inflation value. Code:
from cbr_inflation import get_latest_inflation
df = get_latest_inflation()
