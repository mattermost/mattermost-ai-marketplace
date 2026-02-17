# set

Helpers for SET workflows.

## Skills

| Skill | Description |
|-------|-------------|
| `update-security-fields` | Compose CVE Title, CVE Description, and Security Update Text from a Jira ticket |

## Usage

```
/set:update-security-fields https://mattermost.atlassian.net/browse/MM-67536
```

Provide or reference a Jira ticket and the skill will draft values for the three security custom fields, then offer to update them.

## Author

Jesse Hallam
