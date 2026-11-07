# RISKS (every risk has an automated guard and a one-line residual-risk note; checked by tools/risk_check.py in CI)

| Risk | Automated guard | Residual risk |
|---|---|---|
| YouTube "inauthentic content" | Freshness rules (style seed rotation, history.json), cross-video similarity, uploads PRIVATE until owner approves | Policy changes are outside our control |
| Advertiser-friendly / harmful content | validator content blocklist, survival facts need an official source, honest title/thumbnail | Blocklist is keyword based; owner reviews before publishing |
| Made-for-kids misclassification | upload sets madeForKids=false; teen/adult themes | YouTube may still classify cartoons as kids content |
| AI disclosure | cartoon visuals only, never realistic people/events; description states AI narration | Owner must set the altered-content flag if realism is ever added |
| API quota / private-only uploads | quota-aware publisher (1,600 + 50 + 400 units per video), defers to next Pacific-time day, can skip captions | Unverified projects may force private (intended) |
| Wrong facts | every fact needs an exact number + source URL, verified against the page when written | Pages change; re-verify evergreen facts yearly |
| GitHub terms / account | no cron, no polling, one account, real tests + docs + CHANGELOG, matrix capped, artifacts 3 days | Heavy Actions use could still be rate limited |
| Public repo exposure | git-crypt on jobs/ voices/ inbox/ reference/ history.json, facts/review files; pre-commit + pre-push + CI blob check; age on artifacts/releases; secret scanning + push protection | Pilot content is public by design; key loss = data loss (offline backup) |
| CPU too slow | benchmark.yml, matrix sharding, fallbacks, never lower quality | A 30-min video needs many parallel runners |
| Model or library disappears | pinned versions, content-hash caches, fallback chain in config | Pins need periodic refresh; pip hashes pending |
| Copyright / Content ID | prompt denylist, original synthesised music/SFX, OFL/Apache fonts, licence manifest | Owner-supplied tracks must stay no-attribution |
| Claude Pro limits | token-lean commands, `continue` resumes from docs/PROGRESS.md | none |
| Lost work | mirror.yml (manual) + offline key backup | Owner must keep both keys offline |
| Token/secret leak | settings deny key reads, risk-check secret patterns, never print secrets | Human error when pasting secrets |
