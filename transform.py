import pandas as pd


def get_dataframe(events):
    d = {
        "date_string": map(lambda event: event["start"]["dateTime"], events),
        "distance": map(
            lambda event: event.get("description", "").split("km")[0], events
        ),
    }
    df = pd.DataFrame(data=d)
    df["date"] = pd.to_datetime(df["date_string"].str[:16])
    df["week"] = df["date"].dt.isocalendar().week
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["distance"] = pd.to_numeric(df["distance"])
    df["hour"] = df["date"].dt.hour
    return df
