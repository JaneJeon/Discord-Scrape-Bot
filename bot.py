from discord import Client

client = Client()

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}')

@client.event
async def on_message(msg):
	log_message(msg)

def log_message(msg):
	with open('log.txt', 'a') as log:
		log.write(f'[{msg.timestamp}][{msg.channel}] @{msg.author}: {msg.clean_content}\n')

async def scrape_messages():
	await client.wait_until_ready()
	
	for channel in client.get_all_channels():
		# replace with channels you want to scrape ▼
		if str(channel) in ['treehouse', 'another-place-to-talk', 'secret-channel']:
			try:
				async for message in client.logs_from(channel, limit=1e20, reverse=True):
					log_message(message)
				print(f'Scraped {channel}')
			except Exception as e:
				print(e)

client.change_presence(status='invisible')
client.loop.create_task(scrape_messages())
with open('token.txt', 'r') as file:
	client.run(file.read())