import json
from extract import search_tracks

data = search_tracks("ar rahman", 50)

print(json.dumps(data, indent=2)[:2000])