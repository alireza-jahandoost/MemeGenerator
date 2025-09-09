
# News Meme 🗞️➡️😂

Turn breaking news into spicy, shareable memes in one API call.
FastAPI server + OpenAI for punchlines + memegen.link for instant image generation.

---

## ✨ What it does

* Accepts a news headline.
* Picks a meme template (e.g., **Drake**, **Two Buttons**, **Galaxy Brain**).
* Writes short, punchy captions with a shitposter persona.
* Cleans/normalizes lines (no labels, ≤ \~12 words).
* Redirects you to a ready-to-share meme image URL.

---

## 🚀 Quickstart

**1) Clone & enter**

```
git clone https://github.com/yourname/news-meme.git
cd news-meme
```

**2) Install dependencies**

```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3) Configure**

Copy the example environment file:

```
cp .env.example .env
```

Edit `.env` with your values:

```
OPENAI_API_KEY=sk-your-real-key
OPENAI_MODEL=gpt-5-mini  # optional, default is gpt-5-mini
```

**4) Run**

```
python app.py "EU signs sweeping AI regulations"
```

---


---

## 🧠 Meme templates

| Slug      | Panels | Use when…                                                              |
| --------- | :----: | ---------------------------------------------------------------------- |
| `drake`   |    2   | Reject vs prefer; clean contrast jokes.                                |
| `db`      |    3   | Attention shift; new obsession vs neglected old thing. (distracted bf) |
| `gru`     |    4   | Plans backfire; realization mirrors twice (panels 3 & 4).              |
| `ds`      |    3   | Impossible choices; mutually bad/good options. (two buttons)           |
| `cmm`     |    1   | Spicy declarative take; bold sign energy. (change my mind)             |
| `success` |    2   | Tiny victories; petty wins; unexpected W. (success kid)                |
| `mordor`  |    1   | Obvious truths; near-impossible tasks. (one does not simply)           |
| `gb`      |    4   | Escalation from dumb → galaxy brain.                                   |

