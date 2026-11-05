"""A stand-in for `LlmRunner` that returns scripted outputs per task (pipeline tests)."""

import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from dicrates.llm.prompts import RenderedPrompt
from dicrates.llm.runner import LlmError, LlmResult


@dataclass
class RecordedCall:
    task: str
    prompt: RenderedPrompt
    user_input: str


@dataclass
class ScriptedRunner:
    """`outputs[task]` is consumed in order; an exception instance is raised instead."""

    outputs: dict[str, list[dict[str, Any] | LlmError]]
    calls: list[RecordedCall] = field(default_factory=list[RecordedCall])
    _used: defaultdict[str, int] = field(default_factory=lambda: defaultdict(int))

    def calls_for(self, task: str) -> list[RecordedCall]:
        return [call for call in self.calls if call.task == task]

    async def run[OutputT: BaseModel](
        self,
        *,
        task: str,
        prompt: RenderedPrompt,
        output_type: type[OutputT],
        user_input: str,
        room_id: uuid.UUID | None = None,
    ) -> LlmResult[OutputT]:
        del room_id
        self.calls.append(RecordedCall(task=task, prompt=prompt, user_input=user_input))
        index = self._used[task]
        self._used[task] += 1
        scripted = self.outputs[task][min(index, len(self.outputs[task]) - 1)]
        if isinstance(scripted, LlmError):
            raise scripted
        return LlmResult(
            output=output_type.model_validate(scripted),
            prompt_version=prompt.version,
            model="scripted:model",
            input_tokens=1,
            output_tokens=1,
        )
