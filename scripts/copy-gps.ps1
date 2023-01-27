# Requries at least 2 arguments: First is the source path, rest are destination paths

# Load env variables
Get-Content .env | ForEach-Object {
    $key, $value = $_.split("=")
    Set-Content Env:\$key $value
}

$src, $targets = $args
# Don't use -GPS:All because that will copy GPS Datetime as well and it might clash is the original datetime of the targets
& $Env:Exiftool_Path -TagsFromFile $src -GPSLatitude -GPSLatitudeRef -GPSLongitude -GPSLongitudeRef -GPSAltitude -GPSAltitudeRef -Overwrite_Original $targets
