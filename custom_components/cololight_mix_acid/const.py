"""Constants for the Cololight Mix ACID integration."""

DOMAIN = "cololight_mix_acid"

# BLE Characteristics
CHAR_STATE = "2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3"
CHAR_BRIGHTNESS = "B4D64C4F-C5A0-4A1B-AFEA-306B66269750"

# Protocol constants
DEFAULT_SPEED = 0x0A  # Default effect speed
DEFAULT_VARIATION = 0x00  # Default variation mode

# Effect definitions (following official Cololight BLE spec)
# Format: [0xff][mode][param1][param2][param3]
# Note: Device internally reverses bytes 1-4 when storing, but we send in official format

# All 69 official dynamic effects (for mode 0x01)
DYNAMIC_EFFECTS = {
    # Breathing Effects (0x80-0x89)
    "RGB Breathing": 0x80,
    "7-Color Breathing": 0x81,
    "Green Breathing": 0x82,
    "Cyan Breathing": 0x83,
    "Blue Breathing": 0x84,
    "Purple Breathing": 0x85,
    "Red Breathing": 0x86,
    "Orange Breathing": 0x87,
    "Yellow Breathing": 0x88,
    "White Breathing": 0x89,

    # Gradient Effects (0x8a-0x98)
    "Red-Yellow Gradient": 0x8A,
    "Red-Green Gradient": 0x8B,
    "Red-Blue Gradient": 0x8D,
    "Green-Yellow Gradient": 0x8E,
    "Green-Cyan Gradient": 0x8F,
    "Green-Blue Gradient": 0x90,
    "Blue-Cyan Gradient": 0x91,
    "Blue-Purple Gradient": 0x92,
    "Yellow-White Gradient": 0x93,
    "Red-White Gradient": 0x94,
    "Green-White Gradient": 0x95,
    "Cyan-White Gradient": 0x96,
    "Blue-White Gradient": 0x97,
    "Purple-White Gradient": 0x98,

    # Flash Effects (0x99-0xa2)
    "RGB Flash": 0x99,
    "7-Color Flash": 0x9A,
    "Green Flash": 0x9B,
    "Cyan Flash": 0x9C,
    "Blue Flash": 0x9D,
    "Purple Flash": 0x9E,
    "Red Flash": 0x9F,
    "Orange Flash": 0xA0,
    "Yellow Flash": 0xA1,
    "White Flash": 0xA2,

    # Fast Flash Effects (0xa3-0xac)
    "RGB Fast Flash": 0xA3,
    "7-Color Fast Flash": 0xA4,
    "Green Fast Flash": 0xA5,
    "Cyan Fast Flash": 0xA6,
    "Blue Fast Flash": 0xA7,
    "Purple Fast Flash": 0xA8,
    "Red Fast Flash": 0xA9,
    "Orange Fast Flash": 0xAA,
    "Yellow Fast Flash": 0xAB,
    "White Fast Flash": 0xAC,

    # Party Scene Effects (0xad-0xb2)
    "Birthday Party": 0xAD,
    "Afternoon Tea": 0xAE,
    "Friends Dining": 0xAF,
    "Colleagues Dining": 0xB0,
    "Family Dinner": 0xB1,
    "Couple Date": 0xB2,

    # Mood Color Effects (0xb3-0xbd)
    "Mood Red": 0xB3,
    "Mood Orange": 0xB4,
    "Mood Yellow": 0xB5,
    "Mood Green": 0xB6,
    "Mood Cyan": 0xB7,
    "Mood Sky Blue": 0xB8,
    "Mood Blue": 0xB9,
    "Mood Pink": 0xBA,
    "Mood Gold": 0xBB,
    "Mood Colorful": 0xBC,
    "Mood Full Color": 0xBD,

    # Nature/Time Effects (0xbe-0xc4)
    "Sunrise Dawn": 0xBE,
    "Cloud Rise": 0xBF,
    "Green Field": 0xC0,
    "Sunrise": 0xC1,
    "Starry Sky": 0xC2,
    "Macaron": 0xC3,
    "Blue-Green Breathing": 0xC4,
}

# Variation modes for mode 0x03 (Special Overall Dynamic)
VARIATION_MODES_03 = {
    "Overall Dynamic": 0x0,
    "Outer to Inner Gradient": 0x1,
    "Center Point Dynamic": 0x2,
    "Inner Circle Dynamic": 0x3,
    "Outer Circle Dynamic": 0x4,
    "Sides to Center Gradient": 0x5,
    "Diagonal Center Line": 0x6,
    "Diagonal Center Sides": 0x7,
    "Diagonal Outer Lines": 0x8,
    "Top to Bottom Gradient": 0x9,
    "Bottom Line": 0xA,
    "Horizontal Center Bottom": 0xB,
    "Horizontal Center": 0xC,
    "Horizontal Center Top": 0xD,
    "Top Line": 0xE,
    "Flower Shape": 0xF,
}

# Variation modes for mode 0x04 (Special Individual Dynamic)
VARIATION_MODES_04 = {
    "Overall Point": 0x0,
    "Center Point": 0x1,
    "Inner Circle Point": 0x2,
    "Outer Circle Point": 0x3,
    "Two Block Outer": 0x4,
    "Three Block Outer": 0x5,
}

# Quick access scenes (using mode 0x01 with default settings)
BUILT_IN_SCENES = {
    "Color Flow": "ff01180004",  # Effect 0x18 with mode 0x01, speed 0x00, variation 0x04
    "Cool Mist": "ff01890a00",   # White Breathing
    "Candy": "ff01990a00",       # RGB Flash
    "Savannah": "ff01ad0a00",    # Birthday Party
    "Deep Blue": "ff01841f30",   # Blue Breathing, slower
    "Purple Haze": "ff01b21070", # Couple Date
}

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_CUSTOM_SCENES = "custom_scenes"

# Defaults
DEFAULT_NAME = "Cololight Mix ACID"
