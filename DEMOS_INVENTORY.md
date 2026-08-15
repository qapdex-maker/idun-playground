# Demo recordings inventory (stand-orphaned clips)

Stand: 2026-08-15. These clips are NOT Contoso Expo 2027 booth footage —
they are Microsoft Entra / M365 MCP-server admin recordings, kept because
they may be useful for a separate Entra/M365-MCP demo track. Logged here so
they are not lost or mistaken for booth material.

## Location (kept in place, not copied into this repo)
`~/repo/own/videos/` (Termux: `/data/data/com.termux/files/home/repo/own/videos/`)

| File | Duration | Resolution | Size | Content (verified via frame extract) |
|------|----------|------------|------|--------------------------------------|
| `Screen_Recording_20260815_082829_Edge.mp4` | 91.8s | 1080×2400 (portrait) | 19 MB | Microsoft Entra Admin Center — Connect-Sync → Security Copilot-Agents, QMFI-Research tenant overview (Alexander Kleine, Global Admin + 98 roles, 1 user, 6 apps) |
| `Screen_Recording_20260815_082951_Edge.mp4` | 65.2s | 1080×2400 (portrait) | 24 MB | Microsoft Entra Admin Center — App Registrations → MS 365 MCP Server → API Permissions (Microsoft Graph delegated perms: User.*, Sites.*, Tasks.*, MailboxSettings.*) |

## Notes
- Both recorded 2026-08-15 ~08:27–08:29 in Edge (Android/Termux), German UI.
- NOT part of the Contoso Expo 2027 booth (`expo.html`). The real booth
  recordings, if needed, must be captured from `http://127.0.0.1:9001/expo.html`
  (or `?kiosk=1`) in a browser.
- If these should become a demo asset in this repo later, copy them into
  `assets/demos/` and reference them from `expo.html` (a second, non-Contoso
  demo panel) — out of scope for now.
