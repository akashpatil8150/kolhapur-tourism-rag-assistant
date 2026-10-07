# Tourism AI Assistant — Project Knowledge Guide

This file explains your full project in a simple, interview-friendly way.

The goal of this project is:

- user authentication with MongoDB
- a web chat UI using FastAPI
- fast rule-based replies for simple messages
- RAG for Kolhapur-specific tourism questions
- hosted LLM answering using Groq
- embedding storage in MongoDB
- fast local retrieval using FAISS

---

## 1. Project idea in one line

This is a Tourism AI Assistant that gives instant replies for simple chat messages and uses a RAG pipeline for Kolhapur tourism questions.

---

## 2. Main technologies used

- FastAPI → backend web framework
- Jinja2 templates → renders HTML pages
- JavaScript → sends chat messages from browser to backend
- MongoDB → stores users and embeddings
- Sentence Transformers (`all-MiniLM-L6-v2`) → creates embeddings
- FAISS → fast vector similarity search
- Groq API + `llama-3.1-8b-instant` → fast hosted LLM for final answer generation
- PDF knowledge base → source of tourism data

---

## 3. High-level architecture

```text
User
  ↓
Browser UI (HTML/CSS/JS)
  ↓
FastAPI backend
  ├─ Auth routes
  ├─ Chat route
  └─ RAG logic
       ├─ Fast rule-based response
       ├─ Query routing
       ├─ FAISS retrieval
       ├─ MongoDB embeddings storage
       └─ Groq LLM answer generation
```

---

## 4. Folder structure

```text
app/
  main.py
  auth.py
  chatbot.py
  database.py
  rag.py
  utils.py

templates/
  register.html
  login.html
  chatbot.html

static/
  style.css
  script.js

knowledge_base/
  travel.pdf

faiss_index/
  index.faiss
  index.pkl
  metadata.json
```

---

## 5. What each file does

### `app/main.py`

This is the entry point of the backend.

Responsibilities:

- creates the FastAPI app
- adds session middleware
- mounts static files
- includes auth and chatbot routes
- creates MongoDB indexes at startup

Important point:

It does **not** load FAISS, embeddings, or Groq at startup.

Why?

Because you wanted greetings like `Hi` and `Bye` to feel instant.  
So the expensive RAG components are loaded only when needed.

---

### `app/auth.py`

Handles authentication.

Responsibilities:

- register page
- register user
- login page
- login user
- logout user

How it works:

1. User registers with username, email, password
2. Password is hashed before storing
3. Email is stored in lowercase form
4. Login verifies the hashed password
5. Username is saved in session
6. Logout clears session

Security improvements already added:

- duplicate email protection
- password length check
- MongoDB error handling
- session clear on logout

---

### `app/chatbot.py`

Handles chatbot UI and chat API.

Responsibilities:

- serves chatbot page
- checks if user is logged in
- accepts chat messages at `/chat`
- validates input size
- calls `get_answer()` from `rag.py`

Flow:

1. Browser sends JSON like:

```json
{ "question": "Tell me about Kolhapur" }
```

2. Backend validates the request
3. Backend calls `get_answer(question)`
4. Backend returns:

```json
{ "answer": "..." }
```

---

### `app/database.py`

Connects the project to MongoDB.

Collections used:

- `users`
- `travel_embeddings`

Responsibilities:

- create MongoDB client
- expose collections
- create indexes

Indexes:

- unique index on `users.email`
- unique compound index on:
  - `index_version`
  - `chunk_id`

This helps avoid duplicate embedding records for the same index version.

---

### `app/utils.py`

Contains password helper functions:

- `hash_password()`
- `verify_password()`

It uses `passlib` with bcrypt.

---

### `app/rag.py`

This is the core AI logic of the project.

It handles:

- fast replies
- routing
- PDF cleaning
- chunking
- embedding generation
- FAISS loading/building
- MongoDB embedding storage
- retrieval
- prompt creation
- Groq API answering

This is the most important backend file.

---

### `static/script.js`

Frontend chat behavior.

Responsibilities:

- send message on button click or Enter
- call `/chat`
- append user and bot messages
- disable input while waiting
- show temporary “Thinking…” message
- safely render text without `innerHTML`

Important:

This was improved to avoid XSS by using `textContent`.

---

### `templates/*.html`

These are the frontend pages:

- `register.html`
- `login.html`
- `chatbot.html`

The chatbot page shows:

- welcome message
- example questions
- input box
- send button

---

## 6. Backend request flow

When user opens the app:

1. user goes to `/register` or `/login`
2. after login, user reaches `/chatbot`
3. user types a message
4. JavaScript sends POST request to `/chat`
5. backend calls `get_answer()`
6. response comes back to browser
7. browser shows bot reply

---

## 7. How chat answering works

The backend does **not** treat every message the same way.

It uses a smart flow:

```text
User message
  ↓
Normalize text
  ↓
Check fast responses
  ↓
If Kolhapur query → RAG route
  ↓
Else if general travel query → direct LLM route
  ↓
Else → fixed scope message
```

---

## 8. Fast rule-based responses

Some messages do not need LLM at all.

Examples:

- hi
- hello
- hey
- thanks
- thank you
- help
- bye
- good night

These are handled by:

- `normalize()`
- `fast_response()`

Why this is important:

- zero LLM cost
- zero retrieval cost
- almost instant response
- much better user experience

This is one of the biggest latency improvements in your project.

---

## 9. Query routing logic

After checking fast responses, the backend decides the type of question.

### A. Kolhapur query

If the question contains Kolhapur-specific keywords like:

- kolhapur
- rankala
- panhala
- mahalaxmi
- ambabai
- kolhapuri

Then it goes to the RAG pipeline.

### B. General travel query

If the question contains words like:

- hotel
- flight
- bus
- transport
- travel
- tourism
- food
- restaurant
- trip

Then it goes to the general travel LLM route.

### C. Non-travel query

If it matches neither, the bot returns a fixed message explaining its scope.

---

## 10. What RAG means in your project

RAG = Retrieval-Augmented Generation

In your project, that means:

1. search the PDF knowledge base for relevant information
2. collect the best matching chunks
3. send those chunks to the LLM
4. generate a final answer based only on retrieved context

So the LLM does not answer blindly.

It first gets supporting knowledge from your tourism PDF.

---

## 11. Knowledge base source

Your source file is:

- `knowledge_base/travel.pdf`

This PDF contains the tourism knowledge your assistant uses for Kolhapur-related questions.

---

## 12. How chunking works

The PDF text is split into smaller pieces called chunks.

Current settings:

- `CHUNK_SIZE = 850`
- `CHUNK_OVERLAP = 100`

Why chunking is needed:

- LLM cannot use the entire PDF every time
- embeddings work better on smaller semantic pieces
- retrieval becomes more precise and faster

Why overlap is used:

- avoids losing context at chunk boundaries

Example idea:

If one paragraph ends and the next begins, some shared overlap helps preserve meaning.

---

## 13. Document cleaning

Before chunking, the project cleans the PDF text.

It removes:

- citation marks like `[1]`
- Wikipedia URLs
- some date/footer lines
- map labels like `Show map of Maharashtra`

Why this is useful:

- cleaner chunks
- better embeddings
- less noisy retrieval
- better final answers

---

## 14. Embeddings in your project

Embeddings are numerical vector representations of text.

Your model:

- `sentence-transformers/all-MiniLM-L6-v2`

What it does:

- converts each chunk into a vector
- converts user question into a vector
- helps compare similarity between question and chunk

Simple understanding:

Text becomes numbers, and similar meanings stay close in vector space.

---

## 15. Why embeddings are stored in MongoDB

You asked to store embeddings in MongoDB, and now your project does that.

Collection:

- `travel_embeddings`

Each document stores:

- `index_version`
- `chunk_id`
- `text`
- `metadata`
- `embedding`

### Why store them?

Main reasons:

1. visibility  
   You can inspect stored chunk text and vectors in MongoDB Compass.

2. persistence  
   You keep a database copy of generated embeddings.

3. debugging  
   You can verify what chunk got embedded and stored.

4. project understanding  
   It clearly shows that your RAG pipeline has a document-processing stage.

### Important note

In your current architecture:

- MongoDB stores embeddings
- FAISS performs retrieval

So MongoDB is being used as the persistent embedding store, but **FAISS is still the active search engine**.

This is a very good choice for your project because:

- it stays simple
- it stays local
- it remains interview-friendly
- FAISS is much faster for similarity search in this setup

---

## 16. What `index_version` means

`index_version` is a stable identity for one exact index configuration.

It is based on:

- PDF modification time
- PDF size
- embedding model name
- chunk size
- chunk overlap

Why this matters:

If you change:

- the PDF
- chunking settings
- embedding model

then the system can detect that the old index is outdated and rebuild the vector store.

This prevents stale retrieval.

---

## 17. Why FAISS is still used

Even though embeddings are stored in MongoDB, FAISS is still used for retrieval.

Why?

Because FAISS is extremely fast for local similarity search.

Your current design is:

```text
PDF
  ↓
chunking
  ↓
embeddings
  ├─ stored in MongoDB
  └─ indexed in FAISS
```

Then at query time:

```text
User question
  ↓
question embedding
  ↓
FAISS similarity search
  ↓
top relevant chunks
  ↓
LLM answer
```

This is a clean and practical design.

---

## 18. How FAISS retrieval works

When a Kolhapur question comes:

1. question is embedded
2. FAISS compares it with stored chunk vectors
3. top matching chunks are returned
4. only relevant chunks are kept
5. context is sent to LLM

Current retrieval settings:

- `TOP_K = 3`
- distance threshold: `MAX_RETRIEVAL_DISTANCE = 1.35`

Why this is useful:

- smaller context
- lower latency
- less irrelevant text
- better answer quality

---

## 19. Why relevance filtering was added

FAISS always returns nearest chunks, but nearest does not always mean relevant enough.

So your backend filters results using a max distance threshold.

If no chunk is good enough, the bot returns:

`I couldn't find this information in my knowledge base.`

This reduces hallucination.

---

## 20. Prompt design in your project

You currently use 2 prompts.

### A. `rag_prompt`

Used for Kolhapur RAG questions.

Rules include:

- answer only from reference text
- do not use outside knowledge
- do not invent facts
- if answer is missing, return fixed fallback
- keep answer concise

This makes the bot more grounded.

### B. `travel_prompt`

Used for general travel questions.

It tells the model:

- answer only travel/tourism questions
- do not invent specific facts
- say “I’m not confident enough...” if unsure

---

## 21. Groq and hosted model usage

Your final answer generation uses:

- Groq API
- model: `llama-3.1-8b-instant`

Why this is good for your project:

- much faster than local laptop inference
- free tier available
- simple API integration
- better chat feel for general travel queries
- easy to explain in interviews

Important optimization:

The Groq client is created lazily only when needed.

That means:

- no API call for `Hi`
- no API call for `Thanks`
- no API call for `Help`

Only real AI answers use Groq.

---

## 22. Startup behavior

At startup, the app only does lightweight work:

- creates FastAPI app
- connects MongoDB
- creates indexes

It does **not** automatically load:

- embeddings model
- FAISS index
- Groq client

Why this is important:

- faster app startup
- lower initial delay
- instant greeting responses

---

## 23. First real RAG question behavior

The first real Kolhapur RAG query may take longer because:

1. embeddings model may load
2. FAISS may load or rebuild
3. PDF may be chunked if rebuild is needed
4. embeddings may be stored in MongoDB

After that, later queries are faster.

So this is normal:

- first real RAG query = slower
- later similar RAG queries = faster

---

## 24. Authentication flow

### Register flow

1. user opens `/register`
2. form submits username, email, password
3. password is hashed
4. record stored in MongoDB
5. redirect to `/login?registered=true`

### Login flow

1. user opens `/login`
2. enters email and password
3. backend finds user in MongoDB
4. backend verifies hashed password
5. username stored in session
6. redirect to `/chatbot`

### Logout flow

1. user clicks logout
2. session is cleared
3. redirect to `/login`

---

## 25. Session handling

Your project uses:

- `SessionMiddleware`

The session stores:

- `username`

This is how the backend knows whether the user is logged in.

If session is missing:

- `/chatbot` redirects to login
- `/chat` returns 401

---

## 26. Frontend flow

When the user sends a message:

1. JavaScript gets input text
2. user message is shown in chat box
3. input is temporarily disabled
4. `/chat` API is called
5. backend returns JSON answer
6. answer is displayed
7. input is enabled again

This makes the chat feel smooth and controlled.

---

## 27. Why `textContent` is used instead of `innerHTML`

Earlier, using `innerHTML` could allow unsafe HTML injection.

Now `textContent` is used so that:

- user input is treated as plain text
- LLM output is treated as plain text
- malicious HTML/script is not executed

This is an important frontend security improvement.

---

## 28. Why the project is now faster

Main latency improvements:

### 1. No unnecessary LLM calls for greetings

Messages like:

- hi
- hey
- thanks
- help
- bye

return instantly.

### 2. No LLM-based intent classification

Earlier, classification itself could call the model.

Now routing is done with:

- normalization
- keyword matching
- simple Python logic

### 3. Lazy loading

Heavy components load only when needed.

### 4. Smaller retrieval context

- top 3 chunks instead of larger context
- lower token usage
- faster response

### 5. Relevance filtering

Avoids sending bad chunks to the model.

---

## 29. Limitations of current project

This project is intentionally simple, but you should know its current limits.

### 1. General travel route is keyword-based

If a travel question has none of the travel keywords, it may fall to the fallback response.

### 2. MongoDB stores embeddings but does not do vector search

FAISS is still the actual retrieval engine.

### 3. First RAG query may be slower

Because local models/index may load.

### 4. Knowledge depends on the PDF

If the answer is not in the PDF, RAG should not invent it.

---

## 30. How to explain this project in an interview

You can say:

> I built a Tourism AI Assistant using FastAPI, MongoDB, FAISS, and the Groq API.  
> I optimized it for low latency by handling greetings and simple intents with rule-based Python logic instead of sending every message to the LLM.  
> For Kolhapur-specific questions, I use RAG: I load a tourism PDF, clean it, split it into chunks, generate embeddings using MiniLM, store those embeddings in MongoDB for persistence and inspection, and use FAISS for fast local similarity search.  
> The retrieved context is then passed to a fast hosted Llama model through Groq to generate a grounded answer.  
> Authentication is handled with MongoDB and session middleware, and the frontend communicates with the backend through a simple JavaScript fetch-based chat interface.

---

## 31. Simple end-to-end example

### Example 1: `Hi`

Flow:

1. request goes to `/chat`
2. `get_answer("Hi")`
3. normalized to `hi`
4. found in `FAST_RESPONSES`
5. immediate reply returned

No FAISS.  
No embeddings.  
No Groq call.  

### Example 2: `Tell me about Rankala Lake`

Flow:

1. request goes to `/chat`
2. not a fast response
3. keyword `rankala` matches Kolhapur route
4. vector store loads/builds if needed
5. question embedding is created
6. FAISS retrieves top chunks
7. relevant chunks become context
8. prompt sent to Groq
9. final answer returned

### Example 3: `Best hotels for a family trip`

Flow:

1. request goes to `/chat`
2. not a fast response
3. `hotel` / `trip` matches general travel route
4. travel prompt sent to Groq
5. final answer returned

---

## 32. MongoDB collections summary

### `users`

Stores:

- username
- email
- hashed password

### `travel_embeddings`

Stores:

- index_version
- chunk_id
- text
- metadata
- embedding

---

## 33. What happens when PDF changes

If your PDF changes, the backend compares:

- file size
- modification time
- embedding model
- chunk settings

If anything changed, it rebuilds:

- chunks
- embeddings
- FAISS index
- MongoDB embedding records for that version

This keeps the knowledge base fresh.

---

## 34. Why this project is strong for your journey

This is a strong internship-to-full-time style project because it demonstrates:

- backend development
- authentication
- FastAPI APIs
- frontend-backend integration
- RAG understanding
- embeddings
- vector databases/search
- latency optimization
- hosted LLM usage
- prompt design
- security improvements
- debugging mindset

It is also easy to explain because the architecture is clean and not over-engineered.

---

## 35. Final summary

Your backend works like this:

1. FastAPI receives the request
2. session checks user login
3. chat route calls `get_answer()`
4. simple messages are answered instantly with Python rules
5. Kolhapur questions use PDF-based RAG
6. embeddings are generated with MiniLM
7. embeddings are stored in MongoDB
8. FAISS does fast local similarity search
9. Groq generates the final answer
10. response returns to browser

So in one sentence:

**MongoDB stores users and embeddings, FAISS retrieves similar chunks, and Groq generates the final tourism answer.**

---

## 36. Short personal explanation you can use

> This project is a Tourism RAG Assistant built with FastAPI. I added low-latency routing so greetings and simple intents are handled instantly without calling the LLM. For Kolhapur tourism queries, I use a PDF knowledge base, generate embeddings using MiniLM, store those embeddings in MongoDB, use FAISS for fast similarity retrieval, and then send only the relevant context to a fast hosted Llama model through Groq.

---

## 37. Current environment variables

Your project now uses:

- `GROQ_API_KEY`

Stored in:

- `.env`

Example:

```env
GROQ_API_KEY=your_real_groq_key_here
```

This keeps secrets out of the Python source code.
