#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import errno
import os
import select
import socket
import logging
import fcntl, subprocess

logger = logging.getLogger('main')


BIND_ADDRESS = ('0.0.0.0', 8999)
BACKLOG = 15
CHILDNUM = 50


childrens_pull = []


class ChildController:

    def __init__(self, pipe):
        self.is_free = True
        self.pipe = pipe

    def __repr__(self):
        return '<%s is_free=%s>' % (
            self.__class__.__name__,
            self.is_free)


def handle(sock,p):
    # обработчик, работающий в процессе-потомке

    ## logger.info('Start to process request')

    # получаем все данные до перевода строки
    # (это не очень честный подход, может сожрать сразу несколько строк,
    # если они придут одним пакетом; но для наших целей -- сойдёт)
  in_buffer = b''
  result = b'';
  lines = []
  while True:
    while len(lines)<2:
#        try:
#            select.select([sock],[],[],0)
#        except select.error, e:
#            print e
        in_buffer += sock.recv(1024)
        if len(in_buffer)==0:
            break
            #raise RuntimeError("socket connection broken")
        # print('loop')
        lines = in_buffer.split('\n')

    if len(in_buffer)==0:
        break
    in_buffer = lines[-1]

    ##print(lines)

    ## logger.info('In buffer = ' + repr(in_buffer))

    # изображаем долгую обработку
    # time.sleep(5)
    # получаем результат [не используйте eval!]
#    try:
#        result = str(eval(in_buffer, {}, {}))
#    except Exception as e:
#        result = repr(e)
    #p.stdin.write(in_buffer +b' \n')
    for line in lines[:-1]:
        p.stdin.write(line+b'\n' )
        #while result==b'':


#    	while not result.endswith(b'\n'):
#	    try:
#    		result = p.stdout.read()
#            except Exception:
#                pass
        aline = ''
        while not aline.endswith('\\n"}\n'):
            aline = p.stdout.readline()
#            if not aline.endswith('\\n"}\n'):
            result = result + aline

        #out_buffer = result.encode('utf-8') + b'\r\n'
        out_buffer = result

        ## logger.info('Out buffer = ' + repr(out_buffer))

        # отправляем
        #try:
        sock.sendall(out_buffer+b'<|>')
    #except socket.error, e:
	#    print e
        #    break
        #socket.error: [Errno 104] Connection reset by peer

        ## logger.info('Done.')
    lines = []
    result = ''


def create_child(listen_sock):
    # создаём пару связанных анонимных сокетов
    child_pipe, parent_pipe = socket.socketpair()
    p = subprocess.Popen(['./mystem', '--format', 'json', '-ncs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,bufsize=1)

    # Fix the pipes to be nonblocking
    #fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    #fcntl.fcntl(p.stderr.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

    # порождаем потомка
    pid = os.fork()
    if pid == 0:
        # это выполняется в дочернем процессе
        child_pipe.close()
        # запускаем бесконечный цикл обработки запросов;
        # очень важно, что этот цикл именно бесконечный,
        # потомок не должен выходить из create_child,
        # иначе начнётся безудержное размножение и катаклизм
        while True:
            # блокирующее чтение из сокета, соединяющего
            # потомка с родителем
            command = parent_pipe.recv(1)
            # мы получили единственную возможную команду
            logger.info('Child get command=%s' % repr(command))
            # получаем соединение
            connection, (client_ip, clinet_port) = listen_sock.accept()
            logger.info('Accept connection %s:%d' % (client_ip, clinet_port))
            logger.info('Child send "begin"')
            parent_pipe.send(b'B')
            # отправляем соединение на обработку
            try:
                handle(connection,p)
            except socket.error, e:
                print e
            # всё аккуратненько закрываем
            connection.close()
            # отправляем родителю информацию, что мы освободились
            logger.info('Child send "free"')
            parent_pipe.send(b'F')
    # это выполняется в родительском процессе
    logger.info('Starting child with PID: %s' % pid)
    childrens_pull.append(ChildController(child_pipe))
    # закрываем ненужные дескрипторы
    parent_pipe.close()
    return child_pipe


def prepare_childs_and_serve_forever():
    # открываем сокет
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use the port
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # неблокирующий режим
    #listen_sock.setblocking(0)
    listen_sock.bind(BIND_ADDRESS)
    listen_sock.listen(BACKLOG)
    logger.info('Listning no %s:%d...' % BIND_ADDRESS)
    # создаём потомков
    for i in range(CHILDNUM):
        create_child(listen_sock)
    # массив сокетов-кандидатов на чтение
    to_read = [listen_sock] + [c.pipe.fileno() for c in childrens_pull]
    while True:
        readables, writables, exceptions = select.select(to_read, [], [])
        if listen_sock in readables:
            logger.info('Listning socket is readable')
            # кажется, у нас имеется входящее соединение
            # ищем свободного потомка
            for c in childrens_pull:
                if c.is_free:
                    # передаём свободному потому команду принять подключение
                    logger.info('Send command "accept connection" to child')
                    c.pipe.send(b'A')
                    # ждём подтверждения от потомка, что он
                    # взял в обработку соединение
                    command = c.pipe.recv(1)
                    # строго говоря, тут можно бы и ошибки принимать,
                    # но у нас снова будет только одна команда
                    # "принято в обработку"
                    logger.info(
                        'Parent get command %s from child. Mark free.' %
                        repr(command))
                    # отмечаем потомка, как занятого (хотя, строго говоря, это ещё не факт)
                    c.is_free = False
                    break
                else:
                    logger.info('Child not free')
            else:
                raise Exception('No more childrens.')
        for c in childrens_pull:
            if c.pipe.fileno() in readables:
                # мы получили команду от потомка
                command = c.pipe.recv(1)
                if command != b'F':
                    raise Exception(repr(command))
                logger.info(
                    'Parent get command %s from child. Mark free.' %
                    repr(command))
                # бывает только одна команда: "я освободился"
                c.is_free = True


def main():
    # настраиваем логгинг
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(process)s] %(message)s',
        '%H:%M:%S'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info('Run')
    prepare_childs_and_serve_forever()


if __name__ == '__main__':
    main()
