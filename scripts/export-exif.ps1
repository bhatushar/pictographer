# Requires 1 command-line argument: Path to the directory containing the media

# DateTimeOriginal is the date on which the photo was taken
# TrackCreateDate is the date on which the video was recorded, it excludes the timezone
# XpKeywords are photo tags (Separated by semi-colon)
# Category are video tags (Separated by comma)

.\exiftool.exe -n -r -FileName -DateTimeOriginal -TrackCreateDate -XpKeywords -Category -Title -GPSLatitude -GPSLatitudeRef -GPSLongitude -GPSLongitudeRef -csv > metadata_raw.csv "$($args[0])"
