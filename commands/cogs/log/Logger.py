import json
import nextcord
from nextcord.ext import commands
from nextcord.webhook import Webhook

from nextcord.utils import get

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
        timestamp = message.created_at.strftime("%b %d, %Y %I:%M %p")
        embed = nextcord.Embed(title='Message Log', color=nextcord.Color.blue())
        embed.set_author(name=str(message.author), icon_url=message.author.avatar.url)
        embed.add_field(name='Author', value=message.author.mention)
        embed.add_field(name='Channel', value=message.channel.mention)
        embed.add_field(name='Time', value=timestamp)
        embed.add_field(name='Content', value=message.content, inline=False)

        if len(message.attachments) > 0:
            embed.add_field(name='Attachments', value='\n'.join([a.filename for a in message.attachments]))

        if self.logger_channel and message.channel != self.logger_channel:
            await self.logger_channel.send(embed=embed)
            
            
    @commands.Cog.listener() 
    async def on_bulk_message_delete(self, messages):

        if len(messages) > 5:

            embed = nextcord.Embed(title='Bulk Message Delete', color=nextcord.Color.red())
            embed.set_author(name=f"{len(messages)} Messages Deleted")

            channel = messages[0].channel
            embed.add_field(name='Channel', value=channel.mention)

            msg_links = []
            for msg in messages[:5]: 
                msg_links.append(f"[{msg.created_at.strftime('%H:%M:%S')}]({msg.jump_url}) {msg.author.mention}: {msg.content}")
            
            embed.description = "\n".join(msg_links)
            embed.add_field(name='Total Messages', value=len(messages))

            if self.logger_channel and channel != self.logger_channel:
                await self.logger_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_message_delete(self, message):

        

            embed = nextcord.Embed(color=nextcord.Color.red())

            embed.set_author(name=str(message.author), icon_url=message.author.avatar.url)

            embed.add_field(name='Author', value=message.author.mention)
            embed.add_field(name='Channel', value=message.channel.mention)

            embed.description = message.content[:1024]

            if len(message.content) > 1024:
                embed.description += f"... (truncated)"

            embed.set_footer(text=f"Deleted at {message.created_at.strftime('%m/%d/%Y %I:%M:%S %p')}")

            if self.logger_channel and message.channel != self.logger_channel:
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

    @commands.Cog.listener() # updated jul 12
    async def on_member_join(self, member):
        

        embed = nextcord.Embed(title='Member Joined', color=nextcord.Color.green())
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name='Member', value=f'{member.mention} (ID: {member.id})')
        embed.add_field(name='Created At', value=member.created_at.strftime('%B %d, %Y'))
        
        total = len(self.bot.users)
        embed.set_footer(text=f'Member #{total}')

        if self.logger_channel:
            await self.logger_channel.send(embed=embed)

        role = get(member.guild.roles, name="Members") 
        await member.add_roles(role)

        channel = get(member.guild.channels, name="general")
        await channel.send(f"Welcome to the server, {member.mention}!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        embed = nextcord.Embed(title='Member Left', color=nextcord.Color.dark_red())
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name='Member', value=f'{member.mention} (ID: {member.id})')
        embed.add_field(name='Joined At', value=member.joined_at.strftime('%B %d, %Y'))
        
        total = len(self.bot.users)
        embed.set_footer(text=f'Remaining: {total}')

        if self.logger_channel:
            await self.logger_channel.send(embed=embed)

        role = get(member.guild.roles, name="Members")
        if role in member.roles:
            await member.remove_roles(role)

        channel = get(member.guild.channels, name="general")
        await channel.send(f"{member.mention} has left the server.")

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

        embed = nextcord.Embed(title='Invite Created', color=nextcord.Color.green())

        embed.add_field(name='Code', value=invite.code)
        embed.add_field(name='Channel', value=invite.channel.mention)
        embed.add_field(name='Inviter', value=invite.inviter.mention)

        if invite.max_age > 0:
            embed.add_field(name='Max Age', value=f"{invite.max_age} seconds")

        if invite.max_uses > 0:
            embed.add_field(name='Max Uses', value=invite.max_uses)

        if invite.temporary:
            embed.add_field(name='Temporary', value='Yes')

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

        if before.activity != after.activity:

            # Activity changed
            embed = nextcord.Embed(title='Activity Updated', color=nextcord.Color.green())
            
            embed.add_field(name='Member', value=after.display_name)

            if before.activity is None:
                embed.add_field(name='Before', value='No activity')
            else:
                embed.add_field(name='Before', value=before.activity.name)

            if after.activity is None:
                embed.add_field(name='After', value='No activity')
            else:
                embed.add_field(name='After', value=after.activity.name)

            await self.logger_channel.send(embed=embed)
            
    """ # ! need to add webhook for me personally 
    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        embed = nextcord.Embed(title='New Guild Added', color=nextcord.Color.green())
        embed.add_field(name='Guild', value=guild.name)
        embed.add_field(name='Guild ID', value=guild.id) 
        embed.add_field(name='Owner', value=guild.owner)
        embed.add_field(name='Member Count', value=guild.member_count)

        await self.logger_channel.send(embed=embed) 
        
        
    @commands.Cog.listener() 
    async def on_guild_remove(self, guild):

        embed = nextcord.Embed(title='Removed from Guild', color=nextcord.Color.red())
        embed.add_field(name='Guild', value=guild.name)
        embed.add_field(name='Guild ID', value=guild.id)
        embed.add_field(name='Owner', value=guild.owner)
        embed.add_field(name='Member Count', value=guild.member_count)

        await self.logger_channel.send(embed=embed)       
            
    """
            
            
            
            
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):

        if before.name != after.name:
            # Guild name changed
            embed = nextcord.Embed(title='Guild Name Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.name)
            embed.add_field(name='After', value=after.name)

            await self.logger_channel.send(embed=embed)

        if before.region != after.region:
            # Guild region changed
            embed = nextcord.Embed(title='Guild Region Updated', color=nextcord.Color.green())
            embed.add_field(name='Before', value=before.region)
            embed.add_field(name='After', value=after.region)

            await self.logger_channel.send(embed=embed) 
        
    # Add additional checks for relevant guild changes
            
            
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):

        embed = nextcord.Embed(title='Role Created', color=nextcord.Color.green())
        embed.add_field(name='Role', value=role.mention)
        embed.add_field(name='Role ID', value=role.id)

        await self.logger_channel.send(embed=embed)

    @commands.Cog.listener() 
    async def on_guild_role_delete(self, role):

        embed = nextcord.Embed(title='Role Deleted', color=nextcord.Color.red())
        embed.add_field(name='Role', value=role.name)
        embed.add_field(name='Role ID', value=role.id)

        await self.logger_channel.send(embed=embed)       
            
            
            
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):

        if before.name != after.name:
            # Role name changed
            embed = nextcord.Embed(title='Role Name Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.name)
            embed.add_field(name='After', value=after.name)

            await self.logger_channel.send(embed=embed)

        if before.color != after.color:
            # Role color changed
            embed = nextcord.Embed(title='Role Color Updated', color=after.color)
            embed.add_field(name='Before', value=before.color)
            embed.add_field(name='After', value=after.color)

            await self.logger_channel.send(embed=embed)

    # Add checks for other role changes  
    
    
    
    
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):

        if len(before) < len(after):
            # New emojis added
            new = [e for e in after if e not in before]
            embed = nextcord.Embed(title='Emojis Added', color=nextcord.Color.green())
            embed.add_field(name='Emojis', value=', '.join([str(e) for e in new]))

        if len(before) > len(after):
            # Emojis removed
            removed = [e for e in before if e not in after]
            embed = nextcord.Embed(title='Emojis Removed', color=nextcord.Color.red())
            embed.add_field(name='Emojis', value=', '.join([str(e) for e in removed]))

        await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild, before, after):

        if len(before) < len(after):
            # New stickers added
            new = [s for s in after if s not in before]
            embed = nextcord.Embed(title='Stickers Added', color=nextcord.Color.green())
            embed.add_field(name='Stickers', value='\n'.join([str(s) for s in new]))

        if len(before) > len(after):
            # Stickers removed
            removed = [s for s in before if s not in after] 
            embed = nextcord.Embed(title='Stickers Removed', color=nextcord.Color.red())
            embed.add_field(name='Stickers', value='\n'.join([str(s) for s in removed]))

        await self.logger_channel.send(embed=embed)
            
            
        """
                   
    @commands.Cog.listener()
    async def on_guild_available(self, guild):

        embed = nextcord.Embed(title='Guild Available', color=nextcord.Color.green())
        embed.add_field(name='Guild', value=guild.name)
        embed.add_field(name='Guild ID', value=guild.id)
        embed.add_field(name='Region', value=guild.region)
        embed.add_field(name='Owner', value=guild.owner)

        await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):

        embed = nextcord.Embed(title='Guild Unavailable', color=nextcord.Color.red())
        embed.add_field(name='Guild', value=guild.name)
        embed.add_field(name='Guild ID', value=guild.id)
        embed.add_field(name='Region', value=guild.region)
        embed.add_field(name='Owner', value=guild.owner)

        await self.logger_channel.send(embed=embed) 
        
    """ 
            
            
    @commands.Cog.listener()
    async def on_stage_instance_create(self, stage_instance):

        embed = nextcord.Embed(title='Stage Channel Created', color=nextcord.Color.green())

        embed.add_field(name='Channel', value=stage_instance.channel.mention)
        embed.add_field(name='Topic', value=stage_instance.topic)
        embed.add_field(name='Privacy Level', value=stage_instance.privacy_level)
        
        speakers = ', '.join([m.mention for m in stage_instance.speakers])
        embed.add_field(name='Speakers', value=speakers)

        await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_stage_instance_delete(self, stage_instance):

        embed = nextcord.Embed(title='Stage Channel Deleted', color=nextcord.Color.red())

        embed.add_field(name='Channel', value=stage_instance.channel.mention)
        embed.add_field(name='Topic', value=stage_instance.topic)
        embed.add_field(name='Privacy Level', value=stage_instance.privacy_level)
        
        speakers = ', '.join([m.mention for m in stage_instance.speakers])
        embed.add_field(name='Speakers', value=speakers)

        await self.logger_channel.send(embed=embed)
            
    @commands.Cog.listener() # ! Additional logic could be added to check for changes in the speaker list and embed those as well.
    async def on_stage_instance_update(self, before, after):

        if before.topic != after.topic:
            # Stage channel topic updated
            embed = nextcord.Embed(title='Stage Channel Topic Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.topic)
            embed.add_field(name='After', value=after.topic)

            await self.logger_channel.send(embed=embed)

        if before.privacy_level != after.privacy_level:
            # Privacy level updated
            embed = nextcord.Embed(title='Stage Channel Privacy Updated', color=nextcord.Color.purple())
            embed.add_field(name='Before', value=before.privacy_level)
            embed.add_field(name='After', value=after.privacy_level)

            await self.logger_channel.send(embed=embed)

  # Check for speaker changes      
            
            
    @commands.Cog.listener()
    async def on_group_join(self, channel, user):

        embed = nextcord.Embed(title='User Joined Group', color=nextcord.Color.green())
        embed.add_field(name='Channel', value=channel.mention)
        embed.add_field(name='User', value=user.mention)

        await self.logger_channel.send(embed=embed)


    @commands.Cog.listener() # more metadata
    async def on_group_remove(self, channel, user):

        embed = nextcord.Embed(title='User Left Group', color=nextcord.Color.red())
        embed.add_field(name='Channel', value=channel.mention)
        embed.add_field(name='User', value=user.mention)

        await self.logger_channel.send(embed=embed)
            
            
    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event):

        embed = nextcord.Embed(title='Event Created', color=nextcord.Color.green())

        embed.add_field(name='Name', value=event.name)
        embed.add_field(name='Description', value=event.description)
        embed.add_field(name='Start Time', value=event.scheduled_start_time)
        embed.add_field(name='End Time', value=event.scheduled_end_time)
        embed.add_field(name='Status', value=event.status)

        await self.logger_channel.send(embed=embed)
            
            
    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(self, before, after):

        if before.name != after.name:
            # Name changed
            embed = nextcord.Embed(title='Event Name Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.name)
            embed.add_field(name='After', value=after.name)

            await self.logger_channel.send(embed=embed)

        if before.scheduled_start_time != after.scheduled_start_time:
            # Start time changed
            embed = nextcord.Embed(title='Event Start Time Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.scheduled_start_time)
            embed.add_field(name='After', value=after.scheduled_start_time)

            await self.logger_channel.send(embed=embed)

    # Check other relevant fields for changes


    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
    
        embed = nextcord.Embed(title='Event Deleted', color=nextcord.Color.red())

        embed.add_field(name='Name', value=event.name)
        embed.add_field(name='Scheduled Start Time', value=event.scheduled_start_time)

        await self.logger_channel.send(embed=embed) 
            
            
    @commands.Cog.listener() 
    async def on_guild_scheduled_event_user_add(self, event, user):

        embed = nextcord.Embed(title='User Added to Event', color=nextcord.Color.green())

        embed.add_field(name='Event', value=event.name)
        embed.add_field(name='User', value=user.mention)

        await self.logger_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_scheduled_event_user_remove(self, event, user):

        embed = nextcord.Embed(title='User Removed from Event', color=nextcord.Color.red())

        embed.add_field(name='Event', value=event.name)
        embed.add_field(name='User', value=user.mention)

        await self.logger_channel.send(embed=embed)
        
    @commands.Cog.listener() 
    async def on_auto_moderation_rule_create(self, rule):

        embed = nextcord.Embed(title='AutoMod Rule Created', color=nextcord.Color.green())

        embed.add_field(name='Rule', value=rule.name)
        embed.add_field(name='Rule ID', value=rule.id)
        embed.add_field(name='Creator', value=rule.creator.mention)

        await self.logger_channel.send(embed=embed)
            
            
            
    @commands.Cog.listener()
    async def on_auto_moderation_rule_update(self, before, after):

        if before.name != after.name:
            # Rule name updated
            embed = nextcord.Embed(title='AutoMod Rule Name Updated', color=nextcord.Color.blue())
            embed.add_field(name='Before', value=before.name)
            embed.add_field(name='After', value=after.name)

            await self.logger_channel.send(embed=embed)

        if before.enabled != after.enabled:
            # Enabled status changed
            embed = nextcord.Embed(title='AutoMod Rule Status Updated', color=nextcord.Color.orange())
            embed.add_field(name='Before', value=before.enabled)
            embed.add_field(name='After', value=after.enabled)

            await self.logger_channel.send(embed=embed)
    
  # Check other relevant fields for changes
  
  
  
  
    @commands.Cog.listener()
    async def on_auto_moderation_rule_delete(self, rule):

        embed = nextcord.Embed(title='AutoMod Rule Deleted', color=nextcord.Color.red())

        embed.add_field(name='Rule', value=rule.name)
        embed.add_field(name='Rule ID', value=rule.id)

        await self.logger_channel.send(embed=embed)
  
  

    @commands.Cog.listener()
    async def on_guild_audit_log_entry_create(self, entry):
        embed = nextcord.Embed(title='Audit Log Updated', color=nextcord.Color.dark_gold())

        user = entry.user
        embed.add_field(name='User', value=user.display_name)

        action = entry.action
        embed.add_field(name='Action', value=action.name)

        target = entry.target
        target_name = None

        if isinstance(target, nextcord.User):
            target_name = f"{target.name}#{target.discriminator}"

        elif isinstance(target, nextcord.Role):
            target_name = f"Role: {target.name}"

        elif isinstance(target, nextcord.TextChannel):
            target_name = f"Text Channel: {target.name}"

        elif isinstance(target, nextcord.VoiceChannel):
            target_name = f"Voice Channel: {target.name}"  

        elif isinstance(target, nextcord.CategoryChannel):
            target_name = f"Category: {target.name}"

        elif isinstance(target, nextcord.StageChannel):
            target_name = f"Stage Channel: {target.name}"
            
        elif isinstance(target, nextcord.Webhook):
            target_name = await self.fetch_webhook_name(target.id)
            if target_name is None:
                target_name = f"Unknown target (WIP) (ID: {target.id})"

        elif isinstance(target, nextcord.Thread):
            target_name = f"Thread: {target.name}"

        else:
            target_name = f"Unknown target (ID: {target.id})"

        embed.add_field(name='Target', value=target_name)

        await self.logger_channel.send(embed=embed)


  
  
  
  
  
  
  
  
  
  
  
                
    def cog_unload(self):
        self.save_config()

    # Add more event listeners here as per your requirements

def setup(bot):
    bot.add_cog(Logger(bot))
