from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# مفاتيح التشفير
KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def add_signature(response_data):
    """إضافة التوقيع إلى الاستجابة"""
    if isinstance(response_data, dict):
        response_data["signature"] = {
            "dev": "@SBR_HAMA",
            "team": "SBR"
        }
    return response_data

def encrypt_data(plain_text):
    """تشفير البيانات باستخدام AES-CBC"""
    if isinstance(plain_text, str):
        plain_text = bytes.fromhex(plain_text)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def encode_id(number):
    """تشفير ID اللاعب"""
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def get_jwt_token(uid, password):
    """الحصول على JWT مباشرة بدون API خارجي"""
    try:
        # الخطوة 1: الحصول على التوكن من Garena
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": "",
            "client_id": "100067",
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code != 200:
            print(f"Garena API failed with status: {response.status_code}")
            return None
            
        garena_data = response.json()
        
        if "access_token" not in garena_data or "open_id" not in garena_data:
            print(f"Missing keys in Garena response: {garena_data}")
            return None
            
        NEW_ACCESS_TOKEN = garena_data['access_token']
        NEW_OPEN_ID = garena_data['open_id']
        
        # القيم القديمة الثابتة
        OLD_ACCESS_TOKEN = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
        OLD_OPEN_ID = "4306245793de86da425a52caadf21eed"
        
        # الخطوة 2: إنشاء JWT باستخدام MajorLogin
        # البيانات الأساسية المشفرة
        data = bytes.fromhex('1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132332e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366')
        
        # استبدال القيم القديمة بالجديدة
        data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
        data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
        
        # تشفير البيانات
        encrypted_payload = encrypt_data(data.hex())
        final_payload = bytes.fromhex(encrypted_payload)
        
        # إرسال طلب MajorLogin
        headers = {
            "Host": "loginbp.ggpolarbear.com",
            "X-Unity-Version": "2018.4.11f1",
            "Accept": "*/*",
            "Authorization": "Bearer",
            "ReleaseVersion": "OB53",
            "X-GA": "v1 1",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(final_payload)),
            "User-Agent": "Free%20Fire/2019118692 CFNetwork/3826.500.111.2.2 Darwin/24.4.0",
            "Connection": "keep-alive"
        }
        
        url = "https://loginbp.ggpolarbear.com/MajorLogin"
        response = requests.post(url, headers=headers, data=final_payload, verify=False, timeout=10)
        
        if response.status_code == 200 and len(response.text) >= 10:
            # استخراج JWT من الاستجابة
            response_text = response.text
            start_marker = "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"
            
            if start_marker in response_text:
                base64_token = response_text[response_text.find(start_marker):]
                second_dot_index = base64_token.find(".", base64_token.find(".") + 1)
                if second_dot_index != -1:
                    jwt_token = base64_token[:second_dot_index + 44]
                    return jwt_token
        
        print(f"MajorLogin failed with status: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error getting JWT: {str(e)}")
        return None

@app.route('/add/<uid>/<password>/<friend_id>', methods=['GET'])
def add_friend(uid, password, friend_id):
    """إضافة صديق"""
    jwt_token = get_jwt_token(uid, password)
    if not jwt_token:
        response_data = {
            "error": "فشل في الحصول على ",
            "status": "error"
        }
        return jsonify(add_signature(response_data)), 401
    
    enc_id = encode_id(friend_id)
    payload = f"08a7c4839f1e10{enc_id}1801"
    enc_data = encrypt_data(payload)
    
    try:
        response = requests.post(
            "https://loginbp.ggpolarbear.com/RequestAddingFrien",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB53",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            },
            data=bytes.fromhex(enc_data),
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = {
                "status": "success",
                "message": "✅تم إرسال طلب الصداقة بنجاح",
                "details": {
                    "friend_id": friend_id,
                    "response_code": response.status_code,
                    "server_response": response.text
                }
            }
            return jsonify(add_signature(response_data))
        else:
            response_data = {
                "status": "error",
                "message": "فشل إرسال الطلب❌",
                "details": {
                    "response_code": response.status_code,
                    "server_response": response.text
                }
            }
            return jsonify(add_signature(response_data))
            
    except Exception as e:
        response_data = {
            "status": "error",
            "message": "🛑حدث خطأ أثناء محاولة إرسال طلب الصداقة",
            "error_details": str(e)
        }
        return jsonify(add_signature(response_data)), 500

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    response_data = {
        "status": "نشط",
        "features": {
        },
        "endpoints": {
            "add_friend": "/add/<uid>/<password>/<friend_id> - إضافة صديق",
            "remove_friend": "/remove/<uid>/<password>/<friend_id> - حذف صديق"
        }
    }
    return jsonify(add_signature(response_data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9479, debug=True)
    
