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

## Your role: Emil Vanggaard at Zava

**Zava** is a fictional US insurer that also builds **Aurora**, a smart-home hub sold through retail partners such as Lakeshore Retail. You'll play **Emil Vanggaard**, who uses Copilot to handle very different requests. Each request is a track.

## How the lab runs

1. Everyone completes [Getting started with connectors](02-getting-started.md).
2. **Pick one track.** If you finish early, try another on your own.
3. Everyone does [Bring your own app](07-custom-mcp.md): connect an in-house app to Copilot with no code.
4. Close with the [Summary](08-summary.md).

## The tracks

| Track | The ask | Connectors and tools | Time |
|---|---|---|---|
| [Finance](03-finance.md) | Kristian, who runs the Zava investment portfolio: "Should we buy more Litware? Bring a recommendation to Monday's investment committee." | LSEG, FactSet, Moody's · equity research and company analysis skills · Excel, Word | ~18 min |
| [Legal](04-legal.md) | Luc, Chief Underwriting Officer: "Can we sign Trey Research's AI underwriting contract on the 10th?" | Work IQ (email and Teams), iManage · Copilot Cowork | ~20 min |
| [Productivity](05-productivity.md) | Pitch the Aurora rollout to all 400 Lakeshore Retail stores on Nov 20, with a CFO in the room and a competitor 20% cheaper. | Salesforce_Lab, Teams, Outlook · sales skills · Copilot Cowork | ~10 min (+ stretch) |
| [Engineering](06-engineering.md) | One Sprint 24 item is at risk, and the customer's pilot expands on Monday. Who is it waiting on? | Jira, Confluence, GitHub_Lab, Rovo_Lab, Teams · sprint-to-slides skill · Copilot Cowork | ~15 min |
| [Bring your own app](07-custom-mcp.md) (everyone) | Your expense tool isn't in any catalog. Connect it yourself, then file a trip from your inbox. | Zava Expense (custom MCP connector) · travel-policy skill · Excel | ~20 min |

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
