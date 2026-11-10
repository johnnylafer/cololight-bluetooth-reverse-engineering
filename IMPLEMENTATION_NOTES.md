# Cololight Mix ACID - Implementation Notes

## Project Overview

Home Assistant custom integration for controlling Cololight Mix ACID LED lights via Bluetooth Low Energy (BLE). Provides full control over all device features including RGB colors, 69 dynamic effects, speed control, variations, and smooth transitions.

**Current Version:** 1.1.1
**Repository:** https://github.com/johnnylafer/cololight-bluetooth-reverse-engineering
**Installation:** HACS compatible

---

## Technical Architecture

### BLE Protocol

The device uses a proprietary 5-byte protocol format:

```
[type_byte][mode][param1][param2][param3]
```

**Key Discovery:** The device internally reverses bytes 1-4 when storing state.
- We send: `[0xff][mode][p1][p2][p3]`
- Device stores: `[0xff][p3][p2][p1][mode]`
- Our code handles this transparently in `protocol.py`

### UUIDs

```python
SERVICE_UUID = "2edcf977-60ac-49b0-aa2a-ed75abd74ea3"
CHAR_STATE = "2edcf978-60ac-49b0-aa2a-ed75abd74ea3"    # Effects/scenes
CHAR_POWER = "2edcf979-60ac-49b0-aa2a-ed75abd74ea3"    # Power control
CHAR_BRIGHTNESS = "2edcf97a-60ac-49b0-aa2a-ed75abd74ea3"  # Brightness
```

---

## Protocol Modes

### Mode 0x00 - Solid RGB Color
```
Format: [0xff][0x00][RR][GG][BB]
Example: ff00ff0000 = Red
```

### Mode 0x01 - Overall Dynamic Effects
```
Format: [0xff][0x01][effect_index][speed][variation]
- effect_index: 0x80-0xc4 (69 effects)
- speed: 0x00-0xff (0=fastest, higher=slower)
- variation: 0x00-0x0f (16 patterns)

Example: ff01890a00 = White Breathing, normal speed
```

### Mode 0x03 - Special Overall Dynamic
```
Format: [0xff][0x03][effect_index][speed][cd_byte]
- cd_byte = (variation << 4) | color_jump
- More dramatic effect changes than mode 0x01
```

### Mode 0x04 - Special Individual Dynamic
```
Format: [0xff][0x04][effect_index][speed][cd_byte]
- Individual LED control with special patterns
- Used in original "Color Flow" scene
```

### Mode 0x05 - Smooth Overall Dynamic
```
Format: [0xff][0x05][effect_index][speed][cd_byte]
- Mode 0x03 with smooth transitions between states
- Gentler, more fluid effect changes
```

### Mode 0x06 - Smooth Individual Dynamic
```
Format: [0xff][0x06][effect_index][speed][cd_byte]
- Mode 0x04 with smooth transitions
- Used in most original working scenes (Cool Mist, Candy, etc.)
- Default mode for new effects in v1.1.1+
```

---

## Dynamic Effects (0x80-0xc4)

### Breathing Effects (0x80-0x89)
- RGB Breathing, 7-Color Breathing, Green/Red/Blue/Yellow/Pink/Cyan/White Breathing

### Gradient Effects (0x8a-0x93)
- RGB Gradient, 7-Color Gradient, etc.

### Jumping Effects (0x94-0x9d)
- RGB Jump, 7-Color Jump, various color jumping patterns

### Flash Effects (0x9e-0xa7)
- RGB Flash, 7-Color Flash, strobe effects

### Party Effects (0xa8-0xb1)
- Red/Green/Blue/Colorful/RGB Parties, Birthday Party, etc.

### Mood Effects (0xb2-0xbb)
- Couple Date, Relaxation, Cozy Reading, Nature Forest, etc.

### Nature Effects (0xbc-0xc4)
- Sunrise, Sunset, Whale Ocean, various nature-themed effects

**Full list in:** `custom_components/cololight_mix_acid/const.py`

---

## Home Assistant Entities

### Light Entity
**Entity ID:** `light.cololight_mix_acid`

**Features:**
- On/Off control
- RGB color picker
- Brightness slider (0-255)
- Built-in scenes (Color Flow, Cool Mist, Candy, Savannah, Deep Blue, Purple Haze)

**Implementation:** `light.py`

### Effect Select
**Entity ID:** `select.cololight_mix_acid_effect`

**Features:**
- Choose from 69 dynamic effects
- Uses smooth mode 0x06 by default
- Maintains current speed and variation

**Implementation:** `select.py` (CololightEffectSelect)

### Variation Select
**Entity ID:** `select.cololight_mix_acid_variation_mode`

**Features:**
- 16 variation patterns (0x0-0xF)
- Changes visual pattern within same effect
- Maintains current effect and speed

**Implementation:** `select.py` (CololightVariationSelect)

### Speed Number (Slider)
**Entity ID:** `number.cololight_mix_acid_effect_speed`

**Features:**
- Full 0-255 range control
- 0 = fastest, 255 = slowest
- Maintains current effect and mode
- Real-time speed adjustment

**Implementation:** `number.py`

### Smooth Transition Switch
**Entity ID:** `switch.cololight_mix_acid_smooth_transitions`

**Features:**
- Toggle between smooth (0x05/0x06) and sharp (0x03/0x04) transitions
- Converts current effect to appropriate mode
- Maintains effect, speed, and variation

**Implementation:** `switch.py`

---

## File Structure

```
custom_components/cololight_mix_acid/
├── __init__.py           # Integration setup, platform registration
├── manifest.json         # Integration metadata, dependencies
├── config_flow.py        # UI configuration flow
├── const.py             # Constants, effect definitions, scenes
├── protocol.py          # BLE protocol encoder/decoder
├── coordinator.py       # ActiveBluetoothDataUpdateCoordinator
├── light.py             # Main light entity
├── select.py            # Effect and variation selects
├── number.py            # Speed slider
└── switch.py            # Smooth transition toggle
```

---

## Key Implementation Details

### Coordinator Pattern
Uses `ActiveBluetoothDataUpdateCoordinator` from Home Assistant:
- Automatic BLE connection management
- Service caching with `bleak-retry-connector`
- State polling every 30 seconds
- Notification-based updates for state changes

### State Management
```python
# Coordinator tracks:
- _is_on: bool                    # Power state
- _brightness: int                # 0-255
- _rgb_color: tuple[int,int,int] # RGB values
- _current_scene: str | None     # Hex string of active scene
```

### Scene Restoration
Original working scenes use modes 0x04 and 0x06:
```python
BUILT_IN_SCENES = {
    "Color Flow": "ff04001801",   # Mode 0x04
    "Cool Mist": "ff06891800",    # Mode 0x06 (smooth)
    "Candy": "ff06991800",        # Mode 0x06 (smooth)
    "Savannah": "ff06ad1800",     # Mode 0x06 (smooth)
    "Deep Blue": "ff06841f30",    # Mode 0x06 (smooth)
    "Purple Haze": "ff06b21070",  # Mode 0x06 (smooth)
}
```

**Why these modes?**
- Mode 0x06 provides smoother, more pleasing transitions
- Original scenes were carefully tuned to these modes
- v1.1.0 broke these by switching to mode 0x01
- v1.1.1 restored original values

### Protocol Encoding
All encoding handled in `protocol.py`:
```python
def encode_smooth_individual(effect_index, speed=0x18, variation=0, color_jump=0):
    """Encode mode 0x06 command."""
    cd_byte = ((variation & 0x0F) << 4) | (color_jump & 0x0F)
    return bytes([0xFF, 0x06, effect_index & 0xFF, speed & 0xFF, cd_byte])
```

### State Decoding
Handles device's byte reversal:
```python
def decode_state(state_data: bytes) -> dict:
    """Un-reverse bytes 1-4 to get original format."""
    if len(state_data) < 5:
        return {}

    # Device stores reversed
    mode = state_data[4]
    param1 = state_data[3]
    param2 = state_data[2]
    param3 = state_data[1]

    # Decode based on mode...
    if mode == 0x00:  # Solid color
        return {'mode': mode, 'rgb': (param1, param2, param3)}
    elif mode in (0x01, 0x03, 0x04, 0x05, 0x06):  # Dynamic effects
        return {
            'mode': mode,
            'effect_index': param1,
            'speed': param2,
            'variation': (param3 >> 4) & 0x0F,
            'color_jump': param3 & 0x0F
        }
```

---

## Version History

### v1.1.1 (Latest)
**Bug Fixes:**
- Restored original working scene values (modes 0x04/0x06)
- Scenes now work exactly as before protocol update

**New Features:**
- Speed slider (0-255 range) replacing preset select
- Smooth transition toggle switch
- Effect/variation selects use mode 0x06 by default

**Technical:**
- Created `number.py` for speed control
- Created `switch.py` for smooth transitions
- Removed speed select entity
- Updated platforms to include NUMBER and SWITCH

### v1.1.0
**Major Update:**
- Implemented official BLE protocol from manufacturer
- Added all 69 dynamic effects
- Created proper protocol encoder/decoder
- Added variation mode control
- Expanded effect list with proper naming

**Issues:**
- Broke original scenes by switching to mode 0x01
- Speed control too limited (only 5 presets)
- Fixed in v1.1.1

### v1.0.11
**Fixes:**
- Scene hex values working with reversed byte order
- State updates properly trigger UI refresh

### v1.0.8-1.0.10
**Fixes:**
- Fixed state update issues using `async_update_listeners()`
- Improved BLE connection stability

---

## Development Notes

### Testing Protocol Changes
Always test on device before committing:
```python
# Test script pattern
import asyncio
from bleak import BleakClient

async def test():
    async with BleakClient(MAC) as client:
        # Send command
        await client.write_gatt_char(CHAR_STATE, bytes.fromhex("ff06891800"))

        # Read back
        data = await client.read_gatt_char(CHAR_STATE)
        print(f"Read: {data.hex()}")

asyncio.run(test())
```

### Byte Reversal Discovery
Key debugging that revealed the reversal pattern:
```
Sent: ff00ff0000 → Read: ff0000ff00 (bytes 1-4 reversed!)
Sent: ff0000ff00 → Read: ff00ff0000 (bytes 1-4 reversed!)
Sent: ff01890a00 → Read: ff000a8901 (bytes 1-4 reversed!)
```

This led to the `decode_state()` function properly handling the device's internal storage format.

### HACS Installation
Integration is compatible with HACS:
1. Add custom repository: `https://github.com/johnnylafer/cololight-bluetooth-reverse-engineering`
2. Search for "Cololight Mix ACID"
3. Install and restart Home Assistant
4. Add via Integrations → Cololight Mix ACID

### Dependencies
```json
{
  "dependencies": ["bluetooth_adapters"],
  "requirements": ["bleak>=0.21.0", "bleak-retry-connector>=3.5.0"]
}
```

---

## Common Issues & Solutions

### Scene Not Working
**Problem:** Scene appears active but looks wrong
**Solution:** Check that scene uses correct mode (0x04 or 0x06, not 0x01)

### Speed Control Not Responding
**Problem:** Speed slider changes don't affect effect
**Solution:** Ensure current effect supports speed (some effects ignore speed parameter)

### Smooth Transitions Not Visible
**Problem:** Smooth switch on but no difference
**Solution:** Difference is subtle; try with "Birthday Party" effect for clearest demo

### BLE Connection Drops
**Problem:** Device disconnects frequently
**Solution:** Check Bluetooth adapter proximity, consider ESP32 Bluetooth proxy

---

## Official Documentation

### BLE Specification
Translated from Chinese manufacturer documentation:
- Located: `COLOLIGHT_BLE_SPEC_ENGLISH.md`
- Original: Contact Cololight support for official spec

### Effect Names
All 69 effects named following manufacturer documentation with descriptive English names matching the Chinese originals.

---

## Future Improvements

### Potential Features
- Custom scene creation via UI
- Effect playlists/sequences
- Music sync (if device supports)
- Group control for multiple devices

### Known Limitations
- Cannot read device name via BLE (requires pairing)
- Some effects look similar with different variations
- Speed response varies by effect type
- No feedback on which variation/speed is "best" for each effect

---

## Credits

**Developer:** Johnny Lafer (@johnnylafer)
**Manufacturer:** Cololight (BLE specification support)
**Platform:** Home Assistant
**Libraries:** bleak, bleak-retry-connector

---

## License

See repository for license details.

Last Updated: 2026-01-12
