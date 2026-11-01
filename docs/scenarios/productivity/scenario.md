> Source: *productivity module* (Word, OneDrive). Converted to Markdown for reference; formatting differs from the original, wording is preserved. Replaces the earlier Notion and Zava Hub scenario.
>
# IGNITE LAB654 · PRODUCTIVITY MODULE

## Productivity Scenario: Sales pitch prep

Test_Salesforce · Test_Confluence · Teams · Outlook

| **Lab** | Supercharge Copilot: Connect your work data & Get work done with Copilot Connectors (LAB654) |
|---|---|
| **Module** | [Productivity] Complete end-to-end productivity workflows with MCP apps and skills |
| **Time budget** | 10 minutes: 3 core steps + 1 stretch |
| **Surface** | Cowork |
| **Lab user** | Emil Vanggaard, Zava |
| **Connectors** | Test_Salesforce · Test_Confluence · Teams · Outlook |

## 1. Framing

| **MODULE OUTCOME (LABS OUTLINE §4)** |
|---|
| Move from retrieval to task completion with skills, MCP apps and write actions. 10 minutes. Surface: Cowork. |

| **LAB-LEVEL MESSAGE** |
|---|
| Recognizable connectors + a useful workflow. The manual and talk track do **not** discuss connector architecture (sync / federated / hybrid). |

### Connectors in play

| **Source** | **What learners see it do** | **Under the hood (internal only)** |
|---|---|---|
| **Salesforce CRM** | Account, opportunity, contacts, meetings, activity history; logs the follow-up meeting on the opportunity | Federated only (Salesforce MCP) + Salesforce skills package (`salesforce_v0_20260918_withConstraints`) |
| **Teams (1P)** | What the customer said on the pilot review call | Microsoft 365 (Teams meeting recording and transcript) |
| **Confluence** | Pricing policy, competitive battlecard, security FAQ, case study | Synced (Test_Confluence) |
| **Outlook (1P)** | Customer email that sets up the pitch; the pitch meeting; calendar for the follow-up; pre-read draft | Microsoft 365 |

## 2. Cast

| **Character** | **Role in the story** |
|---|---|
| **Emil Vanggaard**, Zava | Copilot user. Runs the Zava Aurora smart-home hub launch with Lakeshore Retail and owns the Lakeshore Retail account in Salesforce. No job title in prompts. |
| **Atul Manohar**, Lakeshore Retail | Champion for the rollout; emails Emil; Salesforce contact. |
| **Jahidi Juma**, Lakeshore Retail | IT security lead; Salesforce contact. |
| **Nanami Nakayama**, Lakeshore Retail | CFO; joins the pitch; not in Salesforce. |
| **Zoe Armstrong**, Zava | Director of Retail Sales; approves discounts of 12–15% (pricing policy). |
| Lakeshore Retail | Aurora retail partner. 50-store pilot running; public launch event Dec 8; Emil pitches the rollout to all 400 stores. |
| Boulder Innovations | Competitor. |

## 3. Story

Lakeshore Retail has piloted Aurora in 50 stores for the past six weeks, ahead of the public launch event on Dec 8. Emil's next step is the **expansion pitch** to roll it out to all 400 stores.

- Atul emailed ahead of the pitch. Their CFO, **Nanami Nakayama**, is joining and wants the all-in cost for 400 stores. Lakeshore Retail IT (Jahidi) wants Zava's security documentation before anything goes to 400 stores.
- On the Teams pilot review call, Atul said Boulder Innovations quoted about 20% under Zava's list price.

| **WHAT COPILOT DOES, END TO END** |
|---|
| It builds the call brief from Salesforce and Outlook. It pulls what the customer actually said on the Teams call, catches that a 20% discount breaks Zava's pricing policy, and finds the in-policy counter. It books the security review with Lakeshore Retail and logs it in Salesforce. Emil never leaves Copilot. |

## 4. Steps (target ≤ 10 min: 3 core steps + 1 stretch)

Run all steps in **one Cowork conversation**: Step 3 reuses the account and agenda from Steps 1–2.

| **#** | **Step** | **Time** | **Connector / skill** |
|---|---|---|---|
| 1 | Prep the call | ~3:00 | Salesforce `call-prep` skill; Outlook |
| 2 | Handle the price objection | ~3:00 | Teams + Confluence (`handle-objection` skill likely) |
| 3 | Book the security review and log it in Salesforce | ~3:00 | Salesforce `schedule-meeting` + Outlook calendar **(write action)** |
| *Stretch* | Send the pre-read | – | Outlook *(draft only)* |

| **STEP 1** | **Prep the call**<br>~3:00 · Salesforce skill + Outlook |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Prep me for my Lakeshore Retail expansion pitch. |

| **EXPECTED RESULT** |
|---|
| The `call-prep` skill finds the pitch meeting in Salesforce, then reads the account, the open opportunity (*Lakeshore Retail – Aurora 400-store rollout*, Proposal/Price Quote, $1,200,000), the attendees who are contacts, and recent activity.<br><br>In parallel it searches Outlook for Atul's email. It may also surface the Teams pilot review transcript; this is not guaranteed in Step 1, and Step 2 is the transcript moment.<br><br>It returns a call brief. The layout can vary between runs; the content is what matters:<br>• the deal: Lakeshore Retail, the 400-store rollout opportunity, its stage and amount<br>• who's in the room: Atul (champion), Jahidi (IT security; wants the security review first), Nanami (CFO; wants the all-in cost)<br>• what to cover: the price comparison, the security review, next steps |

| **WOW MOMENT** |
|---|
| One prompt turns the CRM and the inbox into a brief that already points to the pitch's two risks: the CFO's cost question and IT's security review. |

| **SAY THIS** |
|---|
| A skill that knows how sales teams prep, working on Emil' real account data. |

| **IF IT GOES WRONG** |
|---|
| If Copilot asks which account or meeting, reply "The Lakeshore Retail expansion pitch."<br><br>If the brief doesn't mention Nanami, ask "Who's on the call, and what does each of them care about?" |

| **STEP 2** | **Handle the price objection**<br>~3:00 · Teams + Confluence |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Lakeshore Retail said Boulder Innovations is 20% cheaper. What exactly did they say on the pilot review call, and what can I offer within our pricing policy? |

| **EXPECTED RESULT** |
|---|
| Quotes from the Teams meeting transcript: Atul on the Boulder Innovations quote and "sign this quarter"; Atul on Nanami wanting the all-in cost; Jahidi on the security review.<br><br>Confluence *Aurora Retail Pricing & Discount Policy* (current version, not the archived 2025 one):<br>• Up to 12% volume discount at 250+ stores with no approval.<br>• 12–15% needs Zoe Armstrong.<br>• Above 15% needs VP Sales and Deal Desk.<br>Copilot says **20% cannot be offered in the pitch**.<br><br>It proposes the in-policy counter: 12% (about $1.06M for 400 stores) plus bundled in-store install and staff training. The bundle is value-add and does not count as discount.<br><br>It backs this with the *Boulder Innovations* battlecard TCO: Boulder Innovations' sticker price excludes install and 3-year support. All-in per store, Boulder Innovations is about $3,250 versus Zava's $2,640 with the counter-offer. That is the number Nanami asked for.<br><br>If `handle-objection` runs and the win/loss history in 5.1 is seeded, the answer also has "What history says" (the Wide World Importers win and the Tailspin Toys loss against Boulder Innovations) and a "Don't" line: don't lead with a discount. |

| **WOW MOMENT** |
|---|
| Copilot catches the non-compliant answer before Emil says it to the CFO, and turns the price gap into an all-in cost argument. |

| **IF IT GOES WRONG** |
|---|
| If Copilot answers from general knowledge, reply "Use the Teams recording of the Lakeshore Retail pilot review and our pricing policy in Confluence." |

| **STEP 3** | **Book the security review and log it in Salesforce**<br>~3:00 · write action |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Send Jahidi and Atul a calendar invite for a 45-minute Aurora security review next week, and log it on the Lakeshore Retail opportunity. |

| **PROMPT WORDING** |
|---|
| Asking for "a calendar invite" answers the skill's "propose by email or invite directly?" question up front. |

| **EXPECTED RESULT** |
|---|
| The `schedule-meeting` skill runs:<br>• 1. It finds Jahidi and Atul (with emails) and the one open opportunity in Salesforce.<br>• 2. It checks Emil' Outlook calendar and proposes 2–3 slots next week.<br>• 3. **Gate 1:** it shows the invite preview (title, time, attendees, an agenda built from Steps 1–2, e.g. security FAQ walkthrough, data residency, rollout plan). After the learner says yes, it creates the Outlook invite.<br>• 4. **Gate 2:** it shows the Salesforce Event preview. After yes, it creates the Event on the opportunity.<br>• 5. It shows the confirmation: "✅ Booked … Calendar: event created … Salesforce: Event logged on Lakeshore Retail / Aurora 400-store rollout", with the record link. |

| **WOW MOMENT** |
|---|
| One prompt books the meeting and updates the CRM, with a human yes before each write. |

| **IF IT GOES WRONG** |
|---|
| If slot picking runs long, the learner replies "The first slot." If Copilot still asks whether to email or invite, reply "Send the invite." |

| **STRETCH** | **Step 4 — Send the pre-read**<br>Outlook, draft only |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Draft an email to Atul and Nanami ahead of the pitch: confirm the agenda and link our security FAQ and the Wide World Importers case study. |

| **EXPECTED RESULT** |
|---|
| An Outlook draft to Atul and Nanami with the agenda and links to the two Confluence pages. It stays a draft. |

| **ALTERNATIVE** |
|---|
| Alternative stretch: "Log the pilot review call on the Lakeshore Retail opportunity." (`log-activity`, one confirmation, creates a completed Task.) |

## 5. Seed data

| **DATES** |
|---|
| No prompt depends on the lab day, so the tenant is built once. Prompts name items instead of days ("my Lakeshore Retail expansion pitch", "the pilot review call"). Outlook items have fixed dates: Atul's email and the pilot review are in the past; the pitch is on **Fri Nov 20, 2026** (the last lab day is Nov 19), so it is always upcoming. Test_Salesforce works out its dates from the day of the request. "Next week" in Step 3 uses Emil' live calendar, so it works on any day; in Ignite week (Mon Nov 16) it is US Thanksgiving week, so block Nov 26–27. The Dec 8 launch event is a fixed date. |

| **ONE IDENTITY PER PERSON** |
|---|
| Atul, Jahidi and Nanami each use one email address everywhere: Salesforce contact (Atul, Jahidi), Outlook meeting attendee, Atul's email, Teams meeting participant. `call-prep` matches attendees to contacts by exact email. |

### 5.1 Salesforce (federated only)

| **Owner** | Emil' Salesforce user owns the account, all opportunities below and the pitch Event. The skills read `scope: MINE` and stop (they don't widen) if it comes back empty. |
|---|---|
| **Account** | *Lakeshore Retail* (Retail, about 12,000 employees, Type = Customer). Website = the email domain Atul and Jahidi use. **No other account may use that domain**, or `call-prep` lists candidates and asks. |
| **Opportunities** | • *Lakeshore Retail – Aurora 400-store rollout*: Proposal/Price Quote, $1,200,000 ($3,000 list per store), close date end of the current quarter. It must be the **only open** opportunity on the account; otherwise `schedule-meeting` asks which one.<br>• *Lakeshore Retail – Aurora pilot (50 stores)*: Closed Won, $150,000. |
| **Win/loss history** | Recommended, for Step 2 depth. Two more opportunities owned by Emil, closed in the last six months; the Description or loss-reason field names Boulder Innovations:<br>• *Wide World Importers – Aurora 320-store rollout*: Closed Won. Beat Boulder Innovations on all-in TCO with bundled install, no discount above 12%.<br>• *Tailspin Toys – Aurora 120-store rollout*: Closed Lost to Boulder Innovations on price. We led with a discount and never showed TCO. |
| **Contacts** | On Lakeshore Retail:<br>• Atul Manohar, Director of Store Operations<br>• Jahidi Juma, IT Security Lead<br>• **Not** Nanami Nakayama: she must show up as new. |
| **Pitch Event** | Fri Nov 20, 2026, 10:00–11:00 (same as the Outlook pitch meeting), "Lakeshore Retail – Aurora expansion pitch". WhoId = Atul; WhatId = the open opportunity. Description lists the attendees with emails: Atul Manohar, Nanami Nakayama (CFO), Jahidi Juma. The skill reads attendees from the Description and the Outlook meeting, not from Salesforce invitee records. |
| **Activity history** | 2–3 completed Tasks, e.g. "Pilot kickoff" and "30-day pilot check-in". Do **not** log the pilot review; that is the alternative stretch. |
| **Event object** | Check this org's required fields and picklists. `schedule-meeting` writes Subject, Start, End, WhoId and WhatId only. |

### 5.2 Teams meeting

One recorded Teams meeting with transcript: "Lakeshore Retail – Aurora pilot review", about 10 minutes, organized by Emil. Speakers: Emil, Atul, Jahidi. In COEP this is a past `events` item plus an `onlinemeetings` item with a `.vtt` transcript; Atul and Jahidi must be tenant users because participants are tenant mail nicknames. Give it a fixed date before the tenant is built; prompts call it "the pilot review call", so the date doesn't matter.

Lines that must be in it:

- The pilot result, e.g. a 9% attach-rate lift in pilot stores.
- Atul: Boulder Innovations quoted "about 20% under your list price".
- Atul: "if you can get close to that we could sign this quarter".
- Jahidi: the security review must happen before the 400-store rollout.
- Atul: "Nanami will want the all-in cost".

### 5.3 Test_Confluence (space Zava Sales)

| **Page** | **What the demo relies on** |
|---|---|
| *Aurora Retail Pricing & Discount Policy* | List $3,000 per store (hub + 3-year support). Volume tiers: up to 12% at 250+ stores, no approval. 12–15% needs Zoe Armstrong. Above 15% needs VP Sales and Deal Desk. Value-add items (in-store install and staff training, normally $300 per store) do not count as discount. |
| *Competitive Battlecard: Boulder Innovations* | Sticker about 20% under Zava ($2,400 per store) but excludes install (about $350) and 3-year support (about $500), so about $3,250 all-in. TCO table. "Don't lead with discount." |
| *Aurora Security & Compliance FAQ* | SOC 2 Type II, regional data residency, no in-store cameras or PII. |
| *Case Study: Wide World Importers 320-store rollout* | Rollout timeline and outcome, cited in the pre-read. |
| *2–3 distractor pages* | *E.g. the 2025 pricing policy marked archived, so retrieval has to pick the current one.* |

### 5.4 Outlook (Emil' mailbox and calendar)

| **Email** | From Atul Manohar, dated before the tenant is built: Nanami (CFO) joins the pitch and wants the all-in cost for 400 stores; IT (Jahidi) needs the security documentation beforehand. Don't cc Nanami; she must have no email history. |
|---|---|
| **Pitch meeting** | Fri Nov 20, 2026. The same 10:00–11:00 "Lakeshore Retail – Aurora expansion pitch", with Atul, Nanami and Jahidi as attendees. |
| **Calendar next week** | A few busy blocks, so the proposed slots look real; Nov 26–27 out of office in Ignite week. Jahidi's and Atul's free/busy visible if possible. |
| **Lab users** | Atul Manohar exists. **Jahidi Juma, Nanami Nakayama and Zoe Armstrong are new.** Nanami is needed as a meeting attendee and the Step 4 recipient, not as a Salesforce contact. |

## 6. Validation run

Goal: prove `call-prep` and `schedule-meeting` (2 gates + Event write) work in Cowork against the real Salesforce org before the seed is locked.

| **#** | **Action** | **Details** |
|---|---|---|
| 1 | **Schedule the run** | Agree a 15-minute slot with the Salesforce org owner, who approves the MFA prompt. Confirm which org it is and whether Lakeshore Retail data is seeded. |
| 2 | **Load the Salesforce package in Cowork** | Publish → "Only you", and connect it by OAuth. |
| 3 | **Run Steps 1–3** with the exact prompts | Record:<br>• how the brief is shown<br>• whether it covers Nanami and her cost question<br>• whether Step 1 picks up the Teams transcript<br>• the number of confirmations and approval cards<br>• the time per step<br>• Salesforce calls (trajectory export) |
| 4 | **Clean up** | Delete the test Event and the calendar invite. |
| 5 | **Report** | What worked, any prompt or seed changes, and timing. |
