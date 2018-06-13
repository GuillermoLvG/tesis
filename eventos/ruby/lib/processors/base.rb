module Processors
  class Base
    def initialize(txt)
      @content = txt
      @children = []
    end
    attr_reader :children

    def process!
      @children += @content.scan(self.class::REGEXP).map { |data| self.class.name.split('::').last + ': ' + data.join(',') }
    end
  end
end
