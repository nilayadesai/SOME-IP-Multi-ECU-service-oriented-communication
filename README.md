# SOME/IP Multi-ECU Service-Oriented Vehicle System

## Overview

This project focuses on implementing service-oriented communication between multiple virtual Electronic Control Units (ECUs) using SOME/IP (Scalable Service-Oriented Middleware over IP).

The system consists of four virtual ECUs: Vehicle ECU, Instrument Cluster ECU, Climate ECU, and Central Display ECU. Each ECU runs as a separate Python application in a Linux (Ubuntu) environment using the `someipy` library.

The Vehicle ECU provides vehicle speed information, while the Climate ECU provides cabin temperature information through separate SOME/IP services. The Instrument Cluster ECU consumes vehicle speed data, whereas the Central Display ECU consumes services from both providers.

The project demonstrates Service Discovery, method calls, event notifications, event-group subscriptions, multiple service consumers, service failure and recovery, and network traffic analysis using Wireshark.

## Technologies Used

- Python
- Linux (Ubuntu)
- SOME/IP Protocol
- someipy Library
- SOME/IP Service Discovery
- UDP Communication
- Wireshark
- Linux Terminal

## System Components

| ECU | Role | Service |
|-----|------|---------|
| Vehicle ECU | Service Provider | VehicleSpeedService |
| Instrument Cluster ECU | Service Consumer | VehicleSpeedService |
| Climate ECU | Service Provider | ClimateService |
| Central Display ECU | Service Consumer | VehicleSpeedService and ClimateService |

## SOME/IP Services

### VehicleSpeedService

- **Service ID:** `0x1234`
- **Instance ID:** `0x5678`

| Element | Type | ID |
|---------|------|----|
| GetSpeed() | Method | `0x0001` |
| GetVehicleState() | Method | `0x0002` |
| SpeedChanged | Event | `0x8001` |
| OverspeedWarning | Event | `0x8002` |

### ClimateService

- **Service ID:** `0x2234`
- **Instance ID:** `0x0001`

| Element | Type | ID |
|---------|------|----|
| GetCabinTemperature() | Method | `0x0001` |
| SetTargetTemperature() | Method | `0x0002` |
| CabinTemperatureChanged | Event | `0x8001` |

## Key Features

- Communication between four independent virtual ECUs.
- SOME/IP Service Discovery and service availability checking.
- Method-based request and response communication.
- Event-based notification and event-group subscription.
- Multiple consumers receiving data from a single service.
- Central Display consuming multiple services.
- Overspeed warning triggered when vehicle speed exceeds 80 km/h.
- Cabin temperature monitoring and target temperature validation.
- Service failure and recovery testing.

## Climate Temperature Validation

The `SetTargetTemperature()` method validates requested temperature values.

| Requested Temperature | Result |
|-----------------------|--------|
| 16.0 °C | ACCEPTED |
| 22.0 °C | ACCEPTED |
| 30.0 °C | ACCEPTED |
| 10.0 °C | REJECTED |
| 35.0 °C | REJECTED |

Invalid temperature requests return `INVALID_TEMPERATURE`.

## Wireshark Analysis

Network traffic was captured and analysed using Wireshark.

- SOME/IP Service Discovery traffic.
- Multicast communication using `224.224.224.245:30490`.
- SOME/IP method request and response packets.
- Event notification traffic.
- SOME/IP header field analysis.
- Service ID, Method ID, Client ID, Session ID, and Message Type inspection.

**Capture File:** `assignment2-multi-ecu.pcapng`

## Validation & Testing

- Verified service discovery and availability.
- Tested method calls and event subscriptions.
- Verified multiple consumers of VehicleSpeedService.
- Tested overspeed warning at speeds above 80 km/h.
- Validated accepted and rejected temperature requests.
- Tested Climate ECU shutdown and restart.
- Tested Vehicle ECU shutdown.
- Verified communication through Wireshark packet capture.

## Learning Outcomes

- Understanding service-oriented architecture in automotive systems.
- Practical implementation of SOME/IP communication.
- Understanding service discovery, methods, events, and subscriptions.
- Working with multiple service providers and consumers.
- Analysing SOME/IP messages and headers using Wireshark.
- Understanding service availability, failure, and recovery.

