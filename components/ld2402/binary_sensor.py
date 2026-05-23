import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import CONF_ID, CONF_TYPE
from . import LD2402Component, CONF_LD2402_ID, ld2402_ns

DEPENDENCIES = ["ld2402"]

CONF_PRESENCE = "presence"
CONF_INTERFERENCE = "interference"

TYPES = {
    CONF_PRESENCE: "set_presence_sensor",
    CONF_INTERFERENCE: "set_interference_sensor",
}

CONFIG_SCHEMA = binary_sensor.binary_sensor_schema().extend(
    {
        cv.GenerateID(CONF_LD2402_ID): cv.use_id(LD2402Component),
        cv.Optional(CONF_TYPE, default=CONF_PRESENCE): cv.one_of(
            *TYPES, lower=True
        ),
    }
)

async def to_code(config):
    hub = await cg.get_variable(config[CONF_LD2402_ID])
    var = await binary_sensor.new_binary_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]])(var))
