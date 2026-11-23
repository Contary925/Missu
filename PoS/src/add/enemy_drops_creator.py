
import copy
import json
import discord

from pathlib import Path
from PoS.src.add.add_enemy_drops import save_enemy_loot_table


ENTITY_PATH = Path("PoS/src/stats/entity_base_stats.json")
ITEM_PATH = Path("PoS/src/items/item_data.json")
LOOT_PATH = Path("PoS/src/stats/loot_tables.json")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class DropSettingsModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Configure Enemy Drop")
        self.editor = view

        item_id = view.selected_item
        current = view.drops.get(item_id, {})

        self.chance = discord.ui.TextInput(
            label="Drop chance (%)",
            placeholder="50",
            default=str(current.get("chance", 50)),
            max_length=3
        )

        self.min_qty = discord.ui.TextInput(
            label="Minimum quantity",
            placeholder="1",
            default=str(current.get("min_qty", 1)),
            max_length=10
        )

        self.max_qty = discord.ui.TextInput(
            label="Maximum quantity",
            placeholder="3",
            default=str(current.get("max_qty", 1)),
            max_length=10
        )

        self.add_item(self.chance)
        self.add_item(self.min_qty)
        self.add_item(self.max_qty)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            chance = int(self.chance.value.strip())
            min_qty = int(self.min_qty.value.strip())
            max_qty = int(self.max_qty.value.strip())

            if not 0 <= chance <= 100:
                raise ValueError("Chance must be between 0 and 100.")

            if min_qty < 1:
                raise ValueError("Minimum quantity must be at least 1.")

            if max_qty < min_qty:
                raise ValueError(
                    "Maximum quantity cannot be lower than minimum quantity."
                )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.editor.drops[self.editor.selected_item] = {
            "chance": chance,
            "min_qty": min_qty,
            "max_qty": max_qty
        }

        await interaction.response.send_message(
            f"Drop settings for `{self.editor.selected_item}` updated.",
            ephemeral=True
        )

        await self.editor.refresh_message()


class EnemySelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label=enemy[:100],
                value=enemy,
                description="Enemy loot table",
                default=enemy == view.selected_enemy
            )
            for enemy in view.enemies
        ]

        super().__init__(
            placeholder="Select enemy...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        enemy = self.values[0]

        self.editor.selected_enemy = enemy
        self.editor.drops = copy.deepcopy(
            self.editor.original_loot.get(enemy, {})
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
            for item_id, item in view.items.items()
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


class EnemyDropsCreatorView(discord.ui.View):
    def __init__(self, author_id: int, selected_enemy: str = None, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        self.enemies = [
            enemy
            for enemy in load_json(ENTITY_PATH)
            if enemy != "player"
        ]

        self.items = load_json(ITEM_PATH)
        self.original_loot = load_json(LOOT_PATH)

        self.selected_enemy = selected_enemy
        self.selected_item = None

        self.drops = copy.deepcopy(
            self.original_loot.get(selected_enemy, {})
        ) if selected_enemy else {}

        if not self.enemies:
            raise ValueError("No enemies found.")

        if len(self.enemies) > 25:
            raise ValueError(
                "More than 25 enemies. Select pagination is required."
            )

        if len(self.items) > 25:
            raise ValueError(
                "More than 25 items. Select pagination is required."
            )

        self.add_item(EnemySelect(self))
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
            title="Path of Steel — Loot Table Editor",
            color=discord.Color.blurple()
        )

        if self.selected_enemy is None:
            embed.description = "Select an enemy to manage its loot table."
            return embed

        embed.description = f"**Enemy:** `{self.selected_enemy}`"

        if self.drops:
            lines = []

            for item_id, data in self.drops.items():
                item_name = self.items.get(
                    item_id, {}
                ).get("name", item_id)

                selected = (
                    " ◀"
                    if item_id == self.selected_item
                    else ""
                )

                lines.append(
                    f"**{item_name}** (`{item_id}`){selected}\n"
                    f"Chance: {data['chance']}% | "
                    f"Quantity: {data['min_qty']}–{data['max_qty']}"
                )

            description = "\n\n".join(lines)

            if len(description) > 4000:
                description = description[:3997] + "..."

            embed.add_field(
                name=f"Current Drops ({len(self.drops)})",
                value=description,
                inline=False
            )
        else:
            embed.add_field(
                name="Current Drops",
                value="No drops configured.",
                inline=False
            )

        if self.selected_item:
            item_name = self.items[self.selected_item].get(
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
        label="Add / Edit Drop",
        style=discord.ButtonStyle.primary,
        row=2
    )
    async def configure_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_enemy is None:
            return await interaction.response.send_message(
                "Select an enemy first.",
                ephemeral=True
            )

        if self.selected_item is None:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            DropSettingsModal(self)
        )

    @discord.ui.button(
        label="Remove Drop",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def remove_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_item is None:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True
            )

        if self.selected_item not in self.drops:
            return await interaction.response.send_message(
                "This item isn't in the selected enemy's loot table.",
                ephemeral=True
            )

        self.drops.pop(self.selected_item)
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
        if self.selected_enemy is None:
            return await interaction.response.send_message(
                "Select an enemy first.",
                ephemeral=True
            )

        try:
            save_enemy_loot_table(
                self.selected_enemy,
                self.drops
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save loot table: `{e}`",
                ephemeral=True
            )

        self.stop()

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Loot Table Saved!",
            description=(
                f"Loot table for `{self.selected_enemy}` "
                f"has been successfully updated."
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
            content="Loot table editing cancelled.",
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


async def start_enemy_drops_creator(
    interaction: discord.Interaction,
    enemy: str = None
):
    view = EnemyDropsCreatorView(
        interaction.user.id,
        selected_enemy=enemy
    )

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
