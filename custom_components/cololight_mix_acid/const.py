"""Constants for the Cololight Mix ACID integration."""

DOMAIN = "cololight_mix_acid"

# BLE Characteristics
CHAR_STATE = "2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3"
CHAR_BRIGHTNESS = "B4D64C4F-C5A0-4A1B-AFEA-306B66269750"

# Built-in scenes (effect name -> hex value to write)
# Note: Device stores these with bytes 1-4 reversed internally
BUILT_IN_SCENES = {
    "Color Flow": "ff04001801",
    "Cool Mist": "ff06891800",
    "Candy": "ff06991800",
    "Savannah": "ff06ad1800",
    "Deep Blue": "ff06841f30",
    "Purple Haze": "ff06b21070",
}

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_CUSTOM_SCENES = "custom_scenes"

# Defaults
DEFAULT_NAME = "Cololight Mix ACID"
