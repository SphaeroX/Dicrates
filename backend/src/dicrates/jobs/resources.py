"""Shared resources for jobs (DB pool, clock, hooks); tests replace them."""

from dataclasses import dataclass, field

from psycopg_pool import AsyncConnectionPool

from dicrates.core.db import create_pool
from dicrates.core.settings import Settings, get_settings
from dicrates.rounds.engine import Clock, HookRegistry, SystemClock


@dataclass
class JobResources:
    clock: Clock = field(default_factory=SystemClock)
    hooks: HookRegistry = field(default_factory=HookRegistry)
    _pool: AsyncConnectionPool | None = None
    _settings: Settings | None = None

    def settings(self) -> Settings:
        return self._settings or get_settings()

    async def pool(self) -> AsyncConnectionPool:
        if self._pool is None:
            database_url = self.settings().database_url
            if database_url is None:
                msg = "DATABASE_URL must be set for the job worker"
                raise RuntimeError(msg)
            self._pool = create_pool(database_url.get_secret_value())
            await self._pool.open()
        return self._pool

    def use(
        self,
        *,
        pool: AsyncConnectionPool | None = None,
        clock: Clock | None = None,
        hooks: HookRegistry | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Replace resources (tests, worker start-up)."""
        if pool is not None:
            self._pool = pool
        if clock is not None:
            self.clock = clock
        if hooks is not None:
            self.hooks = hooks
        if settings is not None:
            self._settings = settings


resources = JobResources()
