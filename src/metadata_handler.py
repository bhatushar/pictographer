import helpers
import numpy as np
import os
import pandas as pd


def _extract_keywords(df: pd.DataFrame) -> pd.Series:
    """Combine XPKeywords and Category into a semi-colon separated format"""
    keywords = df["XPKeywords"].fillna(df["Category"])
    # Change Keywords to "k1; k2; k3" from input "k1;k2;k3" or "k1, k2, k3"
    # Some keywords may already have a space after ;, leave them unchanged
    keywords = keywords.str.replace(r";([^\s])", r"; \1", regex=True)
    keywords = keywords.str.replace(",", ";")
    return keywords


def _extract_datetime(df: pd.DataFrame) -> pd.Series:
    """Combine DateTimeOriginal and TrackCreateDate, localized to origin timezone"""
    # Video datetime is localized to UTC. Convert it to TZ of origin
    df["TrackCreateDate"] = df.apply(helpers.add_utc_offset, axis=1)
    # Merge the two datetime columns
    datetime_series = df["DateTimeOriginal"].fillna(df["TrackCreateDate"])
    datetime_series = pd.to_datetime(datetime_series, format="%Y:%m:%d %H:%M:%S")
    return datetime_series


def _extract_gpsref(df: pd.DataFrame, coordinate_field: str, pos_ref: str, neg_ref: str) -> pd.Series:
    """Compute GPS coordinate reference N/S or E/W if coordinate is defined"""
    return np.where(
        df[coordinate_field].isnull(),
        None,
        np.where(df[coordinate_field] >= 0, pos_ref, neg_ref)
    )


def check_unkown_files(md_csv_path: str) -> list[str]:
    """Returns list of files with extensions that are not recognized as image or video"""
    md = pd.read_csv(md_csv_path)
    media_types = tuple(helpers.img_types | helpers.vid_types)
    known_file_filter = md["SourceFile"].str.endswith(media_types)
    unknown_files = md.loc[~known_file_filter, "SourceFile"]
    return unknown_files.to_list()


def sanitized_df(md_csv_path: str, library_root: str) -> pd.DataFrame:
    """Copy data from raw csv file into a formatted dataframe"""
    raw_md = pd.read_csv(md_csv_path)
    md = pd.DataFrame(
        columns=[
            "FileName",
            "Location",
            "Datetime",
            "OffsetTimeOriginal",
            "Keywords",
            "Title",
            "GPSLatitude",
            "GPSLatitudeRef",
            "GPSLongitude",
            "GPSLongitudeRef",
    ])

    # Depending of the media, following columns may not be present
    # Add empty columns
    optional_cols = [
        "DateTimeOriginal", # Only videos in media
        "TrackCreateDate",  # Only images in media
        "XPKeywords",       # No keywords or only videos
        "Category",         # No keywords or only images
        "Title",            # No title in any media
    ]
    for col in optional_cols:
        if col not in raw_md.columns:
            raw_md[col] = np.nan


    # Copy columns
    for field in ["FileName", "Title", "OffsetTimeOriginal", "GPSLatitude", "GPSLongitude"]:
        md[field] = raw_md[field]
    # Copy file location after removing library root prefix and filename
    md["Location"] = raw_md["SourceFile"].apply(lambda full_path: os.path.relpath(full_path, library_root))
    md["Location"] = md["Location"].apply(lambda filepath: os.path.dirname(filepath))
    # Copy formatted fields
    md["Keywords"] = _extract_keywords(raw_md)
    md["Datetime"] = _extract_datetime(raw_md)
    md["GPSLatitudeRef"] = _extract_gpsref(raw_md, "GPSLatitude", "N", "S")
    md["GPSLongitudeRef"] = _extract_gpsref(raw_md, "GPSLongitude", "E", "W")

    # Maintain relative order of files by datetime
    return md.sort_values(by="Datetime", ignore_index=True)
