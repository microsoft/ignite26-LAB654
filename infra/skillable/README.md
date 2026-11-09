# Skillable lab reset

Scripts that reset a lab seat's Microsoft 365 account, so every attendee starts from the original files. Attendees run them from the **Prepare a clean environment** page of the Skillable instructions.

| File | Purpose |
|---|---|
| [`reset-lab.bat`](reset-lab.bat) | What the attendee runs. Starts `reset-lab.ps1`. Pass the seat's sign-in name as the first argument. |
| [`reset-lab.ps1`](reset-lab.ps1) | Does the reset through Microsoft Graph. |
| [`Trey Research Vendor Agreement v4.2.docx`](Trey%20Research%20Vendor%20Agreement%20v4.2.docx) | Clean copy of the agreement, used if the download from the gist fails. |

## What the reset does

1. Signs in through the browser. If Edge is already signed in as the seat's account, no password or MFA prompt appears.
2. Stops if the signed-in account isn't the one passed to the script. Nothing is changed.
3. Deletes every folder under `Documents/Cowork/Tasks` in the user's OneDrive.
4. Deletes the `Trey Research` folder, then uploads a clean `Trey Research Vendor Agreement v4.2.docx` to a new `Trey Research` folder. The clean copy comes from a [GitHub gist](https://gist.github.com/tezansahu/cb1d8cd77697c089fc7765abb35af2e1) (base64 text), or from the copy next to the script if the download fails.

It works on OneDrive in the cloud, so it doesn't need the OneDrive sync client. It only changes the signed-in user's own OneDrive.

If the agreement is open in Word or in a Copilot session, SharePoint locks the folder. The script retries for one minute, then moves the locked folder aside as `Trey Research (old <date-time>)` and creates a fresh one. A later run deletes the old folder once the lock clears.

Every run writes a log to `reset-lab.log` next to the script, or to `%TEMP%` if that folder isn't writable.

## Set up the lab VM

1. Copy all three files to `C:\LabFiles\` on the VM, then commit the VM changes in Skillable.
2. In the Skillable instructions, add a command link that runs the script with the seat's sign-in name:

   ``@[Reset my lab environment](`C:\LabFiles\reset-lab.bat <seat sign-in name>`){Shell visible}``

   Command links need Integration Services on the VM.

## Set up the tenant

- **Approve the app once.** The script signs in with the Microsoft Graph Command Line Tools public client (`14d82eec-204b-4c2f-b7e8-296a70dab67e`), so no app registration is needed. To spare attendees a permissions prompt, a tenant admin approves it for the organization with the delegated permissions `User.Read` and `Files.ReadWrite`.
- **Allow sign-in from the lab VMs.** If a Conditional Access policy blocks security info registration outside trusted locations, attendees can't set up MFA. Add Skillable's outgoing IP ranges as a trusted named location.

## Update the clean agreement

The gist holds the agreement as base64 text, because gists don't accept binary files. To replace it:

```powershell
[IO.File]::WriteAllText("trey-research-vendor-agreement-v4.2.docx.b64", [Convert]::ToBase64String([IO.File]::ReadAllBytes("Trey Research Vendor Agreement v4.2.docx")))
```

Upload the new `.b64` file to the gist, and replace the `.docx` in this folder.
