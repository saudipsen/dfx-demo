import json
import os
from typing import Any


def deterministic_summary(summaries: list[dict[str, Any]]) -> str:
    rows = sum(item["row_count"] for item in summaries)
    null_cells = sum(item["null_cells"] for item in summaries)
    return (
        f"The two workbooks contain {rows} combined rows and {null_cells} null cells. "
        "The detailed per-file totals are included below."
    )


async def summarize_report(summaries: list[dict[str, Any]]) -> str:
    prompt = (
        "Summarize this ETL result in three concise sentences for a business report. "
        "Mention total rows, data quality, and notable numeric totals.\n"
        + json.dumps(summaries, indent=2)
    )
    try:
        from agent_framework import Agent
        from agent_framework.openai import OpenAIChatClient

        chat_client = OpenAIChatClient(
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
        agent = Agent(
            client=chat_client,
            instructions="You write concise, factual ETL summary paragraphs.",
        )
        response = await agent.run(prompt)
        text = getattr(response, "text", None)
        if text:
            return text
    except Exception:
        if os.getenv("AGENT_REQUIRED", "false").lower() == "true":
            raise
    return deterministic_summary(summaries)