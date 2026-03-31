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
            "dev": "@RIYADBLRX,@SBR_HAMA",
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
        OLD_ACCESS_TOKEN = "ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a"
        OLD_OPEN_ID = "996a629dbcdb3964be6b6978f5d814db"
        
        # الخطوة 2: إنشاء JWT باستخدام MajorLogin
        # البيانات الأساسية المشفرة
        data = bytes.fromhex('1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3131342e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438382f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ca011073616d73756e6720534d2d473935354eea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933a80503b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134b2061e40001147550d0c074f530b4d5c584d57416657545a065f2a091d6a0d5033')
        
        # استبدال القيم القديمة بالجديدة
        data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
        data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
        
        # تشفير البيانات
        encrypted_payload = encrypt_data(data.hex())
        final_payload = bytes.fromhex(encrypted_payload)
        
        # إرسال طلب MajorLogin
        headers = {
            "Host": "loginbp.ggblueshark.com",
            "X-Unity-Version": "2018.4.11f1",
            "Accept": "*/*",
            "Authorization": "Bearer",
            "ReleaseVersion": "OB52",
            "X-GA": "v1 1",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(final_payload)),
            "User-Agent": "Free%20Fire/2019118692 CFNetwork/3826.500.111.2.2 Darwin/24.4.0",
            "Connection": "keep-alive"
        }
        
        url = "https://loginbp.ggblueshark.com/MajorLogin"
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
            "error": "فشل في الحصول على JWT",
            "status": "error"
        }
        return jsonify(add_signature(response_data)), 401
    
    enc_id = encode_id(friend_id)
    payload = f"08a7c4839f1e10{enc_id}1801"
    enc_data = encrypt_data(payload)
    
    try:
        response = requests.post(
            "https://clientbp.ggblueshark.com/RequestAddingFriend",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB52",
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

@app.route('/remove/<uid>/<password>/<friend_id>', methods=['GET'])
def remove_friend(uid, password, friend_id):
    """حذف صديق"""
    jwt_token = get_jwt_token(uid, password)
    if not jwt_token:
        response_data = {
            "error": "فشل في الحصول على JWT",
            "status": "error"
        }
        return jsonify(add_signature(response_data)), 401
    
    enc_id = encode_id(friend_id)
    payload = f"08a7c4839f1e10{enc_id}1802"
    enc_data = encrypt_data(payload)
    
    try:
        response = requests.post(
            "https://clientbp.ggblueshark.com/RemoveFriend",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB51",
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
                "message": "✅تم حذف اللاعب من قائمة الأصدقاء بنجاح",
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
                "message": "🛑فشل في حذف اللاعب",
                "details": {
                    "response_code": response.status_code,
                    "server_response": response.text
                }
            }
            return jsonify(add_signature(response_data))
            
    except Exception as e:
        response_data = {
            "status": "error",
            "message": "🛑حدث خطأ أثناء محاولة حذف الصديق",
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