
import json
import discord

from PoS.src.add.add_base_entity_stats import add_base_entity_stats


ENTITY_STATS_PATH = 'PoS/src/stats/entity_base_stats.json'


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise ValueError(f"{field_name} must be an integer.")


def load_entity_stats(kind: str) -> dict:
    with open(ENTITY_STATS_PATH, 'r') as f:
        stats = json.load(f)

    if kind not in stats:
        raise ValueError(f"Entity `{kind}` was not found.")

    entity = stats[kind]

    return {
        "kind": kind,
        "hp": entity["maxhp"],
        "attack": entity["atk"],
        "defense": entity["def"],
        "exp": entity.get("exp", 0),
        "regeneration": entity.get("regeneration", 0),
        "resistances": entity.get("resistances", {}).copy(),
        "min_lvl": entity.get("min_lvl", 1),
        "max_lvl": entity.get("max_lvl", 999),
        "spawn_rate_weight": entity.get("spawn_rate_weight", 10)
    }


class BasicStatsModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Entity — Basic Stats")
        self.creator_view = view

        data = view.entity_data

        self.kind = discord.ui.TextInput(
            label="Entity ID",
            placeholder="goblin_king",
            default=data["kind"] or None,
            max_length=100
        )

        self.hp = discord.ui.TextInput(
            label="Max HP",
            placeholder="200",
            default=str(data["hp"]) if data["hp"] is not None else None,
            max_length=10
        )

        self.attack = discord.ui.TextInput(
            label="Attack (ATK)",
            placeholder="15",
            default=str(data["attack"]) if data["attack"] is not None else None,
            max_length=10
        )

        self.defense = discord.ui.TextInput(
            label="Defense (DEF)",
            placeholder="5",
            default=str(data["defense"]) if data["defense"] is not None else None,
            max_length=10
        )

        self.exp = discord.ui.TextInput(
            label="Base EXP",
            placeholder="10",
            default=str(data["exp"]) if data["exp"] is not None else None,
            max_length=10
        )

        for item in (self.kind, self.hp, self.attack, self.defense, self.exp):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            kind = self.kind.value.strip()

            if not kind:
                raise ValueError("Entity ID cannot be empty.")

            # Do not allow changing the ID of an existing entity.
            if (
                self.creator_view.original_kind is not None
                and kind != self.creator_view.original_kind
            ):
                raise ValueError(
                    "Entity ID cannot be changed while editing an existing entity."
                )

            hp = parse_int(self.hp.value, "HP")
            attack = parse_int(self.attack.value, "Attack")
            defense = parse_int(self.defense.value, "Defense")
            exp = parse_int(self.exp.value, "EXP")

            if hp <= 0:
                raise ValueError("HP must be greater than zero.")

            if attack < 0 or defense < 0:
                raise ValueError("ATK and DEF cannot be negative.")

            if exp < 0:
                raise ValueError("EXP cannot be negative.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        data = self.creator_view.entity_data
        data["kind"] = kind
        data["hp"] = hp
        data["attack"] = attack
        data["defense"] = defense
        data["exp"] = exp

        await interaction.response.send_message(
            "Basic stats updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class LoadExistingEntityModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Load Existing Entity")
        self.creator_view = view

        self.kind = discord.ui.TextInput(
            label="Entity ID",
            placeholder="goblin",
            max_length=100
        )

        self.add_item(self.kind)

    async def on_submit(self, interaction: discord.Interaction):
        kind = self.kind.value.strip()

        if not kind:
            return await interaction.response.send_message(
                "Entity ID cannot be empty.",
                ephemeral=True
            )

        try:
            entity_data = load_entity_stats(kind)

        except FileNotFoundError:
            return await interaction.response.send_message(
                "Entity stats file was not found.",
                ephemeral=True
            )

        except json.JSONDecodeError:
            return await interaction.response.send_message(
                "Entity stats file contains invalid JSON.",
                ephemeral=True
            )

        except KeyError as e:
            return await interaction.response.send_message(
                f"Entity data is missing required field: `{e}`",
                ephemeral=True
            )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.creator_view.entity_data = entity_data
        self.creator_view.original_kind = kind

        await interaction.response.send_message(
            f"Entity `{kind}` loaded successfully. You can now edit its stats.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class SpawnSettingsModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Entity — Spawn Settings")
        self.creator_view = view

        data = view.entity_data

        self.min_lvl = discord.ui.TextInput(
            label="Minimum level",
            placeholder="1",
            default=str(data["min_lvl"]),
            max_length=10
        )

        self.max_lvl = discord.ui.TextInput(
            label="Maximum level",
            placeholder="999",
            default=str(data["max_lvl"]),
            max_length=10
        )

        self.spawn_weight = discord.ui.TextInput(
            label="Spawn rate weight",
            placeholder="10",
            default=str(data["spawn_rate_weight"]),
            max_length=10
        )

        self.add_item(self.min_lvl)
        self.add_item(self.max_lvl)
        self.add_item(self.spawn_weight)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            min_lvl = parse_int(self.min_lvl.value, "Minimum level")
            max_lvl = parse_int(self.max_lvl.value, "Maximum level")
            spawn_weight = parse_int(self.spawn_weight.value, "Spawn weight")

            if min_lvl < 1:
                raise ValueError("Minimum level must be at least 1.")

            if max_lvl < min_lvl:
                raise ValueError(
                    "Maximum level cannot be lower than minimum level."
                )

            if spawn_weight < 0:
                raise ValueError("Spawn weight cannot be negative.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        data = self.creator_view.entity_data
        data["min_lvl"] = min_lvl
        data["max_lvl"] = max_lvl
        data["spawn_rate_weight"] = spawn_weight

        await interaction.response.send_message(
            "Spawn settings updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class ResistanceModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Entity — Add Resistance")
        self.creator_view = view

        self.name = discord.ui.TextInput(
            label="Resistance name",
            placeholder="stun",
            max_length=50
        )

        self.value = discord.ui.TextInput(
            label="Resistance value",
            placeholder="50",
            max_length=10
        )

        self.add_item(self.name)
        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            name = self.name.value.strip()

            if not name:
                raise ValueError("Resistance name cannot be empty.")

            value = parse_int(self.value.value, "Resistance value")

            if value < 0:
                raise ValueError("Resistance cannot be negative.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.creator_view.entity_data["resistances"][name] = value

        await interaction.response.send_message(
            f"Resistance `{name}` set to `{value}`.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class RegenerationModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Entity — Regeneration")
        self.creator_view = view

        self.regeneration = discord.ui.TextInput(
            label="Regeneration (% of Max HP per tick)",
            placeholder="0",
            default=str(view.entity_data["regeneration"]),
            max_length=10
        )

        self.add_item(self.regeneration)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            regeneration = parse_int(
                self.regeneration.value,
                "Regeneration"
            )

            if regeneration < 0:
                raise ValueError("Regeneration cannot be negative.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.creator_view.entity_data["regeneration"] = regeneration

        await interaction.response.send_message(
            "Regeneration updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class EntityCreatorView(discord.ui.View):
    def __init__(self, author_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        # Original ID is set only when loading an existing entity.
        self.original_kind = None

        self.entity_data = {
            "kind": None,
            "hp": None,
            "attack": None,
            "defense": None,
            "exp": None,
            "regeneration": 0,
            "resistances": {},
            "min_lvl": 1,
            "max_lvl": 999,
            "spawn_rate_weight": 10
        }

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False

        return True

    def construct_embed(self) -> discord.Embed:
        data = self.entity_data

        title = "Path of Steel — Entity Creator"

        if self.original_kind is not None:
            title = "Path of Steel — Entity Editor"

        embed = discord.Embed(
            title=title,
            description="Configure your entity using the buttons below.",
            color=discord.Color.blurple()
        )

        # Basic stats
        if data["kind"] is None:
            basic_text = "Not configured"
        else:
            basic_text = (
                f"**ID:** `{data['kind']}`\n"
                f"**HP:** {data['hp']}\n"
                f"**ATK:** {data['attack']}\n"
                f"**DEF:** {data['defense']}\n"
                f"**EXP:** {data['exp']}\n"
                f"**Regeneration:** {data['regeneration']}% Max HP/tick"
            )

        embed.add_field(
            name="Basic Stats",
            value=basic_text,
            inline=False
        )

        # Spawn settings
        embed.add_field(
            name="Spawn Settings",
            value=(
                f"**Min level:** {data['min_lvl']}\n"
                f"**Max level:** {data['max_lvl']}\n"
                f"**Spawn weight:** {data['spawn_rate_weight']}"
            ),
            inline=False
        )

        # Resistances
        if data["resistances"]:
            resistance_text = "\n".join(
                f"**{name}:** {value}"
                for name, value in data["resistances"].items()
            )

            if len(resistance_text) > 1000:
                resistance_text = resistance_text[:997] + "..."
        else:
            resistance_text = "None"

        embed.add_field(
            name=f"Resistances ({len(data['resistances'])})",
            value=resistance_text,
            inline=False
        )

        if self.original_kind is not None:
            embed.set_footer(
                text=f"Editing existing entity: {self.original_kind}"
            )
        else:
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
        label="Basic Stats",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def basic_stats_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            BasicStatsModal(self)
        )

    @discord.ui.button(
        label="Spawn Settings",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def spawn_settings_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            SpawnSettingsModal(self)
        )

    @discord.ui.button(
        label="Load Existing Entity",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def load_existing_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            LoadExistingEntityModal(self)
        )

    @discord.ui.button(
        label="Add Resistance",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def resistance_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            ResistanceModal(self)
        )

    @discord.ui.button(
        label="Regeneration",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def regeneration_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            RegenerationModal(self)
        )

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def confirm_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        data = self.entity_data

        if data["kind"] is None:
            return await interaction.response.send_message(
                "Please configure Basic Stats first.",
                ephemeral=True
            )

        try:
            add_base_entity_stats(
                kind=data["kind"],
                hp=data["hp"],
                attack=data["attack"],
                defense=data["defense"],
                exp=data["exp"],
                resistances=data["resistances"],
                min_lvl=data["min_lvl"],
                max_lvl=data["max_lvl"],
                spawn_rate_weight=data["spawn_rate_weight"],
                regeneration=data["regeneration"]
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save entity: `{e}`",
                ephemeral=True
            )

        self.stop()

        action = "updated" if self.original_kind is not None else "added"

        embed = discord.Embed(
            title="Entity successfully saved!",
            description=(
                f"Entity `{data['kind']}` has been {action} in game data.\n\n"
                "What would you like to do next?"
            ),
            color=discord.Color.green()
        )

        view = EntitySavedView(
            author_id=self.author_id,
            entity_id=data["kind"]
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.stop()

        await interaction.response.edit_message(
            content="Entity editing cancelled.",
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


class EntitySavedView(discord.ui.View):
    def __init__(self, author_id: int, entity_id: str, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.entity_id = entity_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="Add Loot to Entity",
        style=discord.ButtonStyle.success
    )
    async def add_loot_button(self, interaction, button):
        from PoS.src.add.enemy_drops_creator import (
            start_enemy_drops_creator
        )

        await start_enemy_drops_creator(
            interaction,
            enemy=self.entity_id
        )

    @discord.ui.button(
        label="Create Another Entity",
        style=discord.ButtonStyle.primary
    )
    async def create_another_button(self, interaction, button):
        view = EntityCreatorView(self.author_id)

        await interaction.response.edit_message(
            embed=view.construct_embed(),
            view=view
        )

        view.message = interaction.message

    @discord.ui.button(
        label="Add Skills to Entity",
        style=discord.ButtonStyle.success
    )
    async def add_skills_button(self, interaction, button):
        from PoS.src.add.enemy_skills_creator import (
            start_enemy_skills_creator
        )

        await start_enemy_skills_creator(
            interaction,
            enemy=self.entity_id
        )

    @discord.ui.button(
        label="Finish",
        style=discord.ButtonStyle.secondary
    )
    async def finish_button(self, interaction, button):
        self.stop()

        await interaction.response.edit_message(view=None)


async def start_entity_creator(interaction: discord.Interaction):
    view = EntityCreatorView(interaction.user.id)

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
