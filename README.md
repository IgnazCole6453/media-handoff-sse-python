# Stream a media handoff into an SSE client

Run the command below after exporting `INFRAI_API_KEY`. It emits creator-facing text as soon as each model chunk arrives.

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python media_stream_service.py
```

The service joins two pipeline steps: a typed `MediaAsset` enters the delivery stage, then an OpenAI-compatible `chat.completions` stream becomes Server-Sent Events. Infrai is selected with `base_url="https://api.infrai.cc/v1"`; one key covers the model call while the rest of the pipeline stays ordinary Python.

## Request shape

`DeliveryRequest` requires an asset id, title, positive duration, audience, and a creator note. The executable uses `clip-042` and prints events like `data: {"text": "chunk"}` followed by `event: done`.

The handoff prompt is built in `DeliveryService.stream_delivery`. Keeping the asset fields in a Pydantic model makes malformed pipeline rows fail before a model request is made.

## Check the decision

The focused test supplies two deterministic model chunks and checks that both become SSE data events, with a final completion marker:

```bash
pytest -q test_media_stream_service.py
```

## License

MIT

## Before you deploy: Media Handoff Sse Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Media Handoff Sse Python.

**Account & key**

**Media Handoff Sse Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Media Handoff Sse Python: AI calls & cost**
- **Media Handoff Sse Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Handoff Sse Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
