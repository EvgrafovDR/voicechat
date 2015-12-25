#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import json
import threading
import logging
import configparser
import time
import mysql.connector
import datetime
import csv
import sys
import re
import subprocess
import  xml.etree.ElementTree as ET
# Сообщение отладочное
#logging.debug( u'This is a debug message' )
# Сообщение информационное
#logging.info( u'This is an info message' )
# Сообщение предупреждение
#logging.warning( u'This is a warning' )
# Сообщение ошибки
#logging.error( u'This is an error message' )
# Сообщение критическое
#logging.critical( u'FATAL!!!' )

onlines={}
astercon=""
astconnected = 0
event = True
go = {}
connect =True
reloads = {}
logfile = '/etc/callchat/ctrlog.log'
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG, filename = logfile)
ping = time.time()
socks = {}
pings = {}
mancount = {}
answered = {}
clanswered = {}
started = {}
rec_threads = {}
parse_thread = ""
operators = ["BMI",]
prices = {}
validation = True
callid = True
order = True
statsended = False
asterping = True
asterpings = {}
available = {}
uids = []

#производит первоначальную конфигурацию
def configure():
     global operators
     global validation
     global callid
     global order
     config = configparser.ConfigParser()
     config.readfp(open('/etc/callchat/ctrlconf.cnfg'))
     logfile=config.get('logging', 'logfile')
     logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                         level = logging.DEBUG, filename = logfile)
     lvl=config.get('logging', 'level')
     if lvl=="debug":
         logging.getLogger().setLevel(logging.DEBUG)
     elif lvl=="info":
         logging.getLogger().setLevel(logging.INFO)
     elif lvl=="warning":
         logging.getLogger().setLevel(logging.WARNING)
     elif lvl=="error":
         logging.getLogger().setLevel(logging.ERROR)
     elif lvl=="critical":
         logging.getLogger().setLevel(logging.CRITICAL)


#отправляет запросы в сокет астериска
def sending(str_to_send, s):
  for l in str_to_send.split('\n'):
    logging.debug(u'Sending>' + l)
    s.send(bytes(l+'\r\n', "UTF-8"))

def connectToAsterisk(username, password):
    HOST = '127.0.0.1'
    PORT = 6868
    login = """Action: login
Username: %(username)s
Secret: %(password)s
"""
    login_to_send = login % {
        'username': username,
        'password': password
    }
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    sending(login_to_send, s)
    return s

#отключается от астериска, закрывает сокет
def disconnectFromAsterisk(s):
    logoff = """Action: Logoff
"""
    sending(logoff, s)
    s.close()

def connectToMysql():
   cnx = mysql.connector.connect(user='asterisk', password='asterisk',
                              host='127.0.0.1',
                              database='controllerdb')
   return cnx

def disconnectFromMysql(cnx):
   cnx.close()

#отправляет запрос на звонок к астериску
def callsend(action_id, manager, client, message, conn):
    global astconnected
    global astercon
    global answered
    global clanswered
    global started
    global mancount
    try:
        dial = """Action: originate
Channel: %(manager)s
Exten: %(client)s
Context: %(provider)s-message
Priority: 1
Timeout: %(mtimeout)s
Async: true
Variable: MFILE=%(mfile)s
CallerID: %(client)s
ActionID: %(id)s
ChannelId: %(id)s
"""
        if(astconnected==0):
            astercon=connectToAsterisk("asterisk", "asterisk")
        astconnected+=1

        subprocess.call("wget -U 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5' 'https://tts.voicetech.yandex.net/generate?text=\""+message+"\"&format=wav&lang=ru-RU&emotion=good&speaker=jane&key=b3a7cba8-c45d-465b-8e9a-adaccff0a70c' -O /var/lib/asterisk/wavs/"+action_id+".wav", shell=True)
        subprocess.call("sox -t wav '/var/lib/asterisk/wavs/"+ action_id +".wav' -r 8000 -c1 -t gsm '/var/lib/asterisk/messages/"+action_id+".gsm'", shell=True)

        tofile = "/var/lib/asterisk/messages/" + action_id
        dial_to_send = dial % {
            'manager': 'SIP/BMI/'+manager,
            'client': client,
            'provider': "BMI",
            'id': action_id,
            'mtimeout': 40*1000,
            'mfile': tofile
        }
        logging.debug("sending to asterisk: "+dial_to_send)
        sending(dial_to_send, astercon)
        astconnected-=1
    except Exception as ex:
        print("callsend error "+ str(err))
        logging.error("callsend error " + str(err))

def sockclose(s):
    try:
        s.shutdown(socket.SHUT_RDWR)
    except:
        pass

    try:
        s.close()
    except:
        pass

def parse(sock, block):
  global event
  global go
  global reload
  global socks
  global statsended
  global asterpings
  global uids
  bl="Main"
  try:
          strs = block.split("\r\n")
          if(len(strs[0].split(":"))>1 and \
          (strs[0].split(":")[1].strip()=="DialBegin" or \
          strs[0].split(":")[1].strip()=="DialEnd" or \
          strs[0].split(":")[1].strip()=="Hangup" or \
          strs[0].split(":")[1].strip()=="VarSet" or \
          strs[0].split(":")[1].strip()=="StatusComplete" )):
            logging.debug(block)
            tuple1=[]
            for item in block.split('\r\n'):
                if(len(item.split(": "))==2):
                    tuple1.append(item.split(": "))
            blk = dict((k.strip(), v.strip()) for k, v in tuple1)
            if(blk["Event"] == "Hangup"):
                bl="Hangup"
                uniqueid = blk["Uniqueid"]
                logging.debug("Hanged up " + uniqueid)
                if(blk["Cause"]=="16" and uniqueid in uids):
                    subprocess.call("sox /var/lib/asterisk/records/"+ uniqueid +".gsm -r 44100 -a /var/lib/asterisk/records/"+uniqueid+".wav", shell=True)
                    script_response = subprocess.check_output(["php", "/etc/callchat/recognize.php", "/var/lib/asterisk/records/"+uniqueid+".wav"])
                    tree = ET.ElementTree(ET.fromstring(script_response))
                    root = tree.getroot()
                    res = root[0].text
                    send(socks[uniqueid], {"action": "message", "text":res, "id":uniqueid})
  except socket.error as err:
          print("parser socket error in block "+ bl +":" + str(err))
          logging.error("parser socket error in block "+ bl +":" + str(err))
          reload = True
          event = False
          disconnectFromAsterisk(sock)
  except Exception as ex:
          print("parser error in block "+ bl +":" + str(ex))
          logging.error("parser error in block "+ bl +":" + str(ex))

# парсит event'ы
def eventparser():
  global event
  global go
  global reload
  sock=connectToAsterisk("parser", "asterisk")
  while event:
        try:
            start = True
            data = rec = ''
            while(start or data[-4:] != "\r\n\r\n" and len(rec) > 0):
                start = False
                rec = sock.recv(1024)
                data += rec.decode("UTF-8")
            blocks = data.split("\r\n\r\n")
        except socket.error as err:
            print("event socket error:" + str(err))
            logging.error("event socket error:" + str(err))
            reload = True
            event = False
            disconnectFromAsterisk(sock)
        except Exception as ex:
            print("event error:" + str(ex))
            logging.error("event error:" + str(ex))
        for block in blocks:
            p_thread = threading.Thread(target=parse, args=(sock, block), name='parse')
            p_thread.daemon = True
            p_thread.start()


def send(s, data):
    msg = bytes(json.dumps(data) + "\r\n", 'UTF-8')
    msgLen = len(msg)
    sent = 0
    logging.debug("send to chat: "+str(msg))
    while (sent < msgLen):
        try:
            sl = s.send(msg[sent:])
            if sl == 0:
                print("Channel broken")
            sent += sl
        except Exception as ex:
            print("%s" % ex)
            break
    return sent

#обработка данных, поступающих с сервера
def receiver(conn, addr):
    global operator
    global onlines
    global reloads
    global pings
    while onlines[addr[0]]:
      try:
        datas = rec = ''
        start=True
        while(start or datas[-2:] != "\r\n" and len(rec) > 0):
            start = False
            rec = conn.recv(1024)
            datas += rec.decode("utf-8")
        for data in datas.split("\r\n"):
          if(data.strip() != "" and onlines[addr[0]]):
            logging.debug(u'received message: '+ data)
            request=json.loads(data)
            #обработка пинга
            if request["action"] == "ping":
                send(conn, {"action":"pong"})
                logging.debug("ping from "+addr[0])
            elif request["action"] == "pong":
                pings[addr[0]]=time.time()
                logging.debug("pong from "+addr[0])
            elif request["action"] == "message":
                uids.append(request["id"])
                logging.debug("call to " + request["number"] + " from " + request["from"])
                socks.update({str(request["id"]): conn})
                send_thread=threading.Thread(target=callsend, args=(request["id"], request["number"], request["from"], request["text"], conn), name='callsend')
                send_thread.daemon = True
                send_thread.start()
      except socket.error as err:
          print("reciever socket error: %s" % err)
          logging.error("reciever socket error: "+err)
          reloads[addr[0]] = True
          onlines[addr[0]] = False
      except Exception as ex:
        print("ошибка ресивера: %s" % ex)
        logging.error("reciever error: "+ex)

def connector(sock, c):
    global connect
    global go
    global pings
    global rec_threads
    global onlines
    global reloads
    while connect:
        try:
            conn, addr = sock.accept()
            print(str(addr))
            reloads.update({addr[0]: False})
            while(addr in onlines.keys()):
                pass
            print("Connected from " + addr[0])
            onlines.update({addr[0]: True})
            go.update({addr[0]: True})
            logging.debug(u'socket connected from '+addr[0])
            rec_thread = threading.Thread(target=receiver, args=(conn, addr), name='receiver')
            rec_thread.daemon = True
            rec_thread.start()
            rec_threads.update({addr[0]:rec_thread})
            pings.update({addr[0]:time.time()})
            ping_thread = threading.Thread(target=pinger, args=(conn, addr), name='pinger')
            ping_thread.daemon = True
            ping_thread.start()
        except socket.error as err:
            print("socket error: %s" % str(err))
            logging.error("connector socket error: "+str(err))
        except Exception as ex:
            print("ошибка коннектера: %s" % str(ex))
            logging.error("connector error: "+str(ex))

#пингующий поток
def pinger(conn, addr):
    global go
    global onlines
    global rec_threads
    global reloads
    global pings
    while go[addr[0]]:
        try:
            send(conn, {"action" : "ping"})
            time.sleep(10)
            print(time.time()-pings[addr[0]])
            if(time.time()-pings[addr[0]]>40 or reloads[addr[0]]):
                logging.error(u'server is not avaliable, disconnect')
                onlines[addr[0]]=False
                go[addr[0]]=False
                sockclose(conn)
                while rec_threads[addr[0]].isAlive():
                    pass
                reloads.pop(addr[0])
                rec_threads.pop(addr[0])
                onlines.pop(addr[0])
        except socket.error as err:
            print("pinger socket error: %s" % str(err))
            logging.error("pinger socket error: "+str(err))
        except Exception as ex:
            print("ошибка пингера: %s" % str(ex))
            logging.error("pinger error: "+str(ex))
    go.pop(addr[0])

def parseconnector():
    global event
    global parse_thread
    while connect:
        try:
            while parse_thread.isAlive():
                pass
            logging.debug(u'restart parseconnector')
            event = True
            parse_thread=threading.Thread(target=eventparser, name="eventparser")
            parse_thread.daemon = True
            parse_thread.start()
        except socket.error as err:
            print("parseconnector socket error: %s" % str(err))
            logging.error("parseconnector socket error: "+str(err))
        except Exception as ex:
            print("ошибка парс коннектера: %s" % str(ex))
            logging.error("parseconnector error: "+str(ex))

#главная функция
if __name__ == '__main__':
    try:
        configure()
        sock = socket.socket()
        sock.bind(("", 7676))
        sock.listen(10)
        astercon=connectToAsterisk("asterisk", "asterisk")
        connect=True
        main_thread = threading.Thread(target=connector, args=(sock, connect), name="connector")
        main_thread.daemon = True
        main_thread.start()
        event = True
        parse_thread=threading.Thread(target=eventparser, name="eventparser")
        parse_thread.daemon = True
        parse_thread.start()
        pconn_thread = threading.Thread(target=parseconnector, name="parseconnector")
        pconn_thread.daemon = True
        pconn_thread.start()
        logging.debug(u'Start keyboard listening')
        cmd=input("AsteriskController:>>")
        while cmd != "stop":
            cmd = input("AsteriskController:>>")
    finally:
        connect = False
        event = False
        asterping = False
        print("Asterisk controller is going to shutdown now. You can check logs in " + logfile)
        while main_thread.isAlive():
            pass
        sock.close()
        logging.debug(u'socket closed')
