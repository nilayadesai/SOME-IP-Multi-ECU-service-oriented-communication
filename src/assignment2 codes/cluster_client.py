
"""
Virtual Instrument Cluster ECU.

Consumes VehicleSpeedService.
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

from vehicle_speed_interface import (
    CONSUMER_PORT,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    INSTANCE_ID,
    INTERFACE_IP,
    SERVICE_ID,
    VEHICLE_STOPPED,
    VEHICLE_MOVING,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)


# ---------------------------------------------------------------------------
# Event Callback
# ---------------------------------------------------------------------------

def speed_event_callback(
    event_id: int,
    event_payload: bytes,
) -> None:

    try:

        if event_id == 0x8001:

            speed_message = SpeedPayload().deserialize(
                event_payload
            )

            print()
            print("SpeedChanged notification received")
            print(f"Event ID      : 0x{event_id:04X}")
            print(f"Payload bytes : {event_payload.hex(' ')}")
            print(
                f"Vehicle speed : "
                f"{speed_message.speed_kmph.value} km/h"
            )

        elif event_id == 0x8002:

            speed_message = SpeedPayload().deserialize(
                event_payload
            )

            print()
            print("!!! OVERSPEED WARNING RECEIVED !!!")
            print(f"Event ID      : 0x{event_id:04X}")
            print(f"Payload bytes : {event_payload.hex(' ')}")
            print(
                f"Vehicle speed : "
                f"{speed_message.speed_kmph.value} km/h"
            )

    except Exception as error:

        print(f"Could not decode event payload: {error}")


# ---------------------------------------------------------------------------
# GetSpeed Method
# ---------------------------------------------------------------------------

async def call_get_speed(
    client_instance: ClientServiceInstance,
) -> None:

    while True:

        try:

            print()
            print("Calling GetSpeed...")

            result = await client_instance.call_method(
                GET_SPEED_METHOD_ID,
                b"",
            )

            if result.message_type == MessageType.RESPONSE:

                print("GetSpeed response received")
                print(f"Return code   : {result.return_code}")
                print(f"Payload bytes : {result.payload.hex(' ')}")

                if result.return_code == ReturnCode.E_OK:

                    speed_message = SpeedPayload().deserialize(
                        result.payload
                    )

                    print(
                        f"Vehicle speed : "
                        f"{speed_message.speed_kmph.value} km/h"
                    )

            elif result.message_type == MessageType.ERROR:

                print("Provider returned SOME/IP error")

        except Exception as error:

            print(f"GetSpeed call failed: {error}")

        await asyncio.sleep(5)


# ---------------------------------------------------------------------------
# GetVehicleState Method
# ---------------------------------------------------------------------------

async def call_get_vehicle_state(
    client_instance: ClientServiceInstance,
) -> None:

    while True:

        try:

            print()
            print("Calling GetVehicleState...")

            result = await client_instance.call_method(
                GET_VEHICLE_STATE_METHOD_ID,
                b"",
            )

            if result.message_type == MessageType.RESPONSE:

                print("GetVehicleState response received")
                print(f"Return code   : {result.return_code}")
                print(f"Payload bytes : {result.payload.hex(' ')}")

                if result.return_code == ReturnCode.E_OK:

                    state_message = VehicleStatePayload().deserialize(
                        result.payload
                    )

                    state_value = state_message.vehicle_state.value

                    if state_value == VEHICLE_STOPPED:
                        state_name = "STOPPED"
                    elif state_value == VEHICLE_MOVING:
                        state_name = "MOVING"
                    else:
                        state_name = "UNKNOWN"

                    print(f"Vehicle state : {state_name}")

            elif result.message_type == MessageType.ERROR:

                print("Provider returned SOME/IP error")

        except Exception as error:

            print(f"GetVehicleState call failed: {error}")

        await asyncio.sleep(5)


# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Instrument Cluster ECU")
    print("VehicleSpeedService Consumer")
    print("=" * 60)

    print(f"Required Service ID  : 0x{SERVICE_ID:04X}")
    print(f"Required Instance ID : 0x{INSTANCE_ID:04X}")
    print(f"Consumer endpoint    : {INTERFACE_IP}:{CONSUMER_PORT}")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    client_instance = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CONSUMER_PORT,
    )

    client_instance.register_callback(
        speed_event_callback
    )

    print("Searching for VehicleSpeedService...")

    while not await client_instance.is_available():

        print("VehicleSpeedService is not yet available")

        await asyncio.sleep(1)

    print()
    print("VehicleSpeedService is AVAILABLE")

    # Subscribe to SpeedChanged event group
    print("Subscribing to SpeedChanged...")

    client_instance.subscribe_eventgroup(
        speed_eventgroup,
        5,
    )

    # Subscribe to OverspeedWarning event group
    print("Subscribing to OverspeedWarning...")

    client_instance.subscribe_eventgroup(
        overspeed_eventgroup,
        5,
    )

    print("Both event-group subscriptions requested")

    speed_task = asyncio.create_task(
        call_get_speed(client_instance)
    )

    state_task = asyncio.create_task(
        call_get_vehicle_state(client_instance)
    )

    try:

        await asyncio.Future()

    finally:

        speed_task.cancel()
        state_task.cancel()

        for task in (speed_task, state_task):
            try:
                await task
            except asyncio.CancelledError:
                pass

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nInstrument Cluster stopped")
