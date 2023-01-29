import numpy as np
import pandas as pd
import pytz
from datetime import datetime, timedelta


# Given a datetime string and timezone, method adds timezone offset to datetime string
# Example:
#       Datetime: 2023:01:02 01:00:25
#       Timezone: Asia/Kolkata (+05:30)
#       Output:   2023:01:02 06:30:25
# Parameter
#   Dataframe row with following columns: TrackCreateDate, Timezone
def add_utc_offset(df_row):
    if pd.isnull(df_row["TrackCreateDate"]):
        return np.nan
    dt = datetime.strptime(df_row["TrackCreateDate"], "%Y:%m:%d %H:%M:%S")
    # Convert Timezone offset to timedelta
    # Offset formats: +05:30, 00:00, -04:00
    hrs, mins = map(int, df_row["OffsetTimeOriginal"].split(":"))
    if hrs < 0:
        # Offset is east of UCT, make mins negative
        mins = -mins
    td = timedelta(hours=hrs, minutes=mins)
    dt: datetime = dt + td
    return dt.strftime("%Y:%m:%d %H:%M:%S")


img_types = {".jpg", ".jpeg", ".png", ".heic", ".cr2", ".nef"}
vid_types = {".mp4", ".mkv", ".avi", ".mov", ".m4a"}
