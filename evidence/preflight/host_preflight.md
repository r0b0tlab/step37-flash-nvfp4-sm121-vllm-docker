# Host Preflight — Step 3.7 Flash NVFP4 SM121 Optimization

Captured: 2026-06-03

## Node 1: r0b0t-dgx

- OS: Linux r0b0t-dgx 6.17.0-1021-nvidia #21-Ubuntu SMP PREEMPT_DYNAMIC Wed May 27 19:14:05 UTC 2026 aarch64 aarch64 aarch64 GNU/Linux
- Driver: 580.159.03
- CUDA: 13.0
- GPU: NVIDIA GB10, product architecture Blackwell
- Attached GPUs visible to nvidia-smi: 1
- System memory: 121Gi total, 87Gi available at check time
- Disk mount `/`: 3.7T total, 1.5T available at check time
- Active Docker containers: none at check time
- QSFP interfaces:
  - enp1s0f0np0: 192.168.100.10/24
  - enP2p1s0f0np0: 192.168.100.14/24

## Node 2: r0b0tdgx1 / gn100-89ac

- reachable via IP 192.168.100.11
- Hostname discovered via SSH: r0b0tdgx1
- QSFP interfaces:
  - enp1s0f0np0: 192.168.100.11/24
  - enP2p1s0f0np0: 192.168.100.15/24
- System memory: 119Gi total, 112Gi available at check time
- Disk mount `/`: 3.7T total, 2.9T available at check time
- Docker containers visible at check time: none

## Current blocking network issue

Current DNS resolution on node1 cannot resolve `gn100-89ac`:

- ping gn100-89ac: Temporary failure in name resolution
- SSH via hostname fails until host entry is added
- direct SSH via IP succeeds:

  ssh r0b0tdgx@192.168.100.11 'hostname'

## Conclusion

Dual-GB10 TP=2 prerequisites are present, except the local hostname mapping for `gn100-89ac`.

Recommended remediation:

1. Add `/etc/hosts` entries on node1:
   - 192.168.100.11 gn100-89ac r0b0tdgx1
2. Verify bidirectional fabric reachability on enp1s0f0np0.
3. Only then proceed with Ray TP=2 smoke.
