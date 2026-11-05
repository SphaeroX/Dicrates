from datetime import datetime

from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool

from dicrates.news.models import NewsItem


class PostgresNewsRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def add_new(self, items: list[NewsItem]) -> int:
        """Insert items whose URL is unknown; returns how many were new."""
        added = 0
        async with self._pool.connection() as connection:
            for item in items:
                cursor = await connection.execute(
                    "INSERT INTO public.news_items (url, title, summary, outlet, language,"
                    " leaning, published_at, expires_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    " ON CONFLICT (url) DO NOTHING",
                    (
                        item.url,
                        item.title,
                        item.summary,
                        item.outlet,
                        item.language,
                        item.leaning,
                        item.published_at,
                        item.expires_at,
                    ),
                )
                added += cursor.rowcount
        return added

    async def delete_expired(self, now: datetime) -> int:
        async with self._pool.connection() as connection:
            cursor = await connection.execute(
                "DELETE FROM public.news_items WHERE expires_at <= %s", (now,)
            )
            return cursor.rowcount

    async def recent(self, *, limit: int) -> list[NewsItem]:
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=class_row(NewsItem))
            await cursor.execute(
                "SELECT url, title, summary, outlet, language, leaning, published_at, expires_at"
                " FROM public.news_items ORDER BY published_at DESC LIMIT %s",
                (limit,),
            )
            return await cursor.fetchall()
