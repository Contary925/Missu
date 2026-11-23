import discord

from PoS.src.add.entity_creator import start_entity_creator
from PoS.src.add.item_creator import start_item_creator
from PoS.src.add.enemy_drops_creator import start_enemy_drops_creator
from PoS.src.add.enemy_skills_creator import start_enemy_skills_creator
from PoS.src.add.npc_merchant_editor import start_npc_merchant_editor
from PoS.src.add.npc_quest_creator import start_npc_quest_creator

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
        await start_item_creator(interaction)

    @discord.ui.button(
        label="Enemy Drops",
        style=discord.ButtonStyle.primary
    )
    async def enemy_drops_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await start_enemy_drops_creator(interaction)

    @discord.ui.button(
        label="Enemy Skills",
        style=discord.ButtonStyle.primary
    )
    async def enemy_skills_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await start_enemy_skills_creator(interaction)

    @discord.ui.button(
        label="Merchant Inventory",
        style=discord.ButtonStyle.primary
    )
    async def merchant_inventory_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await start_npc_merchant_editor(interaction)

    @discord.ui.button(
        label="NPC Quests",
        style=discord.ButtonStyle.primary
    )
    async def npc_quests_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await start_npc_quest_creator(interaction)

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