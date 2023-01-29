# Pictographer

Collection of scripts to help me organize my photo library with the help of Exiftool.

## Process overview

**Step 0:** Manually sanitize media files (photos/videos). This includes fixing the datetime and adding keywords, title, and GPS data.

**Step 1:** Run Exiftool to extract metadata from all the files into a CSV. Following tags are captured:

- SourceFile
- FileName
- DateTimeOriginal (For photos, format: yyyy:mm:dd hh:mm:ss)
- TrackCreateDate (For videos, format: yyyy:mm:dd hh:mm:ss)
- OffsetTimeOriginal
- XPKeywords (Keywords for photos)
- Category (Keywords for videos)
- Title
- GPSLatitude
- GPSLatitudeRef
- GPSLongitude
- GPSLongitudeRef

**Step 2:** Verify the data in the generated CSV. This includes:

- Ensuring DateTimeOriginal and TrackCreateDate are defined for all media.
- OffsetTimeOriginal is defined for all media. It's the UTC offset of the origin of photo. Format: +05:30
- XPKeywords are not missing. Sometimes only the Subject property is updated.
- Both GPSLatitude and GPSLongitude are defined for relevant files.
- GPSLatitudeRef and GPSLongitudeRef are defined if GPSLatitude and GPSLongitude are defined.

**Step 3:** Run the main script, `python src/main.py`. It renames the media files, moves them to the appropriate folder and generates a sanitized CSV with following metadata:

- FileName
- Location (Directory path of file relative to libaray root)
- Datetime (Format: yyyy-mm-dd hh:mm:ss)
- OffsetTimeOriginal
- Keywords (Format: kw1; kw2; kw3)
- Title
- GPSLatitude
- GPSLatitudeRef (N for non-negative latitude, else S)
- GPSLongitude
- GPSLongitudeRef (E for non-negative longitude, else W)

**Note about Datetime:** Value stored in DateTimeOriginal is localized to the timezone in which the photo was taken. However, TrackCreateDate is localized to UTC. So, for example, if a video was captured at `2023:01:16 06:00:00` in Asia/Kolkata timezone (+05:30), then TrackCreateDate will show `2023:01:16 00:30:00`. However, all values in Datetime field are localized to the timezone of origin.

## Media renaming format

Media files are divided into three categories, identified by their 3-character type tag:

- IMG: Image files
- VID: Video files
- EDT: Files with "Edit" in their keywords. These are typically files which are modified using an existing source media.

Media files are renamed in the following format: `TAG-YYYYMMDD-XXX.ext`

- `TAG` is one of the values mentioned above.
- `YYYYMMDD` is the date on which the media was captured.
- `XXX` is a 3 digit sequence number of the media, starting from `000`. Each tag has its own sequence count.
- `ext` is just the file extension.

# Libaray folder structure

```
Libarary root
    |
    | - Year
    |   | - Month
    |   |   | - Day
    |   |   |   | - Media file
    |
    | - 2023
    |   | - 01 - January
    |   |   | - 16
    |   |   |   | - EDT-20230116-000.png
    |   |   |   | - IMG-20230116-000.jpg
    |   |   |   | - VID-20230116-000.mp4
    |   |   | - 21 - Family Trip
    |   |   |   | - EDT-20230121-000.png
    |   |   |   | - IMG-20230121-000.jpg
    |   |   |   | - VID-20230121-000.mp4
```

Some of the keywords can be used as folder labels. In the example above, the directory `2023/01 - January/21 - Family Trip` contains at least one media file with keyword "Family Trip" which is marked as a folder label. If more than one folder label keywords are present within a folder, then a prirority system is used to pick one of them.

## Usage

Generate CSV for exif data:

```
.\scripts\export-exif.ps1 "path/to/library"
```

Organize library and generate metadata CSV:

```
python .\scr\main.py "path/to/library"
```
