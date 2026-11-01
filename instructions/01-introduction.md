# Introduction

> **Duration:** ~5 minutes (reading) | **Next:** [Getting started with connectors](02-getting-started.md)

## Welcome

AI is only as useful as the knowledge it can reach. At most companies that knowledge is spread across many systems: CRM, ticketing, code, wikis, document management, meeting recordings and paid data feeds. Copilot connectors bring that knowledge into Microsoft 365 Copilot, so answers are grounded in the information your organization actually uses.

Microsoft 365 Copilot offers a single catalog of more than 300 connectors. Connect a source once, and it's available across the Copilot experiences that support it: Copilot Chat, Copilot Cowork, Word, Excel and PowerPoint.

In this lab you'll go beyond finding information. You'll use connectors, connector skills and write actions to complete real workflows end to end, and you'll approve every change before it happens.

## What you'll learn

By the end of this lab, you'll be able to:

1. **Discover and connect** the right connectors from the catalog, and use connected data wherever it's supported in Microsoft 365.
2. **Ground Copilot** in trusted business and partner data, with citations back to each source.
3. **Finish the work, not just the search:** use skills and write actions to produce a call brief, a sprint decision slide, a committee pack or a contract redline, and bring your own app with a custom connector.

## Your role: Marcus Hollowell at Verdantis

**Verdantis** is a fictional US insurer that also builds **Aurora**, a smart-home hub sold through retail partners such as Contoso Retail. You'll play **Marcus Hollowell**, who uses Copilot to handle very different requests. Each request is a track.

## How the lab runs

1. Everyone completes [Getting started with connectors](02-getting-started.md).
2. **Pick one track.** If you finish early, try another on your own.
3. Everyone does [Bring your own app](07-custom-mcp.md): connect an in-house app to Copilot with no code.
4. Close with the [Summary](08-summary.md).

## The tracks

| Track | The ask | Connectors and tools | Time |
|---|---|---|---|
| [Finance](03-finance.md) | Jordan, who runs the Verdantis investment portfolio: "Should we buy more NVIDIA? Bring a recommendation to Monday's investment committee." | LSEG, FactSet, Moody's · equity research and company analysis skills · Excel, Word | ~18 min |
| [Legal](04-legal.md) | Tomás, Chief Underwriting Officer: "Can we sign Cognivault's AI underwriting contract on the 12th?" | Work IQ (email and Teams), iManage · Word legal skills · Copilot Cowork | ~15 min |
| [Productivity](05-productivity.md) | Pitch the Aurora rollout to all 400 Contoso Retail stores on Nov 20, with a CFO in the room and a competitor 20% cheaper. | Test_Salesforce, Test_Confluence, Teams, Outlook · sales skills · Copilot Cowork | ~10 min (+ stretch) |
| [Engineering](06-engineering.md) | A customer says the Aurora offline-status bug is still there, and the pilot expands on Monday. What's really happening? | Test_Jira, Test_GitHub, Outlook, Teams · sprint-to-slides skill · Copilot Cowork | ~15 min |
| [Bring your own app](07-custom-mcp.md) (everyone) | Your expense tool isn't in any catalog. Connect it yourself, then file a trip from your inbox. | Verdantis Expense (custom MCP connector) · travel-policy skill · Excel | ~20 min |

## Key ideas

### Connectors

Some connectors index content into Microsoft 365 ahead of time; others call the source live, signed in as you. You don't need to know which is which. Copilot picks the right source for your question, respects what you're allowed to see, and cites where each answer came from.

### Skills, plugins and write actions

- **Connector skills** package a partner's expertise, such as how sales teams prep a call or how analysts assess credit. Copilot loads a skill when your request needs it, so you get the partner's method as well as their data.
- **Plugins** bundle a connector and its skills into one package that an admin deploys once. After that, they work across the Copilot experiences that support them.
- **Write actions** let Copilot change things in the source system, such as logging a meeting on a Salesforce opportunity or saving a draft to a document matter. You see a confirmation first, and nothing changes until you approve it.

> [!NOTE]
> This lab runs in a demo tenant with fictional people and companies. Financial and legal outputs are for the exercise only. They aren't investment or legal advice.

---

**Next:** [Getting started with connectors](02-getting-started.md)
