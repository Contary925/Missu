
import copy
import json
import discord

from pathlib import Path
from PoS.src.add.add_enemy_skills import save_enemy_skills


ENTITY_PATH = Path("PoS/src/stats/entity_base_stats.json")
SKILLS_PATH = Path("PoS/src/skills/enemy_skills.json")
SKILL_DATA_PATH = Path("PoS/src/skills/skill_data.json")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class SkillChanceModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Configure Enemy Skill")
        self.editor = view

        current = view.skills.get(view.selected_skill, 0)

        self.chance = discord.ui.TextInput(
            label="Skill usage probability (%)",
            placeholder="50",
            default=str(current),
            max_length=3
        )

        self.add_item(self.chance)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            chance = int(self.chance.value.strip())

            if not 0 <= chance <= 100:
                raise ValueError(
                    "Probability must be between 0 and 100."
                )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        self.editor.skills[self.editor.selected_skill] = chance

        await interaction.response.send_message(
            f"Probability for `{self.editor.selected_skill}` "
            f"set to `{chance}%`.",
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
                description="Enemy skill configuration",
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
        self.editor.skills = copy.deepcopy(
            self.editor.original_skills.get(enemy, {})
        )
        self.editor.selected_skill = None

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class SkillSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label=skill[:100],
                value=skill,
                description=data.get("description", "Enemy skill")[:100],
                default=skill == view.selected_skill
            )
            for skill, data in view.available_skills.items()
        ]

        super().__init__(
            placeholder="Select skill...",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        self.editor.selected_skill = self.values[0]

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class EnemySkillsCreatorView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        selected_enemy: str = None,
        timeout: float = 300
    ):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        self.enemies = [
            enemy
            for enemy in load_json(ENTITY_PATH)
            if enemy != "player"
        ]

        self.original_skills = load_json(SKILLS_PATH)
        self.available_skills = load_json(SKILL_DATA_PATH)
        if len(self.available_skills) > 25:
            raise ValueError(
                "More than 25 available skills. Select pagination is required."
            )

        self.selected_enemy = selected_enemy
        self.selected_skill = None

        self.skills = copy.deepcopy(
            self.original_skills.get(selected_enemy, {})
        ) if selected_enemy else {}

        if not self.enemies:
            raise ValueError("No enemies found.")

        if len(self.enemies) > 25:
            raise ValueError(
                "More than 25 enemies. Select pagination is required."
            )

        self.add_item(EnemySelect(self))
        self.add_item(SkillSelect(self))

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
            title="Path of Steel — Enemy Skills Editor",
            color=discord.Color.blurple()
        )

        if self.selected_enemy is None:
            embed.description = "Select an enemy to manage its skills."
            return embed

        embed.description = f"**Enemy:** `{self.selected_enemy}`"

        if self.skills:
            lines = [
                f"**{skill}:** {chance}%"
                for skill, chance in self.skills.items()
            ]

            embed.add_field(
                name=f"Current Skills ({len(self.skills)})",
                value="\n".join(lines),
                inline=False
            )
        else:
            embed.add_field(
                name="Current Skills",
                value="No skills configured.",
                inline=False
            )

        if self.selected_skill:
            embed.add_field(
                name="Selected Skill",
                value=f"`{self.selected_skill}`",
                inline=False
            )

        total = sum(self.skills.values())

        embed.add_field(
            name="Total Probability",
            value=f"{total}%",
            inline=False
        )

        embed.set_footer(
            text="Total probability must equal 100% before saving."
        )

        return embed

    async def refresh_message(self):
        if self.message is not None:
            await self.message.edit(
                embed=self.construct_embed(),
                view=self
            )

    @discord.ui.button(
        label="Add / Edit Skill",
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

        if self.selected_skill is None:
            return await interaction.response.send_message(
                "Select a skill first.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            SkillChanceModal(self)
        )

    @discord.ui.button(
        label="Remove Skill",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def remove_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_skill is None:
            return await interaction.response.send_message(
                "Select a skill first.",
                ephemeral=True
            )

        if self.selected_skill not in self.skills:
            return await interaction.response.send_message(
                "This skill isn't configured for the selected enemy.",
                ephemeral=True
            )

        self.skills.pop(self.selected_skill)
        self.selected_skill = None

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

        total = sum(self.skills.values())

        if total != 100:
            return await interaction.response.send_message(
                f"Total probability must equal 100%. "
                f"Current total: {total}%.",
                ephemeral=True
            )

        try:
            save_enemy_skills(
                self.selected_enemy,
                self.skills
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save enemy skills: `{e}`",
                ephemeral=True
            )

        self.stop()

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Enemy Skills Saved!",
            description=(
                f"Skill configuration for `{self.selected_enemy}` "
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
            content="Enemy skills editing cancelled.",
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


async def start_enemy_skills_creator(
    interaction: discord.Interaction,
    enemy: str = None
):
    view = EnemySkillsCreatorView(
        interaction.user.id,
        selected_enemy=enemy
    )

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
