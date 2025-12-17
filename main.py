import discord
from discord.ext import commands
from discord.ui import View, Button

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

zapisani = set()
wybrani = set()
LIMIT = 99

def create_embed():
    tekst = ""
    for uid in zapisani:
        if uid in wybrani:
            tekst += f"<@{uid}> | ✅ Wybrany\n"
        else:
            tekst += f"<@{uid}> | 📝 Zapisany\n"

    if not tekst:
        tekst = "Brak zapisanych."

    embed = discord.Embed(
        title="📅 Event zapis",
        color=0x2F3136
    )
    embed.add_field(name="Użytkownik | Status", value=tekst, inline=False)
    embed.add_field(name="Godzina", value="10:45", inline=False)
    embed.add_field(name="Wybrani", value=f"{len(wybrani)}/{LIMIT}", inline=False)
    return embed

class Zapisy(View):
    @discord.ui.button(label="Wpisz się / Wypisz się", style=discord.ButtonStyle.primary)
    async def toggle(self, interaction: discord.Interaction, button: Button):
        uid = interaction.user.id

        if uid in zapisani:
            zapisani.remove(uid)
            wybrani.discard(uid)
        else:
            zapisani.add(uid)

        await interaction.response.edit_message(embed=create_embed(), view=self)

@bot.command()
@commands.has_permissions(administrator=True)
async def event(ctx):
    await ctx.send(embed=create_embed(), view=Zapisy())

@bot.command()
@commands.has_role("Zarząd")
async def wybierz(ctx, member: discord.Member):
    if member.id not in zapisani:
        await ctx.send("❌ Użytkownik nie jest zapisany.")
        return
    wybrani.add(member.id)
    await ctx.send(f"✅ {member.mention} został wybrany.")

@bot.event
async def on_ready():
    print("Bot działa 24/7")

import os
bot.run(os.getenv("TOKEN"))
