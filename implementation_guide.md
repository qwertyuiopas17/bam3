# DIGITAL MENTAL HEALTH PLATFORM - IMPLEMENTATION GUIDE

## 1. FRONTEND DEVELOPMENT

### React.js Components Structure:
`src/
├── components/
│   ├── Dashboard/
│   │   ├── StudentDashboard.jsx
│   │   ├── ProgressTracker.jsx
│   │   └── WellnessMetrics.jsx
│   ├── Chat/
│   │   ├── ChatInterface.jsx
│   │   ├── MessageBubble.jsx
│   │   └── CrisisAlert.jsx
│   ├── Assessment/
│   │   ├── PHQ9Form.jsx
│   │   ├── GAD7Form.jsx
│   │   └── ResultsDisplay.jsx
│   ├── Resources/
│   │   ├── ResourceLibrary.jsx
│   │   ├── CBTModules.jsx
│   │   └── MindfulnessContent.jsx
│   └── Booking/
│       ├── AppointmentScheduler.jsx
│       └── CounselorList.jsx
├── services/
│   ├── api.js
│   ├── auth.js
│   └── websocket.js
└── utils/
    ├── encryption.js
    └── validation.js
`

### Sample Chat Interface Component:
`import React, { useState, useEffect } from 'react';
import { sendMessage, subscribeToChat } from '../services/api';

const ChatInterface = ({ userId, language = 'en' }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [crisisDetected, setCrisisDetected] = useState(false);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      language: language
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await sendMessage({
        message: inputMessage,
        userId,
        language
      });

      if (response.crisisDetected) {
        setCrisisDetected(true);
        // Trigger crisis intervention protocol
      }

      const aiMessage = {
        id: Date.now() + 1,
        text: response.message,
        sender: 'ai',
        timestamp: new Date(),
        confidence: response.confidence,
        resources: response.suggestedResources
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="message-list">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isTyping && <TypingIndicator />}
      </div>

      {crisisDetected && (
        <CrisisAlert 
          onAcceptHelp={() => {/* Navigate to crisis resources */}}
          onDismiss={() => setCrisisDetected(false)}
        />
      )}

      <div className="input-area">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={language === 'hi' ? 'अपना संदेश टाइप करें...' : 'Type your message...'}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};
`

## 2. BACKEND API DEVELOPMENT

### Express.js Server Structure:
`backend/
├── controllers/
│   ├── authController.js
│   ├── chatController.js
│   ├── assessmentController.js
│   └── bookingController.js
├── models/
│   ├── User.js
│   ├── Assessment.js
│   ├── ChatSession.js
│   └── Appointment.js
├── services/
│   ├── aiService.js
│   ├── crisisDetection.js
│   ├── emailService.js
│   └── smsService.js
├── middleware/
│   ├── auth.js
│   ├── validation.js
│   └── rateLimiting.js
├── routes/
│   ├── api.js
│   ├── chat.js
│   └── admin.js
└── utils/
    ├── encryption.js
    └── logger.js
`

### Sample Chat Controller:
`const aiService = require('../services/aiService');
const crisisDetection = require('../services/crisisDetection');
const ChatSession = require('../models/ChatSession');
const ChatMessage = require('../models/ChatMessage');

const chatController = {
  async sendMessage(req, res) {
    try {
      const { message, userId, language = 'en', sessionId } = req.body;

      // Find or create chat session
      let session = await ChatSession.findById(sessionId) || 
                    new ChatSession({ userId, startTime: new Date() });

      // Save user message
      const userMessage = new ChatMessage({
        sessionId: session._id,
        senderType: 'user',
        messageText: message,
        messageLanguage: language,
        timestamp: new Date()
      });
      await userMessage.save();

      // Analyze message for crisis indicators
      const crisisAnalysis = await crisisDetection.analyzeMessage(message, language);

      if (crisisAnalysis.riskLevel >= 3) {
        // High risk detected - trigger immediate intervention
        await crisisDetection.triggerIntervention(userId, crisisAnalysis);
        session.crisisDetected = true;
        session.counselorNotified = true;
      }

      // Generate AI response
      const aiResponse = await aiService.generateResponse({
        message,
        language,
        userProfile: await getUserProfile(userId),
        conversationHistory: await getRecentMessages(session._id),
        crisisContext: crisisAnalysis
      });

      // Save AI response
      const aiMessage = new ChatMessage({
        sessionId: session._id,
        senderType: 'ai',
        messageText: aiResponse.text,
        messageLanguage: language,
        sentimentScore: aiResponse.sentiment,
        emotionDetected: aiResponse.emotion,
        aiConfidence: aiResponse.confidence,
        timestamp: new Date()
      });
      await aiMessage.save();

      session.messageCount += 2;
      await session.save();

      res.json({
        message: aiResponse.text,
        confidence: aiResponse.confidence,
        crisisDetected: crisisAnalysis.riskLevel >= 3,
        suggestedResources: aiResponse.resources,
        sessionId: session._id
      });

    } catch (error) {
      console.error('Chat error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  },

  async getChatHistory(req, res) {
    try {
      const { sessionId } = req.params;
      const messages = await ChatMessage.find({ sessionId })
                                       .sort({ timestamp: 1 })
                                       .limit(50);
      res.json(messages);
    } catch (error) {
      res.status(500).json({ error: 'Failed to retrieve chat history' });
    }
  }
};

module.exports = chatController;
`

## 3. AI SERVICE IMPLEMENTATION

### Crisis Detection Service:
`const natural = require('natural');
const sentiment = require('sentiment');

class CrisisDetectionService {
  constructor() {
    this.suicideKeywords = [
      'kill myself', 'end it all', 'better off dead', 'suicide', 
      'want to die', 'hurt myself', 'no point living'
    ];

    this.selfHarmKeywords = [
      'cut myself', 'hurt myself', 'self harm', 'pain feels good'
    ];

    this.hopelessnessKeywords = [
      'no hope', 'nothing matters', 'pointless', 'worthless',
      'nobody cares', 'alone forever'
    ];

    // Hindi translations
    this.hindiCrisisKeywords = [
      'मरना चाहता हूं', 'जीना नहीं चाहता', 'आत्महत्या', 'खुद को दुख देना'
    ];
  }

  async analyzeMessage(message, language = 'en') {
    const lowerMessage = message.toLowerCase();
    let riskScore = 0;
    let indicators = [];

    // Sentiment analysis
    const sentimentAnalysis = sentiment(message);
    if (sentimentAnalysis.score < -5) {
      riskScore += 2;
      indicators.push('Highly negative sentiment');
    }

    // Keyword matching
    const keywords = language === 'hi' ? 
                    [...this.suicideKeywords, ...this.hindiCrisisKeywords] :
                    this.suicideKeywords;

    for (const keyword of keywords) {
      if (lowerMessage.includes(keyword.toLowerCase())) {
        riskScore += 4;
        indicators.push(Crisis keyword detected: ${keyword});
      }
    }

    // Self-harm detection
    for (const keyword of this.selfHarmKeywords) {
      if (lowerMessage.includes(keyword)) {
        riskScore += 3;
        indicators.push(Self-harm indicator: ${keyword});
      }
    }

    // Hopelessness detection
    for (const keyword of this.hopelessnessKeywords) {
      if (lowerMessage.includes(keyword)) {
        riskScore += 1;
        indicators.push(Hopelessness indicator: ${keyword});
      }
    }

    // Determine risk level (0-4 scale)
    let riskLevel = 0;
    if (riskScore >= 8) riskLevel = 4; // Imminent danger
    else if (riskScore >= 6) riskLevel = 3; // High risk
    else if (riskScore >= 4) riskLevel = 2; // Moderate risk
    else if (riskScore >= 2) riskLevel = 1; // Low risk

    return {
      riskLevel,
      riskScore,
      indicators,
      sentimentScore: sentimentAnalysis.score,
      confidence: Math.min(riskScore / 8, 1.0)
    };
  }

  async triggerIntervention(userId, crisisAnalysis) {
    // Notify counselors immediately
    await this.notifyCounselors(userId, crisisAnalysis);

    // Send crisis resources to user
    await this.sendCrisisResources(userId);

    // Log the incident for follow-up
    await this.logCrisisIncident(userId, crisisAnalysis);
  }

  async notifyCounselors(userId, crisisAnalysis) {
    // Implementation for immediate counselor notification
    const alertData = {
      userId,
      timestamp: new Date(),
      riskLevel: crisisAnalysis.riskLevel,
      indicators: crisisAnalysis.indicators,
      urgency: 'IMMEDIATE'
    };

    // Send to all available counselors
    // Implementation depends on notification system
  }
}

module.exports = new CrisisDetectionService();
`

## 4. DEPLOYMENT AND SCALABILITY

### Docker Configuration:
`# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5000
CMD ["node", "server.js"]
`

### Kubernetes Deployment:
`apiVersion: apps/v1
kind: Deployment
metadata:
  name: mental-health-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mental-health-backend
  template:
    metadata:
      labels:
        app: mental-health-backend
    spec:
      containers:
      - name: backend
        image: mental-health/backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: DB_HOST
          value: "postgresql-service"
        - name: REDIS_HOST
          value: "redis-service"
`

## 5. SECURITY AND PRIVACY

### Data Encryption:
`const crypto = require('crypto');

class EncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.secretKey = process.env.ENCRYPTION_KEY;
  }

  encrypt(text) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(this.algorithm, this.secretKey);
    cipher.setAAD(Buffer.from('mental-health-data'));

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return {
      iv: iv.toString('hex'),
      encryptedData: encrypted,
      authTag: authTag.toString('hex')
    };
  }

  decrypt(encryptedData) {
    const decipher = crypto.createDecipher(this.algorithm, this.secretKey);
    decipher.setAAD(Buffer.from('mental-health-data'));
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

    let decrypted = decipher.update(encryptedData.encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }
}
`

## 6. TESTING AND QUALITY ASSURANCE

### Unit Test Example:
`const { expect } = require('chai');
const CrisisDetectionService = require('../services/crisisDetection');

describe('Crisis Detection Service', () => {
  it('should detect high-risk suicide ideation', async () => {
    const message = 'I want to kill myself, there is no point in living';
    const result = await CrisisDetectionService.analyzeMessage(message);

    expect(result.riskLevel).to.equal(4);
    expect(result.indicators).to.include.members([
      'Crisis keyword detected: kill myself',
      'Crisis keyword detected: no point living'
    ]);
  });

  it('should detect Hindi crisis keywords', async () => {
    const message = 'मुझे मरना चाहता हूं';
    const result = await CrisisDetectionService.analyzeMessage(message, 'hi');

    expect(result.riskLevel).to.be.at.least(2);
  });
});
`

This implementation guide provides a comprehensive foundation for developing the Digital Mental Health Platform with proper AI integration, crisis detection, and cultural sensitivity for Indian students.