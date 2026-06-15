"""
Narration layer — MiniCPM4-0.5B (openbmb, 0.5B params, <=4B cap).
OPTIONAL and NON-BLOCKING: if the model can't load, a deterministic
template narration is used instead. The app never depends on it.
Unlocks: Tiny Titan badge (<=4B), Best MiniCPM sponsor, small-model track.
"""
MODEL_ID = "openbmb/MiniCPM4-0.5B"
try:
    import spaces
    GPU = spaces.GPU
except Exception:
    def GPU(*a, **k):
        def wrap(f): return f
        return wrap(a[0]) if a and callable(a[0]) else wrap
_model = None
_tok = None
_tried = False

def _try_load():
    global _model, _tok, _tried
    if _tried:
        return _model is not None
    _tried = True
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        _tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto",
            trust_remote_code=True)
        return True
    except Exception as e:
        print(f"[narrate] model unavailable, using template fallback: {e}")
        return False

def _template(name, m, klass):
    v, l = m["velocity"], m["leverage"]
    if m["non_compounding"]:
        body = (f"{name} runs a stateless pipe - no cache commits, so the "
                f"cascade can't form. High read volume, but nothing is being "
                f"built forward. Leverage {l:,.1f}x comes from reuse alone.")
    elif v >= 1 and l >= 100:
        body = (f"{name} holds both axes at once: {v:.1f}x generation AND "
                f"{l:,.0f}x memory leverage. A closed kinetic loop - the rare "
                f"operator the leverage/generation tradeoff says shouldn't exist.")
    elif l >= 10 and v < 1:
        body = (f"{name} is an archival sponge - {l:,.0f}x reuse but only "
                f"{v:.2f}x generation. Holds context beautifully, executes little "
                f"with it. The reuse number is inflated by a weak commitment stage.")
    elif v >= 0.8 and l < 2:
        body = (f"{name} is a volatile ingestor - {v:.2f}x generation but "
                f"{l:.1f}x leverage. Fast on single shots, resets between turns. "
                f"Memory doesn't persist into a compounding loop.")
    else:
        body = (f"{name} sits low on both axes: {v:.2f}x generation, {l:.1f}x "
                f"leverage. A transient profile - neither building state nor "
                f"converting input to output efficiently.")
    return f"**{klass}.** {body}"

@GPU
def narrate(name, m, klass):
    if not _try_load():
        return _template(name, m, klass)
    try:
        v, l, snr = m["velocity"], m["leverage"], m["snr"]
        dev = f"{m['dev10x']:.2f}" if m['dev10x'] is not None else "none (stateless)"
        prompt = (
            "You are a terse systems analyst for a token-economy leaderboard. "
            "In 2-3 sentences, characterize this AI coding operator from its "
            "metrics. Be specific and a little vivid. Do not list the numbers back.\n"
            f"Operator: {name}\nClass: {klass}\n"
            f"Generation (output/input): {v:.2f}x\n"
            f"Memory leverage (read/input): {l:.1f}x\n"
            f"Signal (output share): {snr:.2f}\n"
            f"Cascade amplification: {dev}\n")
        msgs = [{"role": "user", "content": prompt}]
        inputs = _tok.apply_chat_template(msgs, add_generation_prompt=True,
                                          return_tensors="pt").to(_model.device)
        out = _model.generate(inputs, max_new_tokens=110, temperature=0.7,
                              do_sample=True, top_p=0.9)
        text = _tok.decode(out[0][inputs.shape[1]:], skip_special_tokens=True).strip()
        return f"**{klass}.** {text}" if text else _template(name, m, klass)
    except Exception as e:
        print(f"[narrate] generation failed, template fallback: {e}")
        return _template(name, m, klass)
