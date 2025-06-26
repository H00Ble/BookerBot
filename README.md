# Discord Class Reminder Bot

A Discord bot that helps users set up recurring class reminders and automatically sends booking links at scheduled times.

## Features

- **Class Management**: Add, remove, and view recurring classes
- **Automatic Reminders**: Sends booking links at scheduled times

## Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `/add_class` | Add a new recurring class | `name`, `day`, `time`, `link` |
| `/remove_class` | Remove an existing class | `name` (with autocomplete) |
| `/list_classes` | View all scheduled classes | None |

### Command Details

- **`name`**: Class name (e.g., "Math 101", "Yoga Session")
- **`day`**: Day of the week (Monday through Sunday)
- **`time`**: Time in 24-hour format (e.g., "14:30" for 2:30 PM)
- **`link`**: Booking or class link (URL)

note: day/time is when you'll be reminded. Not when the event occurs.


