import asyncio


class Async:
    @staticmethod
    async def all(coroutines: list):
        """
        concurrently runs coroutines

        @param coroutines: (list) coroutines tot run
        """
        _coroutines = tuple(coroutines)
        return await asyncio.gather(*_coroutines)
