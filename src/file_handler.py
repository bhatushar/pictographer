import helpers
import math
import os
import numpy as np
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
    sequence = f"{row['Sequence']:03}"
    extension = row['FileName'].rsplit('.', 1)[1]
    return f"{row['MediaType']}-{row['Date']}-{sequence}.{extension}"


def _gen_new_filenames(df: pd.DataFrame) -> pd.DataFrame:
    """Returns dataframe with 'NewFileName' column"""
    df["MediaType"] = df.apply(_media_type, axis=1)     # EDT, IMG or VID
    df["Date"] = df["Datetime"].dt.strftime("%Y%m%d")   # YYYYMMDD
    # Split dataframe on media type and date, generate new names for each group, and combine all groups
    df_groups: list[pd.DataFrame] = []
    for _, sub_df in df.groupby(["MediaType", "Date"]):
        sub_df["Sequence"] = np.arange(len(sub_df.index))
        sub_df["NewFileName"] = sub_df.apply(_filename, axis=1)
        df_groups.append(sub_df)
    updated_metadata = pd.concat(df_groups).sort_index()
    # Remove additionally created columns
    return updated_metadata.drop(["MediaType", "Date", "Sequence"], axis=1)


def rename(metadata: pd.DataFrame, lib_root: str):
    """Rename files in disk as per TAG-YYYYMMDD-XXX format and update the metadata accordingly"""
    local_df = metadata
    local_df = _gen_new_filenames(local_df)
    print("Renaming files:")
    for _, (old_name, new_name, location) in local_df[["FileName", "NewFileName", "Location"]].iterrows():
        old_path = os.path.join(lib_root, location, old_name)
        new_path = os.path.join(lib_root, location, new_name)
        os.rename(old_path, new_path)
        print(old_path, "->", new_path)
    print()
    metadata["FileName"] = local_df["NewFileName"]


##################################################################################################################


def _location_with_label(metadata: pd.DataFrame, folder_labels: list[str]) -> pd.Series:
    """Return list of directories following the library structure including folder labels"""
    df_groups = []
    # Split dataframe by date on which media was created
    date_groups = metadata.groupby(lambda index: metadata["Datetime"].loc[index].strftime("%Y/%m - %B/%d"))
    for group_id, sub_df in date_groups:
        folder_label = None
        label_priority = math.inf
        # Check all keywords present under a particular Day
        # Record the folder label with highest priority
        # Priority is determined by label's index in "folder_labels" (0 being highest)
        keywords = "; ".join(sub_df["Keywords"])
        for keyword in set(keywords.split("; ")):
            if keyword in folder_labels and folder_labels.index(keyword) < label_priority:
                folder_label = keyword
                label_priority = folder_labels.index(keyword)
        # group_id is of the "format 2023/01 - January/16"
        new_location = f"{group_id} - {folder_label}" if folder_label else group_id
        sub_df["NewLocation"] = new_location
        df_groups.append(sub_df)
    # Combine groups into whole with "NewLocation" column, sorted on original order
    metadata = pd.concat(df_groups).sort_index()
    return metadata["NewLocation"]


def _remove_empty_dirs(root_dir: str):
    """Recursively delete empty directories under root_dir, including root_dir"""
    for dirpath, _, _ in os.walk(root_dir, topdown=False):
        try:
            os.rmdir(dirpath)
            print("Deleting empty directory:", dirpath)
        except OSError:
            # Directory is not empty, do nothing
            pass
    print()


def move(metadata: pd.DataFrame, lib_root: str, folder_labels: list[str]):
    metadata["NewLocation"] = _location_with_label(metadata, folder_labels)
    print("Creating directories:")
    print(*metadata["NewLocation"].unique(), sep="\n")
    print()  # Just an empty line, keep moving :D
    print("Moving files:")
    for _, row in metadata.iterrows():
        old_path = os.path.join(lib_root, row["Location"], row["FileName"])
        new_path = os.path.join(lib_root, row["NewLocation"], row["FileName"])
        os.renames(old_path, new_path)
        print(old_path, "->", new_path)
    print()
    metadata.drop("NewLocation", axis=1, inplace=True)
    # Remove old directories
    _remove_empty_dirs(lib_root)
