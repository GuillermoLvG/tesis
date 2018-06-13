require './lib/processors/date'
require './lib/processors/entity'

class Document
  def initialize(name, txt)
    @name    = name
    @content = txt
    @children = []
  end
  attr_reader :name, :children

  PROCESSORS = [
    Processors::Date,
    Processors::Entity
  ]

  def process!
    @content.split("\n").each do |paragraph|
      PROCESSORS.each do |klass|
        processor = klass.new(paragraph.strip)
        processor.process!

        model_class = klass.name.gsub(/.+::/, 'Models::').constantize
        processor.children.each do |data|
          model = model_class.new(data)
        end
      end
    end
  end
end
