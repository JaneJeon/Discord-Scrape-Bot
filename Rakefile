OPTION = ENV['OPTION'] || ''
REMOTE = ENV['REMOTE']

def count
  `cat logs/discord.log | wc -l | awk '{print $1}'`.to_i
end

desc "Pulls log from source"
task :pull do
  `scp #{OPTION} #{REMOTE}:~/discord.log ~/Desktop`
end

desc "Merge the new log with the pre-kick log"
task :merge => :pull do
  lines = count
  `ruby scripts/merge.rb logs/fixed-original.log ~/Desktop/discord.log -o logs/discord.log`
  puts "#{count - lines} new lines since last pull"
end

desc "Update the server's logs"
task :update => :merge do
  `scp #{OPTION} logs/discord.log #{REMOTE}:~`
end

desc "Deploy the new source code"
task :deploy => :update do
  `scp #{OPTION} bot.py #{REMOTE}:~`
  `ssh #{OPTION} #{REMOTE} 'pkill bot.py && nohup python3.6 ~/bot.py -a &'`
end