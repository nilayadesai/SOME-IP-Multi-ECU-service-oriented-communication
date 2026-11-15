
"""
Virtual Central Display ECU.

Consumes:
1. VehicleSpeedService
2. ClimateService
"""

import asyncio
import logging

from someipy import (
    ClientServiceInstance,
    MessageType,
    ReturnCode,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

# Vehicle service interface
from vehicle_speed_interface import (
    SERVICE_ID as VEHICLE_SERVICE_ID,
    INSTANCE_ID as VEHICLE_INSTANCE_ID,
    INTERFACE_IP as VEHICLE_INTERFACE_IP,
    CONSUMER_PORT as VEHICLE_CONSUMER_PORT,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    VEHICLE_STOPPED,
    VEHICLE_MOVING,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)

# Climate service interface
from climate_interface import (
    SERVICE_ID as CLIMATE_SERVICE_ID,
    INSTANCE_ID as CLIMATE_INSTANCE_ID,
    INTERFACE_IP as CLIMATE_INTERFACE_IP,
    CONSUMER_PORT as CLIMATE_CONSUMER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CLIMATE_EVENTGROUP_ID,
    STATUS_ACCEPTED,
    CabinTemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
    climate_service,
)


# ---------------------------------------------------------------------------
# Vehicle Event Callback
# ---------------------------------------------------------------------------

def vehicle_event_callback(event_id: int, event_payload: bytes) -> None:

    try:

        if event_id == 0x8001:

            speed = SpeedPayload().deserialize(event_payload)

            print()
            print("SpeedChanged notification received")
            print(
                f"Vehicle Speed Updated: "
                f"{speed.speed_kmph.value} km/h"
            )

        elif event_id == 0x8002:

            speed = SpeedPayload().deserialize(event_payload)

            print()
            print("!!! OVERSPEED WARNING !!!")
            print(
                f"Vehicle Speed: "
                f"{speed.speed_kmph.value} km/h"
            )

    except Exception as error:
        print(f"Vehicle event decoding error: {error}")


# ---------------------------------------------------------------------------
# Climate Event Callback
# ---------------------------------------------------------------------------

def climate_event_callback(event_id: int, event_payload: bytes) -> None:

    try:

        if event_id == CABIN_TEMPERATURE_CHANGED_EVENT_ID:

            temperature = CabinTemperaturePayload().deserialize(
                event_payload
            )

            print()
            print("CabinTemperatureChanged notification received")
            print(
                f"Cabin Temperature Updated: "
                f"{temperature.temperature.value / 10:.1f} C"
            )

    except Exception as error:
        print(f"Climate event decoding error: {error}")


# ---------------------------------------------------------------------------
# Vehicle Service Method Communication
# ---------------------------------------------------------------------------

async def vehicle_method_loop(
    client: ClientServiceInstance,
) -> None:

    while True:

        try:

            # GetSpeed
            speed_result = await client.call_method(
                GET_SPEED_METHOD_ID,
                b"",
            )

            if (
                speed_result.message_type == MessageType.RESPONSE
                and speed_result.return_code == ReturnCode.E_OK
            ):

                speed = SpeedPayload().deserialize(
                    speed_result.payload
                )

                print(
                    f"\nVehicle Speed: "
                    f"{speed.speed_kmph.value} km/h"
                )

            # GetVehicleState
            state_result = await client.call_method(
                GET_VEHICLE_STATE_METHOD_ID,
                b"",
            )

            if (
                state_result.message_type == MessageType.RESPONSE
                and state_result.return_code == ReturnCode.E_OK
            ):

                state = VehicleStatePayload().deserialize(
                    state_result.payload
                )

                if state.vehicle_state.value == VEHICLE_STOPPED:
                    state_name = "STOPPED"
                elif state.vehicle_state.value == VEHICLE_MOVING:
                    state_name = "MOVING"
                else:
                    state_name = "UNKNOWN"

                print(f"Vehicle State: {state_name}")

        except Exception as error:
            print(f"Vehicle service communication error: {error}")

        await asyncio.sleep(5)


# ---------------------------------------------------------------------------
# Climate Service Method Communication
# ---------------------------------------------------------------------------

async def climate_method_loop(
    client: ClientServiceInstance,
) -> None:

    target_temperature_sent = False

    while True:

        try:

            # GetCabinTemperature
            result = await client.call_method(
                GET_CABIN_TEMPERATURE_METHOD_ID,
                b"",
            )

            if (
                result.message_type == MessageType.RESPONSE
                and result.return_code == ReturnCode.E_OK
            ):

                temperature = CabinTemperaturePayload().deserialize(
                    result.payload
                )

                print(
                    f"\nCabin Temperature: "
                    f"{temperature.temperature.value / 10:.1f} C"
                )

            # SetTargetTemperature - send initial target of 22.0 C
            if not target_temperature_sent:

                request_payload = TargetTemperaturePayload(
                    220
                ).serialize()

                status_result = await client.call_method(
                    SET_TARGET_TEMPERATURE_METHOD_ID,
                    request_payload,
                )

                if (
                    status_result.message_type == MessageType.RESPONSE
                    and status_result.return_code == ReturnCode.E_OK
                ):

                    status = TemperatureStatusPayload().deserialize(
                        status_result.payload
                    )

                    if status.status.value == STATUS_ACCEPTED:
                        print("Target Temperature  : 22.0 C")
                        print("SetTargetTemperature: ACCEPTED")
                    else:
                        print("SetTargetTemperature: INVALID_TEMPERATURE")

                    target_temperature_sent = True

        except Exception as error:
            print(f"Climate service communication error: {error}")

        await asyncio.sleep(5)


# ---------------------------------------------------------------------------
# Vehicle Service Discovery
# ---------------------------------------------------------------------------

async def monitor_vehicle_service(
    client: ClientServiceInstance,
) -> None:

    print("\nSearching for VehicleSpeedService...")

    while not await client.is_available():

        print("VehicleSpeedService : NOT AVAILABLE")
        await asyncio.sleep(2)

    print("\nVehicleSpeedService : AVAILABLE")

    client.subscribe_eventgroup(speed_eventgroup, 5)
    client.subscribe_eventgroup(overspeed_eventgroup, 5)

    print("Subscribed to SpeedChanged and OverspeedWarning")

    await vehicle_method_loop(client)


# ---------------------------------------------------------------------------
# Climate Service Discovery
# ---------------------------------------------------------------------------

async def monitor_climate_service(
    client: ClientServiceInstance,
) -> None:

    print("\nSearching for ClimateService...")

    while not await client.is_available():

        print("ClimateService      : NOT AVAILABLE")
        await asyncio.sleep(2)

    print("\nClimateService      : AVAILABLE")

    client.subscribe_eventgroup(climate_eventgroup, 5)

    print("Subscribed to CabinTemperatureChanged")

    await climate_method_loop(client)


# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("CENTRAL VEHICLE DISPLAY")
    print("=" * 60)

    print(f"Vehicle Service ID : 0x{VEHICLE_SERVICE_ID:04X}")
    print(f"Climate Service ID : 0x{CLIMATE_SERVICE_ID:04X}")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    # Vehicle Service Consumer
    vehicle_client = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=VEHICLE_INSTANCE_ID,
        endpoint_ip=VEHICLE_INTERFACE_IP,
        endpoint_port=VEHICLE_CONSUMER_PORT,
    )

    vehicle_client.register_callback(vehicle_event_callback)

    # Climate Service Consumer
    climate_client = ClientServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=CLIMATE_INTERFACE_IP,
        endpoint_port=CLIMATE_CONSUMER_PORT,
    )

    climate_client.register_callback(climate_event_callback)

    print("Central Display clients initialized")

    vehicle_task = asyncio.create_task(
        monitor_vehicle_service(vehicle_client)
    )

    climate_task = asyncio.create_task(
        monitor_climate_service(climate_client)
    )

    try:

        await asyncio.gather(vehicle_task, climate_task)

    finally:

        vehicle_task.cancel()
        climate_task.cancel()

        for task in (vehicle_task, climate_task):
            try:
                await task
            except asyncio.CancelledError:
                pass

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nCentral Display stopped")
