import nextcord
from nextcord.ext import commands
from nextcord.utils import datetime

class InviteLogger(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        inviter = None
        
        if guild.me.guild_permissions.view_audit_log:
            invite_log = await guild.audit_logs(limit=1, action=nextcord.AuditLogAction.bot_add).flatten()
            invite = invite_log[0]
            inviter = invite.user
            
        if inviter:
            embed = nextcord.Embed(title='Thanks for the invite!', 
                                   description=f'Thank you {inviter.mention} for inviting me to {guild.name}!', 
                                   color=nextcord.Color.green())
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.timestamp = datetime.utcnow()
            
            await inviter.send(embed=embed)
            
def setup(bot):
    bot.add_cog(InviteLogger(bot))