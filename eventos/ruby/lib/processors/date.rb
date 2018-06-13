require './lib/processors/base'

module Processors
  class Date < Base
    MONTHS = %w[enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre]
    REGEXP = Regexp.new("el (\\d{1,2}) de (#{MONTHS.join('|')}) de (\\d{4})", 'i')
  end
end
