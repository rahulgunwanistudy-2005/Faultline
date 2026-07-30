# Judge Mode Specification

## Goal

A judge can understand Faultline’s problem, mechanism, proof, and action in 30 seconds without touching the mouse.

## Timeline

| Time | Screen | Caption | Required event |
|---:|---|---|---|
| 0–3s | Teacher quote over paper stack | “She did everything right. Over half still failed.” | Quiet hook, no logo animation |
| 3–8s | Stack upload | “Scores show who is wrong. Faultline finds the procedure causing it.” | Pages segment and answers appear |
| 8–14s | Class map | “This class is not one problem. It is three different problems.” | Three action lanes form |
| 14–21s | Student evidence | “Every candidate procedure is executed against the actual worksheet.” | Matches illuminate |
| 21–25s | Prediction | “Now it predicts an answer the student has not submitted to the system.” | Prediction card locks |
| 25–28s | Reveal | “The held-out work matches.” | Real crop reveals |
| 28–30s | Tomorrow card | “When evidence is split, we ask the questions that buy the most information.” | Three questions appear |

## Implementation

- Route: `/judge` or `/?judge=1`
- State machine driven by a single timeline file.
- Preload all fixture data and images.
- Disable external OCR during Judge Mode.
- Visible controls: pause, restart, skip to live app.
- Captions are real text, not baked into video.
- Add a small “Demo data” badge to avoid misrepresentation.

## Video reuse

The submission video can use the middle 24 seconds of Judge Mode, but the final video should still include the speaker’s hook, methodology sentence, evaluation proof, and close.
