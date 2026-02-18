#!/bin/bash
# setup.sh - إعداد بيئة Zouaizia Nacer Orchestrator

set -e

echo "🚀 Setting up Zouaizia Nacer Orchestrator..."

# التحقق من Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# إنشاء البيئة الافتراضية
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# إعداد الملفات البيئية
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please configure it."
fi

# إنشاء الهيكل إذا لم يكن موجوداً
echo "🏗️ Creating directory structure..."
mkdir -p logs
mkdir -p data/workflows
mkdir -p data/agents

# التحقق من التثبيت
echo "✅ Running validation..."
python -c "from src.core.orchestrator import ZNOrchestrator; print('Import successful')"

echo "🎉 Setup complete! Activate with: source venv/bin/activate"
