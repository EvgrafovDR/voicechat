class MessagesController < ApplicationController
def create
    @conversation = Conversation.find(params[:conversation_id])
    @message = @conversation.messages.build(message_params)
    @message.user_id = current_user.id
    @message.body = emojify(@message.body)
    @message.save!    
    @path = conversation_path(@conversation)

    @user = User.find(@conversation.recipient_id)
    if @user.status == "Offline"
      @conversation = Conversation.find(params[:conversation_id])
      @message = @conversation.messages.build(message_params)
      @message.body = sendMessage(@message.body)
      @message.user_id = @user.id
      @message.save!    
      #@path = conversation_path(@conversation)
    end

  end

  private

  def message_params
    params.require(:message).permit(:body)
  end
end
