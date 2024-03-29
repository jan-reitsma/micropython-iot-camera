#!/usr/bin/env python3
'''
This program listens for connections, saves received binary streams into jpg files.
'''

import socket, datetime, os, time, sys
sys.path.append('/home/jimra/STU/PROJ/github/micropython-iot-camera/Local/Signal-Client')
import imgbb_signal as sign
from settings import IMG_SUBDIR, LOG_SUBDIR

MAIN_DIR = os.getcwd()
send_signal = False

def server():
    os.chdir(MAIN_DIR)
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(3600)
    s.bind(('', 5555))
    s.listen(5)
    
    if not os.path.exists(IMG_SUBDIR):
        os.mkdir(IMG_SUBDIR)

    print('server: init')
    append_to_log('server.log', datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + ': start')

    return s
    

def append_to_log(file_name, text):
    os.chdir(MAIN_DIR)
    if not os.path.exists(LOG_SUBDIR):
        os.mkdir(LOG_SUBDIR)
    
    log = open(LOG_SUBDIR+file_name, 'a')
    log.write(text + '\n')
    log.close()


def run_forever():   
    global send_signal
    send_signal = False
    try:
        s = server()
        while True:
            print(f"server: listening")
            conn, addr = s.accept()
            conn.settimeout(20)
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y%m%d-%H%M%S')

            print("server: connection from:" + str(addr) + ' at ' + timestamp)
            append_to_log('server.log',
            datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + 
            ': connection from:' + str(addr))

           
            # check first 5 chars:
            d = conn.recv(5)

            if(d.decode() == 'local'):
#                print('local true')
                send_signal = False

            if(d.decode() == 'remot'):
                print('remot true')
                send_signal = True
                
#            else:
#                print('error')
#                raise ValueError()
#
            # file numbering:
            file_name = timestamp +'.jpg'

            #os.chdir(IMG_SUBDIR)
            f = open(IMG_SUBDIR+file_name, 'wb')                   

            print(f"server: saving file: {file_name} ")

            # receive and write blocks:
            byte_count = 0            
            print("server: receiving file")
            start = time.time()

            try:                
                d = conn.recv(2048)
                print('server:', end='')
                while (len(d) > 0):
                    byte_count += len(d)
                    print('.', end='')      
                    f.write(d)
                    d = conn.recv(2048)
                end = time.time()
                diff = end - start
                print(f' done, {byte_count} bytes in {diff} seconds, speed: {str(int(byte_count/diff))} bytes/sec.')   

                # append log entry           
                print("server: done receiving")
                append_to_log('server.log', datetime.datetime.now().strftime\
                    ('%Y%m%d-%H%M%S') +  ': file locally saved: ' + file_name)
                
                file_sent = False
                # if flag send_signal == True, file will be sent to Signal message 
                # using external Python script 
                if send_signal == True:
                    print('tcp server cwd:', os.getcwd())
                    file_sent = sign.send(file_name)
                        
                if file_sent:
                    append_to_log('server.log',
                    datetime.datetime.now().strftime('%Y%m%d-%H%M%S') +  
                    ': file sent as signal message: ' + file_name)

            except socket.timeout:
                print("ERROR the client stopped unexpectedly!")
                append_to_log('server.log', 
                datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + 
                 ': ERROR the client stopped unexpectedly!')

            finally:    
                f.close()
            
        
            conn.close()
           
        s.close()


    except KeyboardInterrupt:
        if s is not None: 
            s.close()
        print("server: Keyboard Interrupt")
        append_to_log('server.log', datetime.datetime.now().strftime('%Y%m%d-%H%M%S') +  ': keyboard interrupt')

    except socket.timeout:
        if s is not None: 
            s.close()
        restart()

    except Exception as e:
        if s is not None: 
            s.close()
        handle_exception(e)
    
def restart():
    run_forever()

def handle_exception(e):
    print(e)
    exception_name = str(type(e).__name__)    
    append_to_log('server.log', datetime.datetime.now().strftime('%Y%m%d-%H%M%S') +  
            ": server " + exception_name + ",  restarting now")
    os.chdir(MAIN_DIR)
    run_forever()


run_forever()


