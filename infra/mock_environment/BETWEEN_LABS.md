# Between lab runs: reset MFA for the lab accounts

Do this as an admin after every lab run, before the next one starts.

## Why this is needed

Each attendee registers an authenticator for their `emilNNN` account on the lab VM. The lab VMs are destroyed after the session, along with that authenticator. On the next sign-in, the account asks for a code from the authenticator that no longer exists, and the attendee is locked out.

Asking the users to register their contact methods again clears the saved MFA device from every lab account. The next attendee can then set up MFA from scratch.

## Admin sign-in

Sign in as the tenant admin. The admin credentials are on the tenant page in the SEVAL portal:

- [Connectors_Ignite_EMP_WW_2, version 1.0](https://seval.microsoft.com/tenant/detail/Connectors_Ignite_EMP_WW_2/1.0)

Do not copy the credentials into this repository.

## Steps

1. Open [Per-user multifactor authentication](https://entra.microsoft.com/#view/Microsoft_AAD_AuthenticationMethods/MultifactorAuthenticationConfig.ReactView/tabId/users) in the Microsoft Entra admin center, signed in as the admin.
2. In the search box, filter for `emil`.
3. Keep scrolling down until `emil114` is listed, so every lab account is loaded.
4. Select all the listed accounts with the checkbox in the column header.
5. Select **User MFA settings**.
6. Check **Require selected users to provide contact methods again**.
7. Select **Save**.

![Per-user multifactor authentication with all emil accounts selected and the User MFA settings panel open](images/entra-user-mfa-settings.png)
