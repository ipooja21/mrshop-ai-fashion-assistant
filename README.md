# Mr.Shop — Track A: Conversational Intelligence & Ambient Context

Mr.Shop is a FastAPI-backed conversational fashion assistant. Track A was selected
to demonstrate intent routing, durable user context, and smooth movement between
styling, shopping, wardrobe, and stylist-booking tasks without rebuilding the
conversation at every turn.

## Architecture

\`\`\`text
Frontend (vanilla HTML/CSS/JS)
  -> FastAPI routes
  -> ConversationOrchestrator
     -> hybrid IntentClassifier
     -> SQLite MemoryService
     -> product / wardrobe / booking tools
     -> optional OpenAI response generation
\`\`\`

The frontend calls the local API at \`http://127.0.0.1:8000\`. It creates a
conversation before chat, restores message history, shows API-supplied product
cards, persists its session wishlist locally, and exposes an offline/retry state.

## Conversational intelligence

The classifier is deliberately hybrid:

- Deterministic rules handle styling, purchases, booking, and explicit wardrobe
  upload/save language quickly and predictably.
- It extracts budget, product category, basic owned-item details, and colour.
- If a rule is ambiguous, the optional LLM classifier is used; if it is
  unavailable, the deterministic result remains the safe fallback.

\`MemoryService\` stores recent messages, current/previous intent, a rolling
conversation summary, budget, style preference, and wardrobe items in SQLite.
The orchestrator passes both recent history and stored context to response
generation, so information is available in later turns.

### Topic-switch example

1. “I have a black kurti. How can I style it?” is \`STYLING\`; the owned item is
   retained in the wardrobe/context.
2. “I want to buy matching footwear.” is \`PURCHASE\`; the previous styling
   intent causes a topic switch, and footwear is normalized to the existing
   sneaker/footwear product-search category.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | \`/api/health\` | Availability check |
| POST | \`/api/conversations\` | Create a conversation |
| POST | \`/api/chat\` | Process a conversational turn |
| POST | \`/api/messages\` | Equivalent message-processing route |
| GET | \`/api/conversations/{id}/messages\` | Restore conversation history |
| GET | \`/api/memory/{user_id}\` | Read ambient context |
| GET | \`/api/users/{user_id}/memory\` | Compatibility memory route |
| POST | \`/api/reset?user_id=...\` | Reset stored context |

## Run locally

\`\`\`powershell
.\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
.\\venv\\Scripts\\python.exe -m pytest -q
\`\`\`

Open \`frontend/index.html\` in a browser after starting the API.

## Demo conversations

1. “I have a black kurti. How can I style it?”
2. “I want to buy matching footwear.” (topic switch)
3. “Show me sneakers under ₹3,000.”
4. “Book a stylist consultation.”

## Failure handling and trade-offs

FastAPI wraps route failures with HTTP errors; the frontend performs a health
check before a chat call and provides a retry/offline state. Product cards only
render records returned by the API and use a fallback visual when an API product
has no image.

The product catalog and booking service are deterministic local demo tools—not
live retail or calendar integrations. The optional LLM improves natural-language
responses, while rule classification and tool routing remain independently
testable. Adding a new capability scales by adding an intent, entity extraction,
and a tool adapter without changing the API shell.

## Assignment audit

| Area | Status | Notes |
| --- | --- | --- |
| Intent classification | PASS | Hybrid rules/LLM fallback covers styling, purchase, booking, and explicit wardrobe upload/save language. |
| Ambient memory/context | PASS | SQLite conversation history, budget, preferences, summary, and wardrobe persistence. |
| Styling → purchase switch | PASS | Covered by \`tests/test_track_a_flows.py\`. |
| Demo conversations | PASS | Four documented scenarios above; two are automated. |
| Orchestration | PASS | Single lightweight coordinator routes intent, memory, tools, and response generation. |
| Error handling | PARTIAL | API/frontend failures are handled; the local deterministic tool catalog has no external-service failure mode. |
| Scalability/documentation | PASS | Tool/intent boundaries and architecture are documented. |

### Remaining limitations

- \`app/tools/products.py\` is a deliberately small local catalog. Replace it
  with a retailer adapter for production data and real image/product URLs.
- There is no multipart file-upload endpoint; “wardrobe upload” currently means
  a conversational save intent. Add a validated upload route/storage adapter if
  literal image uploads are required by an evaluator.
- CORS is permissive for the local demo. Restrict \`allow_origins\` before
  deployment.
