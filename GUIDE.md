# Kisan Slot: beginner guide (short copy; the full version is in the chat)
PART 1 - run on your laptop
1. Install Python from python.org. On the first screen TICK "Add python.exe to PATH".
2. Unzip kisan-slot-v4.zip. Open the folder.
3. Double-click run_windows.bat. Wait until you see "Running on http://127.0.0.1:5000".
4. Open Chrome and go to localhost:5000. Register with an Indian mobile number; the OTP is shown on screen in local mode.
5. Staff: click Centre Staff, PIN 1234, choose centre, Load queue.
6. Stop: click the black window and press Ctrl+C. To reset all data: delete procure.db.
PART 2 - put it online (Vercel + Neon + Fast2SMS)
1. Accounts: github.com, vercel.com (sign up with GitHub), neon.tech, fast2sms.com
2. GitHub: new repository, upload everything INSIDE the unzipped folder (app.py must be at the top level).
3. Neon: create project, copy the connection string (postgresql://...).
4. Fast2SMS: Dev API page, copy API key.
5. Vercel: Add New > Project > import the repository > Environment Variables:
   APP_ENV=production  STAFF_PIN=<secret>  DATABASE_URL=<neon string>  SMS_PROVIDER=fast2sms  FAST2SMS_KEY=<key>
6. Deploy. Check <your-link>/api/health shows "db":"postgres" and "sms":"fast2sms".
