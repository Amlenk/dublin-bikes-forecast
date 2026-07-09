"""Phase 5 Step 1: run the Phase-4 artifact OFFLINE on the golden input
(tests/fixtures/golden_input.json) and print the prediction to 4
decimals. Recorded before any serving code changes."""
import json
from pathlib import Path

import joblib
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
bundle = joblib.load(REPO / "model" / "artifacts" / "model_v1.joblib")
feats = json.loads((REPO / "tests" / "fixtures" / "golden_input.json").read_text())
cols = bundle["feature_columns"]
X = pd.DataFrame([[feats[c] for c in cols]], columns=cols)
print(f"golden_prediction={bundle['model'].predict(X)[0]:.4f}")
