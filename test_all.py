"""End-to-end test. SQLite by default; set DATABASE_URL to test PostgreSQL."""
import os, sys
if not os.environ.get("DATABASE_URL"):
    os.environ["DB_PATH"] = "/tmp/k4.db"
    if os.path.exists("/tmp/k4.db"): os.remove("/tmp/k4.db")
import app as A
c = A.app.test_client(); H = {"X-Staff-Pin": "1234"}
n = 0
def ok(name, cond):
    global n; n += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: sys.exit(1)
def post(url, **kw): return c.post(url, json=kw.pop("json", {}), headers=kw.pop("h", {}))

# ---- Indian phone numbers only ----
good = {"9876543210": "9876543210", "98765 43210": "9876543210", "+91 98765 43210": "9876543210",
        "919876543210": "9876543210", "09876543210": "9876543210", "0091-9876543210": "9876543210", "6000000001": "6000000001"}
for raw, want in good.items(): ok(f"accept {raw!r}", A.norm_phone(raw) == want)
for bad in ["5876543210", "987654321", "98765432101", "+1 9876543210", "+44 7911123456", "abcdefghij", "", None, "9999999999", "0000000000", "+91 12345 67890"]:
    ok(f"reject {bad!r}", A.norm_phone(bad) is None)
r = post("/api/register", json=dict(name="Bad", phone="+1 2025550123", village="Perundurai", crop="Paddy"))
ok("register rejects non-Indian number", r.status_code == 400)
r = post("/api/login", json=dict(phone="12345"))
ok("login rejects bad number", r.status_code == 400)
ok("register rejects XSS-style name", post("/api/register", json=dict(name="<img src=x onerror=alert(1)>", phone="9000000009", village="Perundurai", crop="Paddy")).status_code == 400)

# ---- register / otp ----
def farmer(phone, name):
    r = post("/api/register", json=dict(name=name, phone=phone, village="Perundurai", crop="Paddy", land_acres=2))
    ok(f"register {name} with {phone!r}", r.status_code == 200 and r.json["phone"] == A.norm_phone(phone))
    return c.post("/api/login", json=dict(phone=phone)).json["demo_otp"]
o1 = farmer("+91 90000 00001", "Ravi Kumar")
ok("duplicate number (other format) blocked", post("/api/register", json=dict(name="Ravi", phone="9000000001", village="Perundurai", crop="Paddy")).status_code == 409)
ok("otp cooldown", c.post("/api/login", json=dict(phone="9000000001")).status_code == 429)
for _ in range(5): c.post("/api/verify", json=dict(phone="9000000001", otp="000000"))
ok("5 wrong otps lock", c.post("/api/verify", json=dict(phone="9000000001", otp=o1)).status_code == 429)
with A.app.app_context(): A.run("UPDATE farmers SET otp_tries=0 WHERE phone=?", ("9000000001",))
r = c.post("/api/verify", json=dict(phone="90000 00001", otp=o1)); ok("verify otp (spaced number)", r.status_code == 200)
T1 = {"X-Token": r.json["token"]}
o2 = farmer("9000000002", "Meena Devi")
T2 = {"X-Token": c.post("/api/verify", json=dict(phone="9000000002", otp=o2)).json["token"]}
ok("/api/me works", c.get("/api/me", headers=T1).json["phone"] == "9000000001")

# ---- booking + queue ----
date = c.get("/api/dates").json[0]
sl = c.get(f"/api/slots?centre_id=1&date={date}").json
ok("3 slots", len(sl) == 3)
ok("booking needs a quantity", c.post("/api/bookings", json=dict(slot_id=sl[0]["id"]), headers=T1).status_code == 400)
ok("booking rejects absurd quantity", c.post("/api/bookings", json=dict(slot_id=sl[0]["id"], est_qty=99999), headers=T1).status_code == 400)
b1 = c.post("/api/bookings", json=dict(slot_id=sl[0]["id"], est_qty=30), headers=T1).json
b2 = c.post("/api/bookings", json=dict(slot_id=sl[0]["id"], est_qty=20), headers=T2).json
ok("tokens 1 and 2", (b1["token_no"], b2["token_no"]) == (1, 2))
ok("second booking same day blocked", c.post("/api/bookings", json=dict(slot_id=sl[1]["id"], est_qty=5), headers=T1).status_code == 409)
ok("farmer 2 is #2", c.get("/api/bookings/mine", headers=T2).json[0]["queue_position"] == 2)

# ---- staff flow with payments ----
st = lambda bid, **kw: c.post(f"/api/staff/bookings/{bid}/status", json=kw, headers=H)
B = b1["booking_id"]
ok("cannot skip steps", st(B, status="PAID").status_code == 400)
ok("check in", st(B, status="CHECKED_IN").status_code == 200)
ok("weigh needs quantity", st(B, status="WEIGHED").status_code == 400)
ok("weigh", st(B, status="WEIGHED", qty=30).status_code == 200)
ok("quality", st(B, status="QUALITY_PASSED").status_code == 200)
r = st(B, status="PROCURED"); ok("procured amount = 30 x 2320", r.json["amount"] == 69600)
p = c.get("/api/payments", headers=T1).json
ok("payment row created as PENDING", p["payments"][0]["status"] == "PENDING" and p["pending_total"] == 69600)
ok("cannot start payment without bank details", st(B, status="PAYMENT_INITIATED").status_code == 400)
bank = dict(holder="Ravi Kumar", account="123456789012", account2="123456789012", ifsc="sbin0001234")
ok("bank: mismatch rejected", c.post("/api/bank", json=dict(bank, account2="1"), headers=T1).status_code == 400)
ok("bank: bad ifsc rejected", c.post("/api/bank", json=dict(bank, ifsc="ABCD1234567"), headers=T1).status_code == 400)
ok("bank: short account rejected", c.post("/api/bank", json=dict(bank, account="123", account2="123"), headers=T1).status_code == 400)
r = c.post("/api/bank", json=bank, headers=T1); ok("bank saved", r.status_code == 200)
ok("account number is masked", c.get("/api/me", headers=T1).json["bank"]["account"] == "XXXXXXXX9012")
ok("ifsc stored uppercase", c.get("/api/me", headers=T1).json["bank"]["ifsc"] == "SBIN0001234")
ok("payment initiated", st(B, status="PAYMENT_INITIATED").status_code == 200)
r = st(B, status="PAID", reference="UTR 123-456"); ok("paid with reference", r.status_code == 200 and r.json["reference"] == "UTR123456")
p = c.get("/api/payments", headers=T1).json
ok("payment PAID, totals updated", p["payments"][0]["status"] == "PAID" and p["paid_total"] == 69600 and p["pending_total"] == 0)
notes = [x["message"] for x in c.get("/api/notifications", headers=T1).json]
ok("sms text has masked account, never the full number", any("XXXXXXXX9012" in m for m in notes) and not any("123456789012" in m for m in notes))
ok("closed booking cannot change", st(B, status="PAID").status_code == 400)
ok("farmer 2 moved to #1", c.get("/api/bookings/mine", headers=T2).json[0]["queue_position"] == 1)
ok("turn-near alert sent", any("turn is near" in x["message"] for x in c.get("/api/notifications", headers=T2).json))
q = c.get(f"/api/staff/queue?centre_id=1&date={date}", headers=H).json
ok("staff queue shows payment", q[0]["pay_status"] == "PAID" and q[0]["has_bank"] is True)
s = c.get(f"/api/staff/summary?centre_id=1&date={date}", headers=H).json
ok("staff summary", s["paid"] == 69600 and s["farmers"] == 2)
ok("reject allowed before procurement", st(b2["booking_id"], status="REJECTED").status_code == 200)
ok("cancel after reject not allowed", c.post(f"/api/bookings/{b2['booking_id']}/cancel", headers=T2).status_code == 400)

# ---- security ----
ok("wrong pin message", c.get("/api/staff/queue?centre_id=1", headers={"X-Staff-Pin": "9"}).json["error"] == "Wrong staff PIN")
ok("no token -> 401", c.get("/api/payments").status_code == 401)
ok("sms-test rejects foreign number", c.post("/api/staff/sms-test", json=dict(phone="+1 2025550123"), headers=H).status_code == 400)
ok("home page", b"Kisan Slot" in c.get("/").data)
print(f"\nALL {n} CHECKS PASSED on", c.get("/api/health").json)
