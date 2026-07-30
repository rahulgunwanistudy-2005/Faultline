# Visual System — “Paper, Signal, Faultline”

## Design intent

Beautiful, calm, and evidence-led. Avoid the standard hackathon palette of neon purple gradients, glass cards, floating blobs, and a chatbot sidebar.

## Tokens

```css
:root {
  --paper: #F7F1E8;
  --paper-strong: #FFFDF8;
  --ink: #171717;
  --muted: #6E6A63;
  --fault: #E15B3D;
  --signal: #2E6F65;
  --amber: #D59A2D;
  --line: #D8D0C3;
  --shadow: 0 18px 50px rgba(30, 24, 18, 0.10);
  --radius-card: 20px;
  --radius-control: 12px;
}
```

## Typography

- Display: a confident editorial serif or expressive humanist face.
- UI: a highly legible sans-serif.
- Use large numbers and short phrases; never shrink text to fit analytics.
- Mathematical expressions use a dedicated math renderer and monospaced fallback.

## Signature motif

A thin irregular “fault line” runs through the class map and branches where student procedures diverge. It is functional: selecting a branch filters the student group. Do not animate it constantly.

## Motion

- Page stack settles with subtle physical movement.
- Analysis stages progress like ink moving across a line.
- Prediction reveal uses a single decisive split-screen transition.
- Respect `prefers-reduced-motion`.

## Layout rules

- Maximum two major panels on screen.
- One primary action per state.
- Evidence is progressively disclosed.
- Class map uses whitespace, not borders everywhere.
- Never show more than four colors with semantic meaning.
- No chart without a question it answers.

## Plain-language copy examples

Use:

- “7 students are adding the top numbers and bottom numbers separately.”
- “The evidence is split. Ask these three questions before deciding.”
- “The math procedure looks intact; wording may be the barrier.”

Avoid:

- “Emerging proficiency cluster”
- “Mastery trajectory”
- “AI-powered personalized insights”
- “Holistic learning analytics”
