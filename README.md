 **Fetch: A Discord Bot for Exporting Logs and Converting to PDF**

Fetch is a powerful and easy-to-use Discord bot that allows you to export channel messages into JSON files and convert them into readable PDFs. Fetch also supports exporting logs from multiple channels and provides real-time progress updates when handling large datasets.

**Invite Fetch to Your Server**

To start using Fetch, [click here to invite the bot to your server](https://discord.com/oauth2/authorize?client_id=1288164576629882962&permissions=274878024832&integration_type=0&scope=bot).

**Required Permissions**

To function properly, make sure Fetch has the following permissions in your server:
- `Read Messages`
- `Send Messages`
- `Attach Files`
- `Manage Messages` (only if you need Fetch to delete or modify messages)

**Commands**

**1. Export Logs**
Fetch allows you to export channel messages as a JSON file:

!fetch_logs [optional_channel_name]

- If no channel name is provided, Fetch will export logs from the current channel.
- Once the export is complete, the JSON file will be uploaded to the channel.

**2. Export Logs to PDF**
Convert the exported JSON logs into a PDF file:

!export_to_pdf

- You must attach the previously generated JSON file when using this command. Fetch will process the file and return a PDF of the logs.

**3. Export Multiple Channels**
Fetch supports exporting logs from multiple channels in one command:

!fetch_logs channel1 channel2 channel3

- Logs from each specified channel will be exported and included in the output file.

**Real-time Progress Updates**
For large-scale exports, Fetch will provide progress updates in the form of percentage completion messages, so you'll always know how much longer the export will take.


Now Fetch is ready to be added and used in your server! For further customization or issues, feel free to contact the developer via GitHub.

