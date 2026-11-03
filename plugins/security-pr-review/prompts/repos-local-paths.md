Mattermost repositories. If you need to read code that
lives outside the repo you were pointed at (a plugin, the desktop app, the
enterprise module, ...), use the repository below. If you do not already have
a local checkout, clone it read-only into a temporary directory
(`gh repo clone mattermost/<repo> <tmpdir>/<repo>`) and read the intended tree from it:

WARNING: these checkouts are SHARED and can sit at any commit - a feature
branch, a mid-review state, or simply behind `origin/master`. Any local checkout you find (or that
locates a repo by path) does NOT tell you what its working tree currently holds.
Never read one by bare path to decide what the code is, and never state that a
file or symbol is absent on that basis. Read the intended tree instead - a
pinned worktree you were given, or `git -C <repo> show origin/master:<path>`:
@reading-the-right-tree.md

Mattermost (monorepo/server): mattermost/mattermost
Enterprise: mattermost/enterprise
Desktop: mattermost/desktop
Mattermost Mobile: mattermost/mattermost-mobile
Mattermost Docker: mattermost/docker
Mattermost Cloud: mattermost/mattermost-cloud
Customer Web Server (CWS): mattermost/customer-web-server
Plugin Mattermost Agents: mattermost/mattermost-plugin-agents
Plugin Mattermost Boards: mattermost/mattermost-plugin-boards
Plugin Mattermost Calls: mattermost/mattermost-plugin-calls
Plugin Mattermost Channel Automation: mattermost/mattermost-plugin-channel-automation
Plugin Mattermost Channel Export: mattermost/mattermost-plugin-channel-export
Plugin Mattermost Confluence: mattermost/mattermost-plugin-confluence
Plugin Mattermost Docs: mattermost/mattermost-plugin-docs
Plugin Mattermost Github: mattermost/mattermost-plugin-github
Plugin Mattermost Gitlab: mattermost/mattermost-plugin-gitlab
Plugin Mattermost Jira: mattermost/mattermost-plugin-jira
Plugin Mattermost MS Calendar: mattermost/mattermost-plugin-mscalendar
Plugin Mattermost MS Teams: mattermost/mattermost-plugin-msteams
Plugin Mattermost MS Teams Meetings: mattermost/mattermost-plugin-msteams-meetings
Plugin Mattermost Playbooks: mattermost/mattermost-plugin-playbooks
Plugin Mattermost ServiceNow: mattermost/mattermost-plugin-servicenow
Plugin Mattermost User Survey: mattermost/mattermost-plugin-user-survey
Plugin Mattermost Metrics: mattermost/mattermost-plugin-metrics
Plugin Mattermost Zoom: mattermost/mattermost-plugin-zoom
Plugin Message-Based Encryption: mattermost/message-based-encryption
RTCD: mattermost/rtcd
Calls Offloader: mattermost/calls-offloader
Calls Recorder: mattermost/calls-recorder
Calls Transcriber: mattermost/calls-transcriber
Calls Common: mattermost/calls-common
