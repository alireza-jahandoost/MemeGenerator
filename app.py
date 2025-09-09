# app.py
import os, sys, json, random, re, urllib.parse
from typing import List, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from openai import OpenAI

load_dotenv()
app = FastAPI(title="News Meme")

# OpenAI client (tested with openai 1.35.x on Windows for stability)
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

# ---- Hard-coded templates (6–10 items) ----
TEMPLATES: List[str] = [
    "drake",                 # 2 (reject/prefer)
    "db",  # 3 (boyfriend/girlfriend/distraction)
    "gru",                   # 4 (3&4 mirror realization)
    "ds",           # 3 (A/B choice + sweating)
    "cmm",        # 1 (bold sign)
    "success",           # 2 (set-up / tiny win)
    "mordor",   # 1 (obvious truth)
    "gb",       # 4 (escalation)
]

# Panel counts & short “what it’s good for” descriptions (used only in the prompt)
PANEL_COUNTS: Dict[str, int] = {
    "drake": 2,
    "db": 3,
    "gru": 4,
    "ds": 3,
    "cmm": 1,
    "success": 2,
    "mordor": 1,
    "gb": 4,
}
TEMPLATES_INFO: Dict[str, str] = {
    "drake": "Reject vs Prefer; clean contrast jokes.",
    "db": "Attention shift; new obsession vs neglected old thing. (distracted boyfriend)",
    "gru": "Plans that backfire; realization mirrors twice (panels 3 & 4).",
    "ds": "Impossible choices; mutually bad/good options; indecision. (two buttons)",
    "cmm": "Spicy declarative take; bold sign energy. (change my mind)",
    "success": "Tiny victories; petty wins; unexpected W. (success kid)",
    "mordor": "Obvious truths; near-impossible tasks. (one does not simply)",
    "gb": "Escalation from dumb → galaxy brain. (galaxy brain)",
}

# Remove label-like prefixes if the model tries to sneak them in
LABEL_PREFIXES = [
    r"^\s*(plan|detail|realization|reaction|option\s*[ab]|button\s*[ab]|top|bottom|line\s*\d+)\s*:\s*",
]

def sanitize_line(s: str) -> str:
    s = s.strip()
    for pat in LABEL_PREFIXES:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)
    # keep concise (≈12 words hard cap)
    words = s.split()
    if len(words) > 12:
        s = " ".join(words[:12])
    return s or "…"

def normalize_lines(template: str, lines: List[str]) -> List[str]:
    lines = [sanitize_line(x) for x in (lines or []) if isinstance(x, str) and x.strip()]
    required = PANEL_COUNTS.get(template, 2)

    if template == "gru":
        # Need 4; if missing, mirror line 2 into 3 & 4 (realization)
        if len(lines) < 2:
            lines += ["…"] * (2 - len(lines))
        l2 = lines[1]
        while len(lines) < required:
            lines.append(l2)
        return lines[:required]

    # Expanding brain must be exactly 4 escalating beats
    if template == "gb":
        if len(lines) < required:
            lines += ["…"] * (required - len(lines))
        return lines[:required]

    # Generic padding/trimming for others
    if len(lines) < required:
        lines += ["…"] * (required - len(lines))
    return lines[:required]

def memegen_url(template: str, lines: List[str]) -> str:
    enc = lambda s: urllib.parse.quote(s.replace(" ", "_").replace("/", "_"))
    return f"https://api.memegen.link/images/{template}/" + "/".join(enc(x) for x in lines) + ".png"

def llm_generate(headline: str):
    # ---- Persona + Tropes + Conventions (Top 3 upgrades) ----
    templates_desc = "\n".join(
        [f"- {k} ({PANEL_COUNTS[k]}): {TEMPLATES_INFO[k]}" for k in TEMPLATES]
    )

    prompt = f"""
You are a chronically-online shitposter meme-bot with savage humor and sharp instincts.
Your mission: ROAST the news input and output a meme that actually makes people laugh.

Templates you may choose from (slug • panels • when to use):
{templates_desc}

Respond with JSON ONLY:
{{ "template": "<one-of-these-slugs>", "lines": ["..."] }}

Rules (fun > formal):
- Humor must be bold, sarcastic, absurd, or ironic. Boring = FAIL.
- Use internet-meme tropes when useful: expectation-vs-reality, doomposting, clown world, self-deprecation,
  hyperbole, plot twist, speedrun, 'has left the chat', 'rent-free', galaxy brain escalation.
- Keep each line short & punchy (≤ 9 words), no labels like "Plan:" or "Option A:".
- Match panel counts:
  drake=2; db=3; gru=4 (panels 3&4 mirror realization);
  ds=3; cmm=1; success=2; one-does-not-simply=1; gb=4.
- Be spicy as much as possible.
- Do not use unknown abbreviations so people get it.

News input: "{headline}"
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Output STRICT JSON only. No prose, no markdown, no explanations."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
        template = data.get("template", random.choice(TEMPLATES))
        if template not in TEMPLATES:
            template = random.choice(TEMPLATES)
        lines = data.get("lines", [])
        if not isinstance(lines, list):
            lines = []
    except Exception:
        template = random.choice(TEMPLATES)
        lines = ["When JSON fails", headline]

    lines = normalize_lines(template, lines)

    # tiny variety nudge so it doesn't stagnate
    if random.random() < 0.12:
        alt = [t for t in TEMPLATES if t != template]
        if alt:
            template = random.choice(alt)
            lines = normalize_lines(template, lines)

    return template, lines

@app.get("/")
def root():
    return {"ok": True, "usage": "/meme_custom?headline=Your+news+here", "templates": TEMPLATES}

@app.get("/meme_custom")
def meme_custom(headline: str):
    if not headline or not headline.strip():
        raise HTTPException(status_code=400, detail="Provide a non-empty 'headline' query param.")
    template, lines = llm_generate(headline.strip())
    return RedirectResponse(memegen_url(template, lines))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        headline = " ".join(sys.argv[1:]).strip()
        template, lines = llm_generate(headline)
        print(f"Template: {template}")
        print(f"Lines: {lines}")
        print(f"URL: {memegen_url(template, lines)}")
    else:
        print('Usage:\n  API: uvicorn app:app --reload\n  CLI: python app.py "Your news headline"')
