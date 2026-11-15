
"""
Common definition of the Climate SOME/IP service.
"""

from dataclasses import dataclass

from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import SomeIpPayload, Sint16, Uint8


# ---------------------------------------------------------------------------
# Service identification
# ---------------------------------------------------------------------------

SERVICE_ID = 0x2234
INSTANCE_ID = 0x0001
MAJOR_VERSION = 1


# ---------------------------------------------------------------------------
# Method identification
# ---------------------------------------------------------------------------

GET_CABIN_TEMPERATURE_METHOD_ID = 0x0001
SET_TARGET_TEMPERATURE_METHOD_ID = 0x0002


# ---------------------------------------------------------------------------
# Event identification
# ---------------------------------------------------------------------------

CABIN_TEMPERATURE_CHANGED_EVENT_ID = 0x8001
CLIMATE_EVENTGROUP_ID = 0x0001


# ---------------------------------------------------------------------------
# Temperature validation
# ---------------------------------------------------------------------------

MIN_TARGET_TEMPERATURE = 160
MAX_TARGET_TEMPERATURE = 300

STATUS_ACCEPTED = 0
STATUS_INVALID_TEMPERATURE = 1


# ---------------------------------------------------------------------------
# Network configuration
# ---------------------------------------------------------------------------

INTERFACE_IP = "127.0.0.1"
PROVIDER_PORT = 3001
CONSUMER_PORT = 3003


# ---------------------------------------------------------------------------
# Payload definitions
# ---------------------------------------------------------------------------

@dataclass
class CabinTemperaturePayload(SomeIpPayload):

    temperature: Sint16

    def __init__(self, temperature: int = 240):
        self.temperature = Sint16(temperature)


@dataclass
class TargetTemperaturePayload(SomeIpPayload):

    temperature: Sint16

    def __init__(self, temperature: int = 220):
        self.temperature = Sint16(temperature)


@dataclass
class TemperatureStatusPayload(SomeIpPayload):

    status: Uint8

    def __init__(self, status: int = STATUS_ACCEPTED):
        self.status = Uint8(status)


# ---------------------------------------------------------------------------
# SOME/IP Methods
# ---------------------------------------------------------------------------

get_cabin_temperature_method = Method(
    id=GET_CABIN_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)

set_target_temperature_method = Method(
    id=SET_TARGET_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# ---------------------------------------------------------------------------
# SOME/IP Event
# ---------------------------------------------------------------------------

cabin_temperature_changed_event = Event(
    id=CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


# ---------------------------------------------------------------------------
# Event Group
# ---------------------------------------------------------------------------

climate_eventgroup = EventGroup(
    id=CLIMATE_EVENTGROUP_ID,
    events=[cabin_temperature_changed_event],
)


# ---------------------------------------------------------------------------
# Climate Service
# ---------------------------------------------------------------------------

climate_service = (
    ServiceBuilder()
    .with_service_id(SERVICE_ID)
    .with_major_version(MAJOR_VERSION)
    .with_method(get_cabin_temperature_method)
    .with_method(set_target_temperature_method)
    .with_eventgroup(climate_eventgroup)
    .build()
)
