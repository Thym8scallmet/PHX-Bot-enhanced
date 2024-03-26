import asyncio

import discord
from discord import app_commands
from discord.ext import commands


class MakeMessages(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="make_messages",
        description="Makes a numbered list of messages up to 50")
    async def make_messages(self, interaction: discord.Interaction, number_of_messages: int = 5):
        # Before entering the loop, defer the response
        await interaction.response.defer(ephemeral=True)

        if number_of_messages < 1 or number_of_messages > 50:
            await interaction.followup.send("Please specify a number between 1 and 50.")
            return

        for i in range(1, number_of_messages + 1):
            if isinstance(interaction.channel, discord.TextChannel):
                await interaction.channel.send(f"{i}. This is an app-generated message.")
                await asyncio.sleep(1)  # Introduce a one-second delay here
            else:
                await interaction.followup.send("This command can only be used in text channels.", ephemeral=True)
                break

        await interaction.followup.send("Messages created successfully.", ephemeral=True)

async def setup(client: commands.Bot):
    # Initialize the cog
    cog = MakeMessages(client)
    await client.add_cog(cog)

    # Define allowed guilds
    allowed_guild_ids = [383365467894710272]  # Add other guild IDs as needed

    # Register the cog's commands specifically for the allowed guilds
    for guild_id in allowed_guild_ids:
        # Sync the global commands to the guild, making them appear only in the defined guilds
        client.tree.copy_global_to(guild=discord.Object(id=guild_id))
    await client.tree.sync()
