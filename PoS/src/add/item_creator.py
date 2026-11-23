
import discord
import json

from PoS.src.add.add_item_data import add_item_data
from PoS.src.add.item_additional_data import open_item_additional_data


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise ValueError(f"{field_name} must be an integer.")


def parse_json_dict(value: str, field_name: str) -> dict:
    try:
        result = json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"{field_name}: invalid JSON ({e.msg}).")

    if not isinstance(result, dict):
        raise ValueError(f"{field_name} must be a JSON object.")

    return result


class BasicItemInfoModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Item — Basic Information")
        self.creator_view = view
        data = view.item_data

        self.item_id = discord.ui.TextInput(
            label="Item ID",
            placeholder="small_healing_potion",
            default=data["item_id"] or None,
            max_length=100
        )

        self.name = discord.ui.TextInput(
            label="Item name",
            placeholder="Small healing potion",
            default=data["name"] or None,
            max_length=100
        )

        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="A healing potion. Recovers 50 HP.",
            default=data["description"] or None,
            style=discord.TextStyle.paragraph,
            max_length=1000
        )

        self.price = discord.ui.TextInput(
            label="Merchant price",
            placeholder="5",
            default=str(data["price"]),
            max_length=10
        )

        for item in (
            self.item_id,
            self.name,
            self.description,
            self.price
        ):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            item_id = self.item_id.value.strip()
            name = self.name.value.strip()
            description = self.description.value.strip()
            price = parse_int(self.price.value, "Merchant price")

            if not item_id:
                raise ValueError("Item ID cannot be empty.")

            if not name:
                raise ValueError("Item name cannot be empty.")

            if price < 0:
                raise ValueError("Merchant price cannot be negative.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        data = self.creator_view.item_data
        data["item_id"] = item_id
        data["name"] = name
        data["description"] = description
        data["price"] = price

        await interaction.response.send_message(
            "Basic item information updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class ConsumableEffectsModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Item — Consumable Effects")
        self.creator_view = view

        self.effects = discord.ui.TextInput(
            label="Consumable effects (JSON)",
            placeholder='{"hp": 50, "mp": 20}',
            default=json.dumps(
                view.item_data["consumable_effects"],
                ensure_ascii=False
            ),
            style=discord.TextStyle.paragraph,
            max_length=4000
        )

        self.add_item(self.effects)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            effects = parse_json_dict(
                self.effects.value,
                "Consumable effects"
            )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.creator_view.item_data["consumable_effects"] = effects

        await interaction.response.send_message(
            "Consumable effects updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class EquipmentInfoModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Item — Equipment Info")
        self.creator_view = view

        self.info = discord.ui.TextInput(
            label="Equipment information (JSON)",
            placeholder='{"type": "weapon", "atk": 15}',
            default=json.dumps(
                view.item_data["equipment_info"],
                ensure_ascii=False
            ),
            style=discord.TextStyle.paragraph,
            max_length=4000
        )

        self.add_item(self.info)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            info = parse_json_dict(
                self.info.value,
                "Equipment information"
            )

            if info and not info.get("type"):
                raise ValueError(
                    'Equipment information must contain a "type" field.'
                )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.creator_view.item_data["equipment_info"] = info

        await interaction.response.send_message(
            "Equipment information updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class ItemTypeSelect(discord.ui.Select):
    def __init__(self, view):
        self.creator_view = view

        super().__init__(
            placeholder="Select item type...",
            min_values=1,
            max_values=1,
            row=0,
            options=[
                discord.SelectOption(
                    label="Material",
                    value="material",
                    description="Crafting materials and resources."
                ),
                discord.SelectOption(
                    label="Consumable",
                    value="consumable",
                    description="Items that apply effects when used."
                ),
                discord.SelectOption(
                    label="Equipment",
                    value="equipment",
                    description="Weapons, armor and other equipment."
                )
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        self.creator_view.item_data["type"] = self.values[0]

        await interaction.response.edit_message(
            embed=self.creator_view.construct_embed(),
            view=self.creator_view
        )


class ItemCreatorView(discord.ui.View):
    def __init__(self, author_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        self.item_data = {
            "item_id": None,
            "name": None,
            "type": None,
            "description": None,
            "consumable_effects": {},
            "equipment_info": {},
            "price": 1
        }

        self.add_item(ItemTypeSelect(self))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False

        return True

    def construct_embed(self) -> discord.Embed:
        data = self.item_data

        embed = discord.Embed(
            title="Path of Steel — Item Creator",
            description="Configure your item using the controls below.",
            color=discord.Color.blurple()
        )

        # Basic information
        if data["item_id"] is None:
            basic_text = "Not configured"
        else:
            basic_text = (
                f"**ID:** `{data['item_id']}`\n"
                f"**Name:** {data['name']}\n"
                f"**Description:** {data['description'] or 'None'}\n"
                f"**Merchant price:** {data['price']}"
            )

        embed.add_field(
            name="Basic Information",
            value=basic_text[:1024],
            inline=False
        )

        # Item type
        embed.add_field(
            name="Item Type",
            value=data["type"] or "Not selected",
            inline=False
        )

        # Additional data
        if data["type"] == "consumable":
            extra = json.dumps(
                data["consumable_effects"],
                ensure_ascii=False,
                indent=2
            )

            embed.add_field(
                name="Consumable Effects",
                value=f"```json\n{extra[:1000]}\n```",
                inline=False
            )

        elif data["type"] == "equipment":
            extra = json.dumps(
                data["equipment_info"],
                ensure_ascii=False,
                indent=2
            )

            embed.add_field(
                name="Equipment Info",
                value=f"```json\n{extra[:1000]}\n```",
                inline=False
            )

        embed.set_footer(
            text="Changes are not saved until you press Confirm."
        )

        return embed

    async def refresh_message(self):
        if self.message is not None:
            await self.message.edit(
                embed=self.construct_embed(),
                view=self
            )

    @discord.ui.button(
        label="Basic Info",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def basic_info_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            BasicItemInfoModal(self)
        )

    @discord.ui.button(
        label="Additional Data",
        style=discord.ButtonStyle.primary,
        row=2
    )
    async def additional_data_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.item_data["type"] == "material":
            return await interaction.response.send_message(
                "Materials don't have additional data.",
                ephemeral=True
            )

        if self.item_data["type"] is None:
            return await interaction.response.send_message(
                "Select item type first.",
                ephemeral=True
            )

        await open_item_additional_data(interaction, self)

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
        data = self.item_data

        if not data["item_id"] or not data["name"]:
            return await interaction.response.send_message(
                "Please configure Basic Information first.",
                ephemeral=True
            )

        if data["type"] not in ("material", "consumable", "equipment"):
            return await interaction.response.send_message(
                "Please select an item type.",
                ephemeral=True
            )

        if (
            data["type"] == "equipment"
            and not data["equipment_info"].get("type")
        ):
            return await interaction.response.send_message(
                "Please configure Equipment Info first.",
                ephemeral=True
            )

        try:
            add_item_data(
                item_id=data["item_id"],
                name=data["name"],
                type=data["type"],
                description=data["description"],
                consumable_effects=data["consumable_effects"],
                equipment_info=data["equipment_info"],
                price=data["price"]
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save item: `{e}`",
                ephemeral=True
            )

        self.stop()

        embed = discord.Embed(
            title="Item successfully saved!",
            description=f"Item `{data['item_id']}` has been added to game data.",
            color=discord.Color.green()
        )

        view = ItemSavedView(self.author_id)
        view.message = interaction.message

        await interaction.response.edit_message(
            embed=embed,
            view=view
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
            content="Item creation cancelled.",
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

class ItemSavedView(discord.ui.View):
    def __init__(self, author_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.message = None

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(
        label="Add Another Item",
        style=discord.ButtonStyle.success
    )
    async def add_another_button(self, interaction, button):
        view = ItemCreatorView(self.author_id)

        await interaction.response.edit_message(
            embed=view.construct_embed(),
            view=view
        )

        view.message = interaction.message

    @discord.ui.button(
        label="Finish",
        style=discord.ButtonStyle.secondary
    )
    async def finish_button(self, interaction, button):
        self.stop()
        await interaction.response.edit_message(view=None)

async def start_item_creator(interaction: discord.Interaction):
    view = ItemCreatorView(interaction.user.id)

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
