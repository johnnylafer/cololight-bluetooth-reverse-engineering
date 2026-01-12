"""Cololight Mix ACID BLE Protocol Encoder/Decoder.

Following the official Cololight BLE specification.
Protocol format: [type_byte][mode][param1][param2][param3] = 5 bytes total

Note: The Mix ACID device internally reverses bytes 1-4 when storing state,
but we always send commands in the official format documented in the spec.
"""

from typing import Tuple, Optional
from .const import DEFAULT_SPEED, DEFAULT_VARIATION


def encode_solid_color(r: int, g: int, b: int) -> bytes:
    """Encode solid RGB color command.

    Format: [0xff][0x00][RR][GG][BB]

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        5-byte command to send to device
    """
    return bytes([0xFF, 0x00, r & 0xFF, g & 0xFF, b & 0xFF])


def encode_dynamic_effect(
    effect_index: int,
    speed: int = DEFAULT_SPEED,
    variation: int = DEFAULT_VARIATION
) -> bytes:
    """Encode dynamic effect command (mode 0x01).

    Format: [0xff][0x01][AA][BB][CC]
    - AA: Effect index (0x80-0xC4)
    - BB: Speed (0x00-0xFF, higher = slower)
    - CC: Variation mode (0x00-0x0F)

    Args:
        effect_index: Effect ID from DYNAMIC_EFFECTS (0x80-0xC4)
        speed: Effect speed (0x00-0xFF), default 0x0A
        variation: Variation mode (0x00-0x0F), default 0x00

    Returns:
        5-byte command to send to device
    """
    return bytes([0xFF, 0x01, effect_index & 0xFF, speed & 0xFF, variation & 0x0F])


def encode_special_overall(
    effect_index: int,
    speed: int = DEFAULT_SPEED,
    variation: int = DEFAULT_VARIATION,
    color_jump: int = 0
) -> bytes:
    """Encode special overall dynamic effect (mode 0x03).

    Format: [0xff][0x03][AA][BB][CD]
    - AA: Effect index (0x80-0xC4)
    - BB: Speed (0x00-0xFF)
    - C: Variation mode (0x0-0xF)
    - D: Color jump mode (0x0-0xF)

    Args:
        effect_index: Effect ID (0x80-0xC4)
        speed: Effect speed, default 0x0A
        variation: Variation pattern (0x0-0xF)
        color_jump: Color jump mode (0x0-0xF)

    Returns:
        5-byte command to send to device
    """
    cd_byte = ((variation & 0x0F) << 4) | (color_jump & 0x0F)
    return bytes([0xFF, 0x03, effect_index & 0xFF, speed & 0xFF, cd_byte])


def encode_special_individual(
    effect_index: int,
    speed: int = DEFAULT_SPEED,
    variation: int = DEFAULT_VARIATION,
    color_jump: int = 0
) -> bytes:
    """Encode special individual dynamic effect (mode 0x04).

    Format: [0xff][0x04][AA][BB][CD]
    Same parameters as mode 0x03 but affects individual LEDs.

    Args:
        effect_index: Effect ID (0x80-0xC4)
        speed: Effect speed, default 0x0A
        variation: Variation pattern (0x0-0xF)
        color_jump: Color jump mode (0x0-0xF)

    Returns:
        5-byte command to send to device
    """
    cd_byte = ((variation & 0x0F) << 4) | (color_jump & 0x0F)
    return bytes([0xFF, 0x04, effect_index & 0xFF, speed & 0xFF, cd_byte])


def encode_smooth_overall(
    effect_index: int,
    speed: int = DEFAULT_SPEED,
    variation: int = DEFAULT_VARIATION,
    color_jump: int = 0
) -> bytes:
    """Encode smooth overall dynamic effect (mode 0x05).

    Mode 0x05 is mode 0x03 with smooth transitions.
    Format: [0xff][0x05][AA][BB][CD]

    Args:
        effect_index: Effect ID (0x80-0xC4)
        speed: Effect speed, default 0x0A
        variation: Variation pattern (0x0-0xF)
        color_jump: Color jump mode (0x0-0xF)

    Returns:
        5-byte command to send to device
    """
    cd_byte = ((variation & 0x0F) << 4) | (color_jump & 0x0F)
    return bytes([0xFF, 0x05, effect_index & 0xFF, speed & 0xFF, cd_byte])


def encode_smooth_individual(
    effect_index: int,
    speed: int = DEFAULT_SPEED,
    variation: int = DEFAULT_VARIATION,
    color_jump: int = 0
) -> bytes:
    """Encode smooth individual dynamic effect (mode 0x06).

    Mode 0x06 is mode 0x04 with smooth transitions.
    Format: [0xff][0x06][AA][BB][CD]

    Args:
        effect_index: Effect ID (0x80-0xC4)
        speed: Effect speed, default 0x0A
        variation: Variation pattern (0x0-0xF)
        color_jump: Color jump mode (0x0-0xF)

    Returns:
        5-byte command to send to device
    """
    cd_byte = ((variation & 0x0F) << 4) | (color_jump & 0x0F)
    return bytes([0xFF, 0x06, effect_index & 0xFF, speed & 0xFF, cd_byte])


def decode_state(state_data: bytes) -> dict:
    """Decode device state data.

    The device stores state with bytes 1-4 reversed from what we send.
    When we send: [0xff][mode][p1][p2][p3]
    Device stores: [0xff][p3][p2][p1][mode]

    This function un-reverses to get the original format.

    Args:
        state_data: 5 bytes read from device

    Returns:
        Dictionary with decoded state:
        {
            'mode': Mode byte (0x00, 0x01, 0x03, 0x04, 0x05, 0x06),
            'param1': First parameter byte,
            'param2': Second parameter byte,
            'param3': Third parameter byte,
            'rgb': (r, g, b) tuple if mode 0x00, else None,
            'effect_index': Effect ID if mode 0x01-0x06, else None,
            'speed': Speed value if applicable, else None,
            'variation': Variation mode if applicable, else None,
            'color_jump': Color jump mode if applicable, else None
        }
    """
    if len(state_data) != 5 or state_data[0] != 0xFF:
        return {'mode': None, 'param1': None, 'param2': None, 'param3': None}

    # Un-reverse bytes 1-4: device stores [0xff][p3][p2][p1][mode]
    # We want: [0xff][mode][p1][p2][p3]
    mode = state_data[4]
    param1 = state_data[3]
    param2 = state_data[2]
    param3 = state_data[1]

    result = {
        'mode': mode,
        'param1': param1,
        'param2': param2,
        'param3': param3,
    }

    # Mode-specific decoding
    if mode == 0x00:
        # Solid color mode: param1=R, param2=G, param3=B
        result['rgb'] = (param1, param2, param3)
        result['effect_index'] = None
        result['speed'] = None
        result['variation'] = None
        result['color_jump'] = None

    elif mode == 0x01:
        # Dynamic effect mode: param1=effect, param2=speed, param3=variation
        result['rgb'] = None
        result['effect_index'] = param1
        result['speed'] = param2
        result['variation'] = param3
        result['color_jump'] = None

    elif mode in (0x03, 0x04, 0x05, 0x06):
        # Special modes: param1=effect, param2=speed, param3=CD (variation+jump)
        result['rgb'] = None
        result['effect_index'] = param1
        result['speed'] = param2
        result['variation'] = (param3 >> 4) & 0x0F
        result['color_jump'] = param3 & 0x0F

    else:
        # Unknown mode
        result['rgb'] = None
        result['effect_index'] = None
        result['speed'] = None
        result['variation'] = None
        result['color_jump'] = None

    return result


def encode_power_on() -> bytes:
    """Encode power on command.

    Returns:
        2-byte power on command
    """
    return bytes([0x81, 0x01])


def encode_power_off() -> bytes:
    """Encode power off command.

    Returns:
        2-byte power off command
    """
    return bytes([0x80, 0x00])


def encode_brightness(brightness: int, power_on: bool = True) -> bytes:
    """Encode brightness control command.

    Format: [type][brightness]
    - type: 0xcf (on with brightness) or 0xce (off with brightness)
    - brightness: 0-255

    Args:
        brightness: Brightness level (0-255)
        power_on: True to turn on, False to turn off

    Returns:
        2-byte brightness command
    """
    type_byte = 0xCF if power_on else 0xCE
    return bytes([type_byte, brightness & 0xFF])
