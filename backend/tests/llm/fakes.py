from dicrates.llm.call_log import LlmCallRecord


class InMemoryLlmCallLog:
    def __init__(self) -> None:
        self.records: list[LlmCallRecord] = []

    async def record(self, entry: LlmCallRecord) -> None:
        self.records.append(entry)
