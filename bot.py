from argparse import ArgumentParser
from datetime import datetime
from io import open
from json import dumps
from pathlib import Path
from discord import Channel, Client, Member, Message, Status, User

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

@client.event
async def on_group_join(channel, user):
	log_channel_member(channel, user, 'group_join')

@client.event
async def on_group_remove(channel, user):
	log_channel_member(channel, user, 'group_remove')

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


def log_message(msg: Message, stdout=False):
	line = flatten(event_log('message', msg.server, msg.timestamp, channel=msg.channel, user=msg.author, msg=msg))
	
	write(line)
	if stdout:
		print(line, end='')

def log_member(member: Member, action: str):
	write(flatten(event_log(action, member.server, now(), user=member)))

def log_channel(channel: Channel, action: str, timestamp):
	write(flatten(event_log(action, channel.server, timestamp, channel=channel)))

def log_channel_member(channel: Channel, user: User, action: str):
	write(flatten(event_log(action, channel.server, now(), user=user)))


def event_log(action: str, server, timestamp, channel:Channel=None, user:User=None, msg:Message=None):
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
			'id': user.id
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

def now():
	return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.000000')


parser = ArgumentParser()
parser.add_argument('-a', '--append', action='store_true', help="Preserve existing log and skip scraping")
parser.add_argument('-f', '--file', default='logs/discord.log', help="Specify logfile")
parser.add_argument('-t', '--token', default=None, help="Pass token in as a string")
result = parser.parse_args()

LOG_FILE = result.f

if not result.a:
	# empty the log file
	open(LOG_FILE, 'w').close()
	client.loop.create_task(scrape_messages())

client.loop.create_task(go_invis())
client.run(result.t if result.t else Path('token.txt').read_text())