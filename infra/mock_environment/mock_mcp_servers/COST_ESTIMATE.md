# Cost estimate for the mock MCP servers

A ballpark Azure cost for hosting the mock MCP servers through the LAB654 lab, using live Azure prices (East US, October 2026).

## Summary

- **Cost:** about **$15 (₹1,450)** in the lab month with the current setup, where servers scale to zero when idle. Keeping every server warm all month costs about **$97 (₹9,300)**.
- **Traffic:** about **150,000 tool calls** across all four labs, including a 5× buffer.
- **Capacity:** one replica of each server handles the expected peak load several times over.
- **Trade-off:** with scale to zero, the first call after an idle spell takes 5 to 15 seconds while a replica starts.

## Assumptions

| Item | Value |
|---|---|
| Labs | 4 sessions of about 75 minutes |
| Attendees per lab | 100 |
| Scenarios per attendee | 3 (finance, legal, productivity) |
| Tool calls per scenario | 25. The recorded finance run made 20 |
| Buffer | 5× for attendees exploring beyond the script |
| HTTP requests per tool call | 2, to cover connection setup |
| Servers | 7 in total: 3 finance plus about 4 for legal and productivity |
| Server size | 0.5 vCPU and 1 GiB memory, 0 to 3 replicas |
| Exchange rate | ₹96 to $1, the rate in Azure's own price list |

## Expected traffic

| Measure | Without buffer | With 5× buffer |
|---|---|---|
| Tool calls per attendee | 75 | 375 |
| Tool calls per lab | 7,500 | 37,500 |
| Tool calls across 4 labs | 30,000 | 150,000 |
| HTTP requests across 4 labs | 60,000 | 300,000 |
| Average load during a lab, all servers | 3 requests/s | 17 requests/s |

## How Azure charges

Azure Container Apps (consumption plan) bills by time and by requests, not by tool call.

| Meter | Price | Notes |
|---|---|---|
| vCPU, active | $0.000024 per vCPU-second | While a replica is serving requests |
| vCPU, idle | $0.000003 per vCPU-second | A warm replica with no traffic |
| Memory, active or idle | $0.000003 per GiB-second | Whenever a replica is running |
| Requests | $0.40 per million | |
| Container registry (Basic) | $0.167 per day, about $5 a month | One registry shared by all servers |
| Log Analytics | First 5 GB a month free | These servers log well under 1 GB |

What this means per server, at 0.5 vCPU and 1 GiB:

| State | Cost |
|---|---|
| Kept warm, no traffic | $0.39 a day, $11.66 a month |
| Busy, for each replica | $0.054 an hour |
| Scaled to zero | $0 |

The monthly free allowance (180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests) is left out of these figures. It would lower the cost a little further.

## Cost by option

| Option | What runs when | Cost in lab month | Cost in other months |
|---|---|---|---|
| **A. Scale to zero (current)** | Replicas start on demand, stop when idle | **$15 (₹1,450)** | about $6 |
| B. Warm during lab week | Scale to zero, plus 1 warm replica each for the 7 days of lab week | $35 (₹3,400) | about $6 |
| C. Always warm | 1 warm replica per server all month | $97 (₹9,300) | about $88 |

Every option includes a worst case for the four labs: all 7 servers at 3 replicas for 2 hours each, about $9. The requests themselves cost about $0.12.

### Breakdown of option A

| Item | Cost |
|---|---|
| Four labs at worst-case scale | $9.07 |
| Container registry | $5.00 |
| Logs, requests and testing | $1.12 |
| **Total** | **$15.19** |

## Capacity

- **Load test:** one replica of `mock-lseg` handled **70 to 80 requests/s** with no errors. Median latency was 200 to 600 ms from India to East US.
- **Need:** about 17 requests/s on average across all servers during a lab, or roughly 50 requests/s at a 3× peak. That works out to under 10 requests/s for any one server.
- **Verdict:** one replica per server is enough. Up to 3 replicas is a safety margin.
