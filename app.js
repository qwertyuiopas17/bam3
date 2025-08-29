// βaspirin Digital Mental Health Platform - FIXED Main Application Logic

// --- GOOGLE SHEET SCRIPT URL ---
const SCRIPT_URL = 'YOUR_GOOGLE_SHEET_WEB_APP_URL';

// --- Connect to the Python-SocketIO backend ---
const socket = io("http://localhost:3000");

socket.on("connect", () => {
    console.log("Successfully connected to the Python backend server with ID:", socket.id);
});

// Fixed AI response listener
socket.on("ai response", (data) => {
    console.log("AI Response Received:", data);
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.classList.add('hidden');
    }
    addMessage(data.message, 'bot');
    if (data.is_crisis) {
        showCrisisAlert();
    }
});

// --- TRANSLATIONS AND APP DATA ---
const translations = {
    en: {
        login: "Student Login",
        register: "Register",
        welcome_title: "Welcome to βaspirin",
        welcome_subtitle: "Your Digital Mental Health Support System",
        take_assessment: "Take Assessment",
        assessment_description: "Complete PHQ-9 and GAD-7 screenings to understand your mental health",
        ai_support_chat: "AI Support Chat",
        chat_description: "Get immediate support and coping strategies from our AI assistant",
        resource_library: "Resource Library",
        resources_description: "Access CBT modules, mindfulness practices, and educational content",
        book_appointment: "Book Appointment",
        booking_description: "Schedule sessions with qualified counselors and therapists",
        my_dashboard: "My Dashboard",
        dashboard_description: "Track your progress and view your mental health journey",
        admin_panel: "Admin Panel",
        admin_description: "Institutional analytics and monitoring (Demo)",
        back_to_home: "← Back to Home",
        register_title: "Create Student Account",
        full_name: "Full Name",
        email_address: "Email Address",
        select_college: "Select College",
        password: "Password",
        assessment_title: "Mental Health Assessment",
        assessment_subtitle: "Complete the PHQ-9 and GAD-7 questionnaires to get personalized insights",
        phq9_title: "PHQ-9 Depression Screening",
        phq9_description: "9 questions about depression symptoms over the past 2 weeks",
        start_phq9: "Start PHQ-9",
        gad7_title: "GAD-7 Anxiety Screening",
        gad7_description: "7 questions about anxiety symptoms over the past 2 weeks",
        start_gad7: "Start GAD-7",
        question: "Question",
        previous: "Previous",
        next: "Next",
        results_title: "Your Assessment Results",
        recommendations_title: "Personalized Recommendations",
        talk_to_ai: "Talk to AI Support",
        explore_resources: "Explore Resources",
        retake_assessment: "Take Another Assessment",
        ai_assistant_title: "AI Support Assistant",
        ai_assistant_subtitle: "Get immediate support and guidance. I'm here to help 24/7.",
        chat_welcome: "Hello! I'm your AI mental health assistant. How are you feeling today? I'm here to provide support and resources.",
        crisis_detected: "Crisis Detected:",
        crisis_message: "I'm very concerned about what you've shared. Please reach out for immediate help:",
        contact_helpline: "Contact Crisis Helpline",
        find_counselor: "Find Counselor",
        send: "Send",
        feeling_anxious: "I'm feeling anxious",
        cant_sleep: "I can't sleep",
        exam_stress: "I'm stressed about exams",
        feeling_lonely: "I feel lonely",
        resource_library_title: "Resource Library",
        resource_library_subtitle: "Access educational content, exercises, and tools for mental wellness",
        booking_title: "Book Appointment",
        booking_subtitle: "Schedule a session with our qualified mental health professionals",
        select_counselor: "Select a Counselor",
        select_date_time: "Select Date & Time",
        select_appointment_type: "Select Appointment Type",
        individual_session: "Individual Session",
        individual_session_desc: "One-on-one counseling session (50 minutes)",
        group_session: "Group Session",
        group_session_desc: "Group therapy session (60 minutes)",
        crisis_intervention: "Crisis Intervention",
        crisis_intervention_desc: "Immediate support (30 minutes)",
        confirm_appointment: "Confirm Appointment",
        counselor: "Counselor",
        date: "Date",
        time: "Time",
        type: "Type",
        confirm_booking_btn: "Confirm Appointment",
        my_dashboard_title: "My Dashboard",
        my_dashboard_subtitle: "Track your mental health journey and progress",
        mood_tracking: "Mood Tracking",
        assessment_history: "Assessment History",
        recent_activities: "Recent Activities",
        today: "Today",
        activity1: "Completed PHQ-9 assessment",
        yesterday: "Yesterday",
        activity2: "Used breathing exercise",
        "2_days_ago": "2 days ago",
        activity3: "Booked appointment with Dr. Johnson",
        quick_actions: "Quick Actions",
        chat_support: "Chat Support",
        book_session: "Book Session",
        admin_dashboard_title: "Admin Dashboard",
        admin_dashboard_subtitle: "Institutional analytics and monitoring (Demo)",
        total_students: "Total Students",
        active_users: "Active Users",
        crisis_alerts: "Crisis Alerts",
        appointments: "Appointments",
        usage_analytics: "Usage Analytics",
        risk_level_distribution: "Risk Level Distribution",
        crisis_monitoring: "Crisis Monitoring",
        medium_priority: "Medium Priority:",
        medium_priority_desc: "Student ID #STU456 - Elevated anxiety scores",
        high_priority: "High Priority:",
        high_priority_desc: "Crisis keywords detected in chat - Student ID #STU789",
        success: "Success!",
        booking_success_message: "Your appointment has been booked successfully.",
        registration_success_message: "Your account has been created. Your unique Student ID is:",
        close: "Close",
        student_login: "Student Login",
        student_id: "Student ID",
    },
    hi: {
        login: "छात्र लॉगिन",
        register: "पंजीकरण",
        welcome_title: "βaspirin में आपका स्वागत है",
        welcome_subtitle: "आपका डिजिटल मानसिक स्वास्थ्य सहायता सिस्टम",
        back_to_home: "← होम पर वापस",
        ai_assistant_title: "एआई सहायता सहायक",
        ai_assistant_subtitle: "तुरंत सहायता और मार्गदर्शन प्राप्त करें। मैं 24/7 मदद के लिए यहाँ हूँ।",
        send: "भेजें",
        feeling_anxious: "मुझे घबराहट हो रही है",
        cant_sleep: "मुझे नींद नहीं आ रही",
        exam_stress: "मैं परीक्षाओं को लेकर तनाव में हूँ",
        feeling_lonely: "मुझे अकेलापन महसूस हो रहा है",
        crisis_detected: "संकट का पता चला:",
        crisis_message: "आपने जो साझा किया है, उसे लेकर मैं बहुत चिंतित हूँ। कृपया तत्काल मदद के लिए संपर्क करें:",
        contact_helpline: "संकट हेल्पलाइन से संपर्क करें",
        find_counselor: "परामर्शदाता खोजें"
    },
};

const appData = {
    colleges: [
        "Indian Institute of Technology Madras",
        "Indian Institute of Technology Delhi",
        "Indian Institute of Technology Bombay",
        "Jadavpur University",
        "Vellore Institute of Technology",
        "National Institute of Technology Tiruchirappalli",
        "Birla Institute of Technology and Science, Pilani",
        "Amity University",
        "S.R.M. Institute of Science and Technology",
    ],
    phq9_questions: {
        en: [
            {
                id: "PHQ9_Q1",
                text: "Little interest or pleasure in doing things",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q2",
                text: "Feeling down, depressed, or hopeless",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q3",
                text: "Trouble falling or staying asleep, or sleeping too much",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q4",
                text: "Feeling tired or having little energy",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q5",
                text: "Poor appetite or overeating",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q6",
                text: "Feeling bad about yourself — or that you are a failure",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q7",
                text: "Trouble concentrating on things",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q8",
                text: "Moving or speaking slowly or being restless",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "PHQ9_Q9",
                text: "Thoughts that you would be better off dead",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            }
        ],
        hi: [
            {
                id: "PHQ9_Q1_HI",
                text: "चीजों में कम रुचि या आनंद महसूस करना",
                options: ["बिल्कुल नहीं (0)", "कई दिन (1)", "आधे से अधिक दिन (2)", "लगभग हर दिन (3)"]
            },
            {
                id: "PHQ9_Q2_HI",
                text: "उदास, अवसादग्रस्त या निराश महसूस करना",
                options: ["बिल्कुल नहीं (0)", "कई दिन (1)", "आधे से अधिक दिन (2)", "लगभग हर दिन (3)"]
            }
        ]
    },
    gad7_questions: {
        en: [
            {
                id: "GAD7_Q1",
                text: "Feeling nervous, anxious or on edge",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "GAD7_Q2",
                text: "Not being able to stop or control worrying",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "GAD7_Q3",
                text: "Worrying too much about different things",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "GAD7_Q4",
                text: "Trouble relaxing",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "GAD7_Q5",
                text: "Being so restless that it is hard to sit still",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "GAD7_Q6",
                text: "Becoming easily annoyed or irritable",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            },
            {
                id: "GAD7_Q7",
                text: "Feeling afraid as if something awful might happen",
                options: ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]
            }
        ],
        hi: [
            {
                id: "GAD7_Q1_HI",
                text: "घबराहट, चिंता या बेचैनी महसूस करना",
                options: ["बिल्कुल नहीं (0)", "कई दिन (1)", "आधे से अधिक दिन (2)", "लगभग हर दिन (3)"]
            }
        ]
    },
    counselors: [
        {
            id: "C001",
            name: "Dr. Sarah Johnson",
            specialization: "Anxiety and Depression",
            languages: ["English"],
            availability: ["Monday 10-12", "Wednesday 2-4", "Friday 10-12"]
        },
        {
            id: "C002",
            name: "Dr. Rajesh Kumar",
            specialization: "Student Counseling",
            languages: ["English", "Hindi"],
            availability: ["Tuesday 9-11", "Thursday 1-3"]
        }
    ],
    resources: [
        {
            category: "CBT Modules",
            category_hi: "सीबीटी मॉड्यूल",
            items: [
                {
                    title: "Thought Record Exercise",
                    title_hi: "विचार रिकॉर्ड व्यायाम",
                    description: "Track and analyze your thoughts and feelings",
                    description_hi: "अपने विचारों और भावनाओं को ट्रैक और विश्लेषण करें",
                    type: "Worksheet",
                    type_hi: "कार्यपत्रक"
                },
                {
                    title: "Cognitive Restructuring",
                    title_hi: "संज्ञानात्मक पुनर्गठन",
                    description: "Challenge negative thinking patterns",
                    description_hi: "नकारात्मक सोच पैटर्न को चुनौती दें",
                    type: "Module",
                    type_hi: "मॉड्यूल"
                }
            ]
        },
        {
            category: "Mindfulness & Relaxation",
            category_hi: "माइंडफुलनेस और आराम",
            items: [
                {
                    title: "Breathing Exercises for Anxiety",
                    title_hi: "चिंता के लिए साँस लेने के व्यायाम",
                    description: "Simple breathing techniques to manage anxiety",
                    description_hi: "चिंता को प्रबंधित करने के लिए सरल साँस लेने की तकनीक",
                    type: "Video - 5 min",
                    type_hi: "वीडियो - 5 मिनट"
                }
            ]
        }
    ]
};

// --- App State Variables ---
let currentLanguage = 'en';
let currentAssessment = null;
let currentQuestionIndex = 0;
let assessmentAnswers = [];
let selectedCounselor = null;
let selectedDate = null;
let selectedTime = null;
let bookingStep = 0;
let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    initializeCharts();
    generateCalendar();
    generateResources();
    generateCounselors();
    populateCollegeDropdown();
    updateUIText();
}

// --- UI Text and Translations ---
function updateUIText() {
    document.querySelectorAll('[data-key]').forEach(element => {
        const key = element.getAttribute('data-key');
        if (translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
}

// --- Event Listeners (FIXED) ---
function setupEventListeners() {
    setupNavigation();
    setupAssessment();
    setupChat();
    setupBooking();
    setupModal();
    setupRegistration();

    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', handleLanguageChange);
    }

    const loginBtn = document.getElementById('loginBtn');
    if (loginBtn) {
        loginBtn.addEventListener('click', () => showModalById('loginModal'));
    }

    const registerBtn = document.getElementById('registerBtn');
    if (registerBtn) {
        registerBtn.addEventListener('click', () => showScreen('registrationScreen'));
    }

    const closeLoginModal = document.getElementById('closeLoginModal');
    if (closeLoginModal) {
        closeLoginModal.addEventListener('click', () => hideModalById('loginModal'));
    }
}

// --- Navigation ---
function setupNavigation() {
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('click', () => {
            const targetScreen = card.getAttribute('data-screen');
            showScreen(targetScreen);
        });
    });

    document.querySelectorAll('.back-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetScreen = btn.getAttribute('data-target');
            showScreen(targetScreen || 'landingScreen');
        });
    });

    document.querySelectorAll('[data-screen]').forEach(btn => {
        if (!btn.classList.contains('back-btn') && !btn.classList.contains('feature-card')) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const targetScreen = btn.getAttribute('data-screen');
                if (targetScreen) showScreen(targetScreen);
            });
        }
    });

    const navBrand = document.querySelector('.nav__brand');
    if (navBrand) {
        navBrand.addEventListener('click', (e) => {
            e.preventDefault();
            showScreen('landingScreen');
        });
    }
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => screen.classList.remove('active'));
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) targetScreen.classList.add('active');
    window.scrollTo(0, 0);
}

// --- Assessment Setup (FIXED) ---
function setupAssessment() {
    document.querySelectorAll('.assessment-option button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const assessmentType = e.target.closest('.assessment-option').getAttribute('data-type');
            startAssessment(assessmentType);
        });
    });

    // FIXED: Proper event listener setup for assessment navigation
    const nextQuestionBtn = document.getElementById('nextQuestion');
    const prevQuestionBtn = document.getElementById('prevQuestion');
    const retakeAssessmentBtn = document.getElementById('retakeAssessment');

    if (nextQuestionBtn) {
        nextQuestionBtn.addEventListener('click', nextQuestion);
    }
    if (prevQuestionBtn) {
        prevQuestionBtn.addEventListener('click', prevQuestion);
    }
    if (retakeAssessmentBtn) {
        retakeAssessmentBtn.addEventListener('click', resetAssessment);
    }
}

function startAssessment(type) {
    currentAssessment = type;
    currentQuestionIndex = 0;
    assessmentAnswers = [];
    
    const questions = type === 'phq9' ? appData.phq9_questions[currentLanguage] : appData.gad7_questions[currentLanguage];
    const totalQuestions = document.getElementById('totalQuestions');
    if (totalQuestions) {
        totalQuestions.textContent = questions.length;
    }
    
    showAssessmentStep('assessmentQuestions');
    displayQuestion();
}

function displayQuestion() {
    const questions = currentAssessment === 'phq9' ? appData.phq9_questions[currentLanguage] : appData.gad7_questions[currentLanguage];
    const question = questions[currentQuestionIndex];
    
    const currentQuestion = document.getElementById('currentQuestion');
    const questionText = document.getElementById('questionText');
    const optionsContainer = document.getElementById('questionOptions');

    if (currentQuestion) currentQuestion.textContent = currentQuestionIndex + 1;
    if (questionText) questionText.textContent = question.text;

    if (optionsContainer) {
        optionsContainer.innerHTML = '';
        question.options.forEach((option, index) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'question-option';
            optionDiv.textContent = option;
            optionDiv.setAttribute('data-value', index);
            optionDiv.addEventListener('click', () => selectOption(optionDiv, index));
            
            if (assessmentAnswers[currentQuestionIndex] === index) {
                optionDiv.classList.add('selected');
            }
            
            optionsContainer.appendChild(optionDiv);
        });
    }

    updateProgress();
    updateNavigationButtons();
}

function selectOption(optionElement, value) {
    document.querySelectorAll('.question-option').forEach(opt => opt.classList.remove('selected'));
    optionElement.classList.add('selected');
    assessmentAnswers[currentQuestionIndex] = value;
    updateNavigationButtons();
}

function nextQuestion() {
    const questions = currentAssessment === 'phq9' ? appData.phq9_questions[currentLanguage] : appData.gad7_questions[currentLanguage];
    
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        displayQuestion();
    } else {
        calculateResults();
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        displayQuestion();
    }
}

function updateProgress() {
    const questions = currentAssessment === 'phq9' ? appData.phq9_questions[currentLanguage] : appData.gad7_questions[currentLanguage];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    
    const progressFill = document.querySelector('#assessmentQuestions .progress-fill');
    if (progressFill) {
        progressFill.style.width = progress + '%';
    }
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevQuestion');
    const nextBtn = document.getElementById('nextQuestion');
    
    if (prevBtn) prevBtn.disabled = currentQuestionIndex === 0;
    if (nextBtn) nextBtn.disabled = assessmentAnswers[currentQuestionIndex] === undefined;
}

function calculateResults() {
    const totalScore = assessmentAnswers.reduce((sum, answer) => sum + (answer || 0), 0);
    const maxScore = currentAssessment === 'phq9' ? 27 : 21;
    let riskLevel, riskClass, recommendations;

    if (currentAssessment === 'phq9') {
        if (totalScore <= 4) {
            riskLevel = 'Minimal Depression';
            riskClass = 'risk-minimal';
            recommendations = ['Continue with healthy lifestyle habits'];
        } else if (totalScore <= 9) {
            riskLevel = 'Mild Depression';
            riskClass = 'risk-mild';
            recommendations = ['Consider talking to a counselor', 'Practice stress management'];
        } else if (totalScore <= 14) {
            riskLevel = 'Moderate Depression';
            riskClass = 'risk-moderate';
            recommendations = ['Strongly recommend professional counseling', 'Use our AI chat support'];
        } else {
            riskLevel = 'Severe Depression';
            riskClass = 'risk-severe';
            recommendations = ['Immediate professional help is recommended', 'Contact our crisis helpline'];
        }
    } else {
        if (totalScore <= 4) {
            riskLevel = 'Minimal Anxiety';
            riskClass = 'risk-minimal';
            recommendations = ['Continue with healthy coping strategies'];
        } else if (totalScore <= 9) {
            riskLevel = 'Mild Anxiety';
            riskClass = 'risk-mild';
            recommendations = ['Learn anxiety management techniques', 'Practice breathing exercises'];
        } else if (totalScore <= 14) {
            riskLevel = 'Moderate Anxiety';
            riskClass = 'risk-moderate';
            recommendations = ['Professional counseling is recommended', 'Practice CBT techniques'];
        } else {
            riskLevel = 'Severe Anxiety';
            riskClass = 'risk-severe';
            recommendations = ['Immediate professional help is needed', 'Book an urgent counseling appointment'];
        }
    }

    displayResults(totalScore, maxScore, riskLevel, riskClass, recommendations);
}

function displayResults(score, maxScore, riskLevel, riskClass, recommendations) {
    const resultTitle = document.getElementById('resultTitle');
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreTotal = document.getElementById('scoreTotal');
    const riskElement = document.getElementById('riskLevel');
    const recommendationsList = document.getElementById('recommendationsList');

    if (resultTitle) resultTitle.textContent = currentAssessment === 'phq9' ? 'PHQ-9 Results' : 'GAD-7 Results';
    if (scoreNumber) scoreNumber.textContent = score;
    if (scoreTotal) scoreTotal.textContent = `/ ${maxScore}`;
    
    if (riskElement) {
        riskElement.textContent = riskLevel;
        riskElement.className = `risk-level ${riskClass}`;
    }

    if (recommendationsList) {
        recommendationsList.innerHTML = '';
        recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.textContent = rec;
            recommendationsList.appendChild(item);
        });
    }

    showAssessmentStep('assessmentResults');
}

function showAssessmentStep(stepId) {
    document.querySelectorAll('.assessment-step').forEach(step => step.classList.remove('active'));
    const targetStep = document.getElementById(stepId);
    if (targetStep) targetStep.classList.add('active');
}

function resetAssessment() {
    showAssessmentStep('assessmentSelection');
}

// --- Chat Setup (FIXED) ---
function setupChat() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendMessage');
    
    if (sendButton) sendButton.addEventListener('click', sendMessage);
    
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    document.querySelectorAll('.quick-response').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (chatInput) {
                chatInput.value = e.target.getAttribute('data-message');
                sendMessage();
            }
        });
    });

    const emergencyBtn = document.getElementById('contactHelpline');
    if (emergencyBtn) emergencyBtn.addEventListener('click', () => alert("Please call the crisis helpline immediately!"));

    const findCounselorBtn = document.getElementById('findCounselor');
    if (findCounselorBtn) findCounselorBtn.addEventListener('click', () => showScreen('bookingScreen'));
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';

    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) typingIndicator.classList.remove('hidden');

    socket.emit('chat message', { message: message, language: currentLanguage });

    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
}

// FIXED: Robust message adding function
function addMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) {
        console.error('Error: Chat messages container not found!');
        return;
    }

    const messageText = String(text || '').trim();
    if (messageText === '') {
        console.warn('Warning: addMessage was called with empty text.');
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);

    const paragraph = document.createElement('p');
    paragraph.textContent = messageText;
    messageElement.appendChild(paragraph);

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showCrisisAlert() {
    const crisisAlert = document.getElementById('crisisAlert');
    if (crisisAlert) crisisAlert.classList.remove('hidden');
}

// --- Resource Library ---
function generateResources() {
    const container = document.querySelector('#resourcesScreen .resources-categories');
    if (!container) return;

    container.innerHTML = '';
    appData.resources.forEach(category => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'resource-category';

        const title = document.createElement('h3');
        title.textContent = currentLanguage === 'hi' ? category.category_hi : category.category;
        categoryDiv.appendChild(title);

        const gridDiv = document.createElement('div');
        gridDiv.className = 'resource-grid';

        category.items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'resource-item';

            const itemTitle = document.createElement('h4');
            itemTitle.textContent = currentLanguage === 'hi' ? item.title_hi : item.title;

            const itemDesc = document.createElement('p');
            itemDesc.textContent = currentLanguage === 'hi' ? item.description_hi : item.description;

            const itemType = document.createElement('span');
            itemType.className = 'resource-type';
            itemType.textContent = currentLanguage === 'hi' ? item.type_hi : item.type;

            itemDiv.appendChild(itemTitle);
            itemDiv.appendChild(itemDesc);
            itemDiv.appendChild(itemType);
            gridDiv.appendChild(itemDiv);
        });

        categoryDiv.appendChild(gridDiv);
        container.appendChild(categoryDiv);
    });
}

// --- Counselors ---
function generateCounselors() {
    const container = document.getElementById('counselorList');
    if (!container) return;

    container.innerHTML = '';
    appData.counselors.forEach(counselor => {
        const card = document.createElement('div');
        card.className = 'counselor-card';
        card.setAttribute('data-counselor', counselor.id);
        
        card.innerHTML = `
            <div class="counselor-info">
                <h4>${counselor.name}</h4>
                <p>${counselor.specialization}</p>
                <p>Languages: ${counselor.languages.join(', ')}</p>
                <div class="availability">
                    ${counselor.availability.map(slot => `<span class="time-slot">${slot}</span>`).join('')}
                </div>
                <button class="btn btn-primary select-counselor">Select Counselor</button>
            </div>
        `;

        card.querySelector('.select-counselor').addEventListener('click', () => {
            selectCounselor(counselor);
        });

        container.appendChild(card);
    });
}

function selectCounselor(counselor) {
    selectedCounselor = counselor;
    document.querySelectorAll('.counselor-card').forEach(card => card.classList.remove('selected'));
    document.querySelector(`[data-counselor="${counselor.id}"]`).classList.add('selected');
    
    const nextStepBtn = document.getElementById('selectDateTime');
    if (nextStepBtn) nextStepBtn.disabled = false;
}

// --- Booking System ---
function setupBooking() {
    const selectDateTimeBtn = document.getElementById('selectDateTime');
    const confirmAppointmentBtn = document.getElementById('confirmAppointment');
    
    if (selectDateTimeBtn) {
        selectDateTimeBtn.addEventListener('click', () => {
            showBookingStep('dateTimeSelection');
        });
    }
    
    if (confirmAppointmentBtn) {
        confirmAppointmentBtn.addEventListener('click', confirmBooking);
    }
}

function showBookingStep(stepId) {
    document.querySelectorAll('.booking-step').forEach(step => step.classList.remove('active'));
    const targetStep = document.getElementById(stepId);
    if (targetStep) targetStep.classList.add('active');
}

function confirmBooking() {
    // Booking confirmation logic
    showModalById('successModal');
    const modalMessage = document.getElementById('modalMessage');
    if (modalMessage) {
        modalMessage.textContent = translations[currentLanguage].booking_success_message;
    }
}

// --- Modal Functions ---
function setupModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) hideModal(modal);
        });
    });

    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) hideModal(modal);
        });
    });
}

function showModalById(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'flex';
}

function hideModalById(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

function hideModal(modal) {
    modal.style.display = 'none';
}

// --- Registration ---
function setupRegistration() {
    const registerForm = document.getElementById('registrationForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
}

function handleRegistration(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const studentId = 'STU' + Math.random().toString(36).substr(2, 6).toUpperCase();
    
    showModalById('successModal');
    const modalMessage = document.getElementById('modalMessage');
    if (modalMessage) {
        modalMessage.textContent = `${translations[currentLanguage].registration_success_message} ${studentId}`;
    }
}

// --- College Dropdown ---
function populateCollegeDropdown() {
    const collegeSelect = document.getElementById('college');
    if (!collegeSelect) return;

    collegeSelect.innerHTML = '<option value="">Select College</option>';
    appData.colleges.forEach(college => {
        const option = document.createElement('option');
        option.value = college;
        option.textContent = college;
        collegeSelect.appendChild(option);
    });
}

// --- Calendar Generation ---
function generateCalendar() {
    const calendarContainer = document.getElementById('calendar');
    if (!calendarContainer) return;

    const date = new Date(currentYear, currentMonth);
    const firstDay = new Date(date.getFullYear(), date.getMonth(), 1).getDay();
    const lastDate = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();

    let calendarHTML = '<div class="calendar-header">';
    calendarHTML += `<button id="prevMonth">&lt;</button>`;
    calendarHTML += `<span>${date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>`;
    calendarHTML += `<button id="nextMonth">&gt;</button>`;
    calendarHTML += '</div><div class="calendar-grid">';

    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    weekdays.forEach(day => {
        calendarHTML += `<div class="calendar-weekday">${day}</div>`;
    });

    for (let i = 0; i < firstDay; i++) {
        calendarHTML += '<div class="calendar-day empty"></div>';
    }

    for (let day = 1; day <= lastDate; day++) {
        const isToday = new Date().toDateString() === new Date(currentYear, currentMonth, day).toDateString();
        calendarHTML += `<div class="calendar-day ${isToday ? 'today' : ''}" data-date="${day}">${day}</div>`;
    }

    calendarHTML += '</div>';
    calendarContainer.innerHTML = calendarHTML;

    // Add event listeners for calendar navigation
    document.getElementById('prevMonth')?.addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        generateCalendar();
    });

    document.getElementById('nextMonth')?.addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        generateCalendar();
    });

    // Add event listeners for date selection
    document.querySelectorAll('.calendar-day:not(.empty)').forEach(day => {
        day.addEventListener('click', (e) => {
            document.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('selected'));
            e.target.classList.add('selected');
            selectedDate = `${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}-${e.target.dataset.date.padStart(2, '0')}`;
        });
    });
}

// --- Charts Initialization ---
function initializeCharts() {
    // Placeholder for chart initialization
    console.log('Charts initialized');
}

// --- Language Change Handler ---
function handleLanguageChange(e) {
    currentLanguage = e.target.value;
    updateUIText();
    generateResources();
}

// --- Additional Helper Functions ---
function showNotification(message, type = 'info') {
    // Create and show notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}