> Source: *IGNITE LAB654 · PRODUCTIVITY MODULE* (Word, OneDrive), v4.1, Nov 2, 2026. Converted to Markdown for reference; formatting differs from the original. Replaces the earlier Notion and Zava Hub scenario.
>
# IGNITE LAB654 · PRODUCTIVITY MODULE

## Productivity Scenario: Sales pitch prep (v4.1)

SalesDesk_Lab · Teams · Outlook

| **Lab** | Supercharge Copilot: Connect your work data & Get work done with Copilot Connectors (LAB654) |
|---|---|
| **Module** | [Productivity] Complete end-to-end productivity workflows with MCP apps and skills |
| **Time budget** | 10 minutes: 3 core steps + 1 stretch |
| **Surface** | Cowork |
| **Lab user** | Emil Vanggaard, Zava |
| **Connectors** | SalesDesk_Lab (mock MCP) · WorkIQ (Outlook mail and calendar, Teams meeting transcript) |

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
| **SalesDesk CRM** | Account, opportunity, contacts, meetings, activity history, win/loss history against Boulder Innovations; logs the follow-up meeting on the opportunity | SalesDesk_Lab mock MCP + SalesDesk skills package (`salesforce_v0_20260918_withConstraints`) |
| **Teams (1P)** | What the customer said on the pilot review call | WorkIQ (Teams meeting transcript) |
| **Outlook (1P)** | Customer email that sets up the pitch; the pitch meeting; calendar for the follow-up | WorkIQ |

## 2. Cast

| **Character** | **Role in the story** |
|---|---|
| **Emil Vanggaard**, Zava | Copilot user. Runs the Zava Aurora smart-home hub launch with Lakeshore Retail and owns the Lakeshore Retail account in SalesDesk. No job title in prompts. |
| **Atul Manohar**, Lakeshore Retail | Champion for the rollout; emails Emil; SalesDesk contact. |
| **Jahidi Juma**, Lakeshore Retail | IT security lead; SalesDesk contact. |
| **Nanami Nakayama**, Lakeshore Retail | CFO; joins the pitch; not in SalesDesk. |
| Lakeshore Retail | Aurora retail partner. 50-store pilot running; public launch event Dec 8; Emil pitches the rollout to all 400 stores. |
| Boulder Innovations | Competitor. Zava has beaten it once (Wide World Importers) and lost to it once (Tailspin Toys). |

## 3. Story

Lakeshore Retail has piloted Aurora in 50 stores for the past six weeks, ahead of the public launch event on Dec 8. Emil's next step is the **expansion pitch** to roll it out to all 400 stores.

- Atul emailed ahead of the pitch. Their CFO, **Nanami Nakayama**, is joining and wants the all-in cost for 400 stores. Lakeshore Retail IT (Jahidi) wants Zava's security documentation before anything goes to 400 stores.
- On the Teams pilot review call, Atul said Boulder Innovations quoted about 20% under Zava's list price.

| **WHAT COPILOT DOES, END TO END** |
|---|
| It builds the call brief from SalesDesk and Outlook. It pulls what the customer actually said on the Teams call and uses Zava's win/loss history against Boulder Innovations to turn the 20% gap into an all-in cost argument. It books the security review with Lakeshore Retail and logs it in SalesDesk. Emil never leaves Copilot. |

## 4. Steps (target ≤ 10 min: 3 core steps + 1 stretch)

Run all steps in **one Cowork conversation**: Step 3 reuses the account and agenda from Steps 1–2, and SalesDesk mock writes persist only within that conversation.

| **#** | **Step** | **Time** | **Connector / skill** |
|---|---|---|---|
| 1 | Prep the call | ~3:00 | SalesDesk `call-prep` skill; Outlook |
| 2 | Handle the price objection | ~3:00 | Teams transcript + SalesDesk win/loss history |
| 3 | Book the security review and log it in SalesDesk | ~3:00 | SalesDesk `schedule-meeting` + Outlook calendar **(write action)** |
| *Stretch* | Log the pilot review call | – | SalesDesk `log-activity` **(write action)** |

| **STEP 1** | **Prep the call**<br>~3:00 · SalesDesk skill + Outlook |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Prep me for my Lakeshore Retail expansion pitch. |

| **EXPECTED RESULT** |
|---|
| The `call-prep` skill finds the pitch event in SalesDesk (*Lakeshore Retail – Aurora expansion pitch*, Fri Nov 20, 10:00–11:00 ET; its Description lists Atul, Nanami (CFO) and Jahidi). It reads:<br>• the account: Lakeshore Retail, Retail, 12,000 employees, Customer<br>• the one open opportunity: *Lakeshore Retail – Aurora 400-store rollout*, Proposal/Price Quote, $1,200,000, close Dec 31, Next Step "bring the all-in per-store and total cost"<br>• contacts: Atul and Jahidi. Nanami isn't a contact, so she shows up as new<br>• activity: the pilot kickoff and the 30-day check-in<br><br>From Outlook it adds Atul's Oct 28 email: Nanami joins and wants the all-in cost; IT wants the security docs.<br><br>It returns a call brief. The layout can vary between runs; the content is what matters: the deal, who's in the room, and what to cover (the price comparison, the security review, next steps). |

| **WOW MOMENT** |
|---|
| One prompt turns the CRM and the inbox into a brief that already points to the pitch's two risks: the CFO's cost question and IT's security review. |

| **SAY THIS** |
|---|
| A skill that knows how sales teams prep, working on Emil's real account data. |

| **IF IT GOES WRONG** |
|---|
| If Copilot asks which account or meeting, reply "The Lakeshore Retail expansion pitch."<br><br>If the brief doesn't mention Nanami, ask "Who's on the call, and what does each of them care about?" |

| **STEP 2** | **Handle the price objection**<br>~3:00 · Teams + SalesDesk |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Lakeshore Retail says Boulder Innovations is 20% cheaper. How should I handle that? Use what they said on the pilot review call and our win/loss history against Boulder Innovations. |

| **EXPECTED RESULT** |
|---|
| Quotes from the Oct 22 pilot review transcript in Teams: Atul on the Boulder Innovations quote ("about 20% under your list price", about $2,400 per store) and "if you can get close to that we could sign this quarter"; Emil's breakdown of Boulder's offer (hub only, around $3,250 per store all-in once install and support are added) and his counter-offer (discount held to 12%, $2,640 per store against the $3,000 list, install bundled at no extra cost); Atul on Nanami wanting the all-in cost; Jahidi on the security review before the 400-store rollout.<br><br>SalesDesk win/loss history against Boulder Innovations (Competitor = Boulder Innovations on both):<br>• *Wide World Importers – Aurora 320-store rollout*: Closed Won, $844,800. Won on all-in TCO, not sticker price.<br>• *Tailspin Toys – Aurora 120-store rollout*: Closed Lost, $360,000, Loss Reason Price. "We led with a discount and never showed the all-in TCO."<br><br>The recommendation: **don't match the 20%**. Lead with the all-in cost for 400 stores and offer 12% plus bundled install. That's the number Nanami asked for. |

| **WOW MOMENT** |
|---|
| One answer combines two sources. The competitor's offer and the counter-offer come from the Teams meeting, and SalesDesk shows that leading with all-in cost beat the same competitor while leading with a discount lost. |

| **IF IT GOES WRONG** |
|---|
| If Copilot answers from general knowledge, reply "Use the Teams transcript of the Lakeshore Retail pilot review and our closed deals against Boulder Innovations in SalesDesk." |

| **STEP 3** | **Book the security review and log it in SalesDesk**<br>~3:00 · write action |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Send Jahidi and Atul a calendar invite for a 45-minute Aurora security review next week, and log it on the Lakeshore Retail opportunity. |

| **PROMPT WORDING** |
|---|
| Asking for "a calendar invite" answers the skill's "propose by email or invite directly?" question up front. |

| **EXPECTED RESULT** |
|---|
| The `schedule-meeting` skill runs:<br>• 1. It finds Jahidi and Atul (with emails) and the one open opportunity in SalesDesk.<br>• 2. It checks Emil's Outlook calendar and proposes 2–3 free slots next week, for example Mon Nov 23, 11:30–12:15 ET.<br>• 3. **Gate 1:** it shows the invite preview (title, time, attendees, an agenda built from Steps 1–2). After the learner says yes, it creates the Outlook invite.<br>• 4. **Gate 2:** it shows the SalesDesk activity preview. After yes, it creates a Task on the opportunity (Type Meeting, Status Not Started, related to Jahidi; HTTP 201).<br>• 5. It shows the confirmation with the record link. The record page shows the changes from this conversation. |

| **WOW MOMENT** |
|---|
| One prompt books the meeting and updates the CRM, with a human yes before each write. |

| **IF IT GOES WRONG** |
|---|
| If slot picking runs long, the learner replies "The first slot." If Copilot still asks whether to email or invite, reply "Send the invite."<br><br>"Next week" follows the real current date, so outside Ignite week the proposed slots won't be Nov 23–25. |

| **STRETCH** | **Step 4 — Log the pilot review call**<br>SalesDesk, write action |
|---|---|

| **▶ PROMPT** copy & paste into Copilot |
|---|
| Log the pilot review call on the Lakeshore Retail opportunity. |

| **EXPECTED RESULT** |
|---|
| The `log-activity` skill asks for one confirmation, then creates a completed Task (Type Meeting, dated Oct 22) on the Lakeshore Retail opportunity, with the attendees and key points from the transcript (HTTP 201). It appears on the opportunity's activity timeline.<br><br>If the transcript isn't available, Copilot doesn't make up outcomes. It asks whether to log the basics now or wait for notes. The basics have the date, attendees and agenda, with outcomes marked "[not recorded – add notes]". |

| **ALTERNATIVE** |
|---|
| Where writes aren't wanted: "Draft an email to Atul and Nanami ahead of the pitch to confirm the agenda." Outlook draft only. |

## 5. Seed data

| **DATES** |
|---|
| The tenant is built once. Prompts name items instead of days ("my Lakeshore Retail expansion pitch", "the pilot review call"). Outlook items have fixed dates: Atul's Oct 28 email and the Oct 22 pilot review are in the past; the pitch is on **Fri Nov 20, 2026** (the last lab day is Nov 19), so it is always upcoming. "Next week" in Step 3 uses Emil's live calendar; in Ignite week (Mon Nov 16) it is US Thanksgiving week, so Nov 26–27 are blocked. The Dec 8 launch event is a fixed date. |

| **ONE IDENTITY PER PERSON** |
|---|
| Atul, Jahidi and Nanami each use one email address everywhere: SalesDesk contact (Atul, Jahidi), Outlook meeting attendee, Atul's email, Teams meeting participant. `call-prep` matches attendees to contacts by exact email. |

### 5.1 SalesDesk (SalesDesk_Lab mock)

| **Owner** | Emil's SalesDesk user owns the account, all opportunities below and the pitch Event. The skills read `scope: MINE` and stop (they don't widen) if it comes back empty. |
|---|---|
| **Account** | *Lakeshore Retail* (Retail, 12,000 employees, Type = Customer, Website = lakeshore-retail.com). |
| **Opportunities** | • *Lakeshore Retail – Aurora 400-store rollout*: Proposal/Price Quote, $1,200,000 ($3,000 list per store), close Dec 31, Next Step "bring the all-in per-store and total cost". It must be the **only open** opportunity on the account; otherwise `schedule-meeting` asks which one.<br>• *Lakeshore Retail – Aurora pilot (50 stores)*: Closed Won, $150,000. |
| **Win/loss history** | Two more opportunities owned by Emil, both with Competitor = Boulder Innovations:<br>• *Wide World Importers – Aurora 320-store rollout*: Closed Won, $844,800. Description: won on all-in TCO, not sticker price. The pricing numbers are **not** in SalesDesk; they are in the Teams meeting (5.2).<br>• *Tailspin Toys – Aurora 120-store rollout*: Closed Lost, $360,000, Loss Reason Price. "We led with a discount and never showed the all-in TCO." |
| **Contacts** | On Lakeshore Retail:<br>• Atul Manohar, Director of Store Operations<br>• Jahidi Juma, IT Security Lead<br>• **Not** Nanami Nakayama: she must show up as new. |
| **Pitch Event** | Fri Nov 20, 2026, 10:00–11:00 ET (same as the Outlook pitch meeting), "Lakeshore Retail – Aurora expansion pitch". WhoId = Atul; WhatId = the open opportunity. Description lists the attendees with emails: Atul Manohar, Nanami Nakayama (CFO), Jahidi Juma. |
| **Activity history** | Completed Tasks "Pilot kickoff" and "30-day pilot check-in". Do **not** log the pilot review; that is the stretch. |

### 5.2 Teams meeting

One recorded Teams meeting with transcript: "Lakeshore Retail – Aurora pilot review", Oct 22, about 10 minutes, organized by Emil. Speakers: Emil, Atul, Jahidi. In COEP this is a past `events` item plus an `onlinemeetings` item with a `.vtt` transcript; Atul and Jahidi are tenant users because participants are tenant mail nicknames.

Lines that must be in it:

- The pilot result, e.g. a 9% attach-rate lift in pilot stores.
- Atul: Boulder Innovations quoted "about 20% under your list price".
- Atul: "if you can get close to that we could sign this quarter".
- Atul: he has only seen the per-store number, about $2,400.
- Emil, the competitor offer: Boulder's $2,400 is the hub only; with install and support it lands around $3,250 per store all-in.
- Emil, the counter-offer: hold the discount to 12% ($2,640 per store against the $3,000 list) and bundle install at no extra cost.
- Jahidi: the security review must happen before the 400-store rollout.
- Atul: "Nanami will want the all-in cost".

### 5.3 Outlook (Emil's mailbox and calendar)

| **Email** | From Atul Manohar, Oct 28: Nanami (CFO) joins the pitch and wants the all-in cost for 400 stores; IT (Jahidi) needs the security documentation beforehand. Don't cc Nanami; she must have no email history. |
|---|---|
| **Pitch meeting** | Fri Nov 20, 2026, 10:00–11:00 ET, "Lakeshore Retail – Aurora expansion pitch", with Atul, Nanami and Jahidi as attendees. |
| **Calendar next week** | Busy: Mon Nov 23 9–11 and 14–15:30; Tue Nov 24 10–11 and 13–16; Wed Nov 25 11–11:30. Nov 26–27 out of office. |
| **Lab users** | Atul Manohar, Jahidi Juma and Nanami Nakayama are tenant users with mailbox and Teams. Nanami is needed as a meeting attendee, not as a SalesDesk contact. |

## 6. Validation status

The v4 SalesDesk calls were tested against the live SalesDesk_Lab mock on Nov 2, and the whole flow ran in Cowork as Emil: 20 SalesDesk calls with no failures, including both writes returning HTTP 201. Verdict: feasible.

| **#** | **Watch for** | **Details** |
|---|---|---|
| 1 | **Pilot review transcript in the tenant** | Without it, Step 2 can't quote Atul and the stretch logs only the basics. |
| 2 | **"Next week"** | Cowork uses the real current date. A dry run before Ignite proposed slots from Mon Nov 9; in Ignite week they start Nov 23. |
| 3 | **One conversation** | Step 3 reuses Steps 1–2, and SalesDesk mock writes are kept only within the conversation. |
| 4 | **Discount approval** | The earlier 12–15% approval rule isn't in SalesDesk or WorkIQ, so it isn't part of the expected result. |
