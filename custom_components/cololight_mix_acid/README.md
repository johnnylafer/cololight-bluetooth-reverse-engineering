# Cololight Mix ACID - Home Assistant Integration

Home Assistant custom integration for the **Cololight Mix ACID** Bluetooth RGB light.

## Features

✅ **Full RGB Color Control** - Set any RGB color
✅ **Brightness Control** - 0-100% brightness adjustment
✅ **Built-in Scenes** - 6 pre-programmed animated scenes
✅ **Custom Scenes** - Add your own scenes via hex values
✅ **Bluetooth BLE** - Direct local control, no cloud required
✅ **Config Flow** - Easy setup via Home Assistant UI

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Search for "Cololight Mix ACID" in HACS
3. Click "Download"
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/cololight_mix_acid` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant

## Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Cololight Mix ACID"
4. Select your device from the list (or enter MAC address manually)
5. Click **Submit**

Your Cololight will appear as a light entity!

## Usage

### Basic Light Control

```yaml
# Turn on with color
service: light.turn_on
target:
  entity_id: light.cololight_mix_acid
data:
  rgb_color: [255, 0, 0]  # Red
  brightness: 200

# Turn off
service: light.turn_off
target:
  entity_id: light.cololight_mix_acid
```

### Built-in Scenes

The integration includes 6 built-in animated scenes:

- **Sunrise** - Warm sunrise colors
- **Sunset** - Sunset orange/red hues
- **Jungle** - Green nature theme
- **Ocean** - Blue water theme
- **Cool Mist** - Cyan/blue mist effect
- **Snow Mountain** - Cool white/blue

```yaml
# Activate a scene
service: light.turn_on
target:
  entity_id: light.cololight_mix_acid
data:
  effect: "Cool Mist"
```

### Custom Scenes

You can add custom scenes via the integration options:

1. Go to **Settings** → **Devices & Services**
2. Find **Cololight Mix ACID** and click **Configure**
3. Add custom scenes in this format:

```
My Custom Scene:ff06891800
Another Scene:ff01800900
Party Mode:ff301f8005
```

**Format**: `SceneName:WRITE_HEX_VALUE`
- Scene name can be anything
- Hex value must be 10 characters (WRITE format)
- One scene per line

After adding custom scenes, they'll appear in the effect list!

### Finding Custom Scene Hex Values

To get hex values for custom scenes:

1. Set up the scene you want in the Cololight app
2. Use the BLE monitoring scripts from the reverse engineering repository
3. Read the STATE characteristic and note the 5-byte hex value
4. Convert from READ format to WRITE format (reverse bytes 1-4)

**Example**:
- READ format: `ff00188906` (Cool Mist)
- WRITE format: `ff06891800` (bytes 1-4 reversed)

See the [reverse engineering documentation](../../cololight_reverse_engineering/CUSTOM_SCENE_EFFECT_PATTERNS.md) for details.

## Protocol Details

This integration uses the reverse-engineered BLE protocol:

- **STATE Characteristic**: `2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3`
  - Controls RGB colors and scenes
  - 5-byte format with READ/WRITE byte order differences

- **BRIGHTNESS Characteristic**: `B4D64C4F-C5A0-4A1B-AFEA-306B66269750`
  - Controls brightness for all modes
  - 2-byte format: `[0xCF] [Brightness_0-100]`

For complete protocol documentation, see the [reverse engineering folder](../../cololight_reverse_engineering/).

## Troubleshooting

### Device Not Found

- Ensure Bluetooth is enabled on your Home Assistant host
- Make sure the Cololight is powered on and nearby
- Try restarting the Cololight by power cycling it

### Connection Issues

- The device may only support one connection at a time
- Close the Cololight mobile app before using the integration
- Check Home Assistant logs for detailed error messages

### Custom Scenes Not Working

- Verify hex values are exactly 10 characters
- Ensure you're using WRITE format, not READ format
- Check that the scene works in the Cololight app first

## Development

This integration was developed through extensive reverse engineering of the Cololight Mix ACID BLE protocol. See the [reverse engineering documentation](../../cololight_reverse_engineering/) for:

- Complete protocol specification
- Test scripts and tools
- Discovery process documentation
- Scene and color mode tables

## Credits

Developed by johnny through BLE protocol reverse engineering.

## License

MIT License
