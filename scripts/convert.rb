require 'json'

module Convert
=begin
  Previous format:
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

  New format:
  log = {
    'action': 'message',
    'timestamp': str(msg.timestamp),
    'server': str(msg.server),
    'channel': {
      'name': channel.name,
      'private': channel.is_private
    },
    'user': {
      'name': user.name,
      'id': user.id
    },
    'message': {
      'content': str(msg.clean_content),
      'attachments': msg.attachments, # <-- list
      'embeds': msg.embeds, # <-- list
      'mentions': msg.raw_mentions, # <-- list
      'everyone': msg.mention_everyone
    }
  }
=end
  def self.message(log)
    new_log = {
      action: 'message',
      timestamp: log['message']['timestamp'],
      server: log['message']['server'],
      channel: {
        name: log['message']['channel']
      },
      user: {
        name: log['user']
      },
      message: {
        content: log['message']['content']
      }
    }

    new_log[:message][:attachments] = [{url: log['message']['attachment']}] if log['message'].key? 'attachment'
    new_log[:message][:embeds] = [{url: log['message']['embed']}] if log['message'].key? 'embed'

    new_log
  end

=begin
  Previous format:
  log = {
    'join/leave': {
      'timestamp': str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
      'server': str(member.server)
    },
    'user': str(member.name)
  }

  New format:
  log = {
    'action': 'join/leave/ban/unban',
    'timestamp': str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.000000')),
    'server': str(member.server),
    'user': {
      'name': user.name,
      'id': user.id
    }
  }
=end
  def self.member(log)
    action = log.key?('join') ? 'join' : 'leave'

    {
      action: action,
      timestamp: log[action]['timestamp'] + '.000000',
      server: log[action]['server'],
      user: {
        name: log['user']
      }
    }
  end
end

ARGV.each do |logfile|
  newfile = "fixed-#{logfile}"
  `> #{newfile}`

  File.foreach(logfile, "\n") do |line|
    log = JSON.parse line
    newline = log.key?('message') ? Convert.message(log) : Convert.member(log)
    IO.write(newfile, JSON.dump(newline)+"\n", mode: 'a')
  end
end