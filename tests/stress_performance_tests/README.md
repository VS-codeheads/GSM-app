# GSM JMeter Stress/Performance Tests

Single JMeter test plan with 5 scenarios targeting the Flask backend. Keep the DB seeded (products/orders present) before running writes.

## Scenarios
- **S1 Read Heavy - Catalog & Orders**: 50 users, ramp 30s, 5 min; GET `/getProducts`, `/getRecentOrders` (DB read load).
- **S2 Revenue Calc CPU**: 20 users, ramp 10s, 3 min; POST `/api/calc/revenue` (CPU + DB read for products).
- **S3 Spend Calc Longevity**: 10 users, ramp 10s, 10 min; POST `/api/calc/spend` (CPU math longevity).
- **S4 Order Create Burst**: 15 users, ramp 5s, 5 loops each; POST `/addOrder` (write path + DB stress). Adds data—run on disposable DB or clean afterward.
- **S5 Mixed Soak**: 5 users, ramp 5s, 15 min; GET `/getProducts`, POST `/api/calc/revenue`, POST `/api/calc/spend` (long-running mixed load).

## File
- `gsm_stress_plan.jmx` — contains all scenarios plus Summary Report listener.

## Quick Run (non-GUI)
```bash
# from repo root
tests/stress_performance_tests/jmeter.sh -n \
  -t tests/stress_performance_tests/gsm_stress_plan.jmx \
  -JHOST=localhost -JPORT=5000 \
  -l tests/stress_performance_tests/results.jtl
```

## Adjustable Properties (set via -Jkey=value)
- `HOST` (default: localhost)
- `PORT` (default: 5000)
- `PRODUCT_IDS` (comma list for revenue calc)
- `REVENUE_DAYS` (days parameter for revenue)
- `SPEND_YEAR`, `SPEND_MONTH` (for spend calc payloads)

## Notes
- Uses `Content-Type: application/json` and raw JSON bodies (aligned with backend parsing).
- Listener is Summary Report only to keep the plan light; add more listeners in GUI if needed.
- S4 writes orders; plan cleanup if running against shared DB.
- Timeouts: connect 5s, response 15s; adjust in HTTP Defaults.
