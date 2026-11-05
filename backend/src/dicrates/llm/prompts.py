"""Versioned prompt files: `prompts/<name>.v<N>.md`, placeholders as `$name` / `${name}`.

`string.Template` is used instead of `str.format` so prompts can contain JSON
braces. A changed prompt is a new file with a higher version; the version string
(`<name>.v<N>`) is stored with every LLM result.
"""

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from string import Template

PROMPTS_DIR = Path(__file__).parent / "prompts"
_NAME = re.compile(r"[a-z][a-z0-9_]*")


class PromptNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class RenderedPrompt:
    version: str
    text: str


@dataclass(frozen=True)
class Prompt:
    name: str
    version: int
    template: str

    @property
    def version_id(self) -> str:
        return f"{self.name}.v{self.version}"

    def render(self, **params: str) -> RenderedPrompt:
        """Fill all placeholders; a missing parameter raises `KeyError`."""
        return RenderedPrompt(
            version=self.version_id, text=Template(self.template).substitute(params)
        )


class PromptRegistry:
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def load(self, name: str, *, version: int) -> Prompt:
        version_id = f"{name}.v{version}"
        path = self._directory / f"{version_id}.md"
        if not _NAME.fullmatch(name) or not path.is_file():
            msg = f"prompt {version_id} not found"
            raise PromptNotFoundError(msg)
        return Prompt(name=name, version=version, template=path.read_text(encoding="utf-8"))


@cache
def default_registry() -> PromptRegistry:
    return PromptRegistry(PROMPTS_DIR)
