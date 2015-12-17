Server::Application.routes.draw do
  resources :users
  resources :sessions, only: [:new, :create, :destroy]
  resources :conversations do
    resources :messages
  end
  root  'static_pages#home'
  match '/signup',     to: 'users#new',            via: 'get'
  match '/signin',  	 to: 'sessions#new',         via: 'get'
  match '/signout',		 to: 'sessions#destroy',     via: 'delete'
  match '/message',    to: 'messages#message',     via: 'get'
  match '/send',       to: 'users#sendMessage',    via: 'get'
end
