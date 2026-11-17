# Skillable lab instructions

This folder holds the version of the lab manual that runs in the Skillable lab environment, in the instructions pane beside the virtual machine.

- [`lab-instructions.md`](lab-instructions.md): every page in one file, with `===` between pages. Paste it into the Skillable instructions editor.
- [`images/`](images/): the images the instructions use. They include the five workflow diagrams, the Contoso Authenticator App screenshots and the app icon.

The GitHub version of the manual, in the [`instructions/`](../../../instructions/README.md) folder, is the source of truth for the lab content. When you change it, update this file to match.

## Set up the instructions in Skillable

1. Open the lab profile and select **Edit Instructions**.
2. Upload every image in [`images/`](images/) with the editor's image upload. Keep the file names. The instructions expect each image at `instructions360859/<file name>`.
3. If Skillable gives the images a different folder, replace `instructions360859/` in `lab-instructions.md` with that folder.
4. Uploading inserts image tags into the editor. Select everything in the editor and replace it with the contents of `lab-instructions.md`.
5. Preview every page, then run the lab end to end in a lab instance.

## What the file uses

| Feature | Syntax | Why |
|---|---|---|
| Page break | `===` | One page per part of the lab. Each page starts with a `#` heading, which labels the **Next** button. |
| Type text | `+++text+++` | Types prompts, URLs and form values into the virtual machine with one click. |
| Command link | ``@[text](`Start-Process "url"`){PowerShell}`` | Opens mock data pages in the virtual machine's browser, and runs the reset script (`{Shell visible}`). Plain links open on the attendee's own computer. Needs Integration Services on the virtual machine. |
| Task checkbox | `1. []` and `- []` | Tracks attendee progress. |
| Blocks | `> [!Alert]`, `> [!Note]`, `> [!Hint]`, `> [!Knowledge]`, `> [+Help]` | Replace the GitHub `[!IMPORTANT]`, `[!NOTE]` and `[!TIP]` callouts. |
| Lab tokens | `@lab.Title`, `@lab.CloudCredential(Ignite-LAB654).Username`, `@lab.CloudCredential(Ignite-LAB654).Password`, `@lab.VirtualMachine(...)` | Show the lab title and the seat's username and TAP. The reset link passes the same username token to the reset script. |

## Reset script

The **Prepare a clean environment** page runs `C:\LabFiles\reset-lab.bat` on the VM. The scripts and their VM and tenant setup are in [`infra/skillable/`](../README.md).

## Reference

- [Creating instructions with Markdown syntax](https://docs.skillable.com/docs/creating-instructions-with-markdown-syntax)
- [Instructions writing best practices](https://docs.skillable.com/docs/instructions-writing-best-practices)
- [Accessibility best practices](https://docs.skillable.com/docs/accessibility-best-practices)
