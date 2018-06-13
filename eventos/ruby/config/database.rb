require 'mysql2'
require 'active_record'

ActiveRecord::Base.establish_connection({
  adapter: 'mysql2',
  database: 'legales',
  host: 'localhost',
  username: 'root',
  password: '123456789'
})
