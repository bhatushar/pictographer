# Requires 1 command-line argument: Path to the directory containing the media

# Load env variables
Get-Content .env | ForEach-Object {
    $key, $value = $_.split("=")
    Set-Content Env:\$key $value
}

# DateTimeOriginal is the date on which the photo was taken
# TrackCreateDate is the date on which the video was recorded, it excludes the timezone
# XpKeywords are photo tags (Separated by semi-colon)
# Category are video tags (Separated by comma)

& $Env:Exiftool_Path -n -r -csv > $Env:Raw_Metadata_Path -FileName -DateTimeOriginal -TrackCreateDate -OffsetTimeOriginal -XpKeywords -Category -Title -GPSLatitude -GPSLatitudeRef -GPSLongitude -GPSLongitudeRef "$($args[0])"
