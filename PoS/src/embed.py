import discord

class NumberButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(label=str(number), style=discord.ButtonStyle.primary)
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.author_id:
            return
        self.view.selected_number = self.number
        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(view=self.view)
        self.view.stop()

class NumberView(discord.ui.View):
    def __init__(self, author_id: int, num: int, start_with_zero: bool = True, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.selected_number = None
        start = 0 if start_with_zero else 1
        end = num if start_with_zero else num + 1
        for i in range(start, end):
            self.add_item(NumberButton(i))

class CustomButton(discord.ui.Button):
    def __init__(self, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.label = label
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.author_id:
            return
        self.view.selected = self.label
        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(view=self.view)
        self.view.stop()

class CustomView(discord.ui.View):
    def __init__(self, author_id: int, labels: list[str], timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.selected = None
        for label in labels:
            self.add_item(CustomButton(label))

def construct_embed(title, text):
    embed = discord.Embed(
        title=title,
        color=0x258cb7,
        description=text,
    )
    return embed

async def send_embed_with_buttons(game_msg, message, title, text, num, start_with_zero = True):
    embed = construct_embed(title, text)
    if game_msg is None:
        game_msg = await message.channel.send(embed=embed)
    view = NumberView(author_id=message.author.id, num=num, start_with_zero=start_with_zero)
    result_msg = await game_msg.edit(embed=embed, view=view)
    await view.wait()
    return result_msg, view.selected_number

async def send_embed_with_custom_buttons(game_msg, message, title, text, buttons):
    embed = construct_embed(title, text)
    if game_msg is None:
        game_msg = await message.channel.send(embed=embed)
    view = CustomView(message.author.id, buttons)
    result_msg = await game_msg.edit(embed=embed, view=view)
    await view.wait()
    return result_msg, view.selected

    
