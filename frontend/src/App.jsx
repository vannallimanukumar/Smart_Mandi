import React, { useCallback, useEffect, useMemo, useState } from "react";
import { BarChart3, Sprout, Truck, Users, Languages, MapPin, RefreshCw, LogIn, LogOut, ShieldCheck, Search, ArrowRight, Leaf } from "lucide-react";
import { api } from "./lib/api";
import { supabase, supabaseConfigured } from "./lib/supabase";

const words = {
  en: {
    tagline: "Fair prices for every farmer", browse: "Browse prices without signing in",
    district: "District", crop: "Crop", quantity: "Quantity (quintals)", village: "Village (optional for browsing)",
    compare: "Compare markets", prices: "Market prices", trucks: "Trucks", buyers: "Buyers",
    advice: "Sowing advice", signIn: "Sign in", signOut: "Sign out", loginRequired: "Sign in is required for this action.",
    email: "Email address", sendCode: "Send verification code", phone: "Indian phone number", verify: "Verify code",
    code: "Verification code", close: "Close", refresh: "Refresh", net: "Estimated take-home",
    modal: "Modal price", freight: "Estimated freight", gross: "Gross value", source: "Source",
    demo: "DEMO DATA — not live market information", official: "Official", local: "Local quote", estimate: "Estimate",
    book: "Request truck booking", offer: "Offer crop to buyer", buyer: "Buyer", expected: "Expected price per quintal",
    submit: "Submit request", status: "Status", note: "Check each record’s source and reporting date. Demo prices are illustrative; buyer and truck listings appear only after verification.",
    noAuth: "Configure Supabase in frontend/.env to enable real verification.", quantityError: "Quantity must be between 0.1 and 40 quintals.",
    welcome: "Choose a crop to see available market records.", search: "Search crops", allDistricts: "All pilot districts",
    why: "Transparent baseline score", demoBuyer: "Demo listing", requestSent: "Request submitted",
    bookingHint: "A booking request is not a confirmed truck booking. The owner must confirm it."
  },
  te: {
    tagline: "ప్రతి రైతుకు న్యాయమైన ధరలు", browse: "లాగిన్ లేకుండా ధరలు చూడండి",
    district: "జిల్లా", crop: "పంట", quantity: "పరిమాణం (క్వింటాళ్లు)", village: "గ్రామం (ధరలు చూడటానికి ఐచ్ఛికం)",
    compare: "మార్కెట్ల పోలిక", prices: "మార్కెట్ ధరలు", trucks: "ట్రక్కులు", buyers: "కొనుగోలుదారులు",
    advice: "సాగు సలహా", signIn: "లాగిన్", signOut: "లాగ్ అవుట్", loginRequired: "ఈ చర్యకు లాగిన్ అవసరం.",
    email: "ఈమెయిల్ చిరునామా", sendCode: "ధృవీకరణ కోడ్ పంపండి", phone: "భారతీయ ఫోన్ నంబర్", verify: "కోడ్ ధృవీకరించండి",
    code: "ధృవీకరణ కోడ్", close: "మూసివేయి", refresh: "రిఫ్రెష్", net: "అంచనా చేతికి వచ్చే మొత్తం",
    modal: "మోడల్ ధర", freight: "అంచనా రవాణా ఖర్చు", gross: "మొత్తం విలువ", source: "మూలం",
    demo: "నమూనా డేటా — ప్రత్యక్ష మార్కెట్ సమాచారం కాదు", official: "అధికారికం", local: "స్థానిక కోట్", estimate: "అంచనా",
    book: "ట్రక్కు బుకింగ్ అభ్యర్థన", offer: "కొనుగోలుదారుకు పంట ఆఫర్", buyer: "కొనుగోలుదారు", expected: "క్వింటాల్‌కు ఆశించే ధర",
    submit: "అభ్యర్థన పంపండి", status: "స్థితి", note: "ప్రతి రికార్డు మూలం, తేదీని పరిశీలించండి. నమూనా ధరలు ఉదాహరణ కోసం మాత్రమే; ధృవీకరణ తర్వాతే కొనుగోలుదారు, ట్రక్కు జాబితాలు చూపబడతాయి.",
    noAuth: "నిజమైన ధృవీకరణ కోసం frontend/.env లో Supabase కాన్ఫిగర్ చేయండి.", quantityError: "పరిమాణం 0.1 నుండి 40 క్వింటాళ్ల మధ్య ఉండాలి.",
    welcome: "మార్కెట్ రికార్డులు చూడటానికి పంటను ఎంచుకోండి.", search: "పంటలను వెతకండి", allDistricts: "అన్ని పైలట్ జిల్లాలు",
    why: "స్పష్టమైన ప్రాథమిక స్కోరు", demoBuyer: "నమూనా జాబితా", requestSent: "అభ్యర్థన పంపబడింది",
    bookingHint: "అభ్యర్థన పంపడం అంటే ట్రక్కు ఖరారు అయినట్లు కాదు. యజమాని నిర్ధారించాలి."
  }
};

const money = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(n || 0));

function PriceAnalytics({ crop, market, cropName }) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    if (!crop || !market) { setData(null); return; }
    let active = true;
    api(`/price-analytics?crop_id=${encodeURIComponent(crop)}&market_id=${encodeURIComponent(market)}`)
      .then(result => { if (active) { setData(result); setErr(""); } })
      .catch(error => { if (active) setErr(error.message); });
    return () => { active = false; };
  }, [crop, market]);
  return <div className="section-stack">
    <div className="section-title"><div><h3>Price analytics · {cropName(crop)}</h3><p>Synthetic sample history until the official data API is configured.</p></div></div>
    {err && <div className="notice error">{err}</div>}
    {!data && !err && <div className="notice">Loading analytics…</div>}
    {data && <><div className="notice">{data.note}</div><div className="analytics-metrics"><article className="price-card"><span className="eyebrow">Clean observations</span><strong>{data.observations}</strong></article><article className="price-card"><span className="eyebrow">Baseline forecast</span><strong>{data.forecast ? `₹${data.forecast.next_modal_price}` : "Not enough data"}</strong></article><article className="price-card"><span className="eyebrow">Holdout MAE</span><strong>{data.evaluation ? `₹${data.evaluation.mae}` : "Not evaluated"}</strong></article></div>
      <div className="price-grid">{data.history.map(point => <article className="price-card" key={point.date}><div className="price-head"><h4>{point.date}</h4><span className="source-tag">Historical</span></div><div className="modal-price">₹{point.modal_price}<small> / quintal</small></div></article>)}</div>
      <div className="notice warning">{data.note} The forecast is a transparent baseline, not a reliable prediction. Demo records are excluded from this endpoint.</div>
    </>}
  </div>;
}

export default function App() {
  const [lang, setLang] = useState("en");
  const t = words[lang];
  const [tab, setTab] = useState("compare");
  const [districts, setDistricts] = useState([]);
  const [districtSearch, setDistrictSearch] = useState("");
  const [crops, setCrops] = useState([]);
  const [district, setDistrict] = useState("annamayya");
  const [crop, setCrop] = useState("tomato");
  const [quantity, setQuantity] = useState("10");
  const [village, setVillage] = useState("");
  const [share, setShare] = useState(false);
  const [prices, setPrices] = useState([]);
  const [priceSource, setPriceSource] = useState("all");
  const [markets, setMarkets] = useState([]);
  const [marketFilter, setMarketFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [comparison, setComparison] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [advice, setAdvice] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [session, setSession] = useState(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [authMethod, setAuthMethod] = useState("email");
  const [authMode, setAuthMode] = useState("signin");
  const [authBusy, setAuthBusy] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [identity, setIdentity] = useState("");
  const [otp, setOtp] = useState("");
  const [authMessage, setAuthMessage] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [bookingMarket, setBookingMarket] = useState("madanapalle");
  const [bookingTruck, setBookingTruck] = useState("");
  const [offerBuyer, setOfferBuyer] = useState("");
  const [expectedPrice, setExpectedPrice] = useState("");

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => listener.subscription.unsubscribe();
  }, []);

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [d, c, marketRows, priceRows, comp, tr, by, ad] = await Promise.all([
        api("/districts"), api("/crops"), api(`/markets?district_id=${encodeURIComponent(district)}`),
        api(`/prices?crop_id=${encodeURIComponent(crop)}&district_id=${encodeURIComponent(district)}&source=${encodeURIComponent(priceSource)}${marketFilter ? `&market_id=${encodeURIComponent(marketFilter)}` : ""}${dateFrom ? `&date_from=${dateFrom}` : ""}${dateTo ? `&date_to=${dateTo}` : ""}`),
        api(`/compare?crop_id=${encodeURIComponent(crop)}&district_id=${encodeURIComponent(district)}&quantity_quintals=${encodeURIComponent(quantity || "10")}&share=${share}&source=${encodeURIComponent(priceSource)}`),
        api(`/trucks?district_id=${encodeURIComponent(district)}&quantity_quintals=${encodeURIComponent(quantity || "1")}`),
        api(`/buyers?district_id=${encodeURIComponent(district)}&crop_id=${encodeURIComponent(crop)}`),
        api(`/crop-advice?district_id=${encodeURIComponent(district)}`)
      ]);
      setDistricts(d); setCrops(c); setMarkets(marketRows); setPrices(priceRows); setComparison(comp); setTrucks(tr); setBuyers(by); setAdvice(ad);
      if (!bookingMarket && comp[0]) setBookingMarket(comp[0].market_id);
      if (!offerBuyer && by[0]) setOfferBuyer(String(by[0].id));
    } catch (e) { setError(e.message || "Could not load data"); }
    finally { setLoading(false); }
  }, [crop, district, quantity, share, marketFilter, dateFrom, dateTo, priceSource]);

  useEffect(() => { load(); }, [load]);

  const cropName = (id) => {
    const c = crops.find(x => x.id === id);
    return c ? (lang === "te" ? c.name_te : c.name_en) : id;
  };
  const districtName = (id) => {
    const d = districts.find(x => x.id === id);
    return d ? (lang === "te" ? d.name_te : d.name_en) : id;
  };
  const currentCrop = crops.find(x => x.id === crop);
  const filteredDistricts = districts.filter(d => {
    const query = districtSearch.trim().toLocaleLowerCase();
    return !query || `${d.name_en} ${d.name_te} ${d.id}`.toLocaleLowerCase().includes(query);
  });
  // Keep the selected district visible while the user searches for another one.
  const visibleDistricts = filteredDistricts.some(d => d.id === district)
    ? filteredDistricts
    : [...filteredDistricts, ...districts.filter(d => d.id === district)];

  function normalizePhone(value) {
    const raw = value.trim().replace(/[\s().-]/g, "");
    if (/^\d{10}$/.test(raw)) return `+91${raw}`;
    if (/^91\d{10}$/.test(raw)) return `+${raw}`;
    if (/^\+91\d{10}$/.test(raw)) return raw;
    return null;
  }

  async function sendCode(e) {
    e.preventDefault();
    setAuthMessage("");
    if (!supabaseConfigured || !supabase) {
      setAuthMessage(t.noAuth);
      return;
    }

    let payload;
    if (authMethod === "email") {
      const email = identity.trim().toLowerCase();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setAuthMessage("Enter a valid email address.");
        return;
      }
      payload = {
        email,
        options: { shouldCreateUser: authMode === "signup" }
      };
    } else {
      const phone = normalizePhone(identity);
      if (!phone) {
        setAuthMessage("Enter a valid Indian mobile number, such as 9876543210 or +919876543210.");
        return;
      }
      payload = {
        phone,
        options: { shouldCreateUser: authMode === "signup" }
      };
    }

    setAuthBusy(true);
    try {
      const { error } = await supabase.auth.signInWithOtp(payload);
      if (error) throw error;
      setCodeSent(true);
      setOtp("");
      setAuthMessage(
        authMethod === "email"
          ? "Verification email sent. If your email template uses a numeric OTP, enter it below. If it sends a magic link, open that link to finish signing in."
          : "SMS verification code requested. Enter the code sent to your phone."
      );
    } catch (e) {
      setAuthMessage(e.message || "Could not send the verification code.");
    } finally {
      setAuthBusy(false);
    }
  }

  async function verifyCode(e) {
    e.preventDefault();
    setAuthMessage("");
    if (!supabaseConfigured || !supabase) {
      setAuthMessage(t.noAuth);
      return;
    }
    if (!codeSent) {
      setAuthMessage("Request a verification code first.");
      return;
    }

    const token = otp.trim();
    if (!token) {
      setAuthMessage("Enter the verification code.");
      return;
    }

    let payload;
    if (authMethod === "email") {
      payload = { email: identity.trim().toLowerCase(), token, type: "email" };
    } else {
      const phone = normalizePhone(identity);
      if (!phone) {
        setAuthMessage("Enter a valid Indian mobile number first.");
        return;
      }
      payload = { phone, token, type: "sms" };
    }

    setAuthBusy(true);
    try {
      const { data, error } = await supabase.auth.verifyOtp(payload);
      if (error) throw error;
      if (!data.session) {
        setAuthMessage("Verification was accepted, but no session was returned. Check your Supabase email template and Auth settings.");
        return;
      }
      setSession(data.session);
      setAuthOpen(false);
      setOtp("");
      setCodeSent(false);
      setAuthMessage("");
      setActionMessage(`Signed in successfully${data.user?.email ? ` as ${data.user.email}` : data.user?.phone ? ` as ${data.user.phone}` : ""}.`);
    } catch (e) {
      setAuthMessage(e.message || "Verification failed. Check the code and try again.");
    } finally {
      setAuthBusy(false);
    }
  }

  async function signOut() {
    try {
      if (supabase) {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
      }
      setSession(null);
      setActionMessage("You have signed out.");
    } catch (e) {
      setActionMessage(e.message || "Could not sign out.");
    }
  }

  async function createBooking(e) {
    e.preventDefault(); setActionMessage(""); setError("");
    if (!session) { setAuthOpen(true); setActionMessage(t.loginRequired); return; }
    if (!village.trim()) { setActionMessage("Enter your village before requesting a booking."); return; }
    const qty = Number(quantity);
    if (qty < 0.1 || qty > 40) { setActionMessage(t.quantityError); return; }
    const selected = comparison.find(x => x.market_id === bookingMarket) || comparison[0];
    const truckId = bookingTruck ? Number(bookingTruck) : null;
    try {
      const result = await api("/bookings", { method: "POST", auth: true, body: {
        crop_id: crop, district_id: district, village: village.trim(), quantity_quintals: qty,
        market_id: bookingMarket || selected?.market_id, truck_id: truckId,
        estimated_freight: selected?.estimated_freight ?? 0
      }});
      setActionMessage(`${t.requestSent}: ${result.reference}. ${t.bookingHint}`);
    } catch (e) { setActionMessage(e.message); if (/sign-in|token|auth/i.test(e.message)) setAuthOpen(true); }
  }

  async function createOffer(e) {
    e.preventDefault(); setActionMessage(""); setError("");
    if (!session) { setAuthOpen(true); setActionMessage(t.loginRequired); return; }
    if (!village.trim()) { setActionMessage("Enter your village before sending an offer."); return; }
    try {
      const result = await api("/offers", { method: "POST", auth: true, body: {
        buyer_id: Number(offerBuyer), crop_id: crop, district_id: district,
        quantity_quintals: Number(quantity), expected_price_per_quintal: expectedPrice ? Number(expectedPrice) : null,
        village: village.trim()
      }});
      setActionMessage(`${t.requestSent}: offer #${result.id}`);
    } catch (e) { setActionMessage(e.message); if (/sign-in|token|auth/i.test(e.message)) setAuthOpen(true); }
  }

  const tabs = [
    ["compare", <BarChart3 size={17} />, t.compare],
    ["trucks", <Truck size={17} />, t.trucks],
    ["buyers", <Users size={17} />, t.buyers],
    ["advice", <Sprout size={17} />, t.advice],
    ["analytics", <BarChart3 size={17} />, "Price analytics"]
  ];

  return <div className="app-shell">
    <header className="topbar">
      <div className="brandmark"><div className="logo"><Leaf size={25}/></div><div><h1>Smart Mandi</h1><p>{t.tagline}</p></div></div>
      <div className="top-actions">
        <span className="pilot-pill">Andhra Pradesh · 26 districts</span>
        <button className="language" onClick={() => setLang(lang === "en" ? "te" : "en")}><Languages size={16}/>{lang === "en" ? "తెలుగు" : "English"}</button>
        {session ? <button className="signin secondary" onClick={signOut}><LogOut size={16}/>{t.signOut}</button> : <button className="signin" onClick={() => setAuthOpen(true)}><LogIn size={16}/>{t.signIn}</button>}
      </div>
    </header>

    <main className="layout">
      <aside className="sidebar">
        <section className="panel">
          <div className="panel-heading"><span className="eyebrow">{t.browse}</span><ShieldCheck size={18}/></div>
          <label htmlFor="district-search">{t.district} · {districts.length} available</label>
          <input
            id="district-search"
            className="search-input"
            type="search"
            value={districtSearch}
            placeholder={lang === "te" ? "జిల్లా పేరుతో వెతకండి..." : "Search all Andhra Pradesh districts..."}
            onChange={e => setDistrictSearch(e.target.value)}
            aria-label="Search districts"
          />
          <select value={district} onChange={e => setDistrict(e.target.value)} aria-label="Select district">
            {visibleDistricts.map(d => <option key={d.id} value={d.id}>{lang === "te" ? d.name_te : d.name_en}</option>)}
          </select>
          {districtSearch && <p className="district-search-count">{filteredDistricts.length} matching district(s)</p>}
          <label>{t.crop}</label>
          <input className="search-input" placeholder={t.search} value={currentCrop ? (lang === "te" ? currentCrop.name_te : currentCrop.name_en) : crop} onChange={e => {
            const q = e.target.value.toLowerCase();
            const found = crops.find(c => (c.name_en + " " + c.name_te + " " + c.aliases.join(" ")).toLowerCase().includes(q));
            if (found) setCrop(found.id);
          }} />
          <div className="crop-grid">
            {crops.map(c => <button key={c.id} className={`crop-chip ${crop === c.id ? "selected" : ""}`} onClick={() => setCrop(c.id)}>{lang === "te" ? c.name_te : c.name_en}</button>)}
          </div>
          <label>{t.quantity}</label>
          <input type="number" min="0.1" max="40" step="0.1" value={quantity} onChange={e => setQuantity(e.target.value)} />
          <label>{t.village}</label>
          <input value={village} maxLength={120} placeholder="e.g. village / mandal" onChange={e => setVillage(e.target.value)} />
          <label className="check-row"><input type="checkbox" checked={share} onChange={e => setShare(e.target.checked)}/><span>Share freight with a neighbour (estimate)</span></label>
          <button className="button-outline full" onClick={load}><RefreshCw size={16}/>{t.refresh}</button>
        </section>
        <section className="panel small-panel">
          <h3>How we calculate</h3>
          <p><strong>Estimated net = modal price × quantity − estimated freight.</strong></p>
          <p>Loading, commission, quality deductions and other charges are excluded unless provided.</p>
          <p className="warning-text">{t.note}</p>
        </section>
      </aside>

      <section className="content">
        <div className="hero">
          <div><span className="eyebrow">SMART MANDI • ANDHRA PRADESH</span><h2>Find the market that leaves more in your hand.</h2><p>Compare estimated take-home earnings—not just the highest posted price.</p></div>
          <div className="hero-icon"><Sprout size={54}/></div>
        </div>
<div className="demo-banner">
          <span className="demo-dot" />
          {prices.length === 0
            ? "No prices available for this selection"
            : prices.every(p => p.is_demo)
              ? "DEMO DATA — not live market information"
              : prices.every(p => !p.is_demo && p.source_type === "government")
                ? "Government-reported prices — check report date"
                : "Mixed data — government and demo/other prices are shown"}
          <span>• {districtName(district)}</span>
        </div>
        <nav className="tabs">{tabs.map(([id, icon, label]) => <button key={id} className={tab === id ? "active" : ""} onClick={() => {setTab(id); setActionMessage("");}}>{icon}{label}</button>)}</nav>

        {loading && <div className="notice">Loading data…</div>}
        {error && <div className="notice error">{error} <button onClick={load}>Retry</button></div>}
        {actionMessage && <div className="notice">{actionMessage}</div>}

        {tab === "compare" && <div className="section-stack">
          <div className="section-title"><div><h3>{t.prices}</h3><p>Filter records by market, source and reporting date.</p></div><span className="count">{prices.length} records</span></div>
          <div className="source-filters" role="group" aria-label="Filter prices by source">
            <button type="button" className={priceSource === "all" ? "active" : ""} aria-pressed={priceSource === "all"} onClick={() => setPriceSource("all")}>All prices</button>
            <button type="button" className={priceSource === "government" ? "active" : ""} aria-pressed={priceSource === "government"} onClick={() => setPriceSource("government")}>Government only</button>
            <button type="button" className={priceSource === "demo" ? "active" : ""} aria-pressed={priceSource === "demo"} onClick={() => setPriceSource("demo")}>Demo only</button>
          </div>
          <div className="filter-row">
            <label>Market<select value={marketFilter} onChange={e => setMarketFilter(e.target.value)}><option value="">All markets</option>{markets.map(m => <option key={m.id} value={m.id}>{lang === "te" ? m.name_te : m.name_en}</option>)}</select></label>
            <label>From date<input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} /></label>
            <label>To date<input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} /></label>
            <button className="signin secondary" onClick={() => {setMarketFilter("");setDateFrom("");setDateTo("");}}>Clear filters</button>
          </div>
          {prices.length === 0 && !loading && <div className="empty">{t.welcome}</div>}
          {prices.length === 0 && !loading && <div className="empty">No {priceSource === "government" ? "government" : priceSource === "demo" ? "demo" : "market"} prices are available for this district, crop, market, and date range.</div>}
          <div className="price-grid">{prices.map(p => <article className="price-card" key={`${p.market_id}-${p.crop_id || crop}-${p.price_date}-${p.source_type}`}>
            <div className="price-head"><div><h4>{lang === "te" ? p.market_name_te : p.market_name_en}</h4><p>{districtName(p.district_id)}</p></div><span className="source-tag">{p.is_demo ? "Demo" : p.source_type === "government" ? "Government" : (p.source_type || "Other source")}</span></div>
            <div className="modal-price">{money(p.modal_price)}<small> / quintal</small></div>
            <div className="range-row"><span>Min <b>{money(p.min_price)}</b></span><span>Max <b>{money(p.max_price)}</b></span></div>
            <div className="card-meta"><span>{t.source}: {p.source_name}</span><span>{p.price_date} · {p.freshness || "freshness unknown"}</span></div>
          </article>)}</div>
          <div className="section-title"><div><h3>{t.compare}</h3><p>Ranked by estimated net after freight.</p></div></div>
          <div className="comparison-list">{comparison.map((r, i) => <article className={`comparison-card ${i === 0 ? "best" : ""}`} key={r.market_id}>
            <div className="rank">{i + 1}</div><div className="comparison-main"><div className="comparison-title"><h4>{lang === "te" ? r.market_name_te : r.market_name_en}</h4>{i === 0 && <span className="best-tag">Best estimate</span>}</div>
              <div className="comparison-bar"><div style={{ width: `${Math.max(0, Math.min(100, Number(r.gross_value) ? (Number(r.estimated_net) / Number(r.gross_value)) * 100 : 0))}%` }} /></div>
              <div className="breakdown"><span>{t.gross}: <b>{money(r.gross_value)}</b></span><span>{t.freight}: <b>{r.estimated_freight == null ? "No verified quote" : money(r.estimated_freight)}</b></span><small>{r.freight_method || "Freight method unknown"}</small></div>
            </div><div className="net-value"><small>{t.net}</small><strong>{r.estimated_net == null ? "Quote needed" : money(r.estimated_net)}</strong></div>
          </article>)}</div>
          <p className="muted-foot">Rates are for comparison only. Confirm today's rate, grade, deductions and freight with the market/truck operator.</p>
        </div>}

        {tab === "trucks" && <div className="section-stack">
          <div className="section-title"><div><h3>Verified trucks</h3><p>Only verified listings are shown to farmers.</p></div><span className="count">{trucks.length}</span></div>
          {!trucks.length && <div className="empty">No verified trucks are currently listed for this district and load. Ask the pilot administrator to verify a truck.</div>}
          <div className="truck-grid">{trucks.map(tr => <article className="truck-card" key={tr.id}><div className="truck-icon"><Truck size={26}/></div><div className="truck-content"><h4>{tr.display_name}</h4><p>{tr.vehicle_label}</p><div className="truck-stats"><span>{tr.capacity_quintals} quintals capacity</span><span>{money(tr.base_freight)} base quote</span></div><div className="verified"><ShieldCheck size={15}/> ID and vehicle documents verified</div></div></article>)}</div>
          <form className="form-panel" onSubmit={createBooking}>
            <h3>{t.book}</h3><p>{t.bookingHint}</p>
            <label>Destination market</label><select value={bookingMarket} onChange={e => setBookingMarket(e.target.value)}>{comparison.map(r => <option key={r.market_id} value={r.market_id}>{r.market_name_en}</option>)}</select>
            <label>Truck (optional; admin may assign)</label><select value={bookingTruck} onChange={e => setBookingTruck(e.target.value)}><option value="">No specific truck</option>{trucks.map(tr => <option value={tr.id} key={tr.id}>{tr.display_name} — {tr.capacity_quintals} q</option>)}</select>
            <button className="button-primary" type="submit">{t.book}<ArrowRight size={16}/></button>
          </form>
        </div>}

        {tab === "buyers" && <div className="section-stack">
          <div className="section-title"><div><h3>{t.buyers}</h3><p>Buyer cards only show listings that are verified and active.</p></div><span className="count">{buyers.length}</span></div>
          {!buyers.length && <div className="empty">No verified buyers for this crop and district are currently available.</div>}
          <div className="buyer-grid">{buyers.map(b => <article className="buyer-card" key={b.id}><div className="buyer-icon"><Users size={24}/></div><div><span className="source-tag">{b.buyer_type}</span><h4>{b.display_name}</h4><p>Accepts: {b.crops_accepted.map(cropName).join(", ")}</p><p>Minimum: {b.min_quantity_quintals} quintals</p>{b.offer_price_per_quintal && <strong>{money(b.offer_price_per_quintal)} / quintal (indicative)</strong>}</div></article>)}</div>
          <form className="form-panel" onSubmit={createOffer}>
            <h3>{t.offer}</h3><p>Submitting an offer is not a confirmed sale.</p>
            <label>{t.buyer}</label><select required value={offerBuyer} onChange={e => setOfferBuyer(e.target.value)}><option value="">Choose buyer</option>{buyers.map(b => <option key={b.id} value={b.id}>{b.display_name}</option>)}</select>
            <label>{t.expected}</label><input type="number" min="1" value={expectedPrice} onChange={e => setExpectedPrice(e.target.value)} placeholder="Optional"/>
            <button className="button-primary" type="submit">{t.offer}<ArrowRight size={16}/></button>
          </form>
        </div>}

        {tab === "analytics" && <PriceAnalytics crop={crop} market={marketFilter || markets[0]?.id || ""} cropName={cropName} />}

        {tab === "advice" && <div className="section-stack">
          <div className="section-title"><div><h3>{t.advice}</h3><p>Baseline scoring model from the project brief.</p></div><span className="count">Illustrative</span></div>
          <div className="notice warning">Scores are demo placeholders, not verified agronomic recommendations. Validate local costs, water, season and historical prices before relying on this page.</div>
          <div className="advice-list">{advice.map(a => <article className="advice-card" key={a.crop_id}><div className="advice-rank">{a.score}</div><div className="advice-main"><h4>{cropName(a.crop_id)}</h4><p>{t.why}: margin {a.margin_score}/100 · stability {a.price_stability_score}/100 · glut risk {a.glut_risk}/100</p><div className="comparison-bar"><div style={{width: `${a.score}%`}}/></div><small>{a.explanation}</small></div></article>)}</div>
        </div>}

        <footer className="footer"><span>Smart Mandi · Fair prices for every farmer</span><span><MapPin size={14}/> All 26 Andhra Pradesh districts · Prices depend on data availability</span></footer>
      </section>
    </main>

    {authOpen && <div className="modal-backdrop" role="presentation" onMouseDown={e => { if (e.target === e.currentTarget && !authBusy) { setAuthOpen(false); setAuthMessage(""); } }}>
      <section className="auth-modal" role="dialog" aria-modal="true" aria-labelledby="auth-heading">
        <button className="modal-close" type="button" onClick={() => { if (!authBusy) { setAuthOpen(false); setAuthMessage(""); } }} aria-label={t.close}>×</button>
        <div className="auth-icon"><ShieldCheck size={28}/></div>
        <h2 id="auth-heading">{authMode === "signup" ? "Create your Smart Mandi account" : "Sign in to Smart Mandi"}</h2>
        <p>Browse market prices without signing in. Sign in is required to submit a truck booking or buyer offer.</p>
        {!supabaseConfigured && <div className="notice warning">{t.noAuth} Add the Supabase URL and publishable/anon key to frontend/.env, then restart Vite.</div>}

        <div className="auth-tabs" role="group" aria-label="Account action">
          <button type="button" disabled={authBusy} className={authMode === "signin" ? "active" : ""} onClick={() => { setAuthMode("signin"); setAuthMessage(""); setCodeSent(false); setOtp(""); }}>Sign in</button>
          <button type="button" disabled={authBusy} className={authMode === "signup" ? "active" : ""} onClick={() => { setAuthMode("signup"); setAuthMessage(""); setCodeSent(false); setOtp(""); }}>Sign up</button>
        </div>
        <div className="auth-tabs" role="group" aria-label="Verification method">
          <button type="button" disabled={authBusy} className={authMethod === "email" ? "active" : ""} onClick={() => { setAuthMethod("email"); setAuthMessage(""); setCodeSent(false); setOtp(""); }}>Email</button>
          <button type="button" disabled={authBusy} className={authMethod === "phone" ? "active" : ""} onClick={() => { setAuthMethod("phone"); setAuthMessage(""); setCodeSent(false); setOtp(""); }}>Phone OTP</button>
        </div>

        <form onSubmit={sendCode}>
          <label htmlFor="auth-identity">{authMethod === "email" ? t.email : t.phone}</label>
          <input
            id="auth-identity"
            required
            type={authMethod === "email" ? "email" : "tel"}
            autoComplete={authMethod === "email" ? "email" : "tel"}
            value={identity}
            onChange={e => { setIdentity(e.target.value); setCodeSent(false); setOtp(""); }}
            placeholder={authMethod === "email" ? "you@example.com" : "+919876543210"}
          />
          <button className="button-primary full" type="submit" disabled={authBusy || !supabaseConfigured}>
            {authBusy ? "Please wait…" : codeSent ? "Send code again" : authMode === "signup" ? "Create account and send code" : t.sendCode}
          </button>
        </form>

        <form onSubmit={verifyCode}>
          <label htmlFor="auth-otp">{t.code}</label>
          <input id="auth-otp" required value={otp} onChange={e => setOtp(e.target.value)} inputMode="numeric" autoComplete="one-time-code" placeholder="Enter the OTP" disabled={!codeSent || authBusy}/>
          <button className="button-outline full" type="submit" disabled={authBusy || !codeSent || !supabaseConfigured}>{authBusy ? "Please wait…" : t.verify}</button>
        </form>

        {authMessage && <div className={/failed|error|valid|could not|not configured/i.test(authMessage) ? "notice error" : "notice"} role="status">{authMessage}</div>}
        <p className="small-muted">Phone OTP requires a configured SMS provider in Supabase. Email OTP codes require an email template containing the OTP variable; if the template sends a magic link, use that link instead. For sign-in, the account must already exist; sign-up can create an account.</p>
      </section>
    </div>}
  </div>;
}
