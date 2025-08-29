from flask import Flask
from flask_socketio import SocketIO, emit
import os
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Professional fallback responses for immediate use
fallback_responses = {
    'en': {
        'low': [
            "I understand you're going through a difficult time. How can I support you today?",
            "Thank you for reaching out. What's been on your mind lately?",
            "I'm here to listen. Can you tell me more about what you're experiencing?",
            "It's completely normal to have these feelings. What would be most helpful right now?"
        ],
        'moderate': [
            "I can see you're dealing with some challenging emotions. Have you been able to talk to anyone about this?",
            "These feelings sound overwhelming. Would you like to discuss some coping strategies?",
            "You're being brave by reaching out. Have you considered speaking with a counselor?",
            "It sounds like you're carrying a heavy burden. How long have you been feeling this way?"
        ],
        'high': [
            "I'm very concerned about what you're sharing. Please consider reaching out to a crisis helpline: National Suicide Prevention Lifeline 988.",
            "These thoughts are serious and you don't have to go through this alone. Please contact emergency services or call 988.",
            "I'm worried about your safety. Please reach out for immediate help: call 988 or go to your nearest emergency room.",
            "Your life has value. Please don't wait - contact the National Suicide Prevention Lifeline at 988 immediately."
        ]
    },
    'hi': {
        'low': [
            "मैं समझ सकता हूँ कि आप कठिन समय से गुजर रहे हैं। आज मैं आपकी कैसे मदद कर सकता हूँ?",
            "मेरे पास आने के लिए धन्यवाद। हाल ही में आपके मन में क्या चल रहा है?",
            "मैं यहाँ सुनने के लिए हूँ। क्या आप बता सकते हैं कि आप क्या अनुभव कर रहे हैं?",
            "इस तरह की भावनाएं होना सामान्य है। अभी सबसे मददगार क्या होगा?"
        ],
        'moderate': [
            "मैं देख सकता हूँ कि आप चुनौतीपूर्ण भावनाओं से निपट रहे हैं। क्या आप किसी से इसके बारे में बात कर पाए हैं?",
            "ये भावनाएं बहुत भारी लगती हैं। क्या आप कुछ मुकाबला रणनीतियों पर चर्चा करना चाहेंगे?",
            "मदद मांगकर आप साहस दिखा रहे हैं। क्या आपने किसी परामर्शदाता से बात करने पर विचार किया है?",
            "लगता है आप पर भारी बोझ है। आप कब से ऐसा महसूस कर रहे हैं?"
        ],
        'high': [
            "आपने जो साझा किया है उससे मैं बहुत चिंतित हूँ। कृपया संकट हेल्पलाइन से संपर्क करने पर विचार करें: 112।",
            "ये विचार गंभीर हैं और आपको अकेले इससे नहीं गुजरना होगा। कृपया आपातकालीन सेवाओं से संपर्क करें या 112 पर कॉल करें।",
            "मुझे आपकी सुरक्षा की चिंता है। कृपया तुरंत मदद लें: 112 पर कॉल करें या अपने निकटतम आपातकालीन कक्ष में जाएं।",
            "आपका जीवन मूल्यवान है। कृपया प्रतीक्षा न करें - तुरंत राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन 112 से संपर्क करें।"
        ]
    }
}

def assess_crisis_level(text):
    """Simple crisis assessment"""
    text_lower = text.lower()
    
    high_risk = ['kill myself', 'suicide', 'want to die', 'hurt myself', 'end my life', 
                'मरना चाहता', 'आत्महत्या', 'जिंदगी खत्म']
    moderate_risk = ['hopeless', 'worthless', 'alone', 'depressed', 'overwhelming',
                    'निराशा', 'बेकार', 'अकेला', 'हार गया']
    
    for phrase in high_risk:
        if phrase in text_lower:
            return 'high'
    
    for phrase in moderate_risk:
        if phrase in text_lower:
            return 'moderate'
    
    return 'low'

def get_response(message, language):
    """Get appropriate response based on message and language"""
    crisis_level = assess_crisis_level(message)
    is_crisis = crisis_level in ['moderate', 'high']
    
    responses = fallback_responses.get(language, fallback_responses['en'])
    response_list = responses.get(crisis_level, responses['low'])
    response = random.choice(response_list)
    
    return {'message': response, 'is_crisis': is_crisis, 'language': language}

@app.route('/')
def index():
    return {"status": "Mental Health Chatbot Server - FIXED VERSION", "language_support": True}

@socketio.on('connect')
def on_connect():
    print("🔌 Client connected")
    welcome_msg = "Hello! I'm your AI mental health assistant. How can I help you today?"
    emit('ai response', {'message': welcome_msg, 'is_crisis': False, 'language': 'en'})

@socketio.on('chat message')
def on_message(data):
    """🔥 MAIN FIX: Handle language parameter from frontend"""
    user_message = data.get('message', '').strip()
    user_language = data.get('language', 'en')  # 🔥 KEY FIX: Get language from website!
    
    print(f"📨 Message: '{user_message[:40]}...' Language: {user_language}")
    
    if not user_message:
        empty_responses = {
            'en': "Please enter a message to get started.",
            'hi': "कृपया शुरू करने के लिए एक संदेश दर्ज करें।"
        }
        emit('ai response', {
            'message': empty_responses.get(user_language, empty_responses['en']),
            'is_crisis': False,
            'language': user_language
        })
        return
    
    # Generate response in target language
    result = get_response(user_message, user_language)
    
    print(f"🤖 Response: '{result['message'][:40]}...' Crisis: {result['is_crisis']}")
    
    emit('ai response', {
        'message': result['message'],
        'is_crisis': result['is_crisis'],
        'language': user_language
    })

@socketio.on('disconnect')
def on_disconnect():
    print("🔌 Client disconnected")

if __name__ == '__main__':
    print("🚀 Starting FIXED Mental Health Chatbot Server...")
    print("🌐 Server URL: http://localhost:3000")
    print("✅ Now properly handles language parameter from frontend!")
    print("✅ No more mixed character responses!")
    socketio.run(app, host='localhost', port=3000, debug=True)