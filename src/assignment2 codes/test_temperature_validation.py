import asyncio
import logging

import central_display as cd

async def main():
    cd.set_someipy_log_level(logging.INFO)

    print("=" * 50)
    print("TARGET TEMPERATURE VALIDATION TEST")
    print("=" * 50)

    daemon = await cd.connect_to_someipy_daemon()

    client = cd.ClientServiceInstance(
        daemon=daemon,
        service=cd.climate_service,
        instance_id=cd.CLIMATE_INSTANCE_ID,
        endpoint_ip=cd.CLIMATE_INTERFACE_IP,
        endpoint_port=3004,
    )

    print("\nWaiting for ClimateService...")

    while not await client.is_available():
        await asyncio.sleep(1)

    print("ClimateService AVAILABLE\n")

    test_temperatures = [220, 160, 300, 100, 350]

    for temperature in test_temperatures:
        request = cd.TargetTemperaturePayload(temperature).serialize()

        result = await client.call_method(
            cd.SET_TARGET_TEMPERATURE_METHOD_ID,
            request,
        )

        if (
            result.message_type == cd.MessageType.RESPONSE
            and result.return_code == cd.ReturnCode.E_OK
        ):
            response = cd.TemperatureStatusPayload().deserialize(
                result.payload
            )

            status = response.status.value

            if status == cd.STATUS_ACCEPTED:
                print(f"{temperature / 10:.1f} C : ACCEPTED")
            else:
                print(f"{temperature / 10:.1f} C : REJECTED")
        else:
            print(f"{temperature / 10:.1f} C : NO VALID RESPONSE")

        await asyncio.sleep(1)

    print("\nTemperature validation test completed.")

asyncio.run(main())
