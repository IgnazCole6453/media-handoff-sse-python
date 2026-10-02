from types import SimpleNamespace

from media_stream_service import DeliveryRequest, DeliveryService, MediaAsset, sse_events


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["model"] == "auto"
        assert kwargs["stream"] is True
        return [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="ship "))]),
            SimpleNamespace(choices=[]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="today"))]),
        ]


def test_stream_contains_sse_text_and_done_event():
    request = DeliveryRequest(
        asset=MediaAsset(asset_id="a1", title="Test reel", duration_seconds=12, audience="editors"),
        creator_note="Use the measured caption.",
    )
    output = list(sse_events(DeliveryService(FakeCompletions()), request))
    assert output == ['data: {"text": "ship "}\n\n', 'data: {"text": "today"}\n\n', "event: done\ndata: {}\n\n"]
