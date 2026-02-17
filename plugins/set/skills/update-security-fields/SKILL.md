---
description: "Using the description of the linked Jira ticket, compose values for the CVE Title, CVE Description, and Security Update Text"
---

Using the description of the linked Jira ticket, compose values for the CVE Title, CVE Description, and Security Update Text according to the following format:

* CVE Title (customfield_11368): Short description of the vulnerability
* CVE Description (customfield_11369): fail to [ROOT CAUSE] which allows [ATTACKER] to [IMPACT] via [VECTOR]
* Security Update Text (customfield_11118): Fixed an issue where [ADD DETAILS]. Thanks to [REPORTER, see original field value] for contributing to this improvement under the Mattermost responsible disclosure policy.

Use the format exactly as described above, substituting only the placeholders with the appropriate values from the Jira ticket description. Ensure that the CVE Title is concise, the CVE Description clearly outlines the vulnerability, and the Security Update Text provides additional context and acknowledges the reporter.

To read the ticket and relevant fields:

```
acli jira workitem view MM-67536 --json --fields summary,description,reporter,customfield_11368,customfield_11369,customfield_11118
```

Once the values have been composed, present them to the user and ask for confirmation before updating the Jira ticket. Do not update any fields until the user explicitly approves.

If the values are not ready, ask for more information or clarification on the ticket description to ensure accurate and complete updates.
