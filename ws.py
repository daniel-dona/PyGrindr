import websocket
import threading
import _thread
import uuid
import time
import qrcode
import requests
import base64
import jwt
from xml.dom import minidom
import json
import argparse
import signal

class Auth:

    def __init__(self):
        self.timeout_scan = 30
        self.status = 0
        self.clientId = ""
        self.token = ""
        
    def web_client_start(self):
        endpoint = '''https://grindr.mobi/v4/web-clients'''
        params = {}
        headers = {'User-Agent': 'Firefox 69'}
        r = requests.post(url = endpoint, params = params, headers = headers)
        raw = r.json()
        
        qrdata = "grindrwebchat_"+str(raw["webClientId"])
        
        self.clientId = str(raw["webClientId"])
        
        #print("Request: "+qrdata)
        
        q = qrcode.QRCode()
        q.add_data(qrdata)
        q.make()
        q.print_ascii()
        
        print("Escanea este QR desde Grindr", end="", flush=True)
        
        self.status = 1
        
    def token_decode(self, token):
        token_data = jwt.decode(token,verify=False, algorithms=['HS256'])
        self.profileId = token_data["profileId"]
        self.exp = token_data["exp"]
        
        #Hay otros campos pero no les veo la utilidad, ej:
        # {'features': ['DiscreetIcon', 'PINLock', 'VideoCallDailyFree', 'CreateVideoCall', 'WebChat'], 'profileId': '2******3', 'roles': [], 'exp': 1583344096}
        
    def wait_scanned(self):
        endpoint = '''https://grindr.mobi/v4/authtokens/web/'''+self.clientId
        for i in range(self.timeout_scan):
            r = requests.get(url = endpoint)
            time.sleep(1)
            if r.status_code == 200:
                print('OK!')
                self.token = r.json()["authtoken"]
                self.status = 3
                self.token_decode(self.token)
                return True
            elif r.status_code == 404:
                print('.', end="", flush=True)
                self.status = 2
        self.status = 4
        return False

'''class ChatSync:
    
    
    wss://chatsync.grindr.com/session/websocket?profile_id=[profileId]&token=[token]&type=web
    
class Grid:
    
    # To be decoded 
    # https://grindr.mobi/v4/locations/ezjmg1f7y05n/profiles?myType=true&online=false&faceOnly=false&photoOnly=false&notRecentlyChatted=false&ageMaximum=37&weightMaximum=118000&heightMaximum=186&grindrTribesIds=5&bodyTypeIds=4&sexualPositionIds=4&ethnicityIds=4&lookingForIds=2&relationshipStatusIds=4,-1,3&meetAtIds=2,-1&nsfwIds=3'''
    
    
class XMPPClient:
    
    def __init__(self, auth):
        self.auth = auth
        self.reset()
        self.reconnect = True
        self.reconnect_count = 0
        
    def reset(self):
        self.ackn = 1
        self.status = 0

    def send_test_msg(self,text):
        to = "171176511"
        msgid = str(uuid.uuid4())
        data = {"sourceProfileId":self.auth["profileId"],"targetProfileId":to,"messageId":msgid,"sourceDisplayName":self.auth["profileId"],"type":"text","timestamp":int(time.time() *1000),"body":text}
        msg7 = '''<message from="'''+self.auth["profileId"]+'''@chat.grindr.com" id="'''+msgid+'''" to="'''+to+'''@chat.grindr.com" type="chat" xmlns="jabber:client"><body>'''+str(data)+'''</body></message>'''
        self.ws.send(msg7)
           
    def on_message(self, ws, message):
        
        x = minidom.parseString(message)
        
        print("\n\t"+message)
        
        if x.firstChild.tagName == 'message':
            
            
            if x.firstChild.firstChild.tagName == 'body':
                
                #print("\t"+message)
                
                try:
                    data = json.loads(x.firstChild.firstChild.firstChild.nodeValue)
                except:
                    data = x.firstChild.firstChild.firstChild.nodeValue 
                    
                #data2 = json.loads(data["body"])
                print("\t"+data)
                #print("\t"+data2)
                #print("> "+data["body"])
                
            elif x.firstChild.firstChild.tagName == 'sent' and x.firstChild.firstChild.firstChild.tagName == 'forwarded':
                
                #print("\t"+message)
                
                '''try:
                    data = json.loads(x.firstChild.firstChild.firstChild.firstChild.firstChild.firstChild.nodeValue)
                except:
                    data = x.firstChild.firstChild..firstChildfirstChild.firstChild.firstChild.nodeValue 
                    
                #data2 = json.loads(data["body"])
                print("\t [Desde móvil] "+data)
                #print("\t"+data2)
                #print("> "+data["body"])'''
                
            elif x.firstChild.firstChild.tagName == 'active':
                
                print("\rActivo.......", end="")
                
            elif x.firstChild.firstChild.tagName == 'translate': #Esto es raro
                
                print("\rChat abierto..", end="")
                
            elif x.firstChild.firstChild.tagName == 'composing':
                
                print("\rEscribiendo...", end="")
                
            elif x.firstChild.firstChild.tagName == 'paused':
                
                print("\rPausado.......", end="")
                
            elif x.firstChild.firstChild.tagName == 'displayed':
                
                print("\rVisto.........", end="")
                
            else:
            
                print("?")
            
        elif x.firstChild.tagName == 'r':
            # ACK de stanzas
            ackmsg = '''<a h="'''+str(self.ackn)+'''" xmlns="urn:xmpp:sm:3"/>'''
            self.ws.send(ackmsg)
            self.ackn += 1
        
        elif x.firstChild.tagName == 'failure':
            self.ws.close()
            self.on_close(ws)
            self.reconnect = False
            
        elif x.firstChild.tagName == 'close':
            self.ws.close()
            #self.start()
            
        else:
            
            print("?")
            
            #print("\t"+message)
       
        

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("Reconectando!!!")
        if self.reconnect and self.reconnect_count < 3:
            self.reconnect_count += 1
            self.reset()
            self.start()

    def on_open(self, ws):
        def run(self):
            
            #print(self.auth)
            #quit()
 
            auth_str_data = self.auth["profileId"]+'''@chat.grindr.com'''+'\0'+self.auth["profileId"]+'\0'+ self.auth["token"]
            auth_str = str(base64.b64encode(auth_str_data.encode("UTF-8")), "UTF-8")

            # Este montón de mierda se podría poner más bonito
            
            msg1 = '''<open to="chat.grindr.com" version="1.0" xmlns="urn:ietf:params:xml:ns:xmpp-framing"/>'''
            msg2 = '''<auth mechanism="PLAIN" xmlns="urn:ietf:params:xml:ns:xmpp-sasl">'''+auth_str+'''</auth>'''
            msg3 = '''<open to="chat.grindr.com" version="1.0" xmlns="urn:ietf:params:xml:ns:xmpp-framing"/>'''
            msg4 = '''<iq id="_bind_auth_2" type="set" xmlns="jabber:client"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><resource>'''+self.auth["clientId"]+'''_web</resource></bind></iq>'''
            msg5 = '''<iq id="_session_auth_2" type="set" xmlns="jabber:client"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>'''
            msg6 = '''<iq from="'''+self.auth["profileId"]+'''@chat.grindr.com/'''+self.auth["clientId"]+'''_web" id="'''+str(uuid.uuid4())+''':carbons" type="set" xmlns="jabber:client"><enable xmlns="urn:xmpp:carbons:2"/></iq>'''
            msg8 = '''<enable resume="false" xmlns="urn:xmpp:sm:3"/>'''
            msg9 = '''<presence xmlns="jabber:client"/>'''
            msg10 = '''<r xmlns="urn:xmpp:sm:3"/>'''
            msg11 = '''<message from="277365733@chat.grindr.com" id="'''+str(uuid.uuid4())+'''" to="250015945@chat.grindr.com" type="chat" xmlns="jabber:client"><body>{&quot;sourceProfileId&quot;:&quot;277365733&quot;,&quot;targetProfileId&quot;:&quot;250015945&quot;,&quot;messageId&quot;:&quot;'''+str(uuid.uuid4())+'''&quot;,&quot;sourceDisplayName&quot;:&quot;277365733&quot;,&quot;type&quot;:&quot;image&quot;,&quot;timestamp&quot;:1583677134256,&quot;body&quot;:&quot;{\&quot;imageHash\&quot;:\&quot;taps/looking.png\&quot;,\&quot;imageType\&quot;:2,\&quot;tapType\&quot;:2}&quot;}</body></message>'''

            self.ws.send(msg1)
            self.ws.send(msg2)
            self.ws.send(msg3)
            self.ws.send(msg4)
            self.ws.send(msg5)
            self.ws.send(msg6)
            self.ws.send(msg8)
            self.ws.send(msg9)
            self.ws.send(msg10)
            #self.ws.send(msg11)
        
        #threading.Thread(target=run,args=(self)).start()
        _thread.start_new_thread(run,((self,)))
        
    def start(self):
        
        print("Starting XMPP connection...")
        
        
        ws_endpoint = "wss://chat.grindr.com:2443/ws-xmpp"
        
        self.ws = websocket.WebSocketApp(ws_endpoint,
                                  on_message = lambda ws,message: self.on_message(ws, message),
                                  on_error = lambda ws,error: self.on_error(ws,error),
                                  on_close = lambda ws: self.on_close(ws), 
                                  on_open = lambda ws: self.on_open(ws))
        #websocket.enableTrace(True)
        #self.ws.run_forever()

        wst = threading.Thread(target=self.ws.run_forever, kwargs={'ping_interval': 15, 'ping_timeout' : 5})
        wst.daemon = True
        wst.start()
        wst.join()
        
    def finish(self):
        self.reconnect = False
        self.ws.close()


parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--login', action="store_true")

args = parser.parse_args()


def receiveSignal(signalNumber, frame):
    print('Received:', signalNumber)
    return
    
def exit_ok(s,f):
    xmpp.finish()
    quit()
    
def register_signals():
    # register the signals to be caught
    signal.signal(signal.SIGHUP, receiveSignal)
    signal.signal(signal.SIGINT, exit_ok)
    signal.signal(signal.SIGQUIT, receiveSignal)
    signal.signal(signal.SIGILL, receiveSignal)
    signal.signal(signal.SIGTRAP, receiveSignal)
    signal.signal(signal.SIGABRT, receiveSignal)
    signal.signal(signal.SIGBUS, receiveSignal)
    signal.signal(signal.SIGFPE, receiveSignal)
    #signal.signal(signal.SIGKILL, receiveSignal)
    signal.signal(signal.SIGUSR1, receiveSignal)
    signal.signal(signal.SIGSEGV, receiveSignal)
    signal.signal(signal.SIGUSR2, receiveSignal)
    signal.signal(signal.SIGPIPE, receiveSignal)
    signal.signal(signal.SIGALRM, receiveSignal)
    signal.signal(signal.SIGTERM, receiveSignal)

register_signals()

if args.login:
    auth = Auth()
    auth.web_client_start()

    if(auth.wait_scanned()):
        token = auth.token
        clientId = auth.clientId
    else:
        print("Ooops!")
        quit()

    auth_tmp = {"token": auth.token, "profileId": auth.profileId, "clientId": auth.clientId}
else: 
    auth_tmp = {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmZWF0dXJlcyI6WyJEaXNjcmVldEljb24iLCJQSU5Mb2NrIiwiVmlkZW9DYWxsRGFpbHlGcmVlIiwiQ3JlYXRlVmlkZW9DYWxsIiwiV2ViQ2hhdCJdLCJwcm9maWxlSWQiOiIyNzczNjU3MzMiLCJyb2xlcyI6W10sImV4cCI6MTU4MzY4NTc2Nn0.tqgEcJI8vGkmba2F18nA5cmQWr4WW1foCTSiBR0oSOw', 'profileId': '277365733', 'clientId': 'ggqSJGRctALkAhDlAYqtXcGkbBEAsfpHeikKCrSbfxNVklKDOIpYldhDiBCbpIOX'}


print(auth_tmp)



xmpp = XMPPClient(auth_tmp)
xmpp.start()








