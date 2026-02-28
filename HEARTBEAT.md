# HEARTBEAT.md

## Heartbeat Task: Florida Local Business Website Builder

When triggered by the heartbeat prompt, do **one** full cycle below.

### Goal
Pick a random place in Florida, find one real business that appears to have no website, and produce a high-quality long-form website draft in the workspace.

### Workflow (every heartbeat run)
1. Pick a random Florida city/town (different from recent runs when possible).
2. Find candidate businesses using web search/maps/listings.
3. Verify “no website” with reasonable confidence:
   - listing/profile has no website field, and
   - at least one web search for the business name + city shows no official domain.
4. If confidence is low, skip and pick another business.
5. Create a project folder:
   - `outreach/florida-sites/YYYY-MM-DD-<city>-<business-slug>/`
6. Save research notes in `research.md`:
   - business name, category, city
   - evidence for “no website”
   - any contact/public listing links
   - confidence notes and assumptions
7. Build a long, high-quality website draft (no placeholders):
   - `index.html` (multi-section, polished copy, clear CTAs)
   - `styles.css` (modern responsive styling)
   - `script.js` (small UX enhancements if useful)
   - Required sections/features to include on every site:
     - Hero section
     - Services
     - “Why Choose Us”
     - Ratings summary with visible star rating display
     - Customer reviews/testimonials (mark clearly as sample if drafted/invented)
     - Gallery (“Our Gallery”)
     - Service area/location details
     - Interactive Google Map embed (or clearly marked map placeholder if embed is unavailable)
     - Contact info (phone/email/address when publicly available)
     - Contact methods (“where to contact us”)
     - Business hours / best times to visit (“when to come in”)
     - FAQ section
     - Strong contact/CTA section
8. Add `README.md` with:
   - what was built
   - what content is factual vs drafted/assumed
   - next steps before publishing
9. Do **not** contact the business or publish externally.
10. Append a one-paragraph summary to today’s `memory/YYYY-MM-DD.md`.

### Guardrails
- Never fabricate factual claims as real; label assumptions/drafts clearly.
- Prefer neutral, professional copy.
- Keep all work local unless explicitly told to send/publish.
