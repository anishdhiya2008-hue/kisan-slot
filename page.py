INDEX_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kisan Slot</title>
<style>
:root{--g:#2e7d32;--gd:#1b5e20;--bg:#f3f6f1;--t:#1c2a1c;--m:#667;--r:#b3261e;--o:#e65100}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--t)}
header{background:var(--g);color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:5}
.brand{font-weight:700;font-size:18px}nav button{background:#ffffff33;color:#fff;border:0;padding:8px 14px;border-radius:8px;margin-left:6px;cursor:pointer;font-size:14px}
nav button.on{background:#fff;color:var(--g);font-weight:600}
main{max-width:920px;margin:auto;padding:14px}.hide{display:none!important}
.card{background:#fff;border-radius:12px;padding:14px;margin:12px 0;box-shadow:0 1px 4px #0001}
h3{margin:0 0 8px;font-size:16px}label{display:block;font-size:13px;color:var(--m);margin:10px 0 3px}
input,select{padding:10px;border:1px solid #c9d1c9;border-radius:8px;font-size:15px;width:100%;max-width:340px;background:#fff}
input:focus,select:focus{outline:2px solid #81c784;border-color:var(--g)}
.row{display:flex;flex-wrap:wrap;gap:10px}.row>div{flex:1 1 200px}
.phone{display:flex;align-items:center;max-width:340px}.phone span{padding:10px 12px;background:#eef3ee;border:1px solid #c9d1c9;border-right:0;border-radius:8px 0 0 8px;font-size:15px}
.phone input{border-radius:0 8px 8px 0}
button.p{background:var(--g);color:#fff;border:0;padding:10px 16px;border-radius:8px;font-size:15px;cursor:pointer;margin-top:12px}
button.p:disabled{opacity:.5;cursor:not-allowed}button.s{background:#fff;color:var(--g);border:1px solid var(--g);padding:6px 10px;border-radius:8px;cursor:pointer;font-size:13px;margin:2px}
button.d{background:#fff;color:var(--r);border:1px solid var(--r);padding:6px 10px;border-radius:8px;cursor:pointer;font-size:13px;margin:2px}
.tabs{display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap}.tabs button{border:0;background:#e6ede6;padding:9px 14px;border-radius:8px;cursor:pointer;font-size:14px}
.tabs button.on{background:var(--g);color:#fff}.msg{margin-top:10px;font-size:14px;color:var(--m)}.msg.err{color:var(--r)}.msg.ok{color:var(--gd)}
.slot{display:inline-block;margin:4px;padding:10px 14px;border:1px solid var(--g);border-radius:10px;cursor:pointer;text-align:center;background:#fff}
.slot:hover{background:#e8f5e9}.slot.full{opacity:.4;pointer-events:none}.muted{color:var(--m);font-size:13px}
.chip{display:inline-block;padding:3px 9px;border-radius:12px;font-size:12px;font-weight:600;background:#e0e0e0}
.chip.PAID,.chip.PROCURED,.chip.QUALITY_PASSED{background:#c8e6c9;color:var(--gd)}.chip.CANCELLED,.chip.REJECTED,.chip.NO_SHOW,.chip.FAILED{background:#ffcdd2;color:var(--r)}
.chip.PENDING,.chip.INITIATED,.chip.PAYMENT_INITIATED,.chip.BOOKED{background:#fff3e0;color:var(--o)}.chip.CHECKED_IN,.chip.WEIGHED{background:#e3f2fd;color:#0d47a1}
.steps{display:flex;gap:4px;margin:10px 0;flex-wrap:wrap}.step{font-size:11px;padding:4px 8px;border-radius:12px;background:#e6e6e6}
.step.done{background:#a5d6a7}.step.now{background:var(--g);color:#fff}
.big{font-size:26px;font-weight:700;color:var(--g)}.tiles{display:flex;gap:10px;flex-wrap:wrap}.tile{flex:1 1 140px;background:#f1f8e9;border-radius:10px;padding:12px}
.tile b{display:block;font-size:20px;color:var(--gd)}.tile.warn{background:#fff3e0}.tile.warn b{color:var(--o)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px 6px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
.scroll{overflow-x:auto}.toast{position:fixed;left:50%;top:70px;transform:translateX(-50%);background:#1b5e20;color:#fff;padding:12px 18px;border-radius:10px;z-index:9;box-shadow:0 4px 14px #0004;max-width:90%}
.pay{border:1px solid #e3e8e3;border-radius:10px;padding:10px;margin:8px 0}
</style></head><body>
<header><div class="brand">🌾 Kisan Slot</div>
<nav><button id="nf" class="on" onclick="mode('farmer')">Farmer</button><button id="ns" onclick="mode('staff')">Centre Staff</button></nav></header>
<div id="toast" class="toast hide"></div>
<main>
<!-- ================= FARMER ================= -->
<section id="farmer">
 <div id="auth" class="card">
  <div class="tabs"><button id="tl" class="on" onclick="authTab('login')">Login</button><button id="tr" onclick="authTab('reg')">Register</button></div>
  <div id="pLogin">
   <label>Mobile number (India)</label>
   <div class="phone"><span>+91</span><input id="lp" inputmode="numeric" autocomplete="tel-national" placeholder="98765 43210" oninput="cleanPhone(this)"></div>
   <button class="p" id="bOtp" onclick="sendOtp()">Send OTP</button>
   <div id="otpBox" class="hide">
    <label>Enter the 6-digit OTP sent to your mobile</label>
    <input id="lo" inputmode="numeric" maxlength="6" autocomplete="one-time-code" placeholder="123456" style="max-width:180px;letter-spacing:4px">
    <div><button class="p" onclick="verify()">Verify and login</button></div>
   </div>
  </div>
  <div id="pReg" class="hide">
   <div class="row">
    <div><label>Full name</label><input id="rn" placeholder="Ravi Kumar"></div>
    <div><label>Mobile number (India)</label><div class="phone"><span>+91</span><input id="rp" inputmode="numeric" placeholder="98765 43210" oninput="cleanPhone(this)"></div></div>
    <div><label>Village</label><input id="rv" placeholder="Perundurai"></div>
    <div><label>Main crop</label><select id="rc"><option>Paddy</option><option>Wheat</option></select></div>
    <div><label>Land (acres)</label><input id="ra" type="number" min="0" step="0.1" placeholder="2.5"></div>
   </div>
   <button class="p" onclick="register()">Register and send OTP</button>
  </div>
  <div id="amsg" class="msg"></div>
 </div>

 <div id="app" class="hide">
  <div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
   <div><b id="hello"></b><div class="muted" id="hphone"></div></div><button class="s" onclick="logout()">Logout</button></div>
  <div class="tabs">
   <button id="t_book" class="on" onclick="sub('book')">Book slot</button>
   <button id="t_mine" onclick="sub('mine')">My bookings</button>
   <button id="t_pay" onclick="sub('pay')">Payments</button>
   <button id="t_notes" onclick="sub('notes')">Alerts</button>
  </div>

  <div id="s_book">
   <div class="card"><h3>Centres today (live)</h3><div id="centres" class="muted">Loading...</div></div>
   <div class="card"><h3>Book a procurement slot</h3>
    <div class="row">
     <div><label>Centre</label><select id="bc" onchange="loadSlots()"></select></div>
     <div><label>Date</label><select id="bd" onchange="loadSlots()"></select></div>
     <div><label>Your crop quantity (quintals)</label><input id="bq" type="number" min="1" max="2000" placeholder="30"></div>
    </div>
    <label>Tap a time slot to book</label><div id="slots"></div><div id="bmsg" class="msg"></div>
   </div>
  </div>

  <div id="s_mine" class="hide"><div id="mine"></div></div>

  <div id="s_pay" class="hide">
   <div class="tiles"><div class="tile"><span class="muted">Received</span><b id="paidTotal">₹0.00</b></div>
    <div class="tile warn"><span class="muted">On the way</span><b id="pendTotal">₹0.00</b></div></div>
   <div class="card"><h3>Bank account for payment</h3>
    <div id="bankView"></div>
    <div id="bankForm" class="hide">
     <div class="row">
      <div><label>Account holder name</label><input id="bh" placeholder="As in bank passbook"></div>
      <div><label>Account number</label><input id="ba" inputmode="numeric" placeholder="9 to 18 digits" autocomplete="off"></div>
      <div><label>Confirm account number</label><input id="ba2" inputmode="numeric" autocomplete="off"></div>
      <div><label>IFSC code</label><input id="bi" placeholder="SBIN0001234" maxlength="11" style="text-transform:uppercase" autocomplete="off"></div>
     </div>
     <button class="p" onclick="saveBank()">Save bank details</button> <button class="s" id="bcancel" onclick="bankEdit(false)">Cancel</button>
    </div><div id="bkmsg" class="msg"></div>
   </div>
   <div class="card"><h3>Payment history</h3><div id="pays" class="muted">No payments yet</div></div>
  </div>

  <div id="s_notes" class="hide"><div class="card"><h3>SMS and app alerts</h3><div id="notes" class="muted">No alerts yet</div></div></div>
 </div>
</section>

<!-- ================= STAFF ================= -->
<section id="staff" class="hide">
 <div class="card">
  <div class="row">
   <div><label>Staff PIN</label><input id="pin" type="password" autocomplete="new-password" name="staffpin" placeholder="Staff PIN">
    <label style="display:inline-flex;gap:6px;align-items:center;margin-top:6px"><input type="checkbox" style="width:auto" onchange="$('pin').type=this.checked?'text':'password'"> show PIN</label></div>
   <div><label>Centre</label><select id="sc"></select></div>
  </div>
  <button class="p" onclick="loadQueue()">Load queue</button> <span class="muted">refreshes every 5 seconds after loading</span>
 </div>
 <div class="tiles" id="sum"></div>
 <div class="card scroll"><table><thead><tr><th>Token</th><th>Farmer</th><th>Slot</th><th>Status</th><th>Qty (qtl)</th><th>Payment</th><th>Action</th></tr></thead><tbody id="sq"></tbody></table>
  <div id="sqempty" class="muted" style="padding:10px">Enter the PIN, choose a centre and click Load queue.</div></div>
 <div class="card"><h3>Send a test SMS</h3><div class="phone"><span>+91</span><input id="tp" inputmode="numeric" placeholder="98765 43210" oninput="cleanPhone(this)"></div>
  <button class="s" onclick="smsTest()">Send test SMS</button></div>
</section>
</main>

<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const inr=n=>"₹"+Number(n||0).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2});
const when=s=>{const d=new Date(s);return isNaN(d)?"":d.toLocaleString("en-IN",{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"})};
const label=s=>String(s||"").replace(/_/g," ");
let TOKEN=localStorage.getItem("tok")||"",PAYS=[],LASTKEY=null,POLL=null,cool=null;

async function api(url,method,body){
  const h={"Content-Type":"application/json"};
  if(TOKEN)h["X-Token"]=TOKEN;
  if(url.indexOf("/api/staff")===0)h["X-Staff-Pin"]=($("pin").value||"").trim();
  let r,j={};
  try{r=await fetch(url,{method:method||"GET",headers:h,body:body?JSON.stringify(body):undefined})}catch(e){throw new Error("Cannot reach the server. Check your internet.")}
  try{j=await r.json()}catch(e){throw new Error("Server error "+r.status+". Check the Vercel logs.")}
  if(r.status===401&&TOKEN&&url.indexOf("/api/staff")!==0&&url!=="/api/verify"){logout(true)}
  if(!r.ok)throw new Error(j.error||"Something went wrong");
  return j}

function mode(m){$("farmer").classList.toggle("hide",m!="farmer");$("staff").classList.toggle("hide",m!="staff");$("nf").className=m=="farmer"?"on":"";$("ns").className=m=="staff"?"on":""}
function toast(t){const e=$("toast");e.textContent=t;e.classList.remove("hide");clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.add("hide"),6000)}
function say(id,t,kind){const e=$(id);e.textContent=t||"";e.className="msg "+(kind||"")}

/* ---------- Indian mobile numbers only ---------- */
function cleanPhone(el){const raw=el.value;let d=raw.replace(/\D/g,"");
  if(/^\s*(\+|00)91/.test(raw)||(d.length>=12&&d.indexOf("91")===0))d=d.replace(/^(00)?91/,"");
  else if(d.length==11&&d.charAt(0)=="0")d=d.slice(1);
  d=d.slice(0,10);el.value=d.length>5?d.slice(0,5)+" "+d.slice(5):d}
const digits=id=>$(id).value.replace(/\D/g,"");
const validPhone=p=>/^[6-9]\d{9}$/.test(p)&&!/^(\d)\1{9}$/.test(p);
const PHONE_ERR="Enter a valid Indian mobile number: 10 digits starting with 6, 7, 8 or 9";

/* ---------- login / register ---------- */
function authTab(t){$("pLogin").classList.toggle("hide",t!="login");$("pReg").classList.toggle("hide",t!="reg");$("tl").className=t=="login"?"on":"";$("tr").className=t=="reg"?"on":"";say("amsg","")}
async function sendOtp(){const p=digits("lp");if(!validPhone(p)){say("amsg",PHONE_ERR,"err");return}
  $("bOtp").disabled=true;say("amsg","Sending OTP...");
  try{const j=await api("/api/login","POST",{phone:p});$("otpBox").classList.remove("hide");$("lo").focus();
    say("amsg",j.message+(j.demo_otp?" (demo OTP: "+j.demo_otp+")":"")+". Valid for 10 minutes.","ok");startCool()}
  catch(e){say("amsg",e.message,"err");$("bOtp").disabled=false}}
function startCool(){let s=30;clearInterval(cool);cool=setInterval(()=>{s--;$("bOtp").textContent=s>0?"Resend OTP in "+s+"s":"Resend OTP";if(s<=0){clearInterval(cool);$("bOtp").disabled=false}},1000);$("bOtp").textContent="Resend OTP in 30s"}
async function register(){const p=digits("rp");
  if(!validPhone(p)){say("amsg",PHONE_ERR,"err");return}
  try{await api("/api/register","POST",{name:$("rn").value,phone:p,village:$("rv").value,crop:$("rc").value,land_acres:$("ra").value});
    authTab("login");$("lp").value=p.slice(0,5)+" "+p.slice(5);await sendOtp()}
  catch(e){say("amsg",e.message,"err")}}
async function verify(){const p=digits("lp"),o=$("lo").value.trim();
  if(!/^\d{6}$/.test(o)){say("amsg","Enter the 6-digit OTP","err");return}
  try{const j=await api("/api/verify","POST",{phone:p,otp:o});TOKEN=j.token;localStorage.setItem("tok",TOKEN);await enterApp()}
  catch(e){say("amsg",e.message,"err")}}
function logout(silent){TOKEN="";localStorage.removeItem("tok");clearInterval(POLL);LASTKEY=null;
  $("app").classList.add("hide");$("auth").classList.remove("hide");$("otpBox").classList.add("hide");$("lo").value="";$("bOtp").disabled=false;$("bOtp").textContent="Send OTP";
  say("amsg",silent===true?"Please log in again.":"")}

async function enterApp(){
  const me=await api("/api/me");$("auth").classList.add("hide");$("app").classList.remove("hide");
  $("hello").textContent="Namaste, "+me.name;$("hphone").textContent="+91 "+me.phone.slice(0,5)+" "+me.phone.slice(5)+" · "+me.village;
  const cs=await api("/api/centres");$("bc").innerHTML=cs.map(c=>`<option value="${c.id}">${esc(c.name)}</option>`).join("");
  const ds=await api("/api/dates");$("bd").innerHTML=ds.map(d=>`<option>${d}</option>`).join("");
  sub("book");loadSlots();refreshAll();clearInterval(POLL);POLL=setInterval(()=>{if(!document.hidden)refreshAll()},5000)}

function sub(n){["book","mine","pay","notes"].forEach(k=>{$("s_"+k).classList.toggle("hide",k!=n);$("t_"+k).className=k==n?"on":""})}

/* ---------- booking ---------- */
async function loadSlots(){if(!$("bc").value)return;
  try{const s=await api(`/api/slots?centre_id=${$("bc").value}&date=${$("bd").value}`);
  $("slots").innerHTML=s.map(x=>`<span class="slot ${x.available<=0?"full":""}" onclick="book(${x.id})"><b>${esc(x.start)} - ${esc(x.end)}</b><br><small>${x.available} seats left</small></span>`).join("")}catch(e){say("bmsg",e.message,"err")}}
async function book(id){const q=+$("bq").value;if(!(q>0)){say("bmsg","First enter your crop quantity in quintals","err");$("bq").focus();return}
  try{const j=await api("/api/bookings","POST",{slot_id:id,est_qty:q});say("bmsg","Booked! Your token number is #"+j.token_no+". An SMS was sent to your mobile.","ok");loadSlots();refreshAll();setTimeout(()=>sub("mine"),900)}
  catch(e){say("bmsg",e.message,"err")}}
async function cancelBooking(id){if(!confirm("Cancel this booking?"))return;try{await api(`/api/bookings/${id}/cancel`,"POST");refreshAll();loadSlots()}catch(e){alert(e.message)}}

/* ---------- live refresh ---------- */
async function refreshAll(){if(!TOKEN)return;
  try{const [cs,m,p,n]=await Promise.all([api("/api/centres"),api("/api/bookings/mine"),api("/api/payments"),api("/api/notifications")]);
   $("centres").innerHTML=cs.map(c=>`<div>${esc(c.name)} (${esc(c.crop)}, MSP ₹${c.msp_per_qtl}/qtl): <b>${c.waiting_today}</b> waiting, about ${c.est_wait_min} min</div>`).join("");
   $("mine").innerHTML=m.length?m.map(b=>{const i=b.flow.indexOf(b.status);
     const steps=b.flow.map((s,k)=>`<span class="step ${k<i?"done":k==i?"now":""}">${esc(label(s))}</span>`).join("");
     return `<div class="card"><b>${esc(b.centre)}</b> · ${esc(b.date)} ${esc(b.start)}-${esc(b["end"])} · Token #${b.token_no} <span class="chip ${esc(b.status)}">${esc(label(b.status))}</span>
      ${b.queue_position?`<div class="big">#${b.queue_position} in queue · about ${b.eta_min} min</div>`:""}
      ${b.amount?`<div>Amount: <b>${inr(b.amount)}</b></div>`:""}<div class="steps">${steps}</div>
      ${b.status=="BOOKED"?`<button class="d" onclick="cancelBooking(${b.id})">Cancel booking</button>`:""}</div>`}).join(""):'<div class="card muted">No bookings yet. Use the Book slot tab.</div>';
   renderPay(p);
   $("notes").innerHTML=n.length?n.map(x=>`<div class="pay">📩 ${esc(x.message)}<div class="muted">${esc(when(x.created))}</div></div>`).join(""):"No alerts yet";
   const key=n.length?n[0].created+"|"+n[0].message:"";
   if(LASTKEY!==null&&key&&key!==LASTKEY)toast("📩 "+n[0].message);LASTKEY=key;
  }catch(e){}}

/* ---------- payments ---------- */
function renderPay(p){PAYS=p.payments;$("paidTotal").textContent=inr(p.paid_total);$("pendTotal").textContent=inr(p.pending_total);
  if(p.bank&&!$("bankView").dataset.editing){$("bankView").innerHTML=`<div class="pay"><b>${esc(p.bank.holder)}</b><br>A/c ${esc(p.bank.account)} · IFSC ${esc(p.bank.ifsc)}</div><button class="s" onclick="bankEdit(true)">Change bank details</button>`;$("bankForm").classList.add("hide")}
  else if(!p.bank&&!$("bankView").dataset.editing){$("bankView").innerHTML='<div class="muted">Add your bank account so procurement money can be paid to you.</div>';$("bankForm").classList.remove("hide");$("bcancel").classList.add("hide")}
  $("pays").innerHTML=PAYS.length?PAYS.map(x=>`<div class="pay"><b>${inr(x.amount)}</b> <span class="chip ${esc(x.status)}">${esc(x.status)}</span>
    <div class="muted">${esc(x.centre)} · ${esc(x.date)} · Token #${x.token_no} · ${x.final_qty||""} qtl</div>
    ${x.reference?`<div>Ref: <b>${esc(x.reference)}</b> · ${esc(when(x.paid_at))}</div>`:""}
    ${x.status=="PAID"?`<button class="s" onclick="receipt(${x.id})">View receipt</button>`:""}</div>`).join(""):"No payments yet. They appear after your produce is procured."}
function bankEdit(on){$("bankView").dataset.editing=on?"1":"";if(on){$("bankView").innerHTML="";$("bankForm").classList.remove("hide");$("bcancel").classList.remove("hide")}else{delete $("bankView").dataset.editing;refreshAll()}say("bkmsg","")}
async function saveBank(){try{await api("/api/bank","POST",{holder:$("bh").value,account:$("ba").value,account2:$("ba2").value,ifsc:$("bi").value});
  ["bh","ba","ba2","bi"].forEach(i=>$(i).value="");delete $("bankView").dataset.editing;say("bkmsg","Bank details saved","ok");refreshAll()}catch(e){say("bkmsg",e.message,"err")}}
function receipt(id){const x=PAYS.find(p=>p.id===id);if(!x)return;const w=window.open("","_blank");if(!w){alert("Please allow pop-ups to view the receipt");return}
  w.document.write(`<title>Receipt</title><body style="font-family:sans-serif;max-width:480px;margin:30px auto"><h2>Kisan Slot: Payment Receipt</h2><hr>
  <p>Amount paid: <b>${inr(x.amount)}</b></p><p>Reference: <b>${esc(x.reference)}</b></p><p>Date: ${esc(when(x.paid_at))}</p>
  <p>Centre: ${esc(x.centre)}<br>Token #${x.token_no} · ${x.final_qty} quintals</p><hr><button onclick="print()">Print</button></body>`);w.document.close()}

/* ---------- centre staff ---------- */
let QLOADED=false;
const NEXT={BOOKED:["CHECKED_IN","Check in"],CHECKED_IN:["WEIGHED","Record weight"],WEIGHED:["QUALITY_PASSED","Pass quality"],QUALITY_PASSED:["PROCURED","Procure"],PROCURED:["PAYMENT_INITIATED","Start payment"],PAYMENT_INITIATED:["PAID","Mark paid"]};
async function loadStaffCentres(){try{const c=await api("/api/centres");$("sc").innerHTML=c.map(x=>`<option value="${x.id}">${esc(x.name)}</option>`).join("")}catch(e){}}
async function loadQueue(silent){
  if(!$("pin").value.trim()){if(!silent)alert("Enter the staff PIN first");return}
  if(!$("sc").value){if(!silent)alert("Choose a centre");return}
  try{const id=$("sc").value;const [r,s]=await Promise.all([api("/api/staff/queue?centre_id="+id),api("/api/staff/summary?centre_id="+id)]);QLOADED=true;
   $("sum").innerHTML=`<div class="tile"><span class="muted">Farmers today</span><b>${s.farmers}</b></div><div class="tile"><span class="muted">Procured (qtl)</span><b>${+s.procured_qtl.toFixed(2)}</b></div><div class="tile"><span class="muted">Paid</span><b>${inr(s.paid)}</b></div><div class="tile warn"><span class="muted">Payment pending</span><b>${inr(s.pending)}</b></div>`;
   $("sqempty").classList.toggle("hide",r.length>0);$("sqempty").textContent="No bookings yet at this centre today.";
   $("sq").innerHTML=r.map(b=>{const n=NEXT[b.status];
     return `<tr><td>#${b.token_no}</td><td>${esc(b.name)}<br><small class="muted">${esc(b.village)} · +91 ${esc(b.phone)}</small></td><td>${esc(b.start)}</td>
     <td><span class="chip ${esc(b.status)}">${esc(label(b.status))}</span></td><td>${b.final_qty||b.est_qty||""}</td>
     <td>${b.pay_status?`<span class="chip ${esc(b.pay_status)}">${esc(b.pay_status)}</span><br><small>${inr(b.amount)}${b.pay_ref?" · "+esc(b.pay_ref):""}</small>`:""}${!b.has_bank&&["PROCURED","PAYMENT_INITIATED"].includes(b.status)?'<br><small style="color:#b3261e">No bank details</small>':""}</td>
     <td>${n?`<button class="s" onclick="adv(${b.id},'${n[0]}')">${n[1]}</button>`:""}${["BOOKED","CHECKED_IN","WEIGHED","QUALITY_PASSED"].includes(b.status)?`<button class="d" onclick="adv(${b.id},'REJECTED')">Reject</button>`:""}</td></tr>`}).join("")}
  catch(e){QLOADED=false;if(!silent)alert(e.message)}}
async function adv(id,st){const body={status:st};
  if(st=="WEIGHED"){const q=prompt("Weighed quantity in quintals?");if(q===null)return;body.qty=q}
  if(st=="PAID"){const r=prompt("Bank reference / UTR number (leave blank to auto-generate)");if(r===null)return;body.reference=r}
  if(st=="REJECTED"&&!confirm("Reject this farmer's produce?"))return;
  try{await api(`/api/staff/bookings/${id}/status`,"POST",body);loadQueue()}catch(e){alert(e.message)}}
async function smsTest(){const p=digits("tp");if(!validPhone(p)){alert(PHONE_ERR);return}
  if(!$("pin").value.trim()){alert("Enter the staff PIN first");return}
  try{const j=await api("/api/staff/sms-test","POST",{phone:p});alert(j.message)}catch(e){alert(e.message)}}
setInterval(()=>{if(QLOADED&&!$("staff").classList.contains("hide"))loadQueue(true)},5000);

loadStaffCentres();
if(TOKEN)enterApp().catch(()=>logout(true));
</script></body></html>
"""
