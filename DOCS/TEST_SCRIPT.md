# Multilingual Campus Chatbot - Testing Script

This document provides comprehensive testing procedures for the multilingual campus chatbot system.

## 🧪 Pre-Testing Setup

### 1. Verify System is Running

**Backend Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}
```

**Frontend Check:**
- Open `http://localhost:3000` in browser
- Verify the welcome message is displayed
- Check that language selector shows 5 options

## 📝 Test Cases

### Test 1: Basic Functionality

| Test Step | Expected Result | ✅ Pass | ❌ Fail |
|-----------|----------------|---------|---------|
| Load main interface | Welcome message appears with topic tags | ☐ | ☐ |
| Type "Hello" and send | Bot responds with greeting in English | ☐ | ☐ |
| Check session info | Session ID and message count update | ☐ | ☐ |
| Click clear chat | Conversation history clears | ☐ | ☐ |

### Test 2: Language Detection & Response

#### English Queries
| Query | Expected Keywords Detected | Expected Response Topic | ✅ Pass | ❌ Fail |
|-------|---------------------------|------------------------|---------|---------|
| "What are the fees?" | fees, payment | Fee information with payment details | ☐ | ☐ |
| "Scholarship information" | scholarship, aid | Scholarship application process | ☐ | ☐ |
| "Library timings" | library, books | Library hours and services | ☐ | ☐ |
| "Random question about aliens" | unknown | Fallback response with contact info | ☐ | ☐ |

#### Hindi Queries
| Query | Expected Response Language | ✅ Pass | ❌ Fail |
|-------|---------------------------|---------|---------|
| "शुल्क क्या है?" | Hindi response about fees | ☐ | ☐ |
| "छात्रवृत्ति कैसे मिलेगी?" | Hindi response about scholarships | ☐ | ☐ |
| "पुस्तकालय कब खुला रहता है?" | Hindi response about library | ☐ | ☐ |

#### Gujarati Queries
| Query | Expected Response Language | ✅ Pass | ❌ Fail |
|-------|---------------------------|---------|---------|
| "ફી કેટલી છે?" | Gujarati response about fees | ☐ | ☐ |
| "સ્કોલરશિપ માટે અરજી કેવી રીતે કરવી?" | Gujarati response about scholarships | ☐ | ☐ |

#### Marathi Queries
| Query | Expected Response Language | ✅ Pass | ❌ Fail |
|-------|---------------------------|---------|---------|
| "शुल्क किती आहे?" | Marathi response about fees | ☐ | ☐ |
| "शिष्यवृत्तीसाठी अर्ज कसा करावा?" | Marathi response about scholarships | ☐ | ☐ |

#### Rajasthani Queries
| Query | Expected Response Language | ✅ Pass | ❌ Fail |
|-------|---------------------------|---------|---------|
| "शुल्क कितनो है?" | Rajasthani response about fees | ☐ | ☐ |
| "छात्रवृत्ति कैसे मिलै?" | Rajasthani response about scholarships | ☐ | ☐ |

### Test 3: User Interface Features

| Feature | Test Action | Expected Result | ✅ Pass | ❌ Fail |
|---------|-------------|----------------|---------|---------|
| Language Selector | Change from English to Hindi | Welcome message updates to Hindi | ☐ | ☐ |
| Quick Actions | Click "💰 Fees" button | Sends fees query automatically | ☐ | ☐ |
| Help Sidebar | Click help button (?) | Sidebar opens with contact info | ☐ | ☐ |
| Settings Modal | Click settings gear icon | Modal opens with theme/font options | ☐ | ☐ |
| Theme Toggle | Change theme to Dark | Interface switches to dark mode | ☐ | ☐ |
| Responsive Design | Resize browser to mobile width | Layout adapts properly | ☐ | ☐ |

### Test 4: Context Management

| Test Step | Action | Expected Result | ✅ Pass | ❌ Fail |
|-----------|--------|----------------|---------|---------|
| 1 | Send "Hello" | Bot greets user | ☐ | ☐ |
| 2 | Send "Fees" | Bot provides fee information | ☐ | ☐ |
| 3 | Send "What about scholarships?" | Bot provides scholarship info (maintains context) | ☐ | ☐ |
| 4 | Send "Thank you" | Bot acknowledges thanks | ☐ | ☐ |

### Test 5: Error Handling

| Error Scenario | How to Test | Expected Result | ✅ Pass | ❌ Fail |
|----------------|-------------|----------------|---------|---------|
| Backend Down | Stop backend server, try sending message | Error message displayed | ☐ | ☐ |
| Network Error | Disconnect internet, try sending message | Connection error shown | ☐ | ☐ |
| Empty Message | Try sending empty message | Message not sent, no error | ☐ | ☐ |
| Very Long Message | Send 1000+ character message | System handles gracefully | ☐ | ☐ |

### Test 6: Widget Integration

| Test | Action | Expected Result | ✅ Pass | ❌ Fail |
|------|--------|----------------|---------|---------|
| Widget Loading | Open `widget.html` | Compact chat interface loads | ☐ | ☐ |
| Widget Functionality | Send test message in widget | Same bot responses as main interface | ☐ | ☐ |
| Widget Languages | Change language in widget | Interface updates accordingly | ☐ | ☐ |

## 🔍 Performance Testing

### Response Time Testing

Test with a stopwatch or browser dev tools:

| Query Type | Expected Response Time | Actual Time | ✅ Pass | ❌ Fail |
|------------|----------------------|-------------|---------|---------|
| Simple greeting | < 1 second | ___ seconds | ☐ | ☐ |
| Knowledge base query | < 2 seconds | ___ seconds | ☐ | ☐ |
| Unknown query (fallback) | < 1 second | ___ seconds | ☐ | ☐ |

### Load Testing (Optional)

For production systems, test with multiple simultaneous users:

```bash
# Simple load test (requires Apache Bench)
ab -n 100 -c 10 -H "Content-Type: application/json" \
   -p test_payload.json http://localhost:8000/chat
```

## 📊 API Testing

### Health Check
```bash
curl -X GET http://localhost:8000/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-XX-XXTXX:XX:XX.XXXXXX",
  "components": {
    "chatbot_engine": "ok",
    "language_processor": "ok", 
    "conversation_logger": "ok"
  }
}
```

### Chat API
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "session_id": "test_session",
    "language": "en"
  }'
```

**Expected Response Structure:**
```json
{
  "response": "Hello! Welcome to our campus assistant...",
  "detected_language": "en",
  "session_id": "test_session",
  "confidence": 0.9,
  "needs_human": false,
  "suggested_contact": null
}
```

### Logs API
```bash
curl -X GET http://localhost:8000/logs/daily
```

## 🐛 Common Issues & Solutions

### Issue: Bot not responding
**Symptoms:** Messages sent but no response
**Check:**
- Backend server running? `curl http://localhost:8000/health`
- CORS errors in browser console?
- Correct API_BASE_URL in frontend?

### Issue: Wrong language detected
**Symptoms:** English query gets Hindi response
**Check:**
- Language patterns in `language_processor.py`
- Knowledge base keywords accuracy
- langdetect library installation

### Issue: Low confidence scores
**Symptoms:** Many queries result in human handoff
**Check:**
- Knowledge base completeness
- Keyword matching accuracy
- Confidence threshold settings

## ✅ Test Completion Checklist

### Basic Functionality
- [ ] System startup successful
- [ ] Main interface loads correctly
- [ ] Chat functionality works
- [ ] Language detection working

### Multilingual Support
- [ ] English responses correct
- [ ] Hindi responses correct
- [ ] Gujarati responses correct
- [ ] Marathi responses correct
- [ ] Rajasthani responses correct

### User Interface
- [ ] All buttons functional
- [ ] Responsive design working
- [ ] Themes switch properly
- [ ] Accessibility features working

### Integration
- [ ] Widget integration working
- [ ] Embeddable code functional
- [ ] API endpoints responding
- [ ] Logging system active

### Error Handling
- [ ] Network errors handled gracefully
- [ ] Invalid inputs managed properly
- [ ] Fallback responses working
- [ ] Human handoff functioning

## 📋 Test Report Template

**Test Date:** ___________  
**Tester Name:** ___________  
**System Version:** ___________  

**Overall Results:**
- Total Tests: ____
- Passed: ____
- Failed: ____
- Success Rate: ____%

**Critical Issues Found:**
1. ________________________________
2. ________________________________
3. ________________________________

**Recommendations:**
1. ________________________________
2. ________________________________
3. ________________________________

**System Ready for Production:** ☐ Yes ☐ No

**Tester Signature:** ___________

---

**Note:** Run these tests in a development environment first. For production deployment, ensure all tests pass with at least 95% success rate.
