# Recommended Repository Structure

```text
faultline/
├── apps/
│   ├── web/                    # Next.js UI
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── public/demo/
│   │   └── tests/
│   └── api/                    # FastAPI service
│       ├── faultline_api/
│       │   ├── routes/
│       │   ├── services/
│       │   ├── adapters/
│       │   ├── schemas/
│       │   └── main.py
│       └── tests/
├── packages/
│   └── faultline_core/         # dependency-light deterministic engine
│       ├── faultline_core/
│       └── tests/
├── data/
│   ├── item_bank.json
│   ├── malrules.json
│   ├── demo_class.json
│   └── evaluation/
├── docs/
│   ├── architecture/
│   ├── evaluation/
│   ├── decisions/
│   └── pitch/
├── scripts/
│   ├── seed_demo.py
│   ├── evaluate.py
│   └── verify_submission.sh
├── .github/workflows/ci.yml
├── BUILD_LOG.md
├── README.md
├── LICENSE
└── docker-compose.yml
```

## Separation rule

The core package must not import FastAPI, database clients, or model SDKs. A judge should be able to run `pytest packages/faultline_core/tests` and see the central claim tested independently.
