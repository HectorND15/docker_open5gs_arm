# docker_open5gs
Quite contrary to the name of the repository, this repository contains docker files to deploy an Over-The-Air (OTA) or RF simulated 4G/5G network using following projects:
- Core Network (4G/5G) - open5gs - https://github.com/open5gs/open5gs
- IMS (VoLTE + VoNR) - kamailio - https://github.com/kamailio/kamailio
- IMS HSS - https://github.com/nickvsnetworking/pyhss
- Osmocom HLR - https://github.com/osmocom/osmo-hlr
- Osmocom MSC - https://github.com/osmocom/osmo-msc
- srsRAN_4G (4G eNB + 4G UE + 5G UE) - https://github.com/srsran/srsRAN_4G
- srsRAN_Project (5G gNB) - https://github.com/srsran/srsRAN_Project
- UERANSIM (5G gNB + 5G UE) - https://github.com/aligungr/UERANSIM
- eUPF (5G UPF) - https://github.com/edgecomllc/eupf
- OpenSIPS IMS - https://github.com/OpenSIPS/opensips
- Sigscale OCS - https://github.com/sigscale/ocs
- Osmo-epdg + Strongswan-epdg
  - https://gitea.osmocom.org/erlang/osmo-epdg
  - https://gitea.osmocom.org/ims-volte-vowifi/strongswan-epdg
- SWu-IKEv2 - https://github.com/fasferraz/SWu-IKEv2

## Table of Contents

- [Tested Setup](#tested-setup)
- [Prepare Docker images](#prepare-docker-images)
  - [Get Pre-built Docker images](#get-pre-built-docker-images)
  - [Build Docker images from source](#build-docker-images-from-source)
- [Network and deployment configuration](#network-and-deployment-configuration)
  - [Single Host setup configuration](#single-host-setup-configuration)
  - [Multihost setup configuration](#multihost-setup-configuration)
    - [4G deployment](#4g-deployment)
    - [5G SA deployment](#5g-sa-deployment)
- [Network Deployment](#network-deployment)
- [Docker Compose files overview](#docker-compose-files-overview)
- [Provisioning of SIM information](#provisioning-of-sim-information)
  - [Provisioning of SIM information in open5gs HSS](#provisioning-of-sim-information-in-open5gs-hss-as-follows)
  - [Provisioning of IMSI and MSISDN with OsmoHLR](#provisioning-of-imsi-and-msisdn-with-osmohlr-as-follows)
  - [Provisioning of SIM information in pyHSS](#provisioning-of-sim-information-in-pyhss-is-as-follows)
  - [Provisioning of Diameter Peer + Subscriber information in Sigscale OCS](#provisioning-of-diameter-peer--subscriber-information-in-sigscale-ocs-as-follows-skip-if-ocs-is-not-deployed)
- [Testing VoWiFi with COTS UE](#testing-vowifi-with-cots-ue)
  - [Pre-requisites](#pre-requisites)
  - [Deploy the required components](#deploy-the-required-components)
  - [Provision SIM and IMS subscriber information](#provision-sim-and-ims-subscriber-information)
  - [Manually configure DNS settings on your phone (WiFi connection)](#manually-configure-dns-settings-on-your-phone-wifi-connection)
  - [UE configuration](#ue-configuration)
- [Not supported](#not-supported)

## Tested Setup

Docker host machine

- Ubuntu 22.04 or above

Over-The-Air setups: 

- srsRAN_Project gNB using Ettus USRP B210
- srsRAN_Project (5G gNB) using LibreSDR (USRP B210 clone)
- srsRAN_4G eNB using LimeSDR Mini v1.3
- srsRAN_4G eNB using LimeSDR-USB
- srsRAN_4G eNB using LibreSDR (USRP B210 clone)

RF simulated setups:

- srsRAN_4G (eNB + UE) simulation over ZMQ
- srsRAN_Project (5G gNB) + srsRAN_4G (5G UE) simulation over ZMQ
- UERANSIM (gNB + UE) simulator

## Prepare Docker images

* Mandatory requirements:
	* [docker-ce](https://docs.docker.com/install/linux/docker-ce/ubuntu) - Version 22.0.5 or above
	* [docker compose](https://docs.docker.com/compose) - Version 2.14 or above

You can either pull the pre-built docker images or build them from the source.

### Get Pre-built Docker images

Pull base images:
```
docker pull ghcr.io/herlesupreeth/docker_open5gs:master
docker tag ghcr.io/herlesupreeth/docker_open5gs:master docker_open5gs

docker pull ghcr.io/herlesupreeth/docker_grafana:master
docker tag ghcr.io/herlesupreeth/docker_grafana:master docker_grafana

docker pull ghcr.io/herlesupreeth/docker_metrics:master
docker tag ghcr.io/herlesupreeth/docker_metrics:master docker_metrics
```

You can also pull the pre-built images for additional components

For IMS components:
```
docker pull ghcr.io/herlesupreeth/docker_osmohlr:master
docker tag ghcr.io/herlesupreeth/docker_osmohlr:master docker_osmohlr

docker pull ghcr.io/herlesupreeth/docker_osmomsc:master
docker tag ghcr.io/herlesupreeth/docker_osmomsc:master docker_osmomsc

docker pull ghcr.io/herlesupreeth/docker_pyhss:master
docker tag ghcr.io/herlesupreeth/docker_pyhss:master docker_pyhss

docker pull ghcr.io/herlesupreeth/docker_kamailio:master
docker tag ghcr.io/herlesupreeth/docker_kamailio:master docker_kamailio

docker pull ghcr.io/herlesupreeth/docker_mysql:master
docker tag ghcr.io/herlesupreeth/docker_mysql:master docker_mysql

docker pull ghcr.io/herlesupreeth/docker_opensips:master
docker tag ghcr.io/herlesupreeth/docker_opensips:master docker_opensips
```

For srsRAN components:
```
docker pull ghcr.io/herlesupreeth/docker_srslte:master
docker tag ghcr.io/herlesupreeth/docker_srslte:master docker_srslte

docker pull ghcr.io/herlesupreeth/docker_srsran:master
docker tag ghcr.io/herlesupreeth/docker_srsran:master docker_srsran
```

For UERANSIM components:
```
docker pull ghcr.io/herlesupreeth/docker_ueransim:master
docker tag ghcr.io/herlesupreeth/docker_ueransim:master docker_ueransim
```

For EUPF component:
```
docker pull ghcr.io/herlesupreeth/docker_eupf:master
docker tag ghcr.io/herlesupreeth/docker_eupf:master docker_eupf
```

For Sigscale OCS component:
```
docker pull ghcr.io/herlesupreeth/docker_ocs:master
docker tag ghcr.io/herlesupreeth/docker_ocs:master docker_ocs
```

For Osmo-epdg + Strongswan-epdg component:
```
docker pull ghcr.io/herlesupreeth/docker_osmoepdg:master
docker tag ghcr.io/herlesupreeth/docker_osmoepdg:master docker_osmoepdg
```

For SWu-IKEv2 component:
```
docker pull ghcr.io/herlesupreeth/docker_swu_client:master
docker tag ghcr.io/herlesupreeth/docker_swu_client:master docker_swu_client
```

### Build Docker images from source
#### Clone repository and build base docker image of open5gs, kamailio, srsRAN_4G, srsRAN_Project, ueransim

```
# Build docker image for open5gs EPC/5GC components
git clone https://github.com/herlesupreeth/docker_open5gs
cd docker_open5gs/base
docker build --no-cache --force-rm -t docker_open5gs .

# Build docker image for kamailio IMS components
cd ../ims_base
docker build --no-cache --force-rm -t docker_kamailio .

# Build docker image for srsRAN_4G eNB + srsUE (4G+5G)
cd ../srslte
docker build --no-cache --force-rm -t docker_srslte .

# Build docker image for srsRAN_Project gNB
cd ../srsran
docker build --no-cache --force-rm -t docker_srsran .

# Build docker image for UERANSIM (gNB + UE)
cd ../ueransim
docker build --no-cache --force-rm -t docker_ueransim .

# Build docker image for EUPF
cd ../eupf
docker build --no-cache --force-rm -t docker_eupf .

# Build docker image for OpenSIPS IMS
cd ../opensips_ims_base
docker build --no-cache --force-rm -t docker_opensips .

# Build docker image for Osmo-epdg + Strongswan-epdg
cd ../osmoepdg
docker build --no-cache --force-rm -t docker_osmoepdg .

# Build docker image for SWu-IKEv2
cd ../swu_client
docker build --no-cache --force-rm -t docker_swu_client .
```

#### Build docker images for additional components

```
cd ..
set -a
source .env
set +a
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo cpupower frequency-set -g performance

# For 4G deployment only
docker compose -f 4g-volte-deploy.yaml build

# For 5G deployment only
docker compose -f sa-deploy.yaml build
```

## Network and deployment configuration

The setup can be mainly deployed in two ways:

1. Single host setup where eNB/gNB and (EPC+IMS)/5GC are deployed on a single host machine
2. Multi host setup where eNB/gNB is deployed on a separate host machine than (EPC+IMS)/5GC

### Single Host setup configuration
Edit only the following parameters in **.env** as per your setup

```
MCC
MNC
DOCKER_HOST_IP --> This is the IP address of the host running your docker setup
UE_IPV4_INTERNET --> Change this to your desired (Not conflicted) UE network ip range for internet APN
UE_IPV4_IMS --> Change this to your desired (Not conflicted) UE network ip range for ims APN
```

### Multihost setup configuration

#### 4G deployment

###### On the host running the (EPC+IMS)

Edit only the following parameters in **.env** as per your setup
```
MCC
MNC
DOCKER_HOST_IP --> This is the IP address of the host running (EPC+IMS)
SGWU_ADVERTISE_IP --> Change this to value of DOCKER_HOST_IP
UE_IPV4_INTERNET --> Change this to your desired (Not conflicted) UE network ip range for internet APN
UE_IPV4_IMS --> Change this to your desired (Not conflicted) UE network ip range for ims APN
```

Under **mme** section in docker compose file (**4g-volte-deploy.yaml**), uncomment the following part
```
...
    # ports:
    #   - "36412:36412/sctp"
...
```

Then, uncomment the following part under **sgwu** section
```
...
    # ports:
    #   - "2152:2152/udp"
...
```

###### On the host running the eNB

Edit only the following parameters in **.env** as per your setup
```
MCC
MNC
DOCKER_HOST_IP --> This is the IP address of the host running eNB
MME_IP --> Change this to IP address of host running (EPC+IMS)
SRS_ENB_IP --> Change this to the IP address of the host running eNB
```

Replace the following part in the docker compose file (**srsenb.yaml**)
```
    networks:
      default:
        ipv4_address: ${SRS_ENB_IP}
networks:
  default:
    external:
      name: docker_open5gs_default
```
with 
```
	network_mode: host
```

#### 5G SA deployment

###### On the host running the 5GC

Edit only the following parameters in **.env** as per your setup
```
MCC
MNC
DOCKER_HOST_IP --> This is the IP address of the host running 5GC
UPF_ADVERTISE_IP --> Change this to value of DOCKER_HOST_IP
UE_IPV4_INTERNET --> Change this to your desired (Not conflicted) UE network ip range for internet APN
UE_IPV4_IMS --> Change this to your desired (Not conflicted) UE network ip range for ims APN
```

Under **amf** section in docker compose file (**sa-deploy.yaml**), uncomment the following part
```
...
    # ports:
    #   - "38412:38412/sctp"
...
```

Then, uncomment the following part under **upf** section
```
...
    # ports:
    #   - "2152:2152/udp"
...
```

###### On the host running the gNB

Edit only the following parameters in **.env** as per your setup
```
MCC
MNC
DOCKER_HOST_IP --> This is the IP address of the host running gNB
AMF_IP --> Change this to IP address of host running 5GC
SRS_GNB_IP --> Change this to the IP address of the host running gNB
```

Replace the following part in the docker compose file (**srsgnb.yaml**)
```
    networks:
      default:
        ipv4_address: ${SRS_GNB_IP}
networks:
  default:
    external: true
    name: docker_open5gs_default
```
with 
```
	network_mode: host
```

## Network Deployment

###### 4G deployment

```
# 4G Core Network + IMS + SMS over SGs (uses Kamailio IMS)
docker compose -f 4g-volte-deploy.yaml up

# 4G Core Network + IMS + SMS over SGs (uses openSIPS IMS)
docker compose -f 4g-volte-opensips-ims-deploy.yaml up

# srsRAN eNB using SDR (OTA)
docker compose -f srsenb.yaml up -d && docker container attach srsenb

# Open5GS and srsRAN 5G SA Deployment (Docker)

This repository provides a containerized deployment of a **5G Standalone (SA)** network using **Open5GS** as the Core Network and **srsRAN Project** for the RAN (gNB and UE) with ZMQ simulation.

## Architecture

- **5G Core**: Open5GS (AMF, SMF, UPF, NRF, UDR, UDM, AUSF, NSSF, BSF, PCF, SCP)
- **RAN**: srsRAN Project gNB (ZMQ)
- **UE**: srsRAN Project UE (ZMQ)
- **Monitoring**: Prometheus and Grafana

## Prerequisites

- Linux OS (Ubuntu 22.04 recommended)
- Docker and Docker Compose
- AVX2 supported CPU (for srsRAN)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
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

### 4. Verification

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

