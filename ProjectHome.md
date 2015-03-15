# Introducción #

> _"All problems in computer science can be solved by another level of indirection."_

Hammer of Thor es un Proxy para evitar las limitaciones tecnicas de un ISP defectuoso.

# Descarga #

A la derecha de esta pagina hay bloque verde que dice "Featured Downloads". Hacer click en la flechita.

# Descripción #

Existe cierto ISP que de forma aleatoria falla misteriosamente. Tecnicamente, se genera un paquete RST sin sentido que cierra las conexiones TCP, ocasionando problemas al navegar tales como falta de estilos CSS, imagenes e incluso la incapacidad de visitar sitios web.

La función del Proxy «Hammer of Thor» es detectar la situacion del paquete anómalo RST y reintentar establecer la conexión hasta que se logre o hasta que se cumpla cierto límite de fallas.

El algoritmo utilizado para mitigar el problema se basa en el mismo principio que [CSMA/CD](http://en.wikipedia.org/wiki/Carrier_Sense_Multiple_Access_With_Collision_Detection) de Ethernet para no sobrecargar los recursos de red. Asimismo solamente se realiza sobre las conexiones salientes en el puerto TCP/80, por lo que HTTPS u otros servicios no deberían ser afectados por el Proxy.

Un efecto colateral del uso de «Hammer of Thor» es que la navegación puede ser más lenta. Esto de debe a que cuando se detecta el paquete RST anómalo el Proxy espera cierto tiempo hasta volver a reintentar el pedido, respetando el mismo principio que CSMA/CD.

Aún así, es preferible que la navegación sea ligeramente más lenta a que las páginas directamente no carguen.

# Preguntas Frecuentes #

Visitar la sección especial llamada PreguntasFrecuentes.

# Instalación #

En Debian y Ubuntu hace falta instalar los paquetes:

  * python (version 2.5, 2.6)
  * python-twisted (version 8.x, 9.x, 10.1)

# Instrucciones para Firefox e Iceweasel #

  1. Acceder a la ventana "Preferencias" desde el menu "Editar".
  1. Dentro de la seccion "Avanzada" seleccionar la pestaña "Red"
  1. Hacer un click en el boton "Configuracion".
  1. Elegir la opcion: "Configuracion manual de Proxy".
  1. Verificar que la opcion "Usar el mismo proxy para todos los protocol" se encuentre desactivada.
  1. Eliminar el contenido de todos los campos de "Proxy" excepto el ultimo.
  1. Dentro del campo "Servidor SOCKS" escribir: 127.0.0.1
  1. Dentro del campo "Puerto" del servidor SOCKS escribir: 8081
  1. Elegir la opcion "SOCKS v5".
  1. Dentro del campo "Sin proxy para:" verifica que diga: localhost, 127.0.0.1, 192.168.0.0/16

Verificar que los datos sean ingresados en el campo de SOCKS y que la version sea SOCKS v5.

# <font color='red'>Importante</font> Desactivar el proxy #

En caso de que se quiera desactivar el Proxy y navegar normalmente, hace falta en la misma ventana marcar la opción: **"Sin Proxy"**.

## Ejemplo ##

![http://img707.imageshack.us/img707/5016/screenshotconfiguracind.png](http://img707.imageshack.us/img707/5016/screenshotconfiguracind.png)
