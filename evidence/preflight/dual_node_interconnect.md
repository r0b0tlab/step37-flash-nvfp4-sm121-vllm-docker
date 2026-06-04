# Dual-Node Interconnect — Step 3.7 Flash NVFP4 SM121 Optimization

Captured: 2026-06-03

## Intended interface pinning

Planned TP=2 Ray interface pinning:

- GLOO_SOCKET_IFNAME=enp1s0f0np0
- TP_SOCKET_IFNAME=enp1s0f0np0
- NCCL_SOCKET_IFNAME=enp1s0f0np0

## Observed node1 addresses

- enp1s0f0np0: 192.168.100.10/24
- enP2p1s0f0np0: 192.168.100.14/24

## Observed node2 addresses

- enp1s0f0np0: 192.168.100.11/24
- enP2p1s0f0np0: 192.168.100.15/24

## Evidence

SSH reachability was confirmed by IP address only:

```bash
ssh r0b0tdgx@192.168.100.11 'hostname; ip -brief addr'
```

Hostname reachability failed until hosts mapping was added.

## Current recommendation

Use 192.168.100.10 <-> 192.168.100.11 for the primary dual-node Ray path once hostname mapping is present.
