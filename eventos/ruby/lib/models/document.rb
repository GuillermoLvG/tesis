require 'docx'
require './lib/models/alias'
require './lib/models/article'
require './lib/models/entity'
require './lib/models/occurrence'

module Models
  class Document < ActiveRecord::Base
    has_many :occurrences
    has_many :entities, through: :ocurrences
    has_many :aliases

    def process!
	  #paragraphs tiene el texto plano del archivo.
	  #paragraph tiene cada párrafo, y a cada uno le corresponde un índice que está en index.
      paragraphs.each_with_index do |paragraph, index|
		#Entity.parse recibe cada uno de los parrafos, y el resultado lo pone en entity_name
        Models::Entity.parse(paragraph,index).each do |entity_name|
		#Es decir, entity_name tiene el resultado entities que está en entities.rb
          alias_name = paragraph.scan(Regexp.new("#{Regexp.quote(entity_name)} \\(([^\\)]+)\\)")).map(&:first).first
          #Descomentar los 5 puts para mostrar el resultado de la expresión regular que detecta alias en un párrafo
          #con base en una entidad. Es decir, en cada párrafo, encuentra entidades, y luego busca alias
          #justo delante de ellos.

          #7
          #puts "Párrafo: #{index}"
          #puts "Texto: #{paragraph}"
          #puts "Entidad: #{entity_name}"
          #puts "Alias: #{alias_name}"

          #Si el alias no está vacío entonces
          if alias_name
			#en la base de datos, buscamos o creamos la entidad.
            entity = Models::Entity.find_or_create_by(name: entity_name)
            #creamos el alias asociado a la entidad.
            aliases.create({
              alias: alias_name,
              entity: entity
            })
          #Si sí estuvo vacío, quiere decir que en el párrafo, con la entidad que estamos buscando, no hay alias.
          else
			#en la tabla aliases buscamos el nombre de la entidad.
            alias_entity = aliases.find_by(alias: entity_name)
            #Si encontramos un alias con el nombre de la entidad que estamos buscando.
            if alias_entity
			  #la entidad es igual a la entidad cuyo alias es el nombre de la entidad donde estamos.
              entity = alias_entity.entity
			#Si no hay un alias con el nombre de la entidad, entonces contamos los espacios de la entidad donde estamos.
            #Si hay mas de 0 espacios
            elsif entity_name.count(' ') > 0
			  #creamos la entidad con el nombre de la entidad.
              entity = Models::Entity.find_or_create_by(name: entity_name)
            else
			  #Si no, desechamos la entidad.
              entity = false
            end
          end
          #llenamos la tabla de ocurrencias
          occurrences.create({
            #con entity, que ya lo elegimos en todo el espacio anterior.
            #el índice del párrafo
            #el texto antes de la entidad, que pertenece al párrafo donde estamos.
            entity: entity,
            paragraph: index,
            word: paragraph.split(entity_name).first.count(' ').succ
          }) if entity
        end

        Models::Article.parse(paragraph).each do |article_string|
          word = paragraph.split(article_string).first.count(' ').succ
          laws = Models::Law.joins(:occurrences).where(occurrences: {
            document_id: id,
            paragraph: index,
          }).where('occurrences.word > ?', word).pluck(:name)
          next unless laws.any?

          laws_regexp = laws.map { |law| Regexp.quote(law) }.join('|')
          regexp = Regexp.new("#{article_string}(del|de la) (#{laws_regexp})")
          law_name = paragraph.scan(regexp).map(&:last).first
          law = Models::Law.find_by(name: law_name)
          if law
            article_string.split(/[^\d]/).each do |n|
              n.strip!
              if n != ''
                article = law.articles.create(article: n.to_i)
                occurrences.create({
                  entity: article,
                  paragraph: index,
                  word: word
                })
              end
            end
          end
        end
      end
    end

    def content
      @content ||= Docx::Document.open(name)
    end

    def paragraphs
      @paragraphs ||= content.paragraphs.map(&:text)
    end
  end
end
