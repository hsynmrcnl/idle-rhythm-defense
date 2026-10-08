/* ================= örnek sesler (sample layer) =================
   İki kayıt seti: Yeni (varsayılan) = CC0 kütüphaneler (VSCO 2 CE, VCSL, Karoryfer, Virtuosity Drums; tools/build_sf_cc0.py → sf/c_*.json),
   Klasik = FluidR3 General MIDI soundfont (MIT) bölgeleri, WebAudioFont verisinden (MIT) paketlendi. Yeni sette karşılığı olmayan enstrüman klasik pakete düşer.
   Dosyalar sayfanın yanında durur (sf/*.json: artifact dosyaları / standalone klasörü); dış sunucu gerekmez, yüklenemezse sentez devam eder.
   Bölge = bir kayıt + tuş aralığı + loop noktaları: perde playbackRate ile, uzun nota loop ile tutulur. */
let SF_DIR=(typeof window!=='undefined'&&window.NB_SF_DIR)||'sf/';
/* oyun enstrümanı → GM programı (dosya). Listede olmayanlar sentez kalır: saz, 808, lead, arpej, theremin, gürültü, didgeridoo, tabla */
const SF_PROG={bas:'0330',akustik:'0250',gitar:'0300',keman:'0400',cello:'0420',harp:'0460',akor:'0890',rhodes:'0040',piyano:'0000',org:'0160',klavsen:'0060',ney:'0770',flut:'0730',trompet:'0560',sakso:'0650',tuba:'0580',zurna:'1110',vocoder:'0540',kalimba:'1080',steel:'1140',timbal:'0470',taiko:'1160',gamelan:'0140'};
/* vurmalı → GM davul notası; çift: [düm, tek] (darbuka) ya da [normal, aksan] */
/* Yeni set (S.sfset!=='klasik'): enstrüman → c_ paketi; davul seti c_drums. Ölçek dışı / ezgi dışı enstrümanlar klasik pakete düşer */
const SF_NEW={piyano:'c_piyano',klavsen:'c_klavsen',keman:'c_keman',cello:'c_cello',harp:'c_harp',bas:'c_bas',trompet:'c_trompet',tuba:'c_tuba',flut:'c_flut',sakso:'c_sakso',kalimba:'c_kalimba',steel:'c_steel',didger:'c_didger'};
const sfNewSet=()=>S.sfset!=='klasik';
const sfProg=id=>(sfNewSet()&&SF_NEW[id])||SF_PROG[id];
const sfDK=()=>sfNewSet()?'c_drums':'drums';
const SF_DRUM={davul:36,trampet:38,hihat:[42,46],clap:39,shaker:70,kasik:75,tom:[45,47],darbuka:[61,60],bendir:41,zil:49,gong:52};
/* sönen enstrümanlar: loop'lu kayıt bu sürede (sn) söner; olmayanlar tutulur (yay, nefesli, org, pad, ses) */
const SF_DEC={'0000':2.6,'0040':2.2,'0060':1.2,'0140':3.5,'0250':1.8,'0300':2.2,'0330':1.4,'0360':1.2,'0460':2.4,'0470':1.6,'1080':1.1,'1140':1.6,'1160':1.2,c_piyano:2.6,c_klavsen:1.2,c_harp:2.4,c_bas:1.4,c_kalimba:1.1,c_steel:1.6};
const SF_GAIN={bas:1.15,gitar:0.85,akustik:0.9,harp:0.9,akor:0.7,org:0.8,vocoder:0.7,timbal:1.3,taiko:1.5,ney:0.4,flut:0.5,piyano:0.5,rhodes:0.6,klavsen:0.6,kalimba:0.7,steel:0.7,gamelan:0.7,zurna:0.6,trompet:0.7,sakso:0.7,tuba:0.9,didger:0.8};
const SF_DGAIN={davul:1.2,trampet:0.45,hihat:0.2,clap:0.5,shaker:0.3,kasik:0.4,tom:0.7,darbuka:0.6,bendir:0.9,zil:0.4,gong:0.6};
const sfVol=()=>clamp(+(S.sfv||1),0.25,2); /* genel örnek ses seviyesi: Görünüm → Efekt laboratuvarı */
let SF_VOL=1;
const SF={};
const sfOn=()=>S.sfx!==false;
function sfLoad(key){if(SF[key])return SF[key].p;const st=SF[key]={st:'loading',zones:[],name:key};
 if(location.protocol==='file:'){st.st='fail';st.err='file';st.p=Promise.resolve(false);sfStatus();return st.p} /* diskten açılınca fetch yok: sentez */
 st.p=fetch(SF_DIR+key+'.json').then(r=>{if(!r.ok)throw new Error('http '+r.status);return r.json()}).then(async h=>{if(!h||h.fmt!=='nbsf1'||!Array.isArray(h.zones))throw new Error('format');st.name=h.name;
  const zs=await Promise.all(h.zones.map(z=>{const u=b64dec(z.mp3);const q=Object.assign({},z);delete q.mp3;return ac.decodeAudioData(u.buffer).then(buf=>Object.assign(q,{buf}),()=>null)}));st.zones=zs.filter(Boolean);st.st=st.zones.length?'ok':'fail';return st.st==='ok'}).catch(e=>{st.st='fail';st.err=String(e&&e.message||e);return false}).then(ok=>{sfStatus();return ok});return st.p}
function sfZone(key,m){const st=SF[key];if(!st||st.st!=='ok')return null;let best=null,bd=1e9;for(const z of st.zones){if(m>=z.lo&&m<=z.hi)return z;const d=m<z.lo?z.lo-m:m-z.hi;if(d<bd){bd=d;best=z}}return best}
const sfKey=x=>x?sfProg(x.id):null;
function sfReady(x){if(!x||!sfOn())return false;const k=sfKey(x);if(k)return !!(SF[k]&&SF[k].st==='ok');const dk=sfDK();return !!(SF_DRUM[x.id]&&SF[dk]&&SF[dk].st==='ok')}
function sfLoadStage(){if(!sfOn()||!ac)return;S.slots.forEach(id=>{if(!id)return;if(sfProg(id))sfLoad(sfProg(id));if(SF_DRUM[id])sfLoad(sfDK());if(id==='bas'&&S.up.tk_tel2)sfLoad('0360')})}
function sfStatus(){const el=document.getElementById('sfInfo');if(!el)return;const keys=[...new Set(S.slots.filter(id=>id&&(sfProg(id)||SF_DRUM[id])).map(id=>sfProg(id)||sfDK()))];if(!sfOn()){el.textContent=T('Örnek sesler kapalı: sentez');return}if(!keys.length){el.textContent=T('Sahnede örneklenmiş enstrüman yok');return}const ok=keys.filter(k=>SF[k]&&SF[k].st==='ok').length,fail=keys.filter(k=>SF[k]&&SF[k].st==='fail').length;el.textContent=T('Örnek sesler')+': '+ok+' / '+keys.length+' '+T('yüklendi')+(fail?' · '+fail+' '+T('yüklenemedi, sentez kullanılıyor'):'')}
/* teknikler: playbackRate etrafında (r = temel oran) */
function sfArt(pr,t,dur,art,r){pr.setValueAtTime(r*(art==='slide'?Math.pow(2,-5/12):1.008),t);if(art==='slide')pr.exponentialRampToValueAtTime(r,t+Math.min(0.18,dur*0.5));else pr.exponentialRampToValueAtTime(r,t+0.07);
 if(art==='bend'){const t1=t+Math.min(0.25,dur*0.3),t2=t+Math.min(0.6,dur*0.65);pr.setValueAtTime(r,t1);pr.exponentialRampToValueAtTime(r*Math.pow(2,2/12),t2)}
 if(art==='vib'||art==='fb'||art==='growl'||(art==='none'&&dur>1.2)){const l=ac.createOscillator(),lg=ac.createGain();l.frequency.value=art==='fb'?5.2:art==='growl'?26:5.6;lg.gain.setValueAtTime(0,t);lg.gain.linearRampToValueAtTime(r*(art==='none'?0.006:art==='growl'?0.018:0.012),t+Math.min(0.5,dur*0.4));l.connect(lg);lg.connect(pr);l.start(t);l.stop(t+dur+0.1)}}
/* bir bölgeyi çal: m = MIDI (kesirli olabilir), a = genlik, dur = tutma süresi; hold → loop (sönenlerde loop + sönme zarfı) */
function sfPlay(key,z,t,m,a,dur,art,hold,dest){const src=ac.createBufferSource();src.buffer=z.buf;const base=z.pitch-100*z.coarse-z.fine,r=Math.pow(2,(100*m-base)/1200);src.playbackRate.value=r;if(art&&art!=='none')sfArt(src.playbackRate,t,dur,art,r);else if(dur>1.2)sfArt(src.playbackRate,t,dur,'none',r);
 const loop=!!hold&&z.loopEnd>z.loopStart+1;if(loop){src.loop=true;src.loopStart=z.loopStart/z.sr;src.loopEnd=z.loopEnd/z.sr}
 const dec=SF_DEC[key],g=ac.createGain(),amp=Math.max(0.0002,a*SF_VOL*sfVol()*0.085/(z.rms||0.25)),rel=loop?0.16:0.3;g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(amp,t+0.008);
 if(loop&&dec){g.gain.setTargetAtTime(0.0001,t+0.05,dec/4)}else g.gain.setValueAtTime(amp,t+Math.max(0.01,dur-0.02));g.gain.exponentialRampToValueAtTime(0.0001,t+dur+rel);
 src.connect(g);g.connect(dest||music);if((dest||music)!==drum)g.connect(send);src.start(t);src.stop(t+dur+rel+0.05);
 if(art==='growl'){const ng=ac.createGain();ng.gain.value=0.35;const l=ac.createOscillator();l.type='square';l.frequency.value=31;const lg=ac.createGain();lg.gain.value=amp*0.5;l.connect(lg);lg.connect(g.gain);l.start(t);l.stop(t+dur+0.1)}
 return src}
function sfNote(key,t,f,a,dur,art,hold,dest){const m=f?69+12*Math.log2(f/440):null;const z=sfZone(key,m==null?60:Math.round(m));if(!z)return false;sfPlay(key,z,t,m==null?z.pitch/100:m,a,dur,art,hold,dest);return true}
/* desen notası: akor/arp/kök seçimi sentezle aynı (pitchOf), vurmalılar davul setinden */
function sfVoice(x,t,a,s){if(!sfReady(x))return false;const key=sfKey(x),p=x.v;
 if(!key)return sfDrum(x,t,a,s);
 const fs=!p.pitch?[null]:p.pitch==='chord'?chordAt(s).map(f=>f*Math.pow(2,p.oct||0)):[pitchOf(p,s)];const dur=Math.max(0.25,(p.dur||0.6)*(p.pitch==='chord'?1.2:1));const ga=(SF_GAIN[x.id]||1)*a*(fs.length>1?0.7:1);let ok=true;fs.forEach((f,k)=>{if(!sfNote(key,t+k*(p.strum||0.012),f,ga,dur,null,false,x.fam==='vur'?drum:null))ok=false});return ok}
function sfDrum(x,t,a,s){const d=SF_DRUM[x.id],K=SF[sfDK()];if(!d||!K||K.st!=='ok')return false;let n=d;if(Array.isArray(d))n=x.v.g==='darb'?((MI.pos[s]===0||MI.pos[s]===2)?d[0]:d[1]):(a>1?d[1]:d[0]);const z=K.zones.find(q=>q.lo===n);if(!z)return false;
 const src=ac.createBufferSource();src.buffer=z.buf;const g=ac.createGain();g.gain.value=(SF_DGAIN[x.id]||0.7)*Math.min(1.6,a)*SF_VOL*sfVol()*0.9/(z.pk||1);src.connect(g);g.connect(drum);if(x.id==='zil'||x.id==='gong'||x.id==='bendir')g.connect(send);src.start(t);src.stop(t+z.buf.duration+0.05);return true}
/* solo notası: slap/pop için slap bas programı, feedback için üst oktav ıslığı eklenir */
function sfSolo(x,t,row,hold,art,a){if(!sfReady(x))return false;let key=sfKey(x);if(!key)return false;const f=soloFreq2(x,row);a=a||1;
 if(x.id==='bas'&&(art==='slap'||art==='pop')){if(SF['0360']&&SF['0360'].st==='ok')key='0360';if(!sfNote(key,t,f*(art==='pop'?2:1),1.1*a,Math.max(0.2,hold),'none',true))return false;Nz(t,'bandpass',art==='pop'?3800:1800,1,(art==='pop'?0.2:0.14)*a,0.01,music);return true}
 if(!sfNote(key,t,f,(SF_GAIN[x.id]||1)*1.15*a,Math.max(0.2,hold),art,true))return false;
 if(art==='fb'){const fb=ac.createOscillator(),fg=ac.createGain();fb.type='sine';fb.frequency.value=f*2;fg.gain.setValueAtTime(0.0001,t);fg.gain.exponentialRampToValueAtTime(0.1*a,t+hold*0.7);fg.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.1);fb.connect(fg);fg.connect(music);fb.start(t);fb.stop(t+hold+0.2)}
 return true}

