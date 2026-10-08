/* ================= combat ================= */
let enemies=[],vfx=[],wave=null,core={hp:100,sh:0},retreatFlash=0,waveFlash=0,waveText='',retreatCount=0,soloNow=-1,soloFlash=0,curBar=0,secFlash=0,secName='',dorukFlash=0,lastSqueal=0,transFlash=0,transText='',crashFlash=0;
function squeal(si){const t=lastLogic;for(let k=0;k<WN;k++)wallE[k]*=0.96;if(t-lastSqueal>4){lastSqueal=t;msg('Feedback ıslığa döndü: 16 adımdan uzun tutma, ses duvarı eriyor');vfx.push({k:'ring',col:dispTheme().cv.hot,life:0.6})}}
function doruk(si){const x=slotIns(si);if(!x)return;const col=insColor(x,dispTheme()),d=dmgOf(si,1)*GC.A*SOLO_M*4*globalMDmg();enemies.slice().forEach(e=>hit(e,d,col,null));vfx.push({k:'ring',col,life:1});const g=rate()*5;if(g>0)earn(g);dorukFlash=1;msg('DORUK! '+x.n+' sahneyi doldurdu · herkese hasar · +5 sn gelir')}
const WN=48,wallE=new Float32Array(WN),wallD=new Float32Array(WN);
const wallBase=()=>S.layout==='strip'?0:0.678,wallSpan=()=>S.layout==='strip'?0.47:0.3;
function waveComp(w){const r=rng(w*7919+13);const bd=barDur();let n=Math.min(60,4+Math.floor(w*0.9));let boss=null;if(w%50===0)boss='ceo';else if(w%25===0)boss='mudur';else if(w%10===0)boss='denetci';if(boss)n=Math.ceil(n/2);const span=(6+Math.floor(w/10))*bd;const items=[];const bias=(cityOf()||{}).bias||{};const W=[['sansurcu',w>=9?0.1:0],['avukat',w>=6?0.15:0],['stajyer',w>=4?0.15:0],['kurye',w>=2?0.25:0]];let rest=1;W.forEach(q=>{q[1]*=bias[q[0]]||1;rest-=q[1]});W.push(['memur',Math.max(0.05,rest*(bias.memur||1))]);const tot=W.reduce((a,q)=>a+q[1],0);
 for(let k=0;k<n;k++){let u=r()*tot,ty='memur';for(const [t,p] of W){if(u<p){ty=t;break}u-=p}items.push({ty,at:(k/n)*span+r()*bd*0.5,lane:r()})}if(boss)items.push({ty:boss,at:span*0.5,lane:r()});items.sort((a,b)=>a.at-b.at);return items}
function waveSummary(w){const c={};waveComp(w).forEach(it=>{c[it.ty]=(c[it.ty]||0)+(ETYPES[it.ty].swarm||1)});return Object.entries(c).map(([k,v])=>v+' '+ETYPES[k].n.toLocaleLowerCase('tr-TR')).join(', ')}
function startWave(w,now){S.wave=w;if(w>S.bestWave){S.bestWave=w;const nf=nextFam();if(nf&&famCanOpen(nf[0])&&!famCond(nf[0]).cost)setTimeout(()=>msg(nf[1]+' ailesi açılabilir: Koleksiyon sekmesine bak'),1200)}wave={n:w,queue:waveComp(w),startT:now,done:false,nextAt:0,boss:null};const line=BOSS_LINES[(wave.queue.find(q=>ETYPES[q.ty].boss)||{}).ty]||WAVE_LINES[w];waveText=T('Dalga')+' '+w;waveFlash=1;if(line)msg(line);if(typeof renderDef==='function')renderDef()}
function spawn(ty,now,w,lane){const T=ETYPES[ty];const cnt=T.swarm||1;for(let k=0;k<cnt;k++){const hp=4*Math.pow(1.19,w-1)*T.hp;const e={ty,hp,hpMax:hp,d:1+k*0.03,a:(lane!=null?lane:Math.random())+(cnt>1?(Math.random()-0.5)*0.08:0),sp:T.sp*(1+0.004*w),slow:0,slowT:0,stun:0,dot:0,dotT:0,flash:0,w,boss:!!T.boss,lastSp:now,wob:Math.random()*TAU,id:Math.random(),waved:false};e.a=((e.a%1)+1)%1;enemies.push(e);if(e.boss)wave.boss=e}}
function laneDist(a,b){const d=Math.abs(a-b);return S.layout==='circle'?Math.min(d,1-d):d}
function bounty(e){const T=ETYPES[e.ty];return(2*Math.pow(1.18,e.w-1)*T.b+rate()*0.4*T.b)*bountyM()}
function kill(e,k,now){const g=bounty(e);earn(g);S.kills++;enemies.splice(k,1);if(wave&&wave.boss===e)wave.boss=null;spawnDeath(e);if(S.dnum!==false&&pops.length<48)pops.push({e,t:'+♪ '+fmt(g),life:1,k:1});if(e.boss)msg(ETYPES[e.ty].n+' susturuldu · ♪ '+fmt(g))}
function leak(e,k,now){const T=ETYPES[e.ty];let dmg=T.dmg*(1+0.03*e.w);if(core.sh>0){const a=Math.min(core.sh,dmg);core.sh-=a;dmg-=a}core.hp-=dmg;retreatFlash=Math.max(retreatFlash,0.6);if(T.mute){const cands=S.slots.map((id,si)=>id?si:-1).filter(x=>x>=0);if(cands.length){const si=cands[Math.floor(Math.random()*cands.length)];muteUntil[si]=now+barDur();msg(slotIns(si).n+' bir ölçü susturuldu')}}enemies.splice(k,1);if(wave&&wave.boss===e)wave.boss=null;if(core.hp<=0)retreat(now)}
function retreat(now){retreatCount++;const from=S.wave,to=Math.max(1,Math.floor(S.wave*0.8));enemies=[];core.hp=hpMax();core.sh=0;retreatFlash=1.5;msg('Sessizlik A.Ş. sahneyi bastı. Dalga '+from+' → '+to+'. Nabız tazelendi.');startWave(to,now)}
function wallHit(e){const k=Math.floor(e.a*WN)%WN;const E=wallE[k];if(E<=0.02)return 0;const b=wallBase(),top=b+Math.min(1,E)*wallSpan();if(e.d>=b&&e.d<=top)return E*wallD[k];return 0}
function logic(now){
 const dt=clamp(now-lastLogic,0,0.1);lastLogic=now;if(dt<=0||!wave)return;
 while(wave.queue.length&&wave.startT+wave.queue[0].at<=now){const it=wave.queue.shift();spawn(it.ty,now,wave.n,it.lane)}
 const bd=barDur(),dec=Math.exp(-dt*2.2),gs=Math.min(0.6,globalSlow()+(planAt(curBar).sec.slow||0)),useWall=!!S.stage.wall,useBeams=!!S.stage.beams,beamDps=useBeams?dps()*0.03:0;
 for(let k=0;k<WN;k++){wallE[k]*=dec;wallD[k]*=dec}
 for(let k=enemies.length-1;k>=0;k--){const e=enemies[k];const T=ETYPES[e.ty];e.flash=Math.max(0,e.flash-dt*8);
  if(e.stun>0)e.stun-=dt;else{const sl=Math.min(0.85,(e.slowT>0?e.slow:0)+(T.noSlow?0:gs));e.d-=e.sp*(1-sl)*dt;if(e.slowT>0)e.slowT-=dt}
  if(S.stage.wave&&!e.waved&&e.d<0.8){e.waved=true;applySlow(e,0.25,1.0)}
  let dd=0;
  if(e.dotT>0){dd+=e.dot*dt;e.dotT-=dt}
  if(useWall){const w=wallHit(e);if(w>0){dd+=w*dt;if(Math.random()<dt*6)e.flash=0.6}}
  if(useBeams){const ang=((e.a*TAU)+(S.layout==='strip'?-Math.PI/2:0));for(let b=0;b<6;b++){const a=clock*0.5*(b%2?1:-1)+b*TAU/6+(S.layout==='strip'?-Math.PI/2:0);let df=Math.abs(((ang-a)%TAU+TAU)%TAU);df=Math.min(df,TAU-df);if(df<0.08){dd+=beamDps*dt;break}}}
  if(dd>0){e.hp-=dd;if(e.hp<=0){kill(e,k,now);continue}}
  if(e.boss&&T.spawn&&now-e.lastSp>=bd*2&&e.d<0.95){e.lastSp=now;spawn(T.spawn,now,wave.n,e.a)}
  if(e.d<=0){const rc=retreatCount;leak(e,k,now);if(retreatCount!==rc)break}
 }
 const secNow=planAt(curBar).sec;core.hp=Math.min(hpMax(),core.hp+regen()*dt*(secNow.regen||1));
 if(S.stage.mirror)core.sh=Math.min(shieldMax(),core.sh+2*dt);
 if(!wave.queue.length&&enemies.length===0&&!wave.done){wave.done=true;wave.nextAt=now+bd}
 if(wave.done&&now>=wave.nextAt)startWave(wave.n+1,now);
}
function inRange(){const r=range();return enemies.filter(e=>e.d<=r)}
function hit(e,dmg,col,origin,kind){e.dnA=(e.dnA||0)+Math.min(dmg,Math.max(0,e.hp));e.hp-=dmg;e.flash=1;const k=enemies.indexOf(e);if(origin)vfx.push({k:kind||'tracer',o:origin,e,col,life:1});if(e.hp<=0&&k>=0)kill(e,k,lastLogic)}
function applySlow(e,amt,dur){if(ETYPES[e.ty].noSlow)return;e.slow=Math.max(e.slow,amt);e.slowT=Math.max(e.slowT,dur)}
function pushWall(lane,energy,dmg){const k0=Math.floor(lane*WN)%WN;for(let o=-4;o<=4;o++){const k=(k0+o+WN)%WN,f=Math.exp(-o*o/5);wallE[k]=Math.min(1.6,wallE[k]+energy*f);wallD[k]=Math.max(wallD[k],dmg*f)}}
function fire(si,s,v,pk,mult,art,raw){
 const x=slotIns(si);if(!x)return;const t=lastLogic;if(muteUntil[si]>t)return;mult=(mult||1)*(ART_M[art]||1);
 const lane=S.layout==='strip'?(s+0.5)/MI.N:(s+0.5)/MI.N;
 let dmg=(raw?fillRowDmg(si,v):hitDmg(pk,si,s,v))*GC[pk]*mult;const col=insColor(x,dispTheme()),o={si,s};
 if(x.role==='gelir'||x.role==='destek')return;
 if(x.role==='kalkan'){core.sh=Math.min(shieldMax(),core.sh+dmg*2);vfx.push({k:'shield',col,life:1});return}
 if(x.role==='titresim'){if(S.stage.wall){pushWall(lane,(v===2?1.2:0.7),dmg*BK[pk].wall*1.5);vfx.push({k:'wallpush',a:lane,col,life:1})}return}
 if(S.stage.wall)pushWall(lane,v===2?0.3:0.15,dmg*0.25);
 if(x.role==='darbe'&&S.stage.core)core.sh=Math.min(shieldMax(),core.sh+3);
 if(art==='fb'&&S.stage.wall)pushWall(lane,0.8,dmg*1.5);
 const R=inRange();if(!R.length)return;
 const byD=R.slice().sort((a,b)=>a.d-b.d),near=byD[0],critB=(BK[pk].crit||0)+(art==='vib'?0.3:0);
 if(art==='bend'){near.d=Math.min(1,near.d+(near.boss?0.01:0.04))}if(art==='slap'&&!ETYPES[near.ty].noSlow)near.stun=Math.max(near.stun,0.3);if(art==='slide'&&byD[1])hit(byD[1],dmg*0.5,col,o);
 switch(x.role){
  case 'darbe':{hit(near,dmg,col,o);R.forEach(e=>{if(e!==near&&laneDist(e.a,near.a)<0.06&&Math.abs(e.d-near.d)<0.1)hit(e,dmg*0.3,col)});vfx.push({k:'burst',e:near,col,life:1});break}
  case 'keskin':{const tg=R.slice().sort((a,b)=>b.hp-a.hp)[0];const crit=Math.random()<0.2+critB;hit(tg,dmg*(crit?2.5:1),col,o);if(crit)vfx.push({k:'crit',e:tg,col,life:1});break}
  case 'seri':{const tg=R[Math.floor(Math.random()*R.length)];hit(tg,dmg*(ETYPES[tg.ty].armor?0.5:1),col,o);break}
  case 'alan':{const k=x.id==='gamelan'?0.5:0.35;R.forEach(e=>hit(e,dmg*k,col));vfx.push({k:'ring',o,col,life:1});break}
  case 'delici':{R.forEach(e=>{if(laneDist(e.a,near.a)<0.04)hit(e,dmg,col)});vfx.push({k:'beam',a:near.a,col,life:1});break}
  case 'yavas':{hit(near,dmg*0.7,col,o);applySlow(near,slowPow(),1.5);break}
  case 'gudum':{const tg=R.slice().sort((a,b)=>b.sp-a.sp)[0];hit(tg,dmg,col,o,'homing');break}
  case 'zincir':{hit(near,dmg,col,o);const others=R.filter(e=>e!==near).sort((a,b)=>(laneDist(a.a,near.a)+Math.abs(a.d-near.d))-(laneDist(b.a,near.a)+Math.abs(b.d-near.d))).slice(0,2);let prev=near;others.forEach(e=>{hit(e,dmg*0.6,col);vfx.push({k:'chain',e1:prev,e,col,life:1});prev=e});break}
  case 'statik':{hit(near,dmg*0.4,col,o);near.dot=Math.max(near.dot,dmg*0.3);near.dotT=Math.max(near.dotT,3);applySlow(near,0.2,3);break}
  case 'sarsici':{hit(near,dmg,col,o);if(!ETYPES[near.ty].noSlow)near.stun=Math.max(near.stun,near.boss?0.2:0.5);vfx.push({k:'burst',e:near,col,life:1});break}
  case 'kritik':{const crit=Math.random()<0.35+critB;hit(near,dmg*(crit?3:1),col,o);if(crit)vfx.push({k:'crit',e:near,col,life:1});break}
  default:hit(near,dmg,col,o)
 }
}
function onStep(q){
 const nk=q.k||1;
 if(q.s===0&&nk===1){if(!hitBar)S.seri=Math.floor(S.seri/2);hitBar=false;playPk=q.pk;
  if(S.stage.tower&&enemies.length){const tg=enemies.slice().sort((a,b)=>b.hp-a.hp)[0];const d=(DR[q.pk]*GC[q.pk]/MI.N)*4*globalMDmg();if(d>0){hit(tg,d,dispTheme().cv.hot,null);vfx.push({k:'bolt',e:tg,col:dispTheme().cv.hot,life:1})}}}
 const p=S.pat[q.pk],M=GC[q.pk]*globalM(),vis=q.pk===S.edit;let g=0;
 const b=q.b||0,sa=soloActive(b),pa=planAt(b);let dyn=dynAt(b);if(nk===1)curBar=b;const fb=nk===1&&fillBar(b);
 if(pa.barIn===0){const tm=transM(pa.idx);if(tm>1){dyn*=tm;if(q.s===0&&nk===1){transFlash=1;transText=T('GEÇİŞ')+' ×'+fm(tm)}}if(q.s===0&&nk===1&&b>0&&fillBar(b-1)&&fillHits()>=4){crashFlash=1;enemies.forEach(e=>applySlow(e,1,0.4));vfx.push({k:'ring',col:'#ffffff',life:0.8})}}
 if(q.s===0&&nk===1){if(sa>=0&&soloNow!==sa){soloFlash=1;msg('Solo: '+slotIns(sa).n)}soloNow=sa;if(pa.barIn===0&&(S.up.sef||pa.sec.solo||bActive())){secFlash=1;secName=T(pa.sec.n)}}
 for(let i=0;i<S.slots.length;i++){const x=slotIns(i);if(!x)continue;if(needleOf(i)!==nk)continue;if(muteUntil[i]>q.t)continue;const soloing=pa.sec.solo&&isSolo(i);let v,pkk=q.pk;if(soloing){const dp=duetPart(i);if(dp<0&&sa!==i)continue;if(x.fam!=='vur'&&hasSoloNotes(i)){const off=(pa.barIn%2)*MI.N+q.s;let gs=0;if(duetPlays(i,off)){const A=analyzeSolo(i),dm=dp>=0?1.2:1,R=soloRows();A.ns.forEach((nt,j)=>{const a=artEff(x,nt.art),L=noteLenEff(nt);
   if(nt.t===off){const m=SOLO_M*dyn*A.hab[j]*A.mult*dm;gs+=hitNota('S',i,1)*m*(ART_M[a]||1);flash[i][q.s]=1;spawnPart(i,q.s);fire(i,q.s,1,'S',m,a)}
   else if(off>nt.t&&off<nt.t+L){const k=off-nt.t,p=tickPow(x,k,a);if(p<0){squeal(i);return}if(p<=0)return;const m=SOLO_M*dyn*p*A.mult*dm;gs+=hitNota('S',i,1)*m;fire(i,q.s,1,'S',m,a==='fb'?'fb':'none');if(S.up.sdoruk&&k===3&&L>=4&&nr(nt)>=R-Math.ceil(R/3))doruk(i)}})}g+=gs;continue}v=S.pat.S[i][q.s];pkk='S'}else{const fr=fb&&fillZone(q.s)&&x.fam==='vur';v=fr?S.pat.F[i][q.s]:p[i][q.s];if(v&&!allowed(pa.sec,x,i))continue;if(fr&&v){const sm=dyn;g+=fillRowVal(i,v)*sm;flash[i][q.s]=1;spawnPart(i,q.s);if(x.id==='davul'||x.fam==='vur'&&x.dmg>=4)kickP=Math.max(kickP,v===2?1:0.85);fire(i,q.s,v,pkk,sm,null,true);continue}}if(!v)continue;const sm=(soloing?SOLO_M:1)*dyn;g+=hitNota(pkk,i,v)*sm;
  if(vis||soloing){flash[i][q.s]=1;spawnPart(i,q.s)}
  if(x.id==='davul'||x.fam==='vur'&&x.dmg>=4){kickP=Math.max(kickP,v===2?1:0.85);if(S.stage.tunnel){if(!RM&&waves.length<8)waves.push({r:0,a:v===2?1:0.8,rot:Math.random()*TAU});enemies.forEach(e=>{if(e.d<0.95&&e.d>0.05)e.d=Math.min(1,e.d+(e.boss?0.008:0.02))})}}
  if(x.role==='delici'||x.role==='titresim')bassP=1;
  fire(i,q.s,v,pkk,sm);
 }
 earn(g*M*planBonus());
}
const globalMDmg=()=>tourM();
function setWave(n){n=clamp(n,1,Math.max(1,S.bestWave));S.wave=n;enemies=[];core.hp=hpMax();core.sh=0;if(playing)startWave(n,nowT());else wave=null;renderPanels();updUI()}
function ffSim(sec){let t=lastLogic||0;if(!wave){startWave(S.wave,t);lastLogic=t}const end=t+sec;const nd={2:{nextT:t,step:0},3:{nextT:t,step:0}};while(t<end){if(step>=MI.N){step=0;bar++}onStep({s:step,pk:pkFor(bar),t,b:bar});step++;if(step>=MI.N){step=0;bar++}const sd=60/curBpm(bar)/4;t+=sd;for(let k=2;k<=3;k++){if(!needleOn(k))continue;const n=nd[k],spec=NEEDLES[k-1];while(n.nextT<t){const cell=spec.dir>0?n.step%MI.N:(MI.N-1-n.step%MI.N);onStep({s:cell,pk:pkFor(bar),t:n.nextT,b:bar,k});n.nextT+=sd/spec.speed;n.step++}}logic(t);vfx.length=0;parts.length=0;pops.length=0}lastLogic=t}

