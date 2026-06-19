from __future__ import annotations

import asyncio

from app.db.session import AsyncSessionLocal
from app.seed.symbols import seed_symbols


async def run() -> None:
    async with AsyncSessionLocal() as session:
        result = await seed_symbols(session)
        await session.commit()

    print(
        "Seeded symbols: "
        f"created={result.created} "
        f"updated={result.updated} "
        f"skipped={result.skipped}"
    )


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
