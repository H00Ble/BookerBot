# Email Reminder Bot - Python

A Discord bot that helps users set up recurring class reminders and automatically sends booking links at scheduled times.

## Features

- Add recurring classes with `/add_class` command
- Automatic reminders sent at scheduled times
- Support for different days of the week
- 24-hour time format input with automatic conversion

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in the project root with your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

3. **Update the bot configuration:**
   - Replace `MY_GUILD` ID with your Discord server ID
   - Replace the `channel_id` in `check_bookings_loop()` with your target channel ID

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## Usage

Use the `/add_class` command to add a new recurring class:
- `name`: Name of the class
- `day`: Day of the week (Monday, Tuesday, etc.)
- `time`: Time in 24-hour format (e.g., 06:00)
- `link`: Booking link

The bot will automatically send reminders at the specified times.

## Security Note

Never commit your Discord bot token to version control. Always use environment variables or a `.env` file (which should be added to `.gitignore`). 