import aiohttp
import asyncio
from datetime import datetime, timezone
from discord.ext import commands
from discord import app_commands, Object, Embed
from data import VALRISE_LOGIN_NAME, VALRISE_LOGIN_PASSWORD

def parse_cookies(cookie):
	params = {}
	for param in cookie.split(';'):
		param = param.strip().split('=')
		params[param[0]] = param[1] if len(param) > 1 else None
	return params

async def login():
	async with aiohttp.ClientSession() as session:
		url = 'https://panel-rpg.valrisegaming.com/api/auth/rpg'
		payload = {'name': VALRISE_LOGIN_NAME,'password': VALRISE_LOGIN_PASSWORD}
		async with session.post(url, json=payload) as resp:
			cookie = resp.headers['Set-Cookie']
			params = parse_cookies(cookie)
			expires = datetime.strptime(params['Expires'], "%a, %d %b %Y %H:%M:%S %Z")
			second = expires.second - 2 if expires.second >= 2 else 60 + expires.second - 2 # 2 seconds network gap
			return params['connect.sid'], expires.replace(second=second, tzinfo=timezone.utc)

async def fetch_players(session_id):
	cookies = {'connect.sid': session_id}
	players = []
	async with aiohttp.ClientSession(cookies=cookies) as session:
		async with session.get('https://panel-rpg.valrisegaming.com/api/rpg/general/online') as resp:
			online_players = await resp.json()
		for player in online_players:
			name = player['name'].lower()
			async with session.get(f'https://panel-rpg.valrisegaming.com/api/rpg/user/{name}') as resp:
				players.append(await resp.json())
	return players

class Extras(commands.Cog):
	def __init__(self, sid, expires):
		self.session_id = sid
		self.expires = expires
		self.lock = asyncio.Lock()

	async def check_login(self):
		async with self.lock:
			now = datetime.now(timezone.utc)
			if now >= self.expires:
				self.session_id, self.expires = await login()

	def format_players(self, players):
		_format = lambda name, score : f"| {name.ljust(25)} | {score.ljust(5)} |"
		stroke = lambda x : '-' * x
		headers = _format("NAME", "LEVEL")
		fields = "\n".join(_format(player['name'], str(player['level'])) for player in players)
		string = f" {stroke(35)} \n{headers}\n|{stroke(27)}|{stroke(7)}|\n{fields}\n {stroke(35)} "
		description = string.replace('    ', '\t')
		return f"```txt\n{description}```"

	@app_commands.command(name='online-players')
	#@app_commands.guilds(Object(id=1213615486986747934))
	async def online_players(self, interaction):
		await interaction.response.defer(thinking=True)
		await self.check_login()
		online_players = await fetch_players(self.session_id)
		description = self.format_players(online_players)
		embed = Embed(title=f"ONLINE PLAYERS - {len(online_players)}", description=description)
		await interaction.followup.send(embed=embed)

	@app_commands.command(name='search')
	#@app_commands.guilds(Object(id=1213615486986747934))
	async def search(self, interaction, basis: str):
		await interaction.response.defer(thinking=True)
		await self.check_login()
		cookies = {"connect.sid": self.session_id}
		async with aiohttp.ClientSession(cookies=cookies) as session:
			async with session.get(f'https://panel-rpg.valrisegaming.com/api/rpg/search/user/{basis}') as resp:
				matches = await resp.json()
		if isinstance(matches, dict) and 'error' in matches:
			embed = Embed(title="ERROR!", description=matches['error'])
		elif matches:
			embed = Embed(title=f"MATCHING PLAYERS - {len(matches)}", description=self.format_players(matches))
		else:
			embed = Embed(title="NO MATCHING PLAYERS FOUND!")
		await interaction.followup.send(embed=embed)

async def setup(bot):
	sid, expires = await login()
	await bot.add_cog(Extras(sid, expires))
