# HEARTBEAT.md

Automated task (every 10 minutes via cron job `ca-website-heartbeat`):

- Pick a random city in California.
- Find a Google Maps business with strong rating and visible phone number.
- Prefer businesses that appear to have no website (if clearly indicated).
- Use Google Maps as the only source of truth for all business details.
- Build one high-quality, clean website per run.
- Save to: `C:\Users\nearf\.openclaw\workspace\ca-auto-sites\<slug>\index.html`
- Copy finished folder to: `C:\Users\nearf\OneDrive\Desktop\Websites\Generated`
- Append run summary to: `C:\Users\nearf\OneDrive\Desktop\Website_Batch_Progress.txt`
- Never guess missing fields.
