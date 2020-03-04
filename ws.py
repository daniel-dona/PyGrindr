import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import uuid
import time
import qrcode
import requests
import base64
import jwt

class Auth:

    def __init__(self):
        self.status = 0
        self.clientId = ""
        self.token = ""
        
    def web_client_start(self):

        endpoint = '''https://grindr.mobi/v4/web-clients'''
        params = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) PyGrindr 1'}
        r = requests.post(url = endpoint, params = params)
        raw = r.json()
        
        qrdata = "grindrwebchat_"+str(raw["webClientId"])
        
        self.clientId = str(raw["webClientId"])
        
        #print("Request: "+qrdata)
        
        q = qrcode.QRCode()
        q.add_data(qrdata)
        q.make()
        q.print_ascii()
        
        print("Escanea este QR desde Grindr", end="", flush=True)
        
    def wait_scanned(self):

        endpoint = '''https://grindr.mobi/v4/authtokens/web/'''+self.clientId
        for i in range(30):
            r = requests.get(url = endpoint)
            time.sleep(1)
            if r.status_code == 200:
                print('OK!')
                #print(r.json()["authtoken"])
                self.token = r.json()["authtoken"]
                return True
            elif r.status_code == 404:
                print('.', end="", flush=True)
        return False

'''class ChatSync:
    
    
    wss://chatsync.grindr.com/session/websocket?profile_id=250015945&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmZWF0dXJlcyI6WyJEaXNjcmVldEljb24iLCJQSU5Mb2NrIiwiVmlkZW9DYWxsRGFpbHlGcmVlIiwiQ3JlYXRlVmlkZW9DYWxsIiwiV2ViQ2hhdCJdLCJwcm9maWxlSWQiOiIyNTAwMTU5NDUiLCJyb2xlcyI6W10sImV4cCI6MTU4MzMzODE1MH0.7NqtdkeKgYe41wGS2IGdB3ls6f9tUrkddZrNATVLrL8&type=web'''
    
    
    
                    
                
auth = Auth()
auth.web_client_start()

if(auth.wait_scanned()):
    token = auth.token
    clientId = auth.clientId
else:
    print("Ooops!")
    quit()
    
tokeninfo = jwt.decode(token,verify=False, algorithms=['HS256'])

#userId = "250015945"

userId = tokeninfo["profileId"]

auth_str_data = userId+'''@chat.grindr.com'''+'\0'+userId+'\0'+ token
auth_str = str(base64.b64encode(auth_str_data.encode("UTF-8")), "UTF-8")


msg1 = '''<open to="chat.grindr.com" version="1.0" xmlns="urn:ietf:params:xml:ns:xmpp-framing"/>'''
msg2 = '''<auth mechanism="PLAIN" xmlns="urn:ietf:params:xml:ns:xmpp-sasl">'''+auth_str+'''</auth>'''
msg3 = '''<open to="chat.grindr.com" version="1.0" xmlns="urn:ietf:params:xml:ns:xmpp-framing"/>'''
msg4 = '''<iq id="_bind_auth_2" type="set" xmlns="jabber:client"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><resource>'''+clientId+'''_web</resource></bind></iq>'''
msg5 = '''<iq id="_session_auth_2" type="set" xmlns="jabber:client"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>'''
msg6 = '''<iq from="'''+userId+'''@chat.grindr.com/'''+clientId+'''_web" id="9a74bd55-553a-4468-81af-97a181510055:carbons" type="set" xmlns="jabber:client"><enable xmlns="urn:xmpp:carbons:2"/></iq>'''
msg8 = '''<enable resume="false" xmlns="urn:xmpp:sm:3"/>'''
msg9 = '''<presence xmlns="jabber:client"/>'''
msg10 = '''<r xmlns="urn:xmpp:sm:3"/>'''


ackn = 1
started = 0

def on_message(ws, message):
    print(message)
    
    '''if True:
    
        ackmsg = '''<a h="'''+str(ackn)+'''" xmlns="urn:xmpp:sm:3"/>'''
        ws.send(ackmsg)
        ackn += 1'''

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        
        def send_test_msg(ws,text):
            to = "171176511"
            msgid = str(uuid.uuid4())
            data = {"sourceProfileId":userId,"targetProfileId":to,"messageId":msgid,"sourceDisplayName":userId,"type":"text","timestamp":int(time.time() *1000),"body":text}
            #print(data)
            msg7 = '''<message from="'''+userId+'''@chat.grindr.com" id="'''+msgid+'''" to="'''+to+'''@chat.grindr.com" type="chat" xmlns="jabber:client"><body>'''+str(data)+'''</body></message>'''
            ws.send(msg7)

        ws.send(msg1)
        ws.send(msg2)
        ws.send(msg3)
        ws.send(msg4)
        ws.send(msg5)
        ws.send(msg6)
        ws.send(msg8)
        ws.send(msg9)
        ws.send(msg10)
        
        time.sleep(1)
        
        
        
        '''for i in range(3):
            send_test_msg(ws, "Hola "+str(i))
            time.sleep(4)'''
            
    thread.start_new_thread(run,())
    




#   websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://chat.grindr.com:2443/ws-xmpp",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
ws.on_open = on_open

ws.run_forever()


