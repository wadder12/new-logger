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

        if before.roles != after.roles:
            # Roles changed
            
            embed = nextcord.Embed(title='Roles Updated', color=nextcord.Color.blue())
            embed.add_field(name='Member', value=after.mention)
            embed.add_field(name='Before', value=', '.join([r.mention for r in before.roles]))
            embed.add_field(name='After', value=', '.join([r.mention for r in after.roles]))

            await self.logger_channel.send(embed=embed)

        if before.nick != after.nick:
            # Nickname changed

            embed = nextcord.Embed(title='Nickname Updated', color=nextcord.Color.green())
            embed.add_field(name='Member', value=after.mention)
            embed.add_field(name='Before', value=before.nick)
            embed.add_field(name='After', value=after.nick)

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
    
    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)

            embed = nextcord.Embed(title='Raw Message Edit', color=nextcord.Color.blue())
            embed.add_field(name='Channel', value=channel.mention if channel else payload.channel_id)
            embed.add_field(name='Message ID', value=payload.message_id)

            await self.logger_channel.send(embed=embed)
            
    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):

        if self.logger_channel:
            embed = nextcord.Embed(title='Reaction Added', color=nextcord.Color.green())
            embed.add_field(name='User', value=user.mention)
            embed.add_field(name='Channel', value=reaction.message.channel.mention)
            embed.add_field(name='Message', value=reaction.message.jump_url)
            embed.add_field(name='Emoji', value=reaction.emoji)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            embed = nextcord.Embed(title='Raw Reaction Added', color=nextcord.Color.green())
            embed.add_field(name='User', value=f'<@{payload.user_id}>')
            embed.add_field(name='Channel', value=channel.mention)
            embed.add_field(name='Message', value=message.jump_url)
            embed.add_field(name='Emoji', value=payload.emoji)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):

        if self.logger_channel:
            embed = nextcord.Embed(title='Reaction Removed', color=nextcord.Color.red())
            embed.add_field(name='User', value=user.mention)
            embed.add_field(name='Channel', value=reaction.message.channel.mention)
            embed.add_field(name='Message', value=reaction.message.jump_url)
            embed.add_field(name='Emoji', value=reaction.emoji)

            await self.logger_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)

            embed = nextcord.Embed(title='Raw Reaction Removed', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=channel.mention)
            embed.add_field(name='Message ID', value=payload.message_id)
            embed.add_field(name='Emoji', value=payload.emoji)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener() 
    async def on_reaction_clear(self, message, reactions):

        if self.logger_channel:
            embed = nextcord.Embed(title='Reactions Cleared', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=message.channel.mention)
            embed.add_field(name='Message', value=message.jump_url)
            embed.add_field(name='Reaction Count', value=len(reactions))

            await self.logger_channel.send(embed=embed)
            
            
    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)
            
            embed = nextcord.Embed(title='Raw Reactions Cleared', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=channel.mention)
            embed.add_field(name='Message ID', value=payload.message_id)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_reaction_clear_emoji(self, reaction):

        if self.logger_channel:
            embed = nextcord.Embed(title='Reaction Emoji Cleared', color=nextcord.Color.red())
            embed.add_field(name='Emoji', value=reaction.emoji)
            embed.add_field(name='Channel', value=reaction.message.channel.mention)
            embed.add_field(name='Message', value=reaction.message.jump_url)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):

        if self.logger_channel:
            channel = self.bot.get_channel(payload.channel_id)
            
            embed = nextcord.Embed(title='Raw Reaction Emoji Cleared', color=nextcord.Color.red())
            embed.add_field(name='Channel', value=channel.mention) 
            embed.add_field(name='Message ID', value=payload.message_id)
            embed.add_field(name='Emoji', value=payload.emoji)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener() 
    async def on_interaction(self, interaction):

        if self.logger_channel:
            embed = nextcord.Embed(title='Interaction', color=nextcord.Color.purple())
            embed.add_field(name='Type', value=interaction.type)
            embed.add_field(name='Name', value=interaction.data.name)
            embed.add_field(name='User', value=interaction.user)
            embed.add_field(name='ID', value=interaction.id)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_private_channel_update(self, before, after):

        if self.logger_channel:
            embed = nextcord.Embed(title='Private Channel Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before)
            embed.add_field(name='After', value=after)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener() 
    async def on_private_channel_pins_update(self, channel, last_pin):

        if self.logger_channel:
            embed = nextcord.Embed(title='Private Channel Pins Updated', color=nextcord.Color.blue())
            embed.add_field(name='Channel', value=channel)
            embed.add_field(name='Last Pin', value=last_pin)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):

        if self.logger_channel:
            embed = nextcord.Embed(title='Guild Channel Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.mention)
            embed.add_field(name='After', value=after.mention)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener() 
    async def on_guild_channel_pins_update(self, channel, last_pin):

        if self.logger_channel:
            embed = nextcord.Embed(title='Guild Channel Pins Updated', color=nextcord.Color.blue())
            embed.add_field(name='Channel', value=channel.mention)
            embed.add_field(name='Last Pin', value=last_pin)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_thread_create(self, thread):

        if self.logger_channel:
            embed = nextcord.Embed(title='Thread Created', color=nextcord.Color.green())
            embed.add_field(name='Thread', value=thread.mention)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()  
    async def on_thread_join(self, thread):

        if self.logger_channel:
            embed = nextcord.Embed(title='Thread Joined', color=nextcord.Color.green())
            embed.add_field(name='Thread', value=thread.mention)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_remove(self, thread):

        if self.logger_channel:
            embed = nextcord.Embed(title='Thread Removed', color=nextcord.Color.red())
            embed.add_field(name='Thread', value=thread.mention)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_delete(self, thread):

        if self.logger_channel:
            embed = nextcord.Embed(title='Thread Deleted', color=nextcord.Color.red())
            embed.add_field(name='Thread', value=thread.mention)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_member_join(self, member):

        if self.logger_channel:
            embed = nextcord.Embed(title='User Joined Thread', color=nextcord.Color.green())
            embed.add_field(name='Thread', value=member.thread.mention)
            embed.add_field(name='User', value=member.user.mention)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member):

        if self.logger_channel:
            embed = nextcord.Embed(title='User Left Thread', color=nextcord.Color.red())
            embed.add_field(name='Thread', value=member.thread.mention)
            embed.add_field(name='User', value=member.user.mention)

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_update(self, before, after):

        if self.logger_channel:
            embed = nextcord.Embed(title='Thread Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.mention)
            embed.add_field(name='After', value=after.mention)

            await self.logger_channel.send(embed=embed)

    # Other thread listeners

    @commands.Cog.listener() 
    async def on_integration_create(self, integration):

        if self.logger_channel:
            embed = nextcord.Embed(title='Integration Created', color=nextcord.Color.green())
            embed.add_field(name='Integration', value=integration.name)
            embed.add_field(name='ID', value=integration.id)

            await self.logger_channel.send(embed=embed)


    @commands.Cog.listener() 
    async def on_integration_update(self, integration):
    
        if self.logger_channel:
        
            embed = nextcord.Embed(title='Integration Updated', color=nextcord.Color.blue())
            
            embed.add_field(name='Integration', value=integration.name)
            
            await self.logger_channel.send(embed=embed) 
            
    @commands.Cog.listener()
    async def on_raw_integration_delete(self, payload):

        if self.logger_channel:

            embed = nextcord.Embed(title='Integration Deleted', color=nextcord.Color.red())
            
            embed.add_field(name='Integration ID', value=payload.integration_id)
            
            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener() 
    async def on_webhooks_update(self, channel):

        if self.logger_channel:

            before = len(await channel.webhooks())
            after = len(await channel.webhooks())

            embed = nextcord.Embed(title='Webhooks Updated', color=nextcord.Color.purple())
            embed.add_field(name='Channel', value=channel.mention)
            embed.add_field(name='Before', value=before) 
            embed.add_field(name='After', value=after)

            if before < after:
                # Webhooks were added
                for webhook in await channel.webhooks():
                    if webhook.token:
                        embed.add_field(name='Added', value=f"{webhook.name} ({webhook.url})")
                else:
                    embed.add_field(name='Added', value=webhook.name)

            elif before > after:
                # Webhooks were removed
                pass

            await self.logger_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):

        guild = self.bot.get_guild(payload.guild_id)
        user = await self.bot.fetch_user(payload.user.id)

        if self.logger_channel:

            embed = nextcord.Embed(title='Member Left', color=nextcord.Color.red())
            embed.add_field(name='Member', value=f'{user} (ID: {user.id})')
            embed.add_field(name='Guild', value=guild.name)
            await self.logger_channel.send(embed=embed)
            
            
            
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):

        guild = after.guild

        if before.status != after.status:
            # Status changed
            embed = nextcord.Embed(title='Status Updated', color=nextcord.Color.gold())
            embed.add_field(name='Member', value=after.mention)
            embed.add_field(name='Before', value=before.status)
            embed.add_field(name='After', value=after.status)

            await self.logger_channel.send(embed=embed)

        if before.activity != after.activity:
            # Activity changed
            embed = nextcord.Embed(title='Activity Updated', color=nextcord.Color.green())
            embed.add_field(name='Member', value=after.mention)
            embed.add_field(name='Before', value=before.activity)
            embed.add_field(name='After', value=after.activity)

            await self.logger_channel.send(embed=embed)       
            
            
            
            
            
            
            
            
            
            
            
            
                
    def cog_unload(self):
        self.save_config()

    # Add more event listeners here as per your requirements

def setup(bot):
    bot.add_cog(Logger(bot))
