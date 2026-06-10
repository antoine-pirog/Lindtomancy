import json
import pandas as pd
from datetime import datetime

def load_chocodata(data_path):
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)

def get_session_by_id(objdata, id):
    for session in objdata["sessions"]:
        if session["id"] == id:
            return session
    return {}

def get_column_name(event):
    date_ddmmyyyy = event['date']
    date_yyyymmdd = datetime.strptime(date_ddmmyyyy, '%d/%m/%Y').strftime("%Y-%m-%d")
    session = event['session']
    return f"{date_yyyymmdd} ({session})"

def build_chocodataframe(objdata):
    # Build table rows & columns
    rows = set()
    columns = set()
    for tablet in objdata["tablets"]:
        rows.add(tablet["name"])
        for event in tablet["events"]:
            columns.add(get_column_name(event))
    rows = sorted(list(rows))
    columns = sorted(list(columns))
            
    # Create table skeleton
    tabular_data = {
        "Tablet" : [],
        **{column_name : [] for column_name in columns}
    }
    
    # Populate table
    for tablet in objdata["tablets"]:
        tabular_data["Tablet"].append(tablet["name"])
        for column_name in columns:
            tabular_data[column_name].append(0)
        for event in tablet["events"]:
            column_name = get_column_name(event)
            tabular_data[column_name][-1] = event["quantity"]

    # Create dataframe
    df = pd.DataFrame(tabular_data).set_index("Tablet")

    return df