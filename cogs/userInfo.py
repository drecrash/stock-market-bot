# Copyright 2023, Andre Prakash, All rights reserved.


import nextcord     
from nextcord.ext import commands
from nextcord import Interaction
import os
import json
import random

class userInfo(commands.Cog):
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


    def open_server(self, guild):
        serverData = self.get_server_data()

        if str(guild.id) not in serverData:
            serverData[str(guild.id)] = {}  
            serverData[str(guild.id)]['officer'] = None
            serverData[str(guild.id)]['channel'] = None
            serverData[str(guild.id)]['sheet'] = None

            with open("server_data.json", "w") as f:
                json.dump(serverData,f, indent=4)

        else:
            return False

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

    @nextcord.slash_command(name = "define-officer-role", description = "Define the financial officer role")
    async def officerrole(self, interaction: Interaction, role: nextcord.Role):
        guild = (interaction.guild)
        self.open_server(guild)
        user = (interaction.user)
        self.open_user(user)
        serverData = self.get_server_data()
        self.open_company_data(guild)

        if user.guild_permissions.administrator:
            serverData[str(guild.id)]['officer'] = str(role.name)
            await interaction.response.send_message(f"Assigned the officer role to {role.mention}")

            with open("server_data.json", "w") as f:
                json.dump(serverData,f, indent=4)

        else:
            await interaction.response.send_message("This command is only available to those with admin permissions")


    @nextcord.slash_command(name = "define-stocks-channel", description = "Define the channel where the stock details are")
    async def stockschannel(self, interaction: Interaction, channel: nextcord.abc.GuildChannel):
        guild = (interaction.guild)
        self.open_server(guild)
        user = (interaction.user)
        self.open_user(user)
        serverData = self.get_server_data()
        self.open_company_data(guild)

        if user.guild_permissions.administrator:
            serverData[str(guild.id)]['channel'] = channel.id
            await interaction.response.send_message(f"Assigned the stocks channel to <#{channel.id}>")

            with open("server_data.json", "w") as f:
                json.dump(serverData,f, indent=4)

        else:
            await interaction.response.send_message("This command is only available to those with admin permissions")


    @nextcord.slash_command(name = "define-spreadsheet-name", description = "Define the name of your spreadsheet")
    async def sheetname(self, interaction: Interaction, name):
        guild = (interaction.guild)
        self.open_server(guild)
        user = (interaction.user)
        self.open_user(user)
        serverData = self.get_server_data()
        self.open_company_data(guild)

        if user.guild_permissions.administrator:
            serverData[str(guild.id)]['sheet'] = name
            await interaction.response.send_message(f"Assigned the spreadsheet name to {name}")

            with open("server_data.json", "w") as f:
                json.dump(serverData,f, indent=4)

        else:
            await interaction.response.send_message("This command is only available to those with admin permissions")




    @nextcord.slash_command(name = "portfolio", description = "View a member's portfolio")
    async def portfolio(self, interaction: Interaction, member: nextcord.User):
        userData = self.get_user_data()
        member_name = (str(member).split('#'))[0]
        channel = (interaction.channel)
        balance = str(userData[str(member.id)]["balance"])

        portfolioStartEmb = nextcord.Embed(title=f"{member_name}'s Portfolio", description=f"{member_name}'s balance, shares, and companies", color=nextcord.Color.blurple())
        portfolioStartEmb.add_field(name="Balance:",value=f"${balance}")

        sharesString = ''
        companyString = ''
        allCompanies = list(userData[str(member.id)]["companies"].keys())

        for key, value in userData[str(member.id)]["shares"].items():
            sharesString += f'• {key.capitalize()}: {value} shares \n'

        for i in range(len(allCompanies)):
            companyString += f'• {(allCompanies[i]).capitalize()} \n'


        portfolioStartEmb.add_field(name="Shares: ",value=sharesString)
        portfolioStartEmb.add_field(name=f"{member_name}'s Companies: ",value=companyString)

        await interaction.response.send_message(embed = portfolioStartEmb)

     
        
        # second_message = await first_message.reply(embed=shareEmb)

        # first_message = await channel.send(embed=portfolioStartEmb)

        # if userData[str(member.id)]["shares"] == {}:
        #     second_message = await first_message.reply(f"{member_name} has not invested in any companies")
        # else:
        #     shareEmb = nextcord.Embed(title=f"{member_name}'s Shares", description=f"Companies {member_name} has invested in", color=nextcord.Color.blurple())

        #     for key, value in userData[str(member.id)]["shares"].items():
        #         shareEmb.add_field(name=f"{key}:", value=f"{value} shares")        
            
        #     second_message = await first_message.reply(embed=shareEmb)

        # if userData[str(member.id)]["companies"] != {}:
        #     companyEmb = nextcord.Embed(title=f"{member_name}'s Companies", description=f"Companies {member_name} has made public", color=nextcord.Color.blurple())

        #     allCompanies = list(userData[str(member.id)]["companies"].keys())

        #     for i in range(len(allCompanies)):
        #         companyEmb.add_field(name=allCompanies[i], value="\u200b")


        #     last_message = await second_message.reply(embed = companyEmb)

    @nextcord.slash_command(name = "deposit-money", description = "Deposit money to a user")
    async def depositmoney(self, interaction: Interaction, member: nextcord.User, amount):
        userData = self.get_user_data()
        user = (interaction.user)
        guild = (interaction.guild)
        self.open_user(user)
        serverData = self.get_server_data()
        officer_role = nextcord.utils.get(guild.roles, name=serverData[str(guild.id)]["officer"])

        if officer_role in user.roles:
            userData[str(member.id)]["balance"] += int(amount)

            await interaction.response.send_message(f"Deposited ${amount} into {member.mention}'s balance")

            with open("user_data.json", "w") as f:
                json.dump(userData,f, indent=4)
        else:
            await interaction.response.send_message("This command is only available for financial officers")

    @nextcord.slash_command(name = "withdraw-money", description = "Withdraw money from a user")
    async def withdrawmoney(self, interaction: Interaction, member: nextcord.User, amount):
        userData = self.get_user_data()
        user = (interaction.user)
        guild = (interaction.guild)
        self.open_user(user)
        serverData = self.get_server_data()
        officer_role = nextcord.utils.get(guild.roles, name=serverData[str(guild.id)]["officer"])

        if officer_role in user.roles:
            userData[str(member.id)]["balance"] -= int(amount)

            await interaction.response.send_message(f"Withdrew ${amount} from {member.mention}'s balance")

            with open("user_data.json", "w") as f:
                json.dump(userData,f, indent=4)
        else:
            await interaction.response.send_message("This command is only available for financial officers")

    





def setup(client):
    client.add_cog(userInfo(client))
