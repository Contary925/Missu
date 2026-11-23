
import copy
import json
import discord

from pathlib import Path


NPC_PATH = Path("PoS/src/NPC/npc_info.json")
ITEM_PATH = Path("PoS/src/items/item_data.json")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_npc_inventory(npc_id: str, items: list):
    npcs = load_json(NPC_PATH)

    if npc_id not in npcs:
        raise ValueError(f"NPC `{npc_id}` not found.")

    if npcs[npc_id].get("type") != "merchant":
        raise ValueError(f"NPC `{npc_id}` is not a merchant.")

    npcs[npc_id]["items"] = items

    with NPC_PATH.open("w", encoding="utf-8") as f:
        json.dump(npcs, f, indent=4, ensure_ascii=False)


class NPCSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label=npc[:100],
                value=npc,
                description="Merchant inventory"
            )
            for npc in view.merchants
        ]

        super().__init__(
            placeholder="Select merchant...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        npc = self.values[0]

        self.editor.selected_npc = npc
        self.editor.items = copy.deepcopy(
            self.editor.original_npcs[npc].get("items", [])
        )
        self.editor.selected_item = None

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class ItemSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label=item_id[:100],
                value=item_id,
                description=item.get("name", item_id)[:100]
            )
            for item_id, item in view.available_items.items()
        ]

        super().__init__(
            placeholder="Select item...",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        self.editor.selected_item = self.values[0]

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class NPCMerchantEditorView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        timeout: float = 300
    ):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        self.original_npcs = load_json(NPC_PATH)
        self.available_items = load_json(ITEM_PATH)

        self.merchants = [
            npc_id
            for npc_id, data in self.original_npcs.items()
            if data.get("type") == "merchant"
        ]

        self.selected_npc = None
        self.selected_item = None
        self.items = []

        if not self.merchants:
            raise ValueError("No merchants found.")

        if len(self.merchants) > 25:
            raise ValueError(
                "More than 25 merchants. Select pagination is required."
            )

        if not self.available_items:
            raise ValueError("No items found.")

        if len(self.available_items) > 25:
            raise ValueError(
                "More than 25 items. Select pagination is required."
            )

        self.add_item(NPCSelect(self))
        self.add_item(ItemSelect(self))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False

        return True

    def construct_embed(self):
        embed = discord.Embed(
            title="Path of Steel — Merchant Inventory Editor",
            color=discord.Color.blurple()
        )

        if self.selected_npc is None:
            embed.description = "Select a merchant to manage their inventory."
            return embed

        npc_data = self.original_npcs[self.selected_npc]

        embed.description = (
            f"**Merchant:** `{self.selected_npc}`\n"
            f"**Greeting:** {npc_data.get('greeting', 'Not specified')}"
        )

        if self.items:
            lines = []

            for item_id in self.items:
                item_name = self.available_items.get(
                    item_id, {}
                ).get("name", item_id)

                selected = (
                    " ◀"
                    if item_id == self.selected_item
                    else ""
                )

                lines.append(
                    f"**{item_name}** (`{item_id}`){selected}"
                )

            inventory_text = "\n".join(lines)

            if len(inventory_text) > 4000:
                inventory_text = inventory_text[:3997] + "..."

            embed.add_field(
                name=f"Current Inventory ({len(self.items)})",
                value=inventory_text,
                inline=False
            )
        else:
            embed.add_field(
                name="Current Inventory",
                value="This merchant has no items.",
                inline=False
            )

        if self.selected_item:
            item_name = self.available_items[self.selected_item].get(
                "name", self.selected_item
            )

            embed.add_field(
                name="Selected Item",
                value=f"{item_name} (`{self.selected_item}`)",
                inline=False
            )

        embed.set_footer(
            text="Changes are saved only after Confirm."
        )

        return embed

    async def refresh_message(self):
        if self.message is not None:
            await self.message.edit(
                embed=self.construct_embed(),
                view=self
            )

    @discord.ui.button(
        label="Add Item",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def add_item_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select a merchant first.",
                ephemeral=True
            )

        if self.selected_item is None:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True
            )

        if self.selected_item in self.items:
            return await interaction.response.send_message(
                "This item is already in the merchant's inventory.",
                ephemeral=True
            )

        self.items.append(self.selected_item)

        await interaction.response.edit_message(
            embed=self.construct_embed(),
            view=self
        )

    @discord.ui.button(
        label="Remove Item",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def remove_item_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select a merchant first.",
                ephemeral=True
            )

        if self.selected_item is None:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True
            )

        if self.selected_item not in self.items:
            return await interaction.response.send_message(
                "This item isn't in the merchant's inventory.",
                ephemeral=True
            )

        self.items.remove(self.selected_item)
        self.selected_item = None

        await interaction.response.edit_message(
            embed=self.construct_embed(),
            view=self
        )

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.success,
        row=3
    )
    async def confirm_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select a merchant first.",
                ephemeral=True
            )

        try:
            save_npc_inventory(
                self.selected_npc,
                self.items
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save merchant inventory: `{e}`",
                ephemeral=True
            )

        self.stop()

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Merchant Inventory Saved!",
            description=(
                f"Inventory for `{self.selected_npc}` "
                "has been successfully updated."
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
        row=3
    )
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.stop()

        await interaction.response.edit_message(
            content="Merchant inventory editing cancelled.",
            embed=None,
            view=None
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


async def start_npc_merchant_editor(
    interaction: discord.Interaction
):
    view = NPCMerchantEditorView(interaction.user.id)

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
