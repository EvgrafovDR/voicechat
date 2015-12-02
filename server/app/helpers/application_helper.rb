require 'socket'

module ApplicationHelper
# Returns the full title on a per-page basis.
  def full_title(page_title)
    base_title = "callchat"
    if page_title.empty?
      base_title
    else
      "#{base_title} | #{page_title}"
    end
  end

  def ServerUp
  	server = TCPServer.open(3000)
  	loop
  	{
  	  client = server.accept
  	  line = client.gets
  	}
  end
end
