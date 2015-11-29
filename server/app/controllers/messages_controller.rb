class MessagesController < ApplicationController
  def create
    @message = Message.create!(message_params)
  end

  def message_params
    params.require(:message).permit(:content)
  end

  def message
   @message = Message.new
  end

end
