
import discord

from PoS.src.add.key_value_editor import (
    open_key_value_editor
)


class EquipmentTypeSelect(discord.ui.Select):
    def __init__(self, view):
        self.parent_view = view

        current_type = view.item_data["equipment_info"].get("type")

        options = [
            discord.SelectOption(
                label="Weapon",
                value="weapon",
                default=current_type == "weapon"
            ),
            discord.SelectOption(
                label="Armor",
                value="armor",
                default=current_type == "armor"
            ),
            discord.SelectOption(
                label="Special",
                value="special",
                description="Rings, accessories and other special equipment.",
                default=current_type == "special"
            )
        ]

        super().__init__(
            placeholder="Select equipment type...",
            options=options,
            min_values=1,
            max_values=1,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.item_data["equipment_info"]["type"] = self.values[0]

        await interaction.response.edit_message(
            embed=self.parent_view.construct_embed(),
            view=self.parent_view
        )


class ItemAdditionalDataView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        item_data: dict,
        parent_view: discord.ui.View,
        timeout: float = 300
    ):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.item_data = item_data
        self.parent_view = parent_view
        self.message = None

        if item_data["type"] == "equipment":
            self.add_item(EquipmentTypeSelect(self))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False

        return True

    def construct_embed(self):
        data = self.item_data

        embed = discord.Embed(
            title="Item — Additional Data",
            description=f"Configure additional data for **{data['name'] or data['item_id'] or 'New item'}**.",
            color=discord.Color.blurple()
        )

        if data["type"] == "consumable":
            effects = data["consumable_effects"]

            text = (
                "\n".join(
                    f"**{key}:** `{value}`"
                    for key, value in effects.items()
                )
                if effects else "No effects configured."
            )

            embed.add_field(
                name="Consumable Effects",
                value=text[:1024],
                inline=False
            )

        elif data["type"] == "equipment":
            info = data["equipment_info"]

            embed.add_field(
                name="Equipment Type",
                value=info.get("type", "Not selected"),
                inline=False
            )

            stats = {
                key: value
                for key, value in info.items()
                if key not in ("type", "resistance")
            }

            stats_text = (
                "\n".join(
                    f"**{key}:** `{value}`"
                    for key, value in stats.items()
                )
                if stats else "No equipment stats configured."
            )

            embed.add_field(
                name="Equipment Stats",
                value=stats_text[:1024],
                inline=False
            )

            resistances = info.get("resistance", {})

            resistance_text = (
                "\n".join(
                    f"**{key}:** `{value}`"
                    for key, value in resistances.items()
                )
                if resistances else "No resistances configured."
            )

            embed.add_field(
                name="Resistances",
                value=resistance_text[:1024],
                inline=False
            )

        else:
            embed.description = "Materials have no additional data."

        return embed

    @discord.ui.button(
        label="Edit Effects",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def edit_effects_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.item_data["type"] != "consumable":
            return await interaction.response.send_message(
                "This option is only available for consumables.",
                ephemeral=True
            )

        await open_key_value_editor(
            interaction=interaction,
            data=self.item_data["consumable_effects"],
            title="Consumable Effects",
            parent_view=self
        )

    @discord.ui.button(
        label="Edit Equipment Stats",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def edit_equipment_stats_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.item_data["type"] != "equipment":
            return await interaction.response.send_message(
                "This option is only available for equipment.",
                ephemeral=True
            )

        if not self.item_data["equipment_info"].get("type"):
            return await interaction.response.send_message(
                "Select Weapon or Armor first.",
                ephemeral=True
            )

        await open_key_value_editor(
            interaction=interaction,
            data=self.item_data["equipment_info"],
            title="Equipment Stats",
            parent_view=self,
            protected_keys={"type", "resistance"}
        )

    @discord.ui.button(
        label="Edit Resistances",
        style=discord.ButtonStyle.primary,
        row=2
    )
    async def edit_resistances_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.item_data["type"] != "equipment":
            return await interaction.response.send_message(
                "This option is only available for equipment.",
                ephemeral=True
            )

        if not self.item_data["equipment_info"].get("type"):
            return await interaction.response.send_message(
                "Select Weapon or Armor first.",
                ephemeral=True
            )

        resistances = self.item_data["equipment_info"].setdefault(
            "resistance", {}
        )

        await open_key_value_editor(
            interaction=interaction,
            data=resistances,
            title="Equipment Resistances",
            parent_view=self
        )

    @discord.ui.button(
        label="Back",
        style=discord.ButtonStyle.secondary,
        row=3
    )
    async def back_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.stop()

        await interaction.response.edit_message(
            embed=self.parent_view.construct_embed(),
            view=self.parent_view
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


async def open_item_additional_data(
    interaction: discord.Interaction,
    parent_view
):
    view = ItemAdditionalDataView(
        author_id=interaction.user.id,
        item_data=parent_view.item_data,
        parent_view=parent_view
    )

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
