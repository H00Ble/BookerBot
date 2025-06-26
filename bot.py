# This example requires the 'message_content' intent.

import discord
from discord import app_commands, user
import json
import asyncio
from datetime import datetime, timedelta
import enum
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MY_GUILD = discord.Object(id=1088303994461487197)  # replace with your test server ID

class Day(enum.Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="add_class", description="Add a recurring class to be reminded about")
@app_commands.describe(
    name="Name of the class. Must be unique. Suggested: 'Pilates Thursday' or 'Yoga 10:00AM'",
    time="Time in 24-hour format (e.g., 06:00)",
    link="Link to booking"
)
@app_commands.choices(day=[
    app_commands.Choice(name="Monday", value="Monday"),
    app_commands.Choice(name="Tuesday", value="Tuesday"),
    app_commands.Choice(name="Wednesday", value="Wednesday"),
    app_commands.Choice(name="Thursday", value="Thursday"),
    app_commands.Choice(name="Friday", value="Friday"),
    app_commands.Choice(name="Saturday", value="Saturday"),
    app_commands.Choice(name="Sunday", value="Sunday"),
])
async def add_class(interaction: discord.Interaction, name: str, day: str, time: str, link: str):
    try:
        # Parse and validate time format
        try:
            # Convert 24-hour format to 12-hour format
            time_obj = datetime.strptime(time, "%H:%M")
            formatted_time = time_obj.strftime("%I:%M%p")  # e.g., "06:00AM" (with leading zero)
        except ValueError:
            await interaction.response.send_message("Invalid time format. Please use 24-hour format (e.g., 06:00)", ephemeral=True)
            return
        
        # Create booking time string
        booking_time = f"{day}, {formatted_time}"
        
        new_class = {
            "user": interaction.user.id,
            "class": name,
            "booking_time": booking_time,
            "booking_link": link
        }

        # Load existing data
        try:
            with open("classes.json", "r") as file:
                classes = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            classes = []

        # Check for duplicates
        existing_names = [cls["class"] for cls in classes if cls.get("user") == interaction.user.id]
        if name in existing_names:
            await interaction.response.send_message(f"❌ You already have a class named '{name}'. Please use a different name.", ephemeral=True)
            return

        # Add new class
        classes.append(new_class)

        # Save updated data
        with open("classes.json", "w") as file:
            json.dump(classes, file, indent=4)

        await interaction.response.send_message(f"✅ Added class '{name}' for {day} at {formatted_time}", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error adding class: {str(e)}", ephemeral=True)

#autocomplete for class name
async def class_autocomplete(interaction: discord.Interaction, current: str):
    try:
        # Load existing classes
        with open("classes.json", "r") as file:
            classes = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        classes = []
    
    # Get class names for the current user
    user_classes = [cls["class"] for cls in classes if cls.get("user") == interaction.user.id]
    
    # Filter based on what user is typing
    filtered_classes = [
        app_commands.Choice(name=class_name, value=class_name)
        for class_name in user_classes
        if current.lower() in class_name.lower()
    ]
    
    # Return up to 25 choices (Discord limit)
    return filtered_classes[:25]


@tree.command(name="remove_class", description="Remove a class you don't want to be reminded about anymore")
@app_commands.describe(
    name="Name of the class",
)
@app_commands.autocomplete(name=class_autocomplete)
async def remove_class(interaction: discord.Interaction, name: str):
    try:
        # Load existing data
        with open("classes.json", "r") as file:
            classes = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        classes = []
    
    # Find the class to remove (only for current user)
    class_to_remove = None
    for cls in classes:
        if cls["class"] == name and cls.get("user") == interaction.user.id:
            class_to_remove = cls
            break
    
    if not class_to_remove:
        await interaction.response.send_message(f"❌ Class '{name}' not found in your schedule.", ephemeral=True)
        return
    
    # Remove the class
    classes.remove(class_to_remove)
    
    # Save updated data
    try:
        with open("classes.json", "w") as file:
            json.dump(classes, file, indent=4)
        await interaction.response.send_message(f"✅ Removed class '{name}' from your schedule.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error removing class: {str(e)}", ephemeral=True)

@tree.command(name = "change_class", description = "Change a class in your schedule")
@app_commands.describe(
    name = "Name of the class"
)
@app_commands.autocomplete(name = class_autocomplete)
@app_commands.choices(day=[
    app_commands.Choice(name="Monday", value="Monday"),
    app_commands.Choice(name="Tuesday", value="Tuesday"),
    app_commands.Choice(name="Wednesday", value="Wednesday"),
    app_commands.Choice(name="Thursday", value="Thursday"),
    app_commands.Choice(name="Friday", value="Friday"),
    app_commands.Choice(name="Saturday", value="Saturday"),
    app_commands.Choice(name="Sunday", value="Sunday"),
])
async def change_class(interaction: discord.Interaction, name: str, day: str, time: str = "", link: str = ""):
    try:
        # Load existing data
        with open("classes.json", "r") as file:
            classes = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        classes = []

    # Find the class to change (only for current user)
    class_to_change = None
    for cls in classes:
        if cls["class"] == name and cls.get("user") == interaction.user.id:
            class_to_change = cls
            break
    
    if not class_to_change:
        await interaction.response.send_message(f"❌ Class '{name}' not found in your schedule.", ephemeral=True)
        return
    
    if time:
        try:
            # Convert 24-hour format to 12-hour format
            time_obj = datetime.strptime(time, "%H:%M")
            formatted_time = time_obj.strftime("%I:%M%p")  # e.g., "06:00AM" (with leading zero)
        except ValueError:
            await interaction.response.send_message("Invalid time format. Please use 24-hour format (e.g., 06:00)", ephemeral=True)
            return
        class_to_change["booking_time"] = f"{day}, {formatted_time}"

    if link:
        class_to_change["booking_link"] = link

    # Save updated data
    try:
        with open("classes.json", "w") as file:
            json.dump(classes, file, indent=4)
        await interaction.response.send_message(f"✅ Changed class '{name}' for {day} at {time}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error changing class: {str(e)}", ephemeral=True)

@tree.command(name="list_classes", description="Show all your scheduled classes")
async def list_classes(interaction: discord.Interaction):
    try:
        # Load existing data
        with open("classes.json", "r") as file:
            classes = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        classes = []
    
    # Get classes for current user
    user_classes = [cls for cls in classes if cls.get("user") == interaction.user.id]
    
    if not user_classes:
        await interaction.response.send_message("📝 You don't have any classes scheduled yet. Use `/add_class` to add your first class!", ephemeral=True)
        return
    
    # Format the classes list
    class_list = []
    for i, cls in enumerate(user_classes, 1):
        class_name = cls["class"]
        booking_time = cls["booking_time"]
        booking_link = cls["booking_link"]
        class_list.append(f"**{i}.** {class_name} - {booking_time}\n   🔗 {booking_link}")
    
    # Create the message
    message = f"📚 **Your Scheduled Classes ({len(user_classes)} total):**\n\n" + "\n\n".join(class_list)
    
    await interaction.response.send_message(message, ephemeral=True)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Sync commands globally to force clear cache
    try:
        await tree.sync()  # Global sync instead of guild-specific
        print("Commands synced globally!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    client.loop.create_task(check_bookings_loop())


async def check_bookings_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            now = datetime.now()
            now_string = now.strftime("%A, %I:%M%p")  # e.g., "Thursday, 06:00AM" (with leading zero)

            # Load class booking data
            try:
                with open("classes.json", "r") as file:
                    classes = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                classes = []

            channel_id = os.getenv('REMINDER_CHANNEL_ID')
            if channel_id:
                channel = client.get_channel(int(channel_id))
            else:
                print("Error: REMINDER_CHANNEL_ID environment variable is not set. Please create a .env file with your channel ID.")
                await asyncio.sleep(60)
                continue
            
            # Check if channel exists and is a text channel
            if not channel or not isinstance(channel, discord.TextChannel):
                print(f"Error: Channel {channel_id} not found or not a text channel")
                await asyncio.sleep(60)
                continue
            
            for cls in classes:
                user_id = cls.get("user")
                class_name = cls.get("class")  # Fixed field name
                booking_time = cls.get("booking_time")
                booking_link = cls.get("booking_link")
                  
                print(f"Checking: {now_string} vs {booking_time}")
                if booking_time == now_string:
                    mention = f"<@{user_id}> " if user_id else ""
                    embed = discord.Embed(title=f"⏰ Time to book **{class_name}**!", description=f"{booking_link}", color=discord.Color.blue())
                    await channel.send(content=mention, embed=embed)

        except Exception as e:
            print(f"Error in check_bookings_loop: {e}")
        
        await asyncio.sleep(60)  # check every 60 seconds

# Load token from environment variable for security
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set. Please create a .env file with your token.")
client.run(TOKEN)
