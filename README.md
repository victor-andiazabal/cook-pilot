# Cook Pilot — AI Cooking Assistant

Point your camera at the fridge. Dinner writes itself.

Cook Pilot turns photos of whatever is in your kitchen into three tailored, cookable recipes — with allergies treated as hard safety constraints — then walks you through cooking step by step with built-in timers.

**[▶ Live demo](https://victor-andiazabal.github.io/cook-pilot/)** (bring your own Anthropic API key — it stays in your browser)

<!-- Add a screenshot or GIF here: -->
<!-- ![Cook Pilot demo](screenshots/demo.png) -->

## What it does

1. **Photograph your ingredients** — straight from the phone camera or gallery (up to 5 photos)
2. **AI vision identifies them** — including reading labels on packaged products, with confidence flags on anything uncertain
3. **You confirm and correct** the list — human-in-the-loop before anything is generated
4. **Set constraints** — allergies (hard rules), dietary preferences, cuisine, time limit, calories, servings, skill level, available equipment, free-text notes
5. **Get three genuinely different recipes** — Fastest / Best match / Wild card
6. **Cook with guided mode** — one step at a time, per-step ingredient chips, real timers that survive screen lock, screen wake-lock while cooking
7. **Rate, save, repeat** — feedback and saved recipes persist locally

## Architecture

Following the classic GenAI application pattern:

```
User → UI (web, hosted locally) → Backend (Python/Flask) → OpenAI API
```

- **Frontend** — React (single bundled file), mobile-first, Marmiton-inspired palette
- **Backend** — `app.py`: hosts the UI, converts the UI's content blocks (text + base64 images) into OpenAI chat format, calls `gpt-4o-mini` (vision + generation), returns structured JSON
- **Two-stage generation** — one cheap call produces three compact recipe cards; the full recipe is only generated when a card is opened (token/cost control)
- **Client-side image compression** before upload (max 1400 px, JPEG q0.82) to cut tokens

## Safety design

Generative models hallucinate, so the app never trusts raw output:

- **Human-in-the-loop** — the user validates the ingredient list before generation; low-confidence detections are flagged for review
- **Structured output + validation** — the model must return strict JSON; classical code validates and repairs it (including recovering from invalid JSON like `"quantity": to taste`) before anything is displayed
- **Deterministic allergen double-check** — every recipe is re-scanned against an allergen synonym table (so "dairy" also catches parmesan, "gluten" catches soy sauce); conflicts trigger a prominent warning
- **Standing disclaimer** — AI-generated recipes may contain errors; users are told to check labels, especially for serious allergies

## Iterative prompt engineering

The recipe engine was refined through an adversarial critique loop — each generated recipe was reviewed by a separate LLM acting as a professional recipe critic, and recurring failures were encoded back into the prompt as general rules:

| Version | Failure found | Rule added |
|---------|---------------|------------|
| v2 | Invalid JSON (`"quantity": to taste`) | Numeric-only quantities + automatic JSON repair |
| v3 | Phantom equipment (unused microwave), empty allergen lines | Equipment must match the method; hidden allergens named (e.g. kimchi → fish sauce) |
| v5 | Dishes named "stir-fry" that weren't; flat flavour profiles; 30 g of sesame garnish | Honest naming; complete flavour profile (aromatics/umami/fat/acid); sane per-serving quantities; no fixed salt with salty ingredients |
| v6 | Whole chicken with one flat cooking time; pineapple steaming the skin soggy | Weight-based timing + thermometer + visual doneness check; moisture management (wet ingredients never under food that must crisp) |

Recipe quality (as scored by the critic) went from unusable JSON errors to 8/10 "café-worthy" output.

## Run it locally

```bash
git clone https://github.com/victor-andiazabal/cook-pilot.git
cd cook-pilot
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."   # Windows: $env:OPENAI_API_KEY="sk-..."
python3 app.py
```

Open **http://127.0.0.1:5001** (port 5001 because macOS AirPlay occupies 5000).

## Live demo notes

The GitHub Pages demo (`docs/`) is a serverless variant that calls the Anthropic API directly from the browser. It asks for **your own** API key, which is stored only in your browser's localStorage — nothing is sent anywhere except to the model provider. Without a key, the interface is fully browsable but AI features are disabled.

## Limitations & future work

- No accounts or server-side persistence (prototype scope: saved recipes live in browser storage)
- Recipe knowledge is generative, not retrieved — a RAG layer over a real recipe corpus would ground quantities and techniques further
- Rate limiting and monitoring would be required before public hosting of the backend

## Tech stack

React · Flask · OpenAI API (gpt-4o-mini, vision) · esbuild · Tailwind
