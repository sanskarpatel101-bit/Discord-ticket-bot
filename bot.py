import discord
from discord.ext import commands
import os
import asyncio

# ===== KEEP ALIVE =====
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    Thread(target=run).start()

# ===== BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

OWNER_ID = 1321305307854667837  # 🔥 CHANGE THIS

config = {
    "CATEGORY_ID": None,
    "STAFF_ROLE_ID": None,
    "ALLOWED_ROLE_ID": None,
    "LOG_CHANNEL_ID": None
}

# ================= OWNER CHECK =================
def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

# ================= CLAIM =================
class ClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.blurple)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff = interaction.guild.get_role(config["STAFF_ROLE_ID"])

        if not staff or staff not in interaction.user.roles:
            await interaction.response.send_message("❌ Only staff", ephemeral=True)
            return

        await interaction.channel.edit(name=f"claimed-by-{interaction.user.name}")

        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Claimed by: {interaction.user.name}")

        button.disabled = True
        button.label = "Claimed"

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("✅ Claimed", ephemeral=True)


# ================= MODAL =================
class TicketModal(discord.ui.Modal, title="Trade Ticket"):

    other = discord.ui.TextInput(label="Other trader (@mention / username / ID)")
    giving = discord.ui.TextInput(label="What are you giving?")
    receiving = discord.ui.TextInput(label="What are you receiving?")

    async def on_submit(self, interaction: discord.Interaction):

        try:
            guild = interaction.guild

            # ===== CHECK CONFIG =====
            if not config["CATEGORY_ID"]:
                return await interaction.response.send_message("❌ Set category first (!category)", ephemeral=True)

            if not config["STAFF_ROLE_ID"]:
                return await interaction.response.send_message("❌ Set staff role (!staffrole)", ephemeral=True)

            category = guild.get_channel(config["CATEGORY_ID"])
            staff_role = guild.get_role(config["STAFF_ROLE_ID"])

            # ===== FIND USER =====
            user_input = self.other.value.strip()
            other_user = None

            # mention
            if user_input.startswith("<@"):
                user_id = int(user_input.replace("<@", "").replace(">", "").replace("!", ""))
                other_user = guild.get_member(user_id)

            # id
            elif user_input.isdigit():
                other_user = guild.get_member(int(user_input))

            # username / nickname
            else:
                other_user = discord.utils.find(
                    lambda m: user_input.lower() in m.name.lower()
                    or user_input.lower() in m.display_name.lower(),
                    guild.members
                )

            if not other_user:
                return await interaction.response.send_message("❌ User not found", ephemeral=True)

            # ===== CREATE CHANNEL =====
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True),
                other_user: discord.PermissionOverwrite(view_channel=True),
                staff_role: discord.PermissionOverwrite(view_channel=True)
            }

            channel = await guild.create_text_channel(
                name=f"sab-ticket-{interaction.user.name}",
                category=category,
                overwrites=overwrites
            )

            # ===== EMBED =====
            embed = discord.Embed(title="📩 New Trade Ticket", color=0xff9900)
            embed.add_field(name="Creator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Other Trader", value=other_user.mention, inline=False)
            embed.add_field(name="Giving", value=self.giving.value, inline=True)
            embed.add_field(name="Receiving", value=self.receiving.value, inline=True)
            embed.set_footer(text="⏳ Waiting for middleman...")

            # ===== SEND MESSAGE (PING BOTH) =====
            await channel.send(
                f"{interaction.user.mention} {other_user.mention} {staff_role.mention}",
                embed=embed,
                view=ClaimView()
            )

            await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


# ================= DROPDOWN =================
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Blox Fruits"),
            discord.SelectOption(label="Steal a Brainrot"),
            discord.SelectOption(label="Escape Tsunami"),
            discord.SelectOption(label="Other"),
        ]
        super().__init__(placeholder="Select ticket type", options=options)

    async def callback(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(config["ALLOWED_ROLE_ID"])

        if role and role not in interaction.user.roles:
            return await interaction.response.send_message("❌ Not allowed", ephemeral=True)

        await interaction.response.send_modal(TicketModal())


class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())


# ================= PANEL =================
@bot.command()
@is_owner()
async def panel(ctx):

    embed = discord.Embed(
        title="🎫 Middleman Ticket Panel",
        description="""Need a trusted middleman for your trade or deal?
Open a ticket below and our verified Middlemen will assist you safely and quickly.

📜 Rules before opening a ticket:
• Do not ping or DM staff or middlemen directly.
• Open one ticket at a time.
• Provide clear proof of trade.
• Scamming = ban.

Click below to open a ticket!

🎯 Safe & fast transactions.""",
        color=0xff6600
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1457964741745180785/1491392888469454879/file_00000000f0607208b08ba98abf46985f.png")

    await ctx.send(embed=embed, view=PanelView())


# ================= OWNER COMMANDS =================
@bot.command()
@is_owner()
async def category(ctx, id: int):
    config["CATEGORY_ID"] = id
    await ctx.send("✅ Category set")

@bot.command()
@is_owner()
async def staffrole(ctx, id: int):
    config["STAFF_ROLE_ID"] = id
    await ctx.send("✅ Staff role set")

@bot.command()
@is_owner()
async def supportedrole(ctx, id: int):
    config["ALLOWED_ROLE_ID"] = id
    await ctx.send("✅ Allowed role set")

@bot.command()
@is_owner()
async def log(ctx, id: int):
    config["LOG_CHANNEL_ID"] = id
    await ctx.send("✅ Log channel set")

@bot.command()
@is_owner()
async def help(ctx):
    await ctx.send("""
!panel
!category <id>
!staffrole <id>
!supportedrole <id>
!log <id>
/closeticket
""")


# ================= CLOSE =================
@bot.tree.command(name="closeticket")
async def closeticket(interaction: discord.Interaction):

    staff = interaction.guild.get_role(config["STAFF_ROLE_ID"])

    if not staff or staff not in interaction.user.roles:
        return await interaction.response.send_message("❌ Only staff", ephemeral=True)

    await interaction.response.send_message("🔒 Closing...", ephemeral=True)
    await asyncio.sleep(2)
    await interaction.channel.delete()


# ================= READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


# START
keep_alive()
bot.run(os.getenv("TOKEN"))