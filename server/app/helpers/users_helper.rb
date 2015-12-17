require 'socket'
require 'json'
module UsersHelper
 # Returns the Gravatar (http://gravatar.com/) for the given user.
  def gravatar_for(user)
    gravatar_id = Digest::MD5::hexdigest(user.email.downcase)
    gravatar_url = "https://secure.gravatar.com/avatar/#{gravatar_id}"
    image_tag(gravatar_url, alt: user.name, class: "gravatar")
  end
  
  def interlocutor(conversation)
    current_user == conversation.recipient ? conversation.sender : conversation.recipient
  end

  def sendMessage
  	s = TCPSocket.new '188.166.62.207', 7676

    line = JSON.parse(s.gets)
    action = line['action']
    if action == "ping"
      s.puts "{\"action\": \"pong\"}\r\n"
      line = "nice"
    end

    s.puts "{\"action\": \"message\", \"number\":\"79824765200\", \"from\":\"79197061712\", \"text\":\"Привет, хуйло!\", \"id\":\"124135135\"}\r\n"

    flag = true
    text = "empty"
    while flag
      line = JSON.parse(s.gets)
      action = line['action']
      if action == "ping"
        s.puts "{\"action\": \"pong\"}\r\n"
      else 
        if action == "message"
          text = line['text']
          flag == false
        end
      end
    end
    s.close

    text
  end
end
