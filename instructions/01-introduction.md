# Introduction

> **Duration:** ~5 minutes (reading) | **Next:** [Getting started with connectors](02-getting-started.md)

## Welcome

AI is only as useful as the knowledge it can reach. At most companies that knowledge is spread across many systems: trackers, wikis, the intranet, document management systems, research services and paid data feeds. Copilot connectors bring that knowledge into Microsoft 365 Copilot so answers are grounded in the information your organization actually uses.

In this lab you'll go beyond finding information. You'll use connectors, connector skills and write actions to complete real workflows end to end, and you'll approve every change before it happens.

## What you'll learn

By the end of this lab, you'll be able to:

1. **Discover and connect** the right connectors, and use connected data wherever it's supported in Microsoft 365.
2. **Ground Copilot** in trusted enterprise and partner data, with citations back to each source.
3. **Use skills and write actions** to turn connected data into finished work: a committee pack, a contract redline, an updated project plan.

## Your role: Marcus Hollowell at Verdantis

**Verdantis** is a fictional US car and home insurer based in Stamford, Connecticut. You'll play **Marcus Hollowell**, who uses Copilot to handle three very different requests on the same day. Each request is a track.

## The three tracks

| Track | The ask | Connectors and tools | Time |
|---|---|---|---|
| [Finance](03-finance.md) | Jordan, who runs the Verdantis investment portfolio: "Should we buy more NVIDIA? Bring a recommendation to Monday's investment committee." | LSEG, FactSet, Moody's · equity research and company analysis skills · Excel, Word | ~18 min |
| [Legal](04-legal.md) | Tomás, Chief Underwriting Officer: "Can we sign Cognivault's $14.75M AI underwriting contract on the 15th?" | Work IQ (email and Teams), Harvey, Test_iManage · Word Legal Agent · Copilot Cowork | ~15 min |
| [Productivity](05-productivity.md) | A print vendor just slipped, putting the Aurora smart-home hub's retail launch at risk. Fix the plan before standup. | Test_Notion, Verdantis Hub (Test_Intranet) · Email and Scheduling skills · Copilot Cowork | ~10 min (+3 stretch) |

Everyone completes [Getting started with connectors](02-getting-started.md) first. Then **pick two tracks**. If you finish early, try the third on your own.

## Key ideas

### Two ways a connector brings data to Copilot

| Model | How it works | Example in this lab |
|---|---|---|
| **Synced** | An admin indexes the content once into Microsoft Graph, so everyone's Copilot can search it. Read-only. | Verdantis Hub (Test_Intranet) |
| **Federated** | Copilot calls the source live through an MCP server, signed in as you. Can read and write. | Test_Notion, Test_iManage, Test_LSEG, Test_FactSet, Test_Moodys |

### Skills, plugins and write actions

- **Connector skills** package a partner's expertise, such as an analyst playbook. Copilot loads a skill when your request needs it, so you get the partner's method as well as their data.
- **Plugins** bundle a connector and its skills into one package that an admin deploys once. After that, the connector and skills work across the Copilot experiences that support them.
- **Write actions** let Copilot change things in the source system, such as updating a Notion tracker row or adding a decision log entry. You see a confirmation card first, and nothing changes until you approve it.

> [!NOTE]
> This lab runs in a demo tenant with fictional people and companies. Financial and legal outputs are for the exercise only. They aren't investment or legal advice.

---

**Next:** [Getting started with connectors](02-getting-started.md)
