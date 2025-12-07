# Open5GS and srsRAN 5G SA Deployment (Docker)

This repository provides a containerized deployment of a **5G Standalone (SA)** network using **Open5GS** as the Core Network and **srsRAN Project** for the RAN (gNB and UE) with ZMQ simulation.

## Architecture

- **5G Core**: Open5GS (AMF, SMF, UPF, NRF, UDR, UDM, AUSF, NSSF, BSF, PCF, SCP)
- **RAN**: srsRAN Project gNB (ZMQ)
- **UE**: srsRAN Project UE (ZMQ)
- **Monitoring**: Prometheus and Grafana

## Prerequisites

- Linux OS (Ubuntu 22.04 recommended) 
    - Not tested on other operating systems
- Docker and Docker Compose

## Prepare Docker Images

You can either pull pre-built images or build them from source.

### Option A: Pull Pre-built Images
```bash
# Open5GS and Monitoring
docker pull ghcr.io/herlesupreeth/docker_open5gs:master
docker tag ghcr.io/herlesupreeth/docker_open5gs:master docker_open5gs

docker pull ghcr.io/herlesupreeth/docker_grafana:master
docker tag ghcr.io/herlesupreeth/docker_grafana:master docker_grafana

docker pull ghcr.io/herlesupreeth/docker_metrics:master
docker tag ghcr.io/herlesupreeth/docker_metrics:master docker_metrics

# srsRAN Components
docker pull ghcr.io/herlesupreeth/docker_srslte:master
docker tag ghcr.io/herlesupreeth/docker_srslte:master docker_srslte

docker pull ghcr.io/herlesupreeth/docker_srsran:master
docker tag ghcr.io/herlesupreeth/docker_srsran:master docker_srsran
```

### Option B: Build from Source
```bash
# Build Open5GS base image
cd base
docker build --no-cache --force-rm -t docker_open5gs .

# Build srsRAN 4G (for UE)
cd ../srslte
docker build --no-cache --force-rm -t docker_srslte .

# Build srsRAN Project (for gNB)
cd ../srsran
docker build --no-cache --force-rm -t docker_srsran .

cd ..
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/HectorND15/docker_open5gs_arm
cd docker_open5gs_arm
```

### 2. Configure Environment
Check the `.env` file to ensure the IP addresses and subscriber credentials match your requirements.
- **Subscriber**:
  - IMSI: `001011234567895`
  - Key: `8baf473f2f8fd09487cccbd7097c6862`
  - OP: `11111111111111111111111111111111`

### 3. Deploy the Network

**Step 1: Start the 5G Core**
```bash
docker compose -f sa-deploy.yaml up -d
```
*Wait for the Core Network components (especially UDR, UDM, AMF) to fully initialize and register with the NRF.*

**Step 2: Start the gNB**
```bash
docker compose -f srsgnb_zmq.yaml up -d
```

**Step 3: Start the UE**
```bash
docker compose -f srsue_5g_zmq.yaml up -d
```

### 4. Troubleshooting & Success Factors

To ensure the UE successfully attaches and connects to the internet:

1. **Strict Startup Order**:
   - The **5G Core** must be fully initialized before starting the RAN. If the AMF/UDM/UDR are not ready, the UE registration will fail with "Unknown UE" or "Gateway Timeout".
   - The **gNB** must be started before the **UE** to establish the ZMQ connection correctly.

2. **Subscriber Provisioning**:
   - The subscriber with IMSI `001011234567895` is pre-provisioned in the MongoDB. Ensure your `.env` file matches these credentials.
   - If you see "Unknown UE by SUCI", check the AMF logs. If the Core was just started, it might be a race condition—restart the UE.

3. **Internet Access**:
   - The UE creates a tunnel interface (`tun_srsue`).
   - Successful attachment is indicated by `PDU Session Establishment successful` in the UE logs.
   - You can verify internet access by pinging an external IP (e.g., `8.8.8.8`) through this interface.

### 5. Verification

**Check Logs**
```bash
docker logs -f amf
docker logs -f srsgnb_zmq
docker logs -f srsue_5g_zmq
```

**Test Connectivity**
Ping the UPF or external network from the UE container:
```bash
docker exec srsue_5g_zmq ping -I tun_srsue -c 4 8.8.8.8
```

## Accessing Interfaces

- **Open5GS WebUI**: http://<DOCKER_HOST_IP>:9999 (admin / 1423)
- **Grafana**: http://<DOCKER_HOST_IP>:3000 (admin / admin)

## Directory Structure

- `base/`: Dockerfiles for base images
- `srslte/`: Configuration for srsUE (4G/5G)
- `srsran/`: Configuration for srsgNB
- `*_deploy.yaml`: Docker Compose deployment files

## Acknowledgements

This repository is a simplified fork of [docker_open5gs](https://github.com/herlesupreeth/docker_open5gs) by [Herle Supreeth](https://github.com/herlesupreeth).

The original repository provides a comprehensive suite of Docker files for deploying:
- **4G/5G Core Networks** (Open5GS)
- **IMS** (Kamailio, OpenSIPS)
- **RAN** (srsRAN 4G/5G, UERANSIM)
- **Monitoring Tools**

This fork focuses specifically on a streamlined **5G Standalone (SA)** deployment for educational and testing purposes on ARM/x86 architectures. We thank the original authors for their extensive work in containerizing these complex network components.
