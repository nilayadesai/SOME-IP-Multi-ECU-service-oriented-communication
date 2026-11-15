
"""
Virtual Climate ECU.

Provides:
1. GetCabinTemperature method
2. SetTargetTemperature method
3. CabinTemperatureChanged event
"""

import asyncio
import logging
from typing import Tuple

from someipy import (
    MessageType,
    Method,
    MethodResult,
    ReturnCode,
    ServerServiceInstance,
    ServiceBuilder,
    TransportLayerProtocol,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

from climate_interface import (
    SERVICE_ID,
    INSTANCE_ID,
    MAJOR_VERSION,
    INTERFACE_IP,
    PROVIDER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CLIMATE_EVENTGROUP_ID,
    MIN_TARGET_TEMPERATURE,
    MAX_TARGET_TEMPERATURE,
    STATUS_ACCEPTED,
    STATUS_INVALID_TEMPERATURE,
    CabinTemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
)


# ---------------------------------------------------------------------------
# Climate ECU State
# ---------------------------------------------------------------------------

current_cabin_temperature = 240
target_temperature = 220


# ---------------------------------------------------------------------------
# GetCabinTemperature Handler
# ---------------------------------------------------------------------------

async def get_cabin_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    print()
    print("GetCabinTemperature request received")
    print(f"Current cabin temperature: {current_cabin_temperature / 10:.1f} C")

    response_payload = CabinTemperaturePayload(
        current_cabin_temperature
    ).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print("GetCabinTemperature response sent")

    return result


# ---------------------------------------------------------------------------
# SetTargetTemperature Handler
# ---------------------------------------------------------------------------

async def set_target_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    global target_temperature

    print()
    print("SetTargetTemperature request received")

    try:
        request = TargetTemperaturePayload().deserialize(input_data)
        requested_temperature = request.temperature.value

        print(
            f"Requested target temperature: "
            f"{requested_temperature / 10:.1f} C"
        )

        if MIN_TARGET_TEMPERATURE <= requested_temperature <= MAX_TARGET_TEMPERATURE:

            target_temperature = requested_temperature
            status = STATUS_ACCEPTED

            print("Status: ACCEPTED")
            print(
                f"New target temperature: "
                f"{target_temperature / 10:.1f} C"
            )

        else:

            status = STATUS_INVALID_TEMPERATURE

            print("Status: INVALID_TEMPERATURE")
            print("Target temperature remains unchanged")

    except Exception as error:

        print(f"Could not decode temperature request: {error}")
        status = STATUS_INVALID_TEMPERATURE

    response_payload = TemperatureStatusPayload(status).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print("SetTargetTemperature response sent")

    return result


# ---------------------------------------------------------------------------
# Build Climate Provider Service
# ---------------------------------------------------------------------------

def build_climate_service():

    get_temperature_method = Method(
        id=GET_CABIN_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=get_cabin_temperature_handler,
    )

    set_temperature_method = Method(
        id=SET_TARGET_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=set_target_temperature_handler,
    )

    return (
        ServiceBuilder()
        .with_service_id(SERVICE_ID)
        .with_major_version(MAJOR_VERSION)
        .with_method(get_temperature_method)
        .with_method(set_temperature_method)
        .with_eventgroup(climate_eventgroup)
        .build()
    )


# ---------------------------------------------------------------------------
# Simulate Cabin Temperature and Send Event
# ---------------------------------------------------------------------------

async def simulate_cabin_temperature(
    service_instance: ServerServiceInstance,
) -> None:

    global current_cabin_temperature

    while True:

        current_cabin_temperature += 5

        if current_cabin_temperature > 260:
            current_cabin_temperature = 240

        event_payload = CabinTemperaturePayload(
            current_cabin_temperature
        ).serialize()

        print()
        print(
            f"Cabin temperature changed to "
            f"{current_cabin_temperature / 10:.1f} C"
        )

        service_instance.send_event(
            CLIMATE_EVENTGROUP_ID,
            CABIN_TEMPERATURE_CHANGED_EVENT_ID,
            event_payload,
        )

        print("CabinTemperatureChanged event sent")

        await asyncio.sleep(3)


# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Climate ECU")
    print("ClimateService Provider")
    print("=" * 60)

    print(f"Service ID       : 0x{SERVICE_ID:04X}")
    print(f"Instance ID      : 0x{INSTANCE_ID:04X}")
    print(f"GetTemperature   : 0x{GET_CABIN_TEMPERATURE_METHOD_ID:04X}")
    print(f"SetTemperature   : 0x{SET_TARGET_TEMPERATURE_METHOD_ID:04X}")
    print(f"Temperature Event: 0x{CABIN_TEMPERATURE_CHANGED_EVENT_ID:04X}")
    print(f"Provider endpoint: {INTERFACE_IP}:{PROVIDER_PORT}")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    climate_service = build_climate_service()

    provider_instance = ServerServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    print("Offering ClimateService...")

    await provider_instance.start_offer()

    print("ClimateService is being offered")

    temperature_task = asyncio.create_task(
        simulate_cabin_temperature(provider_instance)
    )

    try:

        await asyncio.Future()

    finally:

        temperature_task.cancel()

        try:
            await temperature_task
        except asyncio.CancelledError:
            pass

        await provider_instance.stop_offer()

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nClimate ECU stopped")
