# Cololight Mix ACID Integration - Development Log

## Session: 2026-01-12 (Late Night Session)

### Issues Fixed

#### 1. State Not Updating in Home Assistant UI (v1.0.8 - v1.0.10)

**Problem:**
- Light entity always showed as "off" in Home Assistant UI
- Physical device responded correctly to commands
- State was being read correctly from device but UI wasn't updating

**Root Cause:**
- After executing commands and reading state back, coordinator was updating internal variables (`self._is_on`, `self._brightness`, etc.)
- But coordinator wasn't notifying listening entities (the light entity) that data had changed
- Wrong method name used: `async_set_updated_data()` doesn't exist on `ActiveBluetoothDataUpdateCoordinator`

**Fix (v1.0.10):**
- Changed from `async_set_updated_data(None)` to `async_update_listeners()`
- This is the correct method for `ActiveBluetoothDataUpdateCoordinator` to notify entities
- Location: `coordinator.py:198` in `_async_execute_command()` method

**Code Change:**
```python
try:
    await command_func(client)
    # Read back state after command
    await self._async_read_state(client)
    # Notify entities of state change
    self.async_update_listeners()  # ← CORRECT METHOD
finally:
    await client.disconnect()
```

---

#### 2. Scenes Not Working Correctly (v1.0.9 - v1.0.11)

**Problem:**
- Only "Cool Mist" effect did something, but it was the wrong scene
- All other scenes didn't work at all
- Scenes were being sent but device wasn't responding correctly

**Investigation Process:**
1. Created test script `test_scene_send.py` to send original hex values
2. Discovered device was reversing bytes 1-4 when storing the state
3. Example: Send `ff00188906` → Device stores `ff06891800`
4. Created `test_reversed_scenes.py` to test sending reversed bytes
5. Confirmed that sending reversed bytes produces correct scenes!

**Root Cause:**
The device expects scene bytes in REVERSED order (bytes 1-4):
- We need to SEND: `ff04001801` (reversed)
- Device stores internally: `ff01180004` (un-reversed)
- When reading back: Device returns `ff01180004`
- For scene detection: We reverse it back to `ff04001801` to match const.py

**Fix (v1.0.11):**

**Updated const.py with reversed hex values:**
```python
# Built-in scenes (effect name -> hex value to write)
# Note: Device stores these with bytes 1-4 reversed internally
BUILT_IN_SCENES = {
    "Color Flow": "ff04001801",   # Was: ff01180004
    "Cool Mist": "ff06891800",    # Was: ff00188906
    "Candy": "ff06991800",        # Was: ff00189906
    "Savannah": "ff06ad1800",     # Was: ff0018ad06
    "Deep Blue": "ff06841f30",    # Was: ff301f8406
    "Purple Haze": "ff06b21070",  # Was: ff7010b206
}
```

**Updated coordinator.py read logic:**
```python
else:
    # Scene mode - Device un-reverses what we send
    # We send: ff04001801 -> Device stores: ff01180004
    # So reverse it back to match our const.py values
    reversed_scene = bytes([state_data[0], state_data[4], state_data[3], state_data[2], state_data[1]])
    self._current_scene = reversed_scene.hex()
```

**Verification:**
- Created `test_final_scenes.py` to test all corrected hex values
- User confirmed all scenes working correctly

---

### Version History

#### v1.0.8
- Attempted to add `async_set_updated_data(None)` to notify entities
- **FAILED:** Method doesn't exist on ActiveBluetoothDataUpdateCoordinator

#### v1.0.9
- Fixed byte reversal in scene reading logic
- Added scene hex value reversal when reading from device
- **INCOMPLETE:** Still using wrong notification method

#### v1.0.10
- Fixed notification method to use `async_update_listeners()` instead
- State updates now work correctly
- **INCOMPLETE:** Scene hex values still wrong

#### v1.0.11 (CURRENT - WORKING)
- Updated all scene hex values in const.py to reversed byte order
- Kept byte reversal logic in coordinator for scene detection
- **COMPLETE:** Both state updates and scenes working correctly

---

### Technical Details

#### Device Byte Order Behavior

**RGB Color:**
- Send: `[0xFF] [0x00] [R] [G] [B]`
- Device stores: Same format
- No reversal

**Scenes:**
- Send: `[0xFF] [B1] [B2] [B3] [B4]` (reversed from what we intuitively expect)
- Device stores: `[0xFF] [B4] [B3] [B2] [B1]` (un-reverses internally)
- Read back: Returns what it stored
- Need to reverse again for scene detection matching

**OFF State:**
- Pattern: `ff 00 00 00 ff`
- Bytes 1-3 all zero AND byte 4 is 0xFF

#### BLE Characteristics

**CHAR_STATE:** `2EDCF977-60AC-49B0-AA2A-ED75ABD74EA3`
- Controls RGB color and scenes
- Format: 5 bytes
- Mode byte at position 4 (0x00 = RGB, others = scene)

**CHAR_BRIGHTNESS:** `B4D64C4F-C5A0-4A1B-AFEA-306B66269750`
- Controls brightness level
- Format: `[0xCF] [brightness_0-100]`

---

### Test Scripts Created

1. **test_scene_send.py** - Original hex values testing (discovered problem)
2. **test_reversed_scenes.py** - Reversed bytes testing (proved solution)
3. **test_final_scenes.py** - Final verification (confirmed working)

All test scripts located in `~/cololight_test/` on a Linux test machine on the local network

---

### User Device Information

- **MAC Address:** `xx:xx:xx:xx:xx:xx` (device-specific - yours will differ)
- **Device Name:** MIX Acid*
- **Model:** Cololight Mix ACID
- **Connection:** Bluetooth LE (BLE)
- **Test Environment:** a Linux test machine on the local network

---

### Files Modified

#### custom_components/cololight_mix_acid/const.py
- Updated all BUILT_IN_SCENES hex values to reversed byte order

#### custom_components/cololight_mix_acid/coordinator.py
- Line 198: Changed `async_set_updated_data(None)` to `async_update_listeners()`
- Lines 113-123: Updated scene reading logic with byte reversal

#### custom_components/cololight_mix_acid/manifest.json
- Version bumped: 1.0.8 → 1.0.9 → 1.0.10 → 1.0.11

---

### Next Steps (If Issues Arise)

1. **If state still doesn't update:**
   - Check Home Assistant logs for errors
   - Verify `async_update_listeners()` is being called
   - Confirm coordinator is initialized correctly

2. **If scenes still don't work:**
   - Run `test_final_scenes.py` on the test machine to verify hex values
   - Check if device firmware has changed
   - Verify BLE connection is stable

3. **For custom scenes:**
   - User needs to discover hex values from app
   - Test with `test_final_scenes.py` template
   - Values must be in reversed byte order (bytes 1-4)
   - Add to options flow in Home Assistant

---

### References

- [Home Assistant Bluetooth Data Fetching](https://developers.home-assistant.io/docs/core/bluetooth/bluetooth_fetching_data/)
- ActiveBluetoothDataUpdateCoordinator documentation
- Integration GitHub: https://github.com/johnnylafer/ha-cololight-mix-acid

---

### Session End

- All background processes stopped
- v1.0.11 pushed to GitHub with tag
- Ready for user testing after update via HACS
- Time: 3 AM - User going to bed
