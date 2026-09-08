# Mr.Shop — Conversational AI Fashion Assistant


Mr.Shop is a lightweight conversational AI fashion assistant 

The goal is to demonstrate how a single conversation can understand user intent, remember relevant context, and smoothly switch between **styling, shopping, wardrobe, and stylist-booking** requests without forcing the user to repeat information.

---

## ✨ Key Features

- 🧠 Hybrid intent classification
- 💬 Multi-turn conversational context
- 🧩 Ambient memory using SQLite
- 👗 Wardrobe-aware styling
- 🛍️ Product recommendations
- 💰 Budget extraction and persistence
- 🔄 Styling → Purchase topic switching
- 👨‍💼 Stylist booking flow
- 🤖 Optional LLM response generation
- 🧭 Central conversation orchestrator
- 🧪 Automated tests
- 📱 Responsive frontend interface
- ❤️ Local wishlist support
- ⚡ FastAPI backend

---

# 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │     Mr.Shop Frontend    │
                    │   HTML / CSS / JavaScript│
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI API        │
                    │  Conversation Endpoints  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Conversation Orchestrator│
                    │                           │
                    │ • Intent routing         │
                    │ • Context management     │
                    │ • Tool coordination      │
                    │ • Response generation    │
                    └───────┬─────────┬────────┘
                            │         │
                ┌───────────┘         └────────────┐
                ▼                                  ▼
       ┌─────────────────┐                ┌─────────────────┐
       │ Intent Classifier│                │  Memory Service │
       │                 │                │     SQLite      │
       │ Rules + LLM     │                │                 │
       └────────┬────────┘                └────────┬────────┘
                │                                  │
                └──────────────┬───────────────────┘
                               ▼
                    ┌─────────────────────────┐
                    │       Tool Layer        │
                    │                         │
                    │ Products | Wardrobe     │
                    │ Booking                 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Optional LLM Provider   │
                    │ Natural-language reply  │
                    └─────────────────────────┘
