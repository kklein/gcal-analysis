import pandas as pd

def get_dataframe(events):
    d = {
        "date": map(lambda event: event["start"]["dateTime"], events),
        "distance": map(lambda event: event["description"].split("km")[0], events),
    }
    df = pd.DataFrame(data=d)
    df["date"] = df["date"].str[:10]
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.isocalendar().week
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["distance"] = pd.to_numeric(df["distance"])
    return df
