"""
Converts logs from the format used in previous commit (96003f1d97fd6e3fb77f2b4372f106cdac73428b),
to the new & improved format featured in this commit.

Previous (log_message):
log = {
	'message': {
		'timestamp': str(msg.timestamp),
		'server': str(msg.server),
		'channel': str(msg.channel),
		'content': str(msg.clean_content)
	},
	'user': str(msg.author)
}
if msg.attachments:
	log['message']['attachment'] = str(msg.attachments[0]['url'])
if msg.embeds:
	log['message']['embed'] = str(msg.embeds[0]['url'])

New (log_message):
???

Previous (log_member):
log = {
	action: {
		'timestamp': str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.000000')),
		'server': str(member.server)
	},
	'user': str(member.name)
}

New (log_member):
???
"""
import json
import sys, os

if len(sys.argv) == 1:
	exit(-1)

open('temp.txt', 'w').close()

with open(sys.argv[1], 'r') as file, open('temp.txt', 'a') as temp:
	for line in file:
		# TODO: pass corrected log lines from file to temp, write it there.
		obj = json.loads(line)
		temp.write(line) # should have newline

open(sys.argv[1], 'w').close()

with open(sys.argv[1], 'a') as file, open('temp.txt', 'r') as temp:
	for line in temp:
		file.write(line)

os.remove('temp.txt')