# Cololight Mix ACID for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/johnnylafer/ha-cololight-mix-acid.svg)](https://github.com/johnnylafer/ha-cololight-mix-acid/releases)
[![License](https://img.shields.io/github/license/johnnylafer/ha-cololight-mix-acid.svg)](LICENSE)

Home Assistant custom integration for the **Cololight Mix ACID** Bluetooth LED light strip.

This integration provides full local control of your Cololight Mix ACID device through Bluetooth, including RGB colors, brightness control, and animated scene effects.

## Background

The Cololight Mix ACID has no official API and no published BLE protocol - Cololight only ships a
mobile app that talks to the device directly. Everything this integration does (colors, brightness,
scenes) was recovered by sniffing and testing the device's own Bluetooth characteristics from
scratch: scanning the GATT services, writing test bytes to each writable characteristic, and
watching how the physical light reacted. The full protocol - every characteristic, byte format and
effect code found this way - is written up in [COLOLIGHT_BLE_SPEC_ENGLISH.md](COLOLIGHT_BLE_SPEC_ENGLISH.md)
(🇩🇪 [German version](COLOLIGHT_BLE_SPEC_DE.md)), with the debugging story in
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md).

## Features

- **Full RGB Color Control** - Set any color (0-255 per channel)
- **Brightness Control** - Adjust brightness from 0-100% in both RGB and scene modes
- **Power Control** - Turn lights on/off
- **6 Built-in Animated Scenes**:
  - Sunrise
  - Sunset
  - Jungle
  - Ocean
  - Cool Mist
  - Snow Mountain
- **Custom Scenes** - Add unlimited custom scenes via hex values through the UI
- **Bluetooth Auto-discovery** - Automatically finds "MIX Acid" devices
- **Config Flow** - Easy setup through Home Assistant UI (no YAML needed)

## Requirements

- Home Assistant 2024.1.0 or newer
- Bluetooth adapter on your Home Assistant server
- Cololight Mix ACID device

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add the repository URL: `https://github.com/johnnylafer/ha-cololight-mix-acid`
5. Select category: "Integration"
6. Click "Add"
7. Find "Cololight Mix ACID" in HACS and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/johnnylafer/ha-cololight-mix-acid/releases)
2. Extract the `cololight_mix_acid` folder from the archive
3. Copy the `cololight_mix_acid` folder to your `custom_components` directory:
   ```
   <config_directory>/custom_components/cololight_mix_acid/
   ```
4. Restart Home Assistant

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Cololight Mix ACID**
4. Select your device from the discovered devices list (or enter MAC address manually)
5. Give your device a name
6. Click **Submit**

Your Cololight Mix ACID light will now appear as a light entity in Home Assistant!

### Adding Custom Scenes

You can add custom scene effects via the integration's options:

1. Go to **Settings** → **Devices & Services**
2. Find your Cololight Mix ACID integration
3. Click **Configure**
4. Add custom scenes in the format:
   ```
   SceneName:ff06891800
   MyCustomScene:ff01800900
   ```
   - One scene per line
   - Format: `Name:HexValue`
   - Hex values must be exactly 10 characters

## Usage Examples

### Automations

Turn on with a specific color at sunset:

```yaml
automation:
  - alias: "Sunset Lights"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.cololight_mix_acid
        data:
          rgb_color: [255, 100, 50]
          brightness: 200
```

Activate a scene when motion is detected:

```yaml
automation:
  - alias: "Motion Scene"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.cololight_mix_acid
        data:
          effect: "Ocean"
```

### Scripts

Cycle through colors:

```yaml
script:
  color_cycle:
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.cololight_mix_acid
        data:
          rgb_color: [255, 0, 0]
      - delay: "00:00:02"
      - service: light.turn_on
        target:
          entity_id: light.cololight_mix_acid
        data:
          rgb_color: [0, 255, 0]
      - delay: "00:00:02"
      - service: light.turn_on
        target:
          entity_id: light.cololight_mix_acid
        data:
          rgb_color: [0, 0, 255]
```

## Technical Details

### Protocol Discovery

This integration was developed through reverse engineering of the Cololight Mix ACID Bluetooth protocol. Key characteristics:

- **STATE Characteristic**: `2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3`
  - Controls RGB colors and scene selection
  - 5-byte format for different modes

- **BRIGHTNESS Characteristic**: `B4D64C4F-C5A0-4A1B-AFEA-306B66269750`
  - Universal brightness control (0-100%)
  - Works for both RGB and scene modes
  - 2-byte format: `[0xCF] [Brightness]`

### Integration Architecture

- Uses Home Assistant's `ActiveBluetoothDataUpdateCoordinator` for reliable state management
- Implements `bleak-retry-connector` for robust Bluetooth connections
- Follows all Home Assistant best practices for Bluetooth integrations
- Supports config flow for easy setup and options flow for customization

## Troubleshooting

### Device Not Discovered

- Ensure your Cololight Mix ACID is powered on and in range
- Make sure Bluetooth is enabled on your Home Assistant server
- Try manually adding the device using its MAC address
- Check Home Assistant logs for Bluetooth errors

### Connection Issues

- The device can only connect to one client at a time
- Make sure the official Cololight app is closed
- Restart the integration from Settings → Devices & Services
- Try power cycling your Cololight device

### Brightness Not Working

- Brightness control works independently in both RGB and scene modes
- If using custom scenes, ensure hex values are exactly 10 characters
- Try adjusting brightness after setting a color or scene

## Development

This integration is based on reverse-engineered Bluetooth protocols. The development involved:

- Monitoring all 15 readable BLE characteristics
- Analyzing byte patterns for different commands
- Testing RGB modes, scene modes, and brightness control
- Implementing Home Assistant coordinator patterns
- Following official HA Bluetooth integration guidelines

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- [Report Issues](https://github.com/johnnylafer/ha-cololight-mix-acid/issues)
- [Discussions](https://github.com/johnnylafer/ha-cololight-mix-acid/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Developed by [@johnnylafer](https://github.com/johnnylafer) through Bluetooth protocol reverse
engineering and analysis of the Cololight Mix ACID device - see [Background](#background) above.

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Cololight. Use at your own risk.
