from pathlib import Path

import pytest

from dicrates.llm.prompts import PromptNotFoundError, PromptRegistry, default_registry


@pytest.fixture
def registry(tmp_path: Path) -> PromptRegistry:
    (tmp_path / "summary.v1.md").write_text(
        "Summarise in $language. Keep {json} braces.", encoding="utf-8"
    )
    (tmp_path / "summary.v2.md").write_text("Version two in $language.", encoding="utf-8")
    return PromptRegistry(tmp_path)


def test_loads_a_version_and_fills_parameters(registry: PromptRegistry) -> None:
    prompt = registry.load("summary", version=1)

    rendered = prompt.render(language="German")

    assert rendered.text == "Summarise in German. Keep {json} braces."
    assert rendered.version == "summary.v1"


def test_versions_are_separate(registry: PromptRegistry) -> None:
    assert registry.load("summary", version=2).render(language="en").text == ("Version two in en.")


def test_missing_version_is_an_error(registry: PromptRegistry) -> None:
    with pytest.raises(PromptNotFoundError, match=r"summary\.v3"):
        registry.load("summary", version=3)


def test_missing_parameter_is_an_error(registry: PromptRegistry) -> None:
    with pytest.raises(KeyError, match="language"):
        registry.load("summary", version=1).render()


@pytest.mark.parametrize("name", ["../secret", "a/b", ""])
def test_rejects_unsafe_names(registry: PromptRegistry, name: str) -> None:
    with pytest.raises(PromptNotFoundError):
        registry.load(name, version=1)


def test_default_registry_has_the_ping_prompt() -> None:
    rendered = default_registry().load("ping", version=1).render(language="English")

    assert "English" in rendered.text
