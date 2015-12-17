require 'socket'
class UsersController < ApplicationController
  before_action :signed_in_user, only: [:edit, :update]
  before_action :correct_user,   only: [:edit, :update]

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
  end

  def edit
    @user = User.find(params[:id])
  end

  def update
     @user = User.find(params[:id])
   if @user.update_attribute(:status, user_status[:status])
      flash[:success] = "Profile updated"
      redirect_to @user
    else
      render 'edit'
    end
  end

  private

    def user_params
      params.require(:user).permit(:name, :email, :password,
                                   :password_confirmation,:status)
    end

    def user_status
      params.require(:user).permit(:status)
    end

    def signed_in_user
      unless signed_in?
        store_location
        redirect_to signin_url, notice: "Please sign in."
      end
    end

    def correct_user
      @user = User.find(params[:id])
      redirect_to(root_url) unless current_user?(@user)
    end
end
