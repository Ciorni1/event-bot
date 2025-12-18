import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import os

# ====== USTAWIENIA ======
EVENT_NAME = "Dilerzy"
EVENT_TIME = "10:45"
LIMIT = 99
ZARZAD_ROLE = "Zarząd"
# =======================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

zapisani = set()
wybrani = set()
event_message = None


# ====== EMBED ======
def create_embed():
    text = ""

    for uid in zapisani:
        if uid in wybrani:
            text += f"<@{uid}> | ✅ Wybrany\n"
        else:
            text += f"<@{uid}> | 📝 Zapisany\n"

    if not text:
        text = "Brak zapisanych."

    embed = discord.Embed(
        title=f"📅 Event: {EVENT_NAME}",
        color=0x2F3136
    )
    embed.add_field(name="Użytkownik | Status", value=text, inline=False)
    embed.add_field(name="Godzina", value=EVENT_TIME, inline=False)
    embed.add_field(name="Wybrani", value=f"{len(wybrani)}/{LIMIT}", inline=False)

    return embed


# ====== PANEL ADMINA ======
class AdminView(View):
    def __init__(self, guild):
        super().__init__(timeout=60)

        zapisani_opts = []
        wybrani_opts = []

        for uid in zapisani:
            member = guild.get_member(uid)
            if member:
                zapisani_opts.append(
                    discord.SelectOption(
                        label=member.display_name,
                        value=str(uid)
                    )
                )

        for uid in wybrani:
            member = guild.get_member(uid)
            if member:
                wybrani_opts.append(
                    discord.SelectOption(
                        label=member.display_name,
                        value=str(uid)
                    )
                )

        self.add_item(WybierzSelect(zapisani_opts))
        self.add_item(CofnijSelect(wybrani_opts))


class WybierzSelect(Select):
    def __init__(self, options):
        super().__init__(
            placeholder="✅ Wybierz użytkownika",
            options=options[:25],
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        uid = int(self.values[0])
        wybrani.add(uid)

        if event_message:
            await event_message.edit(embed=create_embed(), view=MainView())

        await interaction.response.send_message(
            f"✅ <@{uid}> został wybrany",
            ephemeral=True
        )


class CofnijSelect(Select):
    def __init__(self, options):
        super().__init__(
            placeholder="❌ Cofnij wybranie",
            options=options[:25],
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        uid = int(self.values[0])
        wybrani.discard(uid)

        if event_message:
            await event_message.edit(embed=create_embed(), view=MainView())

        await interaction.response.send_message(
            f"❌ Cofnięto wybranie <@{uid}>",
            ephemeral=True
        )


# ====== GŁÓWNY VIEW ======
class MainView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Wpisz się / Wypisz się", style=discord.ButtonStyle.primary)
    async def toggle(self, interaction: discord.Interaction, button: Button):
        uid = interaction.user.id

        if uid in zapisani:
            zapisani.remove(uid)
            wybrani.discard(uid)
        else:
            zapisani.add(uid)

        if event_message:
            await event_message.edit(embed=create_embed(), view=self)

        await interaction.response.defer()

    @discord.ui.button(label="Administracyjne", style=discord.ButtonStyle.secondary)
    async def admin(self, interaction: discord.Interaction, button: Button):

        # 🔥 CACHE-SAFE sprawdzanie roli
        member = await interaction.guild.fetch_member(interaction.user.id)

        if not discord.utils.get(member.roles, name=ZARZAD_ROLE):
            await interaction.response.send_message(
                "❌ Nie masz uprawnień",
                ephemeral=True
            )
            return

        if not zapisani:
            await interaction.response.send_message(
                "Brak zapisanych użytkowników.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔧 Panel administracyjny",
            view=AdminView(interaction.guild),
            ephemeral=True
        )


# ====== START EVENTU ======
@bot.command()
@commands.has_permissions(administrator=True)
async def event(ctx):
    global event_message
    zapisani.clear()
    wybrani.clear()

    event_message = await ctx.send(
        embed=create_embed(),
        view=MainView()
    )


@bot.event
async def on_ready():
    print("Bot działa 24/7 (cache-safe)")


bot.run(os.getenv("TOKEN"))
