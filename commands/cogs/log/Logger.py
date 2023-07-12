import json
import nextcord
from nextcord.ext import commands

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger_channel = None

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.logger_channel = self.bot.get_channel(config['logger_channel'])
        except FileNotFoundError:
            pass

    def save_config(self):
        config = {'logger_channel': self.logger_channel.id if self.logger_channel else None}
        with open('config.json', 'w') as f:
            json.dump(config, f)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logger cog is ready.')
        self.load_config()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild = ctx.guild
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            guild.me: nextcord.PermissionOverwrite(read_messages=True)
        }
        logger_channel_name = '📝-logger'
        self.logger_channel = self.get_logger_channel(guild)
        if not self.logger_channel:
            self.logger_channel = await guild.create_text_channel(logger_channel_name, overwrites=overwrites)
        self.save_config()
        await ctx.send('Logger channel has been set up.')

    def get_logger_channel(self, guild):
        logger_channel_name = '📝-logger'
        for channel in guild.text_channels:
            if channel.name == logger_channel_name:
                return channel
        return None
    
    # * on message

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.logger_channel and message.channel != self.logger_channel:
            embed = nextcord.Embed(title='Message Log', color=nextcord.Color.blue())
            embed.add_field(name='Author', value=message.author.mention)
            embed.add_field(name='Channel', value=message.channel.mention)
            embed.add_field(name='Content', value=message.content)
            await self.logger_channel.send(embed=embed)
            
            
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if self.logger_channel and messages and messages[0].channel != self.logger_channel:
            embed = nextcord.Embed(title='Bulk Message Delete', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=messages[0].channel.mention)
            embed.add_field(name='Message Count', value=len(messages))
            await self.logger_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if self.logger_channel and message.channel != self.logger_channel:
            embed = nextcord.Embed(title='Message Deleted', color=nextcord.Color.red())
            embed.add_field(name='Author', value=message.author.mention)
            embed.add_field(name='Channel', value=message.channel.mention)
            embed.add_field(name='Content', value=message.content)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if self.logger_channel and before.channel != self.logger_channel:
            embed = nextcord.Embed(title='Message Edited', color=nextcord.Color.orange())
            embed.add_field(name='Author', value=before.author.mention)
            embed.add_field(name='Channel', value=before.channel.mention)
            embed.add_field(name='Before', value=before.content)
            embed.add_field(name='After', value=after.content)
            await self.logger_channel.send(embed=embed)

# * end of on message

# * member events

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.logger_channel:
            embed = nextcord.Embed(title='Member Joined', color=nextcord.Color.green())
            embed.add_field(name='Member', value=member.mention)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if self.logger_channel:
            embed = nextcord.Embed(title='Member Left', color=nextcord.Color.dark_red())
            embed.add_field(name='Member', value=member.mention)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if self.logger_channel:
            embed = nextcord.Embed(title='Member Banned', color=nextcord.Color.dark_red())
            embed.add_field(name='Member', value=user.mention)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if self.logger_channel:
            embed = nextcord.Embed(title='Member Unbanned', color=nextcord.Color.green())
            embed.add_field(name='Member', value=user.mention)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.logger_channel:
            if before.display_name != after.display_name:
                embed = nextcord.Embed(title='Member Updated', color=nextcord.Color.blue())
                embed.add_field(name='Member', value=after.mention)
                embed.add_field(name='Before', value=before.display_name)
                embed.add_field(name='After', value=after.display_name)
                await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if self.logger_channel:
            if before.name != after.name:
                embed = nextcord.Embed(title='Username Updated', color=nextcord.Color.blue())
                embed.add_field(name='User', value=after.mention)
                embed.add_field(name='Before', value=before.name)
                embed.add_field(name='After', value=after.name)
                await self.logger_channel.send(embed=embed)
# * end of member events

# * start of guild events 
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if self.logger_channel:
            embed = nextcord.Embed(title='Channel Created', color=nextcord.Color.green())
            embed.add_field(name='Channel', value=channel.mention)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if self.logger_channel:
            embed = nextcord.Embed(title='Channel Deleted', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=channel.name)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if self.logger_channel:
            if before.name != after.name:
                embed = nextcord.Embed(title='Channel Updated', color=nextcord.Color.blue())
                embed.add_field(name='Channel', value=after.mention)
                embed.add_field(name='Before', value=before.name)
                embed.add_field(name='After', value=after.name)
                await self.logger_channel.send(embed=embed)
                
    @commands.Cog.listener()
    async def on_member_emojis_update(self, member, before, after):
        if self.logger_channel:
            if len(before) < len(after):
                added_emoji = set(after) - set(before)
                emoji = added_emoji.pop()
                embed = nextcord.Embed(title='Emoji Added', color=nextcord.Color.green())
                embed.add_field(name='Member', value=member.mention)
                embed.add_field(name='Emoji', value=str(emoji))
                await self.logger_channel.send(embed=embed)
            elif len(before) > len(after):
                removed_emoji = set(before) - set(after)
                emoji = removed_emoji.pop()
                embed = nextcord.Embed(title='Emoji Removed', color=nextcord.Color.red())
                embed.add_field(name='Member', value=member.mention)
                embed.add_field(name='Emoji', value=str(emoji))
                await self.logger_channel.send(embed=embed)
                
    @commands.Cog.listener()
    async def on_member_role_update(self, member, before, after):
        if self.logger_channel:
            if len(before) < len(after):
                added_role = set(after) - set(before)
                role = added_role.pop()
                embed = nextcord.Embed(title='Role Added', color=role.color)
                embed.add_field(name='Member', value=member.mention)
                embed.add_field(name='Role', value=role.mention)
                await self.logger_channel.send(embed=embed)
            elif len(before) > len(after):
                removed_role = set(before) - set(after)
                role = removed_role.pop()
                embed = nextcord.Embed(title='Role Removed', color=role.color)
                embed.add_field(name='Member', value=member.mention)
                embed.add_field(name='Role', value=role.mention)
                await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.logger_channel:
            embed = nextcord.Embed(title='Voice State Update', color=nextcord.Color.teal())
            embed.add_field(name='Member', value=member.mention)
            
            if after.channel:
                embed.add_field(name='Current Channel', value=after.channel.name)
            else:
                embed.add_field(name='Current Channel', value='Not in a voice channel')
                
            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if self.logger_channel:
            embed = nextcord.Embed(title='Joined Guild', color=nextcord.Color.green())
            embed.add_field(name='Guild', value=guild.name)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if self.logger_channel:
            embed = nextcord.Embed(title='Left Guild', color=nextcord.Color.dark_red())
            embed.add_field(name='Guild', value=guild.name)
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if self.logger_channel:
            if before.name != after.name:
                embed = nextcord.Embed(title='Guild Updated', color=nextcord.Color.blue())
                embed.add_field(name='Before', value=before.name)
                embed.add_field(name='After', value=after.name)
                await self.logger_channel.send(embed=embed)
# * end of guild 

# * start of invite events 
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if self.logger_channel:
            embed = nextcord.Embed(title='Invite Created', color=nextcord.Color.green())
            embed.add_field(name='Code', value=invite.code)
            embed.add_field(name='Guild', value=invite.guild.name)
            embed.add_field(name='Channel', value=invite.channel.mention)
            embed.add_field(name='Author', value=invite.inviter.mention)
            
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if self.logger_channel:
            embed = nextcord.Embed(title='Invite Deleted', color=nextcord.Color.red())
            embed.add_field(name='Code', value=invite.code)
            embed.add_field(name='Guild', value=invite.guild.name)
            embed.add_field(name='Channel', value=invite.channel.mention)
            embed.add_field(name='Author', value=invite.inviter.mention)
            await self.logger_channel.send(embed=embed)
# * end of invite events 


# * on typing events             
    @commands.Cog.listener() 
    async def on_typing(self, channel, user, when):

        if self.logger_channel:
            embed = nextcord.Embed(title='User Typing', color=nextcord.Color.blue())
            embed.add_field(name='Channel', value=channel.mention)
            embed.add_field(name='User', value=user.mention)
            embed.add_field(name='When', value=when)

            await self.logger_channel.send(embed=embed)
            
    @commands.Cog.listener() #
    async def on_raw_typing(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)

            embed = nextcord.Embed(title='Raw User Typing', color=nextcord.Color.blue())
            embed.add_field(name='Channel', value=channel.mention if channel else payload.channel_id) 
            embed.add_field(name='User ID', value=payload.user_id)
            embed.add_field(name='When', value=payload.when)

            await self.logger_channel.send(embed=embed) 
            
# * on typing events             
      
    @commands.Cog.listener() #
    async def on_raw_message_delete(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)

            embed = nextcord.Embed(title='Raw Message Delete', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=channel.mention if channel else payload.channel_id)
            embed.add_field(name='Message ID', value=payload.message_id)
        
            await self.logger_channel.send(embed=embed)
    
    

    
                
    def cog_unload(self):
        self.save_config()

    # Add more event listeners here as per your requirements

def setup(bot):
    bot.add_cog(Logger(bot))
