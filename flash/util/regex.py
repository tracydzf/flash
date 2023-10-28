import pydash
import re
from motor.motor_asyncio import AsyncIOMotorCollection


class Regex:
    @staticmethod
    def best_match(entities: list):
        best = {
            'regex_groups': ()
        }
        for entity in entities:
            if pydash.has(
                    entity, 'regex_groups') and len(
                entity['regex_groups']) > len(
                best['regex_groups']):
                best = entity
        return not pydash.is_empty(best['regex_groups']) and best or None

    @staticmethod
    async def get_matched_paths(path: str, db: AsyncIOMotorCollection):
        matches = []
        async for ctx in db.find({}):
            if pydash.has(ctx, 'path'):
                match = re.match(ctx['path'], path)
                match and matches.append(pydash.merge(
                    ctx, {'regex_groups': match.groups()}))
        return matches
