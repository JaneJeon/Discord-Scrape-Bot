from discord import Client

client = Client()

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}')

@client.event
async def on_message(msg):
	log_message(msg)

def log_message(msg):
	line = f'[{msg.timestamp}][{msg.channel}] @{msg.author}: {msg.content}'
	with open('log.txt', 'a') as log:
		log.write(line+"\n")
	print(line)

async def scrape_messages():
	await client.wait_until_ready()
	
	for channel in client.get_all_channels():
		# replace with channels you want to scrape ▼
		if str(channel) in ['treehouse', 'another-place-to-talk', 'secret-channel']:
			async for message in client.logs_from(channel):
				log_message(message)
			print(f'Scraped {channel}')

client.change_presence(status='invisible')
client.loop.create_task(scrape_messages())
with open('token.txt', 'r') as file:
	client.run(file.read())