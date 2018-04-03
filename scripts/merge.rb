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

def count(log)
  `cat #{log} | wc -l | awk '{print $1}'`.to_i
end

exit if ARGV.length < 2

total = 0
lines = {}

ARGV.each do |log|
  total += count log

  `cat #{log}`.split("\n").each do |line|
    lines[JSON.parse(line)['timestamp']] = line
  end
end

`> #{output}`
File.open(output, 'a') do |file|
  lines.each_value do |line|
    file.puts line
  end
end

puts "#{count output} unique lines of total #{total}"