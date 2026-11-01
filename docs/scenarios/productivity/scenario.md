> Source: *productivity module* (Word, OneDrive). Converted to Markdown for reference; formatting differs from the original, wording is preserved. Replaces the earlier Notion and Verdantis Hub scenario.
>
# IGNITE LAB654 · PRODUCTIVITY MODULE

## Productivity Scenario: Sales pitch prep

Test_Salesforce · Test_Confluence · Teams · Outlook

| **Lab** | Supercharge Copilot: Connect your work data & Get work done with Copilot Connectors (LAB654) |
|---|---|
| **Module** | [Productivity] Complete end-to-end productivity workflows with MCP apps and skills |
| **Time budget** | 10 minutes: 3 core steps + 1 stretch |
| **Surface** | Cowork |
| **Lab user** | Marcus Hollowell, Verdantis |
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
| **Marcus Hollowell**, Verdantis | Copilot user. Runs the Verdantis Aurora smart-home hub launch with Contoso Retail and owns the Contoso Retail account in Salesforce. No job title in prompts. |
| **Riley Blake**, Contoso Retail | Champion for the rollout; emails Marcus; Salesforce contact. |
| **Ken Liu**, Contoso Retail | IT security lead; Salesforce contact. |
| **Priya Nair**, Contoso Retail | CFO; joins the pitch; not in Salesforce. |
| **Lena Okafor**, Verdantis | Director of Retail Sales; approves discounts of 12–15% (pricing policy). |
| Contoso Retail | Aurora retail partner. 50-store pilot running; public launch event Dec 8; Marcus pitches the rollout to all 400 stores. |
| Fabrikam Home | Competitor. |

## 3. Story

Contoso Retail has piloted Aurora in 50 stores for the past six weeks, ahead of the public launch event on Dec 8. Marcus's next step is the **expansion pitch** to roll it out to all 400 stores.

- Riley emailed ahead of the pitch. Their CFO, **Priya Nair**, is joining and wants the all-in cost for 400 stores. Contoso IT (Ken) wants Verdantis' security documentation before anything goes to 400 stores.
- On the Teams pilot review call, Riley said Fabrikam Home quoted about 20% under Verdantis' list price.

| **WHAT COPILOT DOES, END TO END** |
|---|
| It builds the call brief from Salesforce and Outlook. It pulls what the customer actually said on the Teams call, catches that a 20% discount breaks Verdantis' pricing policy, and finds the in-policy counter. It books the security review with Contoso and logs it in Salesforce. Marcus never leaves Copilot. |

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
| Prep me for my Contoso Retail expansion pitch. |

| **EXPECTED RESULT** |
|---|
| The `call-prep` skill finds the pitch meeting in Salesforce, then reads the account, the open opportunity (*Contoso Retail – Aurora 400-store rollout*, Proposal/Price Quote, $1,200,000), the attendees who are contacts, and recent activity.<br><br>In parallel it searches Outlook for Riley's email. It may also surface the Teams pilot review transcript; this is not guaranteed in Step 1, and Step 2 is the transcript moment.<br><br>It returns a call brief. The layout can vary between runs; the content is what matters:<br>• the deal: Contoso Retail, the 400-store rollout opportunity, its stage and amount<br>• who's in the room: Riley (champion), Ken (IT security; wants the security review first), Priya (CFO; wants the all-in cost)<br>• what to cover: the price comparison, the security review, next steps |

| **WOW MOMENT** |
|---|
| One prompt turns the CRM and the inbox into a brief that already points to the pitch's two risks: the CFO's cost question and IT's security review. |

| **SAY THIS** |
|---|
| A skill that knows how sales teams prep, working on Marcus' real account data. |

| **IF IT GOES WRONG** |
|---|
| If Copilot asks which account or meeting, reply "The Contoso Retail expansion pitch."<br><br>If the brief doesn't mention Priya, ask "Who's on the call, and what does each of them care about?" |

| **STEP 2** | **Handle the price objection**<br>~3:00 · Teams + Confluence |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Contoso said Fabrikam is 20% cheaper. What exactly did they say on the pilot review call, and what can I offer within our pricing policy? |

| **EXPECTED RESULT** |
|---|
| Quotes from the Teams meeting transcript: Riley on the Fabrikam quote and "sign this quarter"; Riley on Priya wanting the all-in cost; Ken on the security review.<br><br>Confluence *Aurora Retail Pricing & Discount Policy* (current version, not the archived 2025 one):<br>• Up to 12% volume discount at 250+ stores with no approval.<br>• 12–15% needs Lena Okafor.<br>• Above 15% needs VP Sales and Deal Desk.<br>Copilot says **20% cannot be offered in the pitch**.<br><br>It proposes the in-policy counter: 12% (about $1.06M for 400 stores) plus bundled in-store install and staff training. The bundle is value-add and does not count as discount.<br><br>It backs this with the *Fabrikam Home* battlecard TCO: Fabrikam's sticker price excludes install and 3-year support. All-in per store, Fabrikam is about $3,250 versus Verdantis' $2,640 with the counter-offer. That is the number Priya asked for.<br><br>If `handle-objection` runs and the win/loss history in 5.1 is seeded, the answer also has "What history says" (the Wide World Importers win and the Tailspin Toys loss against Fabrikam) and a "Don't" line: don't lead with a discount. |

| **WOW MOMENT** |
|---|
| Copilot catches the non-compliant answer before Marcus says it to the CFO, and turns the price gap into an all-in cost argument. |

| **IF IT GOES WRONG** |
|---|
| If Copilot answers from general knowledge, reply "Use the Teams recording of the Contoso pilot review and our pricing policy in Confluence." |

| **STEP 3** | **Book the security review and log it in Salesforce**<br>~3:00 · write action |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Send Ken and Riley a calendar invite for a 45-minute Aurora security review next week, and log it on the Contoso opportunity. |

| **PROMPT WORDING** |
|---|
| Asking for "a calendar invite" answers the skill's "propose by email or invite directly?" question up front. |

| **EXPECTED RESULT** |
|---|
| The `schedule-meeting` skill runs:<br>• 1. It finds Ken and Riley (with emails) and the one open opportunity in Salesforce.<br>• 2. It checks Marcus' Outlook calendar and proposes 2–3 slots next week.<br>• 3. **Gate 1:** it shows the invite preview (title, time, attendees, an agenda built from Steps 1–2, e.g. security FAQ walkthrough, data residency, rollout plan). After the learner says yes, it creates the Outlook invite.<br>• 4. **Gate 2:** it shows the Salesforce Event preview. After yes, it creates the Event on the opportunity.<br>• 5. It shows the confirmation: "✅ Booked … Calendar: event created … Salesforce: Event logged on Contoso Retail / Aurora 400-store rollout", with the record link. |

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
| Draft an email to Riley and Priya ahead of the pitch: confirm the agenda and link our security FAQ and the Wide World Importers case study. |

| **EXPECTED RESULT** |
|---|
| An Outlook draft to Riley and Priya with the agenda and links to the two Confluence pages. It stays a draft. |

| **ALTERNATIVE** |
|---|
| Alternative stretch: "Log the pilot review call on the Contoso opportunity." (`log-activity`, one confirmation, creates a completed Task.) |

## 5. Seed data

| **DATES** |
|---|
| No prompt depends on the lab day, so the tenant is built once. Prompts name items instead of days ("my Contoso Retail expansion pitch", "the pilot review call"). Outlook items have fixed dates: Riley's email and the pilot review are in the past; the pitch is on **Fri Nov 20, 2026** (the last lab day is Nov 19), so it is always upcoming. Test_Salesforce works out its dates from the day of the request. "Next week" in Step 3 uses Marcus' live calendar, so it works on any day; in Ignite week (Mon Nov 16) it is US Thanksgiving week, so block Nov 26–27. The Dec 8 launch event is a fixed date. |

| **ONE IDENTITY PER PERSON** |
|---|
| Riley, Ken and Priya each use one email address everywhere: Salesforce contact (Riley, Ken), Outlook meeting attendee, Riley's email, Teams meeting participant. `call-prep` matches attendees to contacts by exact email. |

### 5.1 Salesforce (federated only)

| **Owner** | Marcus' Salesforce user owns the account, all opportunities below and the pitch Event. The skills read `scope: MINE` and stop (they don't widen) if it comes back empty. |
|---|---|
| **Account** | *Contoso Retail* (Retail, about 12,000 employees, Type = Customer). Website = the email domain Riley and Ken use. **No other account may use that domain**, or `call-prep` lists candidates and asks. |
| **Opportunities** | • *Contoso Retail – Aurora 400-store rollout*: Proposal/Price Quote, $1,200,000 ($3,000 list per store), close date end of the current quarter. It must be the **only open** opportunity on the account; otherwise `schedule-meeting` asks which one.<br>• *Contoso Retail – Aurora pilot (50 stores)*: Closed Won, $150,000. |
| **Win/loss history** | Recommended, for Step 2 depth. Two more opportunities owned by Marcus, closed in the last six months; the Description or loss-reason field names Fabrikam:<br>• *Wide World Importers – Aurora 320-store rollout*: Closed Won. Beat Fabrikam on all-in TCO with bundled install, no discount above 12%.<br>• *Tailspin Toys – Aurora 120-store rollout*: Closed Lost to Fabrikam on price. We led with a discount and never showed TCO. |
| **Contacts** | On Contoso Retail:<br>• Riley Blake, Director of Store Operations<br>• Ken Liu, IT Security Lead<br>• **Not** Priya Nair: she must show up as new. |
| **Pitch Event** | Fri Nov 20, 2026, 10:00–11:00 (same as the Outlook pitch meeting), "Contoso Retail – Aurora expansion pitch". WhoId = Riley; WhatId = the open opportunity. Description lists the attendees with emails: Riley Blake, Priya Nair (CFO), Ken Liu. The skill reads attendees from the Description and the Outlook meeting, not from Salesforce invitee records. |
| **Activity history** | 2–3 completed Tasks, e.g. "Pilot kickoff" and "30-day pilot check-in". Do **not** log the pilot review; that is the alternative stretch. |
| **Event object** | Check this org's required fields and picklists. `schedule-meeting` writes Subject, Start, End, WhoId and WhatId only. |

### 5.2 Teams meeting

One recorded Teams meeting with transcript: "Contoso Retail – Aurora pilot review", about 10 minutes, organized by Marcus. Speakers: Marcus, Riley, Ken. In COEP this is a past `events` item plus an `onlinemeetings` item with a `.vtt` transcript; Riley and Ken must be tenant users because participants are tenant mail nicknames. Give it a fixed date before the tenant is built; prompts call it "the pilot review call", so the date doesn't matter.

Lines that must be in it:

- The pilot result, e.g. a 9% attach-rate lift in pilot stores.
- Riley: Fabrikam Home quoted "about 20% under your list price".
- Riley: "if you can get close to that we could sign this quarter".
- Ken: the security review must happen before the 400-store rollout.
- Riley: "Priya will want the all-in cost".

### 5.3 Test_Confluence (space Verdantis Sales)

| **Page** | **What the demo relies on** |
|---|---|
| *Aurora Retail Pricing & Discount Policy* | List $3,000 per store (hub + 3-year support). Volume tiers: up to 12% at 250+ stores, no approval. 12–15% needs Lena Okafor. Above 15% needs VP Sales and Deal Desk. Value-add items (in-store install and staff training, normally $300 per store) do not count as discount. |
| *Competitive Battlecard: Fabrikam Home* | Sticker about 20% under Verdantis ($2,400 per store) but excludes install (about $350) and 3-year support (about $500), so about $3,250 all-in. TCO table. "Don't lead with discount." |
| *Aurora Security & Compliance FAQ* | SOC 2 Type II, regional data residency, no in-store cameras or PII. |
| *Case Study: Wide World Importers 320-store rollout* | Rollout timeline and outcome, cited in the pre-read. |
| *2–3 distractor pages* | *E.g. the 2025 pricing policy marked archived, so retrieval has to pick the current one.* |

### 5.4 Outlook (Marcus' mailbox and calendar)

| **Email** | From Riley Blake, dated before the tenant is built: Priya (CFO) joins the pitch and wants the all-in cost for 400 stores; IT (Ken) needs the security documentation beforehand. Don't cc Priya; she must have no email history. |
|---|---|
| **Pitch meeting** | Fri Nov 20, 2026. The same 10:00–11:00 "Contoso Retail – Aurora expansion pitch", with Riley, Priya and Ken as attendees. |
| **Calendar next week** | A few busy blocks, so the proposed slots look real; Nov 26–27 out of office in Ignite week. Ken's and Riley's free/busy visible if possible. |
| **Lab users** | Riley Blake exists. **Ken Liu, Priya Nair and Lena Okafor are new.** Priya is needed as a meeting attendee and the Step 4 recipient, not as a Salesforce contact. |

## 6. Validation run

Goal: prove `call-prep` and `schedule-meeting` (2 gates + Event write) work in Cowork against the real Salesforce org before the seed is locked.

| **#** | **Action** | **Details** |
|---|---|---|
| 1 | **Schedule the run** | Agree a 15-minute slot with the Salesforce org owner, who approves the MFA prompt. Confirm which org it is and whether Contoso data is seeded. |
| 2 | **Load the Salesforce package in Cowork** | Publish → "Only you", and connect it by OAuth. |
| 3 | **Run Steps 1–3** with the exact prompts | Record:<br>• how the brief is shown<br>• whether it covers Priya and her cost question<br>• whether Step 1 picks up the Teams transcript<br>• the number of confirmations and approval cards<br>• the time per step<br>• Salesforce calls (trajectory export) |
| 4 | **Clean up** | Delete the test Event and the calendar invite. |
| 5 | **Report** | What worked, any prompt or seed changes, and timing. |
