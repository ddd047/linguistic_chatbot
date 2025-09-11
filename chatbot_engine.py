import json
import os
from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher
from datetime import datetime
from language_processor import LanguageProcessor

class ChatbotEngine:
    def __init__(self):
        self.language_processor = LanguageProcessor()
        self.knowledge_base = self._load_knowledge_base()
        self.session_contexts = {}  # Store conversation context by session_id
        self.confidence_threshold = 0.6
        
    def _load_knowledge_base(self) -> Dict:
        """Load the FAQ knowledge base from JSON file"""
        kb_path = os.path.join("..", "data", "knowledge_base.json")
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default knowledge base if file doesn't exist
            return self._get_default_knowledge_base()
    
    def _get_default_knowledge_base(self) -> Dict:
        """Default knowledge base with common campus queries"""
        return {
            "categories": {
                "fees": {
                    "keywords": ["fee", "fees", "payment", "tuition", "शुल्क", "फीस", "ફી", "शुल्क"],
                    "responses": {
                        "en": "Fee payment deadline is usually at the beginning of each semester. You can pay online through the college portal or visit the accounts office.",
                        "hi": "शुल्क भुगतान की अंतिम तिथि आमतौर पर हर सेमेस्टर की शुरुआत में होती है। आप कॉलेज पोर्टल के माध्यम से ऑनलाइन भुगतान कर सकते हैं या खाता कार्यालय जा सकते हैं।",
                        "gu": "ફી ચુકવણીની અંતિમ તારીખ સામાન્ય રીતે દરેક સેમેસ્ટરની શરૂઆતમાં હોય છે. તમે કૉલેજ પોર્ટલ દ્વારા ઑનલાઇન ચુકવણી કરી શકો છો અથવા એકાઉન્ટ્સ ઑફિસની મુલાકાત લઈ શકો છો.",
                        "mr": "शुल्क भरणाची शेवटची तारीख सहसा प्रत्येक सेमेस्टरच्या सुरुवातीला असते. तुम्ही कॉलेज पोर्टलद्वारे ऑनलाइन पेमेंट करू शकता किंवा खाते कार्यालयात जाऊ शकता.",
                        "raj": "शुल्क भुगतान री अंतिम तारीख सामान्यतः हर सेमेस्टर री शुरुआत में होवै। थे कॉलेज पोर्टल रे जरिये ऑनलाइन भुगतान कर सको या खाता कार्यालय जा सको।"
                    }
                },
                "scholarships": {
                    "keywords": ["scholarship", "scholarships", "financial aid", "छात्रवृत्ति", "स्कॉलरशिप", "સ્કોલરશિપ", "शिष्यवृत्ती"],
                    "responses": {
                        "en": "Scholarship applications are available on the college website. Merit and need-based scholarships are offered. Submit documents before the deadline.",
                        "hi": "छात्रवृत्ति के लिए आवेदन कॉलेज की वेबसाइट पर उपलब्ध हैं। योग्यता और आवश्यकता आधारित छात्रवृत्ति उपलब्ध हैं। अंतिम तिथि से पहले दस्तावेज जमा करें।",
                        "gu": "સ્કોલરશિપ માટે અરજીઓ કૉલેજની વેબસાઇટ પર ઉપલબ્ધ છે. મેરિટ અને જરૂરિયાત આધારિત સ્કોલરશિપ ઓફર કરવામાં આવે છે. અંતિમ તારીખ પહેલા દસ્તાવેજો સબમિટ કરો.",
                        "mr": "शिष्यवृत्तीसाठी अर्ज कॉलेजच्या वेबसाइटवर उपलब्ध आहेत. गुणवत्ता आणि गरज आधारित शिष्यवृत्ती दिली जाते. शेवटच्या तारखेपूर्वी कागदपत्रे सादर करा.",
                        "raj": "छात्रवृत्ति के लिए आवेदन कॉलेज री वेबसाइट पे उपलब्ध है। योग्यता अर गरज के आधार पे छात्रवृत्ति मिलै। अंतिम तारीख सूं पैली दस्तावेज जमा करो।"
                    }
                },
                "timetable": {
                    "keywords": ["timetable", "schedule", "class", "timing", "समय सारणी", "टाइम टेबल", "વર્ગ", "वेळापत्रक"],
                    "responses": {
                        "en": "Timetables are updated on the college notice board and website. Check for any last-minute changes before attending classes.",
                        "hi": "समय सारणी कॉलेज के नोटिस बोर्ड और वेबसाइट पर अपडेट की जाती है। कक्षा में जाने से पहले किसी भी अंतिम समय के बदलाव की जांच करें।",
                        "gu": "સમયપત્રક કૉલેજના નોટિસ બોર્ડ અને વેબસાઇટ પર અપડેટ કરવામાં આવે છે. વર્ગમાં હાજરી આપતા પહેલા કોઈપણ છેલ્લી ઘડીના ફેરફારો માટે તપાસો.",
                        "mr": "वेळापत्रक कॉलेजच्या नोटीस बोर्ड आणि वेबसाइटवर अपडेट केले जाते. वर्गात जाण्यापूर्वी शेवटच्या क्षणी झालेल्या बदलांची तपासणी करा.",
                        "raj": "समय सारणी कॉलेज रे नोटिस बोर्ड अर वेबसाइट पे अपडेट होवै। क्लास में जावण सूं पैली कोई भी अंतिम समय रे बदलाव री जांच करो।"
                    }
                },
                "admission": {
                    "keywords": ["admission", "admissions", "apply", "entrance", "प्रवेश", "दाखिला", "પ્રવેશ", "प्रवेश"],
                    "responses": {
                        "en": "Admission applications are open from June to August. Check eligibility criteria, fill the online form, and submit required documents.",
                        "hi": "प्रवेश आवेदन जून से अगस्त तक खुले रहते हैं। पात्रता मानदंड जांचें, ऑनलाइन फॉर्म भरें और आवश्यक दस्तावेज जमा करें।",
                        "gu": "પ્રવેશની અરજીઓ જૂનથી ઓગસ્ટ સુધી ખુલ્લી છે. પાત્રતાના માપદંડો તપાસો, ઓનલાઇન ફોર્મ ભરો અને જરૂરી દસ્તાવેજો સબમિટ કરો.",
                        "mr": "प्रवेश अर्ज जून ते ऑगस्ट पर्यंत उघडे आहेत. पात्रता निकष तपासा, ऑनलाइन फॉर्म भरा आणि आवश्यक कागदपत्रे सादर करा.",
                        "raj": "प्रवेश आवेदन जून सूं अगस्त तक खुले रहवै हैं। पात्रता मानदंड देखो, ऑनलाइन फॉर्म भरो अर जरूरी दस्तावेज जमा करो।"
                    }
                },
                "exams": {
                    "keywords": ["exam", "exams", "test", "results", "marks", "परीक्षा", "પરીક્ષા", "परीक्षा"],
                    "responses": {
                        "en": "Exam schedules are published on the college website 2 weeks before exams. Results are declared within 30 days after completion.",
                        "hi": "परीक्षा कार्यक्रम परीक्षा से 2 सप्ताह पहले कॉलेज की वेबसाइट पर प्रकाशित होते हैं। परिणाम पूरा होने के 30 दिनों के भीतर घोषित किए जाते हैं।",
                        "gu": "પરીક્ષાનું શેડ્યૂલ પરીક્ષાના 2 અઠવાડિયા પહેલા કૉલેજની વેબસાઇટ પર પ્રકાશિત કરવામાં આવે છે. પરિણામો પૂર્ણ થયાના 30 દિવસની અંદર જાહેર કરવામાં આવે છે.",
                        "mr": "परीक्षेचे वेळापत्रक परीक्षेच्या 2 आठवड्यांपूर्वी कॉलेजच्या वेबसाइटवर प्रकाशित केले जाते. निकाल पूर्ण झाल्यानंतर 30 दिवसांच्या आत जाहीर केले जातात.",
                        "raj": "परीक्षा कार्यक्रम परीक्षा सूं 2 हफ्ता पैली कॉलेज री वेबसाइट पे छपवावै। परिणाम पूरा होवण रे 30 दिन रे अंदर घोषित करावै।"
                    }
                }
            },
            "greetings": {
                "keywords": ["hello", "hi", "hey", "namaste", "नमस्ते", "નમસ્તે", "नमस्कार"],
                "responses": {
                    "en": "Hello! I'm your campus assistant. I can help you with information about fees, scholarships, timetables, admissions, and exams. How can I help you today?",
                    "hi": "नमस्ते! मैं आपका कैंपस सहायक हूं। मैं शुल्क, छात्रवृत्ति, समय सारणी, प्रवेश और परीक्षा के बारे में जानकारी दे सकता हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
                    "gu": "નમસ્તે! હું તમારો કેમ્પસ સહાયક છું. હું ફી, સ્કોલરશિપ, સમયપત્રક, પ્રવેશ અને પરીક્ષાઓ વિશે માહિતી આપી શકું છું. આજે હું તમને કેવી રીતે મદદ કરી શકું?",
                    "mr": "नमस्कार! मी तुमचा कॅम्पस सहाय्यक आहे. मी फी, शिष्यवृत्ती, वेळापत्रक, प्रवेश आणि परीक्षांबद्दल माहिती देऊ शकतो. आज मी तुम्हाला कशी मदत करू शकतो?",
                    "raj": "नमस्ते! मैं थारो कैंपस सहायक हूं। मैं शुल्क, छात्रवृत्ति, समय सारणी, प्रवेश अर परीक्षा रे बारे में जानकारी दे सकूं। आज मैं थारी कैसे मदद कर सकूं?"
                }
            },
            "contact": {
                "office_hours": "9:00 AM - 5:00 PM, Monday to Friday",
                "phone": "+91-XXX-XXX-XXXX",
                "email": "info@college.edu",
                "address": "College Campus, City, State"
            }
        }
    
    async def process_message(self, message: str, session_id: str, language: str) -> Dict:
        """Process user message and return appropriate response"""
        
        # Initialize session context if new
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                "messages": [],
                "last_category": None,
                "language": language
            }
        
        # Add message to context
        self.session_contexts[session_id]["messages"].append({
            "user": message,
            "timestamp": str(datetime.now())
        })
        
        # Find best matching response
        category, confidence = self._find_best_match(message, language)
        
        if confidence < self.confidence_threshold:
            # Low confidence - suggest human contact
            response = self._get_fallback_response(language)
            needs_human = True
        else:
            # Get response from knowledge base
            response = self._get_response(category, language)
            needs_human = False
        
        # Update session context
        self.session_contexts[session_id]["last_category"] = category
        self.session_contexts[session_id]["messages"][-1]["bot"] = response
        
        return {
            "response": response,
            "confidence": confidence,
            "category": category,
            "needs_human": needs_human,
            "contact": self.knowledge_base.get("contact", {}) if needs_human else None
        }
    
    def _find_best_match(self, message: str, language: str) -> Tuple[str, float]:
        """Find the best matching category for the user message"""
        message_lower = message.lower()
        best_match = None
        best_score = 0.0
        
        # Check greeting first
        greeting_keywords = self.knowledge_base["greetings"]["keywords"]
        for keyword in greeting_keywords:
            if keyword in message_lower:
                return "greetings", 0.9
        
        # Check categories
        for category, data in self.knowledge_base["categories"].items():
            keywords = data["keywords"]
            
            for keyword in keywords:
                # Direct keyword match
                if keyword in message_lower:
                    score = 0.8
                    if score > best_score:
                        best_score = score
                        best_match = category
                
                # Fuzzy string matching for better accuracy
                similarity = SequenceMatcher(None, keyword, message_lower).ratio()
                if similarity > 0.6 and similarity > best_score:
                    best_score = similarity
                    best_match = category
        
        return best_match or "unknown", best_score
    
    def _get_response(self, category: str, language: str) -> str:
        """Get response for the given category and language"""
        if category == "greetings":
            responses = self.knowledge_base["greetings"]["responses"]
        elif category in self.knowledge_base["categories"]:
            responses = self.knowledge_base["categories"][category]["responses"]
        else:
            return self._get_fallback_response(language)
        
        # Return response in requested language, fallback to English
        return responses.get(language, responses.get("en", "I'm sorry, I don't understand."))
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when confidence is low"""
        fallback_responses = {
            "en": "I'm not sure about that. Please contact our office during business hours (9 AM - 5 PM) at +91-XXX-XXX-XXXX or email info@college.edu for assistance.",
            "hi": "मुझे इसके बारे में यकीन नहीं है। कृपया व्यावसायिक घंटों (सुबह 9 बजे - शाम 5 बजे) के दौरान हमारे कार्यालय से +91-XXX-XXX-XXXX पर संपर्क करें या सहायता के लिए info@college.edu पर ईमेल करें।",
            "gu": "મને તેના વિશે ખાતરી નથી. કૃપા કરીને બિઝનેસ અવર્સ (સવારે 9 - સાંજે 5) દરમિયાન અમારી ઓફિસનો સંપર્ક કરો +91-XXX-XXX-XXXX અથવા સહાયતા માટે info@college.edu પર ઈમેલ કરો.",
            "mr": "मला त्याबद्दल खात्री नाही. कृपया कार्यालयीन वेळेत (सकाळी 9 - संध्याकाळी 5) आमच्या कार्यालयाशी +91-XXX-XXX-XXXX वर संपर्क साधा किंवा मदतीसाठी info@college.edu वर ईमेल करा.",
            "raj": "मने इसके बारे में पक्का नहीं है। कृपया व्यावसायिक समय (सवेरे 9 - सांझ 5) में हमारे कार्यालय सूं +91-XXX-XXX-XXXX पे संपर्क करो या मदद रे लिए info@college.edu पे ईमेल करो।"
        }
        
        return fallback_responses.get(language, fallback_responses["en"])
    
    def get_session_context(self, session_id: str) -> Optional[Dict]:
        """Get conversation context for a session"""
        return self.session_contexts.get(session_id)
    
    def clear_session_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
