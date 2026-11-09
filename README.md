## Before you're done

This repo has been created for your Microsoft Ignite 2026 session. Here's how to get it ready.

**Easiest path — use the agent (recommended):**

- Open GitHub Copilot Chat and say `help me initialize repo`. The agent will walk you through getting the README populated.
- When you're ready to publish, say `help me finalize repo`. The agent will clean up unused folders, validate everything, and remove this "Before you're done" section and other extra stuff that attendees don't need to see.
- Curious how it works? Read the [agent workflow](.github/AGENT-WORKFLOW.md).

**Doing it manually?**

Fill in the sections below yourself, then:

- Delete any placeholder folders you don't need (`data/`, `infra/`, etc.)
- Delete this "Before you're done" section
- Delete `.github/agents/`, `.github/tests/`, `.github/copilot-instructions.md`, and `.github/AGENT-WORKFLOW.md` — these are template tooling, not part of your published repo

**Folder conventions:**

- Attendee step-by-step guidance goes in `instructions/`. If you use MkDocs or a docs site instead, put it in `docs/` and link to it from this README.
- Reference material and background reading go in `docs/`.
- You can add a `.devcontainer/` folder if needed.

---

<a name="start-building"></a>

<p align="center">
<img src="img/banner-ignite-26.png" alt="Microsoft Ignite 2026" width="100%"/>
</p>

# [Microsoft Ignite 2026](https://ignite.microsoft.com)

## 🔥LAB654: Copilot Connectors: Connect once. Use enterprise knowledge everywhere.
### Session description

AI is only as powerful as the knowledge it can access. Copilot Connectors securely bring your enterprise data into Copilot, grounding experiences in the information that matters most to your organization. In this hands-on lab, you’ll discover and acquire connectors, connect trusted data sources, and use interactive experiences, skills, and actions to make informed decisions and complete real-world workflows. Explore these end-to-end scenarios across finance, legal, engineering, and productivity

### 🚀 Getting started

The lab runs in a demo tenant where you play **Emil Vanggaard** at **Zava**, a fictional insurer. Everyone completes the introduction and getting started modules, picks one track (finance, legal, productivity or engineering), then connects an in-house expense app to Copilot through a custom MCP server.

#### In a guided session

If you're following along during a live session:

1. Sign in to the lab computer with the credentials on your **seat card**.
2. In the browser, go to **Microsoft 365 Copilot** at [m365.cloud.microsoft](https://m365.cloud.microsoft) and sign in with the Emil Vanggaard account from your seat card.
3. Open the [lab manual](instructions/README.md) beside Copilot and start with the [Introduction](instructions/01-introduction.md).

#### On your own

If you're learning at your own pace:

1. Read the [lab manual](instructions/README.md) to see how each track uses connectors, skills and write actions.
2. Use a Microsoft 365 tenant with Microsoft 365 Copilot. To add a custom MCP connector, you also need access to the Microsoft 365 admin center.
3. Follow the tracks with the connectors your organization uses. The `…_Lab` connectors and the Zava sample data are mock versions built for the live lab, so adapt the prompts to your own sources.

### 🎯 Learning outcomes

By the end of this session, you will be able to:

- Discover and connect the right connectors from the catalog, and use connected data wherever it's supported in Microsoft 365.
- Ground Copilot in trusted business and partner data, with citations back to each source.
- Finish real workflows with connector skills and write actions, and bring your own app to Copilot with a custom MCP connector.

### 💻 Technologies used

- Microsoft 365 Copilot (Copilot Chat and Copilot Cowork)
- Copilot connectors, connector skills and write actions
- Model Context Protocol (MCP) custom connectors in the Microsoft 365 admin center
- Word, Excel, PowerPoint, Outlook and Teams
- Partner connectors: LSEG, FactSet, Moody's, iManage, Salesforce, Jira, Confluence, GitHub and Atlassian Rovo

### 📚 Continue your learning

Pick your next step based on your learning style:

| Resource | What you'll get |
|----------|-----------------|
| **[Ignite 2026 Next Steps](https://aka.ms/ignite26-next-steps)** | Additional session repos and materials from Microsoft Ignite 2026 |
| **[Microsoft AI Skills Navigator](https://aka.ms/ignite26-asn)** | Discover AI skills, learning paths, and resources for your next step |
| **[Microsoft Learn](https://aka.ms/ignite26-learn)** | Official documentation and guided learning paths on these topics |
| **[Microsoft Foundry Community](https://aka.ms/MicrosoftFoundryDiscord-Ignite26)** | Connect with other learners and experts in our Discord community |

### 🌟 Microsoft Learn MCP Server

<!-- Remove this section if the Microsoft Learn MCP Server is not relevant to the session. -->

The Microsoft Learn MCP Server gives your AI agent direct access to Microsoft's official documentation — grounded, up-to-date answers about the topics in this session.

**GitHub Copilot CLI** — Install with:

```shell
copilot plugin install microsoftdocs/mcp
```

**VS Code** — One-click install:  
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Microsoft_Learn_MCP-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=microsoft-learn&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Flearn.microsoft.com%2Fapi%2Fmcp%22%7D)

For more information, visit the [Learn MCP Server repo](https://aka.ms/learnmcp).

### 👥 Content owners

<!-- TODO: Replace the placeholder GitHub links and images for Gargy Shekhar, Shiladitya Saha and Krishan Nagpal. -->

<table>
<tr>
    <td align="center"><a href="https://github.com/tezansahu">
        <img src="https://www.tezansahu.com/assets/images/tezan-profile.png" width="100px;" alt="Tezan Sahu"/><br />
        <sub><b>Tezan Sahu</b></sub></a><br />
            <a href="https://github.com/tezansahu" title="talk">📢</a>
    </td>
    <td align="center"><a href="https://github.com/dannyyaou">
        <img src="https://github.com/dannyyaou.png" width="100px;" alt="Danny Yao"/><br />
        <sub><b>Danny Yao</b></sub></a><br />
            <a href="https://github.com/dannyyaou" title="talk">📢</a>
    </td>
    <td align="center"><a href="https://github.com/yourGitHubHandle">
        <img src="https://github.com/yourGitHubHandle.png" width="100px;" alt="Gargy Shekhar"/><br />
        <sub><b>Gargy Shekhar</b></sub></a><br />
            <a href="https://github.com/yourGitHubHandle" title="talk">📢</a>
    </td>
</tr>
<tr>
    <td align="center"><a href="https://github.com/anparanjape">
        <img src="https://github.com/anparanjape.png" width="100px;" alt="Anshuman Paranjape"/><br />
        <sub><b>Anshuman Paranjape</b></sub></a><br />
            <a href="https://github.com/anparanjape" title="talk">📢</a>
    </td>
    <td align="center"><a href="https://github.com/yourGitHubHandle">
        <img src="https://github.com/yourGitHubHandle.png" width="100px;" alt="Shiladitya Saha"/><br />
        <sub><b>Shiladitya Saha</b></sub></a><br />
            <a href="https://github.com/yourGitHubHandle" title="talk">📢</a>
    </td>
    <td align="center"><a href="https://github.com/yourGitHubHandle">
        <img src="https://github.com/yourGitHubHandle.png" width="100px;" alt="Krishan Nagpal"/><br />
        <sub><b>Krishan Nagpal</b></sub></a><br />
            <a href="https://github.com/yourGitHubHandle" title="talk">📢</a>
    </td>
</tr></table>

### ⚖️ Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.

Any use of third-party trademarks or logos are subject to those third-party's policies.
