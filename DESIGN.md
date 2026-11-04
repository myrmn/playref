# PlayRef: Design Brief (for Google Stitch)

How to use: paste **Section 1 (Design System)** into Stitch first, then paste each prompt from **Section 3** one at a time (one screen per generation). Generate desktop and mobile variants. Export to Figma/code, and give the result to the AI IDE at Phase 3 as visual reference (`docs/design/` screenshots + exported HTML/CSS).

---

## 1. Design System

**Product:** PlayRef, an AI football assistant that explains the Laws of the Game with official citations. Trustworthy like a referee's handbook, friendly like a modern chat app. Not a betting/hype site.

**Mood:** calm, authoritative, clean, a little sporty. Think "referee notebook meets modern AI chat". Lots of whitespace, subtle pitch-inspired accents, never cluttered.

**Colors**
- Primary (pitch green): `#0F7B4B`; hover `#0B6139`; tint `#E6F4EC`
- Accent (referee yellow card): `#F5C400`, used sparingly for "Experimental" and warnings
- Danger (red card): `#D7263D`, only for errors and "wrong law cited"
- Neutrals: background `#F8FAF9`, surface `#FFFFFF`, border `#E3E8E5`, text `#16211B`, muted text `#5E6B64`
- Dark mode: background `#0E1512`, surface `#16201B`, border `#26332C`, text `#EAF2ED`, primary `#2FB878`

**Typography**
- Latin: Inter (UI), headings semi-bold. Arabic: IBM Plex Sans Arabic or Cairo.
- Scale: 12 / 14 / 16 / 18 / 24 / 32. Body 16, line-height 1.6. Rule text in citation drawer uses a slightly larger serif-free reading size (17px).

**Shape and spacing:** 8px grid, card radius 16px, chips fully rounded, soft shadows (low opacity), 1px borders.

**Components**
- Message bubble (user: green tint, right; assistant: white card, left, full-width answer card)
- Answer card with 4 sections: Short answer, Applicable Laws, Possible interpretations (collapsible), What would change the decision (collapsible)
- Citation chip: rounded pill, small book icon, text like "Law 12 - Handball", hover shows tooltip
- Citation drawer: slides from the right (left in RTL), shows Law number badge, section path breadcrumb, exact rule text, page + edition, "Open in Law browser"
- "Experimental" badge: yellow pill with flask icon
- Disclaimer footer: small muted text
- Upload button (paperclip) with drag-and-drop zone, thumbnail preview, remove button
- Stage indicator: "Searching the Laws -> Checking rules -> Writing answer" with subtle animated dots
- Feedback row: thumbs up/down + "Wrong law cited" link

**Icons:** Lucide, 1.5px stroke. No football emojis in UI chrome; a small whistle or pitch-line logo mark only.

**Logo idea:** wordmark "PlayRef" with a minimal whistle or a rectangle-with-center-circle pitch mark in primary green.

**Language and direction:** English, French, Arabic. Arabic is full RTL: layout mirrors, drawers slide from the left, chips and icons flip where directional. Language switcher (EN / FR / AR) in the top bar.

**Accessibility:** contrast AA, focus rings (2px green), 44px touch targets on mobile, keyboard navigable.

---

## 2. Global rules for every screen
- Always show a subtle disclaimer: "PlayRef explains the Laws and possible interpretations. It does not make official decisions."
- Never show a verdict style UI (no big green "PENALTY" / red "NO PENALTY" banners).
- Responsive: design desktop (1440) and mobile (390) versions.

---

## 3. Screen prompts (paste one at a time)

### Screen 1: Empty chat / home
Design the home screen of PlayRef, a football Laws of the Game assistant. Top bar: logo left, language switcher EN/FR/AR, theme toggle, "Law browser" link. Center: a friendly headline "Ask anything about the Laws of the Game", a short subline "Answers grounded in the official IFAB Laws, with citations." Below it a large chat input with a paperclip button (with tooltip "Upload image or video, experimental") and send button. Under the input, 6 suggested prompt cards in a 2x3 grid: "Explain offside", "Is deliberate handball always a foul?", "What is DOGSO?", "Can a goalkeeper score from a goal kick?", "When is advantage applied?", "What counts as a professional foul?". Footer disclaimer. Use pitch green and white, spacious, modern.

### Screen 2: Chat with a streaming answer
Show an active conversation. User message on the right in light green. Assistant reply as a full-width white answer card with: a "Short answer" paragraph; "Applicable Laws" as clickable citation chips ("Law 12 - Handball", "Law 12 - Fouls and Misconduct"); a collapsed accordion "Possible interpretations"; a collapsed accordion "What would change the decision"; an "Assumptions" muted list; and a feedback row (thumbs up, thumbs down, "Wrong law cited"). While streaming, show a stage indicator "Checking the rules..." and a stop button. Sticky input at the bottom.

### Screen 3: Citation drawer open
Same chat screen with a right-side drawer open (480px wide) after clicking a citation chip. Drawer header: large badge "Law 12", title "Fouls and Misconduct", breadcrumb "Direct free kick > Handball". Body: the exact rule text in a comfortable reading size with highlighted key phrases, then metadata row: "Page 104 · Edition 2026/27 · IFAB Laws of the Game". Footer buttons: "Open in Law browser", "Copy citation". Chat dimmed behind it.

### Screen 4: Clarifying question state
Assistant answer card where the bot needs more info. Highlighted callout (yellow-tinted) "I need one more detail:" with the question "Did the ball touch the defender's arm before or after it was played by the attacker?" and 3 quick-reply buttons (Before / After / Not sure) plus free text input. Below, a small "Assumptions I made" list.

### Screen 5: Image upload (experimental)
Chat screen with an image attached. Input area shows a thumbnail preview with remove (x). A yellow "Experimental" badge with flask icon and helper text "Image analysis can't determine official decisions." After sending, the assistant card begins with a collapsible "What I saw" panel listing neutral observations (location on pitch, ball visible, arm position, uncertainty items marked "unclear"), followed by the standard answer card. Also a drag-and-drop overlay state "Drop your image or video here".

### Screen 6: Video upload and progress
Upload modal/panel for a short clip (max 15 s, 20 MB): video preview with a timeline slider to mark the "key moment" (optional), then a progress stepper: Uploading -> Extracting frames -> Analyzing frames (4/10) -> Checking the Laws -> Done. Show the resulting "Timeline" view: horizontal list of frame thumbnails with timestamps and a one-line neutral observation under each. "Experimental" badge visible.

### Screen 7: Law browser
Two-pane layout. Left: searchable list of the 17 Laws (number badge + title) with an expandable section tree. Right: reading pane showing the selected Law's text with sticky section breadcrumb, anchor links, and an "Ask PlayRef about this section" button on each section. Search field at top with highlighted matches.

### Screen 8: Arabic RTL version
Redesign Screen 2 in Arabic, fully mirrored RTL: user message on the left, drawer opens from the left, chips and icons mirrored, Arabic font (IBM Plex Sans Arabic), Arabic UI text. Keep Law numbers and citations readable (e.g. "القانون 12 - لمسة اليد").

### Screen 9: Mobile (390px)
Mobile versions of the home screen, chat answer, and citation drawer (as a bottom sheet with drag handle). Bottom-pinned input with paperclip and send. Collapsible top bar with hamburger for Law browser and language switcher.

### Screen 10: States and edge cases
One sheet showing: loading skeleton for the answer card, error state ("Something went wrong. Try again."), rate-limit message ("You're asking fast, please wait a few seconds"), off-topic redirect message ("I can help with football rules. Try asking about offside or fouls."), and "Not covered by the Laws" abstention card with a gentle suggestion.

### Screen 11: Feedback modal (optional)
Small modal after "Wrong law cited": radio options (Wrong law, Missing law, Answer unclear, Other), optional comment, submit button, thank-you confirmation.

---

## 4. After Stitch: hand-off to the AI IDE
1. Export screenshots of every screen to `docs/design/` (desktop, mobile, RTL, dark mode) and the exported HTML/CSS or Figma link into `docs/design/README.md`.
2. In the Phase 3 prompt, add: "Match the visual design in `docs/design/` and the tokens in `docs/DESIGN.md` Section 1. If a screen is missing, follow the design system and ask me."
3. Create `frontend/src/styles/tokens.css` (or the Tailwind theme) from the Section 1 colors, fonts and radii before building components.
