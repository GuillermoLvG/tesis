require './lib/models/document'
require './lib/models/occurrence'

module Models
  class Entity < ActiveRecord::Base
    REGEXP = /[^\(A-Z]([A-Z]([A-Za-záéíóú]+.)+)/

    before_create :set_type

    has_many :occurrences, as: :entity

    def self.parse(text,index)
	  #Lista de entidades vacía
      entities = []
      #En el párrafo que recibe esta función, cada vez que encuentre algo con la expresión regular
      #lo guarda en match
      text.scan(REGEXP).each do |match|
		
		#1
		#puts "\nPárrafo: #{index}"
		#puts "Texto: #{text}"
		#puts "Match ER: #{match.first}"
		
		#entity tiene el match de la expresión regular, pero sin el último caracter.
		#Parece ser que el último caracter siempre es un signo de puntuación o un espacio en casos raros.
        entity = match.first[0...-1]
		
		#2
		#puts "\nPárrafo: #{index}"
		#puts "Texto: #{text}"
		#puts "Match ER: #{entity}"
		
		#words tiene la entidad que correspondió con la expresión regular, separada por espacios
        words = entity.split(' ')
        error = nil
		#si la entidad tiene más de una palabra
        if words.count > 1
		  next unless words[1] =~ /[a-z]/
        end
        #Si la 2da palabra no estuvo en mayúscula, entonces 
        #sacamos de word los elementos, hasta que la Última palabra
        #empiece en mayúscula.
		
		#3
		#puts "\nPárrafo: #{index}"
		#puts "Texto: #{text}"
		#puts "Lista words: #{words.join(' ')}"      
        
        words.pop until words.last[0] =~ /[A-Z]/
        
		#4
		#puts "\nPárrafo: #{index}"
		#puts "Texto: #{text}"
        #puts "Lista words: #{words.join(' ')}"
        
        entities += words.join(' ').split(/( [a-záéíóú]+){3,}/).map(&:strip).select do |word|
          #5
          #puts "\nPárrafo: #{index}"
          #puts "Lista words: #{words.join(' ')}"
          #puts "Lista words dividida: #{words.join(' ').split(/( [a-záéíóú]+){3,}/).map(&:strip)}"
          word =~ /^[A-Z]/
        end
      end
      #6
	  #puts "\nPárrafo: #{index}"
	  #puts "Texto: #{text}"
	  #puts "Lista entidades: #{entities}"
	  #parse regresa entities.
      entities
    end
  private
    def set_type
      self.type = 'Models::Law'
    end
  end

  class Law < Entity
    has_many :articles
  end
end
