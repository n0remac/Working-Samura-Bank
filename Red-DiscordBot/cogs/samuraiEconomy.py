import json
import discord
import requests
from bs4 import BeautifulSoup
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
	async def show(self, name):
		await self.bot.say(self.centralBank.getAmount(name))

	#should be doen automatically
	@commands.command()
	async def ATM(self):
		self.centralBank.ATM()

	@commands.command()
	async def commands(self):
		await self.bot.say("accounts - shows a list of all accounts\nshow <account name> - shows the banalce of a specified account.\n")



	'''
        @commands.command()
        async def createAccount(self, name):
                self.centralBank.createAccount(name)
                await self.bot.say("Created account named "+name)

	# will use - user : discord.Member - needs discord regestry
	@commands.command()
	async def transfer(self, name, num, to):
		await self.bot.say(self.centralBank.transfer(name, num, to))

	@commands.command()
	async def a(self, name, num):
		self.centralBank.createAccount(name)
		self.centralBank.deposit(name, num)
		await self.bot.say("Created account named "+name+". Added "+str(self.centralBank.getAmount(name)))

	#deposits should only be made through the forum
	@commands.command()
	async def deposit(self, name, num):
		self.centralBank.deposit(name, num)
		await self.bot.say(str(self.centralBank.getAmount(name))+" is in the account")
	'''


class Bank:
	def __init__(self):
		self.accountList={}
		self.currency="$"
		self.atm=AutomaticTransferMachine(self)

		try:
			self.load()
		except:
			self.save()
			self.load()

	def createAccount(self, name):
		self.accountList.update({name: 0})
		self.save()

	def getAmount(self, name):
		if name in self.accountList:
			return self.accountList.get(name)
		else:
			return "Account not found."

	def getAccountList(self):
		accounts=sorted(self.accountList, key=str.lower)
		prettyAccounts=""
		for acnt in accounts:
			prettyAccounts+=acnt+" - "+self.toGold(self.accountList.get(acnt))+"\n"
		return prettyAccounts

	def deposit(self, name, num):
		self.accountList[name]+=int(num)
		self.save(self.accountList)
	
	def withdraw(self, name, num):
		self.accountList[name] -= int(num)
		self.save(self.accountList)
		return num

	def transfer(self, name, num, to):
		ret=self.getAmount(name)
		if name in self.accountList:
			ret="Recipient not found"
			if to in self.accountList:
				if self.getAmount(name)-int(num) >0:
					self.deposit(to, self.withdraw(name, num))
					ret= "Transfer complete."
				else:
					ret="Funds not available."
		return ret

	def toGold(self, amount):
		gold=amount//100
		silver=amount//10%10
		copper=amount%10
		ret="%s Gold %s Silver %s Copper"%(gold,silver,copper)
		#ret=str(gold)+" Gold "+str(silver)+" Silver "+str(copper)+" Copper"
		#{"Gold":gold, "Silver": silver, "Copper":copper}
		return ret

	def ATM(self):
		num=self.atm.getLastTransaction()
		print(num)

		self.atm.pageUpdate(num)
		self.atm.findCommands()
		
		#print(transactions)


	def save(self, saveObj):
		with open('/home/cameron/Projects/Red-DiscordBot/cogs/samuraiCogs/bank.json','w') as fp:
			json.dump(saveObj,fp)

	def load(self):
		with open('/home/cameron/Projects/Red-DiscordBot/cogs/samuraiCogs/bank.json','r') as fp:
			self.accountList=json.load(fp)


class AutomaticTransferMachine:

	def __init__(self, bank):
		self.bankers=["Noremac","Nikodil"]
		self.bank=bank
		self.transactions={}
		self.pageInfo={}
		self.load()


	def pageUpdate(self,num):
		ScrapeForum(num)
		with open('/home/cameron/Projects/Red-DiscordBot/cogs/samuraiCogs/bankPageData.json','r') as fp:
			self.pageInfo=json.load(fp)

	#checks for transactions and sees if they are valid and unique
	def findCommands(self):
		pNum=0
		name=""
		post=""
		#print(pageInfo)
		#print(self.transactions)
		for p in self.pageInfo:
			print("-->"+str(p))
			print(type(p))
			if p!="pNum":
				pNum=p
				print("-->"+str(p))
				print(self.pageInfo)
				name=self.pageInfo.get(pNum)[0]
				#print(name)
				print(self.pageInfo.get(pNum))
				post=self.pageInfo.get(pNum)[1]
				print(post)
				self.checkTransfer(post[0],name,pNum)
				self.checkDeposit(name, post[0], pNum)
			

		self.save(self.transactions)

	def checkDeposit(self, who, post, pNum):
		#print(post)
		#print("\n")
		#print("Command Check"+str(pNum))
		if who in self.bankers:
			if pNum in self.transactions:
				print(post+ " is a repeat")
			elif "|deposit|" in post:
				amount=post.split("|", 3)[2]
				name=post.split("|", 4)[3]
				print(name + "deposited " + amount)
				self.deposit(amount, name)
				saveMe=self.getSaveObj("deposit", [amount, name], pNum)
				self.transactions.update(saveMe)

	def checkTransfer(self, post, name, pNum):
		#print(post)
		#print("Command Check"+str(pNum))
		if pNum in self.transactions:
			pass
			#print(post+" is a repeat")
		elif "|transfer|" in post:
			print("SLASH FOUND!!!!!!!!!!!!!!!!!!!!!!!")
			print(post)
			amount=post.split("|", 3)[2]
			print(amount)
			to=post.split("|", 4)[3]
			print(name + " transfered "+amount+" to "+to)
			self.transfer(name, amount, to)
			saveMe=self.getSaveObj("transfer", [name, amount, to], pNum)
			self.transactions.update(saveMe)
		#return saveMe
		

	def deposit(self, amount, name):
		self.bank.deposit(name, amount)

	def transfer(self, name, num, to):
		money=self.bank.withdraw(name, num)
		self.bank.deposit(to, num)

	def getLastTransaction(self):
		l=len(self.transactions)
		lt=0
		for t in self.transactions:
			lt=t
		return lt
		#t=self.transactions.keys()
		#print(t)
		#return self.transactions.get()

	def save(self, saveObjects):
		with open('/home/cameron/Projects/Red-DiscordBot/cogs/samuraiCogs/transactions.json','w') as fp:
			json.dump(saveObjects,fp)

	def load(self):
		with open('/home/cameron/Projects/Red-DiscordBot/cogs/samuraiCogs/transactions.json','r') as fp:
			self.transactions=json.load(fp)
			#print(self.transactions)

	#post number needs to be used in the save file so that repeat transactions can be checked
	def getSaveObj(self, transactionType, value, pNum):
		return {pNum:[transactionType,value]}
			


class DiscordRegistry:
	def __init__(self):
		self.discordUsers=[]

	def addUser(name):
		self.discordUsers.append(name)

	

class ScrapeForum:

	def __init__(self, num):
		self.isOn=True
		self.run(num)
		


	def run(self, num):
		directUrl="http://forum.openwar.org/t/the-samurai-bank/13399/"
		bankPage={}
		i=int(num)
		#startTime=time.clock()
		while self.isOn:
			scrapeMe=directUrl+str(i)
			bankPage.update(self.scrape(scrapeMe))
			i+=1
			print("passed "+str(i))
		#endTime=time.clock()
		#print(str(i-num)+" scrapes in "+str(endTime-startTime))
		self.save(bankPage)

	def scrape(self, directUrl):
		#print(directUrl)
		page =requests.get(directUrl)
		soup = BeautifulSoup(page.content, 'html.parser')
		#print(soup.prettify())
		divTags=soup.find_all('div', {"itemtype" : "http://schema.org/DiscussionForumPosting"})
	
		bankPage={"pNum": 0}

		

		for tag in divTags:
			postList=[]
			name=tag.find('b',{"itemprop":"author"}).text
			pNum=tag.find('span',{"itemprop":"position"}).text.split("#")[1]
			pTag=tag.find_all('p')
			
			for p in pTag:
				postList.append(p.text)
				bankPage["pNum"]=pNum
			bankPage.update({pNum:[name,postList]})
		
		
		aTag=soup.find_all('a', {"itemprop":"name"})
		#print(aTag)
		if aTag ==[]:
			self.isOn=False
				

		return bankPage

	def save(self, saveMe):
		with open('/home/cameron/Projects/Red-DiscordBot/cogs/samuraiCogs/bankPageData.json','w') as fp:
			json.dump(saveMe,fp)
