"""Kisan Slot v4
Farmer registration (Indian mobile numbers only), slot booking, live queue, real SMS,
procurement tracking and payments. SQLite on your laptop, PostgreSQL when DATABASE_URL is set."""
import os, re, random, secrets, sqlite3, time, base64, urllib.request, urllib.parse, datetime as dt
from flask import Flask, request, jsonify, g
from page import INDEX_HTML

DATABASE_URL = os.environ.get("DATABASE_URL", "")
PG = DATABASE_URL.startswith("postgres")
DB = os.environ.get("DB_PATH", "procure.db")
STAFF_PIN = os.environ.get("STAFF_PIN", "1234")
PRODUCTION = os.environ.get("APP_ENV", "dev") == "production"
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "console").lower()      # console | fast2sms | twilio
if PRODUCTION and STAFF_PIN == "1234":
    raise SystemExit("Set a strong STAFF_PIN environment variable before running in production")
if PG:
    import psycopg2, psycopg2.extras

OTP_TTL_SEC, OTP_COOLDOWN_SEC, OTP_MAX_TRIES = 600, 30, 5
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
def now_ist(): return dt.datetime.now(IST)
def today_ist(): return now_ist().date()
def stamp(): return now_ist().isoformat(timespec="seconds")

app = Flask(__name__, static_folder=None)

FLOW = ["BOOKED", "CHECKED_IN", "WEIGHED", "QUALITY_PASSED", "PROCURED", "PAYMENT_INITIATED", "PAID"]
TERMINAL = {"PAID", "REJECTED", "CANCELLED", "NO_SHOW"}
IN_QUEUE = ("BOOKED", "CHECKED_IN", "WEIGHED", "QUALITY_PASSED")
WINDOWS = [("09:00", "11:00"), ("11:00", "13:00"), ("14:00", "16:00")]
MAX_QTY = 2000   # quintals per booking

# ---------- validation helpers ----------
def norm_phone(raw):
    """Return a 10-digit Indian mobile number (starts with 6-9) or None.
    Accepts 98765 43210, 9876543210, 09876543210, 919876543210, +91 98765 43210, 0091..."""
    d = re.sub(r"[\s\-()]", "", str(raw or ""))
    if d.startswith("+"):
        if not d.startswith("+91"): return None
        d = d[3:]
    elif d.startswith("0091"): d = d[4:]
    elif len(d) == 12 and d.startswith("91"): d = d[2:]
    elif len(d) == 11 and d.startswith("0"): d = d[1:]
    if not re.fullmatch(r"[6-9]\d{9}", d): return None
    if len(set(d)) == 1: return None            # 9999999999 etc. are not real numbers
    return d

def mask_account(acct): return ("X" * max(len(acct) - 4, 0) + acct[-4:]) if acct else ""
def money(n): return f"{float(n):,.2f}"
def num(n): return f"{float(n):g}"
def body(): return request.get_json(silent=True) or {}
NAME_RE = re.compile(r"[A-Za-z][A-Za-z .'\-]{1,59}")
PLACE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .,'\-]{1,59}")

# ---------- database helpers (SQLite + PostgreSQL) ----------
def db():
    if "db" not in g:
        if PG: g.db = psycopg2.connect(DATABASE_URL)
        else:
            g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

def _sql(s): return s.replace("?", "%s") if PG else s
def _cur(con): return con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) if PG else con.cursor()

def q(sql, args=(), one=False):
    cur = _cur(db()); cur.execute(_sql(sql), args); rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows

def run(sql, args=()):
    con = db(); cur = _cur(con); cur.execute(_sql(sql), args); con.commit()

SCHEMA = """
CREATE TABLE IF NOT EXISTS centres(id INTEGER PRIMARY KEY, name TEXT, district TEXT, crop TEXT,
  msp_per_qtl REAL, min_per_farmer INTEGER DEFAULT 8, lanes INTEGER DEFAULT 2);
CREATE TABLE IF NOT EXISTS farmers(id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE, village TEXT,
  crop TEXT, land_acres REAL, otp TEXT, otp_sent REAL DEFAULT 0, otp_tries INTEGER DEFAULT 0, token TEXT,
  bank_holder TEXT, bank_account TEXT, bank_ifsc TEXT);
CREATE TABLE IF NOT EXISTS slots(id INTEGER PRIMARY KEY, centre_id INTEGER, date TEXT, start TEXT, "end" TEXT, capacity INTEGER);
CREATE UNIQUE INDEX IF NOT EXISTS ux_slot ON slots(centre_id, date, start);
CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY, farmer_id INTEGER, slot_id INTEGER, token_no INTEGER,
  status TEXT, est_qty REAL, final_qty REAL, amount REAL, near_notified INTEGER DEFAULT 0, created TEXT, updated TEXT);
CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY, booking_id INTEGER UNIQUE, farmer_id INTEGER, amount REAL,
  status TEXT, reference TEXT, method TEXT, created TEXT, updated TEXT, paid_at TEXT);
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, farmer_id INTEGER, message TEXT, channel TEXT, created TEXT);
"""
EXTRA_COLUMNS = [("farmers", "bank_holder", "TEXT"), ("farmers", "bank_account", "TEXT"), ("farmers", "bank_ifsc", "TEXT")]

def init_db():
    con = psycopg2.connect(DATABASE_URL) if PG else sqlite3.connect(DB)
    if PG: con.autocommit = True
    cur = con.cursor()
    schema = SCHEMA.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY").replace("REAL", "DOUBLE PRECISION") if PG else SCHEMA
    for stmt in schema.split(";"):
        if stmt.strip(): cur.execute(stmt)
    for t, c, ty in EXTRA_COLUMNS:            # upgrade databases made by older versions
        try: cur.execute(f"ALTER TABLE {t} ADD COLUMN {c} {ty}")
        except Exception: pass
    cur.execute("SELECT 1 FROM centres LIMIT 1")
    if not cur.fetchone():
        ph = "%s" if PG else "?"
        for c in [("Erode APMC Procurement Centre", "Erode", "Paddy", 2320),
                  ("Salem DPC Centre", "Salem", "Paddy", 2320),
                  ("Karur Wheat Mandi", "Karur", "Wheat", 2425)]:
            cur.execute(f"INSERT INTO centres(name,district,crop,msp_per_qtl) VALUES({ph},{ph},{ph},{ph})", c)
    if not PG: con.commit()
    con.close()

def ensure_slots(date):
    """Create the day's slots when first asked for (today .. today+7)."""
    try: d = dt.date.fromisoformat(date)
    except Exception: return
    if not (today_ist() <= d <= today_ist() + dt.timedelta(days=7)): return
    for c in q("SELECT id FROM centres"):
        if q("SELECT 1 FROM slots WHERE centre_id=? AND date=?", (c["id"], date), one=True): continue
        for s, e in WINDOWS:
            run('INSERT INTO slots(centre_id,date,start,"end",capacity) VALUES(?,?,?,?,20) ON CONFLICT DO NOTHING',
                (c["id"], date, s, e))

# ---------- SMS ----------
def _post(url, data, headers):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=6) as r:
        return r.status, r.read().decode()

def send_sms(phone, text):
    """Sent immediately (not in a background thread) so it also works on Vercel."""
    print(f"[SMS -> {phone}] {text}")
    if SMS_PROVIDER == "console": return
    try:
        if SMS_PROVIDER == "fast2sms":
            status, resp = _post("https://www.fast2sms.com/dev/bulkV2",
                                 {"route": "q", "message": text, "numbers": phone, "flash": "0"},
                                 {"authorization": os.environ["FAST2SMS_KEY"]})
            ok = status < 300 and '"return":false' not in resp.replace(" ", "")
        elif SMS_PROVIDER == "twilio":
            sid, tok = os.environ["TWILIO_SID"], os.environ["TWILIO_TOKEN"]
            auth = base64.b64encode(f"{sid}:{tok}".encode()).decode()
            status, resp = _post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                                 {"To": "+91" + phone, "From": os.environ["TWILIO_FROM"], "Body": text},
                                 {"Authorization": "Basic " + auth})
            ok = status < 300
        else:
            return
        print(f"[SMS {SMS_PROVIDER} -> {phone}] {'SENT' if ok else 'REJECTED'}: {resp[:150]}")
    except Exception as e:      # an SMS problem must never break booking or payment
        print(f"[SMS {SMS_PROVIDER} -> {phone}] FAILED: {e}")

def notify(farmer_id, text):
    f = q("SELECT phone FROM farmers WHERE id=?", (farmer_id,), one=True)
    run("INSERT INTO notifications(farmer_id,message,channel,created) VALUES(?,?,?,?)", (farmer_id, text, "SMS+APP", stamp()))
    if f: send_sms(f["phone"], text)

# ---------- auth ----------
class StaffDenied(Exception): pass

def current_farmer():
    tok = request.headers.get("X-Token", "")
    return q("SELECT * FROM farmers WHERE token=?", (tok,), one=True) if tok else None

def need_farmer():
    f = current_farmer()
    if not f: raise PermissionError
    return f

def need_staff():
    if (request.headers.get("X-Staff-Pin") or "").strip() != STAFF_PIN: raise StaffDenied

@app.errorhandler(PermissionError)
def _denied(_): return jsonify(error="Please log in again"), 401
@app.errorhandler(StaffDenied)
def _staff_denied(_): return jsonify(error="Wrong staff PIN"), 401

# ---------- queue ----------
def queue_for(centre_id, date):
    return q("""SELECT b.*, s.start, s."end" FROM bookings b JOIN slots s ON s.id=b.slot_id
                WHERE s.centre_id=? AND s.date=? AND b.status IN %s ORDER BY s.start, b.token_no""" % (IN_QUEUE,),
             (centre_id, date))

def position_and_eta(b):
    s = q("SELECT * FROM slots WHERE id=?", (b["slot_id"],), one=True)
    c = q("SELECT * FROM centres WHERE id=?", (s["centre_id"],), one=True)
    ids = [r["id"] for r in queue_for(c["id"], s["date"])]
    if b["id"] not in ids: return None, None
    pos = ids.index(b["id"]) + 1
    return pos, round(pos * c["min_per_farmer"] / c["lanes"])

def alert_near_turn(centre_id, date):
    for i, r in enumerate(queue_for(centre_id, date), start=1):
        if i <= 3 and not r["near_notified"]:
            notify(r["farmer_id"], f"Your turn is near: {i} farmer(s) ahead including you. Please reach the centre.")
            run("UPDATE bookings SET near_notified=1 WHERE id=?", (r["id"],))

# ---------- farmer API ----------
@app.post("/api/register")
def register():
    d = body()
    phone = norm_phone(d.get("phone"))
    name, village = (d.get("name") or "").strip(), (d.get("village") or "").strip()
    if not phone: return jsonify(error="Enter a valid Indian mobile number: 10 digits starting with 6, 7, 8 or 9"), 400
    if not NAME_RE.fullmatch(name): return jsonify(error="Enter your name (letters only, 2 to 60 characters)"), 400
    if not PLACE_RE.fullmatch(village): return jsonify(error="Enter your village name"), 400
    if d.get("crop") not in ("Paddy", "Wheat"): return jsonify(error="Choose a crop"), 400
    try: land = float(d.get("land_acres") or 0)
    except ValueError: return jsonify(error="Land size must be a number"), 400
    if not (0 <= land <= 10000): return jsonify(error="Land size must be between 0 and 10000 acres"), 400
    if q("SELECT 1 FROM farmers WHERE phone=?", (phone,), one=True):
        return jsonify(error="This number is already registered. Please log in."), 409
    run("INSERT INTO farmers(name,phone,village,crop,land_acres) VALUES(?,?,?,?,?)", (name, phone, village, d["crop"], land))
    return jsonify(message="Registered", phone=phone)

@app.post("/api/login")
def login():
    phone = norm_phone(body().get("phone"))
    if not phone: return jsonify(error="Enter a valid Indian mobile number: 10 digits starting with 6, 7, 8 or 9"), 400
    f = q("SELECT * FROM farmers WHERE phone=?", (phone,), one=True)
    if not f: return jsonify(error="This number is not registered. Please register first."), 404
    wait = OTP_COOLDOWN_SEC - (time.time() - (f["otp_sent"] or 0))
    if wait > 0: return jsonify(error=f"Please wait {int(wait) + 1} seconds before asking for another OTP"), 429
    otp = f"{random.randint(0, 999999):06d}"
    run("UPDATE farmers SET otp=?, otp_sent=?, otp_tries=0 WHERE id=?", (otp, time.time(), f["id"]))
    send_sms(phone, f"{otp} is your Kisan Slot OTP. Valid for 10 minutes. Do not share it with anyone.")
    out = dict(message="OTP sent to your mobile")
    if os.environ.get("SHOW_DEMO_OTP", "0" if PRODUCTION else "1") == "1": out["demo_otp"] = otp
    return jsonify(out)

@app.post("/api/verify")
def verify():
    d = body(); phone = norm_phone(d.get("phone"))
    f = q("SELECT * FROM farmers WHERE phone=?", (phone,), one=True) if phone else None
    if not f or not f["otp"] or time.time() - (f["otp_sent"] or 0) > OTP_TTL_SEC:
        return jsonify(error="OTP expired. Please ask for a new one"), 401
    if (f["otp_tries"] or 0) >= OTP_MAX_TRIES:
        return jsonify(error="Too many wrong tries. Please ask for a new OTP"), 429
    if f["otp"] != str(d.get("otp") or "").strip():
        run("UPDATE farmers SET otp_tries=COALESCE(otp_tries,0)+1 WHERE id=?", (f["id"],))
        return jsonify(error="Wrong OTP"), 401
    tok = secrets.token_hex(16)
    run("UPDATE farmers SET token=?, otp=NULL WHERE id=?", (tok, f["id"]))
    return jsonify(token=tok)

def profile(f):
    bank = None
    if f["bank_account"]:
        bank = dict(holder=f["bank_holder"], account=mask_account(f["bank_account"]), ifsc=f["bank_ifsc"])
    return dict(name=f["name"], phone=f["phone"], village=f["village"], crop=f["crop"], bank=bank)

@app.get("/api/me")
def me(): return jsonify(profile(need_farmer()))

@app.post("/api/bank")
def save_bank():
    f = need_farmer(); d = body()
    holder = (d.get("holder") or "").strip()
    acct = re.sub(r"\s", "", str(d.get("account") or ""))
    acct2 = re.sub(r"\s", "", str(d.get("account2") or ""))
    ifsc = (d.get("ifsc") or "").strip().upper()
    if not NAME_RE.fullmatch(holder): return jsonify(error="Enter the account holder name as in the bank"), 400
    if not re.fullmatch(r"\d{9,18}", acct): return jsonify(error="Account number must be 9 to 18 digits"), 400
    if acct != acct2: return jsonify(error="The two account numbers do not match"), 400
    if not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc): return jsonify(error="IFSC must look like SBIN0001234"), 400
    run("UPDATE farmers SET bank_holder=?, bank_account=?, bank_ifsc=? WHERE id=?", (holder, acct, ifsc, f["id"]))
    return jsonify(message="Bank details saved", me=profile(q("SELECT * FROM farmers WHERE id=?", (f["id"],), one=True)))

@app.get("/api/payments")
def my_payments():
    f = need_farmer()
    rows = q("""SELECT p.*, b.token_no, b.final_qty, s.date, c.name AS centre FROM payments p
                JOIN bookings b ON b.id=p.booking_id JOIN slots s ON s.id=b.slot_id JOIN centres c ON c.id=s.centre_id
                WHERE p.farmer_id=? ORDER BY p.id DESC""", (f["id"],))
    pays = [dict(r) for r in rows]
    paid = sum(p["amount"] for p in pays if p["status"] == "PAID")
    pending = sum(p["amount"] for p in pays if p["status"] != "PAID")
    return jsonify(payments=pays, paid_total=paid, pending_total=pending, bank=profile(f)["bank"])

@app.get("/api/dates")
def dates(): return jsonify([(today_ist() + dt.timedelta(days=i)).isoformat() for i in range(4)])

@app.get("/api/centres")
def centres():
    out, today = [], today_ist().isoformat()
    for c in q("SELECT * FROM centres ORDER BY id"):
        waiting = len(queue_for(c["id"], today))
        out.append(dict(c, waiting_today=waiting, est_wait_min=round(waiting * c["min_per_farmer"] / c["lanes"])))
    return jsonify(out)

@app.get("/api/slots")
def slots():
    cid, date = request.args.get("centre_id", ""), request.args.get("date", "")
    if not cid.isdigit(): return jsonify([])
    ensure_slots(date)
    rows = q("""SELECT s.*, (SELECT COUNT(*) FROM bookings b WHERE b.slot_id=s.id AND b.status!='CANCELLED') AS booked
                FROM slots s WHERE centre_id=? AND date=? ORDER BY start""", (cid, date))
    return jsonify([dict(r, available=r["capacity"] - r["booked"]) for r in rows])

@app.post("/api/bookings")
def book():
    f = need_farmer(); d = body()
    try: est = float(d.get("est_qty"))
    except (TypeError, ValueError): est = 0
    if not (0 < est <= MAX_QTY): return jsonify(error=f"Enter your crop quantity in quintals (1 to {MAX_QTY})"), 400
    s = q("SELECT * FROM slots WHERE id=?", (d.get("slot_id"),), one=True)
    if not s: return jsonify(error="Slot not found"), 404
    if q("""SELECT 1 FROM bookings b JOIN slots s ON s.id=b.slot_id WHERE b.farmer_id=? AND s.date=?
            AND b.status NOT IN ('CANCELLED','REJECTED','NO_SHOW','PAID')""", (f["id"], s["date"]), one=True):
        return jsonify(error="You already have an active booking that day"), 409
    con = db(); cur = _cur(con)
    try:   # lock the slot so two farmers cannot take the last seat
        if PG: cur.execute("SELECT id FROM slots WHERE id=%s FOR UPDATE", (s["id"],))
        else: con.execute("BEGIN IMMEDIATE")
        cur.execute(_sql("SELECT COUNT(*) AS c FROM bookings WHERE slot_id=? AND status!='CANCELLED'"), (s["id"],))
        if cur.fetchone()["c"] >= s["capacity"]:
            con.rollback(); return jsonify(error="This slot is full. Please choose another"), 409
        cur.execute(_sql("SELECT COALESCE(MAX(token_no),0) AS m FROM bookings WHERE slot_id=?"), (s["id"],))
        tok_no = cur.fetchone()["m"] + 1
        now = stamp()
        cur.execute(_sql("INSERT INTO bookings(farmer_id,slot_id,token_no,status,est_qty,created,updated) VALUES(?,?,?,?,?,?,?)")
                    + (" RETURNING id" if PG else ""), (f["id"], s["id"], tok_no, "BOOKED", est, now, now))
        bid = cur.fetchone()["id"] if PG else cur.lastrowid
        con.commit()
    except Exception:
        con.rollback(); raise
    c = q("SELECT name FROM centres WHERE id=?", (s["centre_id"],), one=True)
    notify(f["id"], f"Booking confirmed at {c['name']} on {s['date']} {s['start']}-{s['end']}. Token #{tok_no}.")
    return jsonify(booking_id=bid, token_no=tok_no)

@app.get("/api/bookings/mine")
def mine():
    f = need_farmer()
    rows = q("""SELECT b.*, s.date, s.start, s."end", c.name AS centre FROM bookings b
                JOIN slots s ON s.id=b.slot_id JOIN centres c ON c.id=s.centre_id
                WHERE b.farmer_id=? ORDER BY b.id DESC""", (f["id"],))
    out = []
    for r in rows:
        pos, eta = position_and_eta(r)
        out.append(dict(r, queue_position=pos, eta_min=eta, flow=FLOW))
    return jsonify(out)

@app.post("/api/bookings/<int:bid>/cancel")
def cancel(bid):
    f = need_farmer()
    b = q("SELECT * FROM bookings WHERE id=? AND farmer_id=?", (bid, f["id"]), one=True)
    if not b or b["status"] != "BOOKED": return jsonify(error="Only a booking that has not started can be cancelled"), 400
    run("UPDATE bookings SET status='CANCELLED' WHERE id=?", (bid,))
    return jsonify(message="Cancelled")

@app.get("/api/notifications")
def notifications():
    f = need_farmer()
    return jsonify([dict(r) for r in q(
        "SELECT message, created FROM notifications WHERE farmer_id=? ORDER BY id DESC LIMIT 30", (f["id"],))])

# ---------- centre staff API ----------
@app.get("/api/staff/check")
def staff_check():
    need_staff(); return jsonify(message="PIN correct")

@app.get("/api/staff/queue")
def staff_queue():
    need_staff()
    cid = request.args.get("centre_id", ""); date = request.args.get("date", today_ist().isoformat())
    if not cid.isdigit(): return jsonify(error="Choose a centre"), 400
    rows = q("""SELECT b.id, b.token_no, b.status, b.est_qty, b.final_qty, b.amount, s.start, f.name, f.phone, f.village,
                p.status AS pay_status, p.reference AS pay_ref, (f.bank_account IS NOT NULL) AS has_bank
                FROM bookings b JOIN slots s ON s.id=b.slot_id JOIN farmers f ON f.id=b.farmer_id
                LEFT JOIN payments p ON p.booking_id=b.id
                WHERE s.centre_id=? AND s.date=? AND b.status!='CANCELLED' ORDER BY s.start, b.token_no""", (cid, date))
    return jsonify([dict(r, has_bank=bool(r["has_bank"])) for r in rows])

@app.get("/api/staff/summary")
def staff_summary():
    need_staff()
    cid = request.args.get("centre_id", ""); date = request.args.get("date", today_ist().isoformat())
    if not cid.isdigit(): return jsonify(error="Choose a centre"), 400
    out = dict(farmers=0, procured_qtl=0, paid=0, pending=0)
    for r in q("""SELECT b.status, b.final_qty, p.status AS ps, p.amount FROM bookings b JOIN slots s ON s.id=b.slot_id
                  LEFT JOIN payments p ON p.booking_id=b.id WHERE s.centre_id=? AND s.date=? AND b.status!='CANCELLED'""", (cid, date)):
        out["farmers"] += 1
        if r["status"] in ("PROCURED", "PAYMENT_INITIATED", "PAID"): out["procured_qtl"] += r["final_qty"] or 0
        if r["ps"] == "PAID": out["paid"] += r["amount"] or 0
        elif r["ps"]: out["pending"] += r["amount"] or 0
    return jsonify(out)

def set_payment(b, amount, status, ref=None):
    p = q("SELECT * FROM payments WHERE booking_id=?", (b["id"],), one=True)
    now = stamp()
    if not p:
        run("""INSERT INTO payments(booking_id,farmer_id,amount,status,reference,method,created,updated,paid_at)
               VALUES(?,?,?,?,?,?,?,?,?)""", (b["id"], b["farmer_id"], amount, status, ref, "BANK_TRANSFER", now, now,
                                               now if status == "PAID" else None))
    else:
        run("UPDATE payments SET amount=?, status=?, reference=COALESCE(?,reference), updated=?, paid_at=? WHERE id=?",
            (amount, status, ref, now, now if status == "PAID" else p["paid_at"], p["id"]))

@app.post("/api/staff/bookings/<int:bid>/status")
def staff_status(bid):
    need_staff(); d = body(); new = d.get("status")
    b = q("""SELECT b.*, s.centre_id, s.date, c.name AS centre, c.msp_per_qtl FROM bookings b
             JOIN slots s ON s.id=b.slot_id JOIN centres c ON c.id=s.centre_id WHERE b.id=?""", (bid,), one=True)
    if not b: return jsonify(error="Booking not found"), 404
    cur = b["status"]
    if cur in TERMINAL: return jsonify(error="This booking is already closed"), 400
    if new in ("REJECTED", "NO_SHOW"):
        if cur not in IN_QUEUE: return jsonify(error="Too late to reject after procurement"), 400
    elif new in FLOW:
        if FLOW.index(new) != FLOW.index(cur) + 1:
            return jsonify(error=f"Next step must be {FLOW[FLOW.index(cur) + 1].replace('_', ' ')}"), 400
    else: return jsonify(error="Unknown status"), 400
    f = q("SELECT * FROM farmers WHERE id=?", (b["farmer_id"],), one=True)
    qty, amt, ref = b["final_qty"] or b["est_qty"] or 0, b["amount"], None
    if new == "WEIGHED":
        try: qty = float(d.get("qty"))
        except (TypeError, ValueError): qty = 0
        if not (0 < qty <= MAX_QTY): return jsonify(error=f"Enter the weighed quantity in quintals (1 to {MAX_QTY})"), 400
    if new == "PROCURED": amt = round(qty * b["msp_per_qtl"], 2)
    if new == "PAYMENT_INITIATED" and not f["bank_account"]:
        return jsonify(error="This farmer has not added bank details yet. Ask them to open the Payments tab."), 400
    if new == "PAID":
        ref = re.sub(r"[^A-Za-z0-9]", "", str(d.get("reference") or ""))[:30] or ("KS" + now_ist().strftime("%y%m%d%H%M%S") + str(random.randint(100, 999)))
    run("UPDATE bookings SET status=?, final_qty=?, amount=?, updated=? WHERE id=?", (new, qty, amt, stamp(), bid))
    if new == "PROCURED": set_payment(b, amt, "PENDING")
    elif new == "PAYMENT_INITIATED": set_payment(b, amt, "INITIATED")
    elif new == "PAID": set_payment(b, amt, "PAID", ref)
    acct = mask_account(f["bank_account"])
    msgs = {
        "CHECKED_IN": f"Checked in at {b['centre']}. Token #{b['token_no']}. Please wait for your turn.",
        "WEIGHED": f"Your produce was weighed: {num(qty)} qtl. Quality check next.",
        "QUALITY_PASSED": "Quality check passed. Procurement is being finalised.",
        "PROCURED": f"Procurement complete: {num(qty)} qtl, amount Rs {money(amt or 0)}."
                    + ("" if f["bank_account"] else " Please add your bank details in the app to receive payment."),
        "PAYMENT_INITIATED": f"Payment of Rs {money(amt or 0)} initiated to A/c {acct}.",
        "PAID": f"Payment of Rs {money(amt or 0)} credited to A/c {acct}. Ref {ref}. Thank you!",
        "REJECTED": "Your produce was rejected at quality check. Please contact the centre.",
        "NO_SHOW": "You missed your slot. Please book again.",
    }
    notify(b["farmer_id"], msgs[new])
    alert_near_turn(b["centre_id"], b["date"])
    return jsonify(message="Updated", status=new, amount=amt, reference=ref)

@app.post("/api/staff/sms-test")
def sms_test():
    need_staff()
    phone = norm_phone(body().get("phone"))
    if not phone: return jsonify(error="Enter a valid Indian mobile number"), 400
    send_sms(phone, "Kisan Slot test: SMS notifications are working.")
    return jsonify(message=f"Test SMS sent to +91 {phone} using '{SMS_PROVIDER}'. Check your phone.")

@app.get("/api/health")
def health():
    return jsonify(ok=True, version=4, db="postgres" if PG else "sqlite", sms=SMS_PROVIDER,
                   staff_pin_is_default=(STAFF_PIN == "1234"))

@app.get("/")
def home(): return INDEX_HTML, 200, {"Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-cache"}

if not PRODUCTION: print(f"[STAFF] Centre staff PIN is: {STAFF_PIN}")
init_db()      # also runs when Vercel imports the app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=not PRODUCTION)
