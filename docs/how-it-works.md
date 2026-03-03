# How Alkemist Works

Simple explanation of what happens when you ask Alkemist a question.

---

## The Basic Flow

When you ask Alkemist for help:

1. **You ask** — "How do I read a file in Python?"
2. **Alkemist thinks** — (4 stages, see below)
3. **AI responds** — Suggests code and explains it
4. **Everything stays on your computer** — No cloud involved

---

## The 4 Thinking Stages

Alkemist uses a smart 4-stage process (called "Logic Ladder") that's better than simple AI chatbots:

### Stage 1: Awareness
**What it does:**  Looks through your code to understand context
**Why:** So it can give suggestions that fit YOUR code, not just generic answers
**Example:** Sees you're using React, so suggests React patterns

### Stage 2: Literalist  
**What it does:** Understands exactly what you're asking
**Why:** So it doesn't misinterpret vague questions
**Example:** You ask "make it faster" → Alkemist figures out if you mean faster loading, faster code, or faster development

### Stage 3: Congress
**What it does:** Debates the answer from multiple angles
- **Advocate** → Suggests a solution
- **Skeptic** → Finds problems with it
- **Synthesizer** → Combines the best parts

**Why:** More thorough thinking = better code
**Example:** 
- Advocate: "Use threads for speed"
- Skeptic: "That's dangerous in Python"
- Synthesizer: "Use `concurrent.futures` instead"

### Stage 4: Judge
**What it does:** Makes a final decision and writes the code
**Why:** Ensures the answer is complete and tested

---

## Why This is Better Than Other AI

| Approach | Problem | Example |
|----------|---------|---------|
| **Simple AI** | Gives the first answer, even if wrong | You ask "make it concurrent" → gets generic thread example that crashes |
| **Cloud AI** | Costs money, data goes to vendors | Each question costs $0.10, code leaks to OpenAI |
| **Alkemist** | Thinks deeply, stays private | Debates the answer, gives safe code, runs on your computer |

---

## Where Does the AI Come From?

Alkemist uses **Ollama**, which runs open-source AI models locally:

- **Models:** Mistral, Llama, Deepseek (you can choose)
- **Cost:** $0 (runs on your computer)
- **Privacy:** Never sent to the cloud
- **Speed:** Depends on your computer's CPU/GPU

---

## What's NOT Shared with the Cloud?

✅ Your code — stays on your computer  
✅ Your questions — never leave your machine  
✅ Your data — never uploaded anywhere  
✅ Your prompts — local only  

The ONLY thing Ollama might do: Check for model updates (can be disabled).

---

## When You Ask a Question

Here's what actually happens:

```
You: "How do I parse JSON in Python?"
        ↓
[Stage 1] Looks through YOUR files → sees what libraries you use
        ↓
[Stage 2] Understands you want to parse JSON specifically
        ↓
[Stage 3] Debates:
   - Advocate: "Use json.loads()"
   - Skeptic: "What if the JSON is invalid?"
   - Synthesizer: "Use json.loads() with try/except"
        ↓
[Stage 4] Gives you final answer with working code
        ↓
You: (Sees code suggestion) ✅ Use it or modify it
```

**All of this happens on your computer. Nothing leaves your office.**

---

## The Key Difference

| Tool | What Happens to Your Code |
|------|--------------------------|
| Cursor | Sent to Anthropic's servers |
| GitHub Copilot | Sent to Microsoft's servers |
| **Alkemist** | **Stays on your computer** |

---

## How Local AI is Possible

1. **Ollama** — Downloads AI models (like downloading software)
2. **Models** — Run directly on your CPU/GPU (no internet needed after download)
3. **Your machine** → Does all the thinking locally
4. **Result** → You get suggestions, nothing leaves your room

It's like having a helpful programmer in a box that never talks to anyone else.

---

## FAQ

**Q: Is the AI as good as ChatGPT?**  
A: It's different. ChatGPT knows more facts (because it's trained on the whole internet). Alkemist thinks more carefully about your specific code. For programming, Alkemist often wins.

**Q: Will it work offline?**  
A: Yes! After downloading the AI model, you can unplug from the internet and Alkemist still works.

**Q: Can I use my own AI model?**  
A: Yes. Alkemist can run any model that Ollama supports. You can add your own specialized models.

**Q: How much space does it need?**  
A: ~15GB for a decent AI model + your code. Less than a video game.

---

## Next Steps

- 🚀 [Get Started](getting-started.md) — Set up Alkemist now
- 💻 [Contributing](../CONTRIBUTING.md) — Help improve it
- 🏗️ [Architecture](architecture.md) — Technical details
