# سير عمل: إعداد مشروع Zouaizia Nacer

## الهدف
تهيئة بيئة العمل لـ ZNOrchestrator

## المتطلبات المسبقة
- Python 3.9+
- Conductor Server (محلي أو سحابي)
- Antigravity IDE

## الخطوات

### Phase 1: Planning (5 دقائق)
- [ ] قراءة `.antigravity/rules.md`
- [ ] تحليل متطلبات المشروع
- [ ] تحديد الوكلاء المطلوبين
- [ ] إنشاء Plan Artifact

### Phase 2: Environment Setup (10 دقائق)
- [ ] إنشاء virtual environment
- [ ] تثبيت المتطلبات: `pip install -r requirements.txt`
- [ ] إعداد ملف `.env` من `.env.example`
- [ ] اختبار الاتصال بـ Conductor

### Phase 3: Core Installation (15 دقائق)
- [ ] نسخ الكود الأساسي من المستودع الأصلي
- [ ] إعادة بناء `Orchestrator` class
- [ ] إعداد `AgentManager`
- [ ] إعداد `WorkflowEngine`

### Phase 4: Agent Configuration (10 دقائق)
- [ ] إنشاء تعريفات الوكلاء في `.agent/`
- [ ] إعداد مهارات الوكلاء
- [ ] ربط الوكلاء بالـ Orchestrator

### Phase 5: Quality Setup (5 دقائق)
- [ ] إعداد Quality Gates
- [ ] إنشاء اختبارات أولية
- [ ] التحقق من التكامل

### Phase 6: Validation (5 دقائق)
- [ ] تشغيل اختبارات الوحدة
- [ ] اختبار Workflow بسيط
- [ ] التحقق من التوثيق

## الأوامر المسموحة
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/
python src/core/orchestrator.py --dry-run
```

## معايير النجاح
- جميع الاختبارات تمر
- Orchestrator يستجيب للأوامر
- الوكلاء يظهرون في `@agent list`
- لا أخطاء في الـ logs
