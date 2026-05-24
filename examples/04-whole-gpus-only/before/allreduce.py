#!/usr/bin/env python3
"""
Purpose
-------
The core problem in Pain 4 is that two GPUs on different PCI switches fall
back to system RAM for peer-to-peer transfers, costing ~40% throughput on
every collective operation during training. A Kind cluster with fake GPU
labels cannot show this: pods schedule and run fine, the CPU workload
completes normally, and nothing looks wrong.

This script fills that gap. It simulates a ring AllReduce over a 14 GB
payload (7B model in FP16) at three bandwidth tiers and prints the wall-time
comparison. The "different switch — system RAM" row is what the integer
scheduler silently produces when `nvidia.com/gpu: 2` lands on a node where
the two GPUs are on separate switches. That penalty is paid on every gradient
sync step during training.

No GPU, no cluster, no packages required — just Python 3.
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
