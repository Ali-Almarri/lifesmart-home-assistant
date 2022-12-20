"""Support for the LifeSmart climate devices."""
import logging
import time
from homeassistant.components.climate import ENTITY_ID_FORMAT, ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_DRY,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    HVAC_MODE_OFF,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
)

from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from . import LifeSmartDevice
_LOGGER = logging.getLogger(__name__)
DEVICE_TYPE = "climate"

LIFESMART_STATE_LIST = [HVAC_MODE_OFF,
HVAC_MODE_AUTO,
HVAC_MODE_FAN_ONLY,
HVAC_MODE_COOL,
HVAC_MODE_HEAT,
HVAC_MODE_DRY]

LIFESMART_STATE_LIST2 = [HVAC_MODE_OFF,
HVAC_MODE_HEAT]

FAN_MODES = [FAN_LOW, FAN_MEDIUM, FAN_HIGH]
GET_FAN_SPEED = { FAN_LOW:15, FAN_MEDIUM:45, FAN_HIGH:76 }

AIR_TYPES=["V_AIR_P"]

THER_TYPES = ["SL_CP_DN"]

LIFESMART_STATE_LIST

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up LifeSmart Climate devices."""
    if discovery_info is None:
        return
    devices = []
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    if "T" not in dev['data'] and "P3" not in dev['data']:
        return
    devices.append(LifeSmartClimateDevice(dev,"idx","0",param))
    add_entities(devices)

class LifeSmartClimateDevice(LifeSmartDevice, ClimateEntity):
    """LifeSmart climate devices,include air conditioner,heater."""

    def __init__(self, dev, idx, val, param):
        """Init LifeSmart cover device."""
        super().__init__(dev, idx, val, param)
        self._name = dev['name']
        cdata = dev['data']
        self._attr_unique_id = (dev['devtype'] + "_" + dev['agt'] + "_" + dev['me']).lower().replace(":","_").replace("@","_")
        self.entity_id = ENTITY_ID_FORMAT.format(self._attr_unique_id)
        if dev['devtype'] in AIR_TYPES:
            self._attr_hvac_modes = LIFESMART_STATE_LIST
            if cdata['O']['type'] % 2 == 0:
                self._attr_hvac_mode = LIFESMART_STATE_LIST[0]
            else:
                self._attr_hvac_mode = LIFESMART_STATE_LIST[cdata['MODE']['val']]
            self._attr_extra_state_attributes.update({"last_mode": LIFESMART_STATE_LIST[cdata['MODE']['val']]})
            self._attr_current_temperature = cdata['T']['v']
            self._attr_target_temperature = cdata['tT']['v']
            self._attr_min_temp = 10
            self._attr_max_temp = 35
            self._fanspeed = cdata['F']['val']
        else:
            self._attr_hvac_modes = LIFESMART_STATE_LIST2
            if cdata['P1']['type'] % 2 == 0:
                self._attr_hvac_modes = LIFESMART_STATE_LIST2[0]
            else:
                self._attr_hvac_modes = LIFESMART_STATE_LIST2[1]
            if cdata['P2']['type'] % 2 == 0:
                self._attr_extra_state_attributes.setdefault('Heating',"false")
            else:
                self._attr_extra_state_attributes.setdefault('Heating',"true")
            self._attr_current_temperature = cdata['P4']['val'] / 10
            self._attr_target_temperature = cdata['P3']['val'] / 10
            self._attr_min_temp = 5
            self._attr_max_temp = 35

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def fan_mode(self):
        """Return the fan setting."""
        fanmode = None
        if self._fanspeed < 30:
            fanmode = FAN_LOW
        elif self._fanspeed < 65 and self._fanspeed >= 30:
            fanmode = FAN_MEDIUM
        elif self._fanspeed >=65:
            fanmode = FAN_HIGH
        return fanmode

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return FAN_MODES

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        new_temp = int(kwargs['temperature']*10)
        _LOGGER.info("set_temperature: %s",str(new_temp))
        if self._devtype in AIR_TYPES:
            super()._lifesmart_epset(self, "0x88", new_temp, "tT")
        else:
            super()._lifesmart_epset(self, "0x88", new_temp, "P3")

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        super()._lifesmart_epset(self, "0xCE", GET_FAN_SPEED[fan_mode], "F")

    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        if self._devtype in AIR_TYPES:
            if hvac_mode == HVAC_MODE_OFF:
                super()._lifesmart_epset(self, "0x80", 0, "O")
                return
            if self._attr_hvac_mode == HVAC_MODE_OFF:
                if super()._lifesmart_epset(self, "0x81", 1, "O") == 0:
                    time.sleep(2)
                else:
                    return
            super()._lifesmart_epset(self, "0xCE", LIFESMART_STATE_LIST.index(hvac_mode), "MODE")
        else:
            if hvac_mode == HVAC_MODE_OFF:
                super()._lifesmart_epset(self, "0x80", 0, "P1")
                time.sleep(1)
                super()._lifesmart_epset(self, "0x80", 0, "P2")
                return
            else:
                if super()._lifesmart_epset(self, "0x81", 1, "P1") == 0:
                    time.sleep(2)
                else:
                    return

    def turn_on(self):
        """Turn on."""
        super()._lifesmart_epset(self, "0x81", 1, "O")

    def turn_off(self):
        """Turn off."""
        super()._lifesmart_epset(self, "0x80", 0, "O")

    @property
    def supported_features(self):
        """Return the list of supported features."""
        if self._devtype in AIR_TYPES:
            return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE
        else:
            return SUPPORT_TARGET_TEMPERATURE
