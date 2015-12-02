Server::Application.routes.draw do
  resources :users #do
  	#collection do
      #get 'sendMessage'
  	#
  #end
  resources :sessions, only: [:new, :create, :destroy]
  resources :messages, only: [:create, :destroy]
  root  'static_pages#home'
  match '/signup',     to: 'users#new',            via: 'get'
  match '/signin',  	 to: 'sessions#new',         via: 'get'
  match '/signout',		 to: 'sessions#destroy',     via: 'delete'
  match '/chat', 		   to: 'users#sendMessage',    via: 'get'
  match '/message',    to: 'messages#message',     via: 'get'
end
