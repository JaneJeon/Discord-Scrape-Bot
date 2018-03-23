import json
from datetime import datetime
from pathlib import Path
from discord import Client, Member, Message, Status

LOG_FILE = 'discord.log'

client = Client()

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}')

@client.event
async def on_message(msg):
	log_message(msg, True)

@client.event
async def on_member_join(member):
	log_member(member, 'join')

@client.event
async def on_member_remove(member):
	log_member(member, 'leave')

def log_write(line):
	with open(LOG_FILE, 'a') as log:
		log.write(line)

def log_message(msg: Message, stdout=False):
	log = {
		'message': {
			# better safe than sorry, so cast all the fields to string
			'timestamp': str(msg.timestamp),
			'server': str(msg.server),
			'channel': str(msg.channel),
			'content': str(msg.clean_content)
		},
		'user': str(msg.author)
	}
	
	# discord API only allows one attachment/embed per comment
	if msg.attachments:
		log['message']['attachment'] = str(msg.attachments[0]["url"])
	if msg.embeds:
		log['message']['embed'] = str(msg.embeds[0]["url"])
	
	line = json.dumps(log, separators=(',', ':'))+'\n'
	
	log_write(line)
	if stdout:
		print(line, end='')

def log_member(member: Member, action: str):
	line = json.dumps({
		action: {
			'timestamp': str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
			'server': str(member.server)
		},
		'user': str(member.name)
	}, separators=(',', ':'))+'\n'
	
	log_write(line)

# run once on bot startup
async def scrape_messages():
	await client.wait_until_ready()
	await client.change_presence(status=Status.invisible)
	
	for channel in client.get_all_channels():
		try:
			async for message in client.logs_from(channel, limit=1e20):
				# no need to order the entries if pushing to a document store
				log_message(message)
			print(f'Scraped {channel}')
		except Exception as e:
			print(e)

# empty the log file since we'll be scraping
open(LOG_FILE, 'w').close()
client.loop.create_task(scrape_messages())
client.run(Path('token.txt').read_text())