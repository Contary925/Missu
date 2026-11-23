
import json
import discord

from pathlib import Path
from PoS.src.add.add_quest import add_quest


NPC_PATH = Path("PoS/src/NPC/npc_info.json")
QUEST_PATH = Path("PoS/src/quests/quests.json")
ENTITY_PATH = Path("PoS/src/stats/entity_base_stats.json")
ITEM_PATH = Path("PoS/src/items/item_data.json")
SKILL_DATA_PATH = Path("PoS/src/skills/skill_data.json")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise ValueError(f"{field_name} must be an integer.")


# ============================================================
# BASIC INFO
# ============================================================

class QuestBasicInfoModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Quest — Basic Info")
        self.editor = view

        data = view.quest_data

        self.quest_id = discord.ui.TextInput(
            label="Quest ID",
            placeholder="goblin hunter",
            default=data["quest_id"] or None,
            max_length=100
        )

        self.min_level = discord.ui.TextInput(
            label="Minimum level",
            placeholder="1",
            default=str(data["conditions"]["min_level"]),
            max_length=10
        )

        self.max_level = discord.ui.TextInput(
            label="Maximum level",
            placeholder="10",
            default=str(data["conditions"]["max_level"]),
            max_length=10
        )

        self.repeatable = discord.ui.TextInput(
            label="Repeatable (0 or 1)",
            placeholder="0",
            default=str(data["repeatable"]),
            max_length=1
        )

        for item in (
            self.quest_id,
            self.min_level,
            self.max_level,
            self.repeatable
        ):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            quest_id = self.quest_id.value.strip()

            if not quest_id:
                raise ValueError("Quest ID cannot be empty.")

            min_level = parse_int(
                self.min_level.value, "Minimum level"
            )
            max_level = parse_int(
                self.max_level.value, "Maximum level"
            )
            repeatable = parse_int(
                self.repeatable.value, "Repeatable"
            )

            if min_level < 1:
                raise ValueError("Minimum level must be at least 1.")

            if max_level < min_level:
                raise ValueError(
                    "Maximum level cannot be lower than minimum level."
                )

            if repeatable not in (0, 1):
                raise ValueError("Repeatable must be 0 or 1.")

            existing = self.editor.original_quests.get(
                self.editor.selected_npc, {}
            )

            if quest_id in existing:
                raise ValueError(
                    "A quest with this ID already exists for this NPC."
                )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        data = self.editor.quest_data

        data["quest_id"] = quest_id
        data["conditions"]["min_level"] = min_level
        data["conditions"]["max_level"] = max_level
        data["repeatable"] = repeatable

        await interaction.response.send_message(
            "Quest basic information updated.",
            ephemeral=True
        )

        await self.editor.refresh_message()


# ============================================================
# OBJECTIVES
# ============================================================

class ObjectiveQuantityModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Configure Quest Objective")
        self.editor = view

        objective_type = view.selected_objective_type
        target = view.selected_target

        current = view.quest_data["objectives"].get(
            objective_type, {}
        ).get(target, 1)

        self.quantity = discord.ui.TextInput(
            label="Required quantity",
            placeholder="10",
            default=str(current),
            max_length=10
        )

        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            quantity = parse_int(
                self.quantity.value,
                "Required quantity"
            )

            if quantity < 1:
                raise ValueError(
                    "Required quantity must be at least 1."
                )

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        objective_type = self.editor.selected_objective_type
        target = self.editor.selected_target

        objectives = self.editor.quest_data["objectives"]
        objectives.setdefault(objective_type, {})
        objectives[objective_type][target] = quantity

        await interaction.response.send_message(
            f"Objective `{objective_type}: {target}` "
            f"set to `{quantity}`.",
            ephemeral=True
        )

        await self.editor.refresh_message()


class ObjectiveTypeSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label="Kill",
                value="kill",
                description="Defeat a specific enemy.",
                default=view.selected_objective_type == "kill"
            ),
            discord.SelectOption(
                label="Collect",
                value="collect",
                description="Collect a specific item.",
                default=view.selected_objective_type == "collect"
            )
        ]

        super().__init__(
            placeholder="Select objective type...",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        self.editor.selected_objective_type = self.values[0]
        self.editor.selected_target = None
        self.editor.refresh_target_select()

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class ObjectiveTargetSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        if view.selected_objective_type == "kill":
            targets = view.entities
        else:
            targets = view.items

        options = [
            discord.SelectOption(
                label=target[:100],
                value=target,
                description=(
                    view.items[target].get("name", target)[:100]
                    if view.selected_objective_type == "collect"
                    else "Enemy"
                ),
                default=target == view.selected_target
            )
            for target in targets
        ]

        super().__init__(
            placeholder="Select objective target...",
            min_values=1,
            max_values=1,
            options=options,
            row=2
        )

    async def callback(self, interaction: discord.Interaction):
        self.editor.selected_target = self.values[0]

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


# ============================================================
# REWARDS
# ============================================================

class RewardValueModal(discord.ui.Modal):
    def __init__(self, view, reward_type: str):
        super().__init__(title="Configure Quest Reward")
        self.editor = view
        self.reward_type = reward_type

        if reward_type == "EXP":
            current = view.parent_view.quest_data["rewards"].get(
                "EXP", 0
            )
            label = "EXP reward"
            placeholder = "100"
        else:
            current = view.parent_view.quest_data["rewards"].get(
                "items", {}
            ).get(view.selected_target, 1)
            label = "Item quantity"
            placeholder = "10"

        self.value = discord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            default=str(current),
            max_length=10
        )

        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            value = parse_int(self.value.value, "Reward value")

            if value < 0:
                raise ValueError("Reward value cannot be negative.")

            if self.reward_type == "items" and value < 1:
                raise ValueError("Item quantity must be at least 1.")

        except ValueError as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        rewards = self.editor.parent_view.quest_data["rewards"]

        if self.reward_type == "EXP":
            rewards["EXP"] = value
        else:
            rewards.setdefault("items", {})
            rewards["items"][self.editor.selected_target] = value

        await interaction.response.send_message(
            "Reward updated.",
            ephemeral=True
        )

        await self.editor.refresh_message()


class RewardTypeSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label="EXP",
                value="EXP",
                description="Experience points"
            ),
            discord.SelectOption(
                label="Items",
                value="items",
                description="Items and their quantities"
            ),
            discord.SelectOption(
                label="Skills",
                value="skills",
                description="Unlock skills"
            )
        ]

        super().__init__(
            placeholder="Select reward type...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        self.editor.selected_reward_type = self.values[0]
        self.editor.selected_target = None
        self.editor.refresh_target_select()

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class RewardTargetSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view
        reward_type = view.selected_reward_type

        if reward_type == "items":
            targets = view.available_items
        else:
            targets = view.available_skills

        options = [
            discord.SelectOption(
                label=target[:100],
                value=target,
                description=(
                    targets[target].get("name", target)[:100]
                    if reward_type == "items"
                    else targets[target].get(
                        "description", "Skill"
                    )[:100]
                ),
                default=target == view.selected_target
            )
            for target in targets
        ]

        super().__init__(
            placeholder="Select reward...",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        self.editor.selected_target = self.values[0]

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class RewardEditorView(discord.ui.View):
    def __init__(self, parent_view, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.parent_view = parent_view
        self.message = parent_view.message

        self.available_items = load_json(ITEM_PATH)
        self.available_skills = load_json(SKILL_DATA_PATH)

        self.selected_reward_type = "EXP"
        self.selected_target = None

        if len(self.available_items) > 25:
            raise ValueError(
                "More than 25 items. Select pagination is required."
            )

        if len(self.available_skills) > 25:
            raise ValueError(
                "More than 25 skills. Select pagination is required."
            )

        self.add_item(RewardTypeSelect(self))

        self.target_select = None
        self.refresh_target_select()

    def refresh_target_select(self):
        if self.target_select is not None:
            self.remove_item(self.target_select)
            self.target_select = None

        if self.selected_reward_type in ("items", "skills"):
            self.target_select = RewardTargetSelect(self)
            self.add_item(self.target_select)

    async def interaction_check(self, interaction: discord.Interaction):
        return await self.parent_view.interaction_check(interaction)

    def construct_embed(self):
        embed = discord.Embed(
            title="Path of Steel — Reward Editor",
            description=(
                f"**NPC:** `{self.parent_view.selected_npc}`\n"
                f"**Quest:** "
                f"`{self.parent_view.quest_data['quest_id'] or 'Not configured'}`"
            ),
            color=discord.Color.blurple()
        )

        rewards = self.parent_view.quest_data["rewards"]

        embed.add_field(
            name="EXP",
            value=str(rewards.get("EXP", 0)),
            inline=False
        )

        items = rewards.get("items", {})

        item_text = (
            "\n".join(
                f"`{item_id}` × {quantity}"
                for item_id, quantity in items.items()
            )
            if items else "None"
        )

        embed.add_field(
            name=f"Items ({len(items)})",
            value=item_text,
            inline=False
        )

        skills = rewards.get("skills", [])

        embed.add_field(
            name=f"Skills ({len(skills)})",
            value="\n".join(
                f"`{skill}`" for skill in skills
            ) or "None",
            inline=False
        )

        if self.selected_target:
            embed.add_field(
                name="Selected Reward",
                value=f"`{self.selected_target}`",
                inline=False
            )

        embed.set_footer(
            text="Changes are stored in the quest draft."
        )

        return embed

    async def refresh_message(self):
        if self.message is not None:
            await self.message.edit(
                embed=self.construct_embed(),
                view=self
            )

    @discord.ui.button(
        label="Add / Edit Reward",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def add_reward_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        reward_type = self.selected_reward_type

        if reward_type == "EXP":
            return await interaction.response.send_modal(
                RewardValueModal(self, "EXP")
            )

        if self.selected_target is None:
            return await interaction.response.send_message(
                "Select a reward first.",
                ephemeral=True
            )

        if reward_type == "items":
            return await interaction.response.send_modal(
                RewardValueModal(self, "items")
            )

        rewards = self.parent_view.quest_data["rewards"]
        skills = rewards.setdefault("skills", [])

        if self.selected_target in skills:
            return await interaction.response.send_message(
                "This skill is already included in the rewards.",
                ephemeral=True
            )

        skills.append(self.selected_target)

        await interaction.response.edit_message(
            embed=self.construct_embed(),
            view=self
        )

    @discord.ui.button(
        label="Remove Reward",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def remove_reward_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        rewards = self.parent_view.quest_data["rewards"]
        reward_type = self.selected_reward_type

        if reward_type == "EXP":
            if "EXP" not in rewards:
                return await interaction.response.send_message(
                    "No EXP reward configured.",
                    ephemeral=True
                )

            rewards.pop("EXP")

        else:
            if self.selected_target is None:
                return await interaction.response.send_message(
                    "Select a reward first.",
                    ephemeral=True
                )

            if reward_type == "items":
                items = rewards.get("items", {})

                if self.selected_target not in items:
                    return await interaction.response.send_message(
                        "This item isn't in the rewards.",
                        ephemeral=True
                    )

                items.pop(self.selected_target)

                if not items:
                    rewards.pop("items")

            else:
                skills = rewards.get("skills", [])

                if self.selected_target not in skills:
                    return await interaction.response.send_message(
                        "This skill isn't in the rewards.",
                        ephemeral=True
                    )

                skills.remove(self.selected_target)

                if not skills:
                    rewards.pop("skills")

        self.selected_target = None

        await interaction.response.edit_message(
            embed=self.construct_embed(),
            view=self
        )

    @discord.ui.button(
        label="Back to Quest",
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


# ============================================================
# DIALOGUES
# ============================================================

class QuestDialogueModal(discord.ui.Modal):
    def __init__(self, view, dialogue_type: str):
        title = (
            "Accept Dialogue"
            if dialogue_type == "accept_text"
            else "Report Dialogue"
        )

        super().__init__(title=title)

        self.editor = view
        self.dialogue_type = dialogue_type

        current = view.parent_view.quest_data[dialogue_type]

        self.dialogue = discord.ui.TextInput(
            label="Dialogue text",
            style=discord.TextStyle.paragraph,
            placeholder="Enter dialogue...",
            default=current or None,
            max_length=4000,
            required=True
        )

        self.add_item(self.dialogue)

    async def on_submit(self, interaction: discord.Interaction):
        value = self.dialogue.value.strip()

        if not value:
            return await interaction.response.send_message(
                "Dialogue cannot be empty.",
                ephemeral=True
            )

        self.editor.parent_view.quest_data[
            self.dialogue_type
        ] = value

        await interaction.response.send_message(
            "Dialogue updated.",
            ephemeral=True
        )

        await self.editor.refresh_message()


class QuestDialogueEditorView(discord.ui.View):
    def __init__(self, parent_view, timeout: float = 300):
        super().__init__(timeout=timeout)

        self.parent_view = parent_view
        self.message = parent_view.message

    async def interaction_check(self, interaction: discord.Interaction):
        return await self.parent_view.interaction_check(interaction)

    def construct_embed(self):
        data = self.parent_view.quest_data

        accept_text = data["accept_text"] or "Not configured."
        report_text = data["report_text"] or "Not configured."

        embed = discord.Embed(
            title="Path of Steel — Quest Dialogues",
            description=(
                f"**NPC:** `{self.parent_view.selected_npc}`\n"
                f"**Quest:** `{data['quest_id'] or 'Not configured'}`"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Accept Text",
            value=accept_text[:1024],
            inline=False
        )

        embed.add_field(
            name="Report Text",
            value=report_text[:1024],
            inline=False
        )

        embed.set_footer(
            text="Changes are stored in the quest draft."
        )

        return embed

    async def refresh_message(self):
        if self.message is not None:
            await self.message.edit(
                embed=self.construct_embed(),
                view=self
            )

    @discord.ui.button(
        label="Edit Accept Text",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def accept_text_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            QuestDialogueModal(self, "accept_text")
        )

    @discord.ui.button(
        label="Edit Report Text",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def report_text_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            QuestDialogueModal(self, "report_text")
        )

    @discord.ui.button(
        label="Back to Quest",
        style=discord.ButtonStyle.secondary,
        row=1
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


# ============================================================
# NPC QUEST CREATOR
# ============================================================

class NPCSelect(discord.ui.Select):
    def __init__(self, view):
        self.editor = view

        options = [
            discord.SelectOption(
                label=npc[:100],
                value=npc,
                description=data.get("type", "NPC")[:100],
                default=npc == view.selected_npc
            )
            for npc, data in view.npcs.items()
        ]

        super().__init__(
            placeholder="Select NPC...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        npc = self.values[0]

        self.editor.selected_npc = npc
        self.editor.quest_data = self.editor.create_empty_quest()

        self.editor.selected_target = None
        self.editor.selected_objective_type = "kill"
        self.editor.refresh_target_select()

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class NPCQuestCreatorView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        timeout: float = 300
    ):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.message = None

        self.npcs = load_json(NPC_PATH)
        self.original_quests = load_json(QUEST_PATH)

        self.entities = [
            entity
            for entity in load_json(ENTITY_PATH)
            if entity != "player"
        ]

        self.items = load_json(ITEM_PATH)

        self.selected_npc = None
        self.selected_objective_type = "kill"
        self.selected_target = None

        self.quest_data = self.create_empty_quest()
        self.target_select = None

        if not self.npcs:
            raise ValueError("No NPCs found.")

        if len(self.npcs) > 25:
            raise ValueError(
                "More than 25 NPCs. Select pagination is required."
            )

        if not self.entities:
            raise ValueError("No enemies found.")

        if len(self.entities) > 25:
            raise ValueError(
                "More than 25 enemies. Select pagination is required."
            )

        if not self.items:
            raise ValueError("No items found.")

        if len(self.items) > 25:
            raise ValueError(
                "More than 25 items. Select pagination is required."
            )

        self.add_item(NPCSelect(self))
        self.add_item(ObjectiveTypeSelect(self))

        self.refresh_target_select()

    @staticmethod
    def create_empty_quest():
        return {
            "quest_id": None,
            "conditions": {
                "min_level": 1,
                "max_level": 999
            },
            "objectives": {},
            "rewards": {},
            "repeatable": 0,
            "accept_text": "",
            "report_text": ""
        }

    def refresh_target_select(self):
        if self.target_select is not None:
            self.remove_item(self.target_select)

        self.target_select = ObjectiveTargetSelect(self)
        self.add_item(self.target_select)

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
            title="Path of Steel — Quest Creator",
            color=discord.Color.blurple()
        )

        if self.selected_npc is None:
            embed.description = "Select an NPC to create a quest."
            return embed

        data = self.quest_data
        conditions = data["conditions"]

        embed.description = f"**NPC:** `{self.selected_npc}`"

        embed.add_field(
            name="Basic Info",
            value=(
                f"**Quest ID:** "
                f"`{data['quest_id'] or 'Not configured'}`\n"
                f"**Repeatable:** {data['repeatable']}"
            ),
            inline=False
        )

        embed.add_field(
            name="Conditions",
            value=(
                f"**Minimum level:** {conditions['min_level']}\n"
                f"**Maximum level:** {conditions['max_level']}"
            ),
            inline=False
        )

        objectives = data["objectives"]

        if objectives:
            objective_lines = []

            for objective_type, targets in objectives.items():
                for target, quantity in targets.items():
                    objective_lines.append(
                        f"**{objective_type.title()}:** "
                        f"`{target}` × {quantity}"
                    )

            objective_text = "\n".join(objective_lines)
        else:
            objective_text = "Not configured yet."

        if len(objective_text) > 1000:
            objective_text = objective_text[:997] + "..."

        objective_count = sum(
            len(targets) for targets in objectives.values()
        )

        embed.add_field(
            name=f"Objectives ({objective_count})",
            value=objective_text,
            inline=False
        )

        rewards = data["rewards"]
        reward_lines = []

        if "EXP" in rewards:
            reward_lines.append(
                f"**EXP:** {rewards['EXP']}"
            )

        for item_id, quantity in rewards.get("items", {}).items():
            reward_lines.append(
                f"**Item:** `{item_id}` × {quantity}"
            )

        for skill in rewards.get("skills", []):
            reward_lines.append(
                f"**Skill:** `{skill}`"
            )

        reward_text = (
            "\n".join(reward_lines)
            if reward_lines
            else "Not configured yet."
        )

        if len(reward_text) > 1000:
            reward_text = reward_text[:997] + "..."

        embed.add_field(
            name="Rewards",
            value=reward_text,
            inline=False
        )

        dialogue_status = (
            "Configured"
            if data["accept_text"] and data["report_text"]
            else "Incomplete"
        )

        embed.add_field(
            name="Dialogues",
            value=dialogue_status,
            inline=False
        )

        if self.selected_target:
            embed.add_field(
                name="Selected Objective",
                value=(
                    f"**Type:** {self.selected_objective_type}\n"
                    f"**Target:** `{self.selected_target}`"
                ),
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
        row=3
    )
    async def basic_info_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select an NPC first.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            QuestBasicInfoModal(self)
        )

    @discord.ui.button(
        label="Add / Edit Objective",
        style=discord.ButtonStyle.success,
        row=3
    )
    async def configure_objective_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select an NPC first.",
                ephemeral=True
            )

        if self.selected_target is None:
            return await interaction.response.send_message(
                "Select an objective target first.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            ObjectiveQuantityModal(self)
        )

    @discord.ui.button(
        label="Rewards",
        style=discord.ButtonStyle.primary,
        row=3
    )
    async def rewards_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select an NPC first.",
                ephemeral=True
            )

        view = RewardEditorView(self)

        await interaction.response.edit_message(
            embed=view.construct_embed(),
            view=view
        )

        view.message = interaction.message

    @discord.ui.button(
        label="Dialogues",
        style=discord.ButtonStyle.primary,
        row=4
    )
    async def dialogues_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select an NPC first.",
                ephemeral=True
            )

        view = QuestDialogueEditorView(self)

        await interaction.response.edit_message(
            embed=view.construct_embed(),
            view=view
        )

        view.message = interaction.message

    @discord.ui.button(
        label="Remove Objective",
        style=discord.ButtonStyle.danger,
        row=4
    )
    async def remove_objective_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select an NPC first.",
                ephemeral=True
            )

        if self.selected_target is None:
            return await interaction.response.send_message(
                "Select an objective target first.",
                ephemeral=True
            )

        objective_type = self.selected_objective_type
        target = self.selected_target

        objectives = self.quest_data["objectives"]

        if (
            objective_type not in objectives
            or target not in objectives[objective_type]
        ):
            return await interaction.response.send_message(
                "This objective hasn't been configured.",
                ephemeral=True
            )

        objectives[objective_type].pop(target)

        if not objectives[objective_type]:
            objectives.pop(objective_type)

        self.selected_target = None

        await interaction.response.edit_message(
            embed=self.construct_embed(),
            view=self
        )

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.success,
        row=4
    )
    async def confirm_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.selected_npc is None:
            return await interaction.response.send_message(
                "Select an NPC first.",
                ephemeral=True
            )

        data = self.quest_data
        quest_id = data["quest_id"]

        if not quest_id:
            return await interaction.response.send_message(
                "Configure Basic Info first.",
                ephemeral=True
            )

        if not data["objectives"]:
            return await interaction.response.send_message(
                "Add at least one objective.",
                ephemeral=True
            )

        if not data["accept_text"].strip():
            return await interaction.response.send_message(
                "Configure Accept Text first.",
                ephemeral=True
            )

        if not data["report_text"].strip():
            return await interaction.response.send_message(
                "Configure Report Text first.",
                ephemeral=True
            )

        try:
            # Reload to check the latest file contents.
            current_quests = load_json(QUEST_PATH)

            if quest_id in current_quests.get(self.selected_npc, {}):
                return await interaction.response.send_message(
                    "A quest with this ID already exists for this NPC.",
                    ephemeral=True
                )

            quest = {
                "conditions": data["conditions"],
                "objectives": data["objectives"],
                "rewards": data["rewards"],
                "repeatable": data["repeatable"],
                "accept_text": data["accept_text"],
                "report_text": data["report_text"]
            }

            add_quest(
                character=self.selected_npc,
                quest_name=quest_id,
                quest=quest
            )

        except Exception as e:
            return await interaction.response.send_message(
                f"Failed to save quest: `{e}`",
                ephemeral=True
            )

        self.stop()

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Quest Successfully Saved!",
            description=(
                f"Quest `{quest_id}` has been added to "
                f"`{self.selected_npc}`.\n\n"
                "The quest data has been saved successfully."
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
        row=4
    )
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.stop()

        await interaction.response.edit_message(
            content="Quest creation cancelled.",
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


async def start_npc_quest_creator(
    interaction: discord.Interaction
):
    view = NPCQuestCreatorView(interaction.user.id)

    await interaction.response.edit_message(
        embed=view.construct_embed(),
        view=view
    )

    view.message = interaction.message
