import asyncio
from datetime import datetime
from typing import List, NewType, Optional

import strawberry
from aiohttp import web
from pymongo import MongoClient
from strawberry.aiohttp.views import GraphQLView
from indexer.indexer import indexer_id


def parse_hex(value):
    if not value.startswith("0x"):
        raise valueError("invalid Hex value")
    return bytes.fromhex(value.replace("0x", ""))


def serialize_hex(token_id):
    return "0x" + token_id.hex()

HexValue = strawberry.scalar(
    NewType("HexValue", bytes),
    parse_value=parse_hex,
    serialize=serialize_hex
)


@strawberry.type
class Transfer:
    from_address: HexValue
    to_address: HexValue
    timestamp: datetime

    @classmethod
    def from_mongo(cls, data):
        return cls(
            from_address=data["from_address"],
            to_address=data["to_address"],
            timestamp=data["timestamp"],
        )


@strawberry.type
class Token:
    token_id: HexValue
    owner: HexValue
    updated_at: datetime

    @classmethod
    def from_mongo(cls, data):
        return cls(
            token_id=data["token_id"],
            owner=data["owner"],
            updated_at=data["updated_at"],
        )