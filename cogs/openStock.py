import nextcord     
from nextcord.ext import commands
from nextcord import Interaction
import os
import json
import random
import asyncio


class openStock(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_company_data(self):
        with open("company_data.json","r") as f:
            data = json.load(f)

        return data

    def open_company_data(self, guild):
        data = self.get_company_data()

        if str(guild.id) in data:
            return False
        else:
            data[str(guild.id)] = {}

        with open("company_data.json", "w") as f:
            json.dump(data,f, indent=4)

    def get_sell_data(self):
        with open("sell_orders.json","r") as f:
            data = json.load(f)

        return data

    def get_user_data(self):
        with open("user_data.json","r") as f:
            data = json.load(f)

        return data

    def get_server_data(self):
        with open("server_data.json","r") as f:
            data = json.load(f)

        return data

    def open_user(self, user):
        data = self.get_user_data()

        if str(user.id) not in data:
            data[str(user.id)] = {}
            data[str(user.id)]["shares"] = {}
            data[str(user.id)]["balance"] = 0
            data[str(user.id)]["companies"] = {}
        else:
            return False

        with open("user_data.json", "w") as f:
            json.dump(data,f, indent=4)

    @nextcord.slash_command(name="close-ticket", description = "Close a company ticket")
    async def closeticket(self, interaction: Interaction):
        user = (interaction.user)
        guild = (interaction.guild)
        channel = (interaction.channel)
        sellData = self.get_sell_data()
        userData = self.get_user_data()
        serverData = self.get_server_data()
        officer_role = nextcord.utils.get(guild.roles, name=serverData[str(guild.id)]["officer"])

        if officer_role in user.roles:
            if 'ticket' in str(channel):
                await interaction.response.send_message("Deleting channel in 5 seconds")
                await asyncio.sleep(5)
                await channel.delete()
            else:
                await interaction.response.send_message(f"<#{channel.id}> is not a ticket channel")



    @nextcord.slash_command(name="register-company", description = "Register a company into the stock market")
    async def registercompany(self, interaction: Interaction, name, percentage, ipo, owner: nextcord.User):
        user = (interaction.user)
        guild = (interaction.guild)
        sellData = self.get_sell_data()
        userData = self.get_user_data()
        serverData = self.get_server_data()
        officer_role = nextcord.utils.get(guild.roles, name=serverData[str(guild.id)]["officer"])
        data = self.get_company_data()
        self.open_company_data(guild)
        self.open_user(owner)
        user_company_list = userData[str(owner.id)]["companies"]
        worth_per_share = 0.0001

        percentage = float(percentage)
        ipo = int(ipo)

        total_shares_sold = round((int(percentage)/100) * (1/worth_per_share))
        total_cost = round(((percentage/100) * (1/worth_per_share) * int(ipo)))

        if officer_role in user.roles:
            if name in data[str(guild.id)].keys():
                await interaction.response.send_message("Your company is already registered")

            else:
                data[str(guild.id)][name] = {}
                data[str(guild.id)][name]["percentage"] = float(percentage)
                data[str(guild.id)][name]["ipo"] = int(round(float(ipo)))
                data[str(guild.id)][name]["owner"] = str(owner.id)
                data[str(guild.id)][name]["price"] = int(round(float(ipo)))
                
                userData[str(owner.id)]["companies"][name] = 1

                sellData[name] = {}
                sellData[name][str(owner.id)] = [total_shares_sold,ipo]

                with open("company_data.json", "w") as f:
                    json.dump(data,f, indent=4)

                with open("user_data.json", "w") as f:
                    json.dump(userData,f, indent=4)

                with open("sell_orders.json", "w") as f:
                    json.dump(sellData,f, indent=4)

                await interaction.response.send_message(f'The company "{name}" has been registered with {percentage}% of the company being sold. The IPO price is ${ipo} \nMade a sell order for: {total_shares_sold} shares\nTotal cost: {total_cost}')

        else:
            pass

    @nextcord.slash_command(name = "test", description = "make sure the bot works")
    async def test(self, interaction: Interaction):
        await interaction.response.send_message("Hello")


    @nextcord.slash_command(name = "eightball", description = "Predict your future")
    async def eightball(self, interaction: Interaction, question):
        options = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely", "You may rely on it", "Most likely", "Outlook good", "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later",
                "Better not tell you now", "Cannot predict now", "Concentrate and ask again", "Don't count on it",
                "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful", "lmao no XD"]
        ranVal = random.choice(options)
        await interaction.response.send_message(ranVal)

def setup(client):
    client.add_cog(openStock(client))