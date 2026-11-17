@lab.Title

## Welcome to your lab environment

To begin, sign in to the virtual machine with this password: +++@lab.VirtualMachine(ignite26lab654).Password+++

**Note:** Text formatted as an +++example+++ represents type text. Clicking on this text will automatically insert it to prevent any typing errors.

**Note:** Copilot prompts are formatted as ++example prompt++. Select a prompt to copy it, then paste it into Copilot with Ctrl+V.

> [!Note] This lab runs in a demo tenant with fictional people, companies and data. Financial and legal outputs are for the exercise only. They aren't investment or legal advice.

## Sign in to Copilot

1. [] On the taskbar at the bottom of the virtual machine, select **Microsoft Edge**.

    !IMAGE[The Windows taskbar, with the Microsoft Edge icon highlighted.](instructions360859/taskbar-edge.png "Microsoft Edge on the taskbar"){400}

1. [] In Edge, go to +++https://copilot.cloud.microsoft/+++.
1. [] Sign in with this username: +++@lab.CloudCredential(Ignite-LAB654).Username+++
1. [] When you're asked for a password, enter: +++@lab.CloudCredential(Ignite-LAB654).Password+++
1. [] If you see _Let's keep your account secure_ or you're asked for a code, follow the steps in **Verify your sign-in** below. If not, you're signed in: skip to the end of this page.

> [!Hint] If a sign-in popup is blocked at any point, allow popups for the Copilot site and try again.

## Verify your sign-in

Your lab account may ask for a second check (multi-factor authentication) when you sign in. Use the **Contoso Authenticator App** on the virtual machine desktop to get the code. You don't need your phone.

!IMAGE[Contoso Authenticator App icon: a blue floppy disk with a yellow and blue snake logo.](instructions360859/contoso-authenticator-icon.png "Contoso Authenticator App icon"){64}

### Set up the app the first time

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

    > [!Alert] If a _Windows protected your PC_ window appears, select **More info**, then **Run anyway**. The app is safe to run in this lab.

    !IMAGE[The Windows protected your PC window from Microsoft Defender SmartScreen, with a More info link under the message and a Don't run button.](instructions360859/mfa-05a-smartscreen.png "Windows protected your PC")

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

### Enter a code when you're asked again

1. [] Open **Contoso Authenticator App** from the desktop, select **Copy** next to your account, then paste the code in the browser.

> [!Note] Codes change regularly, and the app shows when the next one arrives. If a code is rejected, copy the new one and try again.

### If it goes wrong

#### The app says No QR code found on screen

The app window is probably covering the QR code. Move the app window away from the QR code, then select **Scan QR from Screen** again.

!IMAGE[The Contoso Authenticator App window covering part of the QR code, with the error No QR code found on screen.](instructions360859/mfa-10-no-qr-found.png "No QR code found on screen")

#### Scanning still doesn't work

Zoom the browser to 120% so the QR code is larger, then select **Scan QR from Screen** again.

!IMAGE[The browser zoomed in so the QR code is larger and fully visible next to the Contoso Authenticator App window.](instructions360859/mfa-11-zoom-in.png "Zoom the browser")

#### The app says Failed to parse QR code: Invalid OTP URI

You're on the page for the Microsoft Authenticator phone app. In the browser, go back, select **Set up a different authentication app** and scan the new QR code.

!IMAGE[The error Failed to parse QR code: Invalid OTP URI, next to a QR code page that mentions the Microsoft Authenticator app.](instructions360859/mfa-12-invalid-otp-uri.png "Invalid OTP URI")

When you're signed in to Copilot, select **Next**.

===

# Prepare a clean environment

Someone may have used this lab account before you. Reset it so you start from the original files.

1. [] Select @[Reset my lab environment](`C:\LabFiles\reset-lab.bat @lab.CloudCredential(Ignite-LAB654).Username`){Shell visible}. A command window opens, and a browser tab opens to sign you in.
1. [] If the browser asks you to pick an account, select your lab account. If it asks you to approve permissions for _Microsoft Graph Command Line Tools_, select **Accept**.
1. [] When the tab says _Lab clean-up signed in_, close the tab.
1. [] In the command window, wait for _Your lab environment is clean_. The window closes by itself.

> [!Note] The reset changes only your own account. You can run it again later if you want to start a track over.

> [+Help] If the reset doesn't finish, select to see what to do.
>
> - _Signed in as another account_: in the browser, sign in with your lab username +++@lab.CloudCredential(Ignite-LAB654).Username+++ and password +++@lab.CloudCredential(Ignite-LAB654).Password+++, then select the reset link again.
> - Nothing happens, or you see any other message: ask a proctor.

When the reset finishes, select **Next** to start the lab.

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

**Connectors.** Connectors call the source live, signed in as you. Copilot picks the right source for your question, respects what you're allowed to see and cites where each answer came from.

**Connector skills.** A skill packages a partner's expertise, such as how sales teams prep a call or how analysts assess credit. Copilot loads a skill when your request needs it, so you get the partner's method as well as their data.

**Plugins.** A plugin is one package that an admin deploys once. It can bundle connectors (data and tools), skills (the method) and agents (focused assistants you chat with directly). This lab focuses on connectors and skills.

**Write actions.** Copilot can change things in the source system, such as logging a meeting on a SalesDesk opportunity or saving a draft to a document matter. You see a confirmation first, and nothing changes until you approve it.

===

# Get started with connectors

In this part, you'll find connectors in the catalog, check that the ones for your track are ready and ask your first grounded question.

## Discover connectors

1. [] If Copilot isn't open, select **Microsoft Edge** on the taskbar, then go to +++https://copilot.cloud.microsoft/+++.
1. [] In Copilot, select the three dots (**...**) in the top-right corner, then select **Settings**.

    !IMAGE[The menu under the three dots in the top-right corner of Copilot, with Settings highlighted.](instructions360859/copilot-settings-menu.png "Open Settings")

1. [] In **Settings**, select **Sources**.

    !IMAGE[The Settings window with Sources selected in the left pane, listing connectors such as HubSpot, Intercom and Legal Data Hunter.](instructions360859/rebrand-copilot-settings-sources.png "Sources in Settings"){600}
1. [] Browse the catalog. It has more than 300 connectors, from CRM and ticketing to code, wikis and market data.
1. [] Find the connectors for the track you'll take:

    | Track | Connectors |
    |:---|:---|
    | Finance | +++LSEG_Lab+++, +++FactSet_Lab+++, +++Moodys_Lab+++ |
    | Legal | +++iManage_Lab+++ |
    | Productivity | +++SalesDesk_Lab+++ |
    | Engineering | +++GitHub_Lab+++, +++EngHub_Lab+++ |
    | Bring your own app (everyone) | Zava Expense (you'll add it yourself later) |

    Outlook, Teams and your Microsoft 365 files are available in every track.

> [!Note] All the connectors above are mock versions of the real connectors, built for this lab. They behave like the real ones and come with the same skills, but they serve sample data for Zava. You don't need a third-party account to use them. Changes you make with them are visible only in the conversation where you make them.

## Check your sources are ready

1. [] Close **Settings**.
1. [] In Copilot, select the plus icon (**+**) at the left of the message box, then select **Change data sources**.
1. [] In **Select sources**, check that **Microsoft 365 data** and the connectors for your track are turned on. They're all on by default.

    !IMAGE[The Select sources window, with Microsoft 365 data, EngHub_Lab, FactSet_Lab, GitHub_Lab, iManage_Lab, LSEG_Lab and Moodys_Lab all turned on.](instructions360859/rebrand-copilot-select-sources.png "Select sources"){500}

1. [] If one of your track's connectors is off, turn it on. Then close **Select sources**.

> [!Knowledge] In a real organization, an admin deploys connectors like these once, and people sign in to them with their own accounts. In this lab, that setup has been done for you.

## Ask your first grounded question

Each question below needs facts from a system you'd normally open on its own: market data, a document management system, a CRM record or an EngHub ticket. Without connectors, you'd search that system and copy the answer across. With connectors, Copilot fetches it for you and cites where it came from.

1. [] In Copilot, select **Chat** at the top of the left pane, then select **New chat**.

    !IMAGE[The Copilot left pane with the Chat tab selected and New chat highlighted below it.](instructions360859/copilot-new-chat.png "Start a new chat"){600}

1. [] Select the question for your track:

    - Finance: ++Using LSEG, what was Litware's earnings per share last quarter compared with the analyst consensus?++
    - Legal: ++Using iManage, what are the hard stops in the Zava AI Procurement Playbook?++
    - Productivity: ++What's the stage and amount of the Lakeshore Retail opportunity in SalesDesk?++
    - Engineering: ++What's the status of EngHub work item AUR-142?++

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
>
> !IMAGE[The model menu opened from Auto at the top of the chat, with GPT selected and a list of GPT models: GPT-5.6 Sol Quick response, GPT-6, GPT-5.6 Sol Think deeper and GPT-6.1 Sol.](instructions360859/copilot-model-picker-gpt.png "Switch to a GPT model"){600}

===

# Finance: Should we buy more Litware?

_About 20 minutes · LSEG_Lab, FactSet_Lab, Moodys_Lab · Copilot Cowork_

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

!IMAGE[All steps run in one Cowork task. Step 1 gives a verified verdict. Steps 2 and 3 build the workbook, add scenarios and credit analysis, then give a pressure-tested view and memo.](instructions360859/rebrand-finance-workflow.png "How the finance track flows")

## Before you start

First, check that Kristian's message is waiting for you in Teams.

> [!Knowledge] LSEG, FactSet and Moody's are financial data providers that investment teams use for market data, company fundamentals and credit ratings. **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab** are the lab versions of their connectors.

### Read Kristian's message in Teams

1. [] Select **Microsoft Edge** on the taskbar, then go to +++https://teams.cloud.microsoft/+++.
1. [] In the left rail, select **Chat**.
1. [] Under **Chats**, select **Kristian Stensen**.
1. [] Check that you see Kristian's message: _Committee wants a view on Litware Monday. Should we add more? Bring a short memo._

    !IMAGE[Microsoft Teams on the web with the Chat view open. Kristian Stensen is selected under Chats, and his message asking for a view on Litware for Monday's committee is shown in the conversation.](instructions360859/finance-teams-kristian-message.png "Kristian's message in Teams"){600}

### Turn on the finance connectors in Cowork

You'll run every step of this track in one Copilot Cowork task. Cowork can run long tasks, like building a workbook, and saves what it creates to your OneDrive. It uses only the plugins you turn on, so first turn on the finance connectors.

1. [] Open a new browser tab and go to +++https://copilot.cloud.microsoft/+++.
1. [] In Copilot, select **Cowork** at the top of the left pane.
1. [] In the left pane, select **Customize**.
1. [] Next to **Added**, select **Manage all**.

    !IMAGE[The Cowork Customize page, with Customize highlighted in the left pane and Manage all highlighted next to the Added list of connectors.](instructions360859/rebrand-cowork-customize.png "Open Customize, then Manage all"){600}

1. [] Turn on **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab**.
1. [] Turn off **Fabric IQ**, which is on by default.

    !IMAGE[The Added list in Cowork Customize, with Moodys_Lab, LSEG_Lab and FactSet_Lab turned on and Fabric IQ turned off.](instructions360859/rebrand-cowork-customize-finance.png "Turn on the finance connectors"){600}

## Step 1: Run a sense check

### 1a. Check whether Litware beat expectations

1. [] In the left pane, select **New task**.

    !IMAGE[The Copilot left pane with the Cowork tab selected and New task highlighted below it.](instructions360859/copilot-new-cowork-task.png "Start a new Cowork task"){600}

1. [] Enter:

    ++I'm preparing a recommendation for Monday's investment committee on whether our portfolio should buy more Litware. To start with, did Litware beat analysts' expectations last quarter? Using LSEG, compare its actual earnings per share and revenue with the analyst consensus, and show the quarter and source.++

1. [] Check that you see what Litware earned last quarter against what analysts expected, with LSEG cited as the source.

    > [!Knowledge] LSEG can return charts and analysis cards, not just text: the provider's own experience, inside Copilot.

    > [!Hint] **A skill was used here.** A skill is a set of expert instructions that comes with a connector. You didn't ask for it: Copilot picked LSEG's **equity-research** skill because you asked to compare results with analyst forecasts. The skill tells Copilot how an analyst does this: pull consensus estimates and actuals, then show the gap in a clear table.

### 1b. Compare Litware with its rivals

1. [] In the same Cowork task, enter:

    ++Using FactSet, compare how profitable Litware, A. Datum and Relecloud have been over the past 5 years, using gross margin and return on invested capital (ROIC).++

1. [] Check that you see FactSet profitability figures for all three companies and a clear view of which is strongest.

### 1c. Decide if it's worth a deeper look

1. [] In the same Cowork task, enter:

    ++What is Litware's credit rating and outlook according to Moody's and what's driving them? Then, based on everything so far, give me a one-line verdict on whether Litware is worth a deeper look.++

1. [] Check that you see a Moody's rating and outlook with the reasons behind them, then a one-line verdict that draws on all three sources.

    > [!Hint] **Another skill, picked for you.** Copilot used Moody's **company-analysis** skill because you asked about a credit rating and what's driving it. The skill tells Copilot to find the company in Moody's first, then read its rating, outlook and credit opinion, without inventing any numbers.

    > [!Knowledge] Three connectors, one conversation. Copilot keeps the context, so the verdict builds on the LSEG and FactSet answers above it.

## Step 2: Dig into the numbers

### 2a. Build the committee workbook

1. [] In the same Cowork task, enter:

    ++Using LSEG, create an Excel workbook called "Litware Committee Pack" with an equity research snapshot of Litware: analysts' earnings and revenue forecasts for this year and next (FY1, FY2), how many analysts cover it and how much they disagree, 5 years of financials, and valuation. Cite sources and dates.++

1. [] Check that Cowork uses LSEG's equity research skill and creates a workbook named **Litware Committee Pack**, with sources and dates.

    > [!Hint] Building the workbook can take a few minutes. Select the thought process to watch what Cowork is doing.

### 2b. Model the upside

1. [] In the same Cowork task, enter:

    ++Using LSEG, add a "Scenarios" sheet with worst, middle and best cases (bear, base, bull), using the lowest, average and highest FY2 earnings-per-share forecasts and Litware's current share price. Make the price-to-earnings (P/E) multiple an editable input for each case and use formulas to show the implied share price and % upside or downside.++

1. [] Check that a **Scenarios** sheet appears, built on LSEG forecasts and share price, with LSEG cited.
1. [] Select **Litware Committee Pack** in the task to open the workbook next to the chat and check the new sheet.
1. [] On the **Scenarios** sheet, change one P/E multiple and watch the implied price and upside update.

    > [!Knowledge] You didn't re-explain anything. Cowork kept the context from the task, and these are real formulas you can check.

### 2c. Check that it's financially sound

1. [] In the same Cowork task, enter:

    ++Using Moody's, add a "Credit" sheet with a credit SWOT for Litware (strengths, weaknesses, opportunities and threats) and the factors that could lead to a rating upgrade or downgrade.++

1. [] Check that a **Credit** sheet appears with a SWOT and upgrade and downgrade drivers, sourced from Moody's.

## Step 3: Back-check and report

### 3a. Pressure-test your view (stretch goal)

1. [] In the same Cowork task, continuing from Step 2, enter:

    ++My view: we should buy more Litware because its strong profits and earnings growth justify its high share price. Using the Litware Committee Pack and the latest data from LSEG and Moody's, pressure-test this view: give the evidence for and against, the strongest case against buying, and the questions the committee is likely to ask.++

1. [] Check that you see evidence on both sides, the strongest counter-argument and likely committee questions, each backed by sourced figures.

    > [!Knowledge] Copilot argued against your view, so the committee isn't the first to find the weak spot.

### 3b. Write the committee memo

1. [] In the same Cowork task, enter:

    ++Turn this into a Word memo for the investment committee, reusing the workbook's charts. Cite LSEG, FactSet and Moody's as the source for every number, and flag any missing data.++

1. [] Check that every number in the memo is cited, the workbook charts are reused and any gaps in the data are flagged.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Copilot answers without a source | Start the prompt with _Using LSEG_ or _Using Moody's_. |
| The first answer from a connector is slow | Wait a few seconds and ask again. |
| Copilot asks which company or ticker | Reply ++Litware (LITW)++. |
| Workbook steps don't apply to the right file | In the same Cowork task, start the prompt with _In Litware Committee Pack_. |

## Checkpoint

- [] You compared Litware's results with consensus, rivals and its credit rating.
- [] Your **Litware Committee Pack** has snapshot, **Scenarios** and **Credit** sheets.
- [] You have a committee memo with sources.

## What you take away

- **A full finance workflow in Copilot**, from a first question to a committee memo, on trusted data from LSEG, FactSet and Moody's.
- **Excel analysis on verified data, in minutes**, with real formulas you can trace back to the source.
- **Reusable for any company.** Swap Litware for another company and run the same prompts.

The same pattern works with other connectors. Try them in your own tenant for similar scenarios.

| S&P Global | Morningstar |
|:---:|:---:|
| !IMAGE[S&P Global logo](instructions360859/connector-sp-global.png "S&P Global"){200} | !IMAGE[Morningstar logo](instructions360859/connector-morningstar.png "Morningstar"){200} |

_Logos are trademarks of their respective owners._

> [!Hint] In this track, Copilot picked skills for you based on what you asked. You can also call a skill by name with a slash command. To try that, take the [engineering track](#engineering-find-whats-blocking).

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Legal: Can we sign on the 10th?

_About 20 minutes · Work IQ (email and Teams), iManage_Lab · Copilot Cowork_

Zava wants Trey Research's AI to make up to 4 million underwriting decisions a month: a five-year, $14.75 million deal. Regulators in Colorado and New York hold the insurer responsible for vendor AI. Zava trains the AI on its own claims data, so it must own what gets built.

Nothing is signed. Trey Research sent its own one-sided draft, and it's in your OneDrive. Zava's playbook is in the iManage matter. A negotiation session with Trey Research is booked for Thursday, December 10.

| Person | Role |
|:---|:---|
| Emil Vanggaard (you) | Associate General Counsel, Technology Transactions. You own this contract. |
| Luc Lacombe | Chief Underwriting Officer. Business owner; wants the AI live on the 13th. |
| Hemanti Baishya | SVP, Strategic Procurement. Emailed you the business's must-haves two weeks ago. |

Luc has pinged you on Teams:

> Morning Emil. Have you had a chance to look at Trey Research's contract? We'd like to sign at the session with them on the 10th so we can go live on the 13th. Anything you need from me?

You'll do it all in one Copilot Cowork task: four prompts, plus an optional fifth. Cowork reads your email and Teams, reads the playbook in iManage, and works on the agreement in your OneDrive, opening it right next to the chat. You approve every edit and every invite.

!IMAGE[Steps 1 to 4 run in one Copilot Cowork task. Step 1 gives the backstory from email and Teams, Step 2 adds comments on clauses that break the playbook, Step 3 adds tracked changes for the two must-haves, and Step 4 gives a one-page negotiation sheet and a prep invite for Luc and Hemanti. Optional Step 5 saves the sheet to iManage.](instructions360859/legal-cowork-workflow.png "How the legal track flows")

## Before you start

First, check that Luc's message is waiting for you in Teams. Then you'll set up Cowork.

> [!Knowledge] iManage is a document management system that law firms and legal teams use to store contracts, playbooks and other matter documents. **iManage_Lab** is the lab version of the iManage connector.

### Read Luc's message in Teams

1. [] Select **Microsoft Edge** on the taskbar, then go to +++https://teams.cloud.microsoft/+++.
1. [] In the left rail, select **Chat**.
1. [] Under **Chats**, select **Luc Lacombe**.
1. [] Check that you see Luc's message asking whether you've looked at Trey Research's contract and whether you can sign on the 10th.

    !IMAGE[Microsoft Teams on the web with the Chat view open. Luc Lacombe is selected under Chats, and his message about signing Trey Research's contract on the 10th is shown in the conversation.](instructions360859/legal-teams-luc-message.png "Luc's message in Teams"){600}

> [!Knowledge] The iManage matter @[Trey Research – AI Platform Agreement](`Start-Process "https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io/work/link/w/Dev!1870"`){PowerShell} holds the @[Zava AI Procurement Playbook v2.1](`Start-Process "https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io/work/link/d/DEV!252567.1"`){PowerShell}: Zava's rules for what it will and won't accept in AI contracts. Open it to see what Cowork will read. Section 14 lists six hard stops, positions Zava never concedes. Its Drafts folder is empty until Step 5.

### Set up Copilot Cowork

Cowork uses only the plugins you turn on, so first turn on iManage_Lab.

1. [] Open a new browser tab and go to +++https://copilot.cloud.microsoft/+++.
1. [] Select **Cowork** at the top of the left pane.
1. [] In the left pane, select **Customize**.
1. [] Next to **Added**, select **Manage all**.

    !IMAGE[The Cowork Customize page, with Customize highlighted in the left pane and Manage all highlighted next to the Added list of connectors.](instructions360859/rebrand-cowork-customize.png "Open Customize, then Manage all"){600}

1. [] Turn on **iManage_Lab**.
1. [] Turn off **Fabric IQ**, which is on by default. Leave every other plugin off.

    !IMAGE[The Added list in Cowork Customize, with iManage_Lab turned on and Fabric IQ, Moodys_Lab, SalesDesk_Lab, LSEG_Lab, FactSet_Lab, EngHub_Lab and GitHub_Lab turned off.](instructions360859/rebrand-legal-cowork-customize.png "Turn on iManage_Lab"){600}

1. [] In the left pane, select **New task**.

    !IMAGE[The Copilot left pane with the Cowork tab selected and New task highlighted below it.](instructions360859/copilot-new-cowork-task.png "Start a new Cowork task"){600}

> [!Knowledge] You don't need to turn on Outlook, Teams or Word. Cowork has them built in.

## Step 1: Catch up

_Copilot Cowork, new task, Work IQ (Outlook and Teams)_

1. [] In the new task, enter:

    ++Catch me up on the Trey Research deal in five bullets: what Hemanti and Luc asked for, what we've decided, and what's still open.++

1. [] When the answer appears, select **items complete** above it to expand Cowork's steps. Check that Cowork got Hemanti's email from **Outlook** and read the chat in **Teams**.

    !IMAGE[Cowork's steps for the catch-up: searching for the Trey Research deal across email, Teams, files and calendar, searching people for Hemanti and Luc, getting Hemanti's email from Outlook and listing the Teams chat messages. Below, the answer starts with I based this on Hemanti's 12 Oct email and your 20 Oct Teams chat with her and Luc.](instructions360859/legal-cowork-catch-up.png "Cowork's steps for the catch-up"){600}

1. [] Check that the catch-up includes:

    - What's riding on it: a five-year, $14,750,000 deal for up to 4 million underwriting decisions a month, with the session on December 10.
    - Hemanti's ask: Zava must own the fine-tuned model weights. She calls it the #1 business priority.
    - Luc's ask: no more abrupt model retirements. The last vendor retired its model on two weeks' notice, and Zava couldn't quote for a week.
    - What's been decided: owning the model is a requirement before negotiating.
    - What's still open: your review of the draft against the playbook, and a prep call with Hemanti and Luc before December 10.
    - **Sources** under the answer, linking to Hemanti's email and the Teams chat.

    > [!Knowledge] Luc only asked if you can sign. Cowork pulled the backstory from an older email and a Teams chat, so you know what the business needs before you open the contract.

## Step 2: Flag the hard stops

_Same Cowork task, iManage_Lab, Word_

1. [] In the same task, enter:

    ++Which clauses in the Trey Research Vendor Agreement v4.2 in my OneDrive break the hard stops in our Zava AI Procurement Playbook in iManage? Add one short comment on each in the document, citing the playbook section.++

1. [] Check that **iManage_Lab** appears under **Plugins** in the **Workspace** panel on the right. Cowork is reading the playbook from iManage.
1. [] When the **Edit file?** card appears, select **Always allow: edits to this file**.

    > [!Alert] Choose Always allow: edits to this file. It covers this step and Step 3, so you won't be asked again for each edit. Changes are saved to the agreement in your OneDrive as they're made.

    !IMAGE[The Edit file card for Trey Research Vendor Agreement v4.2, with 8 proposed changes, Add comment 8, and the Cancel and Always allow: edits to this file buttons. iManage_Lab is listed under Plugins in the Workspace panel.](instructions360859/legal-cowork-edit-file.png "Always allow edits to this file"){600}

1. [] Check that the answer says Trey Research's draft breaks all six hard stops, and that each clause now has a short comment in the agreement, posted under your name.
1. [] Check the table of hard stops (Playbook §14) and the clauses that break them:

    - Zava solely owns outputs (§2.2): clauses 3.2 and 9.2.
    - No cap on liability for fraud, wilful misconduct, gross negligence or the IP indemnity (§5.3): clauses 16.2 and 16.3.
    - Trey Research fully liable for its subcontractors (§10.2): clause 14.2.
    - No mandatory arbitration (§12.3): clause 22.2, arbitration in Austin.
    - No class-action waiver (§12.4): clause 22.4.
    - Data returned in open formats (§11.2): clause 20.2.

    !IMAGE[Cowork's answer: Trey's draft breaks all six hard stops in the playbook, with a table of each hard stop, the Trey clause that breaks it and the problem.](instructions360859/legal-cowork-hard-stops.png "Six hard stops flagged"){600}

1. [] Below the table, find the serious gaps that aren't hard stops. They include §9.1 (Trey Research owns every fine-tuned model: Hemanti's concern) and §7.4 (15 days' notice of model changes with no Zava approval: Luc's concern). You'll fix both in Step 3.

    > [!Knowledge] The playbook never left iManage, and nothing was uploaded. Cowork read Zava's rules where they live and applied them to the contract in your OneDrive.

## Step 3: Fix the two must-haves

_Same Cowork task, iManage_Lab, Word_

1. [] In the same task, enter:

    ++Now redline that agreement so we own the fine-tuned model and get 60 days' notice and our approval before any model change or retirement. Use tracked changes, keep the edits minimal, with one short comment on each.++

    > [!Hint] This step can take a few minutes while Cowork reads the clauses and makes the edits.

1. [] Check that the answer lists the tracked changes, each with a short comment citing the playbook:

    - §9.1: Zava owns every model fine-tuned or retrained on its data, with its weights and parameters. Trey Research hands the weights over in a portable format, such as ONNX, and keeps its platform and base models.
    - §7.4: the notice period goes from 15 to 60 days, it covers any model change, and Trey Research can't make a change without Zava's prior written approval.
    - §7.2 and §7.3: "at any time" is deleted, so neither updates nor retirements can bypass §7.4.

1. [] In the answer, select the **Trey Research Vendor Agreement v4.2.docx** link. The agreement opens in Word next to the chat.
1. [] Scroll to **Section 7** and **Section 9**. Check that deleted text is struck through and new text is underlined, in red, and that comment markers appear in the right margin.

    !IMAGE[The agreement open in Word next to the Cowork chat, with tracked changes in red in Section 7.4 and Section 9.1 and comment markers in the right margin.](instructions360859/legal-cowork-redline.png "The redline in the agreement")

1. [] Select **X** in the top-right corner of the agreement to go back to the chat.

    > [!Knowledge] One business sentence, no section numbers. Cowork found the clauses itself and wrote in the positions. Hemanti's and Luc's must-haves are now contract language.

## Step 4: Build the negotiation pack

_Same Cowork task, iManage_Lab, Work IQ (Calendar)_

1. [] In the same task, enter:

    ++Get me ready for the December 10 session with Trey Research. Make a one-sheet negotiation list with just my redline, the hard-stop flags and the top gaps against what Colorado and New York insurance regulators expect against our playbook in iManage. Then send Luc and Hemanti a 30-minute prep invite for this week with a five-line summary as agenda.++

1. [] Check the **Steps** list in the **Workspace** panel: check the playbook and regulator expectations (Colorado, New York), build the one-sheet negotiation list, and send the prep invite.
1. [] When the **Create calendar event?** card appears, check it before you send it:

    - The date and time. To change them, select **Pick custom time**.
    - **Attendees:** Hemanti Baishya and Luc Lacombe.
    - A five-line agenda: your redline, change control, the six hard stops, the Colorado and New York gaps, and fallbacks and walk-away points.

    !IMAGE[The Create calendar event card: a 30-minute slot, the title Trey Research – Dec 10 negotiation prep, Hemanti Baishya and Luc Lacombe as attendees, a numbered agenda, and the Cancel and Send buttons. The negotiation list Word document is below the card.](instructions360859/legal-cowork-invite.png "Check the invite, then send it")

1. [] Select **Send**.

    > [!Alert] Nothing is sent until you select Send. Cowork asks before it sends anything on your behalf.

1. [] Under **Output** in the **Workspace** panel, select **Trey Research Negotiation List** to open it in Word next to the chat.
1. [] Check that the one-sheet has three sections:

    - **Our redline:** your two positions, each with the playbook section and a fallback.
    - **Hard stops:** the six clauses with Trey Research's text and the playbook section. No fallback: a refusal goes to the General Counsel.
    - **Top regulator gaps (Colorado Division of Insurance, New York DFS):** each gap in the draft, what regulators expect, and Zava's ask from the playbook, such as bias testing, model documentation, audit rights and regulator inquiries.

    !IMAGE[The Trey Research Negotiation List for December 10, 2026, open in Word next to the chat, with tables for the redline, the hard stops and the top regulator gaps.](instructions360859/legal-cowork-negotiation-sheet.png "The negotiation sheet")

1. [] In the regulator gaps, compare **What regulators expect** with **Our ask (Playbook)**.

    > [!Knowledge] Where the regulators expect more than the playbook asks, the playbook needs updating, not just the contract. Cowork put the regulations and the playbook side by side so you can see it.

## Step 5 (optional): File it in the matter

_Same Cowork task, iManage_Lab_

1. [] In the same task, enter:

    ++Save the negotiation sheet to the Drafts folder of the Trey Research matter in iManage.++

1. [] When the **iManage_Lab** approval card appears, approve it.
1. [] Open the link to the saved file to see the negotiation sheet in the matter's Drafts folder.

    > [!Knowledge] Cowork writes back to iManage too, so the work product lands in the matter alongside the playbook.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Step 1 doesn't find Hemanti's email or the Teams chat | Ask ++What did Hemanti send me about Trey Research?++ then rerun Step 1. |
| Cowork says it can't find the playbook | Select **Customize**, check that **iManage_Lab** is on, then rerun the step. |
| Cowork asks for permission to use iManage_Lab | Approve it. |
| Cowork can't find the agreement | Check that **Trey Research Vendor Agreement v4.2** is in the **Trey Research** folder of your OneDrive, then rerun the step. |
| You don't see the comments or tracked changes | Close the agreement and open it again from the link in Cowork's answer. |
| Cowork asks you to approve each edit in Step 3 | Select **Always allow: edits to this file** on the next **Edit file?** card. |

## Checkpoint

- [] Your catch-up came from Hemanti's email and the Teams chat.
- [] The agreement has comments on the hard stops and a redline for the two must-haves.
- [] Cowork produced a one-page negotiation sheet and a prep invite for Luc and Hemanti.
- [] (Optional) The negotiation sheet is in the matter's Drafts folder.

Cowork did the reading, the redlining and the drafting across email, Teams and iManage. You stayed the lawyer: every change has a reason, and nothing went out without your approval.

The same pattern works with other connectors. Try them in your own tenant for similar scenarios.

| Harvey |
|:---:|
| !IMAGE[Harvey logo](instructions360859/rebrand-connector-harvey.png "Harvey"){200} |

_Logos are trademarks of their respective owners._

> [!Note] Fictional parties adapted from the Harvey lab (MIT license). Not legal advice.

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Productivity: Prep a sales pitch

_About 10 minutes, plus a stretch step · SalesDesk_Lab, Teams, Outlook · Copilot Cowork_

You own the Lakeshore Retail account. Lakeshore Retail has piloted the Aurora smart-home hub in 50 stores for six weeks, ahead of the public launch event on December 8. Your next step is the expansion pitch to roll it out to all 400 stores.

- Atul Manohar, Lakeshore Retail's Director of Store Operations, emailed ahead of the pitch. Their CFO, Nanami Nakayama, is joining and wants the all-in cost for 400 stores. Lakeshore Retail IT (Jahidi Juma) wants Zava's security documentation first.
- On the Teams pilot review call, Atul said a competitor, Boulder Innovations, quoted about 20% under your list price.

You'll prep the call, handle the price objection and book the security review, without leaving Copilot.

!IMAGE[All steps run in one Copilot Cowork task. Step 1 gives a call brief. Step 2 gives a grounded answer from the Teams call and win and loss history. Step 3 creates an Outlook invite and a SalesDesk activity after you approve each. The stretch step logs the pilot review call.](instructions360859/rebrand-productivity-workflow.png "How the productivity track flows")

## Before you start

First, check that Atul's email is waiting for you in Outlook. Then you'll set up Cowork.

> [!Knowledge] SalesDesk is a customer relationship management (CRM) system that sales teams use to track accounts, contacts and deals. **SalesDesk_Lab** is the lab version of the SalesDesk connector.

### Read Atul's email in Outlook

1. [] Select **Microsoft Edge** on the taskbar, then go to +++https://outlook.cloud.microsoft/+++.
1. [] In the search box at the top, paste ++Aurora expansion pitch++ and press Enter.
1. [] Open the email from **Atul Manohar** titled _Aurora expansion pitch – Nanami joining, security docs_.
1. [] Check that it says Nanami, Lakeshore Retail's CFO, wants the all-in cost for 400 stores, and that Jahidi in IT wants Zava's security documentation first.

    !IMAGE[Outlook on the web with Aurora expansion pitch in the search box. Atul Manohar's email, Aurora expansion pitch – Nanami joining, security docs, is open, with the paragraphs about Nanami's all-in cost request and Jahidi's security documentation request highlighted.](instructions360859/productivity-outlook-atul-email.png "Atul's email in Outlook"){600}

> [!Knowledge] To see what Copilot will read, open the @[Lakeshore Retail account](`Start-Process "https://mock-salesdesk.yellowsand-9530f5dc.eastus.azurecontainerapps.io/lightning/r/Account/001Hp0000000001IAA/view"`){PowerShell} in SalesDesk_Lab.

### Set up Copilot Cowork

Cowork uses only the plugins you turn on, so first turn on SalesDesk_Lab.

1. [] Open a new browser tab and go to +++https://copilot.cloud.microsoft/+++.
1. [] Select **Cowork** at the top of the left pane.
1. [] In the left pane, select **Customize**.
1. [] Next to **Added**, select **Manage all**.

    !IMAGE[The Cowork Customize page, with Customize highlighted in the left pane and Manage all highlighted next to the Added list of connectors.](instructions360859/rebrand-cowork-customize.png "Open Customize, then Manage all"){600}

1. [] Turn on **SalesDesk_Lab**.
1. [] Turn off **Fabric IQ**, which is on by default. Leave every other plugin off.

    !IMAGE[The Added list in Cowork Customize, with SalesDesk_Lab turned on and Fabric IQ, Moodys_Lab, LSEG_Lab, FactSet_Lab, iManage_Lab, EngHub_Lab and GitHub_Lab turned off.](instructions360859/rebrand-productivity-cowork-customize.png "Turn on SalesDesk_Lab"){600}

1. [] In the left pane, select **New task**. Run every step in this one task, because your SalesDesk changes are kept only within it.

    !IMAGE[The Copilot left pane with the Cowork tab selected and New task highlighted below it.](instructions360859/copilot-new-cowork-task.png "Start a new Cowork task"){600}

> [!Knowledge] You don't need to turn on Outlook or Teams. Cowork has them built in.

## Step 1: Prep the call

_Copilot Cowork, SalesDesk_Lab call-prep skill, Outlook_

1. [] In the Cowork task, enter:

    ++Use SalesDesk to prep me for my Lakeshore Retail expansion pitch.++

1. [] Check that the brief includes:

    - The meeting: _Lakeshore Retail – Aurora expansion pitch_ on Friday, November 20.
    - The deal: the _Lakeshore Retail – Aurora 400-store rollout_ opportunity, Proposal/Price Quote, $1,200,000, closing December 31.
    - Who's in the room: Atul (champion), Jahidi (IT security) and Nanami (CFO). Nanami isn't a SalesDesk contact yet, so Copilot flags her as new.
    - What to cover: the price comparison, the security review and next steps.

    > [!Knowledge] The layout can vary between runs. The content is what matters. One prompt turned the CRM and your inbox into a brief that already points to the pitch's two risks.

## Step 2: Handle the price objection

_Same conversation, Teams meeting transcript, SalesDesk_Lab win and loss history_

1. [] In the same task, enter:

    ++Lakeshore Retail says Boulder Innovations is 20% cheaper. How should I handle that? Use what they said on the pilot review call and our win/loss history against Boulder Innovations.++

1. [] Check that the answer includes:

    - From the October 22 pilot review transcript: Boulder's $2,400 per store is the hub only, and lands around $3,250 per store all-in. Your counter-offer was 12% off ($2,640 per store against the $3,000 list) with install bundled.
    - The win: _Wide World Importers – Aurora 320-store rollout_, won against Boulder Innovations on all-in cost rather than sticker price.
    - The loss: _Tailspin Toys – Aurora 120-store rollout_, lost on price after leading with a discount.
    - The recommendation: don't match the 20%. Lead with the all-in cost for 400 stores, and offer 12% plus bundled install.

    > [!Knowledge] The numbers came from the Teams meeting, and the proof that the approach works came from SalesDesk.

## Step 3: Book the security review and log it

_Same conversation, SalesDesk_Lab schedule-meeting skill, Outlook calendar, write actions_

1. [] In the same task, enter:

    ++Send Jahidi and Atul a calendar invite for a 45-minute Aurora security review next week, and log it on the Lakeshore Retail opportunity.++

1. [] Review the two or three free slots Copilot proposes for next week.
1. [] At the first confirmation, check the invite preview and approve it. Copilot creates the Outlook invite.
1. [] At the second confirmation, check the SalesDesk activity preview and approve it. Copilot logs it on the opportunity.
1. [] Open the link to the SalesDesk record and check that the changes from your conversation appear.

    > [!Note] _Next week_ follows today's date, so the proposed slots depend on when you run the lab.

## Stretch: Log the pilot review call

1. [] In the same task, enter:

    ++Log the pilot review call on the Lakeshore Retail opportunity.++

1. [] Approve the confirmation, then open the opportunity's **Activity** tab to see the completed meeting task dated October 22.

> [!Hint] Prefer not to make changes? Try ++Draft an email to Atul and Nanami ahead of the pitch to confirm the agenda.++ It stays an Outlook draft.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Copilot asks which account or meeting | Reply ++The Lakeshore Retail expansion pitch.++ |
| The brief doesn't mention Nanami | Ask ++Who's on the call, and what does each of them care about?++ |
| Step 2 answers from general knowledge | Reply ++Use the Teams transcript of the Lakeshore Retail pilot review and our closed deals against Boulder Innovations in SalesDesk.++ |
| Slot picking runs long | Reply ++The first slot.++ |
| Copilot asks whether to email or invite | Reply ++Send the invite.++ |

## Checkpoint

- [] Your call brief covers the deal, all three attendees and the two risks.
- [] Copilot didn't match the 20% and proposed 12% plus bundled install, led by the all-in cost.
- [] The security review is on your calendar and logged on the Lakeshore Retail opportunity.

Copilot moved from finding information to finishing the job: a brief, a grounded answer, a booked meeting and an updated CRM, with you approving each change.

The same pattern works with other connectors. Try them in your own tenant for similar scenarios.

| Notion | Intercom | Zoom |
|:---:|:---:|:---:|
| !IMAGE[Notion logo](instructions360859/connector-notion.png "Notion"){200} | !IMAGE[Intercom logo](instructions360859/connector-intercom.png "Intercom"){200} | !IMAGE[Zoom logo](instructions360859/connector-zoom.png "Zoom"){200} |

_Logos are trademarks of their respective owners._

When you're done, go to [Bring your own app](#bring-your-own-app-zava-expense), or [choose another track](#choose-your-track).

===

# Engineering: Find what's blocking

_About 15 minutes · GitHub_Lab, EngHub_Lab, Teams · Copilot Chat, Copilot Cowork_

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

!IMAGE[Steps 1 and 2 in Copilot Chat find the at-risk item and what it's waiting on across EngHub, EngHub Docs and GitHub. Steps 3 and 4 in Copilot Cowork send Tama a Teams message and create a one-slide sprint update.](instructions360859/rebrand-engineering-workflow.png "How the engineering track flows")

## Before you start

First, check that Atul's email is waiting for you in Outlook.

> [!Knowledge] EngHub tracks the team's work items, EngHub Docs holds its design pages, and GitHub holds its code and pull requests. **GitHub_Lab** and **EngHub_Lab** are the lab versions of the GitHub and EngHub connectors. **EngHub_Lab** is EngHub's MCP server: one connector that reaches EngHub and EngHub Docs together.

### Read Atul's email in Outlook

1. [] Select **Microsoft Edge** on the taskbar, then go to +++https://outlook.cloud.microsoft/+++.
1. [] In the search box at the top, paste ++Aurora pilot - offline status still wrong++ and press Enter.
1. [] Open the email from **Atul Manohar** titled _Aurora pilot - offline status still wrong_, and scroll to his latest message.
1. [] Check that it says pilot stores still see Aurora hubs marked offline after they reconnect, and that staff keep restarting devices that are working.

    !IMAGE[Outlook on the web with Aurora pilot - offline status still wrong in the search box. Atul Manohar's email thread is open, with his latest message about hubs still marked offline highlighted.](instructions360859/engineering-outlook-atul-email.png "Atul's email in Outlook"){600}

> [!Knowledge] To see what Copilot will read, open the @[Aurora Sprint 24 board](`Start-Process "https://mock-enghub.yellowsand-9530f5dc.eastus.azurecontainerapps.io/"`){PowerShell}, the @[ADR-014 page](`Start-Process "https://mock-enghub.yellowsand-9530f5dc.eastus.azurecontainerapps.io/wiki/spaces/AUR/pages/98457"`){PowerShell} in EngHub Docs and the @[aurora-status pull requests](`Start-Process "https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/zava-lab/aurora-status/pulls"`){PowerShell} in GitHub.

## Step 1: Check how the sprint is going

_Copilot Chat, EngHub_Lab_

1. [] Open a new browser tab and go to +++https://copilot.cloud.microsoft/+++.
1. [] In Copilot, select **Chat** at the top of the left pane, then select **New chat**.

    !IMAGE[The Copilot left pane with the Chat tab selected and New chat highlighted below it.](instructions360859/copilot-new-chat.png "Start a new chat"){600}

1. [] Enter:

    ++What's the status of Aurora Sprint 24? Is anything at risk for the Lakeshore Retail pilot expansion?++

1. [] Check that you see a summary of the Sprint 24 items, with one at risk: AUR-142, _Aurora hubs remain offline after reconnect_, with citations to the EngHub items.

    > [!Knowledge] Most of the sprint is on track. Copilot picks out the one item that matters to your customer.

## Step 2: Find what AUR-142 is waiting on

_Same chat, EngHub_Lab, GitHub_Lab_

1. [] In the same chat, enter:

    ++What's the current status of AUR-142, and what is it waiting on? Check EngHub, EngHub Docs and GitHub.++

1. [] Check that the answer joins all three sources:

    - EngHub: AUR-142 is In Progress and at risk. Triin can't give a date until a design decision gets platform sign-off.
    - EngHub Docs: the pilot moves to the event-driven status service on November 20, and ADR-014 is still _Proposed_, with Tama Surya as the decision owner.
    - GitHub: PR #287 is open. It fixes only the old polling service, and Tama requested changes.
    - The answer: the fix is waiting on Tama's approval of ADR-014.

    > [!Knowledge] No single tool had the whole story. Joining them shows the work isn't stuck on code. It's waiting on one approval.

## Step 3: Ask Tama for the decision

_Copilot Cowork, Teams_

### Set up Copilot Cowork

Cowork uses only the plugins you turn on, so first turn on GitHub_Lab and EngHub_Lab.

1. [] In Copilot, select **Cowork** at the top of the left pane.
1. [] In the left pane, select **Customize**.
1. [] Next to **Added**, select **Manage all**.

    !IMAGE[The Cowork Customize page, with Customize highlighted in the left pane and Manage all highlighted next to the Added list of connectors.](instructions360859/rebrand-cowork-customize.png "Open Customize, then Manage all"){600}

1. [] Turn on **GitHub_Lab** and **EngHub_Lab**.
1. [] Turn off **Fabric IQ**, which is on by default. Leave every other plugin off.

    !IMAGE[The Added list in Cowork Customize, with EngHub_Lab and GitHub_Lab turned on and Fabric IQ, Moodys_Lab, SalesDesk_Lab, LSEG_Lab, FactSet_Lab and iManage_Lab turned off.](instructions360859/rebrand-engineering-cowork-customize.png "Turn on GitHub_Lab and EngHub_Lab"){600}

1. [] In the left pane, select **New task**. Cowork may not have your Chat conversation, so these prompts include the context they need.

    !IMAGE[The Copilot left pane with the Cowork tab selected and New task highlighted below it.](instructions360859/copilot-new-cowork-task.png "Start a new Cowork task"){600}

> [!Knowledge] You don't need to turn on Teams or PowerPoint. Cowork has them built in.

### Send the message

1. [] Enter:

    ++Send Tama Surya a Teams message. Ask Tama to approve ADR-014 so Triin can start the event-driven fix for AUR-142, and to re-review PR #287 once it's updated. Mention the November 20 cutover and include links to the ADR, the EngHub item and the PR.++

1. [] When Cowork shows the Teams message for confirmation, check the recipient and the message, then select **Send**.

## Step 4: Turn the sprint into a slide

_Same Cowork task, EngHub_Lab sprint-to-slides skill_

1. [] In the same task, type +++/sprint-to-slides+++ in the message box.
1. [] In the list that appears, select **/sprint-to-slides** (from EngHub_Lab) to apply the skill.

    !IMAGE[The Cowork message box with /sprint-to-slides typed, and the /sprint-to-slides skill from EngHub_Lab highlighted in the list below.](instructions360859/rebrand-engineering-cowork-skill-picker.png "Select the sprint-to-slides skill"){600}

1. [] Press Shift+Enter for a new line, then paste:

    ++Create one PowerPoint slide summarizing Aurora Sprint 24 for engineering leadership: what's on track, the one item at risk, what it's waiting on, and the next steps.++

1. [] Check that the slide shows the sprint goal and dates, AUR-142 at risk, the blocker (ADR-014 waiting on Tama), next steps with owners, and no invented delivery date.

    > [!Hint] **You chose the skill.** A skill is a set of expert instructions that comes with a connector. Here you named one with a slash command. EngHub's **sprint-to-slides** skill tells Cowork how a project manager reports on a sprint: read the sprint from EngHub, sort what's done, on track and at risk, find the blocker, and turn it into a slide.

    > [!Knowledge] A partner skill turned live EngHub and EngHub Docs data into a leadership-ready slide in one step.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Step 1 doesn't find the sprint | Ask ++Search EngHub for the Aurora Sprint 24 work items.++ |
| Step 2 misses EngHub Docs or GitHub | Ask ++Find ADR-014 in EngHub Docs++ or ++Search GitHub for a pull request that references AUR-142.++ |
| The skill returns an outline, not a slide | Reply ++Create the .pptx file with one slide.++ |
| Cowork sends without showing you the message | Tell a proctor. Messages should always ask for approval first. |

## Checkpoint

- [] You know which Sprint 24 item is at risk and why.
- [] You know the fix is waiting on Tama's approval of ADR-014.
- [] A Teams message to Tama is sent or ready for your approval.
- [] You have one sprint slide for leadership.

Copilot found the one item at risk, joined EngHub, EngHub Docs and GitHub to show what it was waiting on, then Cowork asked for the decision and gave leadership a one-slide update.

The same pattern works with other connectors. Try them in your own tenant for similar scenarios.

| Atlassian | Azure DevOps | Linear | Webflow |
|:---:|:---:|:---:|:---:|
| !IMAGE[Atlassian logo](instructions360859/rebrand-connector-atlassian.png "Atlassian"){200} | !IMAGE[Azure DevOps logo](instructions360859/connector-azure-devops.png "Azure DevOps"){200} | !IMAGE[Linear logo](instructions360859/connector-linear.png "Linear"){200} | !IMAGE[Webflow logo](instructions360859/connector-webflow.png "Webflow"){200} |

_Logos are trademarks of their respective owners._

> [!Hint] In this track, you called a skill by name with a slash command. Copilot can also pick a skill for you based on what you ask. To see that, try the [finance track](#finance-should-we-buy-more-litware).

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
    | Display name | ++Zava Expense - <your name>++ _(keep it under 30 characters)_ |
    | Description | ++Zava's in-house expense app. Use it to see the signed-in employee's expense reports and why any were rejected or returned, find corporate card charges for a trip, create a report from receipts, check it against the Zava travel policy, submit it for manager approval, and compare travel spend with budget.++ |
    | MCP Endpoint URL | ++https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp++ |
    | Developer name | ++Zava++ |
    | Website URL | ++https://zava-online.com++ |
    | Privacy URL | ++https://zava-online.com/privacy++ |
    | Terms of use URL | ++https://zava-online.com/terms++ |
    | Authentication type | None |

    > [!Knowledge] Copilot reads the description to decide when to use Zava Expense and what to ask it. A good description says, in plain words, what data the app holds and what it can do.

    > [!Note] This lab uses _None_ so you can connect quickly. In your own tenant, choose the authentication your app needs, such as Microsoft Entra SSO or OAuth 2.0.

1. [] Select the **Notice** checkbox, then select **Create**.

    !IMAGE[The bottom of the Connect to MCP server form, with Authentication type set to None, the Notice checkbox selected and the Create button highlighted.](instructions360859/byoa-connector-notice-create.png "Select Notice, then Create"){600}

1. [] Wait about a minute while the connection is set up. When you see **Success**, select **Done**.

    !IMAGE[The Success page, showing Created connection for Zava Expense and Linking data source with Your data source is linked and ready to use, and the Done button highlighted.](instructions360859/byoa-connector-done.png "Select Done"){600}

1. [] Select the **Your connections** tab, then select the connection you just created: **Zava Expense - @lab.User.FirstName**.
1. [] In the details pane on the right, scroll down to **Enable/disable this source for users**. Check that **Allow information from this connection to appear in Copilot** is turned **On**. If it isn't, turn it on and select **Save**.

    > [!Note] The setting can take a few seconds to appear. Wait for it before you check.

    !IMAGE[The Your connections tab in the Microsoft 365 admin center, with a Zava Expense connection selected and its details pane open. Under Enable/disable this source for users, Allow information from this connection to appear in Copilot is turned On.](instructions360859/byoa-connector-enabled.png "Check the connection is on"){600}

## File your Seattle trip

Run Steps 1 to 4 in one new chat. Each new chat starts from the original data.

### Turn on Zava Expense in Copilot

1. [] Leave the Microsoft 365 admin center. Open a new browser tab and go to Copilot at +++https://copilot.cloud.microsoft/+++.
1. [] In Copilot, select the three dots (**...**) in the top-right corner, then select **Settings**.
1. [] In **Settings**, select **Sources**. In the search box, type +++zava+++, then select **Connect** next to **Zava Expense - @lab.User.FirstName**.
1. [] In the **Connect to Zava Expense** window, select **Continue to Zava Expense**. Once connected, close **Settings**.

    !IMAGE[Copilot Settings with Sources open and zava in the search box. The Connect to Zava Expense window is open, with the Continue to Zava Expense button highlighted.](instructions360859/byoa-copilot-connect-zava.png "Continue to Zava Expense"){600}

### Step 1: Check where you stand

1. [] In Copilot, select **Chat** at the top of the left pane, then select **New chat**.

    !IMAGE[The Copilot left pane with the Chat tab selected and New chat highlighted below it.](instructions360859/copilot-new-chat.png "Start a new chat"){600}

1. [] Enter:

    ++Using Zava Expense, show me my open expense reports. Were any of them rejected or sent back, and why?++

1. [] Check that you see four open reports:

    - ER-1044 (Dallas) was rejected: the $142.60 Pappas Bros receipt is missing.
    - ER-1046 was returned: it has no business purpose.
    - ER-1045 (Austin, $631.50) and ER-1051 (October local expenses, $953.09) are pending approval.

### Step 2: File the trip

1. [] In the same chat, enter:

    ++Find the receipts from my Seattle trip in my inbox and use them to create a Zava Expense report for the Fabrikam, Inc. partnership review. Check the report against our travel policy, but don't submit it yet.++

1. [] When Copilot asks you to confirm creating the expense report in Zava Expense, check the details and approve it.
1. [] Check that Copilot creates draft report ER-2001 with six items totalling $2,052.65 and flags:

    - Blocking: the Westin charged $389 for the night of October 28, which is $139 over the $250 Seattle cap.
    - Warning: the $52.30 Uber ride was charged twice (TX-10111). Copilot suggests asking Ebere Ibeabuchi in Finance Operations to reverse it.

### Step 3: Fix and submit

This step submits the report, so Copilot asks for your approval first.

1. [] In the same chat, enter:

    ++Add a justification for the $389 Westin night: a city-wide convention pushed up hotel rates, and no hotel near the Fabrikam, Inc. office was under the cap. Then submit the report to my manager.++

1. [] Check that Copilot reruns the policy check with no blocking issues and one justified exception.
1. [] When the approval card appears, approve it.
1. [] Check that Copilot confirms ER-2001 ($2,052.65) was submitted to Hannes Niemi.
1. [] Check the status: ++Has my Seattle report gone through? Who's approving it?++

### Step 4: Review your spend

1. [] In the same chat, enter:

    ++How am I doing against my Q4 travel budget? Put it in an Excel workbook with a chart.++

1. [] Check that you've spent $4,309.55 of $6,800 (63%), you're over budget on meals and entertainment (106%) and ground transport (111%), and Copilot creates an Excel workbook with a chart.

## If it goes wrong

| What happens | Try this |
|:---|:---|
| Zava Expense doesn't appear in Sources | Check that staged rollout includes you, wait a few minutes, then refresh Copilot. |
| Copilot doesn't use Zava Expense | Start the prompt with _Using Zava Expense_. |
| Copilot says Zava Expense isn't responding | Wait 15 seconds, then send the same prompt again in the same chat. |
| Step 2 misses some receipts | Ask ++Find all my Seattle receipts from October in my inbox.++ |

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
| Legal | Comments and a redline in the contract, a negotiation sheet and a prep invite, all in Cowork, from Work IQ and iManage |
| Productivity | A call brief, a grounded answer to a price objection, and a booked and logged meeting, from SalesDesk, Teams and Outlook |
| Engineering | The sprint's one at-risk item and what it's waiting on, a Teams message and a sprint slide, from EngHub, EngHub Docs and GitHub |
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
