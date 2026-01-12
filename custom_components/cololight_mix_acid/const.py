"""Constants for the Cololight Mix ACID integration."""

DOMAIN = "cololight_mix_acid"

# BLE Characteristics
CHAR_STATE = "2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3"
CHAR_BRIGHTNESS = "B4D64C4F-C5A0-4A1B-AFEA-306B66269750"

# Built-in scenes (effect name -> hex value to write/read)
BUILT_IN_SCENES = {
    "Cool Mist": "ff00188906",
    "Candy": "ff00189906",
    "Savannah": "ff0018ad06",
    "Deep Blue": "ff301f8406",
    "Purple Haze": "ff7010b206",
}

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_CUSTOM_SCENES = "custom_scenes"

# Defaults
DEFAULT_NAME = "Cololight Mix ACID"
