module Models
  class Alias < ActiveRecord::Base
    belongs_to :document
    belongs_to :entity
  end
end
