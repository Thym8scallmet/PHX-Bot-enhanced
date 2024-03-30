import datetime
import json
import os

import discord
import gspread
from discord import app_commands
from discord.ext import commands


class GetFlagData(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        # Update to load the service account details from the dictionary and not directly from the file.
        config = {
            "type": "service_account",
            "project_id": "flagcapturedata",
            "private_key_id": "319e906a9631c53c1cd2d358cfc3432b11de428c",
            "private_key": os.environ.get('GCP_PRIVATE_KEY'),  # Load the private key from an environment variable
            "client_email": "flagcapturedata@flagcapturedata.iam.gserviceaccount.com",
            "client_id": "109811611220042004574",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/flagcapturedata%40flagcapturedata.iam.gserviceaccount.com"
        }
        self.gc = gspread.service_account_from_dict(config)
        self.flag_data_workbook = self.gc.open("FlagData")
        self.allowed_guilds = [383365467894710272, 1045479020940234783]  # guild IDs

    async def guild_is_allowed(self, interaction: discord.Interaction):
        return interaction.guild and interaction.guild.id in self.allowed_guilds

    async def user_is_admin(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return False
        member = interaction.guild.get_member(interaction.user.id)
        return any(role.name.lower() == 'admin' for role in member.roles)

    @app_commands.command(name='get_flag_data')
    async def get_flag_data(self, interaction: discord.Interaction):
        if not await self.guild_is_allowed(interaction):
            await interaction.response.send_message("Your server does not have access to this feature.", ephemeral=True)
            return
        if not await self.user_is_admin(interaction):
            await interaction.response.send_message("You must be an admin to use this command.", ephemeral=True)
            return
        sheet = self.flag_data_workbook.sheet1
        data = sheet.get_all_records()
        player_list = [{'name': row['Name'], 'might': int(row['Might'])} for row in data if row['Name'] and row['Might']]
        with open('playerlist.json', 'w', encoding='utf-8') as f:
            json.dump(player_list, f, ensure_ascii=False, indent=4)
        await interaction.response.send_message("Data imported and saved successfully into playerlist.json")

    @app_commands.command(name='send_flag_data')
    async def update_google_sheet(self, interaction: discord.Interaction):
        if not await self.guild_is_allowed(interaction):
            await interaction.response.send_message("Your server does not have access to this feature.", ephemeral=True)
            return
        if not await self.user_is_admin(interaction):
            await interaction.response.send_message("You must be an admin to use this command.", ephemeral=True)
            return
        with open('playerlist.json', 'r', encoding='utf-8') as f:
            player_list = json.load(f)

        values = [['Name', 'Might']] + [[player['name'], player['might']] for player in player_list]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_sheet_title = f"Data_{timestamp}"
        new_sheet = self.flag_data_workbook.add_worksheet(title=new_sheet_title, rows="100", cols="20")
        new_sheet.update('A1', values)

        await interaction.response.send_message(f"Google Sheet successfully updated with the latest data in a new sheet named '{new_sheet_title}'.")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(GetFlagData(client))