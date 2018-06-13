require './lib/models/document'
require './lib/models/entity'

module Models
  class Article < ActiveRecord::Base
    REGEXP = /(art[i|í]culos? [\do\.\, y]+)/

    def self.parse(text)
      text.scan(REGEXP).map(&:first)
    end
  end
end
