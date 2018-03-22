from discord import Client

# replace with channels you want to scrape
CHANNELS_TO_SCRAPE = ['treehouse', 'another-place-to-talk', 'secret-channel']

client = Client()

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}')

@client.event
async def on_message(msg):
	log_message(msg, True)

def log_message(msg, stdout=False):
	line = log_format(msg)
	
	with open('log.txt', 'a') as log:
		log.write(line)
	if stdout:
		print(line)

def log_format(msg):
	# discord API only allows one embed per comment
	embed = f'[{msg.embeds[0].url}]' if msg.embeds else ''
	attachment = f'[{msg.attachments[0]["url"]}]' if msg.attachments else ''
	return f'[{msg.timestamp}][{msg.channel}]{attachment}{embed} @{msg.author}: {msg.clean_content}\n'

# run once on bot startup
async def scrape_messages(chronological=True):
	await client.wait_until_ready()
	messages = []
	
	for channel in client.get_all_channels():
		if str(channel) in CHANNELS_TO_SCRAPE:
			try:
				async for message in client.logs_from(channel, limit=1e20, reverse=True):
					messages.append(message) if chronological else log_message(message)
				print(f'Scraped {channel}')
			except Exception as e:
				print(e)
	
	if chronological:
		messages.sort(key=lambda x: x.timestamp)
		for message in messages:
			log_message(message)

client.change_presence(status='invisible')
client.loop.create_task(scrape_messages())
with open('token.txt', 'r') as file:
	client.run(file.read())