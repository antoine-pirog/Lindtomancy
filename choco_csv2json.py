import csv
import json
import random
import uuid

random.seed(0)
shortuuid = lambda: uuid.UUID(int=random.getrandbits(128)).hex[:8]

ROW_HEADER = 0
ROW_PRICE = 2
ROWS_IGNORE = [
    1, # Weight
]
ROWS_DATA = 3
COLUMN_NAME = 0
COLUMN_WEIGHT = 1
COLUMN_TOTAL = 3
COLUMNS_DATA = 4

""" PRELOAD DATA """
headers = []
prices = []
choco_data = []
with open('Kilo surprise Lindt  - Feuille 1.csv', encoding="utf-8") as csvfile:
    rdr = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(rdr):
        if i == ROW_HEADER:
            headers = row[COLUMNS_DATA:]
            sessions = [shortuuid() for _ in headers]
        elif i == ROW_PRICE:
            prices = [float(x.replace(",", ".").replace("€","")) for x in row[COLUMNS_DATA:] ]
        elif i in ROWS_IGNORE:
            # Weight (ignore)
            continue
        elif i >= ROWS_DATA:
            name       = row[COLUMN_NAME]
            weight     = float(row[COLUMN_WEIGHT].replace(",","."))
            _          = row[COLUMN_TOTAL]
            quantities = [int(x) if x else 0 for x in row[COLUMNS_DATA:] ]
            choco_data.append({
                "name" : name,
                "weight" : weight,
                "quantities" : quantities
            })

""" CONVERT TO DICT """
chocolate_json = {
    "sessions" : [],
    "tablets" : []
}
for s,h,p in zip(sessions, headers, prices):
    entry = {
        "id" : s,
        "date" : h,
        "price" : p
    }
    chocolate_json["sessions"].append(entry)
for l in choco_data:
    entry = {
        "name" : l["name"],
        "weight" : l["weight"],
        "events" : []
    }
    for date, session, quantity in zip(headers, sessions, l["quantities"]):
        if quantity:
            entry["events"].append({"date" : date, "session" : session, "quantity" : quantity})
    chocolate_json["tablets"].append(entry)

""" Export to json """
with open("chocolate.json", "w", encoding="utf-8") as f:
    json.dump(chocolate_json, f, indent=2, ensure_ascii=False)
    
