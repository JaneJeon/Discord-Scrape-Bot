require 'test/unit'
require 'json'
require_relative 'convert'
include Convert

class ConvertTest < Test::Unit::TestCase
  def test_message
    original = JSON.parse '{
      "message": {
        "timestamp": "2018-03-05 10:26:21.835000",
        "server": "Birthday Party",
        "channel": "happy-little-trees",
        "content": "<@303017694964219904> shameless self-shill https://www.youtube.com/watch?v=gv_f3IqTgds",
        "embed": "https://www.youtube.com/watch?v=gv_f3IqTgds"
      },
      "user": "Enfyve#1888"
    }'
    fixed = Convert.message original

    # base
    assert fixed[:action] == 'message'
    assert fixed[:timestamp] == original['message']['timestamp']
    assert fixed[:server] == original['message']['server']

    # channel
    assert fixed[:channel][:name] == original['message']['channel']
    assert_false fixed[:channel].key? :private

    # user
    assert fixed[:user][:name] == original['user']
    assert_false fixed[:user].key? :id

    # message + optionals
    assert fixed[:message][:content] == original['message']['content']
    assert fixed[:message][:embeds].first[:url] == original['message']['embed']
    assert_false fixed[:message].key? :attachments
    assert_false fixed[:message].key? :mentions
    assert_false fixed[:message].key? :everyone
  end

  def test_member
    original1 = JSON.parse '{
      "leave": {
        "timestamp": "2018-03-23 06:58:16",
        "server": "Slumber Party"
      },
      "user": "Miaa"
    }'
    fixed1 = Convert.member original1

    original2 = JSON.parse '{
      "join": {
        "timestamp": "2018-03-23 21:02:06",
        "server": "Birthday Party"
      },
      "user": "Leo Xiao Long"
    }'
    fixed2 = Convert.member original2

    # base
    assert fixed1[:action] == 'leave'
    assert fixed2[:action] == 'join'
    assert_true fixed1[:timestamp].start_with? original1['leave']['timestamp']
    assert_true fixed2[:timestamp].end_with? '.000000'
    assert fixed2[:server] == original2['join']['server']

    # user
    assert fixed1[:user][:name] == original1['user']
    assert_false fixed2[:user].key? :id
  end
end