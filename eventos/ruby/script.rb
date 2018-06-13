require './config/database'
require './lib/models/document'

#Recibe como parámetro el archivo en la carpeta DOCX
puts ARGV[0]
#se busca tabla document de la base de datos, y si no está, la crea.
document = Models::Document.find_or_create_by(name: ARGV[0])
#Al registro de esa tabla se le aplica document.process! en un bloque de transacción para evitar que se guarden fallos.
ActiveRecord::Base.transaction { document.process! }
