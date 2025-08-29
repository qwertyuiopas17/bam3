# STEP 2: Replace your inference.py with this working version

import torch
import re
import random

class MentalHealthChatInference:
    def __init__(self, model_path='mental_health_model.pth', tokenizer_path='mental_health_tokenizer.pkl', use_fallback_only=False):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_ready = False

        # Professional responses for each language and risk level
        self.professional_responses = {
            'en': {
                'low': [
                    "I understand you're going through a challenging time. It's completely normal to feel this way, and I'm here to support you. What would be most helpful for you right now?",
                    "Thank you for reaching out and sharing how you're feeling. That takes courage. Can you tell me more about what's been on your mind lately?",
                    "I hear that you're struggling, and I want you to know that your feelings are valid. How long have you been experiencing these feelings?",
                    "It sounds like you're dealing with some difficult emotions. Many people go through similar experiences. What kind of support would be most beneficial for you today?"
                ],
                'moderate': [
                    "I can see that you're experiencing some significant challenges right now. These feelings can be overwhelming, but please know that you're not alone. Have you been able to talk to anyone else about what you're going through?",
                    "What you're describing sounds really difficult to manage on your own. It's important to have support during times like these. Would you be open to discussing some coping strategies that might help?",
                    "I'm concerned about how you're feeling right now. These experiences can be very isolating, but there are people who want to help. Have you considered speaking with a counselor or therapist?",
                    "It takes strength to reach out when you're struggling. I want to help you find some relief from these overwhelming feelings. Would you like to explore some resources that might be helpful?"
                ],
                'high': [
                    "I'm very concerned about what you've shared with me. These thoughts and feelings are serious, and I want you to know that you don't have to face this alone. Please consider reaching out to a crisis helpline immediately: National Suicide Prevention Lifeline 988 or text HOME to 741741.",
                    "What you're experiencing right now sounds extremely difficult and painful. Your life has value, and there are people trained to help you through this crisis. Please contact emergency services (911) or the National Suicide Prevention Lifeline (988) right away.",
                    "I'm deeply worried about your safety right now. Please reach out for immediate professional help. You can call the National Suicide Prevention Lifeline at 988, go to your nearest emergency room, or call 911. You matter, and help is available.",
                    "These feelings you're describing are signs that you need immediate professional support. Please don't wait - contact the National Suicide Prevention Lifeline at 988 or emergency services. There are people who care and want to help you through this."
                ]
            },
            'hi': {
                'low': [
                    "मैं समझ सकता हूँ कि आप एक चुनौतीपूर्ण समय से गुजर रहे हैं। इस तरह महसूस करना बिल्कुल सामान्य है, और मैं यहाँ आपका साथ देने के लिए हूँ। अभी आपके लिए सबसे मददगार क्या होगा?",
                    "मेरे पास आने और अपनी भावनाओं को साझा करने के लिए धन्यवाद। इसमें साहस लगता है। क्या आप मुझे बता सकते हैं कि हाल ही में आपके मन में क्या चल रहा है?",
                    "मैं सुन रहा हूँ कि आप संघर्ष कर रहे हैं, और मैं चाहता हूँ कि आप जानें कि आपकी भावनाएं वैध हैं। आप कब से इन भावनाओं का अनुभव कर रहे हैं?",
                    "लगता है आप कुछ कठिन भावनाओं से निपट रहे हैं। कई लोग समान अनुभवों से गुजरते हैं। आज आपके लिए किस तरह का सहारा सबसे फायदेमंद होगा?"
                ],
                'moderate': [
                    "मैं देख सकता हूँ कि आप अभी कुछ महत्वपूर्ण चुनौतियों का सामना कर रहे हैं। ये भावनाएं भारी हो सकती हैं, लेकिन कृपया जानें कि आप अकेले नहीं हैं। क्या आप जिससे गुजर रहे हैं उसके बारे में किसी और से बात कर पाए हैं?",
                    "जो आप बता रहे हैं वह अकेले संभालना वाकई कठिन लगता है। ऐसे समय में सहारा होना महत्वपूर्ण है। क्या आप कुछ ऐसी रणनीतियों पर चर्चा करने के लिए तैयार होंगे जो मदद कर सकती हैं?",
                    "मुझे चिंता है कि आप अभी कैसा महसूस कर रहे हैं। ये अनुभव बहुत अलग-थलग कर सकते हैं, लेकिन ऐसे लोग हैं जो मदद करना चाहते हैं। क्या आपने किसी परामर्शदाता या चिकित्सक से बात करने पर विचार किया है?",
                    "संघर्ष के समय मदद माँगना ताकत दिखाता है। मैं आपको इन भारी भावनाओं से राहत दिलाने में मदद करना चाहता हूँ। क्या आप कुछ ऐसे संसाधनों का पता लगाना चाहेंगे जो सहायक हो सकते हैं?"
                ],
                'high': [
                    "आपने जो साझा किया है उससे मैं बहुत चिंतित हूँ। ये विचार और भावनाएं गंभीर हैं, और मैं चाहता हूँ कि आप जानें कि आपको इसका सामना अकेले नहीं करना है। कृपया तुरंत संकट हेल्पलाइन से संपर्क करने पर विचार करें: राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन 112।",
                    "आप अभी जो अनुभव कर रहे हैं वह अत्यंत कठिन और दर्दनाक लगता है। आपका जीवन मूल्यवान है, और ऐसे लोग हैं जो इस संकट से निपटने में आपकी मदद करने के लिए प्रशिक्षित हैं। कृपया तुरंत आपातकालीन सेवाओं (112) या राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन से संपर्क करें।",
                    "मुझे अभी आपकी सुरक्षा की गहरी चिंता है। कृपया तुरंत पेशेवर मदद लें। आप राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन 112 पर कॉल कर सकते हैं, अपने निकटतम आपातकालीन कक्ष में जा सकते हैं, या 112 डायल कर सकते हैं। आप महत्वपूर्ण हैं, और मदद उपलब्ध है।",
                    "आप जिन भावनाओं का वर्णन कर रहे हैं वे इस बात के संकेत हैं कि आपको तुरंत पेशेवर सहायता की आवश्यकता है। कृपया प्रतीक्षा न करें - राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन 112 या आपातकालीन सेवाओं से संपर्क करें। ऐसे लोग हैं जो परवाह करते हैं और इससे उबरने में आपकी मदद करना चाहते हैं।"
                ]
            }
        }

        # Only try to load model if not using fallback only
        if not use_fallback_only:
            try:
                from tokenizer import MentalHealthTokenizer
                from model import MentalHealthChatbot

                self.tokenizer = MentalHealthTokenizer()
                self.tokenizer.load(tokenizer_path)

                self.model = MentalHealthChatbot(self.tokenizer.vocab_size)
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()

                self.model_ready = True
                print("✅ AI Model loaded successfully")

            except Exception as e:
                print(f"⚠️  Model loading failed, using fallback responses: {e}")
                self.model_ready = False
        else:
            print("🔄 Using fallback responses only")

    def detect_language(self, text):
        """Simple language detection"""
        if not text:
            return 'en'
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(text.strip())
        return 'hi' if devanagari_chars > 0.3 * total_chars else 'en'

    def assess_crisis_level(self, text):
        """Assess crisis level from user input"""
        text_lower = text.lower()

        # High-risk indicators (multiple languages)
        high_risk_phrases = [
            'kill myself', 'end it all', 'suicide', 'better off dead', 'want to die',
            'hurt myself', 'end my life', 'not worth living', 'no point living',
            'मरना चाहता', 'आत्महत्या', 'जिंदगी खत्म', 'मौत चाहिए', 'जीने का मन नहीं'
        ]

        # Moderate risk indicators  
        moderate_risk_phrases = [
            'hopeless', 'worthless', 'alone all the time', 'isolated', 'very depressed',
            'can\'t cope', 'overwhelming', 'give up', 'nobody cares', 'hate myself',
            'निराशा', 'बेकार', 'अकेला', 'हार गया', 'कोई नहीं समझता', 'बहुत परेशान'
        ]

        # Check for high risk first
        for phrase in high_risk_phrases:
            if phrase in text_lower:
                return 'high'

        # Check for moderate risk
        for phrase in moderate_risk_phrases:
            if phrase in text_lower:
                return 'moderate'

        return 'low'

    def generate_response(self, user_input, target_language='en', temperature=0.7, max_length=50):
        """🔥 MAIN FIX: Generate response in specified target language"""

        if not user_input or not user_input.strip():
            empty_messages = {
                'en': "I'm here to listen. Please share what's on your mind.",
                'hi': "मैं यहाँ सुनने के लिए हूँ। कृपया बताएं कि आपके मन में क्या है।"
            }
            return {
                'response': empty_messages.get(target_language, empty_messages['en']),
                'is_crisis': False,
                'language': target_language
            }

        # Assess crisis level
        crisis_level = self.assess_crisis_level(user_input)
        is_crisis = crisis_level in ['moderate', 'high']

        # Try AI model first if available
        if self.model_ready:
            try:
                input_ids = self.tokenizer.encode(user_input, max_length=128)
                input_tensor = torch.tensor([input_ids], device=self.device)

                with torch.no_grad():
                    result = self.model.generate(input_tensor, self.tokenizer, max_length, temperature)
                    model_response = result['response'].strip()

                    # Validate model response
                    detected_lang = self.detect_language(model_response)
                    if (detected_lang == target_language and 
                        len(model_response.split()) >= 3 and 
                        not any(char in model_response for char in ['<', '>', '[', ']', '_'])):

                        return {
                            'response': model_response,
                            'is_crisis': is_crisis,
                            'language': target_language
                        }
            except Exception as e:
                print(f"⚠️  AI model failed: {e}")

        # Use professional fallback responses
        responses = self.professional_responses.get(target_language, self.professional_responses['en'])
        response_list = responses.get(crisis_level, responses['low'])
        response = random.choice(response_list)

        return {
            'response': response,
            'is_crisis': is_crisis,
            'language': target_language,
            'source': 'fallback'
        }

# Test the inference system
if __name__ == "__main__":
    print("🧪 Testing Inference System...")

    # Test with fallback only
    inference = MentalHealthChatInference(use_fallback_only=True)

    test_cases = [
        ("I'm feeling anxious about exams", 'en'),
        ("मुझे बहुत परेशानी हो रही है", 'hi'),
        ("I don't want to live anymore", 'en'),
        ("मैं बहुत उदास हूँ", 'hi')
    ]

    for text, lang in test_cases:
        result = inference.generate_response(text, target_language=lang)
        print(f"\n{lang.upper()}: {text}")
        print(f"Response: {result['response'][:60]}...")
        print(f"Crisis: {result['is_crisis']}")
