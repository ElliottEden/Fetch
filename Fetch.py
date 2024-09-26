import discord
import json
import os
from discord.ext import commands
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord bot token from .env
TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize the bot with required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Important for accessing message content

client = commands.Bot(command_prefix='!', intents=intents)

# PDF class to handle pagination, headers, and footers with UTF-8 encoding support
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Discord Conversation Export', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

# DEBUGGING: Notify when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

# Command for fetching logs from multiple channels and saving to a single JSON file
@client.command(name='fetch_logs')
async def fetch_logs(ctx, *channel_names):
    try:
        if not channel_names:
            await ctx.send("Please specify at least one channel.")
            return

        # Collect messages from all specified channels
        messages = []
        cleaned_channel_names = []
        for channel_name in channel_names:
            channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

            if not channel:
                await ctx.send(f"Channel '{channel_name}' not found!")
                continue

            # Clean the channel name for use in a filename (remove spaces, special characters, etc.)
            cleaned_channel_name = ''.join(e for e in channel.name if e.isalnum() or e == '_')
            cleaned_channel_names.append(cleaned_channel_name)

            async for message in channel.history(limit=None, oldest_first=True):
                messages.append({
                    'author': message.author.name,
                    'content': message.content,
                    'timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'channel_name': channel.name
                })

        # If no messages were collected
        if not messages:
            await ctx.send("No messages were fetched.")
            return

        # Sort the messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"))

        # Create the output filenames based on the channels, limiting the total length
        combined_channel_names = '_'.join(cleaned_channel_names)
        if len(combined_channel_names) > 50:  # Limit filename length to 50 characters
            combined_channel_names = combined_channel_names[:50] + "_combined"

        temp_filename = f"{combined_channel_names}_logs.json"
        
        with open(temp_filename, 'w', encoding='utf-8') as f:
            json.dump(sorted_messages, f, ensure_ascii=False, indent=4)

        # Send confirmation message
        await ctx.send(f"Logs from {', '.join(channel_names)} have been combined and saved as {temp_filename}.")

        # Send the combined logs as a JSON file
        with open(temp_filename, 'rb') as file:
            await ctx.send("Here are the combined logs:", file=discord.File(file, temp_filename))

        os.remove(temp_filename)

    except Exception as e:
        await ctx.send(f"Error fetching logs: {str(e)}")
        print(f"Error in fetch_logs: {str(e)}")

# Command for exporting logs to a PDF file
@client.command(name="export_to_pdf")
async def export_to_pdf(ctx):
    try:
        if len(ctx.message.attachments) == 0:
            await ctx.send("Please attach a JSON file to this command.")
            return

        attachment = ctx.message.attachments[0]
        json_filename = attachment.filename
        await attachment.save(json_filename)

        await ctx.send(f"Starting PDF generation for {json_filename}...")

        messages = load_messages_from_json(json_filename)
        sorted_messages = sort_messages(messages)

        # Output PDF filename derived from the JSON filename (based on the channel names)
        output_pdf_filename = json_filename.replace(".json", ".pdf")
        export_messages_to_pdf(sorted_messages, output_pdf_filename)

        # Send the generated PDF back to Discord
        with open(output_pdf_filename, 'rb') as pdf_file:
            await ctx.send(f"Here is the generated PDF ({output_pdf_filename}):", file=discord.File(pdf_file, output_pdf_filename))

    except Exception as e:
        await ctx.send(f"Error generating PDF: {str(e)}")
        print(f"Error in export_to_pdf: {str(e)}")

# Function to load messages from JSON
def load_messages_from_json(json_filename):
    with open(json_filename, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    return messages

# Function to sort messages by timestamp
def sort_messages(messages):
    return sorted(messages, key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"))

# Function to export messages to PDF
def export_messages_to_pdf(messages, output_pdf_filename):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.chapter_title('Combined Discord Conversation')
    for message in messages:
        formatted_message = format_message(message)
        pdf.chapter_body(formatted_message)
    
    pdf.output(output_pdf_filename)

# Function to format a message
def format_message(message):
    timestamp = message['timestamp']
    author = message['author']
    content = message['content']
    channel_name = message['channel_name']
    return f"[{timestamp}] {author} in #{channel_name}: {content}"

# Run the bot with the token from .env
client.run(TOKEN)
