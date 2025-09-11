from typing import Optional, Dict
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent language detection
DetectorFactory.seed = 0

class LanguageProcessor:
    def __init__(self):
        # Language mappings
        self.language_map = {
            'en': 'en',  # English
            'hi': 'hi',  # Hindi
            'gu': 'gu',  # Gujarati
            'mr': 'mr',  # Marathi
            'raj': 'raj'  # Rajasthani (not directly supported by langdetect, use pattern matching)
        }
        
        # Common patterns for different languages
        self.language_patterns = {
            'hi': [
                r'[\u0900-\u097F]',  # Devanagari script (Hindi)
                r'\b(क्या|कैसे|कब|क्यों|कहाँ|नमस्ते|धन्यवाद)\b'
            ],
            'gu': [
                r'[\u0A80-\u0AFF]',  # Gujarati script
                r'\b(શું|કેવી|ક્યારે|કેમ|ક્યાં|નમસ્તે|ધન્યવાદ)\b'
            ],
            'mr': [
                r'[\u0900-\u097F]',  # Devanagari script (also used for Marathi)
                r'\b(काय|कसे|केव्हा|का|कुठे|नमस्कार|धन्यवाद)\b'
            ],
            'raj': [
                r'[\u0900-\u097F]',  # Devanagari script
                r'\b(के|कैं|कद|क्यूं|कठै|नमस्ते|धन्यवाद)\b'
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        if not text or len(text.strip()) < 3:
            return 'en'  # Default to English for very short text
        
        try:
            # First try pattern-based detection for regional languages
            detected_lang = self._pattern_based_detection(text)
            if detected_lang:
                return detected_lang
            
            # Fall back to langdetect
            detected = detect(text)
            
            # Map detected language to our supported languages
            if detected in self.language_map:
                return self.language_map[detected]
            else:
                # If not directly supported, try to map similar languages
                return self._map_similar_language(detected)
                
        except LangDetectException:
            # If detection fails, default to English
            return 'en'
    
    def _pattern_based_detection(self, text: str) -> Optional[str]:
        """Use regex patterns to detect language"""
        for lang, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return lang
        return None
    
    def _map_similar_language(self, detected_lang: str) -> str:
        """Map similar or related languages to our supported set"""
        language_mappings = {
            'ne': 'hi',  # Nepali -> Hindi (similar script)
            'bn': 'hi',  # Bengali -> Hindi (similar region)
            'ur': 'hi',  # Urdu -> Hindi (similar)
            'pa': 'hi',  # Punjabi -> Hindi
        }
        
        return language_mappings.get(detected_lang, 'en')
    
    def is_supported_language(self, language: str) -> bool:
        """Check if the language is supported"""
        return language in self.language_map
    
    def get_language_name(self, lang_code: str) -> str:
        """Get the full name of the language from its code"""
        language_names = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'gu': 'Gujarati (ગુજરાતી)',
            'mr': 'Marathi (मराठी)',
            'raj': 'Rajasthani (राजस्थानी)'
        }
        return language_names.get(lang_code, 'Unknown')
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better processing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert to lowercase for English text (preserve case for other languages)
        if self.detect_language(text) == 'en':
            text = text.lower()
        
        return text
    
    def extract_keywords(self, text: str, language: str) -> list:
        """Extract important keywords from text based on language"""
        normalized_text = self.normalize_text(text)
        
        # Common stop words for different languages
        stop_words = {
            'en': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'],
            'hi': ['और', 'या', 'में', 'पर', 'से', 'के', 'की', 'को', 'का'],
            'gu': ['અને', 'અથવા', 'માં', 'પર', 'થી', 'ના', 'નું', 'ને'],
            'mr': ['आणि', 'किंवा', 'मध्ये', 'वर', 'पासून', 'चा', 'ची', 'ला'],
            'raj': ['अर', 'या', 'में', 'पर', 'सूं', 'रो', 'री', 'नै']
        }
        
        # Split into words and remove stop words
        words = normalized_text.split()
        stop_list = stop_words.get(language, stop_words['en'])
        
        keywords = [word for word in words if word not in stop_list and len(word) > 2]
        
        return keywords
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages with their names"""
        return {
            code: self.get_language_name(code) 
            for code in self.language_map.keys()
        }
