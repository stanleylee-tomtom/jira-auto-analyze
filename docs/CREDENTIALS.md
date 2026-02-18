# How to Get Your Atlassian Credentials

## Required Credentials

You need three pieces of information:
1. **ATLASSIAN_CLOUD_ID** - Your Jira site identifier  
2. **ATLASSIAN_API_TOKEN** - API token for authentication
3. **ATLASSIAN_EMAIL** - Your Atlassian account email

---

## Getting Your Credentials

### 1. Get Your Cloud ID

**Option A: From Jira URL**
- If your Jira is at: `https://yourcompany.atlassian.net`
- Your site URL is: `yourcompany.atlassian.net` (use this as Cloud ID)

**Option B: Get the UUID**
```bash
curl -u your-email@example.com:your-api-token \
  https://api.atlassian.com/oauth/token/accessible-resources
```

Returns:
```json
[
  {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "url": "https://yourcompany.atlassian.net",
    "name": "Your Company"
  }
]
```

Use either the `"id"` (UUID) or the site URL as your Cloud ID.

### 2. Create an API Token

1. Visit: **https://id.atlassian.com/manage-profile/security/api-tokens**
2. Click **"Create API token"**
3. Label it (e.g., "Jira Analysis Tool")
4. **Copy the token immediately** (you won't see it again!)
5. Token format: `ATATTxxxxxxxxx...` (~200 characters)

### 3. Get Your Email

This is the email address you use to log into Jira/Atlassian.

---

## Configure .env File

```bash
cd jira-auto-analyze
cp .env.example .env
nano .env
```

Add your credentials:
```env
ATLASSIAN_CLOUD_ID=yourcompany.atlassian.net
ATLASSIAN_API_TOKEN=ATATTxxxxxxxxxxxxxxxxxxxxxxxxx
ATLASSIAN_EMAIL=your-email@example.com
```

**Note:** You can use either:
- Site URL format: `yourcompany.atlassian.net`
- UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

Both work as Cloud ID.

---

## Verify Setup

```bash
python test_connection.py
```

Or:

```bash
python -m src.cli config
```

Should show all credentials as ✓ Set.

---

## Security Notes

- Never commit `.env` to git (already in .gitignore)
- Store API token securely
- Rotate tokens periodically
- Use read-only permissions if possible
