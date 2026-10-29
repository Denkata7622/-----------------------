"""config.py — единствен източник на пътища."""
from pathlib import Path

PIPELINE_DIR   = Path(__file__).parent.resolve()
PROJECT_ROOT   = PIPELINE_DIR.parent
GENERATED_ROOT = PROJECT_ROOT / "generated"

ARTICLES_DIR   = GENERATED_ROOT / "articles"
ANCHORS_DIR    = GENERATED_ROOT / "anchors"
CACHE_DIR      = GENERATED_ROOT / "cache"
EXTRACTED_DIR  = CACHE_DIR / "extracted"
MERGED_DIR     = CACHE_DIR / "merged"
CLASSIFIED_DIR = CACHE_DIR / "classified"
OCR_CACHE_DIR  = CACHE_DIR / "ocr"
LOGS_DIR       = GENERATED_ROOT / "logs"
STATE_DIR      = GENERATED_ROOT / "state"

CHUNKER_STATE_FILE  = STATE_DIR / "chunker_state.json"
# ВАЖНО: pipeline.py пише в pipeline/state.json (legacy път), не в STATE_DIR.
# Държим го тук за да е ясно на master_orchestrator и daily_verifier къде да четат.
PIPELINE_STATE_FILE = PIPELINE_DIR / "state.json"
PROBLEM_STATE_FILE  = STATE_DIR / "problem_state.json"
GAP_STATE_FILE      = STATE_DIR / "gap_state.json"

STEPS_FILE = PROJECT_ROOT / "data" / "steps.js"
HTML_FILE  = PROJECT_ROOT / "index.html"

for d in [ARTICLES_DIR, ANCHORS_DIR, EXTRACTED_DIR, MERGED_DIR,
          CLASSIFIED_DIR, OCR_CACHE_DIR, LOGS_DIR, STATE_DIR]:
    d.mkdir(parents=True, exist_ok=True)