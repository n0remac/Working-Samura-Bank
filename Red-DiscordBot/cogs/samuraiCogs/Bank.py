import json
import discord
from discord.ext import commands

def setup(bot):
	bot.add_cog(BankCog(bot))

class BankCog:
	def __init__(self, bot):
		self.bot = bot
		self.centralBank=Bank()

	@commands.command()
	async def accounts(self):
		await self.bot.say(self.centralBank.getAccountList())

	@commands.command()
	async def createAccount(self, name):
		self.centralBank.createAccount(name)
		await self.bot.say("Created account named "+name)

	@commands.command()
	async def deposit(self, name, num):
		self.centralBank.deposit(name, num)
		await self.bot.say(str(self.centralBank.getAmount(name))+" is in the account")

	@commands.command()
	async def withdraw(self, name, num):
		money=self.centralBank.withdraw(name, num)
		await self.bot.say("Here is "+money+" don't lose it.")

	@commands.command()
	async def show(self, name):
		amt=self.centralBank.getAmount(name)
		await self.bot.say(amt)


class Bank:
	def __init__(self):
		self.accountList={}
		self.currency="$"
		try:
			self.load()
		except:
			self.save()
			self.load()

	def createAccount(self, name):
		self.accountList.update({name: 0})
		self.save()

	def getAmount(self, name):
		return self.accountList.get(name)

	def getAccountList(self):
		return self.accountList

	def deposit(self, name, num):
		self.accountList[name]+=int(num)
		self.save()
	
	def withdraw(self, name, num):
		self.accountList[name] -= int(num)
		self.save()
		return num

	def save(self):
		with open('/home/cameron/Projets/Red-DiscordBot/cogs/bank.json','w') as fp:
			json.dump(self.accountList,fp)

	def load(self):
		with open('/home/cameron/Projets/Red-DiscordBot/cogs/bank.json','r') as fp:
			self.accountList=json.load(fp)