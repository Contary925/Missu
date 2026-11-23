
import discord


class KeyValueModal(discord.ui.Modal):
    def __init__(self, editor, key=None):
        super().__init__(
            title="Add Parameter" if key is None else "Edit Parameter"
        )

        self.editor = editor
        self.old_key = key

        self.key_input = discord.ui.TextInput(
            label="Parameter name",
            placeholder="hp",
            default=key,
            max_length=50
        )

        self.value_input = discord.ui.TextInput(
            label="Parameter value (integer)",
            placeholder="50",
            default=(
                str(editor.data[key])
                if key is not None else None
            ),
            max_length=20
        )

        self.add_item(self.key_input)
        self.add_item(self.value_input)

    async def on_submit(self, interaction: discord.Interaction):
        key = self.key_input.value.strip()

        if not key:
            return await interaction.response.send_message(
                "Parameter name cannot be empty.",
                ephemeral=True
            )

        if key in self.editor.protected_keys:
            return await interaction.response.send_message(
                "This parameter name is reserved.",
                ephemeral=True
            )

        try:
            value = int(self.value_input.value.strip())
        except ValueError:
            return await interaction.response.send_message(
                "Parameter value must be an integer.",
                ephemeral=True
            )

        if self.old_key is not None:
            # Rename while preserving the original dictionary order.
            if key != self.old_key:
                if key in self.editor.data:
                    return await interaction.response.send_message(
                        f"Parameter `{key}` already exists.",
                        ephemeral=True
                    )

                updated = {}
                for existing_key, existing_value in self.editor.data.items():
                    if existing_key == self.old_key:
                        updated[key] = value
                    else:
                        updated[existing_key] = existing_value

                self.editor.data.clear()
                self.editor.data.update(updated)
            else:
                self.editor.data[key] = value
        else:
            if key in self.editor.data:
                return await interaction.response.send_message(
                    f"Parameter `{key}` already exists. Use Edit instead.",
                    ephemeral=True
                )

            self.editor.data[key] = value

        await interaction.response.defer()
        await self.editor.refresh_message()


class KeyValueSelect(discord.ui.Select):
    def __init__(self, editor, action: str):
        self.editor = editor
        self.action = action

        options = [
            discord.SelectOption(
                label=key[:100],
                description=f"Current value: {value}"[:100],
                value=key
            )
            for key, value in editor.data.items()
            if key not in editor.protected_keys
        ][:25]

        super().__init__(
            placeholder=(
                "Select parameter to edit..."
                if action == "edit"
                else "Select parameter to remove..."
            ),
            min_values=1,
            max_values=1,
            options=options,
            row=0 if action == "edit" else 1
        )

    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]

        if self.action == "edit":
            await interaction.response.send_modal(
                KeyValueModal(self.editor, key)
            )
            return

        self.editor.data.pop(key, None)

        await interaction.response.edit_message(
            embed=self.editor.construct_embed(),
            view=self.editor
        )


class KeyValueEditorView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        data: dict,
        title: str,
        parent_view: discord.ui.View,
        protected_keys: set | None = None,
        timeout: float = 300
    ):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.data = data
        self.title = title
        self.parent_view = parent_view
        self.message = None
        self.protected_keys = protected_keys or set()

        self.rebuild_selects()

        self.add_item(KeyValueSelect(self, "edit")) if any(
            key not in self.protected_keys for key in data
        ) else None

        self.add_item(KeyValueSelect(self, "delete")) if any(
            key not in self.protected_keys for key in data
        ) else None

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
            title=self.title,
            color=discord.Color.blurple()
        )

        visible_data = {
            key: value
            for key, value in self.data.items()
            if key not in self.protected_keys
        }

        if visible_data:
            lines = [
                f"**{key}:** `{value}`"
                for key, value in visible_data.items()
            ]
            description = "\n".join(lines)

            if len(description) > 4000:
                description = description[:3997] + "..."
        else:
            description = "No parameters configured."

        embed.description = description
        embed.set_footer(text="Select a parameter to edit or remove it.")

        return embed

    async def refresh_message(self):
        self.rebuild_selects()

        if self.message is not None:
            await self.message.edit(
                embed=self.construct_embed(),
                view=self
            )

    @discord.ui.button(
        label="Add Parameter",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def add_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            KeyValueModal(self)
        )

    @discord.ui.button(
        label="Back",
        style=discord.ButtonStyle.secondary,
        row=2
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

    def rebuild_selects(self):
        for item in list(self.children):
            if isinstance(item, KeyValueSelect):
                self.remove_item(item)

        available = any(
            key not in self.protected_keys
            for key in self.data
        )

        if available:
            self.add_item(KeyValueSelect(self, "edit"))
            self.add_item(KeyValueSelect(self, "delete"))


async def open_key_value_editor(
    interaction: discord.Interaction,
    data: dict,
    title: str,
    parent_view: discord.ui.View,
    protected_keys: set | None = None
):
    editor = KeyValueEditorView(
        author_id=interaction.user.id,
        data=data,
        title=title,
        parent_view=parent_view,
        protected_keys=protected_keys
    )

    await interaction.response.edit_message(
        embed=editor.construct_embed(),
        view=editor
    )

    editor.message = interaction.message
