FROM ruby:3.0

WORKDIR /srv
COPY app.rb /srv
COPY views /srv/views
COPY flag.txt /flag.txt

RUN /usr/sbin/useradd --no-create-home -u 1000 ctf

RUN gem install rackup \
  && gem install erubis \
  && gem install sinatra

USER ctf

CMD ruby app.rb
