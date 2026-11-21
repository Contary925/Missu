import discord

from PoS.src.add.add_base_entity_stats import add_base_entity_stats


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise ValueError(f"{field_name} must be an integer.")


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

        for item in (self.kind, self.hp, self.attack, self.defense):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            kind = self.kind.value.strip()
            if not kind:
                raise ValueError("Entity ID cannot be empty.")

            hp = parse_int(self.hp.value, "HP")
            attack = parse_int(self.attack.value, "Attack")
            defense = parse_int(self.defense.value, "Defense")

            if hp <= 0:
                raise ValueError("HP must be greater than zero.")

            if attack < 0 or defense < 0:
                raise ValueError("ATK and DEF cannot be negative.")

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

        await interaction.response.send_message(
            "Basic stats updated.",
            ephemeral=True
        )

        await self.creator_view.refresh_message()


class SpawnSettingsModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Entity — Spawn Settings")
        self.creator_view = view

        data = view.entity_data

        self.min_level = discord.ui.TextInput(
            label="Minimum level",
            placeholder="1",
            default=str(data["min_level"]),
            max_length=10
        )

        self.max_level = discord.ui.TextInput(
            label="Maximum level",
            placeholder="999",
            default=str(data["max_level"]),
            max_length=10
        )

        self.spawn_weight = discord.ui.TextInput(
            label="Spawn rate weight",
            placeholder="10",
            default=str(data["spawn_rate_weight"]),
            max_length=10
        )

        self.add_item(self.min_level)
        self.add_item(self.max_level)
        self.add_item(self.spawn_weight)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            min_level = parse_int(self.min_level.value, "Minimum level")
            max_level = parse_int(self.max_level.value, "Maximum level")
            spawn_weight = parse_int(self.spawn_weight.value, "Spawn weight")

            if min_level < 1:
                raise ValueError("Minimum level must be at least 1.")

            if max_level < min_level:
                raise ValueError("Maximum level cannot be lower than minimum level.")

            if spawn_weight < 0:
                raise ValueError("Spawn weight cannot be negative.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        data = self.creator_view.entity_data
        data["min_level"] = min_level
        data["max_level"] = max_level
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


class EntityCreatorView(discord.ui.View):
    def __init__(self, author_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        self.entity_data = {
            "kind": None,
            "hp": None,
            "attack": None,
            "defense": None,
            "resistances": {},
            "min_level": 1,
            "max_level": 999,
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

        embed = discord.Embed(
            title="Path of Steel — Entity Creator",
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
                f"**DEF:** {data['defense']}"
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
                f"**Min level:** {data['min_level']}\n"
                f"**Max level:** {data['max_level']}\n"
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
                data["kind"],
                data["hp"],
                data["attack"],
                data["defense"],
                data["resistances"],
                data["min_level"],
                data["max_level"],
                data["spawn_rate_weight"]
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save entity: `{e}`",
                ephemeral=True
            )

        self.stop()

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Entity successfully saved!",
            description=f"Entity `{data['kind']}` has been added to game data.",
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
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
            content="Entity creation cancelled.",
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


async def start_entity_creator(interaction: discord.Interaction):
    view = EntityCreatorView(interaction.user.id)

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message