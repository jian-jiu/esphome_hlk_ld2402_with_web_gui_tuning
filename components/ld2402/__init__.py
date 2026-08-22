import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID

DEPENDENCIES = ["uart", "network"]
AUTO_LOAD = ["binary_sensor", "sensor", "text_sensor", "web_server_base"]
MULTI_CONF = True

ld2402_ns = cg.esphome_ns.namespace("ld2402")
LD2402Component = ld2402_ns.class_(
    "LD2402Component", cg.Component, uart.UARTDevice
)

CONF_LD2402_ID = "ld2402_id"

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(LD2402Component),
        }
    )
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
