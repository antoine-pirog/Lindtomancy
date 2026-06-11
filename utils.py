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

def get_sessionid(obj):
    date_ddmmyyyy = obj['date']
    date_yyyymmdd = datetime.strptime(date_ddmmyyyy, '%d/%m/%Y').strftime("%Y-%m-%d")
    session = obj.get('session') or obj.get("id")
    return f"{date_yyyymmdd} ({session})"

def build_chocodataframe(objdata):
    """ Build dataframe for tablets found in every purchase event """
    # Build table rows & columns
    rows = set()
    columns = set()
    for tablet in objdata["tablets"]:
        rows.add(tablet["name"])
        for event in tablet["events"]:
            columns.add(get_sessionid(event))
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
            column_name = get_sessionid(event)
            tabular_data[column_name][-1] = event["quantity"]

    # Create dataframe
    df = pd.DataFrame(tabular_data).set_index("Tablet")

    return df

def build_identitydataframe(objdata):
    """ Build dataframe for tablet identity (name, retail price, weight) """
    tabular_data = {
        "Tablet" : [],
        "Retail (€)" : [],
        "Weight (g)" : []
    }
    for tablet in objdata["tablets"]:
        tabular_data["Tablet"].append(tablet["name"])
        tabular_data["Retail (€)"].append(tablet["retail"])
        tabular_data["Weight (g)"].append(tablet["weight"]*1e3)
    return pd.DataFrame(tabular_data).set_index("Tablet")

def build_eventdataframe(objdata):
    """ Build dataframe summarizing all purchase events (date, sessionid, price) """
    tabular_data = {
        "id" : [],
        "Date" : [],
        "Session" : [],
        "Price (€)" : [],
        "Weight (g)" : []
    }
    # Populate sessions
    for session in objdata["sessions"]:
        sessionid = get_sessionid(session)
        if sessionid not in tabular_data["id"]:
            tabular_data["id"].append(sessionid)
            tabular_data["Date"].append(session["date"])
            tabular_data["Session"].append(session["id"])
            tabular_data["Price (€)"].append(session["price"])
            tabular_data["Weight (g)"].append(0)
            
    # Accumulate weight
    for tablet in objdata["tablets"]:
        for event in tablet["events"]:
            sessionid = get_sessionid(event)
            idx = tabular_data["id"].index(sessionid)
            tabular_data["Weight (g)"][idx] += tablet["weight"] * event["quantity"]

    return pd.DataFrame(tabular_data).set_index("id")
                