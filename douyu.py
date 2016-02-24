# -*- coding:utf-8 -*-
import socket
import sys
import time
import uuid
import hashlib
import requests
import re
import sys
import threading
import copy
import struct

reload(sys)
sys.setdefaultencoding('gb18030')

global users
global passes
global realname


realname=['1234再来一次1234','橙汁美味','不吃素菜','我准备好了饿','英雄联盟王者无敌','惜城呦','江左梅郎通过弹幕','换取信任','怎么回事ibuq','请你安静点ye']
users=['auto_F3Z8pi0b1G','auto_J7fRnnfxm7','auto_GmQ77715Np','auto_I6HIDW3ER4','auto_QiJGklM5ZB','auto_3pSaH7yJhu',\
'auto_07DRrfFEBG','auto_ilJp9a8nZk','auto_1qrXY7YfC5','auto_HsKQGNCURr']
passes=['200820e3227815ed1756a6b531e7e0d2','200820e3227815ed1756a6b531e7e0d2',\
'd0dcbf0d12a6b1e7fbfa2ce5848f3eff','200820e3227815ed1756a6b531e7e0d2','200820e3227815ed1756a6b531e7e0d2','d0dcbf0d12a6b1e7fbfa2ce5848f3eff',\
'd0dcbf0d12a6b1e7fbfa2ce5848f3eff','200820e3227815ed1756a6b531e7e0d2','200820e3227815ed1756a6b531e7e0d2','200820e3227815ed1756a6b531e7e0d2']

def staticGet(idolid):
    hea = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64)\
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    url='http://www.douyutv.com/'+idolid
    print('connect url:',url)
    html = requests.get(url,headers = hea).text
    roomid = "".join(re.findall('task_roomid" value="(\d+)',html))
    titleStr = "".join(re.findall('"server_config":"%5B%7B(.*?)%7D%5D","def_disp_gg":0};',html))
    titleStr = re.sub('%22','',titleStr)
    listTitle = titleStr.split('%7D%2C%7B')
    logServer=dict()
    logServer['port']=[]
    logServer['ip']=[]
    for i in range(len(listTitle)):  
        logServer['port'].append(re.findall('%2Cport%3A(\d+)',listTitle[i])[0])
        logServer['ip'].append(re.findall('ip%3A(.*?)%2C',listTitle[i])[0])
        logServer['rid']=roomid
    #print('Logserver,port:',logServer['port'],'ip:',logServer['ip'],'rid:',logServer['rid'])
    return logServer


def danmuServerGet(sockStr):
    contextList=sockStr.split(b'\x00"')[0].split(b'\xb2\x02')
    danmuServer=dict()
    for cl in contextList:
        cl=cl.decode('utf-8','.ignore')
        if re.search('msgrepeaterlist',cl):
            danmuServer['add']=re.findall('Sip@AA=(.*?)@',cl)
            danmuServer['port']=re.findall('Sport@AA=(\d+)',cl)
        elif re.search('setmsggroup',cl):
            danmuServer['gid']=re.findall('gid@=(\d+)/',cl)
            danmuServer['rid']=re.findall('rid@=(.*?)/',cl)
    #print('danmuServer adress:',danmuServer['add'][0],danmuServer['port'][0],'groupID:',danmuServer['gid'])
    return danmuServer

def sendmsg(sock,msgstr) :
    msg=msgstr
    data_length= len(msg)+8
    code=689
    #msgHead=int.to_bytes(data_length,4,'little')+int.to_bytes(data_length,4,'little')+int.to_bytes(code,4,'little')
    msgHead=struct.pack("<l",data_length)+struct.pack("<l",data_length)+struct.pack("<l",code)
    sock.send(msgHead)
    sent=0
    while sent<len(msg):
        tn= sock.send(msg[sent:])
        sent= sent + tn


def dynamicGet(logServer):
    sock=[]
    sucnum=0
    for num in range(len(users)):
        lognum=num % len(logServer['ip'])
        sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        sock[num].connect((logServer['ip'][lognum], int(logServer['port'][lognum])))
        devid=uuid.uuid1().hex.swapcase()
        rt=str(int(time.time()))
        hashvk = hashlib.md5()
        vk=rt+'7oE9nPEG9xXV69phU31FYCLUagKeYtsF'+devid
        hashvk.update(vk.encode('utf-8'))
        vk = hashvk.hexdigest()
        username = users[num]
        password = passes[num]
        rid=logServer.get('rid')
        gid=''
        msg='type@=loginreq'\
        +'/username@='+username\
        +'/ct@=0'\
        +'/password@='+password\
        +'/roomid@='+rid\
        +'/devid@='+devid\
        +'/rt@='+rt\
        +'/vk@='+vk\
        +'/ver@=20150929'\
        +'/\x00'
        print(msg)
        sendmsg(sock[num],msg)
        context=sock[num].recv(1024)
        #print(context)

        context=context.split(b'\xb2\x02')[1].decode('utf-8')
        typeID1st=re.findall('type@=(.*?)/',context)[0]
        if typeID1st != 'error' :
            uid=re.findall('userid@=(\d+)',context)[0]
            sucnum=sucnum+1
            #print ("=======================success==============",sucnum)
            #sendmsg(sock,msg)
            context=sock[num].recv(1024)
            #print(context)
            danmuServer=danmuServerGet(context)
            print (realname[num].decode('utf-8').encode('gb18030'))
            print('group ID get:',danmuServer['gid'],"userid:",uid)
        
            msg='type@=qtlnq'\
            +'/\x00'
            sendmsg(sock[num],msg)

            msg='type@=qrl'\
            +'/rid@='+rid\
            +'/\x00'
            sendmsg(sock[num],msg)

            msg='type@=reqog'\
            +'/uid@='+uid\
            +'/\x00'
            sendmsg(sock[num],msg)

        else:
            danmuServer=dict()
        #sock.close()
        #returnDict={'isError':typeID1st,'typeID':typeID2st,'gid':gid,,}
    
    cput=''
    while cput!='$':
        cput=raw_input("please input content($-exit):")
        if cput!='$':
            cput=cput.decode('gb18030').encode('utf-8')
            conmsg='type@=chatmessage'\
            +'/receiver@=0'\
            +'/content@='+cput\
            +'/scope@=/'\
            +'col@=0/'\
            +'\x00'

            for i in range(len(users)):
                sendmsg(sock[i],conmsg)

    for i in range(len(users)):
        sock[i].close()
    
    return danmuServer

def keeplive(sock):
    global whileCodition
    print('===init keeplive===')
    while whileCodition:
        print('40sleep')
        msg='type@=keeplive/tick@='+str(int(time.time()))+'/\x00'
        sendmsg(sock,msg)
        #keeplive=sock.recv(1024)
        time.sleep(20)
    sock.close()


def main(idolid):
    logServer=staticGet(idolid)
    danmuServer=dynamicGet(logServer)



if __name__=='__main__':
    idolid= sys.argv[1] if len(sys.argv)>1 else 'saro'
    main(idolid)
