# Merge two logs of the same format, with timestamp as the primary key (duplicates are skipped).
# If you're paranoid like me and want to check that it *is* okay to use timestamp as primary key, run the following:
# cat $LOG_FILE | sed -e 's/.*"timestamp":"\(.*\)".*/\1/' | cut -c 1-26 | sort | uniq -d | wc -l
# and check that it is indeed zero.
#
# Of note, this script assumes that the logs are all in the new format, where timestamp is a top-level field.
#
# The reason I rewrote the merge script is because whatever is converted from previous log formats will lack some
# information compared to the new formats, even though they both refer to the same item (message/event/etc).
# To get around that, we need to compare items from different logs using a primary key, not the whole line.
# That way, duplicate items in different logs will be recognized as the same item, despite having different lines.
require 'json'
require 'optparse'

output = 'merged.log'

OptionParser.new do |opts|
  opts.on('-o OUTPUT') do |file|
    output = file
  end
end.parse!

exit if ARGV.length < 2

total = 0
lines = {}

ARGV.each do |log|
  `cat #{log}`.split("\n").each do |line|
    entry = JSON.parse(line)
    user = (entry.key? 'user') ? entry['user']['name'] : 'NONE'
    key = entry['timestamp'] + entry['action'] + user
    
    if !lines.key? key
      lines[key] = line
    elsif line.length > lines[key].length
      puts "Replacing\n#{lines[key]}\nwith\n#{line}"
      lines[key] = line
    end
  end
end

`> #{output}`
File.open(output, 'a') do |file|
  lines.sort_by(&:last).each do |_, line|
    file.puts line
  end
end