import nextcord     
from nextcord.ext import commands
from nextcord import Interaction
import os
import json
from dotenv import load_dotenv # you don't need this unless you're loading from a .env file

def getvar():
    load_dotenv()

getvar()

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

os.chdir(os.getenv('cogs_path'))

initial_extentions = []

client.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initial_extentions.append("cogs."+filename[:-3])
 
if __name__ == '__main__':
    for extention in initial_extentions:
        client.load_extension(extention)

# Persistent view code taken from https://github.com/nextcord/nextcord/blob/stable/examples/views/persistent.py
class openTicket(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    def get_server_data(self):
        with open("server_data.json","r") as f:
            data = json.load(f)

        return data

    @nextcord.ui.button(label = "Open Ticket", style=nextcord.ButtonStyle.green, custom_id="persistent_view:button")
    async def openticketbutton(self, button: nextcord.ui.Button, interaction: Interaction):
        user = (interaction.user)
        guild = (interaction.guild)
        user_name = (str(user).split('#'))[0]
        channel = (interaction.channel)
        channel_name = f"{((user_name).lower()).replace(' ','-')}s-stock-ticket"
        serverData = self.get_server_data()
        officer_role = nextcord.utils.get(guild.roles, name=serverData[str(guild.id)]["officer"])
        print(channel_name)
        
        check_channel = nextcord.utils.get(guild.channels, name=channel_name)
        print(check_channel)
        if check_channel != None:
            await user.send("It looks like you already have a ticket open, make sure to close that one before you open another!")
        else:
            overwrites = {guild.default_role: nextcord.PermissionOverwrite(read_messages=False), 
            user: nextcord.PermissionOverwrite(read_messages=True),
            officer_role: nextcord.PermissionOverwrite(read_messages=True)}
        
            channel = await guild.create_text_channel(channel_name, category=channel.category, overwrites=overwrites)
            print(str(channel))


class Bot(commands.Bot):
    def __init__(self):
        intents = nextcord.Intents.all()

        super().__init__(command_prefix='!', intents=intents)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            # Register the persistent view for listening here.
            # Note that this does not send the view to any message.
            # To do that, you need to send a message with the View as shown below.
            # If you have the message_id you can also pass it as a keyword argument, but for this example
            # we don't have one.
            self.add_view(openTicket())
            self.persistent_views_added = True

        print(f"Logged in as {self.user} (ID: {self.user.id})")

client = Bot()

os.chdir(r'C:\Users\Andre Prakash\Downloads\Stock Market Bot for Blitio')

initial_extentions = []

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initial_extentions.append("cogs."+filename[:-3])

if __name__ == '__main__':
    for extention in initial_extentions:
        client.load_extension(extention)


def get_server_data():
    with open("server_data.json","r") as f:
        data = json.load(f)

    return data

@client.slash_command()
async def opencompanyticket(interaction):
    guild = (interaction.guild)
    user = (interaction.user)
    serverData = get_server_data()
    officer_role = nextcord.utils.get(guild.roles, name=serverData[str(guild.id)]["officer"])

    if officer_role in user.roles:
        await interaction.send("Click the button below to register your own public company!", view=openTicket())

client.run(os.getenv('discord_bot_token'))