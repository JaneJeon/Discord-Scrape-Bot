from argparse import ArgumentParser
from datetime import datetime
from io import open
from json import dumps
from pathlib import Path
from discord import Channel, Client, Message, Status, User

client = Client()

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}')

@client.event
async def on_message(msg):
	log_event('message', msg.server, msg.timestamp, msg.channel, msg.author, msg)

@client.event
async def on_member_join(member):
	log_event('join', member.server, user=member)

@client.event
async def on_member_remove(member):
	log_event('leave', member.server, user=member)

@client.event
async def on_member_ban(member):
	log_event('ban', member.server, user=member)

@client.event
async def on_member_unban(member):
	log_event('unban', member.server, user=member)

@client.event
async def on_channel_create(channel):
	log_event('channel_create', channel.server, channel.created_at, channel)

@client.event
async def on_channel_delete(channel):
	log_event('channel_delete', channel.server, channel=channel)

@client.event
async def on_group_join(channel, user):
	log_event('group_join', channel.server, channel=channel, user=user)

@client.event
async def on_group_remove(channel, user):
	log_event('group_remove', channel.server, channel=channel, user=user)

# ▼ these two methods run once on bot startup ▼
async def go_invis():
	await client.wait_until_ready()
	await client.change_presence(status=Status.invisible)

async def scrape_messages():
	await client.wait_until_ready()
	
	for channel in client.get_all_channels():
		try:
			async for msg in client.logs_from(channel, limit=1e20):
				# no need to order the entries if pushing to a document store
				log_event('message', msg.server, msg.timestamp, msg.channel, msg.author, msg, stdout=False)
			print(f'Scraped {channel}')
		except Exception as e:
			print(f'Error scraping {channel}: {e}')
	
	print('Finished scraping messages')


def log_event(action: str, server, timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.000000'), 
              channel=None, user=None, msg=None, stdout=True):
	line = flatten(event(action, server, timestamp, channel, user, msg))
	
	write(line)
	if stdout:
		print(line, end='')

def event(action: str, server, timestamp, channel:Channel, user:User, msg:Message):
	log = {
		'action': action,
		'timestamp': str(timestamp),
		'server': str(server)
	}
	
	if channel:
		log['channel'] = {
			'name': channel.name,
			'private': channel.is_private
		}
	
	if user:
		log['user'] = {
			'name': str(user),
			'id': user.id,
			'nickname': user.display_name
		}
	
	if msg:
		log['message'] = {
			'content': str(msg.clean_content),
			'attachments': msg.attachments,
			'embeds': msg.embeds,
			'mentions': msg.raw_mentions,
			'everyone': msg.mention_everyone
		}
	
	return log

def flatten(log):
	return dumps(log, separators=(',', ':'), ensure_ascii=False)+'\n'

def write(line):
	with open(LOG_FILE, 'a', encoding='utf8') as log:
		log.write(line)


parser = ArgumentParser()
parser.add_argument('-a', action='store_true', help="Preserve existing log and skip scraping")
parser.add_argument('-f', default='logs/discord.log', help="Specify logfile")
parser.add_argument('-t', default=None, help="Pass token in as a string")
result = parser.parse_args()

LOG_FILE = result.f

if not result.a:
	# empty the log file
	open(LOG_FILE, 'w').close()
	client.loop.create_task(scrape_messages())

client.loop.create_task(go_invis())
client.run(result.t if result.t else Path('token.txt').read_text())