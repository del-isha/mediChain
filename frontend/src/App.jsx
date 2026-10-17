import React, {useEffect, useState} from 'react'
import {Routes, Route, NavLink, Navigate, useNavigate, useLocation} from 'react-router-dom'
import {Activity, AlertTriangle, Archive, ArrowRightLeft, BarChart3, Bell, Building2, ClipboardCheck, FileClock, LogOut, MapPin, Package, QrCode, Search, ShieldCheck, Truck, UserRound, Menu, X} from 'lucide-react'
import api from './api'

const navGroups = [
  {label:'OPERATIONS', items:[
    ['Dashboard','/dashboard',Activity],['Inventory','/inventory',Package],['Medicines','/medicines',Archive],['Facilities','/facilities',Building2]
  ]},
  {label:'TRANSFERS', items:[
    ['All Transfers','/transfers',ArrowRightLeft],['Approvals','/approvals',ClipboardCheck],['Dispatch & Receiving','/shipments',Truck]
  ]},
  {label:'TRACEABILITY', items:[
    ['Medicine Passport','/passport',QrCode],['Alerts','/alerts',Bell],['Audit Log','/audit',FileClock]
  ]}
]

function App(){
  const [user,setUser] = useState(()=>JSON.parse(localStorage.getItem('medchain_user')||'null'))
  const login = (u)=>{setUser(u); localStorage.setItem('medchain_user',JSON.stringify(u))}
  const logout = ()=>{localStorage.clear();setUser(null)}
  return user ? <Shell user={user} logout={logout}/> : <Login onLogin={login}/>
}

function Login({onLogin}){
  const [email,setEmail]=useState('hospital@medchain.local')
  const [password,setPassword]=useState('hospital123')
  const [error,setError]=useState('')
  const [loading,setLoading]=useState(false)
  const submit=async(e)=>{
    e.preventDefault(); setError(''); setLoading(true)
    try { const r=await api.post('/auth/login',{email,password}); localStorage.setItem('medchain_token',r.data.access_token); onLogin(r.data.user)}
    catch(err){setError(err.response?.data?.detail||'Unable to sign in')}
    finally{setLoading(false)}
  }
  return <div className="login-page">
    <div className="login-card">
      <div className="brand-mark"><ShieldCheck size={28}/></div>
      <div className="eyebrow">EMERGENCY MEDICINE TRUST NETWORK</div>
      <h1>MEDCHAIN</h1>
      <p className="muted">Secure medicine movement, inventory and accountability.</p>
      <form onSubmit={submit}>
        <label>Email<input value={email} onChange={e=>setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label>
        {error && <div className="error-box">{error}</div>}
        <button className="primary full" disabled={loading}>{loading?'Signing in…':'Sign in'}</button>
      </form>
      <div className="demo-users">
        <strong>Demo accounts</strong>
        <span>Hospital: hospital@medchain.local / hospital123</span>
        <span>Officer: officer@medchain.local / officer123</span>
        <span>Warehouse: warehouse@medchain.local / warehouse123</span>
      </div>
    </div>
  </div>
}

function Shell({user,logout}){
  const [mobile,setMobile]=useState(false)
  const location=useLocation()
  const title=location.pathname.split('/')[1]||'dashboard'
  return <div className="app-shell">
    <aside className={mobile?'sidebar mobile-open':'sidebar'}>
      <div className="logo"><div className="logo-icon"><ShieldCheck size={20}/></div><div><b>MEDCHAIN</b><small>Trust Network</small></div><button className="icon-btn mobile-close" onClick={()=>setMobile(false)}><X/></button></div>
      <nav>
        {navGroups.map(g=><div className="nav-group" key={g.label}><div className="nav-label">{g.label}</div>{g.items.map(([label,path,Icon])=><NavLink onClick={()=>setMobile(false)} className={({isActive})=>isActive?'nav-link active':'nav-link'} to={path} key={path}><Icon size={17}/>{label}</NavLink>)}</div>)}
      </nav>
      <div className="sidebar-bottom"><div className="user-mini"><div className="avatar">{user.name[0]}</div><div><b>{user.name}</b><small>{user.role}</small></div></div><button className="logout" onClick={logout}><LogOut size={16}/> Sign out</button></div>
    </aside>
    <main className="main">
      <header className="topbar"><button className="icon-btn mobile-menu" onClick={()=>setMobile(true)}><Menu/></button><div className="crumb">MEDCHAIN <span>/</span> {title.replace('-', ' ')}</div><div className="top-actions"><button className="icon-btn"><Bell size={18}/><i className="dot"/></button><div className="top-user"><div className="avatar small">{user.name[0]}</div><span>{user.name}</span></div></div></header>
      <div className="content"><Routes>
        <Route path="/dashboard" element={<Dashboard/>}/>
        <Route path="/inventory" element={<Inventory/>}/>
        <Route path="/medicines" element={<Medicines/>}/>
        <Route path="/facilities" element={<Facilities/>}/>
        <Route path="/transfers" element={<Transfers/>}/>
        <Route path="/approvals" element={<Approvals user={user}/>}/>
        <Route path="/shipments" element={<Shipments user={user}/>}/>
        <Route path="/passport" element={<Passport/>}/>
        <Route path="/alerts" element={<Alerts/>}/>
        <Route path="/audit" element={<Audit/>}/>
        <Route path="*" element={<Navigate to="/dashboard"/>}/>
      </Routes></div>
    </main>
  </div>
}

function PageHeader({title,subtitle,action}){return <div className="page-header"><div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div>{action}</div>}
function Status({children,type='neutral'}){return <span className={`status ${type}`}>{children}</span>}
const typeFor=s=>({CRITICAL:'critical',WARNING:'warning',VERIFIED:'success',NORMAL:'success',PENDING:'warning',APPROVED:'info',IN_TRANSIT:'info',RECEIVED:'success',REJECTED:'critical'}[s]||'neutral')

function Dashboard(){
 const [data,setData]=useState(null),[alerts,setAlerts]=useState([]),[transfers,setTransfers]=useState([])
 useEffect(()=>{Promise.all([api.get('/dashboard'),api.get('/alerts'),api.get('/transfers')]).then(([a,b,c])=>{setData(a.data);setAlerts(b.data);setTransfers(c.data.slice(0,5))})},[])
 return <><PageHeader title="Overview" subtitle="Medicine network status and recent operational activity" action={<button className="primary" onClick={()=>location.href='/transfers'}>New transfer</button>}/>
 <div className="metric-grid">
   <Metric label="Total inventory" value={data?.total_units?.toLocaleString()||'—'} note="Units across network" icon={Package}/>
   <Metric label="Critical inventory" value={data?.critical_inventory??'—'} note="Items below threshold" icon={AlertTriangle} danger/>
   <Metric label="Active transfers" value={data?.transfers??'—'} note="All transfer records" icon={Truck}/>
   <Metric label="Pending approvals" value={data?.pending_approvals??'—'} note="Require officer action" icon={ClipboardCheck}/>
 </div>
 <div className="grid-2">
   <section className="panel"><div className="panel-head"><div><h3>Critical alerts</h3><p>Issues requiring attention</p></div><NavLink to="/alerts" className="text-link">View all</NavLink></div>
   {alerts.slice(0,4).map(a=><div className="alert-row" key={a.id}><div className={`alert-icon ${a.severity.toLowerCase()}`}><AlertTriangle size={16}/></div><div><b>{a.message}</b><small>{a.severity} · {new Date(a.created_at).toLocaleString()}</small></div><Status type={typeFor(a.severity)}>{a.severity}</Status></div>)}
   </section>
   <section className="panel"><div className="panel-head"><div><h3>Recent transfers</h3><p>Latest movement requests</p></div><NavLink to="/transfers" className="text-link">View all</NavLink></div>
   {transfers.map(t=><div className="activity-row" key={t.id}><div className="activity-main"><b>TR-{String(t.id).padStart(5,'0')}</b><span>{t.medicine} · {t.quantity.toLocaleString()} units</span></div><Status type={typeFor(t.status)}>{t.status.replace('_',' ')}</Status></div>)}
   </section>
 </div>
 <section className="panel map-panel"><div className="panel-head"><div><h3>Network snapshot</h3><p>Facilities connected to MEDCHAIN</p></div><NavLink to="/facilities" className="text-link">Open network</NavLink></div><div className="network-strip"><NetworkNode name="Punjab Central Warehouse" status="Healthy"/><div className="network-line"/><NetworkNode name="Chandigarh Distribution Center" status="Healthy"/><div className="network-line"/><NetworkNode name="Himachal Regional Hospital" status="Attention"/></div></section>
 </> 
}
function Metric({label,value,note,icon:Icon,danger}){return <div className="metric"><div className="metric-top"><span>{label}</span><div className={danger?'metric-icon danger':'metric-icon'}><Icon size={18}/></div></div><strong>{value}</strong><small>{note}</small></div>}
function NetworkNode({name,status}){return <div className="network-node"><span className={`node ${status==='Attention'?'attention':''}`}/><div><b>{name}</b><small>{status}</small></div></div>}

function Inventory(){
 const [rows,setRows]=useState([]),[q,setQ]=useState('')
 useEffect(()=>{api.get('/inventory').then(r=>setRows(r.data))},[])
 const filtered=rows.filter(x=>`${x.medicine_name} ${x.batch_number} ${x.facility_name}`.toLowerCase().includes(q.toLowerCase()))
 return <><PageHeader title="Inventory" subtitle="Current medicine and batch quantities across facilities"/>
 <div className="toolbar"><div className="search"><Search size={16}/><input placeholder="Search medicine, batch or facility…" value={q} onChange={e=>setQ(e.target.value)}/></div><button className="secondary">Facility ▾</button><button className="secondary">Status ▾</button></div>
 <section className="panel"><Table headers={['Medicine','Batch','Facility','Quantity','Expiry','Status']} rows={filtered.map(x=>[<b>{x.medicine_name}</b>,x.batch_number,x.facility_name,x.quantity.toLocaleString(),new Date(x.expiry_date).toLocaleDateString(),<Status type={x.quantity<500?'critical':typeFor(x.status)}>{x.quantity<500?'CRITICAL':x.status.replace('_',' ')}</Status>])}/></section></>
}

function Medicines(){
 const [rows,setRows]=useState([])
 useEffect(()=>{api.get('/medicines').then(r=>setRows(r.data))},[])
 return <><PageHeader title="Medicines" subtitle="Registered medicines and manufacturers" action={<button className="primary">Add medicine</button>}/>
 <div className="card-grid">{rows.map(m=><div className="medicine-card" key={m.id}><div className="medicine-icon"><Package size={20}/></div><div><h3>{m.name}</h3><p>{m.category}</p></div><hr/><div className="kv"><span>Manufacturer</span><b>{m.manufacturer}</b></div><div className="kv"><span>Medicine ID</span><b>MED-{String(m.id).padStart(3,'0')}</b></div></div>)}</div></>
}

function Facilities(){
 const [rows,setRows]=useState([])
 useEffect(()=>{api.get('/facilities').then(r=>setRows(r.data))},[])
 return <><PageHeader title="Facilities" subtitle="Warehouses and hospitals in the medicine network"/>
 <div className="facility-grid">{rows.map(f=><div className="facility-card" key={f.id}><div className="facility-top"><div className="facility-icon"><Building2 size={20}/></div><Status type="success">ACTIVE</Status></div><h3>{f.name}</h3><p>{f.type}</p><div className="kv"><span>Address</span><b>{f.address}</b></div><div className="coords"><MapPin size={14}/>{f.latitude.toFixed(4)}, {f.longitude.toFixed(4)}</div></div>)}</div></>
}

function Transfers(){
 const [rows,setRows]=useState([]),[show,setShow]=useState(false)
 const load=()=>api.get('/transfers').then(r=>setRows(r.data))
 useEffect(load,[])
 return <><PageHeader title="Transfers" subtitle="Medicine movement requests and current status" action={<button className="primary" onClick={()=>setShow(true)}>New transfer</button>}/>
 <section className="panel"><Table headers={['Transfer','Medicine','Route','Quantity','Priority','Status']} rows={rows.map(t=>[
   <b>TR-{String(t.id).padStart(5,'0')}</b>,t.medicine,<span>{t.source_facility} → {t.destination_facility}</span>,t.quantity.toLocaleString(),<Status type={t.priority==='CRITICAL'?'critical':t.priority==='HIGH'?'warning':'neutral'}>{t.priority}</Status>,<Status type={typeFor(t.status)}>{t.status.replace('_',' ')}</Status>
 ])}/></section>
 {show&&<TransferModal onClose={()=>setShow(false)} onDone={()=>{setShow(false);load()}}/>}</>
}

function TransferModal({onClose,onDone}){
 const [fac,setFac]=useState([]),[batches,setBatches]=useState([]),[form,setForm]=useState({source_facility_id:'',destination_facility_id:'',batch_id:'',quantity:100,reason:'Flood emergency',priority:'CRITICAL'}),[error,setError]=useState('')
 useEffect(()=>{Promise.all([api.get('/facilities'),api.get('/batches')]).then(([a,b])=>{setFac(a.data);setBatches(b.data);setForm(f=>({...f,source_facility_id:a.data[0]?.id||'',destination_facility_id:a.data[2]?.id||'',batch_id:b.data[0]?.id||''}))})},[])
 const submit=async()=>{try{await api.post('/transfers',{...form,source_facility_id:+form.source_facility_id,destination_facility_id:+form.destination_facility_id,batch_id:+form.batch_id,quantity:+form.quantity});onDone()}catch(e){setError(e.response?.data?.detail||'Could not create transfer')}}
 return <div className="modal-backdrop"><div className="modal"><div className="modal-head"><div><h3>New Emergency Transfer</h3><p>Create a medicine movement request</p></div><button className="icon-btn" onClick={onClose}><X/></button></div>
 {error&&<div className="error-box">{error}</div>}
 <div className="form-grid"><label>Source facility<select value={form.source_facility_id} onChange={e=>setForm({...form,source_facility_id:e.target.value})}>{fac.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
 <label>Destination<select value={form.destination_facility_id} onChange={e=>setForm({...form,destination_facility_id:e.target.value})}>{fac.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
 <label>Medicine / batch<select value={form.batch_id} onChange={e=>setForm({...form,batch_id:e.target.value})}>{batches.map(x=><option key={x.id} value={x.id}>{x.medicine_name} · {x.batch_number}</option>)}</select></label>
 <label>Quantity<input type="number" min="1" value={form.quantity} onChange={e=>setForm({...form,quantity:e.target.value})}/></label>
 <label>Priority<select value={form.priority} onChange={e=>setForm({...form,priority:e.target.value})}><option>CRITICAL</option><option>HIGH</option><option>NORMAL</option></select></label>
 <label>Reason<input value={form.reason} onChange={e=>setForm({...form,reason:e.target.value})}/></label></div>
 <div className="modal-actions"><button className="secondary" onClick={onClose}>Cancel</button><button className="primary" onClick={submit}>Submit request</button></div>
 </div></div>
}

function Approvals({user}){
 const [rows,setRows]=useState([]),[busy,setBusy]=useState(null)
 const load=()=>api.get('/transfers').then(r=>setRows(r.data.filter(x=>x.status==='PENDING')))
 useEffect(load,[])
 const decide=async(id,ok)=>{setBusy(id);try{await api.post(`/transfers/${id}/${ok?'approve':'reject'}`,{comment:ok?'Approved for emergency movement':'Request rejected'});load()}finally{setBusy(null)}}
 return <><PageHeader title="Approvals" subtitle="Review emergency medicine transfer requests"/>
 {user.role!=='OFFICER'&&user.role!=='ADMIN'?<div className="notice">This area is restricted to authorized officers.</div>:<div className="approval-list">{rows.length===0&&<Empty text="No pending transfer requests."/>}{rows.map(t=><div className="approval-card" key={t.id}><div className="approval-top"><div><span className="eyebrow">TR-{String(t.id).padStart(5,'0')} · {t.priority}</span><h3>{t.medicine} — {t.quantity.toLocaleString()} units</h3></div><Status type="warning">PENDING</Status></div><div className="route-box"><div><small>FROM</small><b>{t.source_facility}</b></div><ArrowRightLeft/><div><small>TO</small><b>{t.destination_facility}</b></div></div><p><b>Reason:</b> {t.reason}</p><div className="modal-actions"><button className="secondary" disabled={busy===t.id} onClick={()=>decide(t.id,false)}>Reject</button><button className="primary" disabled={busy===t.id} onClick={()=>decide(t.id,true)}>Approve transfer</button></div></div>)}</div>}
 </>
}

function Shipments({user}){
 const [rows,setRows]=useState([])
 const load=()=>api.get('/transfers').then(r=>setRows(r.data.filter(x=>['APPROVED','IN_TRANSIT'].includes(x.status))))
 useEffect(load,[])
 const action=async(t,kind)=>{await api.post(`/shipments/${t.id}/${kind}`);load()}
 return <><PageHeader title="Dispatch & Receiving" subtitle="Move approved medicine and confirm receipt"/>
 <section className="panel"><Table headers={['Transfer','Medicine','Route','Quantity','Status','Action']} rows={rows.map(t=>[<b>TR-{String(t.id).padStart(5,'0')}</b>,t.medicine,<span>{t.source_facility} → {t.destination_facility}</span>,t.quantity.toLocaleString(),<Status type={typeFor(t.status)}>{t.status.replace('_',' ')}</Status>,t.status==='APPROVED'&&['WAREHOUSE','ADMIN'].includes(user.role)?<button className="table-btn" onClick={()=>action(t,'dispatch')}>Dispatch</button>:t.status==='IN_TRANSIT'&&['HOSPITAL','ADMIN'].includes(user.role)?<button className="table-btn" onClick={()=>action(t,'receive')}>Receive</button>:<span className="muted">—</span>])}/></section></>
}

function Passport(){
 const [batches,setBatches]=useState([]),[id,setId]=useState(''),[data,setData]=useState(null),[error,setError]=useState('')
 useEffect(()=>{api.get('/batches').then(r=>setBatches(r.data))},[])
 const load=async()=>{if(!id)return;try{setData((await api.get(`/passport/${id}`)).data);setError('')}catch(e){setError('Batch not found')}}
 return <><PageHeader title="Medicine Passport" subtitle="Look up a batch and review its recorded journey"/>
 <section className="passport-search panel"><div className="search"><Search size={16}/><select value={id} onChange={e=>setId(e.target.value)}><option value="">Select a batch…</option>{batches.map(b=><option value={b.id} key={b.id}>{b.medicine_name} · {b.batch_number}</option>)}</select></div><button className="primary" onClick={load}>Open passport</button><span className="scan-note"><QrCode size={16}/> QR scanning can map directly to this batch ID.</span></section>
 {error&&<div className="error-box">{error}</div>}
 {data&&<div className="passport"><div className="passport-head"><div><span className="eyebrow">MEDICINE PASSPORT</span><h2>{data.medicine}</h2><p>Batch {data.batch_number}</p></div><Status type={typeFor(data.status)}>{data.status}</Status></div><div className="passport-grid"><div><small>Manufacturer</small><b>{data.manufacturer}</b></div><div><small>Manufactured</small><b>{data.manufactured_date}</b></div><div><small>Expiry</small><b>{data.expiry_date}</b></div></div><h3>Current locations</h3>{data.current_locations.map((x,i)=><div className="location-row" key={i}><MapPin size={17}/><b>{x.facility}</b><span>{x.quantity.toLocaleString()} units</span></div>)}<h3>Custody history</h3>{data.journey.length?data.journey.map((x,i)=><div className="timeline-row" key={i}><div className="timeline-dot"/><div><b>{x.event}</b><p>{x.location} · {x.quantity.toLocaleString()} units</p><small>{new Date(x.timestamp).toLocaleString()}</small></div></div>):<Empty text="No transfer custody events recorded for this batch yet."/>}</div>}
 </>
}

function Alerts(){
 const [rows,setRows]=useState([])
 useEffect(()=>{api.get('/alerts').then(r=>setRows(r.data))},[])
 return <><PageHeader title="Alerts" subtitle="Operational issues requiring attention"/><section className="panel"><Table headers={['Severity','Issue','Type','Status','Created']} rows={rows.map(a=>[<Status type={typeFor(a.severity)}>{a.severity}</Status>,<b>{a.message}</b>,a.type,<Status type="neutral">{a.status}</Status>,new Date(a.created_at).toLocaleString()])}/></section></>
}

function Audit(){
 const [rows,setRows]=useState([])
 useEffect(()=>{api.get('/audit').then(r=>setRows(r.data))},[])
 return <><PageHeader title="Audit Log" subtitle="Recorded actions across medicine movement workflows"/><section className="panel"><div className="audit-list">{rows.map(x=><div className="audit-row" key={x.id}><div className="audit-icon"><FileClock size={17}/></div><div><b>{x.action.replaceAll('_',' ')}</b><p>{x.entity} #{x.entity_id||'—'} · {x.details}</p><small>{x.user_name||'System'} · {new Date(x.timestamp).toLocaleString()}</small></div></div>)}{!rows.length&&<Empty text="No audit events yet."/>}</div></section></>
}

function Table({headers,rows}){return <div className="table-wrap"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows.length?rows.map((r,i)=><tr key={i}>{r.map((c,j)=><td key={j}>{c}</td>)}</tr>):<tr><td colSpan={headers.length}><Empty text="No records found."/></td></tr>}</tbody></table></div>}
function Empty({text}){return <div className="empty">{text}</div>}

export default App
