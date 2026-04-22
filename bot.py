import discord
from discord.ext import commands
import os

# ===== FAST INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

OWNER_ID = 1321305307854667837  # 🔥 CHANGE THIS

config = {
    "CATEGORY_ID": None,
    "STAFF_ROLE_ID": None,
    "ALLOWED_ROLE_ID": None
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

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff = interaction.guild.get_role(config["STAFF_ROLE_ID"])

        if not staff or staff not in interaction.user.roles:
            return await interaction.response.send_message("❌ Staff only", ephemeral=True)

        await interaction.channel.edit(name=f"claimed-{interaction.user.name}")

        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Claimed by {interaction.user.name}")

        button.disabled = True
        button.label = "Claimed"

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("✅ Claimed", ephemeral=True)

# ================= MODAL =================
class TicketModal(discord.ui.Modal, title="Trade Ticket"):

    other = discord.ui.TextInput(label="Other trader (@ / username / ID)")
    giving = discord.ui.TextInput(label="Giving")
    receiving = discord.ui.TextInput(label="Receiving")

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild

        if not config["CATEGORY_ID"] or not config["STAFF_ROLE_ID"]:
            return await interaction.response.send_message("❌ Setup missing (!category / !staffrole)", ephemeral=True)

        category = guild.get_channel(config["CATEGORY_ID"])
        staff = guild.get_role(config["STAFF_ROLE_ID"])

        user_input = self.other.value.strip()
        other_user = None

        # mention
        if user_input.startswith("<@"):
            user_id = int(user_input.replace("<@", "").replace(">", "").replace("!", ""))
            other_user = guild.get_member(user_id)

        # id
        elif user_input.isdigit():
            other_user = guild.get_member(int(user_input))

        # username
        else:
            other_user = discord.utils.find(
                lambda m: user_input.lower() in m.name.lower() or user_input.lower() in m.display_name.lower(),
                guild.members
            )

        if not other_user:
            return await interaction.response.send_message("❌ User not found", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
            other_user: discord.PermissionOverwrite(view_channel=True),
            staff: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(title="📩 New Ticket", color=0x5865F2)
        embed.add_field(name="Creator", value=interaction.user.mention, inline=False)
        embed.add_field(name="Trader", value=other_user.mention, inline=False)
        embed.add_field(name="Giving", value=self.giving.value, inline=True)
        embed.add_field(name="Receiving", value=self.receiving.value, inline=True)
        embed.set_footer(text="Waiting for staff...")

        await channel.send(
            f"{interaction.user.mention} {other_user.mention} {staff.mention}",
            embed=embed,
            view=ClaimView()
        )

        await interaction.response.send_message(f"✅ Created: {channel.mention}", ephemeral=True)

# ================= DROPDOWN =================
class Dropdown(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="Open a ticket", options=[
            discord.SelectOption(label="Blox Fruits"),
            discord.SelectOption(label="Steal a Brainrot"),
            discord.SelectOption(label="Escape Tsunami"),
            discord.SelectOption(label="Other"),
        ])

    async def callback(self, interaction: discord.Interaction):
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
        description=(
            "Need a trusted middleman?\n"
            "Open a ticket below.\n\n"
            "**Rules:**\n"
            "• No DM spam\n"
            "• One ticket per deal\n"
            "• Provide proof\n"
            "• Scam = ban\n\n"
            "🎯 Safe & trusted service"
        ),
        color=0x5865F2
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1457964741745180785/1491392888469454879/file_00000000f0607208b08ba98abf46985f.png")

    await ctx.send(embed=embed, view=PanelView())

# ================= SETUP =================
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

# ================= CLOSE =================
@bot.tree.command(name="closeticket")
async def closeticket(interaction: discord.Interaction):

    staff = interaction.guild.get_role(config["STAFF_ROLE_ID"])

    if not staff or staff not in interaction.user.roles:
        return await interaction.response.send_message("❌ Staff only", ephemeral=True)

    await interaction.response.send_message("Closing...", ephemeral=True)
    await interaction.channel.delete()

# ================= READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Ready as {bot.user}")

bot.run(os.getenv("TOKEN"))