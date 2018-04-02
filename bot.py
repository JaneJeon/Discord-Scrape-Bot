from argparse import ArgumentParser
from json import dumps
from datetime import datetime
from pathlib import Path
from discord import Channel, Client, Member, Message, Status, User

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

@client.event
async def on_member_ban(member):
	log_member(member, 'ban')

@client.event
async def on_member_unban(member):
	log_member(member, 'unban')

@client.event
async def on_channel_create(channel):
	log_channel(channel, 'channel_create', channel.created_at)

@client.event
async def on_channel_delete(channel):
	log_channel(channel, 'channel_delete', now())

def log_message(msg: Message, stdout=False):
	line = flatten(base_log('message', msg.server, msg.timestamp, channel=msg.channel, user=msg.author, msg=msg))
	
	write(line)
	if stdout:
		print(line, end='')

def log_member(member: Member, action: str):
	write(flatten(base_log(action, member.server, timestamp=now(), user=member)))

def log_channel(channel: Channel, action: str, timestamp):
	write(flatten(base_log(action, channel.server, timestamp, channel=channel)))

def base_log(action: str, server, timestamp, channel:Channel=None, user:User=None, msg:Message=None):
	log = {
		'action': action,
		'timestamp': str(timestamp),
		'server': str(server)
	}
	
	if channel is not None:
		log['channel'] = {
			'name': channel.name,
			'private': channel.is_private
		}
	
	if user is not None:
		log['user'] = {
			'name': user.name,
			'id': user.id
		}
	
	if msg is not None:
		log['message'] = {
			'content': str(msg.clean_content),
			'attachment': msg.attachments,
			'embed': msg.embeds,
			'mentions': msg.raw_mentions,
			'everyone': msg.mention_everyone
		}
	
	return log

def flatten(log):
	return dumps(log, separators=(',', ':'))+'\n'

def write(line):
	with open(LOG_FILE, 'a') as log:
		log.write(line)

# the reason I removed this as the default timestamp and instead extracted it into its own function
# is that if I happen to add methods other than log_member later that doesn't have an accurate timestamp,
# I want that dependency to be explicitly stated on function call so that I can merge it properly
def now():
	return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.000000')

# ▼ these two methods run once on bot startup ▼
async def go_invis():
	await client.wait_until_ready()
	await client.change_presence(status=Status.invisible)

async def scrape_messages():
	await client.wait_until_ready()
	
	for channel in client.get_all_channels():
		try:
			async for message in client.logs_from(channel, limit=1e20):
				# no need to order the entries if pushing to a document store
				log_message(message)
			print(f'Scraped {channel}')
		except Exception as e:
			print(f'Error scraping {channel}: {e}')
	
	print('Finished scraping messages')

# append mode doesn't destroy existing log
parser = ArgumentParser()
parser.add_argument('-a', action='store_true')

client.loop.create_task(go_invis())

if not parser.parse_args().a:
	# empty the log file since we'll be scraping
	open(LOG_FILE, 'w').close()
	client.loop.create_task(scrape_messages())

client.run(Path('token.txt').read_text())