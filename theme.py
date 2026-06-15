"""Custom MO§ES dark/gold CSS — pushes past default Gradio (Off Brand badge)."""

CSS = """
:root {
  --moses-gold: #C4923A;
  --moses-bg: #15130F;
  --moses-card: #1E1B15;
  --moses-line: #3A3324;
  --moses-ink: #E8E0CF;
  --moses-dim: #8a7f68;
}
.gradio-container, .gradio-container * { font-family: ui-monospace, "SF Mono", Menlo, monospace !important; }
.gradio-container { background: var(--moses-bg) !important; max-width: 1100px !important; margin: 0 auto !important; }
.dark .gradio-container, body { background: var(--moses-bg) !important; }

#moses-hero {
  border-bottom: 1px solid var(--moses-gold);
  padding: 16px 0 20px;
  margin-bottom: 12px;
  position: relative;
}
#moses-hero h1 {
  color: var(--moses-gold) !important;
  font-size: 32px !important;
  letter-spacing: 0.16em !important;
  font-weight: 700 !important;
  margin: 0 !important;
}
#moses-hero p { color: var(--moses-dim) !important; font-size: 12px !important; margin: 6px 0 0 !important; }
/* stat strip */
#moses-stat-strip {
  display: flex; gap: 24px; margin-top: 10px;
  font-size: 11px; color: var(--moses-dim); letter-spacing: 0.04em;
}
#moses-stat-strip span { color: var(--moses-ink); font-weight: 700; }

.tabs, .tabitem { background: transparent !important; border: none !important; }
button.selected { color: var(--moses-gold) !important; border-bottom: 2px solid var(--moses-gold) !important; }
.tab-nav button { color: var(--moses-dim) !important; font-size: 13px !important; letter-spacing: 0.06em; }

.dataframe, table { background: var(--moses-card) !important; color: var(--moses-ink) !important;
  border: 1px solid var(--moses-line) !important; font-size: 12px !important; }
.dataframe thead th, table thead th { background: var(--moses-bg) !important; color: var(--moses-gold) !important;
  border-bottom: 1px solid var(--moses-gold) !important; font-size: 10px !important;
  letter-spacing: 0.06em !important; text-transform: uppercase; padding: 8px 6px !important; }
.dataframe tbody td, table tbody td { border-bottom: 1px solid var(--moses-line) !important;
  color: var(--moses-dim) !important; padding: 8px 6px !important; }
.dataframe tbody tr:first-child td, table tbody tr:first-child td { color: var(--moses-ink) !important;
  background: rgba(196,146,58,0.08) !important; }

input, textarea, .gr-input, .gr-text-input {
  background: var(--moses-bg) !important; color: var(--moses-ink) !important;
  border: 1px solid var(--moses-line) !important; font-family: ui-monospace, monospace !important; }
input:focus, textarea:focus { border-color: var(--moses-gold) !important; box-shadow: 0 0 0 1px var(--moses-gold) !important; }
label span { color: var(--moses-dim) !important; font-size: 12px !important; letter-spacing: 0.04em; }

button.primary, .gr-button-primary, #compute-btn {
  background: var(--moses-gold) !important; color: var(--moses-bg) !important;
  border: none !important; font-weight: 700 !important; letter-spacing: 0.06em !important; }
button.primary:hover, #compute-btn:hover { background: #d8a449 !important; }

#moses-profile { background: var(--moses-card) !important; border: 1px solid var(--moses-line) !important;
  border-radius: 10px !important; padding: 4px 18px !important; }
#moses-profile h2 { color: var(--moses-gold) !important; letter-spacing: 0.08em; }
#moses-profile blockquote { border-left: 3px solid var(--moses-gold) !important; color: var(--moses-ink) !important;
  background: rgba(196,146,58,0.06); padding: 10px 14px; margin: 10px 0; }
#moses-profile table { font-size: 12px !important; }
#moses-profile th, #moses-profile td { color: var(--moses-ink) !important; }

.prose, .md, #moses-foot { color: var(--moses-dim) !important; font-size: 11px !important; }
#moses-foot { border-top: 1px solid var(--moses-line); padding-top: 10px; margin-top: 16px; line-height: 1.7; }

.moses-board { font-family: ui-monospace, monospace; margin-top: 6px; }
.mb-head, .mb-row { display: grid; grid-template-columns: 28px 1.6fr 0.6fr 0.6fr 0.6fr 0.75fr 0.7fr 1.4fr;
  align-items: center; gap: 8px; padding: 9px 8px; }
.mb-head { color: #C4923A; font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase;
  border-bottom: 1px solid #C4923A; }
.mb-row { border-bottom: 1px solid #3A3324; color: #8a7f68; font-size: 12px; }
.mb-row.you { background: rgba(196,146,58,0.10); color: #E8E0CF; }
.mb-row.you b { color: #C4923A; }
.mb-row.rank1 {
  border-left: 3px solid var(--moses-gold);
  background: rgba(196,146,58,0.12) !important;
  color: var(--moses-ink) !important;
}
.mb-row.rank1 .mb-yval { color: var(--moses-gold); font-size: 14px; }
.mb-rank-1 { color: var(--moses-gold); font-weight: 700; }
.mb-rank-2 { color: #a0a0a0; }
.mb-rank-3 { color: #8a6a3a; }
.mb-row b { color: #E8E0CF; font-family: var(--font-sans, sans-serif); font-size: 13px; }
.mb-raw { color: #7a7060; font-size: 9.5px; }
.mb-num { text-align: right; }
.mb-y { position: relative; display: flex; align-items: center; justify-content: flex-end; gap: 6px; min-height: 20px; }
.mb-bar { position: absolute; left: 0; top: 50%; transform: translateY(-50%); height: 14px;
  background: linear-gradient(90deg, rgba(196,146,58,0.28), rgba(196,146,58,0.72)); border-radius: 2px; }
.mb-row.you .mb-bar { background: linear-gradient(90deg, rgba(196,146,58,0.4), #C4923A); }
.mb-yval { position: relative; z-index: 2; color: #E8E0CF; font-weight: 700; font-size: 12px; padding-right: 4px; }
.mb-foot { color: #5f573f; font-size: 10.5px; padding: 10px 8px 0; line-height: 1.6; }

/* composition bar */
.comp-bar { display: flex; height: 6px; border-radius: 3px; overflow: hidden; margin: 6px 0 10px; width: 100%; }
.comp-read { background: var(--moses-gold); }
.comp-create { background: #8a6a3a; }
.comp-output { background: #5a7a5a; }
.comp-input { background: #3a4a5a; }

/* trading card */
.sig-card {
  width: 380px; min-height: 500px;
  background: linear-gradient(160deg, #1E1B15 60%, #2a2318);
  border: 1px solid var(--moses-gold);
  border-radius: 12px;
  padding: 28px 24px 20px;
  font-family: ui-monospace, monospace;
  position: relative;
  box-shadow: 0 0 40px rgba(196,146,58,0.12), inset 0 1px 0 rgba(196,146,58,0.2);
}
.sig-card-watermark {
  position: absolute; top: 14px; right: 16px;
  font-size: 9px; color: var(--moses-dim); letter-spacing: 0.1em;
}
.sig-card-name { color: var(--moses-gold); font-size: 22px; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 4px; }
.sig-card-archetype {
  display: inline-block; font-size: 10px; letter-spacing: 0.08em;
  border: 1px solid var(--moses-gold); color: var(--moses-gold);
  padding: 2px 8px; border-radius: 2px; margin-bottom: 20px; text-transform: uppercase;
}
.sig-card-yield { font-size: 52px; font-weight: 700; color: var(--moses-ink); line-height: 1; }
.sig-card-yield-label { font-size: 10px; color: var(--moses-dim); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 20px; }
.sig-card-rank { font-size: 13px; color: var(--moses-dim); margin-bottom: 16px; }
.sig-card-rank span { color: var(--moses-ink); font-weight: 700; }
.sig-card-cascade {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; margin-bottom: 16px;
}
.sig-card-cascade-box {
  border: 1px solid #3A3324; padding: 4px 8px; border-radius: 3px;
  color: var(--moses-ink); text-align: center; min-width: 52px;
}
.sig-card-cascade-box small { display: block; color: var(--moses-dim); font-size: 9px; }
.sig-card-cascade-arrow { color: var(--moses-dim); }
.sig-card-quote {
  font-size: 11px; color: var(--moses-dim);
  border-left: 2px solid var(--moses-gold);
  padding: 8px 12px; margin-top: 16px; line-height: 1.5;
  font-style: italic;
}
.sig-card-footer {
  position: absolute; bottom: 16px; left: 24px; right: 24px;
  font-size: 9px; color: #5f573f; letter-spacing: 0.06em;
  border-top: 1px solid #3A3324; padding-top: 8px;
  display: flex; justify-content: space-between;
}

footer { display: none !important; }

@media (max-width: 700px) {
  .mb-head, .mb-row {
    grid-template-columns: 22px 1fr 0.5fr 0.5fr 1fr;
    font-size: 11px;
  }
  /* hide velocity and leverage columns on mobile */
  .mb-head span:nth-child(5), .mb-head span:nth-child(6),
  .mb-row span:nth-child(5), .mb-row span:nth-child(6) { display: none; }
}
"""
