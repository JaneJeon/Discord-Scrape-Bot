from datetime import datetime
from pathlib import Path
from discord import Client, Status

# replace with channels you want to scrape
CHANNELS_TO_SCRAPE = ['treehouse', 'another-place-to-talk', 'secret-channel']

client = Client()

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}')

@client.event
async def on_message(msg):
	log_message(msg, True)

@client.event
async def on_member_join(member):
	log_member(member, 'joined')

@client.event
async def on_member_remove(member):
	log_member(member, 'left')

def log_write(line):
	with open('log.txt', 'a') as log:
		log.write(line)

def log_message(msg, stdout=False):
	# discord API only allows one embed per comment
	embed = f'[{msg.embeds[0].url}]' if msg.embeds else ''
	attachment = f'[{msg.attachments[0]["url"]}]' if msg.attachments else ''
	line = f'[{msg.timestamp}][{msg.channel}]{attachment}{embed} @{msg.author}: {msg.clean_content}\n'
	
	log_write(line)
	if stdout:
		print(line, end='')

def log_member(member, action):
	date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
	log_write(f'[{date}] @{member.name} {action}\n')

# run once on bot startup
async def scrape_messages(chronological=True):
	await client.wait_until_ready()
	messages = []
	
	for channel in client.get_all_channels():
		if str(channel) in CHANNELS_TO_SCRAPE:
			try:
				async for message in client.logs_from(channel, limit=1e20, reverse=True):
					# this may take a lot of memory if you're scraping a big channel
					messages.append(message) if chronological else log_message(message)
				print(f'Scraped {channel}')
			except Exception as e:
				print(e)
	
	if chronological:
		messages.sort(key=lambda x: x.timestamp)
		for message in messages:
			log_message(message)

# empty the log file since we'll be scraping
open('log.txt', 'w').close()
client.change_presence(status=Status.invisible)
client.loop.create_task(scrape_messages())
client.run(Path('token.txt').read_text())