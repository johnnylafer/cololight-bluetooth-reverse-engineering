# Cololight BLE Control Protocol - English Translation

🇩🇪 [Deutsche Version](COLOLIGHT_BLE_SPEC_DE.md)

## BLE UUID

**Cololight Custom UUID:** `91be3ad5-2c4a-4e82-8a1c-bae9c9116593`

---

## Characteristics

### Characteristic 1 (IDX1) - Power & Brightness Control

**UUID:** `b4d64c4f-c5a0-4a1b-afea-306b66269750`

**Properties:** Write, Read, Notify, Write-Without-Response

**Function:** Control and read device IO-P1

**Parameters:** `type(1 byte) + value(1 byte)`

**Commands:**
- **Power On/Off:**
  - Type: `0x80` (off) / `0x81` (on)
  - Value: `0` (off) / `1` (on)

- **Power + Brightness:**
  - Type: `0xce` (off with brightness) / `0xcf` (on with brightness)
  - Value: Brightness `0-255` (light brightness level)

---

### Characteristic 2 (IDX2) - Light Effects Control

**UUID:** `2edcf977-60ac-49b0-aa2a-ed75abd74ea3`

**Properties:** Write, Read, Notify, Write-Without-Response

**Function:** Control and read device IO-P2

**Parameters:** `type(1 byte) + value(4 bytes)`

**Commands:**
- **Power On/Off:**
  - Type: `0x80` (off) / `0x81` (on)
  - Value: `0` / `1`

- **Power + Set Effect:**
  - Type: `0xfe` (off with effect) / `0xff` (on with effect)
  - Value: `1 byte (mode) + 3 bytes (parameters)`
    - First byte: Mode type
    - Last 3 bytes: Parameters for that mode

---

## Mode & Parameter Definitions

### Mode 0x00 - Solid Color Mode

**Format:** `[0xff] [0x00] [RR] [GG] [BB]`

- **RR GG BB:** RGB color values (0x00-0xFF each)

**Example:** `0xff 0x00 0xff 0x00 0x00` = Solid Red

---

### Mode 0x01 - Overall Dynamic Mode

**Format:** `[0xff] [0x01] [AA] [BB] [CC]`

- **AA:** Dynamic effect index (see effect list below)
- **BB:** Change speed (0x00-0xFF, higher value = slower speed)
- **CC:** Variation mode (0x00-0x0F), default: 0x00

**Example:** `0xff 0x01 0x80 0x0a 0x00`
- Mode: 0x01 (dynamic)
- Effect: 0x80 (Red-Green-Blue breathing)
- Speed: 0x0a (default speed)
- Variation: 0x00 (default)

---

### Mode 0x03 - Special Overall Dynamic

**Format:** `[0xff] [0x03] [AA] [BB] [CD]`

- **AA:** Effect index (same as mode 0x01)
- **BB:** Change speed, typically 0x0a
- **C:** Variation mode (0-F)
- **D:** Color jump mode (0-F), default: 0

**Variation Modes (C):**
- `0x0` - Overall dynamic
- `0x1` - Outer circle to inner gradient
- `0x2` - Center point dynamic
- `0x3` - Inner circle overall dynamic
- `0x4` - Outer circle overall dynamic
- `0x5` - Both sides to center line gradient
- `0x6` - Diagonal to center line overall dynamic
- `0x7` - Diagonal center line both sides overall dynamic
- `0x8` - Diagonal outer two lines overall dynamic
- `0x9` - Top to bottom gradient dynamic
- `0xa` - Bottom side one line overall dynamic
- `0xb` - Horizontal center line bottom line overall dynamic
- `0xc` - Horizontal center line overall dynamic
- `0xd` - Horizontal center line top line overall dynamic
- `0xe` - Top side one line overall dynamic
- `0xf` - Flower shape overall dynamic

**Example:** `0xff 0x03 0xaf 0x0a 0x20`
- Mode: 0x03 (special overall)
- Effect: 0xaf (Friend gathering)
- Speed: 0x0a
- Variation: 0x2 (center point)
- Jump: 0x0 (default)

---

### Mode 0x04 - Special Individual Dynamic

**Format:** `[0xff] [0x04] [AA] [BB] [CD]`

- **AA:** Effect index (same as mode 0x01)
- **BB:** Change speed, typically 0x0a
- **C:** Variation mode (0-F)
- **D:** Color jump mode (0-F), default: 0

**Variation Modes (C):**
- `0x0` - Overall point dynamic
- `0x1` - Center point dynamic
- `0x2` - Inner circle point dynamic
- `0x3` - Outer circle point dynamic
- `0x4` - Two blocks as basis outer circle point dynamic
- `0x5` - Three blocks as basis outer circle point dynamic

---

### Mode 0x05 - Smooth Transition of Mode 0x03

Same parameters as Mode 0x03, but with smooth transitions between states.

---

### Mode 0x06 - Smooth Transition of Mode 0x04

Same parameters as Mode 0x04, but with smooth transitions between states.

---

## Effect Index List (AA Parameter for Mode 0x01)

### Breathing Effects

- `0x80` - Red-Green-Blue breathing
- `0x81` - Red-Orange-Yellow-Green-Cyan-Blue-Purple breathing (7-color)
- `0x82` - Green breathing
- `0x83` - Cyan breathing
- `0x84` - Blue breathing
- `0x85` - Purple breathing
- `0x86` - Red breathing
- `0x87` - Orange breathing
- `0x88` - Yellow breathing
- `0x89` - White breathing

### Gradient Effects

- `0x8a` - Red to Yellow gradient
- `0x8b` - Red to Green gradient
- `0x8d` - Red to Blue gradient
- `0x8e` - Green to Yellow gradient
- `0x8f` - Green to Cyan gradient
- `0x90` - Green to Blue gradient
- `0x91` - Blue to Cyan gradient
- `0x92` - Blue to Purple gradient
- `0x93` - Yellow to White gradient
- `0x94` - Red to White gradient
- `0x95` - Green to White gradient
- `0x96` - Cyan to White gradient
- `0x97` - Blue to White gradient
- `0x98` - Purple to White gradient

### Flash Effects

- `0x99` - Red-Green-Blue flash
- `0x9a` - 7-color flash
- `0x9b` - Green flash
- `0x9c` - Cyan flash
- `0x9d` - Blue flash
- `0x9e` - Purple flash
- `0x9f` - Red flash
- `0xa0` - Orange flash
- `0xa1` - Yellow flash
- `0xa2` - White flash

### Fast Flash Effects

- `0xa3` - Red-Green-Blue fast flash
- `0xa4` - 7-color fast flash
- `0xa5` - Green fast flash
- `0xa6` - Cyan fast flash
- `0xa7` - Blue fast flash
- `0xa8` - Purple fast flash
- `0xa9` - Red fast flash
- `0xaa` - Orange fast flash
- `0xab` - Yellow fast flash
- `0xac` - White fast flash

### Scene Effects (Party Mode - P)

- `0xad` - Birthday Party
- `0xae` - Girlfriend Gathering / Afternoon Tea
- `0xaf` - Friends Dining
- `0xb0` - Colleagues Dining
- `0xb1` - Family Dinner
- `0xb2` - Couple Date

### Mood Color Effects (P)

- `0xb3` - Mood Color - Red
- `0xb4` - Mood Color - Orange
- `0xb5` - Mood Color - Yellow
- `0xb6` - Mood Color - Green
- `0xb7` - Mood Color - Cyan
- `0xb8` - Mood Color - Sky Blue
- `0xb9` - Mood Color - Blue
- `0xba` - Mood Color - Pink
- `0xbb` - Mood Color - Gold
- `0xbc` - Mood Color - Colorful
- `0xbd` - Mood Color - Full Color

### Nature/Time Effects

- `0xbe` - Sunrise 0
- `0xbf` - Cloud Rise
- `0xc0` - Green Field
- `0xc1` - Sunrise
- `0xc2` - Starry Sky
- `0xc3` - Macaron
- `0xc4` - Blue-Green Breathing

---

## Protocol Notes

### Speed Parameter (BB)
- Range: `0x00` - `0xFF`
- Higher value = slower speed
- Default/Recommended: `0x0a`

### Variation Mode (CC or C)
- Range: `0x0` - `0xF`
- Controls the pattern of how the effect displays
- Default: `0x00`

### Color Jump Mode (D)
- Range: `0x0` - `0xF`
- Controls how colors transition
- Default: `0x0`

---

## Common Commands Summary

| Command | Type Byte | Mode | Parameters | Description |
|---------|-----------|------|------------|-------------|
| **Solid Color** | `0xff` | `0x00` | `[RR][GG][BB]` | Set RGB color |
| **Dynamic Effect** | `0xff` | `0x01` | `[AA][BB][CC]` | Set dynamic effect |
| **Special Overall** | `0xff` | `0x03` | `[AA][BB][CD]` | Advanced pattern control |
| **Special Individual** | `0xff` | `0x04` | `[AA][BB][CD]` | Individual LED control |
| **Smooth Overall** | `0xff` | `0x05` | `[AA][BB][CD]` | Mode 03 with smoothing |
| **Smooth Individual** | `0xff` | `0x06` | `[AA][BB][CD]` | Mode 04 with smoothing |
| **Power On** | `0x81` | - | `[0x01]` | Turn on |
| **Power Off** | `0x80` | - | `[0x00]` | Turn off |
| **Brightness** | `0xcf` | - | `[0-255]` | Set brightness (on) |

---

## Examples

### Example 1: Set Solid Red
```
Command: ff 00 ff 00 00
- Type: 0xff (on with effect)
- Mode: 0x00 (solid color)
- Red: 0xff (255)
- Green: 0x00 (0)
- Blue: 0x00 (0)
```

### Example 2: White Breathing Effect
```
Command: ff 01 89 0a 00
- Type: 0xff (on with effect)
- Mode: 0x01 (dynamic)
- Effect: 0x89 (white breathing)
- Speed: 0x0a (default)
- Variation: 0x00 (default)
```

### Example 3: Birthday Party with Center Point
```
Command: ff 03 ad 0a 20
- Type: 0xff (on with effect)
- Mode: 0x03 (special overall)
- Effect: 0xad (birthday party)
- Speed: 0x0a (default)
- Variation: 0x2 (center point)
- Jump: 0x0 (default)
```
