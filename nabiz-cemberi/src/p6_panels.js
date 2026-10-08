/* ================= panels ================= */
let tab='studio',soloSel=-1,soloEdSlot=-1,soloDrag=null,bookNew=false,eSel=0,eK=4,eRot=0,eGhost=0,resetArm=false,resetT=0;
const TABS=['studio','coll','def','book','look','album'];
const isPhone=()=>window.matchMedia('(max-width:700px)').matches;
function setTab(t){if(t==='stage'&&!isPhone())t='studio';tab=t;TABS.forEach(k=>{$('p-'+k).hidden=k!==t;$('t-'+k).setAttribute('aria-selected',String(k===t))});$('t-stage').setAttribute('aria-selected',String(t==='stage'));$('app').dataset.tab=t;if(t==='book'){bookNew=false;$('bookBadge').hidden=true}if(t==='def')$('defBadge').hidden=true;if(t==='coll')$('collBadge').hidden=true;const tb=$('t-'+t);if(tb&&tb.scrollIntoView){try{tb.scrollIntoView({block:'nearest',inline:'nearest'})}catch(e){}}if(t==='stage'){window.scrollTo(0,0);renderPads()}if(typeof tutPlace==='function')tutPlace()}
/* phone pad editor: the selected ring's steps as finger-sized buttons */
let soloRowSel=0;
function renderSoloPads(el,th){const si=soloEdSlot,x=slotIns(si),col=insColor(x,th),R=soloRows(),T=soloSteps();soloRowSel=clamp(soloRowSel,0,R-1);const so=S.solos[si]||(S.solos[si]={notes:[],style:'hendrix'});
 let h='<div class="padhead"><button class="btn ghost" data-act="soloRow" data-v="-1" aria-label="Pes halka">‹</button><span class="nm">'+x.n+' solo · '+soloNoteName(soloRowSel)+' <span class="lvl">halka '+(soloRowSel+1)+'/'+R+'</span></span><button class="btn ghost" data-act="soloRow" data-v="1" aria-label="Tiz halka">›</button></div>';
 for(let t=0;t<T;t++){const j=so.notes.findIndex(n=>nr(n)===soloRowSel&&t>=n.t&&t<n.t+noteLenEff(n));const n=so.notes[j];const v=n?(n.t===t?1:2):0;h+='<button class="pad'+(t%4===0?' g':'')+(j>=0&&j===soloSel?' sel':'')+'" data-act="spad" data-t="'+t+'" data-v="'+v+'" style="--c:'+col+'" aria-pressed="'+(v>0)+'" aria-label="Adım '+(t+1)+(v===1?', nota':v===2?', tutuş':'')+'">'+(v===2?'·':(t+1))+'</button>'}
 h+='<div class="padtb tb" id="soloTbStage"></div>';el.innerHTML=h;i18n(el);renderSoloTb()}
function renderPads(){const el=$('pads');if(!el)return;if(!isPhone()){el.hidden=true;return}el.hidden=false;const th=dispTheme();if(S.edit==='S'&&S.up.sdevir&&soloEdCur()>=0){renderSoloPads(el,th);return}eSel=clamp(eSel,0,S.slots.length-1);const x=slotIns(eSel),col=x?insColor(x,th):th.cv.dim,p=S.pat[S.edit];
 let h='<div class="padhead"><button class="btn ghost" data-act="padPrev" aria-label="Önceki sahne yeri">‹</button><span class="nm" id="padName">Yer '+(eSel+1)+' · '+(x?x.n+' <span class="lvl">Sv '+lvOf(x.id)+'</span>':'boş')+(S.edit==='S'?' · Solo deseni':S.edit==='B'?' · Desen B':'')+'</span><button class="btn ghost" data-act="padNext" aria-label="Sonraki sahne yeri">›</button></div>';
 for(let s=0;s<MI.N;s++){const v=x?p[eSel][s]:0;h+='<button class="pad'+(MI.gsSet.has(s)?' g':'')+'" data-act="pad" data-s="'+s+'" data-v="'+v+'" style="--c:'+col+'" aria-pressed="'+(v>0)+'" aria-label="Adım '+(s+1)+(v===2?', aksan':v?', vuruş':'')+'">'+(s+1)+'</button>'}
 el.innerHTML=h;i18n(el)}
function fxVal(th,k){const o=S.fxo[th.id];return o&&o[k]!=null?o[k]:(th.fx[k]||0)}
function eucPattern(k,rot){const N=MI.N,p=Array(18).fill(0);for(let s=0;s<N;s++){const x=(s-rot+N)%N;p[s]=k>0&&((x*k)%N)<k?1:0}return p}
function eucRows(){const np=eucPattern(eK,eRot),cur=S.pat[S.edit][eSel];return{[eSel]:np.map((v,s)=>v&&cur[s]===2?2:v)}}
function planReplace(pk,rows){let placed=placedCount(),cost=0;const cur=S.pat[pk];for(const i in rows)for(let s=0;s<MI.N;s++)if(cur[i][s]&&!rows[i][s]){placed--;cost-=Math.round(costAt(placed)/2)}for(const i in rows)for(let s=0;s<MI.N;s++)if(!cur[i][s]&&rows[i][s]){cost+=costAt(placed);placed++}return cost}
function eLabel(){const c=planReplace(S.edit,eucRows());return c>0?'Uygula · ♪ '+fmt(c):c<0?'Uygula · ♪ '+fmt(-c)+' geri':'Uygula'}
function applyRows(pk,rows,label){const c=planReplace(pk,rows);if(c>0&&S.nota<c){msg('Yeterli nota yok · ♪ '+fmt(c)+' gerekli');return false}S.nota-=c;for(const i in rows)for(let s=0;s<MI.N;s++)S.pat[pk][i][s]=rows[i][s];changed();if(label)msg(label);return true}
function clearRows(pk,which){const rows={};S.slots.forEach((id,si)=>{if(!id)return;if(which!=null&&which!==si)return;rows[si]=Array(18).fill(0)});const back=-planReplace(pk,rows);applyRows(pk,rows,(which!=null?(slotIns(which)||{n:'Yer'}).n+' yeri':'Desen '+pk)+' temizlendi · ♪ '+fmt(back)+' geri')}
function changed(){recalc();renderPanels();updUI()}
function cellClick(si,s){
 const x=slotIns(si);if(!x){msg('Bu sahne yeri boş. Stüdyo sekmesinden bir enstrüman koy.');return}
 if(S.edit==='S'&&!isSolo(si)){msg(x.n+' soloya ayrılmadı. Sahne listesinde Solo düğmesine bas.');return}
 if(S.edit==='F'){if(!isFillRow(si)){msg('Dolgu yalnız vurmalı satırlarda çalınır');return}if(!fillZone(s)){msg('Dolgu ölçünün son yarısında çalar: vuruşu sağ yarıya koy');return}}
 const p=S.pat[S.edit],v=p[si][s];
 if(S.edit==='F'&&v===0){let n=0;for(let k=0;k<MI.N;k++)if(fillZone(k)&&p[si][k])n++;if(n>=8){msg('Satır başına en çok 8 dolgu vuruşu');return}}
 if(v===0){const k=noteCost();if(S.nota<k){msg('Yeterli nota yok · ♪ '+fmt(k)+' gerekli');return}S.nota-=k;p[si][s]=1}
 else if(v===1&&S.up.accent){const k=accCost();if(S.nota<k){msg('Aksan için ♪ '+fmt(k)+' gerekli');return}S.nota-=k;p[si][s]=2}
 else{const pc=placedCount();p[si][s]=0;S.nota+=Math.round(costAt(pc-1)/2)}
 if(p[si][s]&&!playing){ensureAudio();voice(x,ac.currentTime+0.01,p[si][s],s)}
 changed();hintFor(hover);
}
function releaseAlbum(){
 const th=albumTh();if(S.runEarned<th){msg('Albüm için bu dönem ♪ '+fmt(th)+' kazanmalısın');return}
 const f=fansFor(),n=ALB[albumsN()%ALB.length]+(albumsN()>=ALB.length?' II':'');
 const keep={v:3,hayran:S.hayran+f,albums:[{n,f,b:S.bpm,w:S.wave}].concat(S.albums),found:S.found,theme:S.theme,themes:S.themes,famOpen:S.famOpen,layout:S.layout,stage:S.stage,fxo:S.fxo,orders:S.orders,bestWave:S.bestWave,kills:S.kills,total:S.total,muted:S.muted,buy:S.buy,last:Date.now(),tut:S.tut,mn:S.mn,auto:S.auto,efsane:S.efsane,cities:S.cities,tours:S.tours,city:S.city,albMax:Math.max(S.albMax||0,S.albums.length+1),sfx:S.sfx,lang:S.lang};
 S=Object.assign(freshRun(),keep);MI=meterInfo();eSel=0;enemies=[];wave=null;core={hp:hpMax(),sh:0};if(playing)startWave(1,nowT());
 const un=LADDER.find(x=>x.a===albumsN());msg('“'+n+'” çıktı · +'+f+' hayran'+(un?' · Açıldı: '+un.t:''));
 changed();applyTheme();save();
}
function nefesTxt(si){const p=S.pat[S.edit],n=rowLoad(p,si),nf=nefesOf(si,S.edit),f=NF[S.edit][si]||1;return 'nefes '+n+' / '+nf+(f<1?' · <span style="color:var(--hot)">fazla, güç ×'+fm(f)+'</span>':n===0?'':' · tam güç')}
function rowMultTxt(si){const m=ROWM[S.edit][si]||1;return m>1.001?' · <span style="color:var(--acc)">uyum ×'+fm(m)+'</span>':''}
function slotRowHtml(si,th){
 const x=slotIns(si),col=x?insColor(x,th):th.cv.dim;
 const bench=INS.filter(y=>lvOf(y.id)>0&&!S.slots.includes(y.id));
 const opts='<option value="">— boş —</option>'+(x?'<option value="'+x.id+'" selected>'+x.n+'</option>':'')+bench.map(y=>'<option value="'+y.id+'">'+y.n+' · Sv '+lvOf(y.id)+'</option>').join('');
 const sel='<select data-slot="'+si+'" aria-label="Sahne yeri '+(si+1)+'">'+opts+'</select>';
 if(!x)return '<div class="slot"><span class="dot" style="--c:'+col+';background:transparent;border:1.5px dashed '+th.cv.dim+'"></span><span>'+sel+'<span class="ds">Yer '+(si+1)+' boş'+(bench.length?' · yedekten seç':' · koleksiyondan enstrüman aç')+'</span></span><span class="cnt">'+STEPS(S.pat[S.edit],si).length+' vuruş</span></div>';
 const L=lvOf(x.id),nx=MS.find(m=>m>L),w=isWeapon(x.role);
 return '<div class="slot"><span class="dot" style="--c:'+col+'"></span><span>'+sel+'<span class="ds"><span class="role">'+roleName(x.role)+'</span> <span class="lvl">Sv '+L+'</span> ♪ '+fmt(noteVal(si,1))+(w||x.role==='titresim'?' · hasar '+fmt(dmgOf(si,1)):'')+' · '+(isSolo(si)?'<span style="color:var(--hot)">SOLO · döngüde normal çalar, solo bölümünde solo desenini ×3 çalar</span> · ':'')+(needleOf(si)>1?'<span style="color:var(--acc)">'+NEEDLES[needleOf(si)-1].n+'</span> · ':'')+nefesTxt(si)+rowMultTxt(si)+(nx?' · '+nx+'. seviyede ×2':'')+(muteUntil[si]>nowT()?' · SUSTURULDU':'')+'</span></span><span class="act">'+((S.up.needle2||S.up.needle3)?'<span class="seg" title="İbre">'+[1,2,3].filter(k=>k===1||(k===2&&S.up.needle2)||(k===3&&S.up.needle3)).map(k=>'<button data-act="needle" data-i="'+si+'" data-k="'+k+'" aria-pressed="'+(needleOf(si)===k)+'" aria-label="'+NEEDLES[k-1].n+'">'+k+'</button>').join('')+'</span>':'')+(S.up.solo?'<button class="btn'+(isSolo(si)?' ready':' ghost')+'" data-act="solo" data-i="'+si+'" aria-pressed="'+isSolo(si)+'">Solo</button>':'')+'<button class="btn ghost" data-act="clearRow" data-i="'+si+'" title="Bu yerin vuruşlarını kaldır" aria-label="Yeri temizle">×</button><button class="btn" id="lvb-'+x.id+'" data-act="lv" data-id="'+x.id+'" data-cost="0"></button></span></div>';
}
function insRowHtml(x,th){
 const L=lvOf(x.id),col=insColor(x,th),on=S.slots.includes(x.id);
 const stat=(isWeapon(x.role)||x.role==='titresim')?'♪ '+x.b+' · hasar '+x.dmg:'♪ '+x.b*(x.role==='gelir'?3:1)+' · ateş etmez';
 if(!L)return '<div class="row locked"><span class="dot" style="--c:'+col+'"></span><span><span class="nm">'+x.n+'</span><span class="ds"><span class="role">'+roleName(x.role)+'</span> '+x.d+' · '+stat+' · nefes '+x.nf+'</span></span><button class="btn" data-act="lv" data-id="'+x.id+'" data-cost="'+x.u+'">'+(x.u?'Aç · ♪ '+fmt(x.u):'Aç')+'</button></div>';
 return '<div class="row"><span class="dot" style="--c:'+col+'"></span><span><span class="nm">'+x.n+'<span class="lvl">Sv '+L+'</span></span><span class="ds"><span class="role">'+roleName(x.role)+'</span> '+ROLES[x.role].d+' · nefes '+x.nf+'</span></span>'+(on?'<span class="own">Sahnede</span>':(S.slots.includes(null)?'<button class="btn" data-act="place" data-id="'+x.id+'">Sahneye koy</button>':'<span class="cnt">Yedekte</span>'))+'</div>';
}
function renderPanels(){
 const th=dispTheme(),p=S.pat[S.edit];
 $('buyMode').innerHTML=[[1,'×1'],[10,'×10'],[0,'Maks']].map(([v,l])=>'<button data-act="buy" data-v="'+v+'" aria-pressed="'+(S.buy===v)+'">'+l+'</button>').join('');
 $('slotList').innerHTML=S.slots.map((id,si)=>slotRowHtml(si,th)).join('');renderPads();if(ac)sfLoadStage();
 $('slotAdd').innerHTML='<div class="arow" style="padding-top:10px"><span style="display:flex;gap:6px;flex-wrap:wrap"><button class="btn" data-act="clear">'+(S.edit==='S'?'Solo desenini':'Desen '+S.edit+'’yı')+' temizle</button>'+(hasB()?'<button class="btn ghost" data-act="clearBoth">İkisini de temizle</button>':'')+'</span>'+(S.slots.length<MAXSLOTS?'<button class="btn" data-act="addslot" data-cost="'+slotCost()+'">Sahne yeri ekle · '+S.slots.length+'/'+MAXSLOTS+' · ♪ '+fmt(slotCost())+'</button>':'<span class="cnt">Sahne dolu: 10 yer</span>')+'</div>';
 let ch='';FAMS.forEach(([f,fn])=>{if(!famOpen(f))return;ch+='<h3 class="fam">'+fn+'<span class="cnt">'+INS.filter(x=>x.fam===f&&lvOf(x.id)>0).length+' / '+INS.filter(x=>x.fam===f).length+' açık</span></h3>';INS.filter(x=>x.fam===f).forEach(x=>{ch+=insRowHtml(x,th)})});
 $('collList').innerHTML=ch;
 const nf=nextFam();
 $('capBox').innerHTML=nf?'<div class="ord'+(famCanOpen(nf[0])?' ok':'')+'"><h3>'+nf[1]+' ailesi<span>'+INS.filter(x=>x.fam===nf[0]).length+' enstrüman</span></h3><p>'+INS.filter(x=>x.fam===nf[0]).map(x=>x.n).join(', ')+'</p><ul>'+famReqs(nf[0]).map(r=>'<li class="'+(r.ok?'ok':'')+'">'+r.t+'</li>').join('')+'</ul><div class="arow"><span class="cnt">'+(FAMS.findIndex(x=>x[0]===nf[0]))+'. kapı</span><button class="btn'+(famCanOpen(nf[0])?' ready':' poor')+'" data-act="openFam" data-f="'+nf[0]+'">Aileyi aç</button></div></div>':'<p class="note">Bütün aileler açık. 42 enstrümanın hepsi koleksiyonda.</p>';
 const edOpts=[['A','Desen A']].concat(hasB()?[['B','Desen B']]:[]).concat(S.up.solo?[['S','Solo deseni']]:[]).concat(S.up.dolgu?[['F','Dolgu']]:[]);
 let pb='<div class="prow"><span class="pl">Düzenlenen</span><span style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">'+(edOpts.length>1?'<span class="seg">'+edOpts.map(([k,l])=>'<button data-act="ab" data-v="'+k+'" aria-pressed="'+(S.edit===k)+'">'+l+'</button>').join('')+'</span>':'<span class="ds">Desen A</span>')+(hasB()?'':'<span class="ds">B deseni ilk albümle açılır</span>')+'</span></div>'+(S.edit==='S'?'<p class="note">Solo deseni: yalnız soloya ayrılmış yerlerin satırları düzenlenir. Bu ritim solo bölümünde çalınır, notaları oyun seçer.</p>':'')
 +(S.edit==='F'?'<p class="note">Dolgu: her bölümün son ölçüsünün sağ yarısında vurmalılar bu deseni çalar, melodikler normal devam eder. Nefes kuralı işlemez ama her vuruş %60 değerinde, satır başına en çok 8 vuruş. 4+ vuruşluk dolgu zille çözülür: düşman 0,4 sn sarsılır, sonraki ölçü ×1,25 (kadansla ×1,5).</p><div class="prow"><label for="fillType">Dolgu üret</label><span style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><select id="fillType">'+Object.entries(FILLS).map(([k,v])=>'<option value="'+k+'">'+v.n+'</option>').join('')+'</select><button class="btn" data-act="fillGen">Sahnedeki vurmalılara dağıt</button><span class="cnt">'+fillHits()+' dolgu vuruşu</span></span></div>':'');
 if(hasB())pb+='<div class="prow"><span class="pl">Kopyala</span><span><button class="btn" data-act="copy">A’yı B’ye kopyala</button></span></div>';
 pb+='<div class="prow"><label for="selMeter">Ölçü</label><select id="selMeter">'+Object.entries(METERS).map(([k,m])=>'<option value="'+k+'"'+(k===S.meter?' selected':'')+(albUnl()<m.al?' disabled':'')+'>'+m.n+(m.bon?' · ×'+fm(m.bon):'')+(albUnl()<m.al?' · albüm '+m.al:'')+'</option>').join('')+'</select></div>';
 pb+='<div class="prow"><label for="selScale">Gam</label><select id="selScale">'+Object.entries(SCALES).map(([k,m])=>'<option value="'+k+'"'+(k===S.scale?' selected':'')+(albUnl()<m.al?' disabled':'')+'>'+m.n+(m.bon?' · ×'+fm(m.bon):'')+(albUnl()<m.al?' · albüm '+m.al:'')+'</option>').join('')+'</select></div>';
 $('patBox').innerHTML=pb;
 const pl=planArr(),pa=planAt(curBar);
 let ph='<p class="note">Şarkı 8 bölüm × 4 ölçü = 32 ölçü döner. '+(S.up.sef?'Bölümleri sen dizersin; 4+ farklı bölüm türü <b>şarkı bonusu ×1,25</b> verir.':'Şef geliştirmesi olmadan plan otomatik: '+(S.up.solo&&soloSlots().length?'kıta ve solo':hasB()?'kıta ve nakarat':'hep kıta')+'.')+'</p>';
 ph+='<div class="chips" id="planChips">'+pl.map((t,i)=>'<span class="chip'+(i===pa.idx?' on':'')+'" id="pc'+i+'">'+(i+1)+'. '+SECTS[t].n+'</span>').join('')+'</div>';
 if(S.up.sef){ph+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px;margin-top:10px">'+pl.map((t,i)=>'<select data-plan="'+i+'" aria-label="'+(i+1)+'. bölüm">'+SECT_ORDER.map(k=>'<option value="'+k+'"'+(k===t?' selected':'')+'>'+SECTS[k].n+'</option>').join('')+'</select>').join('')+'</div><div class="dev" style="padding-top:10px">'+Object.keys(PLANS).map(k=>'<button class="btn ghost" data-act="preset" data-v="'+k+'">'+PLAN_NAMES[k]+'</button>').join('')+'</div><p class="note" style="margin-top:8px">'+SECT_ORDER.map(k=>'<b style="color:var(--fg);font-weight:500">'+SECTS[k].n+'</b>: '+SECTS[k].d).join(' · ')+'</p>'}
 if(S.up.akor){const ps=PROGS[S.scale]||PROGS.minor;ph+='<div class="prow" style="margin-top:10px"><label for="selRate">Akor hızı</label><span style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><select id="selRate"><option value="beat"'+(S.prate==='beat'?' selected':'')+'>Vuruş başına (dört akor her ölçüde)</option><option value="bar"'+(S.prate==='bar'?' selected':'')+'>Ölçü başına (bölümün dört ölçüsünde dört akor)</option></select><span class="cnt">zıtlık '+(contrastM()>1?'×1,1':'yok')+'</span></span></div>';
  ph+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px;margin-top:6px">'+pl.map((t,i)=>'<label class="cnt" style="display:grid;gap:3px">'+(i+1)+'. '+SECTS[t].n+(kadansAt(i)?' · <span style="color:var(--acc)">kadans</span>':'')+(makamM(i)>1?' · <span style="color:var(--acc)">makam</span>':'')+'<select data-prog="'+i+'" aria-label="'+(i+1)+'. bölüm akor yürüyüşü">'+Object.entries(ps).map(([k,v])=>'<option value="'+k+'"'+((S.prog[i]||'pop')===k?' selected':'')+'>'+v.n+'</option>').join('')+'</select></label>').join('')+'</div><p class="note" style="margin-top:6px">Kadans: bölüm V ile bitip sonraki kökle başlarsa geçiş ölçüsü ×1,25. Zıtlık: iki farklı yürüyüş ×1,1. Hicaz/kürdide Durak–Güçlü ×1,1.</p>'}
 $('planBox').innerHTML=(demoMode?'<p class="note"><b style="color:var(--fg);font-weight:500">Örnek şarkı '+(demoIdx+1)+' · '+DEMOS[demoIdx].name+' nasıl kuruldu:</b> '+DEMOS[demoIdx].notes.join(' · ')+'</p>':'')+ph;
 const tc=tempoCost(),fit=ownTheme().bpm,free=S.bpm<S.bmax;
 let h='<div class="row noicon"><span><span class="nm">Tempo · '+S.bpm+' BPM</span><span class="ds">'+ownTheme().n+' teması '+fit[0]+'–'+fit[1]+' BPM sever'+(fitM()>1?' · uyum ×1,25 aktif':'')+'</span></span><span style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end"><span class="seg"><button data-act="tempoDown" aria-label="Tempoyu 10 BPM düşür">−10</button></span>'+(S.bpm>=180?'<span class="own">Maksimum</span>':'<button class="btn" data-act="tempo" data-cost="'+(free?0:tc)+'">+10 · '+(free?'ücretsiz':'♪ '+fmt(tc))+'</button>')+'</span></div>';
 h+=RUP.map(u=>'<div class="row noicon"><span><span class="nm">'+u.n+'</span><span class="ds">'+u.d+'</span></span>'+(S.up[u.id]?'<span class="own">Alındı</span>':'<button class="btn" data-act="rup" data-id="'+u.id+'" data-cost="'+u.c+'">♪ '+fmt(u.c)+'</button>')+'</div>').join('');
 $('rhyList').innerHTML=h;
 const eb=$('euclidBox');
 if(S.up.euclid){
  if(!S.slots[eSel]){eSel=S.slots.findIndex(id=>id);if(eSel<0)eSel=0}eK=Math.min(eK,MI.N);eRot=Math.min(eRot,MI.N-1);
  const opts=S.slots.map((id,si)=>id?'<option value="'+si+'"'+(si===eSel?' selected':'')+'>'+(si+1)+' · '+IDX[id].n+'</option>':'').join('');
  eb.innerHTML='<div class="euc"><p class="euct">Öklid üretici · desen '+S.edit+'</p><label for="eRing">Yer</label><select id="eRing">'+opts+'</select><label for="eK">Vuruş <b id="eKv">'+eK+'</b></label><input id="eK" type="range" min="0" max="'+MI.N+'" step="1" value="'+eK+'"><label for="eRot">Kaydır <b id="eRv">'+eRot+'</b></label><input id="eRot" type="range" min="0" max="'+(MI.N-1)+'" step="1" value="'+eRot+'"><button class="btn" id="eApply" data-act="euclid" data-cost="'+Math.max(0,planReplace(S.edit,eucRows()))+'">'+eLabel()+'</button></div>';
 }else eb.innerHTML='';
 $('synChips').innerHTML=SYN.map(y=>'<span class="chip" id="sy'+y.id+'" title="'+y.w+'">'+y.n+'<b>×'+fm(y.m)+'</b><small>'+y.d+'</small></span>').join('');
 $('combos').innerHTML=COMBOS.map((k,j)=>'<span class="chip" id="cb'+j+'">'+k.n+'<b>'+pct(k.b)+'</b><small>'+k.d+'</small></span>').join('')+'<span class="chip bad" id="cbP">'+PEN.n+'<b>×'+fm(PEN.m)+'</b><small>'+PEN.d+'</small></span>';
 renderDef();renderSoloBox();renderSoloTree();
 const fc=Object.keys(S.found).length;
 $('bookBox').innerHTML='<h2>Kalıp kitabı <span class="cnt">'+fc+' / '+BOOK.length+' · keşif ×'+fm(bookM())+'</span></h2><p class="note">Bir sahne yerinde aşağıdaki ritimlerden birini birebir kurduğunda kalıp bulunur: keşif kalıcı +%5 verir, kalıbı sahnede çalmaya devam ettiğin sürece de kalıbın kendi etkisi açılır.</p><div class="bookg">'+BOOK.map(e=>{
  const f=!!S.found[e.id],m=METERS[e.m],locked=albUnl()<m.al,g=meterInfoFor(e.m),act=BOOKON[S.edit][e.id]!=null;let st='<div class="steps" aria-hidden="true">';for(let s=0;s<g.N;s++)st+='<i class="'+(f&&e.s.includes(s)?'on ':'')+(g.gsSet.has(s)?'g':'')+'"></i>';st+='</div>';
  return '<div class="bk'+(f?' found':'')+'"><h3>'+(f?e.n:'???')+'<span>'+(act?'<span style="color:var(--acc)">çalıyor</span> · ':'')+m.n.split(' ')[0]+'</span></h3><p>'+(f?e.lore+' <b style="color:var(--fg);font-weight:500">Çalınca: '+e.e+'.</b>':(locked?'Bu ölçü albüm '+m.al+' ile açılır. ':'')+'İpucu: '+e.h+' · '+e.s.length+' darbe')+'</p>'+st+'</div>'}).join('')+'</div>';
 $('layoutBox').innerHTML='<span class="seg"><button data-act="layout" data-v="circle" aria-pressed="'+(S.layout==='circle')+'">Çember</button><button data-act="layout" data-v="strip" aria-pressed="'+(S.layout==='strip')+'"'+(hasB()?'':' disabled')+'>Şerit'+(hasB()?'':' · albüm 1')+'</button></span>';
 $('themeList').innerHTML=THEME_ORDER.map(id=>{const t=THEMES[id],own=themeOwned(id),cur=S.theme===id;
  return '<div class="tc'+(cur?' cur':'')+'"><div class="sw">'+[t.cv.bg,t.fam.vur,t.fam.tel,t.fam.tus,t.cv.acc].map(c=>'<span style="background:'+c+'"></span>').join('')+'</div><h3 style="font-family:'+t.font.d.replace(/"/g,'&quot;')+'">'+t.n+'</h3><p>'+t.blurb+' Sevdiği tempo '+t.bpm[0]+'–'+t.bpm[1]+' BPM.</p><div class="act">'+(cur?'<span class="own">Kullanılıyor</span>':own?'<button class="btn" data-act="theme" data-id="'+id+'">Kullan</button>':'<button class="btn" data-act="buyTheme" data-id="'+id+'" data-cost="'+t.c+'">♪ '+fmt(t.c)+'</button><button class="btn ghost" data-act="preview" data-id="'+id+'">20 sn önizle</button>')+'</div></div>'}).join('');
 $('stageList').innerHTML=SUP.map(u=>'<div class="row noicon"><span><span class="nm">'+u.n+'</span><span class="ds">'+u.d+'</span></span>'+(S.stage[u.id]?'<span class="own">Sahnede</span>':'<button class="btn" data-act="stage" data-id="'+u.id+'" data-cost="'+u.c+'">♪ '+fmt(u.c)+'</button>')+'</div>').join('');
 $('fxBox').innerHTML='<div class="row noicon"><span><span class="nm">Örnek sesler</span><span class="ds">Teller, tuşlular, nefesliler ve davul seti gerçek enstrüman kayıtlarıyla (FluidR3 General MIDI, MIT lisanslı) çalar; saz, elektronik aile, didgeridoo ve tabla sentez kalır. Kayıt yüklenemezse sentez devam eder. <span id="sfInfo" class="cnt" style="white-space:normal"></span></span></span><span class="seg"><button data-act="sfx" data-v="1" aria-pressed="'+(S.sfx!==false)+'">Açık</button><button data-act="sfx" data-v="0" aria-pressed="'+(S.sfx===false)+'">Kapalı</button></span></div><div class="fx" style="margin-bottom:8px"><label for="sfVol">Örnek ses seviyesi<small>Kayıtların sentez katmanına göre yüksekliği</small></label><input type="range" id="sfVol" min="0.25" max="2" step="0.05" value="'+(S.sfv||1)+'"><output id="sfVolO">×'+fm(S.sfv||1)+'</output></div>'+(GLX?'<p class="note">WebGL son işlem zinciri çalışıyor: iz, iki geçişli bloom, sonra tek geçişte diğer efektler. Ayarlar şu an görünen temaya ('+th.n+') kaydedilir.</p>':'<p class="note">Bu cihazda WebGL açılamadı, efektler kapalı. Oyun düz canvas ile çalışıyor.</p>')+'<div class="fx">'+FXK.map(([k,n,d,mn,mx])=>{const v=fxVal(th,k);return '<label for="fx-'+k+'">'+n+'<small>'+d+'</small></label><input id="fx-'+k+'" type="range" min="'+mn+'" max="'+mx+'" step="0.01" value="'+v+'" data-fx="'+k+'"'+(GLX||k==='shake'?'':' disabled')+'><output id="fo-'+k+'">'+fm(v)+'</output>'}).join('')+'</div><div class="dev"><button class="btn" data-act="fxreset">'+th.n+' varsayılanına dön</button></div>';
 sfStatus();
 $('albumBox').innerHTML='<p class="note">Albüm çıkarınca döngü, sahne, seviyeler, savunma geliştirmeleri ve dalga sıfırlanır. Hayranlar, bulunan kalıplar, açılan aileler, temalar ve sahne katmanları kalır. Her hayran gelire kalıcı %5 ekler.</p><div class="prog"><span id="aBar"></span></div><div class="arow"><span class="cnt" id="aTxt"></span><button class="btn" id="aBtn" data-act="album">Albüm çıkar</button></div><ol class="ladder">'+LADDER.map(x=>'<li class="'+(albUnl()>=x.a?'done':'')+'"><b>Albüm '+x.a+'</b><span>'+x.t+'</span></li>').join('')+'</ol>'+(S.albums.length?'<ol class="disco">'+S.albums.map(a=>'<li><span class="an">'+a.n+'</span><span class="cnt">+'+a.f+' hayran · '+a.b+' BPM · dalga '+(a.w||1)+'</span></li>').join('')+'</ol>':'');
 renderMn();renderTour();
 $('mute').textContent=T(S.muted?'Ses kapalı':'Ses açık');
 $('tag').textContent=T((demoMode?'örnek şarkı '+(demoIdx+1)+' · ':'v12 · ')+(S.tours||Object.keys(S.cities||{}).length?cityOf().n+' · ':'')+th.n+' · '+(S.layout==='strip'?'şerit':'çember')+' · '+METERS[S.meter].n.split(' ')[0]+(previewId&&performance.now()<previewUntil?' · önizleme':''));
 if(S.lang==='en'){i18n($('rack'));i18n($('pads'));i18n($('tut'))}
 updUI();
}
function soloEdSlots(){return soloSlots().filter(si=>{const x=slotIns(si);return x&&x.fam!=='vur'})}
function soloEdCur(){const ss=soloEdSlots();if(!ss.length)return -1;if(!ss.includes(soloEdSlot))soloEdSlot=ss[0];return soloEdSlot}
function susTxt(x){const p=susOf(x);let t=SUS_N[p.k];if(p.k==='decay'){const d=(S.up.tk_tus1&&tkgOf(x)==='tus')?Math.max(p.d,0.9):p.d;let al=1;for(let k=1;k<32;k++){if(Math.pow(d,k)<0.08)break;al++}t+=': sönme ×'+fm(d)+' / adım, '+al+' adımda biter'}else if(p.k==='breath')t+=': nefes '+(S.up.tk_nef1?'sınırsız (dairesel nefes)':p.max+' adım, sonra kesilir');else t+=': hiç bitmez, güç her adımda yavaş düşer';return t}
function badgeHtml(A){const b=(on,l)=>'<span class="chip'+(on?' on':'')+'">'+l+'</span>';return '<div class="chips" style="margin-top:6px">'+b(A.karar,'Karar ×1,25')+b(A.doruk,'Doruk ×1,2')+b(A.sc,'Soru–cevap ×1,15')+(A.mg?'<span class="chip bad on">Makineli −'+A.mg+' nota</span>':b(false,'Makineli yok'))+'</div>'}
function renderSoloBox(){
 const el=$('soloBox');if(!el)return;
 if(!S.up.solo){el.innerHTML='<p class="note">Ritim stüdyosundaki “Solo izni” ile açılır.</p>';return}
 const ss=soloEdSlots();if(!ss.length){el.innerHTML='<p class="note">Melodik bir enstrümanın (tel, tuş, nefesli, elektronik, dünya) yanındaki Solo düğmesine bas; solo editörü burada açılır. Vurmalılar solo olarak kendi ritim desenlerini çalar.</p>';return}
 soloEdCur();const x=slotIns(soloEdSlot),so=S.solos[soloEdSlot]||(S.solos[soloEdSlot]={notes:[],style:'hendrix'}),dev=!!S.up.sdevir;
 const head='<div class="tb"><label class="cnt" for="soloSlotSel">Solo yeri</label><select id="soloSlotSel">'+ss.map(si=>'<option value="'+si+'"'+(si===soloEdSlot?' selected':'')+'>'+(si+1)+' · '+slotIns(si).n+'</option>').join('')+'</select><label class="cnt" for="soloStyle">Stil</label><select id="soloStyle">'+Object.entries(SOLO_STYLES).map(([k,v])=>'<option value="'+k+'"'+(so.style===k?' selected':'')+'>'+v.n+'</option>').join('')+'</select><button class="btn" data-act="soloGen">Üret</button><button class="btn ghost" data-act="soloVar">Varyasyon</button><button class="btn ghost" data-act="soloClear">Temizle</button><span class="cnt">'+so.notes.length+' / '+SOLO_MAX+' nota</span></div>';
 const prof='<p class="note" style="margin-top:8px"><b style="color:var(--fg);font-weight:500">'+x.n+'</b> · '+susTxt(x)+(S.up.suzun?'':' · uzun nota için dalda “Uzun nota” gerekir')+'</p>';
 const tail='<p class="note" style="margin-top:6px">'+SOLO_STYLES[so.style||'hendrix'].d+'</p>'+(S.up.sseyir?badgeHtml(analyzeSolo(soloEdSlot)):'');
 if(dev){
  el.innerHTML='<p class="note">Sahne devri açık: solo sahnede çizilir. Halka = perde (içerisi pes, dışarısı tiz), bir tur = 2 ölçü. Boş yere bas: nota · '+(S.up.suzun?'halka boyunca sürükle: uzat · bir barı başka bara değdir: tek bar olurlar · ':'')+'başka halkaya sürükle: perde · notaya bas: seç. Solo bölümünde '+x.n+' sahneyi devralır ve bu notaları ×3 güçte çalar.</p>'+head+'<div class="tb"><button class="btn'+(S.edit==='S'?' ready':'')+'" data-act="soloStage">'+(S.edit==='S'?'Sahnede düzenleniyor':'Sahnede düzenle')+'</button>'+(S.edit==='S'?'<button class="btn ghost" data-act="ab" data-v="A">Desen A’ya dön</button>':'')+'</div>'+prof+tail+'<div class="tb" id="soloTb"></div>';
 }else{
  el.innerHTML='<p class="note">Yatay eksen zaman: 2 ölçü, '+soloSteps()+' adım. Dikey eksen solo gamı: hangi satıra koyarsan koy uyumlu. Boş yere bas'+(S.up.suzun?' ve sağa sürükle: nota uzar':'')+'. Notaya bas: seç. Solo bölümünde bu notalar '+x.n+' ile ×3 güçte çalar. Dalda “Sahne devri” alınca solo sahneye taşınır.</p>'+head+prof+tail+'<div class="soloScroll"><canvas id="soloCv" aria-label="Solo editörü: zaman yatay, nota dikey"></canvas></div><div class="tb" id="soloTb"></div>';
 }
 renderSoloTb();drawSoloEd();
}
function renderSoloTree(){const el=$('soloTree');if(!el)return;if(!S.up.solo){el.innerHTML='<p class="note">Solo dalı Ritim stüdyosundaki “Solo izni” ile açılır. Tek seferlik bir geliştirme değil: sahneyi büyüten, aileye özel teknik veren ve iyi soloyu ödüllendiren bir ağaç.</p>';return}
 const lanes=[['Sahne','Sahne: solo nereye kadar büyür'],['Teknik','Teknikler: aileye özel, her biri ayrı alınır'],['Biçim','Biçim: iyi kurulmuş solo ödüllenir']];let h='';
 lanes.forEach(([ln,title])=>{h+='<h3 class="fam">'+title+'</h3>';SOLO_TREE.filter(u=>u.lane===ln).forEach(u=>{const own=!!S.up[u.id],lock=u.req&&!S.up[u.req],rn=u.req?(TREE_IDX[u.req]||RUP.find(r=>r.id===u.req)||{n:u.req}).n:'';
  h+='<div class="row noicon'+(lock?' locked':'')+'"><span><span class="nm">'+u.n+'</span><span class="ds">'+u.d+(lock?' · <b style="color:var(--fg);font-weight:500">önce '+rn+'</b>':'')+'</span></span>'+(own?'<span class="own">Alındı</span>':lock?'<span class="cnt">kilitli</span>':'<button class="btn" data-act="srup" data-id="'+u.id+'" data-cost="'+u.c+'">♪ '+fmt(u.c)+'</button>')+'</div>'})});
 el.innerHTML=h}
function renderSoloTb(){const so=S.solos[soloEdSlot];const nt=so&&so.notes[soloSel];const x=slotIns(soloEdSlot);let h;
 if(!nt)h='<span class="cnt">Nota seçili değil</span>';
 else{const L=noteLenEff(nt);h='<span class="cnt">'+soloNoteName(nr(nt))+' · adım '+(nt.t+1)+' · uzunluk '+L+(x&&L>1?' · güç '+fm(1+noteSus(x,nt)):'')+'</span><span class="seg">'+artList(x).map(k=>{const ok=artOk(x,k);return '<button data-act="soloArt" data-k="'+k+'" aria-pressed="'+(nt.art===k)+'"'+(ok?'':' disabled title="Solo dalında teknik düğümü gerekir"')+'>'+SOLO_ART[k].g+' '+SOLO_ART[k].n+(ok?'':' (kilitli)')+'</button>'}).join('')+'</span>'+(S.up.suzun?'<button class="btn ghost" data-act="soloLen" data-v="1">Uzat</button><button class="btn ghost" data-act="soloLen" data-v="-1">Kısalt</button>':'')+'<button class="btn ghost" data-act="soloDel">Sil</button>'}
 ['soloTb','soloTbStage'].forEach(id=>{const tb=$(id);if(tb){tb.innerHTML=h;i18n(tb)}})}
function soloGeom(cv){const T=soloSteps(),R=soloRows(),host=cv.parentElement,w0=((host&&host.classList.contains('soloScroll'))?host.getBoundingClientRect().width:cv.getBoundingClientRect().width)||600,lab=34,w=isPhone()?Math.max(w0,lab+T*22):w0,cw=(w-lab)/T,ch=Math.max(13,Math.min(isPhone()?26:20,Math.round(cw*1.25)));return{T,R,w,lab,cw,ch,h:ch*R+18}}
function drawSoloEd(){const cv=$('soloCv');if(!cv)return;const th=dispTheme(),g=soloGeom(cv),dpr=Math.min(2,window.devicePixelRatio||1);if(cv.width!==Math.round(g.w*dpr)||cv.height!==Math.round(g.h*dpr)){cv.width=Math.round(g.w*dpr);cv.height=Math.round(g.h*dpr);cv.style.height=g.h+'px';cv.style.width=g.w+'px'}const c=cv.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.fillStyle=th.cv.bg;c.fillRect(0,0,g.w,g.h);
 const x=slotIns(soloEdSlot),col=x?insColor(x,th):th.cv.acc,so=S.solos[soloEdSlot]||{notes:[]};
 for(let r=0;r<g.R;r++){const y=18+(g.R-1-r)*g.ch;c.fillStyle=hexA(th.cv.ink,r%(soloRows()>>1)===0?0.06:0.025);c.fillRect(g.lab,y,g.w-g.lab,g.ch-1);c.fillStyle=hexA(th.cv.ink,0.6);c.font='500 10px '+th.font.m;c.textAlign='right';c.textBaseline='middle';c.fillText(soloNoteName(r),g.lab-5,y+g.ch/2)}
 for(let t=0;t<=g.T;t++){const xx=g.lab+t*g.cw;c.strokeStyle=hexA(th.cv.ink,t%MI.N===0?0.45:MI.gsSet.has(t%MI.N)?0.22:0.08);c.lineWidth=1;c.beginPath();c.moveTo(xx,18);c.lineTo(xx,g.h);c.stroke()}
 c.fillStyle=hexA(th.cv.ink,0.55);c.font='600 10px '+th.font.m;c.textAlign='left';c.textBaseline='top';c.fillText('1. ölçü',g.lab+3,3);c.fillText('2. ölçü',g.lab+MI.N*g.cw+3,3);
 so.notes.forEach((nt,i)=>{const xx=g.lab+nt.t*g.cw+1,y=18+(g.R-1-nr(nt))*g.ch+1.5,ww=noteLenEff(nt)*g.cw-2,hh=g.ch-4;c.fillStyle=hexA(col,i===soloSel?1:0.78);c.beginPath();c.roundRect?c.roundRect(xx,y,ww,hh,3):c.rect(xx,y,ww,hh);c.fill();if(i===soloSel){c.strokeStyle=th.cv.ink;c.lineWidth=1.5;c.stroke()}if(nt.art&&nt.art!=='none'){c.fillStyle=th.cv.ink;c.font='600 10px '+th.font.m;c.textAlign='left';c.textBaseline='middle';c.fillText(SOLO_ART[nt.art].g,xx+3,y+hh/2)}});
 if(playing&&soloNow===soloEdSlot){const pa=planAt(curBar);const off=(pa.barIn%2)*MI.N+Math.floor(phase*MI.N);const xx=g.lab+off*g.cw;c.fillStyle=hexA(th.cv.hot,0.35);c.fillRect(xx,18,g.cw,g.h-18)}
}
function soloHit(e){const cv=$('soloCv');if(!cv)return null;const b=cv.getBoundingClientRect(),g=soloGeom(cv),px=e.clientX-b.left,py=e.clientY-b.top;if(px<g.lab||py<18)return null;const t=Math.floor((px-g.lab)/g.cw),r=g.R-1-Math.floor((py-18)/g.ch);if(t<0||t>=g.T||r<0||r>=g.R)return null;return{t,r}}
document.addEventListener('pointerdown',e=>{const cv=e.target.closest('#soloCv');if(!cv)return;const h=soloHit(e);if(!h)return;const so=S.solos[soloEdSlot]||(S.solos[soloEdSlot]={notes:[],style:'hendrix'});const idx=so.notes.findIndex(n=>nr(n)===h.r&&h.t>=n.t&&h.t<n.t+noteLenEff(n));if(idx>=0){soloSel=idx;soloDrag=S.up.suzun?{i:idx,t0:so.notes[idx].t,mode:'resize'}:null;renderSoloTb();drawSoloEd();return}if(so.notes.length>=SOLO_MAX){msg('En fazla '+SOLO_MAX+' solo notası');return}so.notes.push({t:h.t,len:1,r:h.r,art:'none'});so.notes.sort((a,b)=>a.t-b.t);soloSel=so.notes.findIndex(n=>n.t===h.t&&n.r===h.r);soloDrag=S.up.suzun?{i:soloSel,t0:h.t,mode:'new'}:null;cv.setPointerCapture&&cv.setPointerCapture(e.pointerId);if(!playing&&slotIns(soloEdSlot)){ensureAudio();soloVoice(slotIns(soloEdSlot),ac.currentTime+0.01,h.r,0.35,'none',1)}renderSoloTb();drawSoloEd();e.preventDefault()});
document.addEventListener('pointermove',e=>{if(!soloDrag)return;const h=soloHit(e);if(!h)return;const so=S.solos[soloEdSlot];const nt=so&&so.notes[soloDrag.i];if(!nt)return;const len=clamp(h.t-nt.t+1,1,soloSteps()-nt.t);if(len!==nt.len){nt.len=len;soloDrag.i=soloMerge(so,nt);soloSel=soloDrag.i;drawSoloEd();renderSoloTb()}});
document.addEventListener('pointerup',()=>{if(soloDrag){soloDrag=null;recalc();updUI();renderSoloTb()}});
function renderMn(){const el=$('mnBox');if(!el)return;if(albUnl()<1){el.innerHTML='<p class="note">Menajer ilk albümle gelir: seviye alma, sipariş teslimi, sahne kurma ve albüm çıkarma kademe kademe otomatikleşir; her kademe ayrı alınır ve istediğin an kapatılır.</p>';return}
 el.innerHTML='<p class="note">Albümden albüme kalır. Açık olanlar sen yokken de çalışır (çevrimdışı değil, sekme açıkken).</p>'+AUTO.map(u=>{const own=!!S.mn[u.id],lock=albUnl()<u.al;return '<div class="row noicon'+(lock?' locked':'')+'"><span><span class="nm">'+u.n+'</span><span class="ds">'+u.d+(lock?' · <b style="color:var(--fg);font-weight:500">'+u.al+'. albümle</b>':'')+'</span></span>'+(own?'<span class="seg"><button data-act="mnTog" data-id="'+u.id+'" data-v="1" aria-pressed="'+(S.auto[u.id]!==false)+'">Açık</button><button data-act="mnTog" data-id="'+u.id+'" data-v="0" aria-pressed="'+(S.auto[u.id]===false)+'">Kapalı</button></span>':lock?'<span class="cnt">kilitli</span>':'<button class="btn" data-act="mnBuy" data-id="'+u.id+'" data-cost="'+u.c+'">♪ '+fmt(u.c)+'</button>')+'</div>'}).join('')}
function renderTour(){const el=$('tourBox');if(!el)return;const c=cityOf(),nx=CITIES[(S.city+1)%CITIES.length],vis=Object.keys(S.cities).length;
 el.innerHTML='<div class="dstat"><div><b>'+c.n+'</b><small>şehir · '+(S.tours+1)+'. turne</small></div><div><b>'+S.efsane+'</b><small>Efsane · gelir ve hasar ×'+fm(tourM())+'</small></div><div><b>'+vis+' / '+CITIES.length+'</b><small>gezilen şehir · her biri +%2</small></div></div>'
 +'<p class="note"><b style="color:var(--fg);font-weight:500">'+c.n+'</b> · '+c.d+'. Sevdiği gam '+SCALES[c.scale].n.split(' ')[0]+(S.scale===c.scale?' <span style="color:var(--acc)">(uyuyor ×1,1)</span>':'')+', ölçü '+METERS[c.meter].n.split(' ')[0]+(S.meter===c.meter?' <span style="color:var(--acc)">(uyuyor ×1,1)</span>':'')+'.</p>'
 +'<p class="note">Turne: '+TOUR_AL+' albümden sonra çıkılır. Albümler ve hayranlar sıfırlanır, albüm eşiği başa döner; kalıplar, aileler, temalar, sahne katmanları, menajer ve açılan ölçü/gamlar kalır. Karşılığı kalıcı Efsane: şu an çıkarsan +'+tourGain()+' (2·√hayran + albüm). Sıradaki şehir: '+nx.n+' · '+nx.d+'.</p>'
 +'<div class="arow"><span class="cnt">'+(canTour()?'Hazır':albumsN()+' / '+TOUR_AL+' albüm')+'</span><button class="btn'+(canTour()?' ready':' poor')+'" data-act="tour" id="tourBtn">Turneye çık</button></div>'
 +(vis?'<div class="chips" style="margin-top:8px">'+CITIES.map(x=>'<span class="chip'+(S.cities[x.id]?' on':'')+'">'+x.n+'</span>').join('')+'</div>':'')}
let tourArm=false,tourT=0;
function goTour(){if(!canTour()||demoMode)return;const gain=tourGain(),c=cityOf();S.cities[c.id]=1;
 const keep={v:3,hayran:0,albums:[],found:S.found,theme:S.theme,themes:S.themes,famOpen:S.famOpen,layout:S.layout,stage:S.stage,fxo:S.fxo,orders:[],bestWave:S.bestWave,kills:S.kills,total:S.total,muted:S.muted,buy:S.buy,last:Date.now(),tut:S.tut,mn:S.mn,auto:S.auto,efsane:S.efsane+gain,cities:S.cities,tours:S.tours+1,city:(S.city+1)%CITIES.length,albMax:Math.max(S.albMax||0,S.albums.length),sfx:S.sfx,lang:S.lang};
 S=Object.assign(freshRun(),keep);MI=meterInfo();eSel=0;enemies=[];wave=null;core={hp:hpMax(),sh:0};ensureOrders();if(playing)startWave(1,nowT());msg(c.n+' turnesi bitti · +'+gain+' Efsane · sıradaki şehir '+cityOf().n);changed();applyTheme();save()}
/* manager: runs every 2 s while the page is open */
let autoT=0;
function autoTick(){if(demoMode||!S.mn)return;const now=Date.now();let ch=false;
 if(S.mn.lv&&S.auto.lv!==false&&now-autoT>10000){autoT=now;const sv=S.buy;S.buy=1;let best=null;S.slots.forEach(id=>{if(!id)return;const x=IDX[id];const q=lvQuote(x);if(q.unlock)return;if(q.c<=S.nota*0.5&&(!best||q.c<best.q.c))best={x,q}});S.buy=sv;if(best){S.nota-=best.q.c;S.lv[best.x.id]+=best.q.n;ch=true}}
 if(S.mn.ord&&S.auto.ord!==false){S.orders.forEach((o,k)=>{if(o&&o.tpl&&orderOk(o)){deliver(k);ch=true}})}
 if(S.mn.ins&&S.auto.ins!==false){const empty=S.slots.indexOf(null);if(empty>=0){const cand=INS.filter(x=>!lvOf(x.id)&&famOpen(x.fam)&&x.u<=S.nota*0.25).sort((a,b)=>a.u-b.u)[0];if(cand){S.nota-=cand.u;S.lv[cand.id]=1;S.slots[empty]=cand.id;const row=Array(18).fill(0);const steps=cand.fam==='vur'?MI.gs.slice(0,Math.min(cand.nf,MI.gs.length)):[MI.gs[0],MI.gs[Math.min(2,MI.gs.length-1)]];steps.forEach(st=>{const k=noteCost();if(S.nota>=k){S.nota-=k;row[st]=1}});S.pat.A[empty]=row;msg('Menajer '+cand.n+' açtı, '+(empty+1)+'. yere koydu');ch=true}}}
 if(S.mn.alb&&S.auto.alb===true&&S.runEarned>=albumTh()*2){releaseAlbum();return}
 if(ch)changed()}
function renderDef(){
 const el=$('defStatus');if(!el)return;
 el.innerHTML='<div class="dstat"><div><b id="dWave">'+S.wave+'</b><small>Dalga · en iyi '+S.bestWave+'</small></div><div><b id="dEn">0</b><small>Sahnedeki düşman</small></div><div><b id="dDps">0</b><small>Hasar / sn</small></div><div><b id="dKills">'+fmt(S.kills)+'</b><small>Susturulan</small></div></div><div class="arow"><span class="cnt">Nabız <span id="dHp"></span> · Kalkan <span id="dSh"></span> · Menzil %'+Math.round(range()*100)+'</span><span style="display:flex;gap:6px"><button class="btn" data-act="waveBack">5 dalga geri</button><button class="btn" data-act="waveFwd"'+(S.wave>=S.bestWave?' disabled':'')+'>5 ileri</button></span></div><div class="hpbar"><span class="hp" id="dHpBar"></span><span class="sh" id="dShBar"></span></div><p class="note" id="dComp">Bu dalga: '+waveSummary(S.wave)+'</p>';
 $('defList').innerHTML=DUP.map(u=>{const L=S.def[u.id]||0,max=u.max&&L>=u.max;return '<div class="row noicon"><span><span class="nm">'+u.n+'<span class="lvl">'+(L?'Sv '+L:'')+'</span></span><span class="ds">'+u.d+'</span></span>'+(max?'<span class="own">Maksimum</span>':'<button class="btn" data-act="def" data-id="'+u.id+'" data-cost="'+defCost(u)+'">♪ '+fmt(defCost(u))+'</button>')+'</div>'}).join('');
 ensureOrders();
 $('orderList').innerHTML=S.orders.map((o,k)=>{if(!o.tpl){const left=Math.max(0,Math.ceil((o.ready-Date.now())/1000));return '<div class="ord"><h3>Yeni sipariş<span>'+Math.floor(left/60)+':'+String(left%60).padStart(2,'0')+'</span></h3><p>Şehir yeni bir istek hazırlıyor.</p></div>'}const t=OTPL.find(x=>x.id===o.tpl);const rq=t.req(o);return '<div class="ord" id="ord'+k+'"><h3>'+t.t+'<span>'+t.who+'</span></h3><ul>'+rq.map((r,j)=>'<li id="oq'+k+'_'+j+'">'+r.t+'</li>').join('')+'</ul><div class="arow"><span class="cnt">'+Math.round(t.secs/60)+' dk gelir · +'+t.fans+' hayran</span><button class="btn" data-act="deliver" data-k="'+k+'" id="odb'+k+'">Teslim et</button></div></div>'}).join('');
 $('enemyLegend').innerHTML=Object.entries(ETYPES).map(([k,T])=>'<span><b>'+T.n+'</b> · '+T.d+'</span>').join('');
}
function updUI(){
 tutCheck();
 $('sNota').textContent='♪ '+fmt(S.nota);const mp=$('mPlay');if(mp){mp.textContent=$('play').textContent;$('mNota').textContent='♪ '+fmt(S.nota)}
 if(isPhone()&&tab==='stage'){const pe=$('pads');if(pe&&!pe.hidden){if(pe.querySelector('[data-act=spad]')){let cur=-1;if(playing&&soloNow===soloEdSlot){const pa=planAt(curBar);cur=(pa.barIn%2)*MI.N+Math.floor(phase*MI.N)}pe.querySelectorAll('.pad').forEach(e=>e.classList.toggle('cur',+e.dataset.t===cur))}else{const k=needleOf(eSel),cur=playing?Math.floor((k===2?phase2:k===3?phase3:phase)*MI.N)%MI.N:-1;pe.querySelectorAll('.pad').forEach(e=>e.classList.toggle('cur',+e.dataset.s===cur))}}}
 const r=rate();$('sRate').textContent=r.toLocaleString('tr-TR',{maximumFractionDigits:r<100?1:0});
 $('sMult').textContent='×'+(GC[S.edit]*globalM()).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2});
 $('sWave').textContent=S.wave+(enemies.length?' · '+enemies.length:'');
 const hpf=clamp(core.hp/hpMax(),0,1);$('sHp').textContent=Math.round(hpf*100)+'%'+(core.sh>0?' +'+Math.round(core.sh):'');$('stNabiz').classList.toggle('danger',hpf<0.35);
 $('sFans').textContent=fmt(S.hayran);
 INS.forEach(x=>{const b=$('lvb-'+x.id);if(!b)return;const q=lvQuote(x);b.textContent='+'+q.n+' · ♪ '+fmt(q.c);b.dataset.cost=q.c});
 document.querySelectorAll('[data-cost]').forEach(b=>b.classList.toggle('poor',S.nota<+b.dataset.cost));
 const p=S.pat[S.edit];COMBOS.forEach((k,j)=>{const e=$('cb'+j);if(e)e.classList.toggle('on',!!k.t(p))});
 const pe=$('cbP');if(pe)pe.classList.toggle('on',PEN.t(p));
 SYN.forEach(y=>{const e=$('sy'+y.id);if(e)e.classList.toggle('on',!!SYNON[S.edit][y.id])});
 {const pa=planAt(curBar);document.querySelectorAll('#planChips .chip').forEach((e,i)=>e.classList.toggle('on',i===pa.idx))}
 if(playing&&soloNow===soloEdSlot&&$('soloCv'))drawSoloEd();
 const th=albumTh(),pr=Math.min(1,S.runEarned/th),bar=$('aBar');
 if(bar){bar.style.width=(pr*100).toFixed(1)+'%';$('aTxt').textContent='♪ '+fmt(S.runEarned)+' / '+fmt(th)+' · +'+fansFor()+' hayran';$('aBtn').classList.toggle('ready',pr>=1)}
 if($('dWave')){$('dWave').textContent=S.wave;$('dEn').textContent=enemies.length;$('dDps').textContent=fmt(dps());$('dHp').textContent=Math.round(core.hp)+' / '+hpMax();$('dSh').textContent=Math.round(core.sh)+' / '+Math.round(shieldMax());$('dHpBar').style.width=(hpf*100).toFixed(1)+'%';$('dShBar').style.width=(clamp(core.sh/hpMax(),0,1)*100).toFixed(1)+'%'}
 S.orders.forEach((o,k)=>{if(!o.tpl){return}const t=OTPL.find(x=>x.id===o.tpl);if(!t)return;const rq=t.req(o);let all=true;rq.forEach((q,j)=>{const li=$('oq'+k+'_'+j);const ok=!!q.ok();if(!ok)all=false;if(li)li.classList.toggle('ok',ok)});const card=$('ord'+k),btn=$('odb'+k);if(card)card.classList.toggle('ok',all);if(btn)btn.classList.toggle('ready',all)});
 const nf=nextFam();if(nf&&famCanOpen(nf[0])&&tab!=='coll')$('collBadge').hidden=false;
 checkBook();
}
function checkBook(){
 const pats=[S.pat.A];if(bActive())pats.push(S.pat.B);let any=false;
 for(const e of BOOK){
  if(S.found[e.id]||e.m!==S.meter)continue;const want=e.s.join(',');let hitB=false;
  for(const p of pats){for(let i=0;i<S.slots.length&&!hitB;i++){if(STEPS(p,i).join(',')===want)hitB=true}if(hitB)break}
  if(hitB){S.found[e.id]=1;any=true;msg('Kalıp bulundu: '+e.n+' · keşif +%5 · çalınca: '+e.e);if(tab!=='book'){bookNew=true;$('bookBadge').hidden=false}}
 }
 if(any){recalc();renderPanels()}
}
/* ---------- tutorial: ten steps, most advance on the player's own action ---------- */
const TUT=[
 {t:'Hoş geldin',p:'Sessizlik A.Ş. şehri susturmaya geliyor; tek savunma senin döngün. Halkada boş bir hücreye dokun: vuruş ekle.',tab:'stage',cond:()=>placedCount()>=3},
 {t:'Başlat',p:'Başlat’a bas. İbre döndükçe her vuruş hem nota kazandırır hem de yaklaşan susturuculara ateş eder.',tab:'stage',hi:'play',cond:()=>playing},
 {t:'Kuşatma',p:'Düşmanlar kenardan merkeze yürür. Merkeze varırlarsa Nabız düşer; sıfırlanırsa dalga 5 geri gider. İlk susturucuyu düşür.',tab:'stage',cond:()=>S.kills>=1},
 {t:'Seviye',p:'Biriken notayla Stüdyo’dan Davul’u yükselt: her seviye değeri artırır, 10. ve 25. seviyede ikiye katlar.',tab:'studio',hi:'lvb-davul',cond:()=>lvOf('davul')>=2},
 {t:'Nefes',p:'Her enstrümanın ölçü başına bir nefesi var: Davul 4 vuruşa kadar tam güç, fazlası zayıflar. Her hücreyi doldurmak kazandırmaz; es bırak, yerine aksan koy.',tab:'studio',btn:'Anladım'},
 {t:'Koleksiyon',p:'Koleksiyon sekmesinden ikinci bir vurmalı aç (trampet ya da alkış). Alkış trampetin üstüne biner, hi-hat araları doldurur: uyumlar çarpan verir. Diğer aileler dalga ilerledikçe açılır.',tab:'coll',hi:'t-coll',cond:()=>INS.some(x=>x.id!=='davul'&&lvOf(x.id)>0)},
 {t:'İkinci halka',p:'Yeni enstrüman 2. yere kondu. Onun halkasına da en az iki vuruş ekle; birbirine cevap veren desenler Uyum kazandırır.',tab:'stage',cond:()=>!!S.slots[1]&&STEPS(S.pat.A,1).length>=2},
 {t:'Ritme vur',p:'İbre bir vuruşun üstündeyken Ritme vur’a (ya da boşluk tuşuna) bas: seri bonusu. Üç kez üst üste tuttur.',tab:'stage',hi:'tap',cond:()=>S.seri>=3,btn:'Geç'},
 {t:'Savunma',p:'Savunma sekmesinde Nabız, hasar ve menzil geliştirmeleri var; Siparişler ekstra ödül verir. Dalga ilerledikçe patronlar gelir.',tab:'def',hi:'t-def',btn:'Anladım'},
 {t:'Albüm',p:'Dönemde yeterince nota kazanınca Albüm çıkar: hayran kazanırsın, döngü sıfırlanır ama hayranlar kalıcı çarpan verir. Kitap kalıpları, temalar ve solo dalı seni bekliyor.',tab:'album',hi:'t-album',btn:'Bitir'}
];
let tutShown=-1,tutHiEl=null;
const tutActive=()=>!!(S.tut&&!S.tut.done&&!demoMode&&S.tut.s<TUT.length);
function tutHi(id){if(tutHiEl&&tutHiEl.id!==id){tutHiEl.classList.remove('tut-hi');tutHiEl=null}if(!id)return;const el=$(id);if(el&&!el.classList.contains('tut-hi')){el.classList.add('tut-hi');tutHiEl=el}}
/* the card lives in the page flow: above the ring on phones, at the top of the open panel on other tabs, under the stage controls on desktop */
function tutPlace(){const el=$('tut');if(!el||el.hidden)return;if(isPhone()){if(tab==='stage'){const cw=$('cvwrap');if(cw&&el.nextElementSibling!==cw)cw.before(el)}else{const host=$('p-'+tab);if(host&&host.firstElementChild!==el)host.prepend(el)}}else{const rk=$('rack');if(rk&&rk.firstElementChild!==el)rk.prepend(el)}}
function tutShow(){const el=$('tut');if(!el)return;if(!tutActive()){el.hidden=true;tutHi(null);return}const i=S.tut.s,st=TUT[i];el.hidden=false;$('tutN').textContent='Öğretici '+(i+1)+' / '+TUT.length;$('tutT').textContent=st.t;$('tutP').textContent=st.p;$('tutNext').hidden=!st.btn;$('tutNext').textContent=st.btn||'İleri';$('tutWait').hidden=!!st.btn;$('tutBar').hidden=!st.btn&&isPhone();
 if(tutShown!==i){tutShown=i;if(st.tab&&(st.tab!=='stage'||isPhone()))setTab(st.tab)}tutPlace();tutHi(st.hi||null)}
function tutAdvance(){if(!tutActive())return;S.tut.s++;if(S.tut.s>=TUT.length){S.tut.done=true;msg('Öğretici bitti. İyi çalışmalar!')}save();tutShow()}
function tutCheck(){if(!tutActive()){if(tutHiEl)tutHi(null);const el=$('tut');if(el&&!el.hidden)el.hidden=true;return}const st=TUT[S.tut.s];if(st.cond&&st.cond()){tutAdvance();return}tutHi(st.hi||null)}
let loadArm=false,loadT=0;
function applyLoaded(d){if(demoMode)exitDemo();S=Object.assign(freshRun(),freshMeta(),d);if(!d.tut)S.tut=null;normalizeS();MI=meterInfo();eSel=0;previewId=null;enemies=[];wave=null;core={hp:hpMax(),sh:0};if(playing)startWave(S.wave,nowT());recalc();renderPanels();applyTheme();syncFx();save();tutShown=-1;tutShow();msg('Kayıt yüklendi · dalga '+S.wave+' · '+S.albums.length+' albüm · '+Object.keys(S.lv).length+' enstrüman')}
const HINT_C='Hücreye dokun: vuruş ekle. Merkeze dokun ya da boşluk tuşuna bas: ritme vur.';
const HINT_S='Satırdaki hücreye dokun: vuruş ekle. Sahne alanına dokun ya da boşluk tuşuna bas: ritme vur.';
const hintSet=t=>{$('hint').textContent=T(t)};
function hintFor(h){
 const el=$('hint');if(!h){if(S.edit==='F'){hintSet('Dolgu: vurmalı halkalarının sağ yarısına vuruş koy; sol yarı ve melodikler dolguda çalmaz.');return}if(S.up.sdevir&&S.edit==='S'&&soloEdSlots().length){const x=slotIns(soloEdCur());hintSet('Solo sahnesi · '+(x?x.n:'')+': boş yere bas, nota'+(S.up.suzun?' · halka boyunca sürükle, uzat · bara değdir, birleşir':'')+' · başka halkaya sürükle, perde · merkez: ritme vur');return}hintSet(S.layout==='strip'?HINT_S:HINT_C);return}
 const x=slotIns(h.i);if(!x){hintSet('Yer '+(h.i+1)+' boş · Stüdyo sekmesinden enstrüman koy');return}
 const v=S.pat[S.edit][h.i][h.s];const soloTxt=isSolo(h.i)?' · solo ritmi':'';
 const rn=(RUN[S.edit][h.i]||[])[h.s]||0,nf=NF[S.edit][h.i]||1,sm=supM(S.edit,h.s);hintSet(x.n+soloTxt+' · adım '+(h.s+1)+' · '+(v===0?'ekle ♪ '+fmt(noteCost()):v===1&&S.up.accent?'aksan yap ♪ '+fmt(accCost()):'sil, ♪ '+fmt(Math.round(costAt(placedCount()-1)/2))+' geri')+' · nefes '+rowLoad(S.pat[S.edit],h.i)+'/'+nefesOf(h.i,S.edit)+(nf<1?' (güç ×'+fm(nf)+')':'')+(rn>1?' · '+rn+'. ardışık, alışkanlık ×'+fm(habF(rn)):'')+(sm>1?' · destek ×'+fm(sm):''));
}
function applyTheme(){
 const th=dispTheme(),r=document.documentElement;
 Object.entries(th.css).forEach(([k,v])=>r.style.setProperty('--'+k,v));
 r.style.setProperty('--f-d',th.font.d);r.style.setProperty('--f-b',th.font.b);r.style.setProperty('--f-m',th.font.m);
 r.style.colorScheme=th.light?'light':'dark';
 bgKey='';syncFx();renderPanels();
}
function soloAct(act,b){const so=S.solos[soloEdSlot]||(S.solos[soloEdSlot]={notes:[],style:'hendrix'}),x=slotIns(soloEdSlot);
 if(act==='soloGen'||act==='soloVar'){const st=$('soloStyle')?$('soloStyle').value:so.style;so.style=st;so.seed=act==='soloVar'&&so.seed?so.seed+1:(Date.now()%100000);so.notes=genSolo(soloEdSlot,st,so.seed);soloSel=-1;msg(SOLO_STYLES[st].n+' tarzı solo üretildi · '+so.notes.length+' nota')}
 else if(act==='soloClear'){so.notes=[];soloSel=-1;msg('Solo temizlendi')}
 else if(act==='soloArt'){const nt=so.notes[soloSel];if(nt){if(!artOk(x,b.dataset.k)){msg('Bu teknik için Solo dalında '+tkgOf(x)+' ailesinin teknik düğümü gerekir');return true}nt.art=b.dataset.k;if(!playing&&x){ensureAudio();soloPlay(x,ac.currentTime+0.01,{t:0,len:Math.min(noteLenEff(nt),6),r:nr(nt),art:nt.art},0.15,1)}}}
 else if(act==='soloLen'){const nt=so.notes[soloSel];if(nt){const T=soloSteps(),n0=so.notes.length;nt.len=clamp(nt.len+(+b.dataset.v),1,T-nt.t);soloSel=soloMerge(so,nt);if(so.notes.length<n0)msg('Barlar birleşti · '+nt.len+' adım')}}
 else if(act==='soloDel'){if(so.notes[soloSel]){so.notes.splice(soloSel,1);soloSel=-1}}
 else if(act==='soloRow'){soloRowSel=clamp(soloRowSel+(+b.dataset.v),0,soloRows()-1)}
 else if(act==='spad'){const t=+b.dataset.t;const j=so.notes.findIndex(n=>nr(n)===soloRowSel&&t>=n.t&&t<n.t+noteLenEff(n));if(j>=0){soloSel=j}else{if(so.notes.length>=SOLO_MAX){msg('En fazla '+SOLO_MAX+' solo notası');return true}so.notes.push({t,len:1,r:soloRowSel,art:'none'});so.notes.sort((a,c)=>a.t-c.t);soloSel=so.notes.findIndex(n=>n.t===t&&n.r===soloRowSel);if(!playing&&x){ensureAudio();soloVoice(x,ac.currentTime+0.01,soloRowSel,0.35,'none',1)}}}
 else return false;return true}
$('rack').addEventListener('click',e=>{
 const b=e.target.closest('[data-act]');if(!b||b.disabled)return;const act=b.dataset.act;
 const pay=c=>{if(S.nota<c){msg('Yeterli nota yok · ♪ '+fmt(c)+' gerekli');return false}S.nota-=c;return true};
 if(act==='tab'){setTab(b.dataset.tab);return}
 if(act==='buy'){S.buy=+b.dataset.v}
 else if(act==='lv'){const x=IDX[b.dataset.id];if(!x)return;const q=lvQuote(x);if(q.unlock){if(!famOpen(x.fam)){msg(FAM[x.fam].n+' ailesi kapalı: Koleksiyon sekmesindeki kapıya bak');return}if(pay(q.c)){S.lv[x.id]=1;const empty=S.slots.indexOf(null);if(empty>=0){S.slots[empty]=x.id;msg(x.n+' açıldı ve '+(empty+1)+'. yere kondu. Vuruş eklemeyi unutma.')}else msg(x.n+' açıldı, yedekte bekliyor. Bir yeri boşalt ya da yer ekle.')}}else if(pay(q.c)){const was=lvOf(x.id);S.lv[x.id]+=q.n;const ms=MS.find(m=>was<m&&S.lv[x.id]>=m);if(ms)msg(x.n+' '+ms+'. seviye · nota ve hasar ×2'+(ms===25?' · ses zenginleşti':''))}}
 else if(act==='openFam'){const f=b.dataset.f;if(!famCanOpen(f)){msg('Kapı için koşullar tamamlanmadı');return}const c=famCond(f).cost||0;if(c&&!pay(c))return;S.famOpen[f]=1;msg(FAM[f].n+' ailesi açıldı');save()}
 else if(act==='place'){const x=IDX[b.dataset.id],empty=S.slots.indexOf(null);if(x&&empty>=0){S.slots[empty]=x.id;msg(x.n+' '+(empty+1)+'. yere kondu')}}
 else if(act==='addslot'){if(S.slots.length<MAXSLOTS&&pay(slotCost())){S.slots.push(null);msg('Yeni sahne yeri açıldı: '+S.slots.length)}}
 else if(act==='solo'){const si=+b.dataset.i;if(!S.up.solo)return;if(S.solo[si])delete S.solo[si];else S.solo[si]=1;msg(S.solo[si]?(slotIns(si)||{n:'Yer'}).n+' soloya ayrıldı: solo bölümünde Solo desenini çalar. Şimdi “Solo deseni”ni seçip ritmini çiz.':(slotIns(si)||{n:'Yer'}).n+' artık solo almıyor')}
 else if(act==='needle'){const si=+b.dataset.i,k=+b.dataset.k;S.needle[si]=k;msg((slotIns(si)||{n:'Yer'}).n+' → '+NEEDLES[k-1].n+(k===2?' (¾ hız)':k===3?' (yarı hız, ters yön)':''))}
 else if(act==='preset'){S.plan=PLANS[b.dataset.v].slice();msg('Şarkı planı: '+PLAN_NAMES[b.dataset.v])}
 else if(act==='srup'){const u=TREE_IDX[b.dataset.id];if(u&&!S.up[u.id]){if(u.req&&!S.up[u.req]){msg('Önce '+(TREE_IDX[u.req]||{n:'Solo izni'}).n+' gerekir');return}if(pay(u.c)){S.up[u.id]=1;msg(u.n+' alındı'+(u.id==='sdevir'?' · Solo editöründe “Sahnede düzenle”ye bas':u.id==='suzun'?' · notayı halka boyunca sürükle':''));save()}}}
 else if(act==='soloStage'){S.edit='S';soloEdCur();soloSel=-1;hintFor(null);if(isPhone())setTab('stage');msg('Sahne solistin: boş yere bas, sürükle, perde için başka halkaya taşı')}
 else if(soloAct(act,b)){}
 else if(act==='clear'){clearRows(S.edit,null);return}
 else if(act==='clearBoth'){clearRows('A',null);clearRows('B',null);return}
 else if(act==='clearRow'){clearRows(S.edit,+b.dataset.i);return}
 else if(act==='ab'){S.edit=b.dataset.v;hintFor(null)}
 else if(act==='copy'){const rows={};for(let i=0;i<S.slots.length;i++)rows[i]=S.pat.A[i].slice();applyRows('B',rows,'A deseni B’ye kopyalandı');return}
 else if(act==='tempo'){if(S.bpm<180){if(S.bpm<S.bmax)S.bpm+=10;else if(pay(tempoCost())){S.bpm+=10;S.bmax=S.bpm}else return;syncFx();msg('Tempo '+S.bpm+' BPM')}}
 else if(act==='tempoDown'){if(S.bpm>70){S.bpm-=10;syncFx();msg('Tempo '+S.bpm+' BPM · geri çıkmak ücretsiz')}}
 else if(act==='rup'){const u=RUP.find(x=>x.id===b.dataset.id);if(u&&!S.up[u.id]&&pay(u.c)){S.up[u.id]=1;syncFx();msg(u.n+' alındı')}}
 else if(act==='def'){const u=DUP.find(x=>x.id===b.dataset.id);if(u&&!(u.max&&(S.def[u.id]||0)>=u.max)&&pay(defCost(u))){S.def[u.id]=(S.def[u.id]||0)+1;if(u.id==='nabiz')core.hp+=60;msg(u.n+' geliştirildi')}}
 else if(act==='stage'){const u=SUP.find(x=>x.id===b.dataset.id);if(u&&!S.stage[u.id]&&pay(u.c)){S.stage[u.id]=1;msg(u.n+' sahneye kuruldu: '+u.d)}}
 else if(act==='theme'){const id=b.dataset.id;if(themeOwned(id)){S.theme=id;previewId=null;applyTheme();msg(THEMES[id].n+' teması');save()}return}
 else if(act==='buyTheme'){const id=b.dataset.id,t=THEMES[id];if(t&&!themeOwned(id)&&pay(t.c)){S.themes[id]=1;S.theme=id;previewId=null;applyTheme();msg(t.n+' teması satın alındı');save()}return}
 else if(act==='preview'){previewId=b.dataset.id;previewUntil=performance.now()+20000;applyTheme();msg(THEMES[previewId].n+' önizlemesi · 20 saniye');return}
 else if(act==='layout'){if(b.dataset.v==='strip'&&!hasB())return;S.layout=b.dataset.v;bgKey='';hover=null;hintFor(null);msg(S.layout==='strip'?'Şerit düzeni: düşmanlar yukarıdan iner':'Çember düzeni: düşmanlar her yönden gelir');save()}
 else if(act==='fillGen'){const k=$('fillType')?$('fillType').value:'eighth';const tpl=FILLS[k];if(!tpl)return;const z0=Math.floor(MI.N/2),zl=MI.N-z0;const rows={};S.slots.forEach((id,si)=>{if(isFillRow(si))rows[si]=Array(18).fill(0)});if(!Object.keys(rows).length){msg('Sahnede vurmalı yok');return}
  const pick=part=>{for(const id of FILL_PARTS[part]){const si=S.slots.indexOf(id);if(si>=0)return si}return S.slots.findIndex((id,si)=>isFillRow(si))};
  tpl.h.forEach(([off,part,v])=>{const si=pick(part);if(si<0)return;const s=Math.min(MI.N-1,z0+Math.round(off*zl/8));rows[si][s]=Math.max(rows[si][s],v)});applyRows('F',rows,tpl.n+' dolgusu yerleştirildi');return}
 else if(act==='euclid'){applyRows(S.edit,eucRows(),(slotIns(eSel)||{n:'Yer'}).n+' yerine '+eK+' vuruş dağıtıldı');return}
 else if(act==='album'){if(demoMode){msg('Örnek şarkıdayken albüm çıkmaz. Önce kendi oyununa dön.');return}releaseAlbum();return}
 else if(act==='fxreset'){delete S.fxo[dispTheme().id];renderPanels();return}
 else if(act==='waveBack'){setWave(S.wave-5);msg('Dalga '+S.wave+' · geri çekilmek ücretsiz');return}
 else if(act==='waveFwd'){setWave(S.wave+5);msg('Dalga '+S.wave);return}
 else if(act==='deliver'){deliver(+b.dataset.k)}
 else if(act==='cheat'){const g=Math.max(1e4,rate()*600);earn(g);msg('Test: ♪ '+fmt(g)+' eklendi')}
 else if(act==='sfx'){S.sfx=b.dataset.v==='1';if(S.sfx&&ac)sfLoadStage();save();renderPanels();sfStatus();msg(S.sfx?'Örnek sesler açık: yüklendikçe gerçek enstrüman kayıtları çalar':'Örnek sesler kapalı: sentez');return}
 else if(act==='mnBuy'){const u=AUTO.find(x=>x.id===b.dataset.id);if(u&&!S.mn[u.id]&&albUnl()>=u.al&&pay(u.c)){S.mn[u.id]=1;if(S.auto[u.id]==null)S.auto[u.id]=u.id!=='alb';msg(u.n+' tutuldu');save()}}
 else if(act==='mnTog'){S.auto[b.dataset.id]=b.dataset.v==='1';save();renderMn();return}
 else if(act==='tour'){if(demoMode){msg('Önce kendi oyununa dön');return}if(!canTour()){msg('Turne için '+TOUR_AL+' albüm gerekir');return}if(!tourArm){tourArm=true;b.textContent='Emin misin? Albümler ve hayranlar sıfırlanır · tekrar bas';tourT=setTimeout(()=>{tourArm=false;b.textContent='Turneye çık'},4000);return}tourArm=false;clearTimeout(tourT);goTour();return}
 else if(act==='tutRestart'){S.tut={s:0,done:false};tutShown=-1;save();tutShow();msg('Öğretici başladı');return}
 else if(act==='saveCode'){const ta=$('saveCode');exportCode().then(code=>{ta.value=code;$('saveInfo').textContent=Math.round(code.length/1024*10)/10+' KB';const done=()=>msg('Kayıt kodu kopyalandı · başka cihazda Albüm → Kayıt → yapıştır → Koddan yükle');const fb=()=>{ta.focus();ta.select();msg('Kod üretildi · seçili metni kopyala')};if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(code).then(done,fb);else fb()});return}
 else if(act==='loadCode'){const code=($('saveCode').value||'').trim();if(!code){msg('Önce kayıt kodunu yapıştır');return}if(!loadArm){loadArm=true;b.textContent='Emin misin? Buradaki kayıt silinir · tekrar bas';loadT=setTimeout(()=>{loadArm=false;b.textContent='Koddan yükle'},4000);return}loadArm=false;clearTimeout(loadT);b.textContent='Koddan yükle';parseCode(code).then(d=>{applyLoaded(d)},err=>msg('Yüklenemedi: '+(err&&err.message||'kod okunamadı')));return}
 else if(act==='tutNext'||act==='tutSkip'){return}
 else if(act==='reset'){
  if(demoMode){msg('Önce kendi oyununa dön');return}
  if(resetArm){resetArm=false;clearTimeout(resetT);S=Object.assign(freshRun(),freshMeta());MI=meterInfo();eSel=0;previewId=null;enemies=[];wave=null;core={hp:hpMax(),sh:0};try{localStorage.removeItem(KEY)}catch(err){}b.textContent='Kaydı sıfırla';msg('Kayıt sıfırlandı');changed();applyTheme();return}
  resetArm=true;b.textContent='Emin misin? Tekrar bas';resetT=setTimeout(()=>{resetArm=false;b.textContent='Kaydı sıfırla'},3000);return
 }
 changed();
});
$('rack').addEventListener('change',e=>{
 const t=e.target;
 if(t.id==='selMeter'){S.meter=t.value;MI=meterInfo();step=step%MI.N;eRot=0;eK=Math.min(eK,MI.N);msg('Ölçü: '+METERS[S.meter].n);changed()}
 else if(t.id==='selScale'){S.scale=t.value;msg('Gam: '+SCALES[S.scale].n);changed()}
 else if(t.id==='soloSlotSel'){soloEdSlot=+t.value;soloSel=-1;renderSoloBox();return}
 else if(t.id==='soloStyle'){const so=S.solos[soloEdSlot]||(S.solos[soloEdSlot]={notes:[],style:'hendrix'});so.style=t.value;renderSoloBox();return}
 else if(t.dataset.plan!=null){const pl=planArr().slice();pl[+t.dataset.plan]=t.value;S.plan=pl;msg((+t.dataset.plan+1)+'. bölüm: '+SECTS[t.value].n);changed()}
 else if(t.dataset.prog!=null){S.prog[+t.dataset.prog]=t.value;msg((+t.dataset.prog+1)+'. bölüm: '+(PROGS[S.scale][t.value]||{n:t.value}).n);changed()}
 else if(t.id==='selRate'){S.prate=t.value;msg(t.value==='bar'?'Akor ölçü başına değişir':'Akor vuruş başına değişir');changed()}
 else if(t.dataset.slot!=null){const si=+t.dataset.slot,id=t.value||null;if(id&&S.slots.includes(id)&&S.slots[si]!==id){msg('Bu enstrüman zaten sahnede');renderPanels();return}S.slots[si]=id;changed()}
});
$('rack').addEventListener('input',e=>{
 const t=e.target;
 if(t.id==='sfVol'){S.sfv=+t.value;$('sfVolO').textContent='×'+fm(S.sfv);return}
 if(t.dataset.fx){const th=dispTheme();(S.fxo[th.id]=S.fxo[th.id]||{})[t.dataset.fx]=+t.value;$('fo-'+t.dataset.fx).textContent=fm(+t.value);return}
 if(t.id==='eRing'||t.id==='eK'||t.id==='eRot'){eSel=+$('eRing').value;eK=+$('eK').value;eRot=+$('eRot').value;$('eKv').textContent=eK;$('eRv').textContent=eRot;const btn=$('eApply');btn.textContent=eLabel();btn.dataset.cost=Math.max(0,planReplace(S.edit,eucRows()));eGhost=performance.now()+2600;updUI()}
});
let demoIdx=0;
function enterDemo(k){k=DEMOS[k]?k:0;if(demoMode){if(k===demoIdx)return;S=JSON.parse(demoSnap);demoMode=false}demoIdx=k;demoSnap=JSON.stringify(S);const keep={v:3,hayran:S.hayran,albums:S.albums,found:S.found,theme:S.theme,themes:S.themes,famOpen:S.famOpen,layout:S.layout,fxo:S.fxo,orders:S.orders,bestWave:S.bestWave,kills:S.kills,total:S.total,muted:S.muted,buy:S.buy,last:S.last,tut:S.tut,mn:S.mn,auto:S.auto,efsane:S.efsane,cities:S.cities,tours:S.tours,city:S.city,albMax:S.albMax,sfx:S.sfx,lang:S.lang};
 const D=JSON.parse(JSON.stringify(DEMOS[k]));S=Object.assign(freshRun(),keep,{slots:D.slots,lv:D.lv,bpm:D.bpm,bmax:D.bpm,meter:D.meter,scale:D.scale,solo:D.solo,needle:D.needle,plan:D.plan,up:D.up,stage:D.stage,nota:0,prog:D.prog||Array(8).fill('pop'),prate:D.prate||'beat'});
 ['A','B','S','F'].forEach(k=>{S.pat[k]=mkPat();Object.entries(D[k]||{}).forEach(([si,arr])=>arr.forEach(([s,v])=>S.pat[k][si][s]=v))});
 demoMode=true;MI=meterInfo();eSel=0;enemies=[];wave=null;core={hp:hpMax(),sh:0};soloSel=-1;soloEdSlot=-1;if(S.edit==='S')S.edit='A';
 /* solo notaları: elle yazılmışsa (D.solos) aynen, yoksa her solo yeri için stilden üretilir */
 S.solos={};Object.keys(D.solo||{}).forEach(si=>{const h=D.solos&&D.solos[si];const st=(h&&h.style)||D.soloStyle||'taksim';S.solos[si]=h&&Array.isArray(h.notes)?{notes:h.notes,style:st,seed:4242}:{notes:genSolo(+si,st,4242),style:st,seed:4242}});
 recalc();renderPanels();syncFx();if(!playing)startStop();else startWave(1,nowT());
 $('demo').textContent='Kendi oyununa dön';const d2=$('demo2');if(d2){d2.hidden=DEMOS.length<2;d2.textContent=T('Diğer örnek şarkı')+' · '+DEMOS[(k+1)%DEMOS.length].name}tutShow();msg('Örnek şarkı '+(k+1)+': '+D.name+' · '+D.msg);}
function exitDemo(){if(!demoMode)return;S=JSON.parse(demoSnap);demoMode=false;MI=meterInfo();eSel=0;enemies=[];wave=null;core={hp:hpMax(),sh:0};soloSel=-1;soloEdSlot=-1;recalc();renderPanels();syncFx();if(playing)startWave(S.wave,nowT());$('demo').textContent='Örnek şarkıyı dinle';const d2=$('demo2');if(d2)d2.hidden=true;tutShown=-1;tutShow();msg('Kendi oyununa döndün')}
$('demo').addEventListener('click',()=>{if(demoMode)exitDemo();else enterDemo(demoIdx);$('demo').blur()});
$('demo2').addEventListener('click',()=>{if(demoMode)enterDemo((demoIdx+1)%DEMOS.length);$('demo2').blur()});
$('play').addEventListener('click',()=>{startStop();$('play').blur()});
$('mPlay').addEventListener('click',()=>{startStop();updUI();$('mPlay').blur()});
$('langBtn').addEventListener('click',()=>{S.lang=S.lang==='en'?'tr':'en';save();location.reload()});
$('ledeBtn').addEventListener('click',()=>{const o=$('top').classList.toggle('open');$('ledeBtn').setAttribute('aria-expanded',String(o))});
$('pads').addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(!b||b.disabled)return;const act=b.dataset.act;if(act==='pad'){cellClick(eSel,+b.dataset.s);renderPads()}else if(act==='padPrev'){eSel=(eSel-1+S.slots.length)%S.slots.length;renderPads()}else if(act==='padNext'){eSel=(eSel+1)%S.slots.length;renderPads()}else if(soloAct(act,b)){recalc();updUI();renderSoloBox();renderPads()}});
$('mini').addEventListener('click',e=>{const b=e.target.closest('[data-act=tab]');if(b)setTab(b.dataset.tab)});
$('tut').addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(!b)return;if(b.dataset.act==='tutNext')tutAdvance();else if(b.dataset.act==='tutSkip'){S.tut.done=true;save();tutShow();msg('Öğretici kapatıldı · Albüm sekmesinden yeniden başlatabilirsin')}});
window.addEventListener('resize',()=>{if(!isPhone()&&tab==='stage')setTab('studio');renderPads();drawSoloEd()});
$('tap').addEventListener('click',()=>{tap();$('tap').blur()});
$('mute').addEventListener('click',()=>{S.muted=!S.muted;syncFx();$('mute').textContent=T(S.muted?'Ses kapalı':'Ses açık');msg(S.muted?'Ses kapalı, döngü yine de kazandırıyor ve savunuyor':'Ses açık')});
const isField=el=>el&&/^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName);
document.addEventListener('keydown',e=>{if(e.code==='Space'&&!isField(document.activeElement)){e.preventDefault();if(!e.repeat)tap()}});
document.addEventListener('keyup',e=>{if(e.code==='Space'&&!isField(document.activeElement))e.preventDefault()});

