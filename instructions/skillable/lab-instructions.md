@lab.Title

Username: +++AlexW@@lab.CloudCredential(WWLM365E7).TenantName+++

TAP: +++@lab.Variable(TAP)+++

## Welcome to Your Lab Environment

To begin, log into the virtual machine using the following credentials: +++@lab.VirtualMachine(Win11-Pro-Base).Password+++

**Note:** Text formatted as an +++example+++ represents type text. Clicking on this text will automatically insert it to prevent any typing errors.

## Sign in to Copilot

You'll do the whole lab in Microsoft 365 Copilot on the web, signed in with the lab account above.

1. [] In the virtual machine, open the browser and go to +++https://copilot.cloud.microsoft/+++.
1. [] Sign in with the **Username** at the top of this page.
1. [] When you're asked for a Temporary Access Pass, enter the **TAP** at the top of this page.
1. [] If you see _Let's keep your account secure_ or you're asked for a code, select **Next** at the bottom of these instructions and follow the steps on the next page.

> [!Hint] If a sign-in popup is blocked at any point, allow popups for the Copilot site and try again.

> [!Note] This lab runs in a demo tenant with fictional people, companies and data. Financial and legal outputs are for the exercise only. They aren't investment or legal advice.

===

# Verify your sign-in

Your lab account may ask for a second check (multi-factor authentication) when you sign in. Use the **Contoso Authenticator App** on the virtual machine desktop to get the code. You don't need your phone.

!IMAGE[Contoso Authenticator App icon: a blue floppy disk with a yellow and blue snake logo.](instructions360859/contoso-authenticator-icon.png "Contoso Authenticator App icon"){64}

If you weren't asked to verify your sign-in, select **Next** to skip this page.

## Set up the app the first time

1. [] On the _Let's keep your account secure_ page, select **Next**.

    !IMAGE[The Let's keep your account secure page, with a Next button in the lower-right corner.](instructions360859/mfa-01-keep-account-secure.png "Let's keep your account secure")

1. [] On the _Install Microsoft Authenticator_ page, select **Set up a different authentication app**.

    > [!Alert] Don't select Next on this page. That sets up the phone app, and the Contoso Authenticator App can't read its QR code.

    !IMAGE[The Install Microsoft Authenticator page, with the Set up a different authentication app link highlighted below the app store buttons.](instructions360859/mfa-02-different-authentication-app.png "Set up a different authentication app")

1. [] On the _Set up your account in app_ page, select **Next**.

    !IMAGE[The Set up your account in app page, with a Next button in the lower-right corner.](instructions360859/mfa-03-set-up-account-in-app.png "Set up your account in app")

1. [] Check that the _Scan the QR code_ page shows a QR code. Leave this page open.

    !IMAGE[The Scan the QR code page, showing a QR code and a Next button.](instructions360859/mfa-04-scan-qr-code-page.png "Scan the QR code")

1. [] On the virtual machine desktop, open **Contoso Authenticator App**.

    !IMAGE[The Contoso Authenticator App window, titled OTP Accounts, with a Scan QR from Screen button.](instructions360859/mfa-05-authenticator-app.png "Contoso Authenticator App")

1. [] Move the app window so that it doesn't cover the QR code in the browser.
1. [] In the app, select **Scan QR from Screen**. Your account and a 6-digit code appear.

    !IMAGE[The Contoso Authenticator App showing the lab account, a 6-digit code and a Copy button.](instructions360859/mfa-06-code-shown.png "Account and code in the app")

1. [] Select **Copy**, then select **OK** in the _Copied_ message.

    !IMAGE[The Copied message in the Contoso Authenticator App, saying OTP copied to clipboard, with an OK button.](instructions360859/mfa-07-code-copied.png "Code copied")

1. [] In the browser, select **Next** on the _Scan the QR code_ page.
1. [] On the _Enter the code_ page, paste the code, then select **Next**.

    !IMAGE[The Enter the code page, with a 6-digit code typed in the box and a Next button.](instructions360859/mfa-08-enter-code.png "Enter the code")

1. [] On the _Authenticator app added_ page, select **Done**.

    !IMAGE[The Authenticator app added page, with a Done button in the lower-right corner.](instructions360859/mfa-09-app-added.png "Authenticator app added")

## Enter a code when you're asked again

1. [] Open **Contoso Authenticator App** from the desktop, select **Copy** next to your account, then paste the code in the browser.

> [!Note] Codes change regularly, and the app shows when the next one arrives. If a code is rejected, copy the new one and try again.

## If it goes wrong

### The app says No QR code found on screen

The app window is probably covering the QR code. Move the app window away from the QR code, then select **Scan QR from Screen** again.

!IMAGE[The Contoso Authenticator App window covering part of the QR code, with the error No QR code found on screen.](instructions360859/mfa-10-no-qr-found.png "No QR code found on screen")

### Scanning still doesn't work

Zoom the browser to 120% so the QR code is larger, then select **Scan QR from Screen** again.

!IMAGE[The browser zoomed in so the QR code is larger and fully visible next to the Contoso Authenticator App window.](instructions360859/mfa-11-zoom-in.png "Zoom the browser")

### The app says Failed to parse QR code: Invalid OTP URI

You're on the page for the Microsoft Authenticator phone app. In the browser, go back, select **Set up a different authentication app** and scan the new QR code.

!IMAGE[The error Failed to parse QR code: Invalid OTP URI, next to a QR code page that mentions the Microsoft Authenticator app.](instructions360859/mfa-12-invalid-otp-uri.png "Invalid OTP URI")

When you're signed in to Copilot, select **Next**.

===

# Prepare a clean environment

> [!Alert] PLACEHOLDER FOR LAB AUTHORS: add the step that runs the clean-up batch script here, then delete this alert.

===

# Get to know the lab

AI is only as useful as the knowledge it can reach. At most companies, that knowledge is spread across many systems: CRM, ticketing, code, wikis, document management, meeting recordings and paid data feeds. Copilot connectors bring that knowledge into Microsoft 365 Copilot, so answers are grounded in the information your organization actually uses.

Microsoft 365 Copilot offers one catalog of more than 300 connectors. Connect a source once, and it's available across the Copilot experiences that support it: Copilot Chat, Copilot Cowork, Word, Excel and PowerPoint.

In this lab you'll go beyond finding information. You'll use connectors, connector skills and write actions to finish real workflows, and you'll approve every change before it happens.

## What you'll learn

- Discover and connect the right connectors from the catalog, and use connected data wherever it's supported in Microsoft 365.
- Ground Copilot in trusted business and partner data, with citations back to each source.
- Finish the work, not just the search: use skills and write actions to produce a call brief, a sprint slide, a committee pack or a contract redline, and bring your own app with a custom connector.

## Your role: Emil Vanggaard at Zava

Zava is a fictional US insurer that also builds Aurora, a smart-home hub sold through retail partners such as Lakeshore Retail. You play Emil Vanggaard, who uses Copilot to handle very different requests. Each request is a track.

## How the lab runs

1. Everyone completes **Get started with connectors** on the next page.
1. Choose one track: finance, legal, productivity or engineering. If you finish early, try another.
1. Everyone completes **Bring your own app**: connect an in-house app to Copilot with no code.
1. Wrap up with a short summary.

## Key ideas

**Connectors.** Some connectors index content into Microsoft 365 ahead of time; others call the source live, signed in as you. Copilot picks the right source for your question, respects what you're allowed to see and cites where each answer came from.

**Connector skills.** A skill packages a partner's expertise, such as how sales teams prep a call or how analysts assess credit. Copilot loads a skill when your request needs it, so you get the partner's method as well as their data.

**Plugins.** A plugin bundles a connector and its skills into one package that an admin deploys once. After that, it works across the Copilot experiences that support it.

**Write actions.** Copilot can change things in the source system, such as logging a meeting on a Salesforce opportunity or saving a draft to a document matter. You see a confirmation first, and nothing changes until you approve it.

===

# Get started with connectors

In this part, you'll find connectors in the catalog, check that the ones for your track are ready and ask your first grounded question.

## Discover connectors

1. [] In Copilot, open **Settings** and then **Sources**.
1. [] Browse the catalog. It has more than 300 connectors, from CRM and ticketing to code, wikis and market data.
1. [] Find the connectors for the track you'll take:

    | Track | Connectors |
    |:---|:---|
    | Finance | LSEG_Lab, FactSet_Lab, Moodys_Lab |
    | Legal | iManage_Lab |
    | Productivity | Salesforce_Lab |
    | Engineering | Jira, Confluence, GitHub_Lab, Rovo_Lab |
    | Bring your own app (everyone) | Zava Expense, which you'll add yourself later |

    Outlook, Teams and your Microsoft 365 files are available in every track.

> [!Note] Connectors named _…_Lab_ are mock versions of the real connectors, built for this lab. They behave like the real ones and come with the same skills, but they serve sample data for Zava. You don't need a third-party account to use them. Changes you make with them are visible only in the conversation where you make them.

## Check your sources are ready

1. [] Confirm that the connectors for your track show as **Connected**.
1. [] If one shows **Connect** instead, select it and follow the prompts. If it still doesn't connect, ask a proctor.

In a real organization, an admin deploys connectors like these once, and people sign in to them with their own accounts. In this lab, that setup has been done for you.

## Ask your first grounded question

1. [] Start a new chat, then select the question for your track:

    - Finance: +++Using LSEG, what was Litware's earnings per share last quarter compared with the analyst consensus?+++
    - Legal: +++What did Hemanti send me about Trey Research?+++
    - Productivity: +++What's the stage and amount of the Lakeshore Retail opportunity in Salesforce?+++
    - Engineering: +++What's the status of Jira issue AUR-142?+++

1. [] Check that the answer cites its source, such as the connector name, a record, a page or a link.

> [!Knowledge] Connect once, use everywhere. These connectors also work in the Copilot experiences in Word, Excel, PowerPoint and Copilot Cowork. You'll see this in the tracks: you don't need to set anything up again.

===

# Choose your track

Pick the track closest to your work. Each track takes about 15 to 20 minutes. Select a track to go to its page, or select **Next** to move through the pages in order.

| Track | The ask |
|:---|:---|
| [Finance](#finance-should-we-buy-more-litware) | Kristian, who runs the Zava investment portfolio, asks: should we buy more Litware? Bring a recommendation to Monday's investment committee. |
| [Legal](#legal-can-we-sign-on-the-10th) | Luc, Chief Underwriting Officer, asks: can we sign Trey Research's AI underwriting contract on the 10th? |
| [Productivity](#productivity-prep-a-sales-pitch) | Pitch the Aurora rollout to all 400 Lakeshore Retail stores, with a CFO in the room and a competitor 20% cheaper. |
| [Engineering](#engineering-find-whats-blocking) | One Sprint 24 item is at risk, and the customer's pilot expands on Monday. Who is it waiting on? |

After your track, everyone goes to [Bring your own app](#bring-your-own-app-zava-expense).

> [!Hint] If Copilot doesn't give the response you expect in any track, select the model name at the top of the chat, switch from _Auto_ to a GPT model that isn't a quick-response one, and send the prompt again.

===

# Finance: Should we buy more Litware?

_About 20 minutes · LSEG_Lab, FactSet_Lab, Moodys_Lab · Copilot Chat, Copilot Cowork, Excel_

You'll use the LSEG, FactSet and Moody's connectors to take one investment question from a quick sense check to a committee-ready memo.

Zava invests the premiums it holds, and Litware, a chipmaker, is one of its biggest holdings. Kristian Stensen, who runs the portfolio, messages you on Teams:

> Committee wants a view on Litware Monday. Should we add more? Bring a short memo.

The committee will challenge the case, so every number has to be sourced and checked. You need to know whether the business is beating expectations, whether it's stronger than its rivals, what the upside and downside are at today's price, and whether your view survives tough questions.

> [+Help] New to finance? Select to see the terms you'll meet.
>
> - _EPS (earnings per share)_: profit divided by the number of shares.
> - _Consensus_: the average forecast from analysts who follow the company.
> - _Gross margin_: how much of each dollar of sales is left after making the product.
> - _ROIC_: profit earned on the money put into the business.
> - _P/E (price-to-earnings)_: how much investors pay for one dollar of profit.
> - _FY1 and FY2_: this fiscal year and next fiscal year.
> - _Bear, base and bull_: worst, middle and best case.
> - _Credit rating_: a grade for how likely a company is to repay its debts.
> - _SWOT_: strengths, weaknesses, opportunities and threats.

!IMAGE[Step 1 in Copilot gives a verified verdict. Step 2a in Copilot in Cowork mode builds the workbook. Steps 2b and 2c in Excel add scenarios and credit analysis. Step 3 back in Copilot gives a pressure-tested view and memo.](instructions360859/finance-workflow.png "How the finance track flows")

## Before you start

- [] **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab** appear in **Settings** › **Sources**.

## Step 1: Run a sense check

### 1a. Check whether Litware beat expectations

> [!Alert] The first time you use Cowork, select **Customize** and turn on LSEG_Lab, FactSet_Lab and Moodys_Lab. Then turn off the Fabric IQ plugin, which is on by default.

1. [] In Copilot, start a new chat in either Chat or Cowork mode, then enter:

    +++I'm preparing a recommendation for Monday's investment committee on whether our portfolio should buy more Litware. To start with, did Litware beat analysts' expectations last quarter? Using LSEG, compare its actual earnings per share and revenue with the analyst consensus, and show the quarter and source.+++

1. [] Check that you see what Litware earned last quarter against what analysts expected, with LSEG cited as the source.

    > [!Knowledge] LSEG can return charts and analysis cards, not just text: the provider's own experience, inside Copilot.

### 1b. Compare Litware with its rivals

1. [] In the same chat, enter:

    +++Using FactSet, compare how profitable Litware, A. Datum and Relecloud have been over the past 5 years, using gross margin and return on invested capital (ROIC).+++

1. [] Check that you see FactSet profitability figures for all three companies and a clear view of which is strongest.

### 1c. Decide if it's worth a deeper look

1. [] In the same chat, enter:

    +++What is Litware's credit rating and outlook according to Moody's and what's driving them? Then, based on everything so far, give me a one-line verdict on whether Litware is worth a deeper look.+++

1. [] Check that you see a Moody's rating and outlook with the reasons behind them, then a one-line verdict that draws on all three sources.

    > [!Knowledge] Three connectors, one conversation. Copilot keeps the context, so the verdict builds on the LSEG and FactSet answers above it.

## Step 2: Dig into the numbers

### 2a. Build the committee workbook

This is a long-running task, so you'll use Cowork. Cowork creates the workbook and saves it to your OneDrive.

1. [] In Copilot, start a new chat, select **Cowork** mode, then enter:

    +++Using LSEG, create an Excel workbook called "Litware Committee Pack" with an equity research snapshot of Litware: analysts' earnings and revenue forecasts for this year and next (FY1, FY2), how many analysts cover it and how much they disagree, 5 years of financials, and valuation. Cite sources and dates.+++

1. [] Check that Copilot uses LSEG's equity research skill and creates a workbook named **Litware Committee Pack**, with sources and dates.

    > [!Hint] Building the workbook can take a few minutes. Select the thought process to watch what Cowork is doing, or go back to your Step 1 chat while the task finishes.

### 2b. Model the upside

1. [] In the same Cowork chat, select **Litware Committee Pack** to open the workbook next to the chat.
1. [] In Copilot in Excel, enter:

    +++Using LSEG, add a "Scenarios" sheet with worst, middle and best cases (bear, base, bull), using the lowest, average and highest FY2 earnings-per-share forecasts and Litware's current share price. Make the price-to-earnings (P/E) multiple an editable input for each case and use formulas to show the implied share price and % upside or downside.+++

1. [] Check that a **Scenarios** sheet appears, built on LSEG forecasts and share price, with LSEG cited.
1. [] On the **Scenarios** sheet, change one P/E multiple and watch the implied price and upside update.

    > [!Knowledge] You didn't re-explain anything. Copilot in Excel picked up the context from the workbook, and these are real formulas you can check.

### 2c. Check that it's financially sound

1. [] In Copilot in Excel, enter:

    +++Using Moody's, add a "Credit" sheet with a credit SWOT for Litware (strengths, weaknesses, opportunities and threats) and the factors that could lead to a rating upgrade or downgrade.+++

1. [] Check that a **Credit** sheet appears with a SWOT and upgrade and downgrade drivers, sourced from Moody's.

## Step 3: Back-check and report

### 3a. Pressure-test your view (stretch goal)

1. [] In Copilot, go back to your chat from Step 1, then enter:

    +++My view: we should buy more Litware because its strong profits and earnings growth justify its high share price. Using the Litware Committee Pack and the latest data from LSEG and Moody's, pressure-test this view: give the evidence for and against, the strongest case against buying, and the questions the committee is likely to ask.+++

1. [] Check that you see evidence on both sides, the strongest counter-argument and likely committee questions, each backed by sourced figures.

    > [!Knowledge] Copilot argued against your view, so the committee isn't the first to find the weak spot.

### 3b. Write the committee memo

1. [] In the same chat, enter:

    +++Turn this into a Word memo for the investment committee, reusing the workbook's charts. Cite LSEG, FactSet and Moody's as the source for every number, and flag any missing data.+++

1. [] Check that every number in the memo is cited, the workbook charts are reused and any gaps in the data are flagged.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Copilot answers without a source | Start the prompt with _Using LSEG_ or _Using Moody's_. |
| The first answer from a connector is slow | Wait a few seconds and ask again. |
| Copilot asks which company or ticker | Reply +++Litware (LITW)+++. |
| Workbook steps don't apply to the right file | Open **Litware Committee Pack** next to your Cowork chat and start the prompt with _In Litware Committee Pack_. |

## Checkpoint

- [] You compared Litware's results with consensus, rivals and its credit rating.
- [] Your **Litware Committee Pack** has snapshot, **Scenarios** and **Credit** sheets.
- [] You have a committee memo with sources.

## What you take away

- **A full finance workflow in Copilot**, from a first question to a committee memo, on trusted data from LSEG, FactSet and Moody's.
- **Excel analysis on verified data, in minutes**, with real formulas you can trace back to the source.
- **Reusable for any company.** Swap Litware for another company and run the same prompts.

Other connectors that fit this pattern: S&P Global and Morningstar.

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Legal: Can we sign on the 10th?

_About 15 minutes · Work IQ (email and Teams), iManage_Lab · Word with legal skills, Copilot Cowork_

Zava wants Trey Research's AI to make up to 4 million underwriting decisions a month: a five-year, $14.75 million deal. Regulators in Colorado and New York hold the insurer responsible for vendor AI. Zava trains the AI on its own claims data, so it must own what gets built.

Nothing is signed. Trey Research sent its own one-sided draft, and it's in your OneDrive. Zava's playbook is in the iManage matter. A negotiation session with Trey Research is booked for Thursday, December 10.

| Person | Role |
|:---|:---|
| Emil Vanggaard (you) | Associate General Counsel, Technology Transactions. You own this contract. |
| Luc Lacombe | Chief Underwriting Officer. Business owner; wants the AI live on the 13th. |
| Hemanti Baishya | SVP, Strategic Procurement. Emailed you the business's must-haves two weeks ago. |

Luc has pinged you on Teams:

> Morning Emil. Have you had a chance to look at Trey Research's contract? We'd like to sign at the session with them on the 10th so we can go live on the 13th. Anything you need from me?

You'll use three prompts in one Word chat and one in Cowork, and you'll approve everything.

!IMAGE[Steps 1 to 3 in the Word Copilot pane give the backstory, comments on clauses that break the playbook, and tracked changes. Step 4 in Cowork, opened from Word, gives a negotiation list, a one-pager and a reply to Luc saved to iManage.](instructions360859/legal-workflow.png "How the legal track flows")

## Before you start

- [] **iManage_Lab** shows as connected.
- [] You can see Luc's message in Teams.

## Open the agreement in Word

1. [] In Copilot, select the app launcher (the 3×3 grid of dots) in the top-left corner.
1. [] Select **More apps**, then **OneDrive**.
1. [] In the left pane, select **My files**, then open the **Trey Research** folder.
1. [] Double-click **Trey Research Vendor Agreement v4.2** to open it in Word.
1. [] In Word, select the **Copilot** icon in the top-right corner to open the Copilot pane.

> [!Knowledge] The iManage matter @[Trey Research – AI Platform Agreement](`Start-Process "https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io/work/link/w/Dev!1870"`){PowerShell} holds the @[Zava AI Procurement Playbook v2.1](`Start-Process "https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io/work/link/d/DEV!252567.1"`){PowerShell}: Zava's rules for what it will and won't accept in AI contracts. Open it to see what Copilot will read. Its Drafts folder is empty until Step 4.

## Step 1: Catch up

_Word, Copilot pane, Work IQ_

1. [] With the agreement open, in the Copilot pane, enter:

    +++Catch me up on the Trey Research deal in five bullets: what Hemanti and Luc asked for, what we've decided, and what's still open.+++

1. [] Check that the catch-up includes:

    - Hemanti's ask: Zava must own the fine-tuned model.
    - Luc's ask: no more abrupt model retirements. The last vendor gave two weeks' notice and Zava couldn't quote for a week.
    - What's still open: the draft meets neither ask. Trey Research owns models trained on Zava's data (§9.1), and can change or retire a model on 15 days' notice with no Zava veto (§§7.2–7.5).
    - Links from each bullet to Hemanti's email or the Teams chat.

    > [!Knowledge] Luc only asked if you can sign. Copilot pulled the backstory from an older email and a Teams chat, then checked it against the open draft, without you leaving the contract.

## Step 2: Flag the hard stops

_Same Word chat, iManage_Lab, Word legal skills_

1. [] In the same Copilot pane, enter:

    +++Which clauses in this agreement break the hard stops in our AI Procurement Playbook in the Trey Research AI Platform matter in iManage? Add a comment on each one with the playbook section.+++

1. [] Check that you see eight comment suggestions covering all six hard stops, each citing the playbook section and its hard-stop number.
1. [] Select **Apply 8 suggestions**.

    > [!Hint] Say _which clauses break_, not _review against the playbook_. That second phrase starts a different flow that asks you to upload a playbook.

## Step 3: Fix the two must-haves

_Same Word chat, iManage_Lab, edit contract skill_

1. [] In the same Copilot pane, enter:

    +++Now redline this so we own the fine-tuned model, and Trey Research can't change or retire the model without real notice and our approval. Explain each change in a comment.+++

1. [] Check that you see eight tracked changes, each with a comment:

    - Zava owns fine-tuned models, delivered in a portable format (§9.1).
    - 60 days' detailed notice and Zava approval before any model change or retirement (§§7.2–7.4).
    - Retired versions kept for 12 months, with migration help (§7.5).

1. [] Apply the first two changes, then select **Apply 6 suggestions**.

    > [!Knowledge] One business sentence, no section numbers. Copilot found the clauses itself and wrote in the playbook's positions.

## Step 4: Build the negotiation pack

_Copilot Cowork opened from Word, iManage_Lab, Work IQ_

> [!Alert] In Cowork, select **Customize** and turn on iManage_Lab. Then turn off the Fabric IQ plugin, which is on by default.

1. [] Open Cowork from Word, then enter:

    +++Get me ready for the December 10 session with Trey Research. Turn my redline and the flags into a negotiation list with our playbook fallbacks, check whether it covers what Colorado and New York regulators expect, write a one-page summary for Luc and Hemanti, and draft my reply to Luc. Save it all to the matter.+++

1. [] Check that Cowork produces:

    - A negotiation list with one row per change or flag, the playbook fallback, and _do not concede_ on hard stops.
    - A regulator check against the Colorado and New York rules.
    - A one-pager for Luc and Hemanti: the 10th is a negotiation, not a signing.
    - A reply to Luc, held for your approval, with files saved to the matter's Drafts folder.

1. [] Open Cowork's review list, check the one-pager and approve the reply to Luc.

    > [!Knowledge] Cowork keeps working in the background. One request becomes four deliverables across iManage and Outlook, and nothing is sent until you approve it.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Step 1 doesn't find Hemanti's email or the Teams chat | Ask +++What did Hemanti send me about Trey Research?+++ then rerun Step 1. |
| Copilot asks you to upload a playbook | Rephrase with _which clauses break the hard stops in our AI Procurement Playbook in iManage_. |
| Suggestions don't appear as comments or tracked changes | Make sure the agreement is the active document, then rerun the step. |
| Cowork is still working | Carry on, and come back to the review list when it's done. |

## Checkpoint

- [] Your catch-up linked to Hemanti's email and the Teams chat.
- [] The agreement has comments on the hard stops and a redline for the two must-haves.
- [] The negotiation list, one-pager and reply are in Drafts, and you approved the reply.

Copilot did the reading, the redlining and the drafting across email, Teams and iManage. You stayed the lawyer: every change has a reason, and nothing went out without your approval.

Other connectors that fit this pattern: LexisNexis and Legal Data Hunter.

> [!Note] Fictional parties adapted from the Harvey lab (MIT license). Not legal advice.

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Productivity: Prep a sales pitch

_About 10 minutes, plus a stretch step · Salesforce_Lab, Teams, Outlook · Copilot Cowork_

You own the Lakeshore Retail account. Lakeshore Retail has piloted the Aurora smart-home hub in 50 stores for six weeks, ahead of the public launch event on December 8. Your next step is the expansion pitch to roll it out to all 400 stores.

- Atul Manohar, Lakeshore Retail's Director of Store Operations, emailed ahead of the pitch. Their CFO, Nanami Nakayama, is joining and wants the all-in cost for 400 stores. Lakeshore Retail IT (Jahidi Juma) wants Zava's security documentation first.
- On the Teams pilot review call, Atul said a competitor, Boulder Innovations, quoted about 20% under your list price.

You'll prep the call, handle the price objection and book the security review, without leaving Copilot.

!IMAGE[All steps run in one Copilot Cowork task. Step 1 gives a call brief. Step 2 gives a grounded answer from the Teams call and win and loss history. Step 3 creates an Outlook invite and a Salesforce activity after you approve each. The stretch step logs the pilot review call.](instructions360859/productivity-workflow.png "How the productivity track flows")

## Before you start

- [] **Salesforce_Lab** shows as connected.
- [] Open **Copilot Cowork** and start a new task. Run every step in this one conversation, because your Salesforce changes are kept only within it.
- [] In Cowork, select **Customize** and turn on **Salesforce_Lab**. Then turn off the **Fabric IQ** plugin, which is on by default.

> [!Knowledge] To see what Copilot will read, open the @[Lakeshore Retail account](`Start-Process "https://mock-salesforce.yellowsand-9530f5dc.eastus.azurecontainerapps.io/lightning/r/Account/001Hp0000000001IAA/view"`){PowerShell} in Salesforce_Lab.

## Step 1: Prep the call

_Copilot Cowork, Salesforce_Lab call-prep skill, Outlook_

1. [] In the Cowork task, enter:

    +++Use Salesforce to prep me for my Lakeshore Retail expansion pitch.+++

1. [] Check that the brief includes:

    - The meeting: _Lakeshore Retail – Aurora expansion pitch_, Friday, November 20, 10:00–11:00 ET.
    - The deal: the _Lakeshore Retail – Aurora 400-store rollout_ opportunity, Proposal/Price Quote, $1,200,000, closing December 31.
    - Who's in the room: Atul (champion), Jahidi (IT security) and Nanami (CFO). Nanami isn't a Salesforce contact yet, so Copilot flags her as new.
    - What to cover: the price comparison, the security review and next steps.

    > [!Knowledge] The layout can vary between runs. The content is what matters. One prompt turned the CRM and your inbox into a brief that already points to the pitch's two risks.

## Step 2: Handle the price objection

_Same conversation, Teams meeting transcript, Salesforce_Lab win and loss history_

1. [] In the same task, enter:

    +++Lakeshore Retail says Boulder Innovations is 20% cheaper. How should I handle that? Use what they said on the pilot review call and our win/loss history against Boulder Innovations.+++

1. [] Check that the answer includes:

    - From the October 22 pilot review transcript: Boulder's $2,400 per store is the hub only, and lands around $3,250 per store all-in. Your counter-offer was 12% off ($2,640 per store against the $3,000 list) with install bundled.
    - The win: _Wide World Importers – Aurora 320-store rollout_, won against Boulder Innovations on all-in cost rather than sticker price.
    - The loss: _Tailspin Toys – Aurora 120-store rollout_, lost on price after leading with a discount.
    - The recommendation: don't match the 20%. Lead with the all-in cost for 400 stores, and offer 12% plus bundled install.

    > [!Knowledge] The numbers came from the Teams meeting, and the proof that the approach works came from Salesforce.

## Step 3: Book the security review and log it

_Same conversation, Salesforce_Lab schedule-meeting skill, Outlook calendar, write actions_

1. [] In the same task, enter:

    +++Send Jahidi and Atul a calendar invite for a 45-minute Aurora security review next week, and log it on the Lakeshore Retail opportunity.+++

1. [] Review the two or three free slots Copilot proposes for next week.
1. [] At the first confirmation, check the invite preview and approve it. Copilot creates the Outlook invite.
1. [] At the second confirmation, check the Salesforce activity preview and approve it. Copilot logs it on the opportunity.
1. [] Open the link to the Salesforce record and check that the changes from your conversation appear.

    > [!Note] _Next week_ follows today's date, so the proposed slots depend on when you run the lab.

## Stretch: Log the pilot review call

1. [] In the same task, enter:

    +++Log the pilot review call on the Lakeshore Retail opportunity.+++

1. [] Approve the confirmation, then open the opportunity's **Activity** tab to see the completed meeting task dated October 22.

> [!Hint] Prefer not to make changes? Try +++Draft an email to Atul and Nanami ahead of the pitch to confirm the agenda.+++ It stays an Outlook draft.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Copilot asks which account or meeting | Reply +++The Lakeshore Retail expansion pitch.+++ |
| The brief doesn't mention Nanami | Ask +++Who's on the call, and what does each of them care about?+++ |
| Step 2 answers from general knowledge | Reply +++Use the Teams transcript of the Lakeshore Retail pilot review and our closed deals against Boulder Innovations in Salesforce.+++ |
| Slot picking runs long | Reply +++The first slot.+++ |
| Copilot asks whether to email or invite | Reply +++Send the invite.+++ |

## Checkpoint

- [] Your call brief covers the deal, all three attendees and the two risks.
- [] Copilot didn't match the 20% and proposed 12% plus bundled install, led by the all-in cost.
- [] The security review is on your calendar and logged on the Lakeshore Retail opportunity.

Copilot moved from finding information to finishing the job: a brief, a grounded answer, a booked meeting and an updated CRM, with you approving each change.

Other connectors that fit this pattern: Notion, Intercom and Zoom.

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Engineering: Find what's blocking

_About 15 minutes · Jira and Confluence (synced), GitHub_Lab, Rovo_Lab, Teams · Copilot Chat, Copilot Cowork_

You're the product manager for Aurora, a smart-home hub that retail stores use to track devices. Lakeshore Retail is piloting it, and on Monday, November 23, every pilot store goes live.

Atul, the pilot coordinator, has emailed again: hubs keep showing _Offline_ after they reconnect, and staff are restarting devices that are working fine. On the Sprint 24 board, almost everything is on track. One item isn't, and it's Atul's bug. Before you answer Atul, you need to know who the work is really waiting on.

| Person | Role |
|:---|:---|
| Emil Vanggaard (you) | Product manager; owns the Lakeshore Retail pilot. |
| Atul Manohar | Pilot coordinator, Lakeshore Retail. |
| Triin Lepp | Engineer working on the fix. |
| Maria Oliva | Engineer who owns rollout and reconnect testing. |
| Tama Surya | Platform lead; signs off design changes and reviews the fix. |
| Kerry Allen | Engineering lead; runs the sprint. |

You won't change any code. You'll investigate in Copilot Chat, then switch to Copilot Cowork to act.

!IMAGE[Steps 1 and 2 in Copilot Chat find the at-risk item and what it's waiting on across Jira, Confluence and GitHub. Steps 3 and 4 in Copilot Cowork send Tama a Teams message and create a one-slide sprint update.](instructions360859/engineering-workflow.png "How the engineering track flows")

## Before you start

- [] **GitHub_Lab** and **Rovo_Lab** show as connected.
- [] The **Jira** and **Confluence** synced connectors are available in your tenant.

> [!Knowledge] To see what Copilot will read, open the @[Aurora Sprint 24 board](`Start-Process "https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/jira/software/projects/AUR/boards/57"`){PowerShell}, the @[ADR-014 page](`Start-Process "https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/wiki/spaces/AUR/pages/98457"`){PowerShell} in Confluence and the @[aurora-status pull requests](`Start-Process "https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/zava-lab/aurora-status/pulls"`){PowerShell} in GitHub.

## Step 1: Check how the sprint is going

_Copilot Chat, Jira_

1. [] In Copilot, start a new chat, then enter:

    +++What's the status of Aurora Sprint 24? Is anything at risk for the Lakeshore Retail pilot expansion?+++

1. [] Check that you see a summary of the six Sprint 24 items, with one at risk: AUR-142, _Aurora hubs remain offline after reconnect_, with citations to the Jira items.

    > [!Knowledge] The board is mostly green, and Copilot picks out the one item that matters to your customer.

## Step 2: Find what AUR-142 is waiting on

_Same chat, Jira, Confluence, GitHub_Lab_

1. [] In the same chat, enter:

    +++What's the current status of AUR-142, and what is it waiting on? Check Jira, Confluence and GitHub.+++

1. [] Check that the answer joins all three sources:

    - Jira: AUR-142 is In Progress and at risk. Triin can't give a date until a design decision gets platform sign-off.
    - Confluence: the pilot moves to the event-driven status service on November 20, and ADR-014 is still _Proposed_, with Tama Surya as the decision owner.
    - GitHub: PR #287 is open. It fixes only the old polling service, and Tama requested changes.
    - The answer: the fix is waiting on Tama's approval of ADR-014.

    > [!Knowledge] No single tool had the whole story. Joining them shows the work isn't stuck on code. It's waiting on one approval.

## Step 3: Ask Tama for the decision

_Copilot Cowork, Teams_

> [!Alert] In Cowork, select **Customize** and turn on GitHub_Lab and Rovo_Lab. Then turn off the Fabric IQ plugin, which is on by default.

1. [] Open **Copilot Cowork** and start a new task. Cowork may not have your Chat conversation, so these prompts include the context they need.
1. [] Enter:

    +++Send Tama Surya a Teams message. Ask Tama to approve ADR-014 so Triin can start the event-driven fix for AUR-142, and to re-review PR #287 once it's updated. Mention the November 20 cutover and include links to the ADR, the Jira item and the PR.+++

1. [] Check the recipient and the message, then approve it.

## Step 4: Turn the sprint into a slide

_Same Cowork task, Rovo_Lab sprint-to-slides skill_

1. [] In the same task, enter +++/skill sprint-to-slides+++, press Shift+Enter for a new line, then enter:

    +++Create one PowerPoint slide summarizing Aurora Sprint 24 for engineering leadership: what's on track, the one item at risk, what it's waiting on, and the next steps.+++

1. [] Check that the slide shows the sprint goal and dates, AUR-142 at risk, the blocker (ADR-014 waiting on Tama), next steps with owners, and no invented delivery date.

    > [!Knowledge] A partner skill turned live Jira and Confluence data into a leadership-ready slide in one step.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Step 1 doesn't find the sprint | Ask +++Search Jira for the Aurora Sprint 24 work items.+++ |
| Step 2 misses Confluence or GitHub | Ask +++Find ADR-014 in Confluence+++ or +++Search GitHub for a pull request that references AUR-142.+++ |
| The skill returns an outline, not a slide | Reply +++Create the .pptx file with one slide.+++ |
| Cowork sends without showing you the message | Tell a proctor. Messages should always ask for approval first. |

## Checkpoint

- [] You know which Sprint 24 item is at risk and why.
- [] You know the fix is waiting on Tama's approval of ADR-014.
- [] A Teams message to Tama is sent or ready for your approval.
- [] You have one sprint slide for leadership.

Copilot found the one item at risk, joined Jira, Confluence and GitHub to show what it was waiting on, then Cowork asked for the decision and gave leadership a one-slide update.

Other connectors that fit this pattern: Azure DevOps, Linear and Webflow.

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Bring your own app: Zava Expense

_About 20 minutes · Zava Expense (custom MCP connector), Outlook · Microsoft 365 admin center, Copilot Chat, Excel_

You'll connect Zava Expense, Zava's in-house expense app, as a custom connector with no code, then use it from Copilot to file a trip, from receipts in your inbox to a submitted report.

You're also just back from a client trip to Seattle for the Fabrikam, Inc. partnership review, and Zava Expense has emailed a reminder: submit your expenses by Friday, November 20. Your receipts are scattered across your inbox, and your last report was rejected for a missing receipt.

!IMAGE[Set up your own app in the admin center through a custom MCP server, then run Steps 1 to 4 in one Copilot chat.](instructions360859/custom-lob-workflow.png "How the bring your own app module flows")

## Before you start

- [] You finished one of the tracks.
- [] You can open the Microsoft 365 admin center. Your lab account has admin rights.

## Connect Zava Expense

Zava Expense isn't in the connector catalog. Zava's app team has already made it available through a custom MCP server (a standard way for AI tools to talk to an app), so you only need to connect it.

1. [] In the browser, open the Microsoft 365 admin center at +++https://admin.microsoft.com+++.
1. [] Go to **Copilot** › **Connectors**.
1. [] On the **Gallery** tab, under **Created by your org**, select **Create a new connector**, then **Connect to MCP server**.
1. [] Fill in the form:

    | Field | Enter |
    |:---|:---|
    | Display name | +++Zava Expense+++ |
    | Description | +++Zava's in-house expense app. Use it to see the signed-in employee's expense reports and why any were rejected or returned, find corporate card charges for a trip, create a report from receipts, check it against the Zava travel policy, submit it for manager approval, and compare travel spend with budget.+++ |
    | Base URL | +++https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp+++ |
    | Developer name | +++Zava+++ |
    | Website URL | +++https://contoso.com+++ |
    | Privacy URL | +++https://contoso.com/privacy+++ |
    | Terms of use URL | +++https://contoso.com/terms+++ |
    | Authentication | No Auth |

    > [!Knowledge] Copilot reads the description to decide when to use Zava Expense and what to ask it. A good description says, in plain words, what data the app holds and what it can do.

    > [!Note] This lab uses _No Auth_ so you can connect quickly. In your own tenant, choose the authentication your app needs, such as Microsoft Entra SSO or OAuth 2.0.

1. [] Save the connector.
1. [] Under **Staged rollout**, make Zava Expense available to yourself. It now appears under **Your connections**, next to the catalog connectors.

    > [!Note] Changes can take up to 10 minutes to appear.

1. [] In Copilot, open **Settings** › **Sources** and connect **Zava Expense**.

===

# File your Seattle trip

Run Steps 1 to 4 in one new chat. Each new chat starts from the original data.

## Step 1: Check where you stand

1. [] In Copilot, start a new chat, then enter:

    +++Using Zava Expense, show me my open expense reports. Were any of them rejected or sent back, and why?+++

1. [] Check that you see four open reports:

    - ER-1044 (Dallas) was rejected: the $142.60 Pappas Bros receipt is missing.
    - ER-1046 was returned: it has no business purpose.
    - ER-1045 (Austin, $631.50) and ER-1051 (October local expenses, $953.09) are pending approval.

## Step 2: File the trip

1. [] In the same chat, enter:

    +++Find the receipts from my Seattle trip in my inbox and use them to create a Zava Expense report for the Fabrikam, Inc. partnership review. Check the report against our travel policy, but don't submit it yet.+++

1. [] Check that Copilot creates draft report ER-2001 with six items totalling $2,052.65 and flags:

    - Blocking: the Westin charged $389 for the night of October 28, which is $139 over the $250 Seattle cap.
    - Warning: the $52.30 Uber ride was charged twice (TX-10111). Copilot suggests asking Ebere Ibeabuchi in Finance Operations to reverse it.

## Step 3: Fix and submit

This step submits the report, so Copilot asks for your approval first.

1. [] In the same chat, enter:

    +++Add a justification for the $389 Westin night: a city-wide convention pushed up hotel rates, and no hotel near the Fabrikam, Inc. office was under the cap. Then submit the report to my manager.+++

1. [] Check that Copilot reruns the policy check with no blocking issues and one justified exception.
1. [] When the approval card appears, approve it.
1. [] Check that Copilot confirms ER-2001 ($2,052.65) was submitted to Hannes Niemi.
1. [] Check the status: +++Has my Seattle report gone through? Who's approving it?+++

## Step 4: Review your spend

1. [] In the same chat, enter:

    +++How am I doing against my Q4 travel budget? Put it in an Excel workbook with a chart.+++

1. [] Check that you've spent $4,309.55 of $6,800 (63%), you're over budget on meals and entertainment (106%) and ground transport (111%), and Copilot creates an Excel workbook with a chart.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Zava Expense doesn't appear in Sources | Check that staged rollout includes you, wait a few minutes, then refresh Copilot. |
| Copilot doesn't use Zava Expense | Start the prompt with _Using Zava Expense_. |
| Copilot says Zava Expense isn't responding | Wait 15 seconds, then send the same prompt again in the same chat. |
| Step 2 misses some receipts | Ask +++Find all my Seattle receipts from October in my inbox.+++ |

## Checkpoint

- [] Zava Expense is connected and shows in your sources.
- [] ER-2001 was checked against policy, justified and submitted after your approval.
- [] You have an Excel summary of your Q4 travel spend.

## What you take away

- **Bring your in-house apps into Copilot.** If an app is available through an MCP server, you can connect it in minutes, with no code.
- **Real work, not just answers.** Copilot read your inbox, built the report, fixed the policy issue and submitted it, and asked before submitting.
- **Governed like every other connector.** Admins choose who gets it, and staged rollout lets you test it before everyone sees it.

===

# Wrap up the lab

## What you did

| Track | What Copilot finished |
|:---|:---|
| Finance | A Litware committee pack in Excel and a memo in Word, from LSEG, FactSet and Moody's |
| Legal | Flags and a redline in Word, then a negotiation pack in Cowork, from Work IQ and iManage |
| Productivity | A call brief, a grounded answer to a price objection, and a booked and logged meeting, from Salesforce, Teams and Outlook |
| Engineering | The sprint's one at-risk item and what it's waiting on, a Teams message and a sprint slide, from Jira, Confluence and GitHub |
| Bring your own app | An expense report checked, fixed and submitted, plus a spend summary in Excel, from Zava Expense |

## Key takeaways

1. **Connect once, use everywhere.** A connector set up once works across Copilot Chat, Cowork, Word, Excel and PowerPoint.
1. **The catalog covers the popular tools; MCP covers the rest.** Pick from 300+ connectors, and connect your own apps with no code.
1. **Skills bring the method, not just the data.** Partner skills shape how Copilot works with each source.
1. **Write actions stay in your control.** Copilot acts with your permissions, and only after you approve.
1. **From answers to finished work.** You can find the information, decide and act without leaving Copilot.

## Govern what you connect

Every connector you used today, including your own app, is managed in the same place:

- Admins allow or block connectors and org-built apps in the Microsoft 365 admin center.
- Staged rollout lets you start with a pilot group.
- Copilot asks before it sends, books, updates or submits anything.

## Your next step

Enable the connectors that matter most to your organization. Start with the systems where your people spend their day, such as your CRM, ticketing, code, documents and line-of-business apps.

## Share your feedback

!IMAGE[LAB654 feedback slide. Scan the first QR code to rate the session on the Ignite page, at aka.ms/ignite2026-feedback. Scan the second QR code to open an issue in the lab repo, at aka.ms/ignite2026-LAB654.](instructions360859/lab654-feedback.png "LAB654 feedback")

Your feedback helps us improve this lab for future events.

- **Rate the session.** Give your satisfaction score and written feedback about the lab at [aka.ms/ignite2026-feedback](https://aka.ms/ignite2026-feedback).
- **Suggest changes to the content.** For ideas to improve the lab content or docs, open an issue at [aka.ms/ignite2026-LAB654](https://aka.ms/ignite2026-LAB654).

## Keep learning

- [Ignite 2026 next steps](https://aka.ms/ignite26-next-steps)
- [Microsoft AI Skills Navigator](https://aka.ms/ignite26-asn)
- [Microsoft Learn](https://aka.ms/ignite26-learn)

Thanks for joining LAB654!
