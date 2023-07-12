import nextcord
from nextcord.ext import commands

class DirectMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="directme", description="Send me a message of bugs!")
    async def directmessage(self, interaction: nextcord.Interaction, *, message):
        user = await self.bot.fetch_user(404687039905136661)  # Replace YOUR_USER_ID with your user ID

        # Create an embed for the DM to the bot owner
        dm_embed = nextcord.Embed(
            title="New Message from a User",
            description=message,
            color=0x00ff00
        )
        dm_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        dm_embed.set_footer(text="Sent by", icon_url=interaction.user.avatar.url)
        dm_embed.timestamp = interaction.created_at

        # Send the DM to the bot owner
        await user.send(embed=dm_embed)

        # Create an embed for the response to the user in the server
        response_embed = nextcord.Embed(
            title="Message Sent",
            description="Your message has been sent to the bot owner.",
            color=0x0000ff
        )
        response_embed.set_author(name="Bot Response", icon_url=self.bot.user.avatar.url)
        response_embed.set_footer(text="Sent by", icon_url=self.bot.user.avatar.url)
        response_embed.timestamp = nextcord.utils.utcnow()

        # Reply to the user in the server with the embed
        await interaction.response.send_message(embed=response_embed)

def setup(bot):
    bot.add_cog(DirectMessage(bot))
    print("DirectMessage is loaded")
