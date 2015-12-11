class UsersController < ApplicationController
  def new
  	@user = User.new
  end

  def show
    @users = User.where.not("id = ?",current_user.id).order("created_at DESC")
    @conversations = Conversation.involving(current_user).order("created_at DESC")
    @user = User.find(params[:id])
  end

  def create
    @user = User.new(user_params)    
    if @user.save
      sign_in @user
      redirect_to @user
    else
      render 'new'
    end
  end

  def sendMessage
    #begin
      s = TCPSocket.new '188.226.166.81', 6565    
      s.puts "hello, Danila"
    #rescue
      #retry
    # 
  end

  private

    def user_params
      params.require(:user).permit(:name, :email, :password,
                                   :password_confirmation)
    end
end
