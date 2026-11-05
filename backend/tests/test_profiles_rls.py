"""Row level security on `public.profiles` (migration in supabase/migrations/)."""

import json
import uuid

import psycopg
import pytest
from psycopg import sql

pytestmark = pytest.mark.integration

type Connection = psycopg.AsyncConnection[tuple[object, ...]]


async def create_user_with_profile(connection: Connection, pseudonym: str) -> uuid.UUID:
    user_id = uuid.uuid4()
    await connection.execute(
        "INSERT INTO auth.users (id, email) VALUES (%s, %s)",
        (user_id, f"{user_id}@example.test"),
    )
    await connection.execute(
        "INSERT INTO public.profiles (id, pseudonym) VALUES (%s, %s)", (user_id, pseudonym)
    )
    return user_id


async def act_as(connection: Connection, role: str, user_id: uuid.UUID | None = None) -> None:
    claims = {"sub": str(user_id), "role": role} if user_id else {"role": role}
    await connection.execute(
        "SELECT set_config('request.jwt.claims', %s, true)", (json.dumps(claims),)
    )
    await connection.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))


async def visible_profile_ids(connection: Connection) -> set[object]:
    cursor = await connection.execute("SELECT id FROM public.profiles")
    return {row[0] for row in await cursor.fetchall()}


async def test_authenticated_user_sees_only_own_profile(db_connection: Connection) -> None:
    own = await create_user_with_profile(db_connection, "Owl")
    other = await create_user_with_profile(db_connection, "Fox")

    await act_as(db_connection, "authenticated", own)

    visible = await visible_profile_ids(db_connection)
    assert own in visible
    assert other not in visible


async def test_anon_sees_no_profiles(db_connection: Connection) -> None:
    await create_user_with_profile(db_connection, "Owl")

    await act_as(db_connection, "anon")

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        await visible_profile_ids(db_connection)


async def test_authenticated_user_cannot_write_profiles(db_connection: Connection) -> None:
    own = await create_user_with_profile(db_connection, "Owl")

    await act_as(db_connection, "authenticated", own)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        await db_connection.execute(
            "UPDATE public.profiles SET pseudonym = 'Hacker' WHERE id = %s", (own,)
        )


@pytest.mark.parametrize("role", ["anon", "authenticated"])
async def test_client_roles_cannot_read_job_queue(db_connection: Connection, role: str) -> None:
    await act_as(db_connection, role, uuid.uuid4() if role == "authenticated" else None)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        await db_connection.execute("SELECT * FROM procrastinate_jobs")
