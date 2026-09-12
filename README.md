# Durable Excel ETL

Python Azure Durable Functions orchestration that reads exactly two Excel workbooks, normalizes them in parallel, and writes a Word report. Durable orchestration history is stored in the local Durable Task Scheduler emulator. The fan-out is `normalize_excel_file`; the fan-in is `create_word_report`.

## Run locally

1. Install Azure Functions Core Tools, Azurite, and Python 3.10+.
2. Create a virtual environment and install `requirements.txt`.
3. Copy `local.settings.json.example` to `local.settings.json`.
4. Put exactly two `.xlsx` or `.xlsm` files in `data/incoming`.
5. Start the Durable Task Scheduler emulator on `http://localhost:8080`.
6. Run `func start` or use the VS Code debug configuration.

The Durable Task Scheduler emulator is the orchestration backend, not an Excel transformation HTTP endpoint. Excel normalization runs locally by default. Set `DTS_NORMALIZATION_URL` only when a separate transformer service exposes the configured normalization route.

Start an instance:

```powershell
Invoke-RestMethod -Method Post http://localhost:7071/api/etl/start -ContentType 'application/json' -Body '{}'
```

The response contains Durable status URLs. Cancel and erase an instance:

```powershell
Invoke-RestMethod -Method Post http://localhost:7071/api/etl/cancel/<instance-id>
```

Cancellation terminates the instance and starts a cleanup orchestration that erases input, output, and working data. Set `DTS_REQUIRED=true` or `AGENT_REQUIRED=true` when fallback behavior is not acceptable.