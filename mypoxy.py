import socket as s
import sys
from datetime import datetime as time
import threading as t
class UDPMid:
    def __init__(self,p):
        self.so=s.socket(s.AF_INET,s.SOCK_DGRAM)
        self.so.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.so.bind(('0.0.0.0',p))
        self.client=dict()
        self.isrun=0
    def start(self):
        self.isrun=1
        t.Thread(target=self.listen).start()
    def listen(self):
        while self.isrun:
            try:
                data,addr=self.so.recvfrom(4096)
                if len(data)<6:
                    continue
                rsv,frag=data[:2]
                atyp=data[2]
                if atyp==0x01:
                    ip=s.inet_ntop(s.AF_INET,data[3:7])
                    port=int.from_bytes(data[7:9],'big')
                    payload=data[9:]
                elif atyp==0x03:
                    dlen=data[3]
                    domain=data[4:4+dlen].decode('ascii')
                    port=int.from_bytes(data[4+dlen:6+dlen],'big')
                    payload=data[6+dlen:]
                    ip=s.gethostbyname(domain)
                else: continue
                self.client[addr]=(ip,port)
                fsock=s.socket(s.AF_INET,s.SOCK_DGRAM)
                fsock.sendto(payload,(ip,port))
                t.Thread(target=self.share,args=(fsock,addr)).start()
            except Exception as e:
                print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                  '\033[31m[Error]\033[0m'+\
                 'UDP错误:'+str(e))
    def share(self,socka,sockb):
        try:
            data1,_=socka.recvfrom(4096)
            header=bytes([0,0,0,0x01])
            if sockb in self.client:
                target_ip, target_port = self.client[sockb]
                ip = s.inet_pton(s.AF_INET, target_ip)
                port = target_port.to_bytes(2, 'big')
            self.so.sendto(header+ip+port+data1,sockb)
        except: pass
        finally: socka.close()
def justdoit(conn,addr):#待实现配置
    global info,mid
    def handle5():
        med=conn.recv(1)[0]
        med=conn.recv(med)
        if 0x00 not in med:
            conn.sendall(bytes([0x05,0xFF]))
            print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                  '\033[31m[Error]\033[0m'+\
                  str(addr)+'无可用验证方法')
            return
        conn.sendall(bytes([0x05,0x00]))
        while 1:
            msg=conn.recv(4)
            if len(msg)<4 or msg[0]!=0x05: conn.close();return
            cmd=msg[1]
            if cmd==0x01:
                atype=msg[3]
                if atype==0x01:
                    info.conntype='ipv4'
                    host=conn.recv(4)
                    info.hostaddr=s.inet_ntop(s.AF_INET,host)
                    info.targ=s.socket(s.AF_INET,s.SOCK_STREAM)
                elif atype==0x03:
                    try:
                        info.conntype='demain'
                        addr_info = s.getaddrinfo(info.hostaddr, info.hostport, s.AF_UNSPEC, s.SOCK_STREAM)
                        family, _, _, _, sockaddr = addr_info[0]
                        info.hostaddr=sockaddr
                        info.targ=s.socket(family,s.SOCK_STREAM)
                    except s.gaierror:
                        conn.sendall(bytes([0x05, 0x04, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
                        print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                      '\033[31m[Error]\033[0m'+\
                      str(addr)+'不存在的域名')
                        return
                elif atype==0x04:
                    info.conntype='ipv6'
                    host=conn.recv(16)
                    info.hostaddr=s.inet_ntop(s.AF_INET6,host)
                    info.targ=s.socket(s.AF_INET6,s.SOCK_STREAM)
                else:
                    conn.sendall(bytes([0x05,0x08,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00]))
                    print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                      '\033[31m[Error]\033[0m'+\
                      str(addr)+'地址格式不合法')
                    return           
                info.hostport=int.from_bytes(conn.recv(2),'big')
                info.targ.connect((info.hostaddr,info.hostport))
                conn.sendall(bytes([0x05,0x00,0x00,0x01,0x00,0x00,0x00,0x00,(info.hostport>>8)&0xFF,info.hostport&0xFF]))
                def share(fromh,toh,se1,se2):
                    global packetID
                    try:
                        while not se1.is_set():
                            d=fromh.recv(4096)
                            if not se1.is_set():
                                toh.sendall(d)
                            if d:
                                mid=fromh.getsockname()
                                fip=(mid[0]+':'+str(mid[1])).encode('utf-8')
                                mid=toh.getsockname()
                                tip=(mid[0]+':'+str(mid[1])).encode('utf-8')
                                t=str(time.now().time().strftime("%H:%M:%S")).encode('utf-8')
                                f=open(f'cache/{packetID}.info','wb')
                                f.write(str(packetID).encode('utf-8'))
                                f.write(b'/'+t+b'/'+fip+b'/'+tip+b'\n'+d)
                                f.close()
                                packetID+=1
                    except Exception as e:
                        pass
                    finally:
                        try:
                            se2.set()
                            fromh.close()
                        except:
                            pass
                se1=t.Event()
                se2=t.Event()
                info.t1=t.Thread(target=share,args=(conn,info.targ,se1,se2))
                info.t2=t.Thread(target=share,args=(info.targ,conn,se2,se1))
                info.t1.start()
                info.t2.start()
                print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                    '\033[32m[Succeed]\033[0m'+\
                    str(addr)+f'已成功搭建与({info.hostaddr},{info.hostport})的TCP连接，开始转发数据')
            elif cmd==0x03:
                port=mid.so.getsockname()[1]
                r=bytes([0x05,0x00,0x00,0x01])+s.inet_pton(s.AF_INET,'0.0.0.0')+port.to_bytes(2,'big')
                conn.sendall(r)
                print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                    '\033[32m[Succeed]\033[0m'+\
                    f'成功处理了{addr}的UDP请求')
    try:
        neg=conn.recv(1)
        if neg[0]==0x05:
            handle5()
        else:
            return
    except Exception as e:
        print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+'\033[31m[Error]\033[0m'+str(e))
    finally:
        conn.close()
        print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+'\033[36m[Notice]\033[0m'+str(addr)+'断开连接')
def doHead(m, f, v):
    def doAll():
        import os
        r = []
        for filename in os.listdir('cache'):
            if filename.endswith('.info'):
                with open(os.path.join('cache', filename), 'rb') as file:
                    line = file.readline().decode('utf-8', errors='replace').strip()
                    r.append(line)
        return '\n'.join(r)

    def doGET(packet_id):
        try:
            with open(f'cache/{packet_id}.info', 'rb') as file:
                header_line = file.readline().decode('utf-8', errors='replace').strip()
                payload = file.read().decode('utf-8', errors='replace')
            return f'''
            <html>
                <head><title>流量详情 - {packet_id}</title></head>
                <body>
                    <h2>流量详情 (ID: {packet_id})</h2>
                    <p>头部信息: {header_line}</p>
                    <hr>
                    <pre><xmp>{payload}</xmp></pre>
                </body>
            </html>
            '''
        except FileNotFoundError:
            return '<html><body>数据包不存在</body></html>'
        except Exception as e:
            return f'<html><body>读取错误: {str(e)}</body></html>'

    file = None
    status = ' 200 OK'
    try:
        if m == 'GET':
            if f == 'all':
                content = doAll()
                file = content.encode('utf-8')
            elif f.startswith('getpacket.'):
                packet_id = f.split('.')[1]
                html_content = doGET(packet_id)
                file = html_content.encode('utf-8')
            else:
                with open(f'webui/{f}', 'rb') as static_file:
                    file = static_file.read()
        else:
            status = ' 405 Method Not Allowed'
            file = b'<html><body>Method not allowed</body></html>'
    except FileNotFoundError:
        status = ' 404 Not Found'
        file = b'<html><body>File not found</body></html>'
    except Exception as e:
        status = ' 500 Internal Server Error'
        file = f'<html><body>Server error: {str(e)}</body></html>'.encode('utf-8')

    return [v + status, file]
def httphandle(conn):
    msg = conn.recv(4096).decode('UTF-8')
    if len(msg) != 0:
        head = msg.split('\n')[0]
        head = head.split(' ')
        m = head[0]
        f = head[1][1:]
        v = head[2]
        r = doHead(m, f, v)
        rh = r[0]
        rf = r[1]
        if f.endswith(('.html', '.htm')):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'text/html;charset=UTF-8\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.css'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'text/css;charset=UTF-8\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.js'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'text/scrip;charset=UTF-8\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith(('.jpg', '.jpeg')):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'image/jpeg\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.png'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'image/png\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.gif'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'image/gif;charset=UTF-8\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.svg'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'image/svg+xml\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.ico'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'image/x-icon\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.mp3'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'audio/mpeg\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.wav'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'audio/wav\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.aac'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'audio/aac\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.flac'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'audio/flac\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.mp4'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'video/mp4\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.avi'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'video/x-msvideo\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.mov'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'video/quicktime\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        elif f.endswith('.mkv'):
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'video/x-matroska\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        else:
            msg = (rh + '\r\nDate:' + str(time.now().strftime('%a,%d %m %Y %H:%M:%S')) + ' GMT\r\n' + \
                   'Content-Type:' + 'application/octet-stream\r\n' + 'x-content-type-options: nosniff\r\n' + \
                   'Content-Length:' + str(len(rf)) + '\n\n').encode('utf-8') + rf
        conn.sendall(msg)
        conn.close();
def webmain(so):
    while 1:
        conn,addr=so.accept()
        #print('\033[36m' + '[' + str(time.now().time().strftime("%H:%M:%S")) + ']' + \
         #     '\033[36m[Notice]\033[0m' + \
          #    '网页GUI连接'+str(addr))
        t.Thread(target=httphandle,args=(conn,)).start()
if __name__=='__main__':
    packetID=0
    import os
    for i in os.listdir('cache\\'):
        os.remove(f'cache\\{i}')
    info=t.local()
    port=9527
    webport=8080
    argv=sys.argv;argv.pop(0)
    nowarg=''
    args={'-nostarts':[]}
    for i in argv:
        if i.startswith('--'):
            i=i[2:]
            nowarg=i
        elif i.startswith('-'):
            i=i[1:]
            nowarg=i
        else:
            if nowarg:
                args[nowarg]=i
            else:
                args['-nostarts'].append(i)
    if args.get('port','') != '':
        port=int(args.get('port',''))
    if args.get('web-port','')!='':
        webport=int(args.get('web-port',''))
    so=s.socket()
    webs=s.socket()
    so.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    webs.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    so.bind(('0.0.0.0',port))
    webs.bind(('0.0.0.0',webport))
    webs.listen(5)
    so.listen(5)
    mid=UDPMid(port+1)
    print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                      '\033[36m[Notice]\033[0m'+\
                      '代理已开始运行，监听'+str(port))
    t.Thread(target=webmain,args=(webs,)).start()
    mid.start()
    print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                      '\033[36m[Notice]\033[0m'+\
                      '网页GUI已开始运行，请访问http://127.0.0.1:'+str(webport)+'/index.html')
    while 1:
        conn,addr=so.accept()
        print('\033[36m'+'['+str(time.now().time().strftime("%H:%M:%S"))+']'+\
                      '\033[36m[Notice]\033[0m'+\
                      '新连接:'+str(addr))
        t.Thread(target=justdoit,args=(conn,addr)).start()
