
Hammer of Thor Socks v5 Proxy.

Website: http://code.google.com/p/hammerofthor/
Licence: GNU GPL v3
Author: Alejandro Santos <alejolp arroba alejolp.com.ar>

Hammer of Thor es un proxy socks para evitar problemas tecnicos en ciertos
proveedores de Internet con una mala configuracion de acceso.

El autor de programa tiene la esperanza que este software le resulte util
a otros, pero de ninguna manera se hace responsable por cualquier daño de
cualquier clase que le genere a los usuarios del mismo.

Antes de empezar
----------------

El proxy fue diseñado para correr en la PC del usuario afectado. No esta 
pensado para ser usado abiertamente en Internet ya que no tiene restricciones
de seguridad.

Repito: El proxy no tiene ninguna restriccion de seguridad, por lo que deberan
configurar correctamente el firewall de su PC.

Es un patch para no tener que sufrir la incorrecta configuracion del ISP. 

Lamentablemente este software es una solucion de compromiso, y como desventaja
tiene que la navegacion de los sitios web puede ser mucho mas lenta de lo
normal.

Eso se debe a que la deteccion del flag RST se hace disparando un timer que 
espera una determina cantidad de tiempo, calibrado sin ninguna clase de metodo
cientifico.

Repito: este proxy no es una solucion permanente sino una forma de salir del
paso.

INSTALACION
-----------

El proxy no requiere instalacion adicional y puede ser ejecutado libremente.

Los requisitos son:

- Tener una version moderna de Python instalada (2.6). No funciona con Python 3.

- Tener una version moderna de las librerias Twisted (10.1).

Instalacion en Debian y Ubuntu
------------------------------

Instalar los paquetes:

- python
- python-twisted

Instalacion en Windows
----------------------

Bajar Python 2.6 desde:

  http://python.org

Bajar Twisted para Windows desde:

  http://twistedmatrix.com/trac/

A la fecha, solo hay paquetes de Twisted Windows para Python 2.6.

MODO DE USO
-----------

Primero, hace falta iniciar el Proxy. Para ello hay que abrir una terminal y
ejecutar:

# python2.6 hammerofthor.py

Segundo, configurar el navegador para usar correctamente el proxy.

Host:   localhost
Puerto: 8081

Firefox/Iceweasel:
------------------

- Acceder a la ventana "Preferencias" desde el menu "Editar".
- Dentro de la seccion "Avanzada" seleccionar la pestaña "Red"
- Hacer un click en el boton "Configuracion".
- Elegir la opcion: "Configuracion manual de Proxy".
- Verificar que la opcion "Usar el mismo proxy para todos los protocol" se
  encuentre desactivada.
- Eliminar el contenido de todos los campos de "Proxy" excepto el ultimo.
- Dentro del campo "Servidor SOCKS" escribir: 127.0.0.1
- Dentro del campo "Puerto" del servidor SOCKS escribir: 8081
- Elegir la opcion "SOCKS v5".
- Dentro del campo "Sin proxy para:" verifica que diga: localhost, 127.0.0.1, 192.168.0.0/16

Hacer click en Aceptar.

Notas
-----

Los acentos en este documento fueron deliberadamente omitidos para reducir los
problemas de encoding.


