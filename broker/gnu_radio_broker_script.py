#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GNU Radio ZMQ Broker for Multi-UE/Multi-gNB srsRAN scenarios.
This broker acts as a virtual RF channel that:
- DOWNLINK: Receives signal from gNB(s) and distributes to all UEs.
- UPLINK: Receives signals from all UEs, sums them and sends to gNB(s).
"""
import argparse
import json
import sys
import signal
from gnuradio import gr, blocks, zeromq

def gnb_ports(n: int):
    """
    Docstring for gnb_ports
    
    :param n: gNB id starting by 1
    :type n: int
    return: (tx_port, rx_port)
    TX=2000+(n-1)*1000
    RX=2001+(n-1)*1000
    """
    base = 2000 + (n-1) * 1000
    return base, base+1

def ue_ports(gnb_n: int, ue_m: int):
    rx = 2100 + (gnb_n - 1) * 1000 + (ue_m - 1) * 100
    return rx, rx + 1



def db_to_lin_ampl(db: float) -> float:
    """dB (amplitud) -> factor lineal (amplitud). Path loss: factor < 1."""
    return 10 ** (-db / 20.0)

def zmq_addr(host: str, port: int) -> str:
    return f"tcp://{host}:{port}"

class MultiUEBroker(gr.top_block):
    """
    Broker ZMQ multi-gNB / multi-UE.

    """
    
    def __init__(self, config: dict):
        super().__init__("Multi-UE/Multi-gNB ZMQ Broker", catch_exceptions= True)
        
        # Base parameters
        self.samp_rate = float(config.get('samp_rate', 11_520_000))
        self.zmq_timeout = int(config.get('zmq_timeout', 100))
        self.zmq_hwm = int(config.get('zmq_hwm', -1))
        
        # Host binding
        self.bind_addr = config.get("bind_addr", config.get("bind_addr_ip", "0.0.0.0"))
        
        # Host peer address
        self.peer_addr = config.get("peer_addr", config.get("peer_addr_ip", "127.0.0.1"))
        
        self.gnbs = config.get("gnbs", [{"id": 1, "ues": [{"id": 1, "path_loss_db": 0}]}])
        
        
        # Keep blocks references
        self._req_sources = []
        self._rep_sinks = []
        self._misc_blocks = []
        
        self._build()
        
    def _make_pull_source(self, addr: str):
        b = zeromq.pull_source(
            gr.sizeof_gr_complex, 1, addr,
            self.zmq_timeout, False, self.zmq_hwm
        )
        self._req_sources.append(b)
        return b

    def _make_push_sink(self, addr: str):
        b = zeromq.push_sink(
            gr.sizeof_gr_complex, 1, addr,
            self.zmq_timeout, False, self.zmq_hwm
        )
        self._rep_sinks.append(b)
        return b


    def _chain_sum(self, streams):
        """
        Sum N complex streams using a cascade of 2-input adders.
        Returns the last block (summed output).
        """
        if not streams:
            return None
        if len(streams) == 1:
            return streams[0]

        # Primer adder suma stream0 + stream1
        add = blocks.add_cc()
        self._misc_blocks.append(add)
        self.connect(streams[0], (add, 0))
        self.connect(streams[1], (add, 1))
        acc = add

        # Then cascade: (acc + stream_i)
        for i in range(2, len(streams)):
            add_next = blocks.add_cc()
            self._misc_blocks.append(add_next)
            self.connect(acc, (add_next, 0))
            self.connect(streams[i], (add_next, 1))
            acc = add_next
        
        return acc
            
    def _build(self):
        for gnb in self.gnbs:
            gnb_id = int(gnb["id"])
            ues = gnb.get("ues", [])
            gnb_tx_port, gnb_rx_port = gnb_ports(gnb_id)

            print(f"[INFO] gNB{gnb_id}: TX={gnb_tx_port} RX={gnb_rx_port} | UEs={len(ues)}")

            # -------------------------
            # DOWNLINK: gNB TX -> UEs RX
            # -------------------------
            gnb_tx_in = self._make_pull_source(zmq_addr(self.peer_addr, gnb_tx_port))

            throttle = blocks.throttle(gr.sizeof_gr_complex, self.samp_rate, True)
            self._misc_blocks.append(throttle)
            self.connect(gnb_tx_in, throttle)

            for ue in ues:
                ue_id = int(ue["id"])
                pl_db = float(ue.get("path_loss_db", 0.0))
                pl = db_to_lin_ampl(pl_db)

                ue_rx_port, ue_tx_port = ue_ports(gnb_id, ue_id)

                # DL pathloss
                dl_pl = blocks.multiply_const_cc(pl)
                self._misc_blocks.append(dl_pl)

                ue_rx_out = self._make_push_sink(zmq_addr(self.bind_addr, ue_rx_port))

                self.connect(throttle, dl_pl, ue_rx_out)

                print(f"  [DL] gNB{gnb_id}:{gnb_tx_port} -> UE{ue_id}:{ue_rx_port}  (PL={pl_db} dB)")

            # -------------------------
            # UPLINK: UEs TX -> gNB RX (sum)
            # -------------------------
            ul_streams = []
            for ue in ues:
                ue_id = int(ue["id"])
                pl_db = float(ue.get("path_loss_db", 0.0))
                pl = db_to_lin_ampl(pl_db)

                ue_rx_port, ue_tx_port = ue_ports(gnb_id, ue_id)

                ue_tx_in = self._make_pull_source(zmq_addr(self.peer_addr, ue_tx_port))

                ul_pl = blocks.multiply_const_cc(pl)
                self._misc_blocks.append(ul_pl)

                self.connect(ue_tx_in, ul_pl)
                ul_streams.append(ul_pl)

                print(f"  [UL] UE{ue_id}:{ue_tx_port} -> gNB{gnb_id}:{gnb_rx_port} (PL={pl_db} dB)")

            if ul_streams:
                summed = self._chain_sum(ul_streams)
                gnb_rx_out = self._make_push_sink(zmq_addr(self.bind_addr, gnb_rx_port))
                self.connect(summed, gnb_rx_out)
                print(f"  [UL] SUM -> gNB{gnb_id} RX:{gnb_rx_port}")

def load_config(path: str) -> dict:
    """Load JSON configuration from file."""
    with open(path, 'r') as f:
        return json.load(f)
        
def default_config(num_gnbs=1, ues_per_gnb=2):
    cfg = {
        "samp_rate": 11520000,
        "zmq_timeout": 100,
        "zmq_hwm": -1,
        "bind_addr": "0.0.0.0",
        "peer_addr": "127.0.0.1",
        "gnbs": []
    }
    for g in range(1, num_gnbs + 1):
        gn = {"id": g, "ues": []}
        for u in range(1, ues_per_gnb + 1):
            gn["ues"].append({"id": u, "path_loss_db": (u - 1) * 10})
        cfg["gnbs"].append(gn)
    return cfg

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-c", "--config", help="JSON config path")
    p.add_argument("-g", "--gnbs", type=int, default=1)
    p.add_argument("-u", "--ues", type=int, default=2)
    p.add_argument("--bind", default="0.0.0.0", help="host para rep_sink (bind)")
    p.add_argument("--peer", default="127.0.0.1", help="host al que conectan los req_source")
    p.add_argument("--gen", help="Generar config JSON y salir")
    args = p.parse_args()

    if args.gen:
        cfg = default_config(args.gnbs, args.ues)
        cfg["bind_addr"] = args.bind
        cfg["peer_addr"] = args.peer
        with open(args.gen, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"[OK] Config generado en: {args.gen}")
        return 0

    cfg = load_config(args.config) if args.config else default_config(args.gnbs, args.ues)
    cfg["bind_addr"] = args.bind
    cfg["peer_addr"] = args.peer

    tb = MultiUEBroker(cfg)

    def handler(sig, frame):
        print("\n[INFO] Stopping...")
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    print("[INFO] Starting...")
    tb.start()
    tb.wait()
    return 0


if __name__ == "__main__":
    sys.exit(main())
