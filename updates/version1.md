# Changelog

## Version 1.0.0

### New Features
- Added the `Logger` cog to log various events in a Discord server.
- Implemented the `setup` command to create a logger channel and configure permissions.
- Implemented event listeners to capture and log the following events:
    - `on_message`: Logs when a message is sent in a non-logger channel.
    - `on_message_delete`: Logs when a message is deleted in a non-logger channel.
    - `on_message_edit`: Logs when a message is edited in a non-logger channel.
    - `on_member_join`: Logs when a member joins the server.
    - `on_member_remove`: Logs when a member leaves the server.
    - `on_member_ban`: Logs when a member is banned from the server.
    - `on_member_unban`: Logs when a member is unbanned from the server.
    - `on_member_update`: Logs when a member's display name is changed.
    - `on_user_update`: Logs when a user's username is changed.
    - `on_guild_channel_create`: Logs when a new channel is created in the server.
    - `on_guild_channel_delete`: Logs when a channel is deleted from the server.
    - `on_guild_channel_update`: Logs when a channel is updated in the server.
    - `on_member_role_update`: Logs when a member's roles are added or removed.
    - `on_voice_state_update`: Logs when a member's voice state changes.
    - `on_guild_join`: Logs when the bot joins a new server.
    - `on_guild_remove`: Logs when the bot is removed from a server.
    - `on_guild_update`: Logs when the server's name is changed.
    - `on_invite_create`: Logs when an invite is created in the server.
    - `on_invite_delete`: Logs when an invite is deleted in the server.
    - `on_bulk_message_delete`: Logs when multiple messages are deleted in a non-logger channel.
    - `on_member_emojis_update`: Logs when a member's emojis are added or removed.
- Added the `DirectMessage` cog to handle the `directme` slash command.
- Implemented the `directmessage` function to send a message to the bot owner via DM and respond to the user in the server with an embed.
- Created a `config.json` file to store the logger channel ID for persistent configuration.
- Implemented the `load_config` and `save_config` functions to load and save the logger channel configuration.
- Added the `cog_unload` function to save the logger channel configuration when the cog is unloaded.
- Updated the `setup` function to check for an existing logger channel before creating a new one.
- Added appropriate embeds for logging various events, including message actions, member actions, channel actions, role actions, voice state changes, server actions, and invite actions.

### TODO
- [ ] Implement additional event listeners as per requirements.
- [ ] Refactor the code for improved readability and maintainability.
- [ ] Add error handling to handle potential exceptions.
- [ ] Enhance the logger channel configuration to support multiple guilds.
- [ ] Implement a command to customize the logger channel's name and permissions.
- [ ] Improve the formatting and appearance of embeds for better visual representation.
- [ ] Add logging of more specific information for each event type.
- [ ] Enhance the error logging mechanism for better debugging.
- [ ] Write comprehensive documentation and usage guide for the cog.
- [ ] Implement unit tests to ensure code reliability and stability.
- [ ] Gather user feedback and iterate on the cog's functionality based on suggestions.
- [ ] Consider adding support for logging events to external storage or databases(ex- MongoDB).

