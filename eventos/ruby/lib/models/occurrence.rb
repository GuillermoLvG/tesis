require './lib/models/document'
require './lib/models/entity'

module Models
  class Occurrence < ActiveRecord::Base
    belongs_to :document
    belongs_to :entity, polymorphic: true
  end
end
