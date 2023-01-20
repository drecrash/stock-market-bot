# Copyright 2022 Andre Prakash



import nextcord     
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import os
import json
import random
from random import randrange
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import difflib



class buysell(commands.Cog):
    def __init__(self, client):
        self.client = client




    def get_sell_data(self):
        with open("sell_orders.json","r") as f:
            data = json.load(f)

        return data

    def get_buy_data(self):
        with open("buy_orders.json","r") as f:
            data = json.load(f)

        return data


    def get_company_data(self):
        with open("company_data.json","r") as f:
            data = json.load(f)

        return data


    def get_user_data(self):
        with open("user_data.json","r") as f:
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



    async def give_money(self, user, company_name, shares, cost):
        data = self.get_user_data()
        self.open_user(user)

        if company_name not in data[str(user.id)]["shares"]:
            data[str(user.id)]["shares"][company_name] = 0


        data[str(user.id)]["shares"][company_name] -= shares
        data[str(user.id)]["balance"] += cost

        with open("user_data.json", "w") as f:
            json.dump(data,f, indent=4)

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
                print(value[1])
                if value[1] > highest_value:
                    highest_value = value[1]
                    highest_key = key

            return [highest_key, highest_value]  

    def get_server_data(self):
        with open("server_data.json","r") as f:
            data = json.load(f)

        return data


    @nextcord.slash_command(name = "instantbuy", description = "instantly buy stock of a company")
    async def instantbuy(self, interaction: Interaction, company_name, shares):
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
        guild = (interaction.guild)
        user = (interaction.user)
        self.open_user(user)
        shares = int(shares)
        originalShares = int(shares)
        failedExchange = False
        fullCost = 0
        money_error = False
        company_name = company_name.lower()

        await interaction.response.defer()


        if company_name not in companyData[str(guild.id)]:
            await interaction.followup.send("The company that you have entered is not a valid company, please open a ticket to validate a company")
        else:
            if company_name not in sellData:
                await interaction.followup.send(f"No sell orders have been made for {company_name}")
            else:
                if sellData[company_name] == {}:
                    await interaction.followup.send(f"No sell orders are currently open for {company_name}")
                else:

                    while shares > 0:
                        lowest_sell = await self.find_lowest_sell(company_name)
                        # lowest_sell[0] = str(user.id)
                        # lowest_sell[1] = [amt of shares, cost]

                        if lowest_sell == False:
                            failedExchange = True
                            break
                            

                        lowest_sell_person = await self.client.fetch_user(int(lowest_sell[0]))
                        share_available = int((sellData[company_name][lowest_sell[0]])[0])

                        
                        


                        if share_available == shares:
                            fullCost += ((sellData[company_name][lowest_sell[0]][1]) * share_available)
                            

                            if fullCost > userData[str(user.id)]["balance"]:
                                money_error = True
                                fullCost -= ((sellData[company_name][lowest_sell[0]][1]) * share_available)
                                break

                            # await self.give_money(lowest_sell_person, company_name, share_available, ((sellData[company_name][lowest_sell[0]][1]) * share_available))
                            userData[str(user.id)]["balance"] -= fullCost

                            await lowest_sell_person.send(f"Your sell order for {company_name} was filled! You sold {share_available} shares for ${(share_available * (sellData[company_name][lowest_sell[0]][1]))}")

                            if company_name not in userData[str(user.id)]["shares"].keys():
                                userData[str(user.id)]["shares"][company_name] = share_available
                                del sellData[company_name][lowest_sell[0]]
                            else:
                                userData[str(user.id)]["shares"][company_name] += share_available
                                del sellData[company_name][lowest_sell[0]]

                            

                            with open("sell_orders.json", "w") as f:
                                json.dump(sellData,f, indent=4)

                            with open("user_data.json", "w") as f:
                                json.dump(userData,f, indent=4)

                            

                            shares = 0

                            break

                        if share_available > shares:
#                            sellData[company_name][lowest_sell[0]] = [(((sellData[company_name][lowest_sell[0]])[0])-shares),(sellData[company_name][lowest_sell[0]])[1]]
                            currentShares = sellData[company_name][lowest_sell[0]][0]
                            sellData[company_name][lowest_sell[0]][0] = currentShares - shares
                            boughtShares = share_available - shares
                            boughtShares = currentShares - boughtShares
                            print(boughtShares)
                            fullCost += ((sellData[company_name][lowest_sell[0]][1]) * boughtShares)
                            
                            

                            if fullCost > userData[str(user.id)]["balance"]:
                                money_error = True
                                fullCost -= ((sellData[company_name][lowest_sell[0]][1]) * boughtShares)
                                break

                            userData[str(user.id)]["balance"] -= fullCost
                            # await self.give_money(lowest_sell_person, company_name, boughtShares, ((sellData[company_name][lowest_sell[0]][1]) * boughtShares))

                            with open("sell_orders.json", "w") as f:
                                json.dump(sellData,f, indent=4)

                            print("what the damn shares should be",sellData[company_name][lowest_sell[0]][0])

                            share_available = int((sellData[company_name][lowest_sell[0]])[0])
     

                            print(sellData[company_name][lowest_sell[0]])
                            if company_name not in userData[str(user.id)]["shares"].keys():
                                userData[str(user.id)]["shares"][company_name] = shares
                            else:
                                userData[str(user.id)]["shares"][company_name] += shares

                            await lowest_sell_person.send(f"Part of your sell order for {company_name} was filled! Just now, you sold {boughtShares} shares for ${(boughtShares * (sellData[company_name][lowest_sell[0]][1]))}")
                            

                            shares = 0

                        if share_available < shares:
                            
                            fullCost += (sellData[company_name][lowest_sell[0]][1] * share_available)
                            

                            if fullCost > userData[str(user.id)]["balance"]:
                                money_error = True
                                fullCost -= ((sellData[company_name][lowest_sell[0]][1]) * share_available)
                                break

                            # await self.give_money(lowest_sell_person, company_name, share_available, ((sellData[company_name][lowest_sell[0]][1]) * share_available))

                            og_shares_for_one_if_statement = shares

                            shares -= share_available


                            userData[str(user.id)]["balance"] -= fullCost

                            await lowest_sell_person.send(f"Your sell order for {company_name} was filled! You sold {share_available} shares for ${(share_available * (sellData[company_name][lowest_sell[0]][1]))}")

                            if company_name not in userData[str(user.id)]["shares"].keys():
                                userData[str(user.id)]["shares"][company_name] = og_shares_for_one_if_statement
                                del sellData[company_name][lowest_sell[0]]
                            else:
                                userData[str(user.id)]["shares"][company_name] += og_shares_for_one_if_statement
                                del sellData[company_name][lowest_sell[0]]

                            

                        print(shares)
                        print("Full Cost:",fullCost)                      

                        with open("sell_orders.json", "w") as f:
                            json.dump(sellData,f, indent=4)

                        with open("user_data.json", "w") as f:
                            json.dump(userData,f, indent=4)

                    fullCost = round(fullCost)

                    if failedExchange == True:
                        await interaction.followup.send(f"We were only able to purchase {originalShares-shares} shares. Total cost was ${fullCost}. Please try again later")
                    elif money_error == True:
                        await interaction.followup.send(f"You did not have sufficient funds to make the entirety of the purchase. You were able to purchase {originalShares-shares}/{originalShares} shares for ${fullCost}")
                    else:
                        await interaction.followup.send(f"We purchased {originalShares} shares of {company_name} for ${fullCost}")


    @nextcord.slash_command(name = "instantsell", description = "instantly sell stock of a company")
    async def instantsell(self, interaction: Interaction, company_name, shares):
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
        guild = (interaction.guild)
        user = (interaction.user)
        self.open_user(user)
        shares = int(shares)
        originalShares = int(shares)
        failedExchange = False
        fullCost = 0
        user_balance = userData[str(user.id)]["balance"]
        share_error = False
        company_name = company_name.lower()


        if company_name not in companyData[str(guild.id)]:
            await interaction.response.send_message("The company that you have entered is not a valid company, please open a ticket to validate a company")
        else:
            if company_name not in buyData:
                await interaction.response.send_message(f"No buy orders have been made for {company_name}")
            else:
                if buyData[company_name] == {}:
                    await interaction.response.send_message(f"No buy orders are currently open for {company_name}")
                else:
                    if (company_name not in userData[str(user.id)]["shares"]) or (shares > userData[str(user.id)]["shares"][company_name]):
                        share_error = True

                    else:

                        while shares > 0:
                            lowest_buy = await self.find_highest_buy(company_name)
                            # lowest_sell[0] = str(user.id)
                            # lowest_sell[1] = [amt of shares, cost]

                            if lowest_buy == False:
                                failedExchange = True
                                break
                                
                            print(lowest_buy)
                            lowest_buy_person = await self.client.fetch_user(int(lowest_buy[0]))
                            share_available = int((buyData[company_name][lowest_buy[0]])[0])

                            print(share_available,"shares available")

                            
                            


                            if share_available == shares:
                                fullCost += ((buyData[company_name][lowest_buy[0]][1]) * share_available)


                                await lowest_buy_person.send(f"Your buy order for {company_name} was filled! You bought {share_available} shares for ${(share_available * (buyData[company_name][lowest_buy[0]][1]))}")


                                if company_name not in userData[str(user.id)]["shares"].keys():
                                    userData[str(user.id)]["shares"][company_name] = share_available
                                    del buyData[company_name][lowest_buy[0]]
                                else:
                                    userData[str(user.id)]["shares"][company_name] -= share_available
                                    del buyData[company_name][lowest_buy[0]]

                                print("removed:",share_available)

                                with open("buy_orders.json", "w") as f:
                                    json.dump(buyData,f, indent=4)

                                with open("user_data.json", "w") as f:
                                    json.dump(userData,f, indent=4)

                                

                                shares = 0

                                break

                            elif share_available > shares:
    #                            sellData[company_name][lowest_sell[0]] = [(((sellData[company_name][lowest_sell[0]])[0])-shares),(sellData[company_name][lowest_sell[0]])[1]]
                                currentShares = buyData[company_name][lowest_buy[0]][0]
                                buyData[company_name][lowest_buy[0]][0] = currentShares - shares

                                 


                                fullCost += ((buyData[company_name][lowest_buy[0]][1]) * shares)

                                await lowest_buy_person.send(f"Your buy order for {company_name} was partially filled! Just now, you bought {shares} shares for ${(share_available * (buyData[company_name][lowest_buy[0]][1]))}")
                                

                                if fullCost > userData[str(user.id)]["balance"]:
                                    money_error = True
                                    fullCost -= ((buyData[company_name][lowest_buy[0]][1]) * shares)
                                    break


                                with open("buy_orders.json", "w") as f:
                                    json.dump(buyData,f, indent=4)

                                print("what the damn shares should be",buyData[company_name][lowest_buy[0]][0])

                                share_available = int((buyData[company_name][lowest_buy[0]])[0])
        

                                print(buyData[company_name][lowest_buy[0]])
                                if company_name not in userData[str(user.id)]["shares"].keys():
                                    userData[str(user.id)]["shares"][company_name] = shares
                                else:
                                    userData[str(user.id)]["shares"][company_name] -= shares

                                print("removed:",shares)


                                

                                shares = 0

                            elif share_available < shares:
                                
                                fullCost += (buyData[company_name][lowest_buy[0]][1] * share_available)

                                og_shares_for_one_if_statement = shares

                                print("og_shares:",og_shares_for_one_if_statement)

                                shares -= share_available

                                await lowest_buy_person.send(f"Your buy order for {company_name} was filled! You sold {share_available} shares for ${(share_available * (buyData[company_name][lowest_buy[0]][1]))}")


                                

                                if company_name not in userData[str(user.id)]["shares"].keys():
                                    userData[str(user.id)]["shares"][company_name] = share_available
                                    del buyData[company_name][lowest_buy[0]]
                                else:
                                    userData[str(user.id)]["shares"][company_name] -= share_available
                                    del buyData[company_name][lowest_buy[0]]

                                print("removed:",og_shares_for_one_if_statement)

                                

                            print("shares:",shares)
                            print("Full Cost:",fullCost)                      

                            with open("buy_orders.json", "w") as f:
                                json.dump(buyData,f, indent=4)

                            with open("user_data.json", "w") as f:
                                json.dump(userData,f, indent=4)


                    userData[str(user.id)]["balance"] += fullCost

                    with open("user_data.json", "w") as f:
                        json.dump(userData,f, indent=4)

                    if failedExchange == True:
                        await interaction.response.send_message(f"We were only able to sell {originalShares-shares} shares. Total sale was ${fullCost}. Please try again later")
                    elif share_error == True:
                        await interaction.response.send_message(f"You do not have enough shares to make this sale")
                    else:
                        await interaction.response.send_message(f"You sold {originalShares} shares of {company_name} for ${fullCost}")            



# while I was writing the code, I thought I would need two separate kinds of functions. one to match sell orders to buy orders, and one to match buy orders to sell orders
# i later realized that one matching algorithm would make it work
# but im too lazy to rename the functions so you get what you get

    async def single_sell_order_match(self, user_list, company): # match up a single sell order of a user to all the buy orders
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        if company in buyData:
            buy_user_list = list(buyData[company].keys())
            code_breaker = False

            for i in range(len(buyData[company].keys())):
                if code_breaker == False:
                    for x in range(len(user_list)):
                        user = await self.client.fetch_user(int(user_list[x]))

                        print("iteration:",x)
                        print('user:', user.id)

                        if str(user.id) in sellData[company]:
                            if sellData[company][str(user.id)][1] == buyData[company][buy_user_list[i]][1]: # check if they're buying and selling for the same cost
                                buyer = await self.client.fetch_user(int(buy_user_list[i]))
                                print("buyer:",buyer)
                                print("seller:",user)

                                
                                shares_needed = buyData[company][buy_user_list[i]][0]
                                shares_sold = sellData[company][str(user.id)][0]
                                cost_per_share = buyData[company][buy_user_list[i]][1]

                                if shares_needed == shares_sold:
                                    del sellData[company][str(user.id)]
                                    del buyData[company][buy_user_list[i]]

                                    if company not in userData[buy_user_list[i]]["shares"]:
                                        userData[buy_user_list[i]]["shares"][company] = 0

                                    userData[buy_user_list[i]]["shares"][company] += shares_sold

                                    userData[str(user.id)]["balance"] += (shares_sold * cost_per_share)

                                    await user.send(f"Your sell order for {company} was filled! You sold {shares_sold} shares for ${(shares_sold * cost_per_share)}")
                                    await buyer.send(f"Your buy order for {company} was filled! You bought {shares_sold} shares for ${(shares_sold * cost_per_share)}")

                                    buy_user_list.remove(buy_user_list[i])

                                elif shares_needed < shares_sold:
                                    sellData[company][str(user.id)][0] -= shares_needed
                                    del buyData[company][buy_user_list[i]]

                                    if company not in userData[buy_user_list[i]]["shares"]:
                                        userData[buy_user_list[i]]["shares"][company] = 0

                                    userData[buy_user_list[i]]["shares"][company] += shares_needed

                                    userData[str(user.id)]["balance"] += (shares_needed * cost_per_share)

                                    await buyer.send(f"Your buy order for {company} was filled! You bought {shares_needed} shares for ${(shares_needed * cost_per_share)}")

                                    buy_user_list.remove(buy_user_list[i])

                                elif shares_needed > shares_sold:
                                    buyData[company][buy_user_list[i]][0] -= shares_sold
                                    del sellData[company][str(user.id)]

                                    if company not in userData[buy_user_list[i]]["shares"]:
                                        userData[buy_user_list[i]]["shares"][company] = 0

                                    userData[buy_user_list[i]]["shares"][company] += shares_sold

                                    userData[str(user.id)]["balance"] += (shares_sold * cost_per_share)    

                                    await user.send(f"Your sell order for {company} was filled! You sold {shares_sold} shares for ${(shares_sold * cost_per_share)}")
                                    await buyer.send(f"Part of your buy order for {company} was filled! Just now, you bought {shares_sold} shares for ${(shares_sold * cost_per_share)}")

                                    buy_user_list.remove(buy_user_list[i])     

                                        
                            with open("buy_orders.json", "w") as f:
                                json.dump(buyData,f, indent=4)

                            with open("sell_orders.json", "w") as f:
                                json.dump(sellData,f, indent=4)

                            with open("user_data.json", "w") as f:
                                json.dump(userData,f, indent=4)

                        else:
                            code_breaker = True
                            break

                elif code_breaker == True:
                    break



    async def match_sell_orders(self, guild): # run this whenever a message is sent to match up sell orders to other sell orders
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
#        companyList = list(companyData[str(guild.id)].keys)

        companyList = []

        for key in companyData[str(guild.id)].keys():
            companyList.append(key)

        print(companyList)

        for i in range(len(companyList)):

            if companyList[i] not in sellData:
                continue
            else:

                all_users = list(sellData[companyList[i]].keys())

                for user in range(len(list(sellData[companyList[i]].keys()))):
                    await self.single_sell_order_match(all_users, companyList[i])





    @nextcord.slash_command(name = "createsellorder", description = "create a sell order for shares of a company")
    async def sellorder(self, interaction: Interaction, company_name, shares, cost_per_share: str = SlashOption(choices={"custom": 'c', "Lowest Sell": '0%', "Lowest Sell -1%": '1%', 'Lowest Sell -5%': '5%'},)):
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
        guild = (interaction.guild)
        user = (interaction.user)
        self.open_user(user)
        continue_function = True
        channel = (interaction.channel)
        custom_message = False
        company_name = company_name.lower()

        print(cost_per_share)


        if not shares.isdigit():
            await interaction.response.send_message("Invalid shares, please enter a number")
            continue_function = False
        else:
            shares = int(shares)


            if continue_function == True:

                if company_name not in companyData[str(guild.id)]:
                    await interaction.response.send_message("The company that you have entered is not a valid company, please open a ticket to validate a company")
                    continue_function = False
                if company_name not in sellData:
                    sellData[company_name] = {}
                    continue_function = True
                elif company_name not in userData[str(user.id)]["shares"]:
                    await interaction.response.send_message(f"You do not own any shares of {company_name}")
                    continue_function = False
                elif int(shares) > userData[str(user.id)]["shares"][company_name]:
                    await interaction.response.send_message(f"You don't own {shares} shares of {company_name}, please purchase more shares before making this sell order")
                    continue_function = False
                elif str(user.id) in sellData[company_name]:
                    await interaction.response.send_message(f"You already have a sell order open for {company_name}. Please close it, or wait for it to get filled, before creating another one")
                    continue_function = False

                if continue_function == True:

                    if cost_per_share == '0%':
                        cost_per_share = await self.find_lowest_sell(company_name)
                        if cost_per_share == False:
                            await interaction.response.send_message(f"No sell orders have been made for {company_name}. Please make a custom order")
                            continue_function = False
                        else:
                            cost_per_share = cost_per_share[1]


                    if cost_per_share == '1%':
                        cost_per_share = await self.find_lowest_sell(company_name)
                        if cost_per_share == False:
                            await interaction.response.send_message(f"No sell orders have been made for {company_name}. Please make a custom order")
                            continue_function = False
                        else:
                            cost_per_share = (cost_per_share[1] - (cost_per_share[1] * 0.01))

                    if cost_per_share == '5%':
                        cost_per_share = await self.find_lowest_sell(company_name)
                        if cost_per_share == False:
                            await interaction.response.send_message(f"No sell orders have been made for {company_name}. Please make a custom order")
                            continue_function = False
                        else:
                            cost_per_share = (cost_per_share[1] - (cost_per_share[1] * 0.05))

                    if cost_per_share == 'c':
                        await interaction.response.send_message(f"Please reply to this message with how much you would like each share to cost. Please do not use any symbols or non-arabic numerals")

                        def attributecheck(m):
                            return m.channel == channel and m.author == interaction.user and (m.content).isdigit() and int(m.content) >= 1

                        msg = await self.client.wait_for('message', check=attributecheck)
                        cost_per_share = int(msg.content)

                        custom_message = True


                    if continue_function == True:

                        sellData[company_name][str(user.id)] = [int(shares), int(cost_per_share)]
                        userData[str(user.id)]["shares"][company_name] -= shares

                        if custom_message == False:
                            await interaction.response.send_message(f"Created a sell order for {company_name}. {shares} shares for ${cost_per_share} each")
                        else:
                            await msg.reply(f"Created a sell order for {company_name}. {shares} shares for ${cost_per_share} each")

                        with open("sell_orders.json", "w") as f:
                            json.dump(sellData,f, indent=4)

                        with open("user_data.json", "w") as f:
                            json.dump(userData,f, indent=4)




    @nextcord.slash_command(name = "createbuyorder", description = "create a buy order for shares of a company")
    async def buyorder(self, interaction: Interaction, company_name, shares, cost_per_share: str = SlashOption(choices={"custom": 'c', "Lowest Buy": '0%', "Lowest Buy +1%": '1%', 'Lowest Buy +5%': '5%'},)):
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
        guild = (interaction.guild)
        user = (interaction.user)
        self.open_user(user)
        continue_function = True
        user_balance = userData[str(user.id)]["balance"]
        channel = (interaction.channel)
        custom_message = False
        company_name = company_name.lower()

        if not shares.isdigit():
            await interaction.response.send_message("Invalid shares, please enter a number")
            continue_function = False
        else:
            shares = int(shares)

        if continue_function == True:

            if company_name not in companyData[str(guild.id)]:
                await interaction.response.send_message("The company that you have entered is not a valid company, please open a ticket to validate a company")
                continue_function = False
            if company_name not in buyData:
                buyData[company_name] = {}
                continue_function = True
            elif str(user.id) in buyData[company_name]:
                await interaction.response.send_message(f"You already have a buy order open for {company_name}. Please close it, or wait for it to get filled, before creating another one")
                continue_function = False

            if continue_function == True:
                if cost_per_share == '0%':
                    cost_per_share = await self.find_highest_buy(company_name)
                    if cost_per_share == False:
                        await interaction.response.send_message(f"No buy orders have been made for {company_name}. Please make a custom order")
                        continue_function = False
                    else:
                        cost_per_share = cost_per_share[1]
                        if (cost_per_share * shares) > user_balance:
                            await interaction.response.send_message(f"You do not have enough money to make this purchase")
                            continue_function = False



                if cost_per_share == '1%':
                    cost_per_share = await self.find_highest_buy(company_name)
                    if cost_per_share == False:
                        await interaction.response.send_message(f"No buy orders have been made for {company_name}. Please make a custom order")
                        continue_function = False
                    else:
                        cost_per_share = (cost_per_share[1] + (cost_per_share[1] * 0.01))
                        if (cost_per_share * shares) > user_balance:
                            await interaction.response.send_message(f"You do not have enough money to make this purchase")
                            continue_function = False

                if cost_per_share == '5%':
                    cost_per_share = await self.find_highest_buy(company_name)
                    print(cost_per_share)
                    if cost_per_share == False:
                        await interaction.response.send_message(f"No buy orders have been made for {company_name}. Please make a custom order")
                        continue_function = False
                    else:
                        cost_per_share = (cost_per_share[1] + (cost_per_share[1] * 0.05))
                        if (cost_per_share * shares) > user_balance:
                            await interaction.response.send_message(f"You do not have enough money to make this purchase")
                            continue_function = False

                if cost_per_share == 'c':
                    await interaction.response.send_message(f"Please reply to this message with how much you would like each share to cost. Please do not use any symbols or non-arabic numerals")

                    def attributecheck(m):
                        return m.channel == channel and m.author == interaction.user and (m.content).isdigit() and int(m.content) >= 1

                    msg = await self.client.wait_for('message', check=attributecheck)
                    cost_per_share = int(msg.content)

                    if (cost_per_share * shares) > user_balance:
                        await interaction.response.send_message(f"You do not have enough money to make this purchase")
                        continue_function = False

                    custom_message = True

                if continue_function == True:
                    buyData[company_name][str(user.id)] = [int(shares), int(cost_per_share)]
                    userData[str(user.id)]["balance"] -= (shares*cost_per_share)

                    if custom_message == False:
                        await interaction.response.send_message(f"Created a buy order for {company_name}. {shares} shares for ${cost_per_share} each. Total cost is ${(shares*cost_per_share)}")
                    else:
                        await msg.reply(f"Created a buy order for {company_name}. {shares} shares for ${cost_per_share} each. Total cost is ${(shares*cost_per_share)}")

                    with open("buy_orders.json", "w") as f:
                        json.dump(buyData,f, indent=4)

                    with open("user_data.json", "w") as f:
                        json.dump(userData,f, indent=4)



    @nextcord.slash_command(name = "closesellorder", description = "close a sell order for a company")
    async def closesellorder(self, interaction: Interaction, company_name):
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
        guild = (interaction.guild)
        user = (interaction.user)
        self.open_user(user)
        company_name = company_name.lower()

        if company_name not in sellData:
            await interaction.response.send_message("The company that you have entered is not a valid company, please open a ticket to validate a company")
        elif str(user.id) not in sellData[company_name]:
            await interaction.response.send_message(f"You do not currently have a sell order open for {company_name}")
        else:
            all_shares = sellData[company_name][str(user.id)][0]
            userData[str(user.id)]["shares"][company_name] += all_shares
            del sellData[company_name][str(user.id)]

            await interaction.response.send_message(f"You have closed your sell order for {company_name}. All non-sold shares ({all_shares} shares) have been returned")

            with open("user_data.json", "w") as f:
                json.dump(userData,f, indent=4)            

            with open("sell_orders.json", "w") as f:
                json.dump(sellData,f, indent=4)


        
    @nextcord.slash_command(name = "closebuyorder", description = "close a buy order for a company")
    async def closebuyorder(self, interaction: Interaction, company_name):
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()
        userData = self.get_user_data()
        companyData = self.get_company_data()
        guild = (interaction.guild)
        user = (interaction.user)
        self.open_user(user)
        company_name = company_name.lower()

        if company_name not in buyData:
            await interaction.response.send_message("The company that you have entered is not a valid company, please open a ticket to validate a company")
        elif str(user.id) not in buyData[company_name]:
            await interaction.response.send_message(f"You do not currently have a buy order open for {company_name}")
        else:
            total_cost = ((buyData[company_name][str(user.id)][0]) * (buyData[company_name][str(user.id)][1]))
            userData[str(user.id)]["balance"] += total_cost
            del buyData[company_name][str(user.id)]

            await interaction.response.send_message(f"You have closed your buy order for {company_name}. All not-spent money (${total_cost}) has been returned")

            with open("user_data.json", "w") as f:
                json.dump(userData,f, indent=4)            

            with open("buy_orders.json", "w") as f:
                json.dump(buyData,f, indent=4)


    async def update_sheet(self, sheet, guild, channel_id):
        buyData = self.get_buy_data()
        companyData = self.get_company_data()
        company_list = list(companyData[str(guild.id)].keys())
        sheet.clear()
        message_exist = False
        message_thing = None
        sellData = self.get_sell_data()
        buyData = self.get_buy_data()

        sheet.append_row(['Company Name','Highest Buy','Lowest Sell','Total Buy','Total Sell'])

        for key in company_list:
            company = key
            lowest_sell = await self.find_lowest_sell(key)
            highest_buy = await self.find_highest_buy(key)


            

            if lowest_sell == False:
                lowest_sell = [None,0]
                sheet_sell_list = []
            else:
                sheet_sell_list = list(sellData[company].keys())

            if highest_buy == False:
                highest_buy = [None,0]
                sheet_buy_list = []
            else:
                sheet_buy_list = list(buyData[company].keys())


            sheet.append_row([company, highest_buy[1], lowest_sell[1], str(len(sheet_buy_list)), str(len(sheet_sell_list))])

        channel = self.client.get_channel(channel_id)

        async for message in channel.history(limit=100):
            if message.author.bot:
                message_exist = True
                message_thing = message
                break
        
        if message_exist == False:
            company_string = ''
            company_string += 'Company Name - Highest Buy - Lowest Sell - Total Buy - Total Sell\n\n'

            for i in range(len(company_list)):

                print(company_list[i])

                lowest_sell = await self.find_lowest_sell(company_list[i])
                highest_buy = await self.find_highest_buy(company_list[i])

                if lowest_sell == False:
                    lowest_sell = [None,0]
                    sheet_sell_list = []
                else:
                    sheet_sell_list = list(sellData[company].keys())

                if highest_buy == False:
                    highest_buy = [None,0]
                    sheet_buy_list = []
                else:
                    sheet_buy_list = list(buyData[company].keys())



                msg_sell_list = list(sellData[company].keys())
                msg_buy_list = list(buyData[company].keys())                
                
                company_string += f'{(company_list[i]).capitalize()} - {highest_buy[1]} - {lowest_sell[1]} - {str(len(msg_buy_list))} - {str(len(msg_sell_list))}\n'

            await channel.send(company_string)

        elif message_exist == True:
            company_string = ''
            company_string += 'Company Name - Highest Buy - Lowest Sell - Total Buy - Total Sell\n\n'





            for i in range(len(company_list)):

                lowest_sell = await self.find_lowest_sell(company_list[i])
                highest_buy = await self.find_highest_buy(company_list[i])

                if lowest_sell == False:
                    lowest_sell = [None,0]
                    msg_sell_list = []
                else:
                    msg_sell_list = list(sellData[company].keys())

                if highest_buy == False:
                    highest_buy = [None,0]
                    msg_buy_list = []
                else:
                    msg_buy_list = list(buyData[company].keys())


                company_string += f'{(company_list[i]).capitalize()} - {highest_buy[1]} - {lowest_sell[1]} - {str(len(msg_buy_list))} - {str(len(msg_sell_list))}\n'

            await message_thing.edit(company_string)



        

    
    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author
        guild = message.guild
        serverData = self.get_server_data()

        if not user.bot:
            self.open_user(user)
            if randrange(5) == 3:
                await self.match_sell_orders(guild)   
            if randrange(2) == 1:
                scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                client2 = gspread.authorize(creds)

                spreadsheet = client2.open("Blitio Stock Market Bot").sheet1

                print('sheet')

                await self.update_sheet(spreadsheet, guild, serverData[str(guild.id)]["channel"])







def setup(client):
    client.add_cog(buysell(client))