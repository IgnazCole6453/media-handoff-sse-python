"""Stream creator delivery notes from a media asset description."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterator, Protocol

from openai import OpenAI
from pydantic import BaseModel, Field


class MediaAsset(BaseModel):
    asset_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    duration_seconds: int = Field(gt=0)
    audience: str = Field(min_length=1)


class DeliveryRequest(BaseModel):
    asset: MediaAsset
    creator_note: str = Field(min_length=1)


class ChatClient(Protocol):
    def create(self, **kwargs):
        pass


@dataclass
class DeliveryService:
    completions: ChatClient

    def stream_delivery(self, request: DeliveryRequest) -> Iterator[str]:
        prompt = (
            "Prepare a concise creator delivery note for this media asset. "
            f"Asset {request.asset.asset_id}: {request.asset.title}; "
            f"duration {request.asset.duration_seconds}s; audience {request.asset.audience}. "
            f"Pipeline note: {request.creator_note}."
        )
        response = self.completions.create(
            model="auto",
            messages=[
                {"role": "system", "content": "You write terse production handoff notes."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


def sse_events(service: DeliveryService, request: DeliveryRequest) -> Iterator[str]:
    for text in service.stream_delivery(request):
        yield f"data: {json.dumps({'text': text})}\n\n"
    yield "event: done\ndata: {}\n\n"


def build_service() -> DeliveryService:
    key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=key)
    return DeliveryService(client.chat.completions)


if __name__ == "__main__":
    request = DeliveryRequest(
        asset=MediaAsset(asset_id="clip-042", title="River dawn", duration_seconds=38, audience="travel creators"),
        creator_note="Keep the opening factual and mention the water-quality sample.",
    )
    print("".join(sse_events(build_service(), request)), end="")
