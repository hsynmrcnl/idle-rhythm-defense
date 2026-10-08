
/* ================= state ================= */
const mkPat=()=>Array.from({length:MAXSLOTS},()=>Array(18).fill(0));
const freshRun=()=>{const A=mkPat();A[0][0]=1;A[0][8]=1;return{nota:25,slots:['davul',null,null,null],lv:{davul:1},pat:{A,B:mkPat(),S:mkPat(),F:mkPat()},edit:'A',bpm:90,bmax:90,seri:0,up:{},def:{},solo:{},solos:{},plan:null,needle:{},wave:1,runEarned:0,meter:'m44',scale:'minor',prog:Array(8).fill('pop'),prate:'beat'}};
const freshMeta=()=>({v:3,hayran:0,albums:[],found:{},theme:'neon',themes:{neon:1},famOpen:{vur:1},layout:'circle',stage:{},fxo:{},orders:[],bestWave:1,kills:0,total:0,muted:false,buy:1,last:Date.now(),tut:{s:0,done:false},mn:{},auto:{lv:true,ord:true,ins:true,alb:false},efsane:0,cities:{},tours:0,city:0,sfx:true,lang:'tr',open:{},sfset:'yeni'});
const KEY='nabiz-cemberi-v3';
let S=Object.assign(freshRun(),freshMeta());
try{const raw=localStorage.getItem(KEY);if(raw){const d=JSON.parse(raw);if(d&&d.v===3&&d.pat&&Array.isArray(d.pat.A)&&Array.isArray(d.slots)){S=Object.assign(S,d);if(!d.tut)S.tut=null}}}catch(e){}
function normalizeS(){
['up','def','found','stage','fxo','lv','themes','famOpen','solo','needle','solos','open'].forEach(k=>{if(!S[k]||typeof S[k]!=='object')S[k]={}});
if(!Array.isArray(S.orders))S.orders=[];
while(S.pat.A.length<MAXSLOTS)S.pat.A.push(Array(18).fill(0));
while(S.pat.B.length<MAXSLOTS)S.pat.B.push(Array(18).fill(0));if(!Array.isArray(S.pat.S))S.pat.S=mkPat();while(S.pat.S.length<MAXSLOTS)S.pat.S.push(Array(18).fill(0));if(S.edit==='S'&&!S.up.solo)S.edit='A';
if(!Array.isArray(S.pat.F))S.pat.F=mkPat();while(S.pat.F.length<MAXSLOTS)S.pat.F.push(Array(18).fill(0));if(S.edit==='F'&&!S.up.dolgu)S.edit='A';
if(!Array.isArray(S.prog)||S.prog.length!==8)S.prog=Array(8).fill('pop');if(S.prate!=='bar')S.prate='beat';
S.slots=S.slots.slice(0,MAXSLOTS).map(id=>id&&IDX[id]?id:null);
while(S.slots.length<4)S.slots.push(null);
if(!S.bmax)S.bmax=Math.max(90,S.bpm);
if(!THEMES[S.theme])S.theme='neon';if(!METERS[S.meter])S.meter='m44';if(!SCALES[S.scale])S.scale='minor';if(S.layout!=='strip')S.layout='circle';
S.wave=Math.max(1,Math.floor(S.wave||1));S.bestWave=Math.max(S.bestWave||1,S.wave);
S.albMax=Math.max(S.albMax||0,S.albums.length);S.themes.neon=1;THEME_ORDER.forEach(id=>{if(THEMES[id].al>0&&albUnl()>=THEMES[id].al)S.themes[id]=1});
S.famOpen.vur=1;[['tel',5],['tus',12],['nef',20],['ele',30],['dun',45]].forEach(([f,w])=>{if(S.bestWave>=w)S.famOpen[f]=1});
if(S.stage.crown){S.stage.wall=1;delete S.stage.crown}
if(!S.themes[S.theme])S.theme='neon';
 if(!S.tut||typeof S.tut!=='object')S.tut={s:0,done:(S.kills>0||S.albums.length>0||Object.keys(S.lv).length>1||(S.total||0)>50)};
 if(S.sfx!==false)S.sfx=true;if(S.lang!=='en')S.lang='tr';
 if(!S.mn||typeof S.mn!=='object')S.mn={};if(!S.auto||typeof S.auto!=='object')S.auto={lv:true,ord:true,ins:true,alb:false};if(!S.cities||typeof S.cities!=='object')S.cities={};S.efsane=Math.max(0,Math.floor(S.efsane||0));S.tours=Math.max(0,Math.floor(S.tours||0));S.city=((S.city|0)%CITIES.length+CITIES.length)%CITIES.length;
}
normalizeS();
const b64enc=u8=>{let s='';for(let i=0;i<u8.length;i+=0x8000)s+=String.fromCharCode.apply(null,u8.subarray(i,i+0x8000));return btoa(s)};
const b64dec=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function exportCode(){const json=JSON.stringify(S);try{if(window.CompressionStream){const cs=new CompressionStream('deflate-raw'),w=cs.writable.getWriter();w.write(new TextEncoder().encode(json));w.close();const buf=await new Response(cs.readable).arrayBuffer();return 'NB2.'+b64enc(new Uint8Array(buf))}}catch(e){}return 'NB1.'+b64enc(new TextEncoder().encode(json))}
async function parseCode(code){code=(code||'').replace(/\s+/g,'');if(!/^NB[12]\./.test(code))throw new Error('Bu bir Nabız Çemberi kayıt kodu değil');const body=code.slice(4);let bytes;if(code.startsWith('NB2.')){const ds=new DecompressionStream('deflate-raw'),w=ds.writable.getWriter();w.write(b64dec(body));w.close();bytes=new Uint8Array(await new Response(ds.readable).arrayBuffer())}else bytes=b64dec(body);const d=JSON.parse(new TextDecoder().decode(bytes));if(!(d&&d.v===3&&d.pat&&Array.isArray(d.pat.A)&&Array.isArray(d.slots)))throw new Error('Kod bozuk ya da eksik');return d}
let demoMode=false,demoSnap=null;
function save(){if(demoMode)return;S.last=Date.now();try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}}

let MI=null;
function meterInfo(){const m=METERS[S.meter];const gs=[],grp=[],pos=[];let a=0;m.g.forEach((len,gi)=>{gs.push(a);for(let k=0;k<len;k++){grp.push(gi);pos.push(k)}a+=len});return{N:a,g:m.g,gs,gsSet:new Set(gs),grp,pos,mids:gs.map(s=>s+2)}}
MI=meterInfo();
function meterInfoFor(k){const sv=S.meter;S.meter=k;const m=meterInfo();S.meter=sv;return m}

let previewId=null,previewUntil=0;
const dispTheme=()=>THEMES[previewId&&performance.now()<previewUntil?previewId:S.theme];
const ownTheme=()=>THEMES[S.theme];
const albumsN=()=>S.albums.length;
function albUnl(){return Math.max(S.albums.length,S.albMax||0)}
const hasB=()=>albUnl()>=1;
const themeOwned=id=>!!S.themes[id];
const famOpen=f=>!!S.famOpen[f];
const famCond=f=>FAMS.find(x=>x[0]===f)[2];
function famReqs(f){const c=famCond(f),r=[];if(c.wave)r.push({t:'En iyi dalga '+c.wave,ok:S.bestWave>=c.wave});if(c.albums)r.push({t:c.albums+' albüm',ok:albUnl()>=c.albums});if(c.fans)r.push({t:c.fans+' hayran',ok:S.hayran>=c.fans});if(c.cost)r.push({t:'♪ '+fmt(c.cost)+' ödeme',ok:S.nota>=c.cost});return r}
const famCanOpen=f=>famReqs(f).every(r=>r.ok);
const nextFam=()=>FAMS.find(x=>!famOpen(x[0]));
const slotIns=si=>{const id=S.slots[si];return id?IDX[id]:null};
const lvOf=id=>S.lv[id]||0;
const insColor=(x,th)=>shade(th.fam[x.fam],SHADES[(x.fi-1)%SHADES.length]);
const roleName=r=>ROLES[r].n;
const isWeapon=r=>!(r==='kalkan'||r==='titresim'||r==='gelir'||r==='destek');
const isSolo=si=>!!(S.up.solo&&S.solo[si]&&S.slots[si]);
const soloK=()=>S.up.solofast?4:8;
const soloSlots=()=>S.slots.map((id,si)=>isSolo(si)?si:-1).filter(x=>x>=0);
function planArr(){if(S.up.sef&&Array.isArray(S.plan)&&S.plan.length===8&&S.plan.every(t=>SECTS[t]))return S.plan;if(S.up.solo&&soloSlots().length)return S.up.solofast?['verse','verse','solo','verse','verse','solo','verse','verse']:['verse','verse','verse','solo','verse','verse','verse','solo'];return hasB()?['verse','chorus','verse','chorus','verse','chorus','verse','chorus']:['verse','verse','verse','verse','verse','verse','verse','verse']}
const planLen=()=>planArr().length*SEC_BARS;
function planAt(b){const pl=planArr();const i=Math.floor(b/SEC_BARS)%pl.length;return{type:pl[i],sec:SECTS[pl[i]],idx:i,barIn:b%SEC_BARS,pl}}
const pkFor=b=>planAt(b).sec.pk==='B'&&bActive()?'B':'A';
function allowed(sec,x,si){if(sec.mask==='all')return true;if(sec.mask==='rhythm')return x.fam==='vur'||x.role==='titresim'||x.role==='destek'||x.role==='kalkan';return x.fam!=='vur'||x.role==='kalkan'}
function dynAt(b){const pa=planAt(b);let d=pa.sec.dyn;if(pa.sec.ramp)d*=1+pa.sec.ramp*(pa.barIn+1)/SEC_BARS*0.5;return d}
function tempoMulAt(b){const pa=planAt(b);return pa.sec.ramp?1+pa.sec.ramp*(pa.barIn+1)/SEC_BARS:1}
function soloActive(b){const ss=soloSlots();if(!ss.length)return -1;const pa=planAt(b);if(!pa.sec.solo)return -1;const occ=pa.pl.slice(0,pa.idx).filter(t=>t==='solo').length,total=pa.pl.filter(t=>t==='solo').length||1,cyc=Math.floor(b/planLen());return ss[(cyc*total+occ)%ss.length]}
const planBonus=()=>new Set(planArr()).size>=4?1.25:1;
/* ---- chord progressions ---- */
function progOf(i){const ps=PROGS[S.scale]||PROGS.minor;const k=(S.up.akor&&S.prog&&ps[S.prog[i]])?S.prog[i]:'pop';return ps[k]||ps.pop}
const chordIdx=(b,s)=>(S.up.akor&&S.prate==='bar')?(b%SEC_BARS)%4:(MI.grp[s]%4);
const curChord=(b,s)=>progOf(planAt(b).idx).c[chordIdx(b,s)];
const scaleBase=()=>SCALES[S.scale].root[0]*2;
const chordSemi=ch=>ch[0]>=5?ch[0]-12:ch[0];
const chordFreqs=ch=>QUAL[ch[1]].map(iv=>scaleBase()*Math.pow(2,(chordSemi(ch)+iv)/12));
const rootFreq=ch=>scaleBase()/2*Math.pow(2,chordSemi(ch)/12);
const chordName=ch=>{const off=Math.round(12*Math.log2(scaleBase()/440)+1200)%12;return NOTE_N[(off+ch[0])%12]+(ch[1]==='m'?'m':ch[1]==='5'?'5':'')};
const kadansAt=i=>{if(!S.up.akor)return false;const pl=planArr(),a=progOf(i).c,b=progOf((i+1)%pl.length).c;return a[3][0]===7&&b[0][0]===0&&a[3][1]!=='5'};
const makamM=i=>(S.up.akor&&(S.scale==='hicaz'||S.scale==='kurdi')&&S.prog[i]==='makam')?1.1:1;
function contrastM(){if(!S.up.akor)return 1;const pl=planArr();const set=new Set();pl.forEach((t,i)=>{if(!SECTS[t].solo)set.add(S.prog[i]||'pop')});return set.size>=2?1.1:1}
/* ---- drum fill ---- */
const fillZone=s=>s>=Math.floor(MI.N/2);
const isFillRow=si=>{const x=slotIns(si);return !!x&&x.fam==='vur'};
function fillHits(){let n=0;S.slots.forEach((id,si)=>{if(!isFillRow(si))return;for(let s=0;s<MI.N;s++)if(fillZone(s)&&S.pat.F[si][s])n++});return n}
const fillOn=()=>!!S.up.dolgu&&fillHits()>0;
const fillBar=b=>fillOn()&&planAt(b).barIn===SEC_BARS-1;
/* multiplier of a section's first bar: cadence resolution and/or fill+crash */
function transM(i){const pl=planArr(),prev=(i-1+pl.length)%pl.length;const k=kadansAt(prev),f=fillOn()&&fillHits()>=4;return k&&f?1.5:(k||f)?1.25:1}
const FILL_M=0.6; /* fills are flourishes: dense but each hit worth 60% */
const fillRowVal=(si,v)=>noteVal(si,v)*(ROWM.A[si]||1)*BK.A.nota*FILL_M;
const fillRowDmg=(si,v)=>dmgOf(si,v)*(ROWM.A[si]||1)*BK.A.dmg*FILL_M;
const SOLO_M=3;
const ART_M={none:1,bend:1.2,vib:1.15,slide:1.1,fb:1.3,slap:1.25,pop:1.2,trem:1.1,growl:1.2,arp:1.15};
const susOf=x=>SUS_OVR[x.id]||SUSP[x.v.solo||'lead']||{k:'hold'};
const tkgOf=x=>TKG[x.v.solo||'lead']||'ele';
/* which techniques an instrument may use, by its solo flavor and the owned branch nodes */
function artOk(x,art){if(!art||art==='none')return true;if(!x)return false;const g=tkgOf(x),fl=x.v.solo||'lead',u=S.up;
 if(g==='tel'){if(art==='bend'||art==='vib'||art==='slide')return !!u.tk_tel1;if(art==='trem')return !!u.tk_tel2&&(fl==='tel'||fl==='saz');if(art==='fb')return !!u.tk_tel2&&fl==='edrive';if(art==='slap'||art==='pop')return !!u.tk_tel2&&fl==='bass';return false}
 if(g==='nef'){if(art==='vib')return !!u.tk_nef1;if(art==='growl'||art==='bend')return !!u.tk_nef2;return false}
 if(g==='tus'){return art==='slide'&&!!u.tk_tus2}
 if(g==='ele'){if(art==='slide'||art==='vib')return !!u.tk_ele1;if(art==='arp')return !!u.tk_ele2;return false}
 return false}
const artEff=(x,art)=>artOk(x,art)?art:'none';
const artList=x=>Object.keys(SOLO_ART).filter(k=>k==='none'||(x&&(function(){const g=tkgOf(x),fl=x.v.solo||'lead';if(g==='tel')return ['bend','vib','slide'].includes(k)||(k==='trem'&&(fl==='tel'||fl==='saz'))||(k==='fb'&&fl==='edrive')||((k==='slap'||k==='pop')&&fl==='bass');if(g==='nef')return ['vib','growl','bend'].includes(k);if(g==='tus')return k==='slide';return ['slide','vib','arp'].includes(k)})()));
/* power of the k-th held step (k>=1); onset is always 1 */
function tickPow(x,k,art){if(!S.up.suzun||!x)return 0;const p=susOf(x),u=S.up;
 if(art==='fb')return k<16?Math.min(1,0.35+0.05*k):-0.5;
 if(art==='trem')return 0.5*Math.pow(1+k,-0.25);
 if(art==='arp')return 0.55;
 if(p.k==='decay'){const d=(u.tk_tus1&&tkgOf(x)==='tus')?Math.max(p.d,0.9):p.d,v=Math.pow(d,k);return v<0.08?0:v}
 if(p.k==='breath'){if(!u.tk_nef1&&k>=p.max)return 0;return Math.pow(1+k,-0.5)}
 return Math.pow(1+k,-0.5)}
const noteLenEff=nt=>S.up.suzun?nt.len:1;
const nr=nt=>Math.min(nt.r,soloRows()-1);
/* sürüklenen nota m, aynı halkada çakışan ya da bitişik notaları yutar: tek bar olur, arada boşluk kalmaz. m'nin tekniği korunur; yeni dizini döner */
function soloMerge(so,m){if(!S.up.suzun||!so||!so.notes.includes(m))return so?so.notes.indexOf(m):-1;const r=nr(m),T=soloSteps();let t0=m.t,t1=m.t+m.len,hit=true;
 while(hit){hit=false;for(let k=0;k<so.notes.length;k++){const q=so.notes[k];if(q===m||nr(q)!==r)continue;const q1=q.t+noteLenEff(q);if(q.t<=t1&&q1>=t0){t0=Math.min(t0,q.t);t1=Math.max(t1,q1);so.notes.splice(k,1);hit=true;break}}}
 m.t=t0;m.len=clamp(t1-t0,1,T-t0);return so.notes.indexOf(m)}
function aliveLen(x,nt){const a=artEff(x,nt.art),L=noteLenEff(nt);for(let k=1;k<L;k++)if(tickPow(x,k,a)<=0)return k;return L}
function noteSus(x,nt){const a=artEff(x,nt.art);let v=0;for(let k=1;k<noteLenEff(nt);k++){const p=tickPow(x,k,a);if(p>0)v+=p}return v}
/* seyir analysis: phrase shape badges, machine-gun habituation */
function analyzeSolo(si){const x=slotIns(si);const ns=soloNotesOf(si).slice().sort((a,b)=>a.t-b.t||a.r-b.r);const R=soloRows(),n=(SOLO_SCALE[S.scale]||SOLO_SCALE.minor).length,T=soloSteps();let run=0,mg=0;const hab=[];
 ns.forEach((nt,i)=>{const pv=ns[i-1];const chain=pv&&noteLenEff(pv)===1&&noteLenEff(nt)===1&&pv.t+1===nt.t;run=chain?run+1:1;const h=Math.pow(HAB,Math.max(0,run-4));if(h<1)mg++;hab.push(h)});
 const last=ns[ns.length-1];const karar=!!x&&!!last&&nr(last)%n===0&&noteLenEff(last)>=2&&last.t+noteLenEff(last)>=T-2&&tickPow(x,1,'none')>0;
 const doruk=!!x&&ns.some(nt=>nr(nt)>=R-Math.ceil(R/3)&&noteLenEff(nt)>=4&&tickPow(x,3,artEff(x,nt.art))>0);
 let gaps=0;for(let i=3;i<ns.length-2;i++){const g=ns[i].t-(ns[i-1].t+noteLenEff(ns[i-1]));if(g>=2)gaps++}const sc=gaps>=1;
 const on=!!S.up.sseyir,mult=on?(karar?1.25:1)*(doruk?1.2:1)*(sc?1.15:1):1;return{ns,hab,karar,doruk,sc,mg,mult,on}}
const duetOn=()=>!!S.up.sduet&&soloSlots().filter(si=>{const x=slotIns(si);return x&&x.fam!=='vur'}).length>=2;
function duetPart(si){if(!duetOn())return -1;const ss=soloSlots().filter(s=>{const x=slotIns(s);return x&&x.fam!=='vur'});const k=ss.indexOf(si);return k<0||k>1?-1:k}
const duetPlays=(si,off)=>{const k=duetPart(si);return k<0?true:Math.floor(off/4)%2===k};
const soloNotesOf=si=>(S.solos[si]&&Array.isArray(S.solos[si].notes))?S.solos[si].notes:[];
const hasSoloNotes=si=>soloNotesOf(si).length>0;
const soloRows=()=>(SOLO_SCALE[S.scale]||SOLO_SCALE.minor).length*(S.up.soktav?2:1)+1;
const soloSteps=()=>MI.N*2;
function soloNoteName(row){const sc=SOLO_SCALE[S.scale]||SOLO_SCALE.minor,n=sc.length,semi=sc[row%n]+12*Math.floor(row/n);const rootN=Math.round(12*Math.log2(SCALES[S.scale].root[0]/440))%12;const names=['A','A#','B','C','C#','D','D#','E','F','F#','G','G#'];return names[(((rootN+semi)%12)+12)%12]+(row>=n?'′':'')}
function genSolo(si,style,seed){const x=slotIns(si);if(!x)return[];const R=soloRows(),T=soloSteps(),r=rng(seed>>>0),st=SOLO_STYLES[style]?style:'hendrix',notes=[];const pick=a=>a[Math.floor(r()*a.length)];let row=Math.floor(R*0.45),t=0;
 const add=(tt,len,rr,art)=>{if(tt>=T||notes.length>=SOLO_MAX)return;len=Math.min(len,T-tt);notes.push({t:tt,len,r:clamp(rr,0,R-1),art:art||'none'})};
 if(st==='hendrix'){while(t<T){const ph=pick([[2,1,1,0,4],[1,1,2,0,0,4],[2,2,0,4],[1,1,1,1,0,2,0,4]]);for(const L of ph){if(t>=T)break;if(L===0){t+=1;continue}row=clamp(row+pick([-2,-1,-1,0,1,1,2]),2,R-2);const long=L>=4;const sc=SOLO_SCALE[S.scale]||SOLO_SCALE.minor,deg=row%sc.length;let art='none';if(long)art=pick(['vib','vib','fb','bend']);else if((deg===1||deg===sc.length-1)&&r()<0.5)art='bend';else if(r()<0.15)art='slide';add(t,L,row,art);if(long&&r()<0.35)add(t,L,row+2,'none');t+=L}t+=pick([0,1,2])}}
 else if(st==='wooten'){while(t<T){const run=pick([4,6,8]);for(let k=0;k<run&&t<T;k++){const oct=r()<0.25?pick([-5,5,6]):pick([-2,-1,1,1,2]);row=clamp(row+oct,0,R-1);const art=t%4===0?'slap':(row>R*0.6&&r()<0.5?'pop':'none');add(t,1,row,art);t+=1}t+=pick([1,2,2,4]);if(r()<0.4){row=clamp(row-3,0,R-1);add(t,2,row,'slap');t+=2}}}
 else if(st==='taksim'){let first=true;while(t<T){if(r()<0.35&&!first){add(t,1,row+pick([-1,1]),'none');t+=1}row=clamp(row+pick([-1,-1,0,1,1,2]),1,R-2);const L=pick([3,4,4,6,8]);add(t,L,row,first?'slide':(L>=4?pick(['vib','vib','none']):'none'));first=false;t+=L;if(r()<0.5)t+=pick([1,2])}}
 else{let dir=1;while(t<T){const L=pick([1,1,2]);row+=dir*pick([1,2,2]);if(row>=R-1||row<=1)dir=-dir;row=clamp(row,0,R-1);add(t,L,row,'none');t+=L;if(r()<0.18){add(t,6,clamp(row+2,0,R-1),'vib');t+=6}}}
 return shapeSolo(notes.sort((a,b)=>a.t-b.t),R,T,st)}
/* post-pass: generated solos resolve on a root row and, for hendrix/taksim, hold a top note */
function shapeSolo(notes,R,T,st){const n=(SOLO_SCALE[S.scale]||SOLO_SCALE.minor).length,sus=!!S.up.suzun;const ov=(t,len,r,skip)=>notes.some(m=>m!==skip&&m.r===r&&t<m.t+m.len&&m.t<t+len);
 if(sus&&(st==='hendrix'||st==='taksim')&&!notes.some(m=>m.r>=R-Math.ceil(R/3)&&m.len>=4)){const cand=notes.filter(m=>m.t>=T/2&&m.t+4<=T-4).sort((a,b)=>b.len-a.len)[0];if(cand){cand.r=R-1;cand.len=Math.max(cand.len,4);notes=notes.filter(m=>m===cand||!(m.r===cand.r&&m.t<cand.t+cand.len&&cand.t<m.t+m.len))}}
 const last=notes[notes.length-1];if(last){const root=Math.floor(last.r/n)*n;last.r=root;if(sus){last.len=Math.max(2,Math.min(4,T-last.t))}if(last.t+last.len<T-2){const t=Math.max(last.t+last.len,T-4);if(!ov(t,T-t,root,null)&&notes.length<SOLO_MAX)notes.push({t,len:sus?T-t:1,r:root,art:'none'})}}
 return notes.sort((a,b)=>a.t-b.t)}
const needleOf=si=>{const k=S.needle[si]||1;if(k===2&&!S.up.needle2)return 1;if(k===3&&!S.up.needle3)return 1;return k};
const needleSpeed=si=>NEEDLES[needleOf(si)-1].speed;
const needleOn=k=>k===1||(k===2&&!!S.up.needle2&&S.slots.some((id,si)=>id&&needleOf(si)===2))||(k===3&&!!S.up.needle3&&S.slots.some((id,si)=>id&&needleOf(si)===3));

/* ================= economy ================= */
const ON=(p,si,s)=>!!S.slots[si]&&s<MI.N&&p[si][s]>0;
const STEPS=(p,si)=>{const a=[];if(S.slots[si])for(let s=0;s<MI.N;s++)if(p[si][s])a.push(s);return a};
const anyNotes=p=>{for(let i=0;i<S.slots.length;i++)if(STEPS(p,i).length)return true;return false};
const bActive=()=>hasB()&&anyNotes(S.pat.B);
function sameAB(){for(let i=0;i<S.slots.length;i++)for(let s=0;s<MI.N;s++)if((S.pat.A[i][s]>0)!==(S.pat.B[i][s]>0))return false;return true}
const slotsRole=r=>S.slots.map((id,si)=>id&&IDX[id].role===r?si:-1).filter(x=>x>=0);
const anySlot=(r,f)=>slotsRole(r).some(f);
const playingSlots=(p=S.pat[S.edit])=>S.slots.filter((id,si)=>id&&STEPS(p,si).length>0).length;
const hasRolePlaying=(r,p=S.pat[S.edit])=>slotsRole(r).some(si=>STEPS(p,si).length>0);
const famPlaying=(f,p=S.pat[S.edit])=>S.slots.filter((id,si)=>id&&IDX[id].fam===f&&STEPS(p,si).length>0).length;
const famCount=(p=S.pat[S.edit])=>new Set(S.slots.filter((id,si)=>id&&STEPS(p,si).length).map(id=>IDX[id].fam)).size;
const COMBOS=[
 {n:'Grup başları',b:.5,d:'Bir Darbe her grup başında',t:p=>anySlot('darbe',si=>MI.gs.every(s=>ON(p,si,s)))},
 {n:'Backbeat',b:.5,d:'Bir Keskin 2. ve 4. grup başında',t:p=>{const g=MI.gs.filter((s,k)=>k%2===1);return g.length>0&&anySlot('keskin',si=>g.every(s=>ON(p,si,s)))}},
 {n:'Ofbit',b:.3,d:'Bir Seri tüm grup ortalarında',t:p=>anySlot('seri',si=>MI.mids.every(s=>ON(p,si,s)))},
 {n:'Es payı',b:.3,d:'Bir Güdümlü 3+ vuruş, yan yana yok',t:p=>anySlot('gudum',si=>{const a=STEPS(p,si);return a.length>=3&&a.every(s=>!ON(p,si,(s+1)%MI.N))})},
 {n:'Ara akor',b:.3,d:'Bir Yavaşlatıcı yalnız grup ortalarında, 2+',t:p=>anySlot('yavas',si=>{const a=STEPS(p,si);return a.length>=2&&a.every(s=>MI.mids.includes(s))})},
 {n:'Kalkan ritmi',b:.2,d:'Bir Kalkan tüm grup başlarında',t:p=>anySlot('kalkan',si=>MI.gs.every(s=>ON(p,si,s)))},
 {n:'Aile uyumu',b:.3,d:'Sahnede 3+ aile çalıyor',t:p=>famCount(p)>=3},
 {n:'Tam kadro',b:.25,d:'Her sahne yeri dolu ve çalıyor',t:p=>S.slots.length>=4&&S.slots.every((id,si)=>id&&STEPS(p,si).length>0)},
 {n:'Şarkı yapısı',b:.4,d:'B deseni dolu ve A’dan farklı',t:()=>bActive()&&!sameAB()}
];
const PEN={n:'Kakofoni',m:.75,d:'Bir adımda 6+ vuruş',t:p=>{for(let s=0;s<MI.N;s++){let c=0;for(let i=0;i<S.slots.length;i++)if(ON(p,i,s))c++;if(c>=6)return true}return false}};
const grooveCount=(p=S.pat[S.edit])=>COMBOS.filter(c=>c.t(p)).length;

/* synergies: real-groove relationships, each returns the rows it lights up */
const SYN=[
 {id:'kilit',n:'Kilit',d:'Delici ya da Titreşim vuruşlarının hepsi bir Darbe ile aynı adımda (2+)',w:'Bas ile kick aynı yere basınca groove oturur',m:1.3,
  t:p=>{const dr=slotsRole('darbe'),out={};[...slotsRole('delici'),...slotsRole('titresim')].forEach(si=>{const a=STEPS(p,si);if(a.length>=2&&a.every(s=>dr.some(dj=>ON(p,dj,s)))){out[si]=1;dr.forEach(dj=>{if(a.some(s=>ON(p,dj,s)))out[dj]=1})}});return out}},
 {id:'katman',n:'Katman',d:'Bir Destek, bir Keskin’in tüm adımlarında onunla birlikte vuruyor (2+)',w:'Alkış ya da shaker trampetin üstüne katman olur',m:1.3,
  t:p=>{const out={};slotsRole('destek').forEach(ds=>{slotsRole('keskin').forEach(ks=>{const a=STEPS(p,ks);if(a.length>=2&&a.every(s=>ON(p,ds,s))){out[ds]=1;out[ks]=1}})});return out}},
 {id:'ofbit',n:'Ofbit nefesi',d:'Bir Seri yalnız Darbe’nin olmadığı adımlarda vuruyor (4+)',w:'Hi-hat davulun arasını doldurur, üstüne binmez',m:1.2,
  t:p=>{const dr=slotsRole('darbe'),out={};if(!dr.length)return out;slotsRole('seri').forEach(si=>{const a=STEPS(p,si);if(a.length>=4&&a.every(s=>!dr.some(dj=>ON(p,dj,s)))){out[si]=1;dr.forEach(dj=>{if(STEPS(p,dj).length)out[dj]=1})}});return out}},
 {id:'yuruyus',n:'Yürüyüş',d:'Delici ya da Titreşim, her vuruşu bir Darbe’den hemen sonraki adımda (2+)',w:'Bas kick’in peşinden yürür',m:1.2,
  t:p=>{const dr=slotsRole('darbe'),out={};[...slotsRole('delici'),...slotsRole('titresim')].forEach(si=>{const a=STEPS(p,si);if(a.length>=2&&a.every(s=>dr.some(dj=>ON(p,dj,(s-1+MI.N)%MI.N))))out[si]=1});return out}},
 {id:'soru',n:'Soru-cevap',d:'İki melodik enstrüman: biri yalnız ölçünün ilk yarısında, diğeri yalnız ikinci yarısında',w:'Çağrı ve yanıt; melodiler birbirinin boşluğunu doldurur',m:1.4,
  t:p=>{const mel=[...slotsRole('gudum'),...slotsRole('zincir'),...slotsRole('keskin').filter(si=>IDX[S.slots[si]].fam!=='vur')],half=Math.floor(MI.N/2),out={};const first=mel.filter(si=>{const a=STEPS(p,si);return a.length>=2&&a.every(s=>s<half)}),second=mel.filter(si=>{const a=STEPS(p,si);return a.length>=2&&a.every(s=>s>=half)});if(first.length&&second.length){first.forEach(si=>out[si]=1);second.forEach(si=>out[si]=1)}return out}},
 {id:'pedal',n:'Pedal',d:'Bir Yavaşlatıcı yalnız grup başlarında, bir melodik enstrüman hiç grup başına basmıyor',w:'Pad vuruşa oturur, melodi aralara',m:1.3,
  t:p=>{const out={};slotsRole('yavas').forEach(ps=>{const a=STEPS(p,ps);if(!(a.length>=2&&a.every(s=>MI.gsSet.has(s))))return;[...slotsRole('gudum'),...slotsRole('zincir')].forEach(ms=>{const b=STEPS(p,ms);if(b.length>=2&&b.every(s=>!MI.gsSet.has(s))){out[ps]=1;out[ms]=1}})});return out}},
 {id:'bir',n:'Birde crash',d:'Bir Alan rolü yalnız 1. adımda vuruyor',w:'Crash ölçünün başını işaretler, her yere değil',m:1.5,
  t:p=>{const out={};slotsRole('alan').forEach(si=>{const a=STEPS(p,si);if(a.length===1&&a[0]===0)out[si]=1});return out}},
 {id:'dinamik',n:'Dinamik',d:'Bir halkada tam bir aksan var ve o aksan grup başında',w:'Tek vurgu cümleye yön verir',m:1.15,
  t:p=>{const out={};S.slots.forEach((id,si)=>{if(!id)return;const acc=[];for(let s=0;s<MI.N;s++)if(p[si][s]===2)acc.push(s);if(acc.length===1&&MI.gsSet.has(acc[0]))out[si]=1});return out}},
 {id:'clave',n:'Clave’ye uyum',d:'Bir halka kitaptan bir clave çalıyor, başka bir halkanın tüm vuruşları clave adımlarında (2+)',w:'Clave anahtar ritimdir; ona oturan her şey yerine oturur',m:1.25,
  t:p=>{const out={};const claves=BOOK.filter(b=>b.fx&&b.fx.clave&&b.m===S.meter&&S.found[b.id]);S.slots.forEach((id,si)=>{if(!id)return;const st=STEPS(p,si).join(',');const cl=claves.find(b=>b.s.join(',')===st);if(!cl)return;S.slots.forEach((id2,sj)=>{if(!id2||sj===si)return;const a=STEPS(p,sj);if(a.length>=2&&a.every(s=>cl.s.includes(s))){out[sj]=1;out[si]=1}})});return out}}
];
const msMult=L=>{let m=1;for(const x of MS)if(L>=x)m*=2;return m};
let GC={A:1,B:1,S:1,F:1},BR={A:0,B:0,S:0,F:0},DR={A:0,B:0,S:0,F:0},BRS={A:[],B:[],S:[],F:[]},DRS={A:[],B:[],S:[],F:[]},NF={A:[],B:[],S:[],F:[]},RUN={A:[],B:[],S:[],F:[]},ROWM={A:[],B:[],S:[],F:[]},SUPS={A:[],B:[],S:[],F:[]},BK={A:{row:{},roleD:{},famD:{},nota:1,dmg:1,slow:0,meter:0,wall:1,crit:0,nefes:{},on:{}},B:null,S:null,F:null},SYNON={A:{},B:{},S:{},F:{}},BOOKON={A:{},B:{},S:{},F:{}};
BK.B=JSON.parse(JSON.stringify(BK.A));BK.S=JSON.parse(JSON.stringify(BK.A));
const HAB=0.85;
function rowLoad(p,si){let n=0;for(let s=0;s<MI.N;s++){const v=p[si][s];if(v)n+=v===2?2:1}return n}
function nefesOf(si,pk){const x=slotIns(si);if(!x)return 4;let nf=x.nf*Math.max(1,MI.N/16);const bk=BK[pk||S.edit];if(bk&&bk.nefes&&bk.nefes[si])nf+=bk.nefes[si];return nf}
function nefesF(p,si,pk){const x=slotIns(si);if(!x)return 1;const n=rowLoad(p,si),nf=nefesOf(si,pk);return n<=nf?1:Math.pow(nf/n,1.5)}
function runsOf(p,si){const N=MI.N,out=new Array(N).fill(0);if(!S.slots[si])return out;let full=true;for(let s=0;s<N;s++)if(!p[si][s]){full=false;break}if(full){for(let s=0;s<N;s++)out[s]=N;return out}let start=0;while(p[si][start])start++;let run=0;for(let k=0;k<N;k++){const s=(start+k)%N;if(p[si][s]){run++;out[s]=run}else run=0}return out}
const habF=run=>Math.pow(HAB,Math.max(0,run-1));
function bookFx(p){const fx={row:{},roleD:{},famD:{},nota:1,dmg:1,slow:0,meter:0,wall:1,crit:0,nefes:{},on:{}};
 S.slots.forEach((id,si)=>{if(!id)return;const st=STEPS(p,si).join(',');const e=BOOK.find(b=>S.found[b.id]&&b.m===S.meter&&b.s.join(',')===st);if(!e)return;fx.on[e.id]=si;const f=e.fx||{};fx.row[si]=(fx.row[si]||1)*(f.row||1.3);if(f.roleD)Object.entries(f.roleD).forEach(([r,m])=>fx.roleD[r]=(fx.roleD[r]||1)*m);if(f.famD)Object.entries(f.famD).forEach(([r,m])=>fx.famD[r]=(fx.famD[r]||1)*m);if(f.nota)fx.nota*=f.nota;if(f.dmg)fx.dmg*=f.dmg;if(f.slow)fx.slow=Math.max(fx.slow,f.slow);if(f.meter)fx.meter+=f.meter;if(f.wall)fx.wall*=f.wall;if(f.crit)fx.crit=Math.max(fx.crit,f.crit);if(f.nefes)fx.nefes[si]=(fx.nefes[si]||0)+f.nefes});
 return fx}
function recalc(){
 for(const pk of ['A','B','S','F']){const p=S.pat[pk];BK[pk]=bookFx(p);NF[pk]=S.slots.map((id,si)=>nefesF(p,si,pk));RUN[pk]=S.slots.map((id,si)=>runsOf(p,si));
  const syn={},rm=S.slots.map(()=>1);SYN.forEach(y=>{const o=y.t(p);const ks=Object.keys(o);if(ks.length){syn[y.id]=1;ks.forEach(si=>rm[si]*=y.m)}});SYNON[pk]=syn;
  const bk=BK[pk];S.slots.forEach((id,si)=>{if(!id)return;const x=IDX[id];rm[si]*=(bk.row[si]||1)*(bk.roleD[x.role]||1)*(bk.famD[x.fam]||1)});ROWM[pk]=rm;BOOKON[pk]=bk.on;
  const sup=new Array(MI.N).fill(0);slotsRole('destek').forEach(si=>{for(let s=0;s<MI.N;s++)if(p[si][s])sup[s]++});SUPS[pk]=sup}
 GC={A:groove('A'),B:groove('B'),S:1};const a=barRaw('A'),b=barRaw('B'),c=barRaw('S');BR={A:a[0],B:b[0],S:c[0]};DR={A:a[1],B:b[1],S:c[1]};
}
function groove(pk){const p=S.pat[pk];let m=1;for(const c of COMBOS)if(c.t(p))m+=c.b;if(PEN.t(p))m*=PEN.m;return m}
const hasarM=()=>Math.pow(1.12,S.def.hasar||0)*(S.up.fill?1.1:1);
const supM=(pk,s)=>Math.min(2,1+0.5*((SUPS[pk]||[])[s]||0));
const noteVal=(si,v)=>{const x=slotIns(si);if(!x)return 0;const L=lvOf(x.id);return x.b*L*msMult(L)*(v===2?2:1)*(x.role==='gelir'?3:1)};
const dmgOf=(si,v)=>{const x=slotIns(si);if(!x)return 0;const L=lvOf(x.id);return x.dmg*L*msMult(L)*(v===2?2:1)*hasarM()};
const hitNota=(pk,si,v)=>noteVal(si,v)*(NF[pk][si]||1)*(ROWM[pk][si]||1)*BK[pk].nota;
const hitDmg=(pk,si,s,v)=>dmgOf(si,v)*(NF[pk][si]||1)*(ROWM[pk][si]||1)*habF((RUN[pk][si]||[])[s]||1)*supM(pk,s)*BK[pk].dmg;
function barRaw(pk){const p=S.pat[pk];let g=0,d=0;BRS[pk]=S.slots.map(()=>0);DRS[pk]=S.slots.map(()=>0);for(let i=0;i<S.slots.length;i++){const x=slotIns(i);if(!x)continue;let gi=0,di=0;
  if(pk==='S'&&x.fam!=='vur'&&hasSoloNotes(i)){const A=analyzeSolo(i),dm=duetPart(i)>=0?1.2:1;A.ns.forEach((nt,j)=>{const w=(1+noteSus(x,nt))*(ART_M[artEff(x,nt.art)]||1)*A.hab[j]*A.mult*dm/2;gi+=noteVal(i,1)*w;if(isWeapon(x.role)||x.role==='titresim')di+=dmgOf(i,1)*w});BRS[pk][i]=gi;DRS[pk][i]=di;g+=gi;d+=di;continue}for(let s=0;s<MI.N;s++){const v=p[i][s];if(v){gi+=hitNota(pk,i,v);if(isWeapon(x.role))di+=hitDmg(pk,i,s,v);else if(x.role==='titresim'&&S.stage.wall)di+=hitDmg(pk,i,s,v)*BK[pk].wall}}BRS[pk][i]=gi;DRS[pk][i]=di;g+=gi;d+=di}return[g,d]}
function planAvg(kind){const pl=planArr();let tot=0;pl.forEach(t=>{const sec=SECTS[t];const pk=sec.pk==='B'&&bActive()?'B':'A';let sum=0;S.slots.forEach((id,si)=>{if(!id)return;const x=IDX[id];if(sec.solo&&isSolo(si)){sum+=((kind==='n'?BRS:DRS).S[si]||0)*SOLO_M*needleSpeed(si);return}if(!allowed(sec,x,si))return;sum+=((kind==='n'?BRS:DRS)[pk][si]||0)*needleSpeed(si)});const dyn=sec.dyn*(sec.ramp?1+sec.ramp*0.3125:1),tm=sec.ramp?1+sec.ramp*0.625:1;tot+=sum*GC[pk]*dyn*tm});
 /* chord and fill bonuses, averaged over the section's bars */
 if(S.up.akor||S.up.dolgu){let extra=0;pl.forEach((t,i)=>{const sec=SECTS[t];const pk=sec.pk==='B'&&bActive()?'B':'A';let sum=0;S.slots.forEach((id,si)=>{if(!id)return;const x=IDX[id];if(sec.solo&&isSolo(si))return;if(!allowed(sec,x,si))return;sum+=((kind==='n'?BRS:DRS)[pk][si]||0)*needleSpeed(si)});const base=sum*GC[pk]*sec.dyn;extra+=base*((transM(i)-1)/SEC_BARS+(makamM(i)-1));
  if(fillOn()&&!sec.solo){let fv=0;S.slots.forEach((id,si)=>{if(!isFillRow(si)||!allowed(sec,IDX[id],si))return;for(let s=0;s<MI.N;s++)if(fillZone(s)&&S.pat.F[si][s])fv+=(kind==='n'?fillRowVal(si,S.pat.F[si][s]):fillRowDmg(si,S.pat.F[si][s]))});extra+=fv*GC.A*sec.dyn/SEC_BARS}});tot+=extra}
 return tot/pl.length*contrastM()}
const effSeri=()=>S.up.assist?Math.max(S.seri,6):S.seri;
const seriM=()=>1+0.04*Math.min(effSeri(),12);
const upM=()=>['swing','echo','side','filter'].reduce((m,k)=>S.up[k]?m*1.15:m,1);
const fanM=()=>1+0.05*S.hayran;
const bookM=()=>1+0.05*Object.keys(S.found).length;
const fitM=()=>{const th=ownTheme();return S.bpm>=th.bpm[0]&&S.bpm<=th.bpm[1]?1.25:1};
const meterM=()=>(METERS[S.meter].bon||1)+(BK[S.edit].meter||0);
const scaleM=()=>SCALES[S.scale].bon||1;
const waveM=()=>1+0.08*(S.wave-1);
const cityOf=()=>CITIES[S.city%CITIES.length];
const tourM=()=>(1+0.03*S.efsane)*(1+0.02*Object.keys(S.cities).length);
const cityM=()=>{const c=cityOf();return (S.scale===c.scale?1.1:1)*(S.meter===c.meter?1.1:1)};
const tourGain=()=>Math.max(1,Math.round(2*Math.sqrt(S.hayran)+albumsN()));
const canTour=()=>albumsN()>=TOUR_AL;
const globalM=()=>seriM()*upM()*fanM()*bookM()*fitM()*meterM()*scaleM()*waveM()*tourM()*cityM();
const curBpm=b=>S.bpm*tempoMulAt(b||0);
const barDur=()=>60/S.bpm*MI.N/4;
function rate(){return planAvg('n')*globalM()*planBonus()*(S.bpm*4/60)/MI.N}
function dps(){return planAvg('d')*planBonus()/barDur()}
function earn(x){if(!(x>0))return;S.nota+=x;S.runEarned+=x;S.total+=x}
function placedCount(){let c=0;const pk=hasB()?['A','B','S']:['A','S'];for(const k of pk)for(let i=0;i<S.slots.length;i++){if(!S.slots[i])continue;for(let s=0;s<MI.N;s++)if(S.pat[k][i][s])c++}return c}
const costAt=p=>Math.round(5*Math.pow(1.09,p));
const noteCost=()=>costAt(placedCount());
const accCost=()=>Math.round(noteCost()*0.5);
const tempoCost=()=>Math.round(300*Math.pow(3,(S.bmax-90)/10));
const slotCost=()=>Math.round(2000*Math.pow(10,S.slots.length-4));
const defCost=u=>Math.round(u.c*Math.pow(u.g,S.def[u.id]||0));
const albumTh=()=>Math.round(1.5e7*Math.pow(4,albumsN()));
const fansFor=()=>Math.max(1,Math.floor(10*Math.sqrt(S.runEarned/albumTh())));
function lvQuote(x){const L=lvOf(x.id);if(!L)return{n:1,c:x.u,unlock:true};const c0=x.lb*Math.pow(GROW,L);let n=S.buy;if(n===0)n=Math.max(1,Math.floor(Math.log(S.nota*(GROW-1)/c0+1)/Math.log(GROW)));return{n,c:Math.round(c0*(Math.pow(GROW,n)-1)/(GROW-1))}}
const hpMax=()=>100+60*(S.def.nabiz||0);
const shieldMax=()=>(50+50*(S.def.kalkan||0))*(S.stage.mirror?1.5:1);
const range=()=>Math.min(1,0.65+0.07*(S.def.menzil||0)+(S.stage.stars?0.1:0));
const slowPow=()=>0.4+0.1*(S.def.yavas||0);
const regen=()=>(S.def.tamir||0)+(S.stage.core?0.5:0)+(S.stage.mirror?0:0);
const bountyM=()=>1+0.25*(S.def.ganimet||0);
const globalSlow=()=>Math.min(0.5,(S.stage.stars?0.1:0)+(BK[S.edit].slow||0));

function fmt(n){if(!isFinite(n))return '∞';n=Math.floor(n);const u=[[1e18,' Kn'],[1e15,' Kt'],[1e12,' T'],[1e9,' Mr'],[1e6,' Mn']];for(const [v,s] of u)if(n>=v)return(n/v).toLocaleString('tr-TR',{maximumFractionDigits:2})+s;return n.toLocaleString('tr-TR')}
const fm=m=>m.toLocaleString('tr-TR',{maximumFractionDigits:2});
const pct=b=>'+%'+Math.round(b*100);
let msgT=0;
function msg(t){$('msg').textContent=T(t);clearTimeout(msgT);msgT=setTimeout(()=>{$('msg').textContent=''},3600)}

/* ================= orders ================= */
const OTPL=[
 {id:'kafe',t:'Kafe çalma listesi',who:'Köşedeki kafe',secs:240,fans:1,req:()=>[{t:'Tempo 70–95 BPM',ok:()=>S.bpm>=70&&S.bpm<=95},{t:'En az 3 enstrüman çalıyor',ok:()=>playingSlots()>=3},{t:'Alan rolü çalmıyor (sakin olsun)',ok:()=>!hasRolePlaying('alan')}]},
 {id:'kulup',t:'Kulüp gecesi',who:'Bodrum kat kulüp',secs:300,fans:2,req:()=>[{t:'Tempo 125 ve üstü',ok:()=>S.bpm>=125},{t:'Delici ya da Titreşim çalıyor',ok:()=>hasRolePlaying('delici')||hasRolePlaying('titresim')},{t:'3+ groove kalıbı tutuyor',ok:()=>grooveCount()>=3}]},
 {id:'dugun',t:'Düğün',who:'Salon sahibi',secs:360,fans:2,req:()=>albUnl()>=2?[{t:'Ölçü 9/8',ok:()=>S.meter==='m98'},{t:'Darbe rolü çalıyor',ok:()=>hasRolePlaying('darbe')},{t:'Tempo 100 ve üstü',ok:()=>S.bpm>=100}]:[{t:'4+ Vurmalı çalıyor',ok:()=>famPlaying('vur')>=4},{t:'Tempo 100 ve üstü',ok:()=>S.bpm>=100}]},
 {id:'dizi',t:'Dizi jeneriği',who:'Yapım şirketi',secs:300,fans:2,req:()=>[{t:albUnl()>=3?'Hicaz ya da Kürdi':'Minör gam',ok:()=>albUnl()>=3?(S.scale==='hicaz'||S.scale==='kurdi'):S.scale==='minor'},{t:'Tempo 100 ya da altı',ok:()=>S.bpm<=100},{t:'Tel ailesinden biri çalıyor',ok:()=>famPlaying('tel')>=1}]},
 {id:'reklam',t:'Reklam müziği',who:'Ajans',secs:200,fans:1,req:()=>hasB()?[{t:'B deseni dolu ve A’dan farklı',ok:()=>bActive()&&!sameAB()},{t:'Tempo 110–140',ok:()=>S.bpm>=110&&S.bpm<=140}]:[{t:'Tam kadro kalıbı tutuyor',ok:()=>COMBOS[7].t(S.pat[S.edit])},{t:'Tempo 110–140',ok:()=>S.bpm>=110&&S.bpm<=140}]},
 {id:'jam',t:'Oyun jam’i',who:'İndie stüdyo',secs:300,fans:2,req:()=>[{t:'Siberpunk ya da Synthwave teması',ok:()=>S.theme==='cyber'||S.theme==='synth'},{t:'Seri rolü çalıyor',ok:()=>hasRolePlaying('seri')},{t:'Ses duvarı sahnede',ok:()=>!!S.stage.wall}]},
 {id:'yayin',t:'Canlı yayın',who:'Yayıncı',secs:240,fans:1,req:()=>[{t:'Tempo 100–120',ok:()=>S.bpm>=100&&S.bpm<=120},{t:'Bir sahne katmanı kurulu',ok:()=>Object.values(S.stage).some(Boolean)},{t:'Seri sıfır değil',ok:()=>effSeri()>0}]},
 {id:'festival',t:'Festival ana sahne',who:'Organizatör',secs:600,fans:4,req:()=>[{t:'6+ enstrüman çalıyor',ok:()=>playingSlots()>=6},{t:'3+ aile',ok:()=>famCount()>=3},{t:'2+ uyum tutuyor',ok:()=>Object.keys(SYNON[S.edit]).length>=2}]},
 {id:'medit',t:'Meditasyon uygulaması',who:'Uygulama',secs:300,fans:2,req:()=>[{t:'Tempo 80 ya da altı',ok:()=>S.bpm<=80},{t:'Kalkan ya da Yavaşlatıcı çalıyor',ok:()=>hasRolePlaying('kalkan')||hasRolePlaying('yavas')},{t:'Kakofoni yok',ok:()=>!PEN.t(S.pat[S.edit])}]},
 {id:'dalga',t:'Sahne savunması',who:'Belediye',secs:400,fans:3,req:o=>[{t:'Dalga '+o.p.target+' ya da ötesine ulaş',ok:()=>S.wave>=o.p.target}]},
 {id:'kitap',t:'Ritim dersi',who:'Konservatuvar',secs:300,fans:2,req:()=>[{t:'Kitaptan bir kalıp sahnede çalıyor',ok:()=>Object.keys(BOOKON[S.edit]).length>=1},{t:'Bir uyum tutuyor',ok:()=>Object.keys(SYNON[S.edit]).length>=1}]}
];
function newOrder(seedExtra){const used=S.orders.map(o=>o.tpl);const r=rng((Date.now()+seedExtra*7919)>>>0);let pool=OTPL.filter(t=>!used.includes(t.id));if(!pool.length)pool=OTPL;const t=pool[Math.floor(r()*pool.length)];return{tpl:t.id,p:{target:S.bestWave+3},ready:0}}
function ensureOrders(){const now=Date.now();while(S.orders.length<3)S.orders.push(newOrder(S.orders.length));S.orders.forEach((o,k)=>{if(o.tpl&&!OTPL.find(x=>x.id===o.tpl))S.orders[k]=newOrder(k+5);else if(!o.tpl&&o.ready&&now>=o.ready)S.orders[k]=newOrder(k+11)})}
function orderOk(o){const t=OTPL.find(x=>x.id===o.tpl);if(!t)return false;return t.req(o).every(r=>r.ok())}
function deliver(k){const o=S.orders[k];if(!o||!o.tpl||!orderOk(o))return;const t=OTPL.find(x=>x.id===o.tpl);const g=Math.max(200,rate()*t.secs);earn(g);S.hayran+=t.fans;S.orders[k]={tpl:null,p:{},ready:Date.now()+5*60*1000};msg(t.t+' teslim edildi · ♪ '+fmt(g)+' · +'+t.fans+' hayran')}

