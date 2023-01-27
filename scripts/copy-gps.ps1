# Requries at least 2 arguments: First is the source path, rest are destination paths

$src, $targets = $args
# Don't use -GPS:All because that will copy GPS Datetime as well and it might clash is the original datetime of the targets
.\exiftool.exe -TagsFromFile $src -GPSLatitude -GPSLatitudeRef -GPSLongitude -GPSLongitudeRef -GPSAltitude -GPSAltitudeRef -Overwrite_Original $targets
