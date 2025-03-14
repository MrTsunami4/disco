import discord

class Dropdown(discord.ui.Select):
    """Dropdown menu for color selection."""
    
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(
                label="Red", description="Your favourite colour is red", emoji="🟥"
            ),
            discord.SelectOption(
                label="Green", description="Your favourite colour is green", emoji="🟩"
            ),
            discord.SelectOption(
                label="Blue", description="Your favourite colour is blue", emoji="🟦"
            ),
        ]

        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Your favourite colour is {self.values[0]}"
        )


class DropdownView(discord.ui.View):
    """View that contains the dropdown menu."""
    
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())