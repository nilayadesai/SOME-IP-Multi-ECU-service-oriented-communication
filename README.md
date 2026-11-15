# SOME/IP-Based Vehicle Communication System

## Overview

This project focuses on implementing service-oriented communication between vehicle-related software components using SOME/IP (Scalable Service-Oriented Middleware over IP).

The project starts with a basic Vehicle Speed Service consisting of a Vehicle ECU acting as the service provider and an Instrument Cluster ECU acting as the service consumer. It is further extended into a multi-ECU architecture consisting of four virtual ECUs: Vehicle ECU, Instrument Cluster ECU, Climate ECU, and Central Display ECU.

The Vehicle ECU provides vehicle speed information through the VehicleSpeedService, while the Climate ECU provides cabin temperature information through the ClimateService. The Instrument Cluster ECU consumes vehicle speed data, whereas the Central Display ECU consumes services from both providers.

The system implements method-based request-response communication and event-based notifications. It also demonstrates SOME/IP Service Discovery, event-group subscriptions, multiple service consumers, temperature validation, and service failure and recovery.

The implementation uses Python and the `someipy` library on Linux (Ubuntu). The applications communicate using UDP through the loopback interface (`127.0.0.1`). Wireshark and tcpdump are used to capture and analyse SOME/IP network traffic.

## Technologies Used

- Python
- Linux (Ubuntu)
- SOME/IP Protocol
- someipy Library
- UDP Communication
- SOME/IP Service Discovery
- Wireshark
- tcpdump
- Linux Terminal

## System Architecture

The system consists of the following components:

| Component | Role | Purpose |
|-----------|------|---------|
| SOME/IP Daemon | Service Discovery | Helps consumers discover available services |
| Vehicle ECU | Service Provider | Provides vehicle speed information |
| Instrument Cluster ECU | Service Consumer | Requests and receives vehicle speed data |
| Climate ECU | Service Provider | Provides cabin temperature information |
| Central Display ECU | Service Consumer | Consumes VehicleSpeedService and ClimateService |

## SOME/IP Services

The system implements two services:

### 1. VehicleSpeedService

- **Service ID:** `0x1234`
- **Instance ID:** `0x5678`

| Element | Type | ID | Description |
|---------|------|----|-------------|
| GetSpeed() | Method | `0x0001` | Returns the current vehicle speed |
| GetVehicleState() | Method | `0x0002` | Returns vehicle state (STOPPED / MOVING) |
| SpeedChanged | Event | `0x8001` | Sends updated vehicle speed |
| OverspeedWarning | Event | `0x8002` | Sends warning when speed exceeds 80 km/h |

### 2. ClimateService

- **Service ID:** `0x2234`
- **Instance ID:** `0x0001`

| Element | Type | ID | Description |
|---------|------|----|-------------|
| GetCabinTemperature() | Method | `0x0001` | Returns current cabin temperature |
| SetTargetTemperature() | Method | `0x0002` | Sets and validates target temperature |
| CabinTemperatureChanged | Event | `0x8001` | Sends updated cabin temperature |

## Communication Features

- **Service Discovery:** Consumers discover available services through the SOME/IP daemon.
- **GetSpeed:** Implements request-response communication to retrieve current vehicle speed.
- **GetVehicleState:** Returns the current vehicle state as STOPPED or MOVING.
- **SpeedChanged:** Sends automatic speed updates to subscribed consumers.
- **OverspeedWarning:** Generates a warning when vehicle speed exceeds 80 km/h.
- **GetCabinTemperature:** Retrieves the current cabin temperature.
- **SetTargetTemperature:** Accepts or rejects temperature requests based on validation.
- **CabinTemperatureChanged:** Sends cabin temperature updates to subscribed consumers.
- **Multiple Consumers:** Allows both Instrument Cluster and Central Display to consume VehicleSpeedService.
- **Multiple Services:** Allows the Central Display to consume VehicleSpeedService and ClimateService.

## SOME/IP Configuration

| Parameter | Value |
|-----------|-------|
| VehicleSpeedService ID | `0x1234` |
| VehicleSpeedService Instance ID | `0x5678` |
| ClimateService ID | `0x2234` |
| ClimateService Instance ID | `0x0001` |
| Transport Protocol | UDP |
| Provider Endpoint (Vehicle ECU) | `127.0.0.1:3000` |
| Consumer Endpoint (Instrument Cluster) | `127.0.0.1:3002` |
| Provider Endpoint (Climate ECU) | `127.0.0.1:3001` |
| Service Discovery Port | `30490` |
| Multicast Address | `224.224.224.245` |

## Project Files

| File | Purpose |
|------|---------|
| `vehicle_speed_interface.py` | Defines VehicleSpeedService identifiers, methods, events, event groups, and payload format |
| `vehicle_speed_service.py` | Implements the Vehicle Speed Service provider |
| `cluster_client.py` | Implements service discovery, method calls, and event subscriptions |
| `someipyd.json` | Contains SOME/IP daemon configuration |

## Climate Temperature Validation

The `SetTargetTemperature()` method validates requested temperature values.

| Requested Temperature | Result |
|-----------------------|--------|
| 16.0 °C | ACCEPTED |
| 22.0 °C | ACCEPTED |
| 30.0 °C | ACCEPTED |
| 10.0 °C | REJECTED |
| 35.0 °C | REJECTED |

- Valid temperature requests return `ACCEPTED`.
- Invalid temperature requests return `INVALID_TEMPERATURE`.
- The target temperature remains unchanged when an invalid value is received.

## Key Features

- Communication between multiple virtual ECUs.
- SOME/IP Service Discovery and service availability checking.
- Method-based request-response communication.
- Event-based notification and event-group subscription.
- Multiple consumers receiving data from a single service.
- Central Display consuming multiple services.
- Vehicle speed and cabin temperature monitoring.
- Overspeed warning generation above 80 km/h.
- Target temperature validation.
- Service failure and recovery testing.

## Execution

1. Open the project folder and activate the Python virtual environment.
2. Start the SOME/IP daemon using the configuration file.
3. Run `vehicle_speed_service.py` to start the Vehicle Speed Service provider.
4. Run `cluster_client.py` to start the Instrument Cluster consumer.
5. Verify service discovery, GetSpeed responses, and SpeedChanged notifications.
6. Run the respective ECU applications to test the multi-ECU services.
7. Capture network traffic using Wireshark on the loopback interface (`lo`).

## Wireshark Analysis

Network traffic was captured and analysed using Wireshark and tcpdump.

- SOME/IP Service Discovery traffic.
- Multicast communication using `224.224.224.245:30490`.
- SOME/IP method request and response packets.
- Event notification traffic.
- VehicleSpeedService and ClimateService communication.
- SOME/IP header field analysis.
- Service ID, Method ID, Client ID, Session ID, and Message Type inspection.
- Used **Decode As** to identify UDP application traffic as SOME/IP in Wireshark.

**Capture File:** `assignment2-multi-ecu.pcapng`

## Validation & Testing

- Verified service discovery and service availability.
- Tested method calls and event subscriptions.
- Verified multiple consumers of VehicleSpeedService.
- Tested overspeed warning at speeds above 80 km/h.
- Validated accepted and rejected temperature requests.
- Tested Climate ECU shutdown and restart.
- Tested Vehicle ECU shutdown.
- Verified communication through Wireshark packet capture.
- Observed SOME/IP request-response and event notification traffic.

## Learning Outcomes

- Understanding service-oriented architecture in automotive systems.
- Practical implementation of SOME/IP communication using Python.
- Understanding service providers and service consumers.
- Working with SOME/IP Service Discovery.
- Understanding method-based and event-based communication.
- Implementing multiple service providers and consumers.
- Understanding service IDs, method IDs, event IDs, and event groups.
- Analysing SOME/IP messages and headers using Wireshark.
- Understanding service availability, failure, and recovery.
- Capturing and analysing network packets using Wireshark and tcpdump.
