Server::Application.routes.draw do
  resources :users
  root  'static_pages#home'
  match '/signup',       to: 'users#new',                 via: 'get'
end
