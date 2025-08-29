@echo off
echo ============================================================
echo βaspirin Mental Health AI - Automated Setup
echo ============================================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7+ first.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies. Please check your pip installation.
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Train the model (10-30 mins)
echo 🧠 Training your custom AI model. This may take 10-30 minutes...
python train.py

if errorlevel 1 (
    echo ❌ Training failed. Please check the error messages above.
    pause
    exit /b 1
)

echo ✅ Model training completed successfully!

REM Test the model
echo 🧪 Testing the trained model with sample input...
python inference.py

echo ============================================================
echo 🎉 Setup completed successfully!
echo.
echo Next steps:
echo 1. Start the AI server: python server.py
echo 2. Open your website index.html in a browser
echo 3. The chat should now be connected to your custom AI!
echo ============================================================
pause
