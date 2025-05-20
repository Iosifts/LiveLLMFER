# app.py  ▸  cumulative word-cloud version
from flask import Flask, request, send_file, abort
from wordcloud import WordCloud
from collections import deque
import io, os, threading, textwrap
import re
from rembg import remove
import base64
from PIL import Image   # (Pillow is installed automatically with rembg)



# master vocab we want to visualise
EMOTION_LEXICON = {
    # Positive Emotions
    "joy", "love", "amusement", "gratitude", "excitement", "admiration", "affection",
    "approval", "caring", "contentment", "compassion", "desire", "enthusiasm",
    "euphoria", "hope", "inspiration", "interest", "kindness", "optimism", "pride",
    "relief", "satisfaction", "serenity", "trust", "cheerfulness", "confidence",

    # Negative Emotions
    "anger", "annoyance", "anxiety", "betrayal", "contempt", "disappointment",
    "disapproval", "disgust", "embarrassment", "envy", "fear", "frustration", "guilt",
    "grief", "hurt", "jealousy", "loneliness", "panic", "rage", "regret", "remorse",
    "resentment", "sadness", "shame", "worry", "rejection", "pity", "nervousness",

    # Ambiguous or Cognitive Emotions
    "confusion", "curiosity", "surprise", "realization", "awe", "boredom", "hesitation",
    "uncertainty", "puzzlement", "ambivalence", "intrigue", "mixed",

    # Intensity and Mood Qualifiers
    "neutral", "positive", "negative", "mild", "moderate", "intense", "extreme",
    "strong", "weak", "overwhelming", "subtle", "suppressed", "flat", "calm",
    "agitated", "relaxed", "tense", "tired", "alert", "focused", "distracted",

    # Identity and Context Tags
    "man", "woman", "male", "female", "adult", "child", "elderly",
    "unknown", "human", "individual",

    # Expression Tags
    "smiling", "frowning", "laughing", "crying", "blinking", "squinting", "yawning",
    "gazing", "glancing", "clenching", "staring", "expressionless",

    # Special Use-Case States
    "pain", "fatigue", "burnout", "mania", "depression", "stimulation", "flat affect"
}


# compiled once → faster
WORD_RE = re.compile(r"[A-Za-z]+")

def pick_keywords(text: str) -> list[str]:
    """
    From arbitrary free text, return ONLY the words that
    match our emotion lexicon (case-insensitive).
    """
    words = WORD_RE.findall(text.lower())
    return [w for w in words if w in EMOTION_LEXICON]

# ---------- basic Flask setup ----------
BASE_DIR = os.path.dirname(__file__)
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path=""
)

# ---------- thread-safe caption store ----------
# deque is fast and has a maxlen so the list never explodes
CAPTIONS      = deque(maxlen=500)          # keep last 5 000 captions (~hundreds KB)
CAPTIONS_LOCK = threading.Lock()            # because Flask may be multi-threaded


def strip_bg(data_url: str) -> bytes:
    """
    data_url → PNG bytes with transparent background.
    Uses rembg (U-2-Net) to remove the background.
    """
    # remove the “data:image/...;base64,” header
    b64_data = data_url.split(",", 1)[1]
    # run background removal
    return remove(base64.b64decode(b64_data))


# ---------- routes ----------
@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/wordcloud", methods=["POST"])
def api_wordcloud():
    data = request.get_json(force=True, silent=True)
    if not data or not (txt := data.get("text", "").strip()):
        abort(400, "No text provided")

    # NEW → filter the model’s free text
    keywords = pick_keywords(txt)
    if not keywords:                 # nothing worth keeping
        return send_file(io.BytesIO(), mimetype="image/png")

    with CAPTIONS_LOCK:
        CAPTIONS.extend(keywords)    # store words, not whole caption
        corpus = " ".join(CAPTIONS)

    wc = WordCloud(
        width=800, height=400,
        background_color="white",
        colormap="PuBuGn"            # nicer palette
    ).generate(corpus)

    img_io = io.BytesIO()
    wc.to_image().save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")



@app.route("/wordcloud/reset", methods=["POST"])
def api_reset_cloud():
    """Optional helper – POST here to clear the history."""
    with CAPTIONS_LOCK:
        CAPTIONS.clear()
    return {"status": "cleared"}, 200


@app.route("/favicon.ico")
def empty_favicon():
    return "", 204

@app.route("/api/segment", methods=["POST"])
def api_segment():
    """
    Accepts JSON { "image": "<data-URL>" } and returns a PNG
    (image/png) in which the background is transparent.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "image" not in data:
        abort(400, "No image provided")

    try:
        png_bytes = strip_bg(data["image"])
        return send_file(io.BytesIO(png_bytes), mimetype="image/png")
    except Exception as e:
        abort(500, f"Segmentation failed: {e}")


# ---------- run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
