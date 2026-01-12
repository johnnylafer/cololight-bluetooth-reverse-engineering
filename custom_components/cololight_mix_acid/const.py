"""Constants for the Cololight Mix ACID integration."""

DOMAIN = "cololight_mix_acid"

# BLE Characteristics
CHAR_STATE = "2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3"
CHAR_BRIGHTNESS = "B4D64C4F-C5A0-4A1B-AFEA-306B66269750"

# Built-in scenes (effect name -> hex value to write)
BUILT_IN_SCENES = {
    "Sunrise": "ff01800900",
    "Sunset": "ff02800902",
    "Jungle": "ff03800a03",
    "Ocean": "ff04001801",
    "Cool Mist": "ff06891800",
    "Snow Mountain": "ff07800504",
}

# Reverse mapping for reading
SCENE_READ_TO_NAME = {
    "ff00098001": "Sunrise",
    "ff02090280": "Sunset",
    "ff030a0a80": "Jungle",
    "ff01180004": "Ocean",
    "ff00188906": "Cool Mist",
    "ff04050580": "Snow Mountain",
}

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_CUSTOM_SCENES = "custom_scenes"

# Defaults
DEFAULT_NAME = "Cololight Mix ACID"
