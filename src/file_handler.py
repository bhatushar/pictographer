import helpers
import os
import pandas as pd


def _media_type(row: pd.Series) -> str:
    """Returns tag of the media type"""
    if "Edit" in row["Keywords"].split("; "):
        # Edit has higer priority over image and video
        return "EDT"
    elif row["FileName"].endswith(tuple(helpers.img_types)):
        return "IMG"
    else:
        return "VID"


def _filename(row: pd.Series) -> str:
    sequence = f"{row.name:03}"
    extension = row['FileName'].rsplit('.', 1)[1]
    return f"{row['MediaType']}-{row['Date']}-{sequence}.{extension}"


def _gen_new_filenames(df: pd.DataFrame) -> pd.DataFrame:
    """Returns dataframe with 'NewFileName' column"""
    df["MediaType"] = df.apply(_media_type, axis=1)     # EDT, IMG or VID
    df["Date"] = df["Datetime"].dt.strftime("%Y%m%d")   # YYYYMMDD
    # Split dataframe on media type and date, generate new names for each group, and combine all groups
    df_groups: list[pd.DataFrame] = []
    for _, sub_df in df.groupby(["MediaType", "Date"]):
        sub_df = sub_df.reset_index(drop=True)
        sub_df["NewFileName"] = sub_df.apply(_filename, axis=1)
        df_groups.append(sub_df)
    updated_metadata = pd.concat(df_groups, ignore_index=True)
    # Remove additionally created columns
    return updated_metadata.drop(["MediaType", "Date"], axis=1)


def rename(metadata: pd.DataFrame, lib_root: str):
    """Rename files in disk as per TAG-YYYYMMDD-XXX format and update the metadata accordingly"""
    # If two files have same datetime, sequence is maintained based on filename
    df = metadata.sort_values(by=["FileName"])
    df = _gen_new_filenames(df)
    print("Renaming files:")
    for _, (old_name, new_name, location) in df[["FileName", "NewFileName", "Location"]].iterrows():
        old_path = os.path.join(lib_root, location, old_name)
        new_path = os.path.join(lib_root, location, new_name)
        os.rename(old_path, new_path)
        print(old_path, "->", new_path)
    print()
    metadata["FileName"] = df["NewFileName"]
