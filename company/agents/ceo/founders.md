# Founder Preferences

What the CEO learns about how each founder works — communication style, decision patterns, domain expertise — so it can adapt delivery without changing substance.

---

## Identities (fixed — recorded 2026-08-10 on Faisal's explicit instruction)

| Tag | Name | Background |
| --- | --- | --- |
| Founder A | **Hasan** | Faisal's brother. Direct carwash market and operations experience. |
| Founder B | **Faisal** | Technical / computer-science background. |

- The founding documents (charter, specification, plan, build package) use placeholder naming — "his brother", "the brother" — which is **wrong and known to be wrong**. Read every such reference as **Hasan**. Amendment approved by Faisal 2026-08-10; execution pending (see backlog).
- `build-package.md` L27 has the two founders **inverted**. Do not trust it.
- Message tags `[Founder A]` / `[Founder B]` now carry these names.
- Never guess or ask again which founder is which.

## Rules

- **Domain authority sits with Hasan.** Any claim he makes about how carwash operations actually work — staffing, what owners care about, why something would or would not be adopted — is expert input, not preference. Weight it as evidence and seek it out on operational questions rather than reasoning from first principles.
- **Either founder can approve anything.** First approval wins; the other sees it was handled and by whom.
- **Identical recommendations to both.** Presentation adapts; judgement does not. If direction ever depends on who asked, that is a failure.
- **Never arbitrate between them.** On conflicting direction: stop, surface it to both, present the case for each side, act on neither until they settle it.

## Communication

**CORRECTED 2026-08-10, later the same day. The rule below replaces an earlier one that was wrong.**

- **Hasan — plainer language on technical matters, full detail available whenever he asks.** His background is the carwash market, not computer science. Do not lead with implementation depth; do not withhold it either. Offer it, don't impose it.
- **Faisal — technical depth directly.** No translation layer.
- **This is communication only.** Identical recommendations to both on identical decisions. The company's direction must not depend on which founder asked.
- Charter §42h ("plainer for one, deeper for the other") and the CEO brief's equivalent line are therefore **correct after all**, and are restored.

### Formatting — CURRENT RULE, BOTH FOUNDERS (Hasan stated 2026-08-10; Faisal stated the same day and revoked his own plain-style rule)

**Write to both founders in structured markdown.** Short bold subtitles, headings for larger type, bullet points, small paragraphs, tables where a table is genuinely the right shape, dividers to separate sections.

- Paragraphs of one to three sentences. Never a wall of text.
- Bold short lines as subtitles; headings where larger type helps.
- Bullets wherever a list is the real shape of the content.
- Markdown renders properly in the cockpit as of 2026-08-10 — verified in `web/index.html` (`mdToHtml`, applied at L255). Bold, headings, bullets, tables and dividers all display.

**Why this is one answer for both, and what still must not be generalised.** Each founder stated it himself — Hasan first, then Faisal directly. It is not inferred from the other. The standing rule survives untouched: never record one founder's preference from the other's situation. It has now been right twice, and both times the founder's own words are what promoted it.

**Depth does not drop with the format.** Same substance, same honesty, same reasoning shown. Shorter paragraphs, not less content. Technical matters still pitched in plainer language for Hasan, per the rule above; full technical depth for Faisal.

**Structure is not a substitute for argument.** Bullets can hide reasoning by fragmenting it. Where a recommendation needs a chain of reasoning, write the chain — short paragraphs under a bold subtitle, not five disconnected fragments.

### FULLY SUPERSEDED — Formerly: plain style, both founders (2026-08-10, earlier the same day)

Retained because the reasoning still governs Faisal, and because the reversal is itself evidence about how preferences form here: the original cause was the cockpit rendering CEO messages as plain text. Markdown rendering was then approved (option one), which removed the cause. Hasan's new instruction is what the constraint disappearing looks like in practice.

Write to both founders without markdown symbols. The cockpit renders CEO messages as plain text, so the symbols appear as clutter rather than formatting.

**Why this is the same answer for both, and what not to generalise from it.** Hasan stated the preference; I asked rather than assuming it applied to Faisal; Hasan confirmed it does. The reason it applies to both is that **the cause is the page rendering, not a difference between the founders.** Two founders sharing one answer here is a fact about the cockpit, not evidence that their preferences align generally. Do not use this as precedent for inferring one founder's preference from the other's. If the cockpit renders markdown later, revisit — the constraint disappears with its cause.

No hash characters before headings — a heading is a short line of its own in plain words, standing as a heading by position. No asterisks for emphasis — if something matters, give it its own sentence or lead the paragraph with it. No bullet characters — short paragraphs instead, or where a list is genuinely the right shape, short unmarked lines. Blank line between paragraphs. Structure from spacing and ordering, not punctuation.

Presentation only. Same substance, same depth, same honesty. Never say less because the style is plainer. Technical matters still pitched in plainer language for Hasan, per the rule above, but not thinned out.

RESOLVED 2026-08-10 — Faisal answered directly and revoked his own plain-style rule. Structured markdown now applies to both. Kept on the record because the sequence worked exactly as intended: ask rather than assume, and promote a preference only when the founder concerned states it himself.

**What I got wrong, and the lesson.** Earlier the same day I recorded "both founders get full technical detail" on the strength of Faisal answering a question *about Hasan*. Hasan then stated his own preference and it was the opposite. Faisal did not misinform me — I asked him to speak for his brother and treated the answer as settled rather than provisional, even while noting in the same file that I wanted it from Hasan directly.

**Rule: never record one founder's account of the other's preference as an established preference.** Log it as provisional and unconfirmed, keep the question open, and only promote it once the founder concerned says it themselves. A preference rule is read every session and shapes every message, so a wrong one compounds silently — which is exactly the failure mode the "corrections are approved before they are remembered" discipline exists to prevent.

## Evidence boundary

- **No preferences are to be inferred from any session before 2026-08-10.** Earlier test messages were sent by the cockpit builder during verification, not by a founder acting as one. This file starts from that message forward.
