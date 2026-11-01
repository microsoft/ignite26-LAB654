# Getting started with connectors

> **Duration:** ~10 minutes | **Previous:** [Introduction](01-introduction.md) | **Next:** pick a track

## Objective

Sign in as Marcus, discover connectors in the catalog, check the ones for your track are ready, and ask your first grounded question.

## Step 1: Sign in

1. Sign in to the lab computer with the credentials on your **seat card**.
2. Open the **Microsoft 365 Copilot** app and sign in with the Marcus Hollowell account from your seat card.

> [!TIP]
> If a sign-in popup is blocked at any point in the lab, allow popups for the Copilot site and try again.

## Step 2: Discover connectors

1. In Copilot, open **Settings** › **Sources**.
2. Browse the catalog. Microsoft 365 Copilot offers more than 300 connectors, from CRM and ticketing to code, wikis and market data.
3. Find the connectors for the track you'll take:

    | Track | Connectors |
    |---|---|
    | Finance | Test_LSEG · Test_FactSet · Test_Moodys |
    | Legal | Test_iManage |
    | Productivity | Test_Salesforce · Test_Confluence |
    | Engineering | Test_Jira · Test_GitHub |
    | Bring your own app (everyone) | Verdantis Expense: you'll add this one yourself in [module 7](07-custom-mcp.md) |

    Outlook, Teams and your Microsoft 365 files are available in every track.

> [!NOTE]
> Connectors named `Test_…` are mock versions of the real connectors, built for this lab. They behave like the real ones and come with the same skills, but they serve sample data for the fictional Verdantis company. You don't need any third-party account to use them. Changes you make with them are visible only in the conversation where you make them.

## Step 3: Check your sources are ready

1. Confirm the connectors for your track show as **Connected**.
2. If one shows **Connect** instead, select it and follow the prompts. If it still doesn't connect, ask a proctor.

In a real organization, an admin deploys connectors like these once, and people sign in to them with their own accounts. In this lab, that setup has been done for you.

## Step 4: Ask your first grounded question

Start a new chat and try a question for your track:

```text
Using LSEG, what was NVIDIA's earnings per share last quarter compared with the analyst consensus?
```

```text
What did Radhika send me about Cognivault?
```

```text
What's the stage and amount of the Contoso Retail opportunity in Salesforce?
```

```text
What's the status of Jira issue AUR-142?
```

**What to look for:**

- The answer cites its source: the connector name, a record, a page or a link.
- Copilot only uses data that Marcus is allowed to see.

> [!TIP]
> **Connect once, use everywhere.** These connectors also work in the Copilot experiences in Word, Excel, PowerPoint and Copilot Cowork that support them. You'll see this in the tracks: you don't need to set anything up again.

## Checkpoint

- [ ] You're signed in as Marcus.
- [ ] The connectors for your track show as connected.
- [ ] Your first question came back with a cited source.

---

**Pick a track:** [Finance](03-finance.md) · [Legal](04-legal.md) · [Productivity](05-productivity.md) · [Engineering](06-engineering.md)
