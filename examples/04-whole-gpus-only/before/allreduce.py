#!/usr/bin/env python3
"""
Simulate ring AllReduce throughput under two GPU placement scenarios.

No GPU required — this is a bandwidth model to make the 40% throughput
penalty tangible when two GPUs are on different PCI switches and P2P
transfers fall back to system RAM instead of NVLink / Infinity Fabric.
"""

NVLINK_BW_GBps   = 600  # NVIDIA NVLink 4.0, bidirectional per GPU pair
INFFAB_BW_GBps   = 400  # AMD Infinity Fabric (MI300X)
SYSRAM_BW_GBps   =  50  # PCIe 4.0 x16 → system RAM (different-switch fallback)


def ring_allreduce_s(data_gb, bw_gbps, num_gpus=2):
    """Ring AllReduce: 2*(N-1)/N passes over the data at the interconnect BW."""
    passes = 2 * (num_gpus - 1) / num_gpus
    return passes * data_gb / bw_gbps


def row(label, bw, data_gb, baseline_s):
    t = ring_allreduce_s(data_gb, bw)
    slowdown = f"+{(t / baseline_s - 1) * 100:.0f}% slower" if t > baseline_s else "baseline"
    print(f"  {label:<42} {t * 1000:>7.1f} ms   {slowdown}")


data_gb = 14.0  # 7B-param model, FP16 weights

baseline = ring_allreduce_s(data_gb, NVLINK_BW_GBps)

print(f"Ring AllReduce — {data_gb:.0f} GB payload (7B model, FP16), 2 GPUs\n")
print(f"  {'Scenario':<42} {'Time':>10}   Notes")
print(f"  {'-'*42} {'-'*10}   -----")
row("Same switch — NVIDIA NVLink 4.0",    NVLINK_BW_GBps,  data_gb, baseline)
row("Same switch — AMD Infinity Fabric",  INFFAB_BW_GBps,  data_gb, baseline)
row("Different switch — system RAM",      SYSRAM_BW_GBps,  data_gb, baseline)

print()
print("The 'different switch' row is what the integer scheduler can give you.")
print("nvidia.com/gpu: 2 counts GPUs. It does not check which switch they sit on.")
