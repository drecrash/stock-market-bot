import nextcord     
from nextcord.ext import commands
from nextcord import Interaction
import os
import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class spreadsheet(commands.Cog):
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

    def get_buy_data(self):
        with open("buy_orders.json","r") as f:
            data = json.load(f)

        return data

    def get_user_data(self):
        with open("user_data.json","r") as f:
            data = json.load(f)

        return data

    async def find_lowest_sell(self, name):
        data = self.get_sell_data()

        lowest_value = float('inf')
        lowest_key = None


        if name not in data:
            return False

        elif data[name] == {}:
            return False
        else:

            for key, value in data[name].items():
                # Check if the current value is lower than the lowest value seen so far
                if value[1] < lowest_value:
                    lowest_value = value[1]
                    lowest_key = key

            return [lowest_key, lowest_value]  

    async def find_highest_buy(self, name):
        data = self.get_buy_data()

        highest_value = 0
        highest_key = None

        if name not in data:
            return False

        elif data[name] == {}:
            return False
        else:
            for key, value in data[name].items():
                if value[1] > highest_value:
                    highest_value = value[1]
                    highest_key = key

            return [highest_key, highest_value]  



    async def update_sheet(self, sheet, guild, channel_id):
        buyData = self.get_buy_data()
        companyData = self.get_company_data()
        company_list = list(companyData[str(guild.id)].keys())
        sheet.clear()
        message_exist = False
        message_thing = None

        sheet.append_row(['Company Name','Highest Buy','Lowest Sell'])

        for key in company_list:
            company = key
            lowest_sell = await self.find_lowest_sell(key)
            highest_buy = await self.find_highest_buy(key)

            channel = self.client.get_channel(channel_id)

            if lowest_sell == False:
                lowest_sell = [None,0]
            if highest_buy == False:
                highest_buy = [None,0]


            sheet.append_row([company, highest_buy[1], lowest_sell[1]])


        async for message in channel.history(limit=100):
            if message.author.bot:
                message_exist = True
                message_thing = message
                break
        
        if message_exist == False:
            company_string = ''
            company_string += 'Company Name - Highest Buy - Lowest Sell\n'

            for i in range(len(company_list)):

                print(company_list[i])

                if lowest_sell == False:
                    lowest_sell = [None,0]
                if highest_buy == False:
                    highest_buy = [None,0]

                lowest_sell = await self.find_lowest_sell(company_list[i])
                highest_buy = await self.find_highest_buy(company_list[i])
                
                company_string += f'{company_list[i]} - {highest_buy[1]} - {lowest_sell[1]}\n'

            await channel.send(company_string)

        elif message_exist == True:
            company_string = ''
            company_string += 'Company Name - Highest Buy - Lowest Sell\n\n'





            for i in range(len(company_list)):

                lowest_sell = await self.find_lowest_sell(company_list[i])
                highest_buy = await self.find_highest_buy(company_list[i])

                if lowest_sell == False:
                    lowest_sell = [None,0]
                if highest_buy == False:
                    highest_buy = [None,0]

                company_string += f'{company_list[i]} - {highest_buy[1]} - {lowest_sell[1]}\n'

            await message_thing.edit(company_string)



        


            

    @nextcord.slash_command(name = "testsheet", description = "Test spreadsheet")
    async def testsheet(self, interaction: Interaction):
        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client2 = gspread.authorize(creds)

        print('m')

        guild = (interaction.guild)

        spreadsheet = client2.open("Blitio Stock Market Bot").sheet1

        await self.update_sheet(spreadsheet, guild, 1064389234812788736)


def setup(client):
    client.add_cog(spreadsheet(client))