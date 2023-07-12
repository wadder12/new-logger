```
# Logger Bot

Logger Bot is a Discord bot that logs various events in a server. It provides a logging feature to keep track of important activities and changes happening within the server.

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies by running the following command:
   ```

   pip install -r requirements.txt

   ```
3. Create a new file named `config.json` in the root directory and add the following content:
   ```json
   {
       "token": "YOUR_DISCORD_BOT_TOKEN",
       "logger_channel": null
   }
   ```

   Replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord bot token.
4. Run the bot by executing the following command:

   ```
   python main.py
   ```

## Usage

To use the Logger Bot, invite it to your server and make sure it has the necessary permissions to access the channels and perform the logging activities.

### Commands

- `qsetup`: Sets up the logger channel in your server. Only users with administrator permissions can use this command.

### Event Listeners

The Logger Bot listens to the following events:

- Message events: Logs messages sent, edited, and deleted by members.
- Member events: Logs member join, leave, ban, unban, update, and emoji update events.
- Channel events: Logs channel create, delete, and update events.
- Guild events: Logs guild join, leave, and update events.
- Invite events: Logs invite create and delete events.
- Voice State events: Logs voice state updates of members.
- Bulk Message Delete events: Logs bulk message deletion events.
- Member Emojis Update events: Logs member emoji add and remove events.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
```
