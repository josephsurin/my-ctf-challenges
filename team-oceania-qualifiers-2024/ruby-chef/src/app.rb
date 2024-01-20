require 'sinatra'
require 'base64'
require 'json'

set :environment, :production
set :port, 1337
enable :sessions

class Chef
  public

  def b64e(s)
    Base64.encode64(s).chomp
  end

  def rot13(s)
    s.chars.map { |x| ((x.ord + 13) % 128).chr }.join
  end

  def affine(s, a, b)
    s.chars.map { |x| ((a * x.ord + b) % 128).chr }.join
  end
end

get '/' do
  session[:chef] = Chef.new
  erb :index
end

post '/transform' do
  content_type :json
  payload = JSON.parse request.body.read, symbolize_names: true

  unless payload[:recipe] && payload[:ingredients]
    halt 500, {:err => "Invalid recipe or ingredients!"}.to_json
  end

  unless /\A[a-z0-9]+\z/.match?(payload[:ingredients]) && payload[:ingredients].length <= 9
    halt 500, {:err => 'Please limit ingredients to abc\'s and 123\'s and no more than 9 items.'}.to_json
  end

  begin
    result = payload[:ingredients]
    payload[:recipe].each do |step|
      if step[:action] == 'affine' then
        result = session[:chef].public_send(step[:action], result, *step[:options])
      else
        result = session[:chef].public_send(step[:action], result)
      end
    end

    return {:result => result}.to_json
  rescue Exception => e
    p e
    halt 500, {:err => "Server Error"}.to_json
  end
end
