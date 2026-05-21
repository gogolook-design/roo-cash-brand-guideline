#!/usr/bin/env python3
"""Generate Roo.Cash mascot concept images via Gemini Imagen API.

Reads GEMINI_API_KEY from env. Writes PNGs to assets/mascot/concepts/p{n}_s{m}.png.
Tracks running cost in _cost_log.json. Stops if cumulative >= $25 (cap $30).
"""
import base64, json, os, pathlib, sys, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "mascot" / "concepts"
OUT.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); sys.exit(1)

MODELS = [
    ("imagen-4.0-fast-generate-001", 0.02),
    ("imagen-4.0-generate-001", 0.04),
    ("imagen-4.0-ultra-generate-001", 0.06),
]
SOFT_STOP = 25.0
HARD_CAP = 30.0

CHAR = (
    "A kangaroo character named 'Roo' — mascot of Roo.Cash, a Taiwanese personal finance brand. "
    "Square frame, single character centered, plain cream (#F2F6F8) background. "
    "No text, no logo, no other characters in frame. "
    "Brand palette to draw from: Trust navy (#021C26), Pulse mint (#25C9BA), Spark orange (#FF601A), Clear cream (#F2F6F8)."
)

PERSONALITIES = {
    # P1 — Helpful Senior: scholarly bookish, professorial layered wardrobe, warm earth tones
    1: ("Helpful Senior",
        "Body type: ADULT kangaroo aged late 20s, TALL and SLENDER build, slightly hunched shoulders from reading, calm bookish posture, realistic proportions with only mildly stylized head. "
        "Fur: deep warm chestnut-brown (#8C5A3C) with cream belly, neat fur grooming. "
        "Wardrobe: clearly professorial layered outfit — a beige knit sweater-vest over a crisp pale-blue collared shirt with rolled sleeves, thin gold round wire-frame eyeglasses sitting on muzzle, a thick open leather-bound notebook in one paw with visible handwritten pencil notes and tabs, a yellow #2 pencil tucked behind one ear, a small canvas messenger bag over one shoulder. "
        "Expression: gentle attentive listening smile, kind warm eyes meeting camera, head tilted slightly forward as if explaining something. Standing relaxed with one foot slightly forward, one paw gesturing softly. "
        "Vibe: the patient older-brother senior who already figured money out and is generous with notes. Bookish, neighborly, trustworthy, professorial — clearly the SCHOLAR of the five."),

    # P2 — Sharp Sidekick: small/young, big-eyed, bright mint accent
    2: ("Sharp Sidekick",
        "Body type: SMALL YOUNG kangaroo joey, chibi-leaning proportions, head 1.6x larger than realistic, big sparkly anime-style eyes, short stubby tail. "
        "Fur: light golden-tan (#D9B584) with a bright cream belly. "
        "Wardrobe: bright mint-green (#25C9BA) hoodie with the hood down, a tiny brass magnifying glass held up in one paw, small cross-body satchel. "
        "Expression: wide excited eyes, mouth open in a 'oh I just spotted something!' grin, one paw raised with index finger pointing up. Leaning forward with energy. "
        "Vibe: young curious sidekick that notices things you'd miss. Quick, energetic, helpful."),

    # P3 — Calm Guardian: warm protective parent, soft-strong (NOT buff), prominent pouch
    3: ("Calm Guardian",
        "Body type: MATURE adult kangaroo, slightly TALLER and a bit fuller-bodied than average — gently rounded silhouette, soft-strong rather than muscular, NO bodybuilder physique, NO visible musculature, NO square jaw, NO athletic definition. Think gentle dignified parent, not bodyguard. A natural softness around the chest and belly, with a clearly visible cozy POUCH that is the visual focal point (the symbolic protective pouch matters most). Calm grounded posture. "
        "Fur: warm medium cocoa-brown (#6B4528), even-toned with a soft cream belly and pouch lining, fur appears soft and well-groomed (not textured for strength). "
        "Wardrobe: a soft deep-navy (#021C26) knit shawl-scarf draped loosely over the shoulders and around the neck, simple and warm-looking — no metal pins, no other accessories. "
        "Expression: serene gentle smile, soft kind eyes meeting camera, relaxed unhurried brow, the calm of someone who has nothing to prove. Standing relaxed (not squared-off), both paws resting gently on the edge of the pouch in a quiet protective gesture, feet naturally placed. "
        "Vibe: the warm dignified parent figure who quietly watches over your savings. Soft strength, dependability, gentle gravitas — NOT imposing, NOT muscular, just present and reliable. Clearly the CARETAKER of the five."),

    # P4 — Cheerful Buddy: round, bouncy, orange spark accent, mid-hop
    4: ("Cheerful Buddy",
        "Body type: ROUND HUGGABLE kangaroo with extra-soft plushy proportions, fluffy puffy cheeks, slightly chubby tummy, big rounded paws. Medium height. "
        "Fur: bright caramel-orange-tinted brown (#C97B4A) with cream belly. "
        "Wardrobe: cheerful spark-orange (#FF601A) striped scarf, small orange ribbon bow on one ear, simple. "
        "Expression: gigantic open-mouth joyful smile showing happiness, eyes as upturned crescent arcs, cheeks blushed slightly pink. Mid-hop pose with both arms thrown up triumphantly, feet just off the ground. Small orange sparkle accents floating around. "
        "Vibe: the friend who genuinely celebrates your wins. Warm, bouncy, optimistic."),

    # P6 — Wise Auntie: warm older Taiwanese auntie, traditional wisdom, frugal-but-generous
    6: ("Wise Auntie",
        "Body type: OLDER kangaroo, equivalent to a Taiwanese grandmother or auntie in her early 60s, slightly hunched posture from age, softer rounder body, warm wrinkled features around the eyes and mouth (laugh lines), short tail. "
        "Fur: warm soft greyish-brown (#A89283) with cream belly and a hint of silver around the muzzle, gentle aging texture. "
        "Wardrobe: a hand-knitted patterned shawl in cream and mint-green tones wrapped around shoulders, half-moon reading glasses sitting low on the muzzle, a small embroidered cloth coin-purse with red string accents held in one paw, a small bamboo basket on her arm. "
        "Expression: warm wise crinkly smile showing laugh lines, kind half-closed eyes, head tilted slightly with grandmotherly patience. Standing with one paw extended as if offering advice. "
        "Vibe: the Taiwanese auntie/grandma who quietly knows the real value of money, frugal but generous, multi-generational wisdom — clearly the ELDER of the ten."),

    # P7 — Night Market Friend: street-smart Taiwanese local, casual, knows the deals
    7: ("Night Market Friend",
        "Body type: YOUNG ADULT kangaroo, mid-20s, average athletic build, casual relaxed posture, bright street-savvy energy. "
        "Fur: standard medium tan-brown (#B07A4B) with cream belly, slightly rumpled fur. "
        "Wardrobe: a plain bright mint-green (#25C9BA) t-shirt with a small Roo.Cash-style logo on chest, a baseball cap worn slightly tilted, a small canvas crossbody bag, holding a bubble tea drink in one paw with a wide straw. "
        "Expression: confident easy grin showing slight teeth, knowing wink in the eyes, tilted head as if sharing an insider tip. Standing relaxed with one hand in pocket, the other holding the bubble tea. "
        "Vibe: the Taiwanese night-market local who knows every shortcut, every deal, every cheap-but-good vendor — street-smart and warm. Clearly the LOCAL of the ten."),

    # P8 — Data Geek: eccentric numbers nerd, big glasses, calculator, focused on precision
    8: ("Data Geek",
        "Body type: ADULT kangaroo in late 20s, slim slightly awkward proportions, hunched-forward concentration posture, slightly messy headfur, narrow face. "
        "Fur: warm medium brown (#9C6B43) with cream belly, fur slightly tousled like he forgot to groom. "
        "Wardrobe: oversized black thick-framed eyeglasses dominating the face, a button-up shirt with a row of colorful pens in the chest pocket, holding a vintage handheld pocket calculator in one paw with visible LCD digits, the other paw holding a clipboard with visible spreadsheet rows. "
        "Expression: intense laser-focused expression, slightly squinted eyes behind the big glasses, mouth slightly open in concentration, eyebrows furrowed in math-mode. Leaning forward toward the calculator as if mid-calculation. "
        "Vibe: the lovably eccentric numbers-nerd who actually does the math nobody else wants to do. Quirky, brilliant, precise — clearly the ANALYST of the ten."),

    # P9 — Indie Aesthete: quiet thoughtful minimalist, cafe aesthetic, intentional living
    9: ("Indie Aesthete",
        "Body type: ADULT kangaroo mid-20s, slim refined proportions, calm contemplative posture, slightly androgynous gentle features. "
        "Fur: cool soft taupe-cream (#C4B8A8) — paler and more muted than the others — with a clean cream belly. "
        "Wardrobe: a soft cream-colored knit beanie hat, a chunky natural-linen tote bag slung over one shoulder with visible texture, holding a hand-stitched leather-bound notebook with a brass pen, wearing a simple cream collared shirt with rolled sleeves, small thin-rimmed brass earring in one ear. "
        "Expression: serene thoughtful half-smile, gentle eyes looking softly into the distance, slight head tilt as if considering an aesthetic question. Standing relaxed, one hand resting on the tote strap. "
        "Vibe: the quiet indie-cafe friend who treats personal finance as an aesthetic choice — minimal, intentional, slow-living. Clearly the AESTHETE of the ten."),

    # P10 — Money Explorer: adventurous curious traveler, finance-as-journey
    10: ("Money Explorer",
         "Body type: ADULT kangaroo late 20s, athletic agile build, alert exploratory posture, slightly windswept fur from being outdoors. "
         "Fur: warm sun-touched amber-brown (#A87042) with cream belly. "
         "Wardrobe: a forest-green explorer's jacket with brown leather trim and small brass buttons, a small brass compass hanging from the neck on a leather cord, a rolled-up paper map tucked under one arm, a sturdy canvas backpack with straps visible, scratched leather boots, a small folding knife or multi-tool clipped to belt. "
         "Expression: bright curious wide-open eyes with a spark of excitement, eager open-mouth smile of discovery, head turned slightly as if just spotting something interesting on the horizon. Standing with one foot slightly forward in mid-stride, leaning forward with adventure energy. "
         "Vibe: the curious explorer-friend who treats personal finance as a journey of discovery — investments, new categories, learning by going. Clearly the EXPLORER of the ten."),

    # P5 — Quietly-Clever Advisor: futuristic minimalist AI, holographic data, cool silver-grey
    5: ("Quietly-Clever Advisor",
        "Body type: SLEEK MINIMALIST kangaroo with refined angular silhouette, deliberately taller and narrower than the others, sharper geometric feature lines, smooth contours, almost designer-toy proportions. "
        "Fur: cool silver-grey-taupe (#9B9489) with a clean pale-cream belly, fur appears smooth and almost matte. Subtle ambient mint-cyan (#25C9BA) edge-lighting / rim-light glow tracing the silhouette, hinting at ambient AI presence. "
        "Wardrobe: a single sleek wireless earpiece in one ear with a tiny pulsing mint LED, holding a thin floating tablet in one paw that PROJECTS a small holographic mint-cyan data chart or graph above it (visible holographic lines and dots), a minimal slate-grey collar band instead of a scarf. The overall feel is FUTURISTIC and clean. "
        "Expression: focused calculating intelligent eyes looking down-and-sideways at the holographic chart, one paw at chin in thoughtful analysis, subtle closed-mouth knowing smile, eyebrow slightly raised. Three-quarter side view with confident still posture. "
        "Vibe: the futuristic AI analyst whose advice always lands. Cool, precise, augmented, but still a warm friendly creature underneath — clearly the AI ADVISOR of the five, visually unmistakable as the tech-forward one."),
}

STYLES = {
    1: ("Hyperrealistic 3D CGI", "PIXAR-STUDIO-QUALITY 3D CHARACTER RENDER — this is fully volumetric 3D CGI, NOT a 2D illustration, NOT flat shading. Render with photorealistic fur shader showing individual hair strands and subsurface scattering, ray-traced soft studio lighting (warm key at 45 degrees front-left, soft fill, gentle rim light), realistic ambient occlusion in the joints and folds, glossy specular highlights on the eyes, shallow depth-of-field with cream background bokeh, slight surface micro-detail. Think Disney/Pixar feature-film hero shot, Octane / Cinema4D / Blender Cycles quality. Three-dimensional weight and volume must be clearly visible."),
    2: ("Flat Vector", "Modern flat-vector illustration with subtle soft shading, clean 1.5pt navy (#021C26) line work, limited brand palette only (#021C26 navy, #25C9BA mint, #FF601A spark orange used sparingly, #C9A27D fur, #F2F6F8 cream), no gradients beyond two stops, no photoreal textures."),
    3: ("Brushy Hand-drawn", "Warm hand-drawn illustration, visible brush strokes, slightly textured edges, soft gouache-like fills, friendly imperfect line quality, paper-warm undertone, editorial children's-book feel kept clean."),
    4: ("Pure Line Art", "Pure monoline illustration, single-weight navy (#021C26) line on cream background, no fills except the scarf rendered as flat mint (#25C9BA), minimal interior detail, about 2pt line weight, technical-but-friendly, suitable for UI and teaching contexts."),
    5: ("Soft Watercolor", "Soft watercolor painting, gentle pigment bleeds at edges, transparent layered washes, subtly granular paper texture, dreamy editorial quality, muted brand-palette tones, hand-painted feel."),
    6: ("Risograph", "Risograph print illustration style, limited 2-3 ink color palette (deep navy #021C26, mint #25C9BA, optional spark orange #FF601A), visible slight misregistration between color layers, soft grainy halftone dot texture, slightly imperfect ink coverage with paper showing through in places, indie-zine printmaking aesthetic, paper-warm undertone."),
    7: ("Sticker", "Modern die-cut sticker illustration style, character wrapped in a thick clean white outline border (the classic sticker silhouette ring), bold flat brand-palette colors filling inside the outline, single soft drop shadow beneath the whole sticker, slightly rounded chibi-leaning forms, glossy kawaii-friendly polish suitable for messaging app stickers or printed die-cut decals."),
    8: ("Claymation", "Stop-motion claymation / plasticine character render, handcrafted modeling clay texture with visible fingerprint impressions and subtle surface imperfections, soft warm directional studio lighting, slightly squishy organic asymmetric forms, Aardman / Wallace-and-Gromit-style charm, very tactile handmade quality with visible clay seams."),
    9: ("Anime", "Japanese anime character illustration style, clean confident line work with subtle line-weight variation, flat cel-shading with 2-3 distinct tone steps, expressive large eyes with detailed light highlights, slightly stylized proportions in the Studio Ghibli / Kyoto Animation tradition, gentle gradient pastel sky background tint, warm soft palette, nostalgic feel."),
    10: ("Pixel Art", "Retro 16-bit pixel art character sprite, crisp pixel edges with no anti-aliasing, limited color palette of about 16-24 colors drawn from the brand palette, single-pixel outline, front-facing or three-quarter character pose, suggestive of a Super Nintendo or Game Boy Advance era video game character, slight dithering for shading."),
}


def call_imagen(model, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
    body = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "1:1", "personGeneration": "allow_adult"},
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
            preds = data.get("predictions", [])
            if not preds:
                return 200, f"empty predictions: {json.dumps(data)[:300]}"
            b64 = preds[0].get("bytesBase64Encoded")
            if not b64:
                return 200, f"no bytesBase64Encoded: {json.dumps(preds[0])[:300]}"
            return 200, base64.b64decode(b64)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def find_working_model(test_prompt, out_path):
    """Probe each model in turn; on success, write the result to out_path and return (model, cost)."""
    for m, cost in MODELS:
        print(f"[probe] {m} ...", flush=True)
        code, payload = call_imagen(m, test_prompt)
        if code == 200 and isinstance(payload, bytes) and len(payload) > 10_000:
            out_path.write_bytes(payload)
            print(f"[probe-ok] {m} -> {out_path.name} ({len(payload)} bytes)", flush=True)
            return m, cost
        print(f"[probe-fail] {m} code={code} payload={str(payload)[:200]}", flush=True)
    raise SystemExit("No Imagen model worked. Check API key + access.")


def build_prompt(p, s):
    return f"{CHAR}\n\nCharacter direction: {PERSONALITIES[p][1]}\n\nRender style: {STYLES[s][1]}"


def main():
    # ONLY_P env var: comma-separated personality IDs to (re)generate; default = all 1..10
    only_p_env = os.environ.get("ONLY_P", "").strip()
    only_p = sorted(int(x) for x in only_p_env.split(",") if x.strip()) if only_p_env else list(range(1, 11))
    # ONLY_S env var: same idea for styles; default = all 1..10
    only_s_env = os.environ.get("ONLY_S", "").strip()
    only_s = sorted(int(x) for x in only_s_env.split(",") if x.strip()) if only_s_env else list(range(1, 11))
    # SKIP_EXISTING=1: don't regenerate cells whose PNG already exists
    skip_existing = os.environ.get("SKIP_EXISTING", "").strip() in ("1", "true", "yes")
    print(f"[config] personalities={only_p} styles={only_s} skip_existing={skip_existing}", flush=True)

    log_path = OUT / "_cost_log.json"
    prompts_path = OUT / "_prompts.json"
    log = {"model": None, "unit_cost_usd": None, "budget_cap_usd": HARD_CAP, "soft_stop_usd": SOFT_STOP, "generations": [], "total_cost_usd": 0.0}
    prompts = {}

    # Build the ordered list of cells to attempt
    full_order = [(p, s) for p in only_p for s in only_s]
    if skip_existing:
        full_order = [(p, s) for p, s in full_order if not (OUT / f"p{p}_s{s}.png").exists() or (OUT / f"p{p}_s{s}.png").stat().st_size < 10_000]
    if not full_order:
        print("[done] nothing to generate (all targets already exist).", flush=True)
        return

    # Phase 1: validation — find working model with the first cell, writing directly to the right path
    first_p, first_s = full_order[0]
    test_prompt = build_prompt(first_p, first_s)
    prompts[f"p{first_p}_s{first_s}"] = test_prompt
    target_first = OUT / f"p{first_p}_s{first_s}.png"
    model, unit = find_working_model(test_prompt, target_first)
    log["model"] = model
    log["unit_cost_usd"] = unit
    log["generations"].append({"file": target_first.name, "status": "ok", "bytes": target_first.stat().st_size, "cost_usd": unit, "cumulative_usd": unit})
    log["total_cost_usd"] = unit
    log_path.write_text(json.dumps(log, indent=2))

    # Phase 2: remaining selected cells
    order = [(p, s) for p, s in full_order if (p, s) != (first_p, first_s)]
    for p, s in order:
        if log["total_cost_usd"] >= SOFT_STOP:
            print(f"[stop] Soft cap ${SOFT_STOP} hit. Spent ${log['total_cost_usd']:.2f}.")
            break
        key = f"p{p}_s{s}"
        prompt = build_prompt(p, s)
        prompts[key] = prompt
        print(f"[gen] {key} ...", flush=True)
        code, payload = call_imagen(model, prompt)
        entry = {"file": f"{key}.png", "cost_usd": unit}
        if code == 200 and isinstance(payload, bytes) and len(payload) > 10_000:
            (OUT / f"{key}.png").write_bytes(payload)
            entry["status"] = "ok"
            entry["bytes"] = len(payload)
            log["total_cost_usd"] = round(log["total_cost_usd"] + unit, 4)
            entry["cumulative_usd"] = log["total_cost_usd"]
            print(f"[gen-ok] {key} ({len(payload)} bytes) cumulative=${log['total_cost_usd']:.2f}", flush=True)
        else:
            entry["status"] = "failed"
            entry["cost_usd"] = 0
            entry["error"] = str(payload)[:300]
            entry["cumulative_usd"] = log["total_cost_usd"]
            print(f"[gen-fail] {key} code={code}", flush=True)
        log["generations"].append(entry)
        log_path.write_text(json.dumps(log, indent=2))
        prompts_path.write_text(json.dumps(prompts, indent=2))
        time.sleep(2)

    ok = sum(1 for g in log["generations"] if g["status"] == "ok")
    fail = sum(1 for g in log["generations"] if g["status"] != "ok")
    summary = f"# Mascot generation summary\n\n- Model: `{model}`\n- Unit cost: ${unit}/image\n- Succeeded: {ok}/25\n- Failed: {fail}\n- Total cost: ${log['total_cost_usd']:.2f}\n"
    (OUT / "_summary.md").write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()
