import discord

from PoS.src.add.entity_creator import start_entity_creator

class CreationMenu(discord.ui.View):
    def __init__(self, author_id: int, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Entity", style=discord.ButtonStyle.primary)
    async def entity_button(self, interaction, button):
        await start_entity_creator(interaction)

    @discord.ui.button(label="Item", style=discord.ButtonStyle.primary)
    async def item_button(self, interaction, button):
        await interaction.response.send_message(
            "Item creation will be implemented here.",
            ephemeral=True
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction, button):
        self.stop()
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)


async def creation_menu(message):
    embed = discord.Embed(
        title="Path of Steel — Creation Menu",
        description="Select the type of game data you want to create."
    )

    view = CreationMenu(message.author.id)

    await message.channel.send(embed=embed, view=view)