"""Short, easy-to-read invite codes (no 0/O, 1/I/L, 5/S)."""

import secrets
from random import Random

INVITE_ALPHABET = "ABCDEFGHJKMNPQRTUVWXYZ2346789"
INVITE_CODE_LENGTH = 6
_SEPARATORS = str.maketrans("", "", " -_")


def new_invite_code(generator: Random | None = None) -> str:
    choose = generator.choice if generator is not None else secrets.choice
    return "".join(choose(INVITE_ALPHABET) for _ in range(INVITE_CODE_LENGTH))


def normalize_invite_code(typed: str) -> str | None:
    """Upper-case and strip spaces/dashes; `None` if it cannot be a code."""
    code = typed.strip().upper().translate(_SEPARATORS)
    if len(code) != INVITE_CODE_LENGTH or not set(code) <= set(INVITE_ALPHABET):
        return None
    return code
