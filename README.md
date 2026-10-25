# Kisan Slot v4
Indian-mobile-only registration + OTP, slot booking, live queue, real SMS, procurement tracking, payments.
Run on your laptop: double-click run_windows.bat (Windows) or run ./run_mac_linux.sh
Then open http://localhost:5000   (staff PIN: 1234 when running locally)
Full beginner guide: GUIDE.md
Tests: python test_all.py     (SQLite)   |   set DATABASE_URL=... then python test_all.py   (PostgreSQL)
Environment variables (for hosting): APP_ENV=production, STAFF_PIN, DATABASE_URL, SMS_PROVIDER=fast2sms, FAST2SMS_KEY
