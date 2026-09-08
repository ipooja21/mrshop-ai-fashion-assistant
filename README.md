# Mr.Shop — Conversational AI Fashion Assistant

Mr.Shop is a lightweight conversational AI fashion assistant designed to provide personalized fashion recommendations through a natural multi-turn conversation.

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

## 🖥️ Mr.Shop Interface

<p align="center">
  <img src="docs/mrshop-screenshot.png" alt="Mr.Shop AI Fashion Assistant interface" width="100%">
</p>

<p align="center">
  <em>Mr.Shop — AI-powered conversational fashion assistant</em>
</p>

---

## 🏗️ Architecture

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
```

---

## 🔄 Conversation Flow

```text
User Message
     │
     ▼
Frontend
     │
     ▼
FastAPI /api/chat
     │
     ▼
Conversation Orchestrator
     │
     ├── Intent Detection
     ├── Memory Retrieval
     ├── Context Processing
     ├── Tool Selection
     └── Response Generation
              │
              ▼
        AI Response
              │
              ▼
          Frontend
```

---

## 🧠 Intent Handling

Mr.Shop can identify and route different types of user requests, including:

- Styling requests
- Product shopping
- Wardrobe-related questions
- Budget-based recommendations
- Occasion-based styling
- Stylist booking
- Follow-up questions
- Topic switching within the same conversation

The system combines rule-based logic with optional LLM-based classification.

---

## 💾 Memory System

Mr.Shop uses SQLite-based memory to preserve useful user preferences across conversations.

Examples include:

- Style preferences
- Budget preferences
- Relevant conversation context
- User-specific fashion preferences

---

## 🛍️ Product Recommendation

The product recommendation layer can return relevant fashion products based on:

- Category
- Occasion
- Style
- Budget
- User preferences
- Conversation context

The frontend displays recommended products through interactive product cards.

---

## 💰 Budget Awareness

Mr.Shop can detect budget information from natural-language requests.

Example:

```text
"Show me a wedding outfit under ₹5000"
```

---

## 👗 Wardrobe-Aware Styling

The assistant can incorporate wardrobe information when generating styling suggestions.

Example:

```text
"I already have black trousers. What should I wear with them?"
```

---

## 👨‍💼 Stylist Booking

Mr.Shop supports a stylist-booking flow where users can express their requirement naturally during the conversation.

Example:

```text
"I want to talk to a stylist for a wedding outfit."
```

---

## ❤️ Wishlist

The frontend provides a local wishlist where users can save recommended products.

Wishlist functionality includes:

- Add product
- Remove product
- View saved products
- Persistent browser storage

---

## 🤖 LLM Integration

An optional LLM provider can be used for:

- Natural-language response generation
- Intent classification
- Conversational understanding
- Context-aware responses

API credentials should be stored securely using environment variables and should **never be hard-coded in the frontend**.

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Responsive UI
- LocalStorage

### Backend
- Python
- FastAPI
- SQLite
- REST API

### AI
- LLM-based response generation
- Hybrid intent classification
- Context-aware conversation

### Deployment
- Static frontend hosting
- FastAPI backend service
- SQLite database

---

## 📁 Project Structure

```text
Mr.Shop/
│
├── frontend/
│   └── index.html
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── database/
│   ├── services/
│   ├── tools/
│   └── tests/
│
├── docs/
│   └── mrshop-screenshot.png
│
├── README.md
└── .gitignore
```

---

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Mr.Shop
```

### 2. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

### 4. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload
```

### 5. Open the frontend

Open `frontend/index.html` or serve it using a local development server.

---

## 🔐 Environment Variables

```env
OPENAI_API_KEY=
```

**Never commit API keys to GitHub.**

---

## 🧪 Testing

```bash
pytest
```

---

## 📱 Responsive Design

The Mr.Shop frontend is designed to work across:

- Desktop
- Laptop
- Tablet
- Mobile devices

---

## 🎯 Project Goal

Mr.Shop demonstrates how conversational AI can combine:

**Natural Language + Memory + Intent Detection + Product Recommendations + Styling + Tools**

into a single fashion-assistant experience.
