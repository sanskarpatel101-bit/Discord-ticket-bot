# Middleman Ticket Bot

A lightweight and professional ticket system for Discord trading communities.
Built with modern Discord features like modals and dropdowns, this bot makes the middleman process simple, fast, and secure.

---

## Setup Guide

### 1. Install Dependencies

Make sure you have the required library installed:

```bash
pip install discord.py
```

---

### 2. Configure the Owner

Open `bot.py` and replace the `OWNER_ID` with your Discord user ID:

```python
OWNER_ID = 1321305307854667837  # Replace with your ID
```

---

### 3. Add Your Bot Token

The bot reads your token from environment variables.

* Recommended: Set a `TOKEN` environment variable
* Alternative: Replace:

  ```python
  os.getenv("TOKEN")
  ```

  with your actual bot token

---

### 4. Run the Bot

```bash
python bot.py
```

---

## Admin Configuration

Once the bot is online, the owner must run these commands:

| Command           | Description                                    |
| ----------------- | ---------------------------------------------- |
| `!category <ID>`  | Sets the category for all new tickets          |
| `!staffrole <ID>` | Defines the staff role that can manage tickets |
| `!panel`          | Sends the ticket creation panel                |

---

## How It Works

### For Users

**Open Ticket:**
Select a game from the dropdown menu on the ticket panel.

**Fill Form:**
A form will appear asking for:

* Other trader’s name or ID
* Items being traded

**Wait:**
A private ticket channel is created automatically, and staff are notified.

---

### For Staff

**Claiming:**
Click the “Claim Ticket” button.
The bot will rename the channel and mark you as the assigned middleman.

**Closing:**
Use the slash command:

```
/closeticket
```

This will delete the ticket channel after completion.

---

## Features

* Modern interface using buttons and dropdowns
* Flexible user lookup (mention, ID, or partial username)
* Automatic permission control for secure conversations
* Optimized and minimal codebase

---

## Notes

To get a Category ID or Role ID:

1. Enable Developer Mode in Discord
   `User Settings → Advanced → Developer Mode`
2. Right-click the role or category
3. Click “Copy ID”

---

## Summary

This bot simplifies trading workflows by:

* Automating ticket creation
* Structuring communication
* Ensuring secure, staff-managed transactions
