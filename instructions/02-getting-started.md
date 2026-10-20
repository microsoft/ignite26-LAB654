# Getting started with connectors

> **Duration:** ~10 minutes | **Previous:** [Introduction](01-introduction.md) | **Next:** pick a track

## Objective

Sign in as Marcus, find the connectors this lab uses, check they're ready, and ask your first grounded question.

## Step 1: Sign in

1. Sign in to the lab computer with the credentials on your **seat card**.
2. Open the **Microsoft 365 Copilot** app and sign in with the Marcus Hollowell account from your seat card.

> [!TIP]
> If a sign-in popup is blocked at any point in the lab, allow popups for the Copilot site and try again.

## Step 2: Discover connectors

1. In Copilot Chat, open **Settings** › **Sources**.
2. Browse the connectors available to you. Microsoft 365 Copilot offers hundreds of synced and federated connectors.
3. Find the connectors used in this lab:

    | Connector | Track | Model | Setup |
    |---|---|---|---|
    | Test_LSEG | Finance | Federated | Pre-configured for the lab |
    | Test_FactSet | Finance | Federated | Pre-configured for the lab |
    | Test_Moodys | Finance | Federated | Pre-configured for the lab |
    | Test_iManage | Legal | Federated | Pre-configured for the lab |
    | Test_Notion | Productivity | Federated | Pre-configured for the lab |
    | Verdantis Hub (Test_Intranet) | Productivity | Synced | Pre-configured for the lab |

> [!NOTE]
> Connectors named `Test_…` are mock versions of the real connectors, built for this lab. They behave like the real ones and come with the same skills, but they serve sample data for the fictional Verdantis company. You don't need any third-party account to use them.

## Step 3: Check your sources are ready

1. Confirm the connectors for your two chosen tracks show as **Connected**.
2. If one shows **Connect** instead, select it and follow the prompts. If it still doesn't connect, ask a proctor.

In a real organization, an admin deploys connectors like these once, and you sign in to the federated ones with your own account. In this lab, that setup has been done for you.

## Step 4: Ask your first grounded question

Start a new chat and try a question that needs a connector. Pick one from your first track:

```text
Using LSEG, what was NVIDIA's earnings per share last quarter compared with the analyst consensus?
```

```text
What did Radhika send me about Cognivault?
```

```text
Find the Retail Partner Launch Playbook on Verdantis Hub and summarize the rules for POS kit shipments.
```

**What to look for:**

- The answer cites its source: the connector name, a document or page title, or a link.
- Copilot only uses data that Marcus is allowed to see.

> [!TIP]
> **Connect once, use everywhere.** These connectors also work in the Copilot experiences in Excel, Word and Copilot Cowork that support them. You'll see this in the tracks: you don't need to set anything up again.

## Checkpoint

- [ ] You're signed in as Marcus.
- [ ] The connectors for your two tracks show as connected.
- [ ] Your first question came back with a cited source.

---

**Pick a track:** [Finance](03-finance.md) · [Legal](04-legal.md) · [Productivity](05-productivity.md)
