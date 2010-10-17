#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hammer of Thor: Proxy SOCKS v5

Website: http://code.google.com/p/hammerofthor/
Licencia: GNU GPL v3.

    Hammer of Thor - Simple SOCKS v5 Proxy

    Copyright (C) 2010 Alejandro Santos

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, sys, struct, socket
from collections import deque

try:
    from twisted.internet.protocol import Protocol, Factory, ClientFactory, ClientCreator
    from twisted.internet import reactor
    # from twisted.protocols.socks import SOCKSv4
except ImportError:
    print "Necesita tener instalado python-twisted. Para mas informacion visitar:"
    print ">>> http://code.google.com/p/hammerofthor/"
    print
    sys.exit(0)

THOR_MAX_ATTEMPTS = 20

# FIXME: La siguiente linea es *TODA* la magia del proxy.
#        ¿0.33 esta bien? Con un valor mas grande Internet anda *MUY* lento :(

THOR_PATIENCE = 0.33

def THOR_PRINT(*args, **kwargs):
    for e in args:
        print e,
    print

THOR_PRINT_NULL = lambda *args, **kwargs: None

THOR_ERROR = THOR_PRINT
THOR_INFO = THOR_PRINT
THOR_DEBUG = THOR_PRINT

SOCKS5_REPLY_CMD_UNSUPPORTED = 0x07
SOCKS5_ADDRESS_NOT_SUPPORTED = 0x08

SOCKS4_REJECT = 91
SOCKS4_GRANTED = 90

def THOR_STOP():
    THOR_DEBUG("THOR_STOP")
    reactor.stop()

class ThorFatalException(Exception):
    pass

class TunnelHandlerBase(object):
    def __init__(self, prot):
        self.prot = prot
        self._thor_buffer_in = ""

    def dataReceived(self, data):
        raise Exception("Not implemented")

    def _handleData(self):
        raise Exception("Not implemented")

    def remoteConnectionMade(self):
        raise Exception("Not implemented")

    def isConnected(self):
        raise Exception("Not implemented")

    def _flushData(self):
        self.prot.clientSendData(self._thor_buffer_in)
        self._thor_buffer_in = ""

class TunnelHandlerSocks4(TunnelHandlerBase):
    def __init__(self, prot):
        super(TunnelHandlerSocks4, self).__init__(prot)
        self._thor_state = 0

    def dataReceived(self, data):
        self._thor_buffer_in += data

        try:
            self._handleData()
        except ThorFatalException, e:
            THOR_ERROR(e)
            self.prot.transport.loseConnection()

    def _handleData(self):
        # Estado 0: Esperando el welcome del cliente
        if self._thor_state == 0:
            THOR_DEBUG("Socks4: nueva conexion, data: ", repr(self._thor_buffer_in))
            
            count = len(self._thor_buffer_in)
            data = self._thor_buffer_in

            if count > 0 and ord(data[0]) != 0x04:
                self._sendSocksReply(SOCKS4_REJECT)
                raise ThorFatalException("Solo se aceptan conexiones SOCKSv4")

            byte_count = 8
            if len(self._thor_buffer_in) < byte_count:
                THOR_DEBUG("Faltan datos, cant: ", count)
                return

            version, cmd, dest_port, dest_addr = struct.unpack(">BBHL",
                self._thor_buffer_in[:byte_count])


            if cmd != 0x01:
                self._sendSocksReply(SOCKS4_REJECT)
                raise ThorFatalException("Solo se acepta el comando: CONNECT")


            null_pos = self._thor_buffer_in.find(chr(0), byte_count)
            if null_pos == -1:
                THOR_DEBUG("Faltan datos, cant: ", count)
                return

            byte_count = null_pos + 1

            self._thor_buffer_in = self._thor_buffer_in[byte_count:]
            self._thor_state = 1

            dest_addr = socket.inet_ntoa(struct.pack(">L", dest_addr))
            self.prot.connectRemoteTCP(dest_addr, dest_port)

        # Estado 1: Esperando conexion remota
        if self._thor_state == 1:
            pass

        # Estado 2: Tunel activo
        if self._thor_state == 2:
            self._flushData()

    def remoteConnectionMade(self):
        if self._thor_state == 1:
            self._thor_state = 2
            self._sendSocksReply(SOCKS4_GRANTED)
        else:
            THOR_ERROR("SOCKSv4: Estado invalido", self._thor_state)
            THOR_STOP()

    def _sendSocksReply(self, code):
        self.prot.transport.write(struct.pack(">BBHL", 0x00, code, 0, 0))

    def isConnected(self):
        return self._thor_state == 2

class TunnelHandlerSocks5(TunnelHandlerBase):
    def __init__(self, prot):
        super(TunnelHandlerSocks5, self).__init__(prot)
        self._thor_state = 0
        self._thor_buffer_in = ""

    def dataReceived(self, data):
        self._thor_buffer_in += data

        try:
            self._handleData()
        except ThorFatalException, e:
            THOR_ERROR(e)            
            self.prot.transport.loseConnection()

    def _handleData(self):
        # Estado 0: esperando el welcome del cliente

        if self._thor_state == 0:
            if len(self._thor_buffer_in) >= 3:
                THOR_DEBUG("Socks5: Nueva conexion, data: ", repr(self._thor_buffer_in))

                bytes_count = 2
                version, nmethods = struct.unpack(">BB",
                    self._thor_buffer_in[0:2])

                # FIXME: Solo acepto conexiones SOCKS versión 5
                #
                if version != 0x05:
                    raise ThorFatalException("Solo se aceptan conexiones SOCKS v5, " + \
                        " solicitada: %d" % version)

                
                if nmethods < 1:
                    raise ThorFatalException("No hay metodos de conexion")

                bytes_count += nmethods
                if len(self._thor_buffer_in) < bytes_count:
                    return

                method_list = struct.unpack(">%dB" % nmethods,
                    self._thor_buffer_in[2:bytes_count])

                # FIXME: Solo acepto conexiones anonimas
                #
                if 0x00 not in method_list:
                    raise ThorFatalException("Metodo de conexion no encontrado")

                self._thor_buffer_in = self._thor_buffer_in[bytes_count:]
                self.prot.transport.write(struct.pack(">BB", 0x05, 0x00))
                self._thor_state = 1

        # Estado 1: esperando los datos de conexion del cliente
        if self._thor_state == 1:
            if len(self._thor_buffer_in) >= 10:
                byte_count = 4
                ver, cmd, rsv, atyp = struct.unpack(">BBBB",
                    self._thor_buffer_in[0:4])

                # FIXME: Solo Socks v5, comando CONNECT y conexiones IPv4.
                #
                if ver != 0x05 or rsv != 0x00:
                    raise ThorFatalException("Solo se aceptan conexiones SOCKS v5")

                if cmd != 0x01 or cmd != 0x03:
                    self._sendSocksReply(SOCKS5_REPLY_CMD_UNSUPPORTED)
                    raise ThorFatalException("Solo se aceptan los comandos: CONNECT, UDP")

                if atyp != 0x01:
                    self._sendSocksReply(SOCKS5_ADDRESS_NOT_SUPPORTED)
                    raise ThorFatalException("Solo se aceptan conexiones IPv4")

                byte_count += 6
                dest_addr, dest_port = struct.unpack(">LH", self._thor_buffer_in[4:10])
                dest_addr = socket.inet_ntoa(struct.pack(">L", dest_addr))

                THOR_INFO("Intento de conexion a: ", "%s:%d" % (dest_addr, dest_port))

                # FIXME: Validar que el par (dest_addr, dest_port) sea valido.
                #

                self._thor_state = 2
                self._thor_buffer_in = self._thor_buffer_in[byte_count:]

                if cmd == 0x01:
                    self.prot.connectRemoteTCP(dest_addr, dest_port)
                elif cmd == 0x03:
                    self.prot.connectRemoteUDP(dest_addr, dest_port)

        # Estado 2: esperando conectarse al cliente
        if self._thor_state == 2:
            pass

        # Estado 3: conexion establecida
        if self._thor_state == 3:
            self._flushData()

    def _sendSocksReply(self, rep):
        """
        Respuesta al pedido de conexion.
        """
        self.prot.transport.write(struct.pack(">BBBBLH",
            0x05, rep, 0x00, 0x01, 0x0L, 0x0))

    def remoteConnectionMade(self):
        if self._thor_state == 2:
            self._thor_state = 3
            self._sendSocksReply(0x00)
            self._flushData()
        else:
            THOR_ERROR("Error fatal: estado invalido: %d" % self._thor_state)
            THOR_STOP()

    def isConnected(self):
        return self._thor_state == 3

class ThorProtocol(Protocol):
    def __init__(self, *args, **kwargs):
        # Estoy usando "_thor" de prefijo porque no conozco las variables de 
        # instancia de Protocol.

        self._thor_tunnel = TunnelHandlerSocks4(self)
        self._thor_client_bytes = 0
        self._thor_server_bytes = 0
        self._thor_client = None

    def dataReceived(self, data):
        self._thor_client_bytes += len(data)
        self._thor_tunnel.dataReceived(data)

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        if self._thor_client is not None:
            cli = self._thor_client
            self._thor_client = None
            cli.transport.loseConnection()

    def remoteConnectionMade(self):
        self._thor_tunnel.remoteConnectionMade()

    def _flushData(self):
        self._thor_client.transport.write(self._thor_buffer_in)
        self._thor_buffer_in = ""

    def clientSendData(self, data):
        self._thor_client.transport.write(data)

    def connectRemoteTCP(self, dest_addr, dest_port):
        reactor.connectTCP(dest_addr, dest_port,
            ThorClientFactory(self, dest_addr, dest_port, dest_port == 80))

    def connectRemoteUDP(self, dest_addr, dest_port):
        pass

class ThorClient(Protocol):
    """
    Implementacion por default del endpoint cliente del servidor socks. Al detectar un
    error lo propaga directamente al cliente.
    """

    def __init__(self, prot):
        self._thor_prot = prot
        self._thor_prot._thor_client = self

    def dataReceived(self, data):
        if self._thor_prot is not None:
            self._thor_prot.transport.write(data)

    def connectionMade(self):
        THOR_DEBUG("ThorClient :: connectionMade")
        self._thor_prot.remoteConnectionMade()

    def connectionLost(self, reason):
        THOR_DEBUG("ThorClient :: connectionLost")

        if self._thor_prot is not None:
            prot = self._thor_prot
            self._thor_prot = None
            prot.transport.loseConnection()

class ThorHammerClient(ThorClient):
    """
    Esta clase es responsable de insistir hasta poder acceder al sitio web, cuando detecta
    un error espera.
    """

    def dataReceived(self, data):
        self.timeoutOnConnect(False)
        ThorClient.dataReceived(self, data)

    def connectionMade(self):
        THOR_DEBUG("ThorHammerClient :: connectionMade")
        self._thor_is_waiting = True
        reactor.callLater(THOR_PATIENCE, self.timeoutOnConnect, True)

    def connectionLost(self, reason):
        if self._thor_is_waiting:
            self._thor_is_waiting = False
            # FIXME: Reconnect? La Factory atrapa el error antes que llege aca.
            THOR_INFO("THOR HAMMER IS WAITING")
        else:
            ThorClient.connectionLost(self, reason)

    def timeoutOnConnect(self, timeOut):
        if self._thor_is_waiting:
            THOR_DEBUG("timeoutOnConnect: ", timeOut)

            # Si, estoy accediendo a variables privadas.
            # Si, esta un poco atado con alambre.
            # Si, este software nunca deberia haber sido escrito pero el ISP esta roto.

            self._thor_is_waiting = False
            self._thor_prot.remoteConnectionMade()

class ThorClientFactory(ClientFactory):
    def __init__(self, thor_prot, host, port, retry):
        self._thor_prot = thor_prot
        self._thor_host = host
        self._thor_port = port
        self._thor_counter = 0
        self._thor_retry = retry

    def startedConnecting(self, connector):
        THOR_DEBUG("ThorClientFactory :: startedConnecting ", connector)

        ClientFactory.startedConnecting(self, connector)

    def buildProtocol(self, addr):
        THOR_DEBUG("buildProtocol: ", addr)

        if self._thor_retry:
            return ThorHammerClient(self._thor_prot)
        else:
            return ThorClient(self._thor_prot)

    def clientConnectionLost(self, connector, reason):
        THOR_DEBUG("clientConnectionLost: ", connector, reason)

        self._thorReconnect(connector)

    def clientConnectionFailed(self, connector, reason):
        THOR_DEBUG("clientConnectionFailed: ", connector, reason)

        self._thorReconnect(connector)

    def _thorReconnect(self, connector):
        THOR_DEBUG("ThorClientFactory :: _thorReconnect", connector)

        if self._thor_prot._thor_tunnel.isConnected():
            # Llegado a este punto la conexion fue exitosa y no hace falta
            # seguir insistiendo.
            self._thor_prot.transport.loseConnection()
            return

        THOR_INFO("Thor esta esperando")

        if not self._thor_retry or self._thor_counter >= THOR_MAX_ATTEMPTS:
            self._thor_prot._sendSocksReply(0x05)
            self._thor_prot.transport.loseConnection()
        elif self._thor_counter < THOR_MAX_ATTEMPTS:
            #
            # El Martillo de Thor hay que usarlo sabiamente, no hay que
            # insistir demasiado rapido. La idea es parecida a CSMA-CD:
            #
            # La primer vez espera 0.33 segundos para reintentar.
            # La segunda vez espera 0.66 segundos para reintentar.
            # La tercer vez espera 0.99 segundos para reintentar...
            # Y asi hasta llegar a 1.98 segundos. Ahi vuelve a 0.33.
            #
            # Este camino lo hace 20 veces como maximo (deberia ser mas que suficiente).
            #
            reactor.callLater(((self._thor_counter % 6) + 1) * THOR_PATIENCE,
                self._thorRetry, connector)

    def _thorRetry(self, connector):
        self._thor_counter += 1
        connector.connect()

class ThorFactory(Factory):
    protocol = ThorProtocol

def main():
    reactor.listenTCP(8081, ThorFactory(), interface='127.0.0.1')
    THOR_INFO("Thor esta a la escucha.")
    reactor.run()

if __name__ == '__main__':
    main()

