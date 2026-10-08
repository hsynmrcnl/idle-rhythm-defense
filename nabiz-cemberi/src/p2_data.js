<script>
(()=>{
'use strict';
const $=id=>document.getElementById(id);
const TAU=Math.PI*2;
const RM=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const RGBC={};
function rgbOf(h){let v=RGBC[h];if(!v)v=RGBC[h]=[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)];return v}
const hexA=(h,a)=>{const v=rgbOf(h);return 'rgba('+v[0]+','+v[1]+','+v[2]+','+a+')'};
const SHC={};
function shade(hex,amt){const k=hex+amt;if(SHC[k])return SHC[k];const [r,g,b]=rgbOf(hex);const f=v=>clamp(Math.round(amt>0?v+(255-v)*amt:v*(1+amt)),0,255);return SHC[k]='#'+[f(r),f(g),f(b)].map(v=>v.toString(16).padStart(2,'0')).join('')}
function rng(seed){let a=seed>>>0;return()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296}}

/* ================= data ================= */
const FAMS=[['vur','Vurmalı',{}],['tel','Tel',{wave:5}],['tus','Tuş',{albums:1}],['nef','Nefesli',{wave:20,fans:10}],['ele','Elektronik',{albums:2,cost:1e8}],['dun','Dünya',{albums:3,fans:100,cost:1e11}]];
const FAM={};FAMS.forEach(([id,n,w])=>FAM[id]={id,n,w});
const ROLES={
 darbe:{n:'Darbe',d:'En yakına ağır vuruş, yanındakilere sıçrar'},
 keskin:{n:'Keskin',d:'En sağlam düşmanı hedefler, %20 kritik'},
 seri:{n:'Seri',d:'Rastgele düşmana hafif vuruş, zırha yarı işler'},
 alan:{n:'Alan',d:'Menzildeki herkese vurur'},
 delici:{n:'Delici',d:'Aynı hattaki tüm düşmanları deler'},
 yavas:{n:'Yavaşlatıcı',d:'Vurur ve yavaşlatır'},
 gudum:{n:'Güdümlü',d:'En hızlı düşmanı bulur'},
 kalkan:{n:'Kalkan',d:'Sahneye kalkan ekler, hasar vermez'},
 zincir:{n:'Zincir',d:'Bir düşmandan iki düşmana daha sıçrar'},
 statik:{n:'Statik',d:'Zamanla hasar, hafif yavaşlatma'},
 sarsici:{n:'Sarsıcı',d:'Vurur ve kısa süre durdurur'},
 kritik:{n:'Kritik',d:'%35 ihtimalle üç kat vurur'},
 titresim:{n:'Titreşim',d:'Ateş etmez; ses duvarını dışarı iter, çubuğa değen düşman hasar alır'},
 gelir:{n:'Gelir',d:'Ateş etmez; vuruş başı nota ×3'},
 destek:{n:'Destek',d:'Ateş etmez; aynı adımda vuran her silah ×1,5'}
};
const INS=[
{id:'davul',nf:4,n:'Davul',fam:'vur',b:1,dmg:2,role:'darbe',u:0,v:{g:'kick',f0:165,f1:44,dur:0.4,click:1},d:'Döngünün temeli'},
{id:'trampet',nf:2,n:'Trampet',fam:'vur',b:2,dmg:3,role:'keskin',u:150,v:{g:'noise',ft:'highpass',f:1400,a:0.42,dur:0.16,tone:210,gate:1},d:'Arka vuruş'},
{id:'shaker',nf:8,n:'Shaker',fam:'vur',b:1,dmg:0.4,role:'destek',u:400,v:{g:'noise',ft:'bandpass',f:6000,q:1.2,a:0.14,dur:0.06},d:'Kuru tıkırtı, aynı adımdaki silahları güçlendirir'},
{id:'hihat',nf:8,n:'Hi-hat',fam:'vur',b:1,dmg:0.6,role:'seri',u:800,v:{g:'noise',ft:'highpass',f:7600,a:0.15,dur:0.045,open:0.14},d:'Aralardaki tıs, aksanlı açık'},
{id:'clap',nf:2,n:'El çırpma',fam:'vur',b:2,dmg:1.2,role:'destek',u:5e3,v:{g:'clap'},d:'Trampete katman: aynı adımdaki silahları güçlendirir'},
{id:'kasik',nf:6,n:'Kaşık',fam:'vur',b:2,dmg:2,role:'kritik',u:2e4,v:{g:'noise',ft:'bandpass',f:2800,q:3,a:0.3,dur:0.04,tone:1400,toneDur:0.02},d:'Tahta şakırtı, sert kritik'},
{id:'tom',nf:4,n:'Tom',fam:'vur',b:3,dmg:4,role:'darbe',u:6e4,v:{g:'kick',f0:220,f1:95,dur:0.3,noise:1},d:'Dolgu davulu'},
{id:'darbuka',nf:6,n:'Darbuka',fam:'vur',b:3,dmg:2.5,role:'darbe',u:2e5,v:{g:'darb'},d:'Adıma göre düm ya da tek'},
{id:'bendir',nf:3,n:'Bendir',fam:'vur',b:3,dmg:3,role:'sarsici',u:8e5,v:{g:'kick',f0:120,f1:70,dur:0.5,noise:1,a:0.7},d:'Derin çerçeve davul, sarsar'},
{id:'zil',nf:1,n:'Zil',fam:'vur',b:3,dmg:1.5,role:'alan',u:3e6,v:{g:'metal',f:1,dur:0.9,a:0.12,hp:5000},d:'Crash: sahnedeki herkese'},
{id:'timbal',nf:2,n:'Timbal',fam:'vur',b:5,dmg:8,role:'titresim',u:2e7,v:{g:'tkick',pitch:'root',oct:-1,dur:0.9,a:0.9},d:'Akortlu orkestra davulu, ses duvarını iter'},
{id:'gong',nf:1,n:'Gong',fam:'vur',b:8,dmg:14,role:'titresim',u:3e8,v:{g:'metal',f:0.4,dur:2.5,a:0.2,hp:300},d:'Bir vuruş, uzun titreşim; duvarı en çok iten'},
{id:'bas',nf:4,n:'Bas',fam:'tel',b:3,dmg:3,role:'delici',u:2.5e4,v:{solo:'bass',g:'bass',pitch:'root'},d:'Akor yürüyüşünü izler, hattı deler'},
{id:'akustik',nf:4,n:'Akustik gitar',fam:'tel',b:5,dmg:0,role:'gelir',u:1.5e6,v:{g:'pluck2',pitch:'chord',strum:0.014,dur:1.9,a:0.24,bright:0.55,pick:0.22,lp:5500,body:[[108,2,0.9],[214,3,0.7],[425,4,0.45]],wet:0.42,course:[[1,1],[1.0015,0.5]],pickF:2800,pickA:0.1,solo:'tel'},d:'Tel çınlaması, akor tarar; nota kazandırır'},
{id:'gitar',nf:2,n:'Gitar',fam:'tel',b:4,dmg:5,role:'darbe',u:6e5,v:{solo:'edrive',g:'power',pitch:'root',oct:1},d:'Distorsiyonlu güç akoru'},
{id:'saz',nf:6,n:'Saz',fam:'tel',b:4,dmg:3.5,role:'zincir',u:2e6,v:{g:'saz',pitch:'arp',dur:1.1,a:0.22,solo:'saz'},d:'Bağlama tınısı, düşmandan düşmana sıçrar'},
{id:'keman',nf:4,n:'Keman',fam:'tel',b:5,dmg:5,role:'gudum',u:8e6,v:{g:'bow',pitch:'arp',dur:0.75,a:0.16,att:0.09,vib:5.6,lp:3400,body:[[280,2,0.9],[600,3,0.7],[1100,4,0.5],[2800,5,0.3]],solo:'bow'},d:'Yay ve vibrato, en hızlıyı bulur'},
{id:'cello',nf:2,n:'Çello',fam:'tel',b:6,dmg:10,role:'delici',u:1e8,v:{g:'bow',pitch:'root',dur:0.85,a:0.2,att:0.11,vib:4.8,lp:1800,body:[[100,2,1],[200,3,0.8],[400,4,0.5],[800,4,0.3]],solo:'bow'},d:'Kalın yay, hattı deler'},
{id:'harp',nf:6,n:'Arp',fam:'tel',b:7,dmg:4,role:'gelir',u:1.2e9,v:{g:'pluck2',pitch:'high',dur:2.6,a:0.2,bright:0.3,pick:0.35,lp:6000,body:[[160,2,0.6],[300,3,0.5]],wet:0.3,course:[[1,1],[1.002,0.5]],pickF:2200,pickA:0.05,solo:'tel'},d:'Her glisando nota, ateş etmez'},
{id:'akor',nf:2,n:'Akor',fam:'tus',b:4,dmg:2.5,role:'yavas',u:5e5,v:{solo:'lead',g:'pad',dur:0.35,lp0:2400,lp1:500,a:0.05},d:'Synth pad, yavaşlatır'},
{id:'rhodes',nf:4,n:'Rhodes',fam:'tus',b:5,dmg:4,role:'gelir',u:1.5e7,v:{solo:'keys',g:'fm',pitch:'chord',chord:1,ratio:1,index:0.8,dur:0.9,a:0.05},d:'Sıcak elektrikli piyano, nota kazandırır'},
{id:'piyano',nf:4,n:'Piyano',fam:'tus',b:6,dmg:9,role:'keskin',u:6e7,v:{solo:'keys',g:'fm',pitch:'chord',chord:1,ratio:2,index:2,dur:0.7,a:0.06},d:'Sert tuşe, en sağlamı hedefler'},
{id:'org',nf:2,n:'Org',fam:'tus',b:7,dmg:5,role:'kalkan',u:4e8,v:{solo:'keys',g:'organ',dur:0.4,a:0.04},d:'Çekilen registerler, kalkan'},
{id:'klavsen',nf:6,n:'Klavsen',fam:'tus',b:8,dmg:12,role:'kritik',u:3e9,v:{solo:'keys',g:'pluck',pitch:'arp',oct:1,type:'square',lp0:5000,lp1:1500,dur:0.2,a:0.1,det:[0]},d:'Barok çıtırtı, kritik'},
{id:'ney',nf:4,n:'Ney',fam:'nef',b:4,dmg:3,role:'gudum',u:1e6,v:{solo:'wind',g:'flute',pitch:'arp',breath:0.08,att:0.05,dur:0.45,a:0.18},d:'Nefesli, hüzünlü, güdümlü'},
{id:'flut',nf:6,n:'Flüt',fam:'nef',b:5,dmg:4,role:'gudum',u:1.2e7,v:{solo:'wind',g:'flute',pitch:'high',breath:0.04,att:0.02,dur:0.35,a:0.16},d:'Tiz ve çevik'},
{id:'trompet',nf:3,n:'Trompet',fam:'nef',b:6,dmg:11,role:'keskin',u:1e8,v:{solo:'brass',g:'brass',pitch:'arp',dur:0.3,a:0.14,lp:3200},d:'Parlak patlama'},
{id:'sakso',nf:4,n:'Saksafon',fam:'nef',b:7,dmg:7,role:'zincir',u:7e8,v:{solo:'brass',g:'brass',pitch:'arp',oct:-1,dur:0.4,a:0.14,lp:2200,growl:1},d:'Hırıltılı, sıçrar'},
{id:'tuba',nf:2,n:'Tuba',fam:'nef',b:9,dmg:22,role:'titresim',u:5e9,v:{solo:'brass',g:'brass',pitch:'root',oct:-1,dur:0.5,a:0.22,lp:900},d:'Ağır bakır, ses duvarını iter'},
{id:'zurna',nf:4,n:'Zurna',fam:'nef',b:10,dmg:10,role:'alan',u:2e10,v:{solo:'brass',g:'brass',pitch:'high',dur:0.35,a:0.12,lp:4200,nasal:1},d:'Düğün sesi, herkese'},
{id:'melodi',nf:6,n:'Lead',fam:'ele',b:5,dmg:4,role:'gudum',u:2.5e6,v:{solo:'lead',g:'lead',pitch:'arp',type:'triangle',dur:0.32,a:0.22},d:'Synth lead, en hızlıyı bulur'},
{id:'sub808',nf:2,n:'808',fam:'ele',b:6,dmg:12,role:'titresim',u:5e7,v:{solo:'bass',g:'tkick',pitch:'root',oct:-1,dur:0.7,a:0.9,sub:1},d:'Uzun sub bas, ses duvarını iter'},
{id:'arpej',nf:8,n:'Arpej',fam:'ele',b:7,dmg:5,role:'zincir',u:3e8,v:{solo:'lead',g:'pluck',pitch:'arp',oct:1,type:'sawtooth',lp0:4200,lp1:900,q:8,dur:0.2,a:0.12,det:[0]},d:'Arpejiyatör, sıçrar'},
{id:'theremin',nf:3,n:'Theremin',fam:'ele',b:9,dmg:8,role:'statik',u:4e9,v:{solo:'lead',g:'lead',pitch:'high',type:'sine',att:0.06,dur:0.7,vib:7,a:0.16,gliss:1},d:'Dokunmadan çalınır, statik bırakır'},
{id:'gurultu',nf:1,n:'Gürültü',fam:'ele',b:11,dmg:16,role:'alan',u:3e10,v:{g:'riser'},d:'Beyaz gürültü yükselişi'},
{id:'vocoder',nf:2,n:'Vocoder',fam:'ele',b:12,dmg:10,role:'destek',u:2e11,v:{solo:'lead',g:'vox'},d:'Robot koro, aynı adımdaki silahları güçlendirir'},
{id:'kalimba',nf:8,n:'Kalimba',fam:'dun',b:8,dmg:5,role:'gelir',u:1e9,v:{solo:'keys',g:'fm',pitch:'high',ratio:5,index:0.6,dur:0.5,a:0.14},d:'Başparmak piyanosu, nota kazandırır'},
{id:'steel',nf:6,n:'Steel drum',fam:'dun',b:10,dmg:9,role:'gelir',u:1e10,v:{solo:'keys',g:'fm',pitch:'arp',oct:1,ratio:2.5,index:1.4,dur:0.5,a:0.12},d:'Karayip çeliği, nota kazandırır'},
{id:'tabla',nf:8,n:'Tabla',fam:'dun',b:11,dmg:7,role:'kritik',u:8e10,v:{g:'tabla'},d:'Na ve ge, kritik'},
{id:'didger',nf:1,n:'Didgeridoo',fam:'dun',b:13,dmg:20,role:'titresim',u:5e11,v:{solo:'bass',g:'drone',pitch:'root',oct:-1,dur:0.9,a:0.2},d:'Dairesel nefes, duvarı sürekli iter'},
{id:'taiko',nf:2,n:'Taiko',fam:'dun',b:15,dmg:45,role:'titresim',u:4e12,v:{g:'kick',f0:95,f1:40,dur:0.8,a:1,noise:1,big:1},d:'Devasa davul, duvarı fırlatır'},
{id:'gamelan',nf:4,n:'Gamelan',fam:'dun',b:18,dmg:25,role:'alan',u:3e13,v:{solo:'keys',g:'fm',pitch:'arp',ratio:1.4,index:2.2,dur:1.2,a:0.1},d:'Bronz metalofon, herkese'}
];
const IDX={};const famCounter={};
INS.forEach((x,i)=>{x.i=i;x.lb=Math.max(12,x.u);x.fi=famCounter[x.fam]=(famCounter[x.fam]||0)+1;IDX[x.id]=x});
const GROW=1.19,MS=[25,50,100,200,300,400,500],MAXSLOTS=10;
const SHADES=[0,0.18,-0.2,0.36,-0.36,0.09,-0.1,0.27,-0.28,0.45,-0.45,0.14];

const THEMES={
 neon:{id:'neon',c:0,n:'Neon',al:0,bpm:[90,130],light:false,ring:'neon',needle:'neon',core:'neon',part:'spark',
  css:{bg:'#07060f',panel:'#0e0c1c',panel2:'#151229',line:'#272148',fg:'#ece9ff',muted:'#948dbd',dim:'#5d5788',acc:'#3ff2d2',onacc:'#03201b',hot:'#ff3fb4'},
  font:{d:'"Unbounded","Arial Black",sans-serif',b:'"Instrument Sans",system-ui,sans-serif',m:'"JetBrains Mono",ui-monospace,monospace'},
  cv:{bg:'#07060f',ink:'#ece9ff',dim:'#5d5788',acc:'#3ff2d2',hot:'#ff3fb4',core:'#0b0a17',warn:'#ffb054'},
  fam:{vur:'#ff3fb4',tel:'#8b6bff',tus:'#5a9bff',nef:'#3ff2d2',ele:'#8ff3ff',dun:'#ffb054'},
  en:{body:'#9aa0c8',edge:'#ffffff',boss:'#ff5370',style:'glow'},
  kit:{drive:0,crush:0,lp:20000,gate:0,crackle:0},
  fx:{bloom:.8,ca:.15,scan:0,crt:0,glitch:0,grain:.05,half:0,mis:0,vign:.45,trail:.5,dust:0,warm:0,sat:1.05,kaleid:0,shake:.15},
  blurb:'Mor gece, parlak halkalar, dönen ince ibre.'},
 cyber:{id:'cyber',c:2e+06,n:'Siberpunk',al:1,bpm:[120,150],light:false,ring:'hud',needle:'laser',core:'hud',part:'line',
  css:{bg:'#03030f',panel:'#0a0b1e',panel2:'#11142c',line:'#1d2850',fg:'#d1f7ff',muted:'#7d95c0',dim:'#46557d',acc:'#fcee0a',onacc:'#1a1700',hot:'#ff2a6d'},
  font:{d:'"Chakra Petch","Arial Narrow",sans-serif',b:'"Chakra Petch",system-ui,sans-serif',m:'"JetBrains Mono",ui-monospace,monospace'},
  cv:{bg:'#03030f',ink:'#d1f7ff',dim:'#2b3a66',acc:'#05d9e8',hot:'#ff2a6d',core:'#060716',warn:'#fcee0a'},
  fam:{vur:'#ff2a6d',tel:'#8f6bff',tus:'#05d9e8',nef:'#00ff9f',ele:'#fcee0a',dun:'#ff9f1c'},
  en:{body:'#ff2a6d',edge:'#ffffff',boss:'#fcee0a',style:'hud'},
  kit:{drive:8,crush:1,lp:20000,gate:0,crackle:0},
  fx:{bloom:1.05,ca:.6,scan:.4,crt:.16,glitch:.45,grain:.08,half:0,mis:0,vign:.55,trail:.3,dust:0,warm:-.25,sat:1.2,kaleid:0,shake:.3},
  blurb:'HUD radarı, lazer ibre, glitch ve tarama çizgileri.'},
 punk:{id:'punk',c:2e+07,n:'Punk',al:2,bpm:[150,180],light:true,ring:'spray',needle:'marker',core:'paper',part:'splat',
  css:{bg:'#ece6d6',panel:'#f6f2e6',panel2:'#e3dbc7',line:'#1a1a1a',fg:'#111111',muted:'#47433b',dim:'#8b8574',acc:'#ff2e88',onacc:'#ffffff',hot:'#2b59ff'},
  font:{d:'"Rubik Dirt","Impact",sans-serif',b:'"Courier Prime","Courier New",monospace',m:'"Courier Prime","Courier New",monospace'},
  cv:{bg:'#ece6d6',ink:'#111111',dim:'#8b8574',acc:'#ff2e88',hot:'#2b59ff',core:'#f6f2e6',warn:'#ff2e88'},
  fam:{vur:'#111111',tel:'#2b59ff',tus:'#ff2e88',nef:'#111111',ele:'#2b59ff',dun:'#ff2e88'},
  en:{body:'#111111',edge:'#ff2e88',boss:'#2b59ff',style:'spray'},
  kit:{drive:40,crush:0,lp:9000,gate:0,crackle:0},
  fx:{bloom:0,ca:0,scan:0,crt:0,glitch:.15,grain:.3,half:.8,mis:.6,vign:.15,trail:0,dust:.25,warm:0,sat:1,kaleid:0,shake:.4},
  blurb:'Fotokopi, sprey boya, halftone ve kaymış baskı.'},
 lofi:{id:'lofi',c:2e+08,n:'Lo-fi',al:3,bpm:[70,95],light:false,ring:'vinyl',needle:'tonearm',core:'label',part:'dust',
  css:{bg:'#1b1512',panel:'#241c17',panel2:'#2e241e',line:'#4a3a2e',fg:'#f3e3c9',muted:'#b39d80',dim:'#7d6a55',acc:'#f4a259',onacc:'#2a1608',hot:'#e76f51'},
  font:{d:'"Fraunces",Georgia,serif',b:'"Instrument Sans",system-ui,sans-serif',m:'"JetBrains Mono",ui-monospace,monospace'},
  cv:{bg:'#1b1512',ink:'#f3e3c9',dim:'#5d4a3b',acc:'#f4a259',hot:'#e76f51',core:'#e76f51',warn:'#e9c46a'},
  fam:{vur:'#e76f51',tel:'#2a9d8f',tus:'#e9c46a',nef:'#a3b18a',ele:'#cdb4db',dun:'#d4a373'},
  en:{body:'#8a8f98',edge:'#f3e3c9',boss:'#e76f51',style:'soft'},
  kit:{drive:0,crush:0,lp:6000,gate:0,crackle:1},
  fx:{bloom:.45,ca:.06,scan:0,crt:0,glitch:0,grain:.22,half:0,mis:0,vign:.7,trail:.25,dust:.6,warm:.4,sat:.85,kaleid:0,shake:0},
  blurb:'Dönen plak, pikap kolu, toz ve sıcak ışık.'},
 synth:{id:'synth',c:2e+09,n:'Synthwave',al:4,bpm:[100,125],light:false,ring:'neon',needle:'neon',core:'sun',part:'spark',
  css:{bg:'#120a2a',panel:'#1a0f3d',panel2:'#241552',line:'#3b2a6e',fg:'#ffe9f7',muted:'#b79ad6',dim:'#6d55a0',acc:'#ff6ec7',onacc:'#2b0a1f',hot:'#00e5ff'},
  font:{d:'"Monoton","Arial Black",sans-serif',b:'"Instrument Sans",system-ui,sans-serif',m:'"JetBrains Mono",ui-monospace,monospace'},
  cv:{bg:'#120a2a',ink:'#ffe9f7',dim:'#3b2a6e',acc:'#ff6ec7',hot:'#00e5ff',core:'#1a0f3d',warn:'#ffd166'},
  fam:{vur:'#ff6ec7',tel:'#7b61ff',tus:'#00e5ff',nef:'#ffd166',ele:'#ff8c42',dun:'#b388ff'},
  en:{body:'#ffffff',edge:'#ff6ec7',boss:'#00e5ff',style:'wire'},
  kit:{drive:4,crush:0,lp:20000,gate:1,crackle:0},
  fx:{bloom:.95,ca:.25,scan:.25,crt:.1,glitch:.05,grain:.06,half:0,mis:0,vign:.5,trail:.45,dust:0,warm:0,sat:1.3,kaleid:0,shake:.2},
  blurb:'Çizgili güneş, ufuk ızgarası, krom parıltı.'},
 anadolu:{id:'anadolu',c:2e+10,n:'Anadolu psikedelik',al:5,bpm:[85,115],light:false,ring:'kilim',needle:'neon',core:'eye',part:'spark',
  css:{bg:'#1d0f0a',panel:'#2a160e',panel2:'#3a1f12',line:'#5a3320',fg:'#ffe8c8',muted:'#d9a66f',dim:'#8c5a3a',acc:'#ffb703',onacc:'#2b1600',hot:'#06d6a0'},
  font:{d:'"Righteous","Arial Rounded MT Bold",sans-serif',b:'"Instrument Sans",system-ui,sans-serif',m:'"JetBrains Mono",ui-monospace,monospace'},
  cv:{bg:'#1d0f0a',ink:'#ffe8c8',dim:'#5a3320',acc:'#ffb703',hot:'#06d6a0',core:'#3a1f12',warn:'#ef476f'},
  fam:{vur:'#ef476f',tel:'#ffb703',tus:'#06d6a0',nef:'#fb8500',ele:'#8338ec',dun:'#ffd166'},
  en:{body:'#8338ec',edge:'#ffe8c8',boss:'#ef476f',style:'eye'},
  kit:{drive:10,crush:0,lp:12000,gate:0,crackle:0},
  fx:{bloom:.6,ca:.1,scan:0,crt:0,glitch:0,grain:.14,half:0,mis:0,vign:.6,trail:.3,dust:0,warm:.45,sat:1.3,kaleid:.35,shake:.1},
  blurb:'Kilim desenli halkalar, nazar çekirdeği, kaleydoskop.'}
};
const THEME_ORDER=['neon','cyber','punk','lofi','synth','anadolu'];
const FXK=[
 ['bloom','Bloom','Parlak alanlar ışık saçar',0,1.6],
 ['ca','RGB kayması','Renk kanalları kenara doğru ayrılır',0,1.5],
 ['scan','Tarama çizgisi','Eski monitör satırları',0,1],
 ['crt','CRT bükülmesi','Tüplü ekran kavisi',0,.5],
 ['glitch','Glitch','Vuruşlarda yatay dilim kayması',0,1],
 ['grain','Gren','Film ya da kâğıt dokusu',0,.6],
 ['half','Halftone','Fotokopi noktaları ve mürekkep',0,1],
 ['mis','Baskı kayması','Renkli katman siyah baskıdan kayar',0,1.5],
 ['vign','Vinyet','Kenarlar kararır',0,1],
 ['trail','İz','Hareket eden şeyler iz bırakır',0,.95],
 ['dust','Toz ve çizik','Plak tozu, film çiziği',0,1],
 ['warm','Sıcaklık','Soğuk maviden sıcak turuncuya',-.6,.8],
 ['sat','Doygunluk','Renklerin canlılığı',0,1.6],
 ['kaleid','Kaleydoskop','Görüntü dilimlere aynalanır',0,1],
 ['shake','Sarsıntı','Davulda ekran titrer',0,1]
];
const METERS={
 m44:{n:'4/4',g:[4,4,4,4],al:0},
 m98:{n:'9/8 aksak · 2+2+2+3',g:[4,4,4,6],al:2,bon:1.3},
 m78:{n:'7/8 · 3+2+2',g:[6,4,4],al:4,bon:1.3},
 m58:{n:'5/8 · 2+3',g:[4,6],al:4,bon:1.3}
};
const SCALES={
 minor:{n:'Minör · Am F C G',al:0,ch:[[220,261.63,329.63],[174.61,220,261.63],[261.63,329.63,392],[196,246.94,293.66]],root:[110,87.31,130.81,98]},
 major:{n:'Majör · C G Am F',al:0,ch:[[261.63,329.63,392],[196,246.94,293.66],[220,261.63,329.63],[174.61,220,261.63]],root:[130.81,98,110,87.31]},
 hicaz:{n:'Hicaz · A B♭ Gm A',al:3,bon:1.2,ch:[[220,277.18,329.63],[233.08,293.66,349.23],[196,233.08,293.66],[220,277.18,329.63]],root:[110,116.54,98,110]},
 kurdi:{n:'Kürdi · Am B♭ Gm Am',al:5,bon:1.25,ch:[[220,261.63,329.63],[233.08,293.66,349.23],[196,233.08,293.66],[220,261.63,329.63]],root:[110,116.54,98,110]}
};
const RUP=[
 {id:'swing',n:'Swing',d:'Ara vuruşlar geriden gelir · gelir ×1,15',c:5e3},
 {id:'accent',n:'Aksan',d:'Dolu hücreye ikinci dokunuş: nota ve hasar iki katı',c:2e4},
 {id:'euclid',n:'Öklid üretici',d:'Vuruşları bir sahne yerine eşit aralıkla dağıtır',c:5e4},
 {id:'echo',n:'Eko pedalı',d:'Tel, tuş ve nefeslilere yankı · ×1,15',c:3e5},
 {id:'assist',n:'Metronom asistanı',d:'Sen bakmazken de seri en az 6 kalır',c:1e6},
 {id:'side',n:'Sidechain pompası',d:'Her davulda müzik nefes alır · ×1,15',c:3e6},
 {id:'fill',n:'Dolgu',d:'Her dördüncü ölçünün sonu vurgulu · hasar ×1,1',c:5e7},
 {id:'filter',n:'Filtre süpürmesi',d:'Ses yavaşça açılıp kapanır · ×1,15',c:2e8},
 {id:'akor',n:'Akor yürüyüşü',d:'Şarkı planında her bölüme akor yürüyüşü ve akor hızı seçilir. Akor izleyen enstrümanlar ona uyar; zıtlık, kadans ve makam sadakati bonus verir',c:3e5},
 {id:'dolgu',n:'Dolgu',d:'Desen anahtarına Dolgu eklenir: her bölümün son ölçüsünün son yarısında vurmalılar dolgu desenini çalar, oyun zil ile çözer; geçiş düşmanı sarsar ve sonraki ölçüyü güçlendirir',c:3e5},
 {id:'solo',n:'Solo izni',d:'Sahne yerlerini soloya ayırabilirsin: solo yeri döngüde normal çalar, solo bölümünde kendi solo desenini ×3 güçle çalar. Solo dalının ilk düğümü.',c:2e4},
 {id:'needle2',n:'İkinci ibre',d:'Seçtiğin yerleri ¾ hızda ayrı bir ibre çalar: 4’e karşı 3, dört ölçüde bir buluşurlar',c:3e6},
 {id:'needle3',n:'Üçüncü ibre',d:'Seçtiğin yerleri yarı hızda ve ters yönde çalan üçüncü ibre: desen geriye doğru okunur',c:3e8},
 {id:'sef',n:'Şef',d:'Şarkı planı: 8 bölüm × 4 ölçü. Giriş, kıta, nakarat, köprü, yükseliş, düşüş, solo, çıkış; sen dizersin',c:1e5}
];
const SECTS={
 intro:{n:'Giriş',mask:'rhythm',pk:'A',dyn:0.8,regen:4,d:'Yalnız ritim grubu; nabız 4 kat hızlı yenilenir'},
 verse:{n:'Kıta',mask:'all',pk:'A',dyn:1,d:'Herkes çalar, desen A'},
 chorus:{n:'Nakarat',mask:'all',pk:'B',dyn:1.2,d:'Herkes çalar, desen B, güç ×1,2'},
 bridge:{n:'Köprü',mask:'melodic',pk:'A',dyn:0.9,slow:0.2,d:'Yalnız melodikler; düşmanlar %20 yavaş'},
 build:{n:'Yükseliş',mask:'all',pk:'A',dyn:1,ramp:0.15,d:'Tempo 4 ölçüde %15 hızlanır, güç yükselir'},
 drop:{n:'Düşüş',mask:'all',pk:'B',dyn:1.3,d:'Tempo yerine oturur, desen B, güç ×1,3'},
 solo:{n:'Solo',mask:'all',pk:'A',dyn:1,solo:1,d:'Solo yerleri sırayla çalar (güç ×3)'},
 outro:{n:'Çıkış',mask:'rhythm',pk:'A',dyn:0.8,regen:4,d:'Yalnız ritim grubu; nabız 4 kat hızlı yenilenir'}
};
const SECT_ORDER=['intro','verse','chorus','bridge','build','drop','solo','outro'];
/* chord progressions per scale: [semitone from tonic, quality]; quality M major, m minor, 5 open fifth (drone) */
const QUAL={M:[0,4,7],m:[0,3,7],5:[0,7,12]};
const PROGS={
 minor:{root:{n:'Tek kök',c:[[0,'m'],[0,'m'],[0,'m'],[0,'m']]},pop:{n:'i–VI–III–VII · Am F C G',c:[[0,'m'],[8,'M'],[3,'M'],[10,'M']]},klasik:{n:'i–iv–v–i · Am Dm Em Am',c:[[0,'m'],[5,'m'],[7,'m'],[0,'m']]},blues:{n:'i–iv–i–v · Am Dm Am Em',c:[[0,'m'],[5,'m'],[0,'m'],[7,'m']]},endulus:{n:'i–VII–VI–V · Am G F E',c:[[0,'m'],[10,'M'],[8,'M'],[7,'M']]},kadans:{n:'i–VI–iv–V · Am F Dm E',c:[[0,'m'],[8,'M'],[5,'m'],[7,'M']]}},
 major:{root:{n:'Tek kök',c:[[0,'M'],[0,'M'],[0,'M'],[0,'M']]},pop:{n:'I–V–vi–IV · C G Am F',c:[[0,'M'],[7,'M'],[9,'m'],[5,'M']]},klasik:{n:'I–IV–V–I · C F G C',c:[[0,'M'],[5,'M'],[7,'M'],[0,'M']]},blues:{n:'I–IV–I–V · C F C G',c:[[0,'M'],[5,'M'],[0,'M'],[7,'M']]},endulus:{n:'vi–V–IV–III · Am G F E',c:[[9,'m'],[7,'M'],[5,'M'],[4,'M']]},kadans:{n:'I–vi–IV–V · C Am F G',c:[[0,'M'],[9,'m'],[5,'M'],[7,'M']]}},
 hicaz:{root:{n:'Durak (dem)',c:[[0,'5'],[0,'5'],[0,'5'],[0,'5']]},makam:{n:'Durak–Güçlü · A5 E5 A5 A5',c:[[0,'5'],[7,'5'],[0,'5'],[0,'5']]},pop:{n:'A B♭ Gm A',c:[[0,'M'],[1,'M'],[10,'m'],[0,'M']]},klasik:{n:'A Dm E A',c:[[0,'M'],[5,'m'],[7,'M'],[0,'M']]},kadans:{n:'A B♭ Dm E',c:[[0,'M'],[1,'M'],[5,'m'],[7,'M']]}},
 kurdi:{root:{n:'Durak (dem)',c:[[0,'5'],[0,'5'],[0,'5'],[0,'5']]},makam:{n:'Durak–Güçlü · A5 D5 A5 A5',c:[[0,'5'],[5,'5'],[0,'5'],[0,'5']]},pop:{n:'Am B♭ Gm Am',c:[[0,'m'],[1,'M'],[10,'m'],[0,'m']]},endulus:{n:'Am G F E',c:[[0,'m'],[10,'M'],[8,'M'],[7,'M']]},klasik:{n:'Am Dm Em Am',c:[[0,'m'],[5,'m'],[7,'m'],[0,'m']]}}
};
const NOTE_N=['A','B♭','B','C','C#','D','E♭','E','F','F#','G','G#'];
/* drum fill templates: [offset within the fill zone (0..7 of an 8-step zone), part]; parts map to the player's percussion */
const FILLS={one:{n:'Tek vuruş',h:[[4,'snare',2]]},eighth:{n:'Sekizlik yükseliş',h:[[0,'snare',1],[2,'snare',1],[4,'tomH',1],[6,'tomL',2]]},run:{n:'On altılık koşu',h:[[0,'snare',1],[1,'snare',1],[2,'snare',1],[3,'snare',1],[4,'tomH',1],[5,'tomH',1],[6,'tomL',1],[7,'tomL',2]]},trip:{n:'Üçleme',h:[[0,'snare',1],[1,'tomH',1],[3,'tomL',1],[4,'snare',1],[5,'tomH',1],[7,'tomL',2]]},flam:{n:'Flam',h:[[0,'snare',2],[2,'snare',2],[4,'snare',2],[6,'snare',2],[7,'tomL',2]]}};
const FILL_PARTS={snare:['trampet','clap','kasik','darbuka','bendir','davul'],tomH:['tom','darbuka','bendir','timbal','davul','trampet'],tomL:['bendir','tom','timbal','davul','darbuka','trampet']};
const PLANS={pop:['intro','verse','chorus','verse','chorus','bridge','chorus','outro'],club:['intro','build','drop','verse','build','drop','solo','outro'],gece:['verse','solo','chorus','solo','bridge','build','drop','solo'],loop:['verse','chorus','verse','chorus','verse','chorus','verse','chorus']};
const PLAN_NAMES={pop:'Pop',club:'Kulüp',gece:'Solo gecesi',loop:'Döngü'};
const SEC_BARS=4;
const SOLO_SCALE={minor:[0,3,5,6,7,10],major:[0,2,4,7,9,10],hicaz:[0,1,4,5,7,8,10],kurdi:[0,1,3,5,7,8,10]};
const SOLO_ART={none:{n:'Düz',g:'·'},bend:{n:'Bend',g:'↗'},vib:{n:'Vibrato',g:'~'},slide:{n:'Slide',g:'/'},fb:{n:'Feedback',g:'∞'},slap:{n:'Slap',g:'!'},pop:{n:'Pop',g:'^'},trem:{n:'Tremolo',g:'≋'},growl:{n:'Growl',g:'≈'},arp:{n:'Arpej',g:'⋰'}};
/* sustain gene: how a held note loses power, by solo flavor; per-instrument overrides */
const SUSP={tel:{k:'decay',d:0.75},saz:{k:'decay',d:0.68},edrive:{k:'decay',d:0.8},bass:{k:'decay',d:0.8},bow:{k:'hold'},wind:{k:'breath',max:12},brass:{k:'breath',max:8},keys:{k:'decay',d:0.78},lead:{k:'hold'}};
const SUS_OVR={harp:{k:'decay',d:0.8},klavsen:{k:'decay',d:0.6},org:{k:'hold'},akor:{k:'hold'},theremin:{k:'hold'},vocoder:{k:'hold'},didger:{k:'hold'},sub808:{k:'decay',d:0.85},tuba:{k:'breath',max:6},sakso:{k:'breath',max:10},flut:{k:'breath',max:10},kalimba:{k:'decay',d:0.7},steel:{k:'decay',d:0.75},gamelan:{k:'decay',d:0.8}};
const SUS_N={decay:'Sönen tel',hold:'Tutan ses',breath:'Nefesli'};
const TKG={tel:'tel',saz:'tel',edrive:'tel',bass:'tel',bow:'tel',wind:'nef',brass:'nef',keys:'tus',lead:'ele'};
const SOLO_TREE=[
 {id:'sdevir',n:'Sahne devri',c:2e5,req:'solo',lane:'Sahne',d:'Solo bölümünde sahne solistin olur: halkalar notaya dönüşür (içerisi pes, dışarısı tiz), ibre yarı hıza düşer, solo doğrudan sahnede çizilir.'},
 {id:'suzun',n:'Uzun nota',c:8e5,req:'sdevir',lane:'Sahne',d:'Notayı halka boyunca sürükleyerek uzat. Gücün nasıl düştüğünü enstrümanın türü belirler: sönen tel, tutan ses, nefesli.'},
 {id:'soktav',n:'İkinci oktav',c:5e6,req:'suzun',lane:'Sahne',d:'Halka sayısı iki katına çıkar: tiz bölge açılır.'},
 {id:'sdoruk',n:'Doruk',c:3e8,req:'soktav',lane:'Sahne',d:'Tepe bölgede 4+ adım tutulan nota sahneyi dolduran bir patlama yapar: herkese hasar, +1 hayran.'},
 {id:'sduet',n:'Sualli-cevaplı',c:2e9,req:'sdoruk',lane:'Sahne',d:'İki solist 4 adımlık cümlelerle birbirine cevap verir; ikisi de ×1,2 güçle çalar.'},
 {id:'tk_tel1',n:'Tel: bend & vibrato',c:3e6,req:'suzun',lane:'Teknik',g:'tel',d:'Telli ve yaylı solistlere bend, vibrato ve slide.'},
 {id:'tk_tel2',n:'Tel: tremolo / feedback / slap',c:3e7,req:'tk_tel1',lane:'Teknik',g:'tel',d:'Saz, akustik, arp: tremolo (uzun nota sönmez, yarı güçte sürer). Elektro: feedback (uzadıkça güçlenir, 16 adımdan sonra ıslık). Bas: slap & pop.'},
 {id:'tk_nef1',n:'Nefesli: dairesel nefes',c:3e6,req:'suzun',lane:'Teknik',g:'nef',d:'Nefes sınırı kalkar; vibrato açılır.'},
 {id:'tk_nef2',n:'Nefesli: growl & bend',c:3e7,req:'tk_nef1',lane:'Teknik',g:'nef',d:'Hırıltı (growl) ve nefesli bend.'},
 {id:'tk_tus1',n:'Tuş: sustain pedalı',c:3e6,req:'suzun',lane:'Teknik',g:'tus',d:'Tuşlular pedalla daha yavaş söner (0,78 → 0,90).'},
 {id:'tk_tus2',n:'Tuş: glissando',c:3e7,req:'tk_tus1',lane:'Teknik',g:'tus',d:'Tuşlulara slide (glissando).'},
 {id:'tk_ele1',n:'Elektronik: portamento',c:3e6,req:'suzun',lane:'Teknik',g:'ele',d:'Synth ve theremin notalar arasında kayar (slide), vibrato yapar.'},
 {id:'tk_ele2',n:'Elektronik: arpejiyatör',c:3e7,req:'tk_ele1',lane:'Teknik',g:'ele',d:'Uzun nota yukarı doğru arpej olur: her adım bir üst halka.'},
 {id:'sseyir',n:'Seyir',c:3e7,req:'suzun',lane:'Biçim',d:'Solonun biçimi puanlanır: Karar (kökte uzun bitiş ×1,25), Doruk (tepede 4+ adım ×1,2), Soru–cevap (cümle arası nefes ×1,15).'},
 {id:'solofast',n:'Bis',c:5e7,req:'sseyir',lane:'Biçim',d:'Solo bölümü iki kat sık gelir: her 12 ölçüde 4 ölçü.'}
];
const TREE_IDX={};SOLO_TREE.forEach(u=>TREE_IDX[u.id]=u);
const SOLO_STYLES={hendrix:{n:'Hendrix',d:'Blues pentatonik, bend ve vibratolu uzun notalar, çift sesler, es payı',arts:['bend','vib','fb','none','slide']},wooten:{n:'Wooten',d:'Hızlı 16’lık koşular, oktav atlamalar, slap ve pop',arts:['slap','pop','none']},taksim:{n:'Taksim',d:'Basamak basamak yürüyen uzun notalar, slide ile giriş, geç vibrato, süslemeler',arts:['slide','vib','none']},synth:{n:'Synth',d:'Arpej koşuları ve tutulan tepe notası',arts:['none','vib']}};
const SOLO_STEPS=32,SOLO_MAX=28;
const DEMO={name:'Gece Vardiyası',msg:'8 enstrüman, 8 bölüm, solo 4. bölümde',bpm:100,meter:'m44',scale:'minor',slots:['davul','trampet','clap','hihat','bas','akustik','saz','ney'],lv:{davul:12,trampet:8,clap:6,hihat:8,bas:8,akustik:6,saz:6,ney:6},
 A:{0:[[0,1],[4,1],[8,1],[12,1]],1:[[4,1],[12,1]],2:[[4,1],[12,1]],3:[[2,1],[6,1],[10,1],[14,1]],4:[[0,1],[8,1]],5:[[0,1],[8,1]],6:[[1,1],[3,1],[6,1]],7:[[8,2],[11,1],[14,1]]},
 B:{0:[[0,1],[4,1],[8,1],[12,1]],1:[[4,1],[12,1]],2:[[4,1],[12,1]],3:[[2,1],[6,1],[10,1],[14,1]],4:[[0,1],[4,1],[8,1],[12,1]],5:[[0,1],[4,1],[8,1],[12,1]],6:[[1,1],[3,1],[6,1]],7:[[8,2],[11,1],[14,1]]},
 S:{6:[[0,1],[3,1],[6,1],[8,1],[11,1],[14,1]]},F:{1:[[8,1],[10,1],[12,1],[13,1]],0:[[14,1],[15,2]]},prog:['root','pop','kadans','pop','pop','klasik','kadans','pop'],prate:'bar',
 solo:{6:1},soloStyle:'taksim',needle:{5:2},plan:['intro','verse','chorus','solo','verse','bridge','build','drop'],up:{solo:1,sef:1,needle2:1,accent:1,echo:1,sdevir:1,suzun:1,soktav:1,tk_tel1:1,tk_tel2:1,sseyir:1,akor:1,dolgu:1},stage:{wall:1,core:1},
 notes:['Akor ölçü başına: nakarat ve yükseliş kadansla (E) bitip kıtaya çözülür','Dolgu: trampet 16’lık koşu, davul son iki vuruş; zil ile geçiş','Davul 1-2-3-4 (grup başları)','Trampet 2 ve 4 (backbeat), el çırpma üstüne katman','Hi-hat aralarda (ofbit nefesi)','Bas davulla aynı yerde (kilit)','Akustik gitar ikinci ibrede, ¾ hızda kayıyor','Saz ilk yarıda sorar, Ney ikinci yarıda cevap verir (soru-cevap)','Saz solo yeri: 4. bölümde parlar','Plan: giriş, kıta, nakarat, solo, kıta, köprü, yükseliş, düşüş']};
/* 2. örnek şarkı — yeni özelliklerin vitrini: hicaz, ölçü başına akor (makam + kadans), dolgu + zil geçişi, sahne devri düeti (gitar sorar, ney cevaplar), teknikler, Doruk ve Karar. Solo notaları elle yazıldı (satır = hicaz basamağı, 7 = üst oktav A′, 10+ = doruk bölgesi). */
const DEMO2={name:'Boğaz’da Düet',msg:'hicaz, akor yürüyüşü, dolgu ve gitar–ney düeti · solo 4. ve 8. bölümde',bpm:112,meter:'m44',scale:'hicaz',slots:['davul','trampet','hihat','darbuka','bas','keman','gitar','ney'],lv:{davul:14,trampet:10,hihat:10,darbuka:10,bas:10,keman:8,gitar:8,ney:8},
 A:{0:[[0,2],[7,1],[8,1],[12,1]],1:[[4,1],[12,2]],2:[[0,1],[2,1],[4,1],[6,1],[8,1],[10,1],[12,1],[14,1]],3:[[2,1],[3,1],[6,1],[11,1],[14,1],[15,1]],4:[[0,1],[7,1],[8,1]],5:[[0,1],[8,1]],6:[[4,1],[12,1]],7:[[8,2],[14,1]]},
 B:{0:[[0,2],[4,1],[8,2],[12,1]],1:[[4,2],[12,2]],2:[[0,1],[2,1],[4,1],[6,1],[8,1],[10,1],[12,1],[14,1]],3:[[1,1],[3,1],[5,1],[7,1],[9,1],[11,1],[13,1],[15,1]],4:[[0,1],[4,1],[8,1],[12,1]],5:[[2,1],[6,1],[10,1],[14,1]],6:[[0,1],[3,1],[6,1],[8,1],[11,1],[14,1]],7:[[0,2],[8,2]]},
 S:{},F:{1:[[8,1],[9,1],[10,1],[11,1]],3:[[12,1],[13,1],[14,1]],0:[[15,2]]},prog:['root','makam','kadans','makam','pop','kadans','makam','kadans'],prate:'bar',
 solo:{6:1,7:1},needle:{5:2},plan:['intro','verse','chorus','solo','bridge','build','drop','solo'],
 up:{solo:1,sef:1,needle2:1,accent:1,echo:1,sdevir:1,suzun:1,soktav:1,sdoruk:1,sduet:1,tk_tel1:1,tk_tel2:1,tk_nef1:1,tk_nef2:1,sseyir:1,akor:1,dolgu:1},stage:{wall:1,core:1,wave:1},
 solos:{6:{style:'hendrix',notes:[{t:0,len:1,r:4,art:'slide'},{t:1,len:1,r:5,art:'none'},{t:2,len:2,r:7,art:'vib'},{t:8,len:1,r:9,art:'bend'},{t:9,len:1,r:10,art:'none'},{t:10,len:2,r:9,art:'vib'},{t:16,len:4,r:11,art:'fb'},{t:24,len:1,r:8,art:'slide'},{t:25,len:5,r:7,art:'vib'}]},
  7:{style:'taksim',notes:[{t:4,len:1,r:7,art:'bend'},{t:5,len:3,r:8,art:'vib'},{t:12,len:4,r:10,art:'vib'},{t:20,len:1,r:11,art:'bend'},{t:21,len:1,r:10,art:'none'},{t:22,len:2,r:9,art:'growl'},{t:28,len:4,r:7,art:'vib'}]}},
 notes:['Hicaz makamı, 112 BPM: Doğu ile Batı aynı sahnede','Akor ölçü başına: kıta ve düşüşte Durak–Güçlü (makam ×1,1); nakarat ve yükseliş kadansla (E) bitip soloya ve düşüşe çözülür','Kadans + dolgu aynı anda: bölüm geçişi ×1,5','Dolgu: trampet 16’lık koşu, darbuka cevap, davul son vuruş (aksan); zil ile geçiş, düşmanlar kısa süre sersemler','Davul düm–tek: 1, 2-ve, 3, 4 · trampet 2 ve 4','Hi-hat sekizlik; darbuka tek-ka süslemeleri','Bas davulu izler, akorun köküne basar','Keman ikinci ibrede ¾ hızda, uzun sesler','Düet (Sualli-cevaplı): gitar 4 adım sorar, ney 4 adım cevaplar; ikisi de ×1,2','Gitar: slide ile giriş, bend, vibrato; 3. cümlede tiz E′ üzerinde 4 adım feedback → Doruk patlaması','Ney: dairesel nefesle uzun nota, tepede D′ 4 adım vibrato → Doruk; growl hırıltısı','Seyir: ikisi de kökte (A′) uzun notayla bitirir → Karar ×1,25 · Doruk ×1,2 · cümle arası nefes → Soru–cevap ×1,15','Plan: giriş, kıta, nakarat, solo, köprü, yükseliş, düşüş, solo']};
const DEMOS=[DEMO,DEMO2];
const NEEDLES=[{k:1,speed:1,dir:1,n:'Ana ibre'},{k:2,speed:0.75,dir:1,n:'İkinci ibre'},{k:3,speed:0.5,dir:-1,n:'Üçüncü ibre'}];
const SUP=[
 {id:'core',n:'Nabız çekirdeği',d:'Her Darbe vuruşunda kalkan +3, nabız saniyede 0,5 yenilenir',c:3e3},
 {id:'wall',n:'Ses duvarı',d:'Halkadan dışarı fışkıran ses çubukları. Titreşim vuruşları uzatır; çubuğa değen düşman uzunlukla orantılı hasar alır',c:3e4},
 {id:'wave',n:'Dalga halkası',d:'Dalga halkasını geçen düşman %25 yavaşlar',c:8e4},
 {id:'beams',n:'Işık huzmeleri',d:'Dönen ışık huzmeleri değdiği düşmanı yakar',c:1.5e7},
 {id:'tunnel',n:'Tünel',d:'Davul şok dalgaları düşmanları geri iter',c:5e7},
 {id:'tower',n:'Ekolayzer kulesi',d:'Her ölçü başında en sağlam düşmana yıldırım iner',c:4e8},
 {id:'mirror',n:'Ayna dalga',d:'Kalkan kapasitesi ×1,5, saniyede +2 kalkan',c:1e9},
 {id:'stars',n:'Takımyıldız',d:'Menzil +%10, ağdaki tüm düşmanlar %10 yavaş',c:1e10}
];
const DUP=[
 {id:'nabiz',n:'Nabız',s:'+60 nabız',d:'Sahne dayanıklılığı +60',c:400,g:1.7},
 {id:'hasar',n:'Hasar',s:'+%12 vuruş',d:'Tüm vuruşlar +%12',c:1500,g:1.8},
 {id:'menzil',n:'Menzil',s:'uzak hedef',d:'Düşmanlar daha uzaktan hedeflenir',c:4000,g:4,max:5},
 {id:'kalkan',n:'Kalkan',s:'+50 sınır',d:'Kalkan üst sınırı +50',c:2500,g:1.9},
 {id:'tamir',n:'Tamir',s:'+1 / sn',d:'Saniyede +1 nabız yenilenir',c:6000,g:2.2},
 {id:'ganimet',n:'Ganimet',s:'+%25 ödül',d:'Düşman ödülü +%25',c:8000,g:2.4},
 {id:'yavas',n:'Yavaşlat',s:'+%10 etki',d:'Yavaşlatıcı etkisi +%10',c:1e4,g:2.6,max:4}
];
const ETYPES={
 memur:{n:'Memur',hp:1,sp:0.045,dmg:10,b:1,r:1,shape:'circle',d:'Yürür, dosya taşır'},
 kurye:{n:'Kurye',hp:0.5,sp:0.1,dmg:6,b:1.2,r:0.8,shape:'tri',d:'Hızlı, kırılgan'},
 stajyer:{n:'Stajyer',hp:0.22,sp:0.07,dmg:3,b:0.35,r:0.55,shape:'dot',swarm:6,d:'Sürü halinde, bedava çalışır'},
 avukat:{n:'Avukat',hp:3,sp:0.035,dmg:18,b:2.5,r:1.2,shape:'hex',armor:true,d:'Zırhlı; Seri yarı işler'},
 sansurcu:{n:'Sansürcü',hp:1.6,sp:0.04,dmg:8,b:1.8,r:1.05,shape:'square',mute:true,d:'Sahneye ulaşırsa bir enstrümanı bir ölçü susturur'},
 denetci:{n:'Denetçi',hp:14,sp:0.03,dmg:40,b:12,r:1.9,shape:'boss',boss:true,noSlow:true,d:'Her 10. dalga; yavaşlamaz'},
 mudur:{n:'Müdür',hp:30,sp:0.028,dmg:60,b:25,r:2.2,shape:'boss',boss:true,spawn:'stajyer',d:'Her 25. dalga; stajyer çağırır'},
 ceo:{n:'CEO',hp:80,sp:0.024,dmg:120,b:60,r:2.6,shape:'boss',boss:true,spawn:'kurye',noSlow:true,d:'Her 50. dalga; kurye çağırır, yavaşlamaz'}
};
const WAVE_LINES={1:'Sessizlik A.Ş. ilk memurlarını yolladı. Döngü çalsın.',2:'Kuryeler hızlı gelir; Güdümlü bir enstrüman iyi olur.',4:'Stajyer sürüsü: bedava çalışırlar, kalabalık gelirler. Alan vuruşu düşün.',6:'Avukatlar zırhlı: Seri vuruşlar yarı işler, Delici ve Darbe tam.',9:'Sansürcüler sahneye ulaşırsa bir enstrümanı bir ölçü susturur.',15:'Şirket bütçe onayladı: dalgalar kalabalıklaşıyor.',21:'Üst kat sessizlik sever. Sen de yüksek sesle çal.'};
const BOSS_LINES={denetci:'Denetçi geldi: klasörü kalın, adımı yavaş, yavaşlatma işlemez.',mudur:'Müdür sahnede: iki ölçüde bir stajyer sürüsü çağırır.',ceo:'CEO bizzat geldi. Kuryeler ardı ardına gelir.'};
const LADDER=[
 {a:1,t:'B deseni · Şerit düzeni'},
 {a:2,t:'9/8 aksak ölçü'},
 {a:3,t:'Hicaz makamı'},
 {a:4,t:'7/8 ve 5/8 ölçüleri'},
 {a:5,t:'Kürdi makamı'},
 {a:6,t:'Dünya turnesi: şehirler ve Efsane'}
];
/* manager automation, bought once and kept across albums; each tier can be switched off */
const AUTO=[
 {id:'lv',n:'Menajer: seviye',d:'10 saniyede bir, notanın yarısını aşmayan en ucuz seviyeyi sahnedeki enstrümanlara alır',c:2e6,al:1},
 {id:'ord',n:'Menajer: sipariş',d:'Koşulu sağlanan siparişi kendisi teslim eder',c:2e7,al:2},
 {id:'ins',n:'Menajer: sahne',d:'Boş yer varsa ve notanın dörtte birine sığıyorsa açık ailelerden sıradaki enstrümanı açar, sahneye koyar ve rolüne uygun basit bir desen çizer',c:2e8,al:2},
 {id:'alb',n:'Menajer: albüm',d:'Dönem kazancı eşiğin iki katına ulaşınca albümü kendisi çıkarır',c:5e8,al:3}
];
/* world tour cities: liked scale/meter give ×1,1 each, enemy mix is biased */
const CITIES=[
 {id:'istanbul',n:'İstanbul',scale:'hicaz',meter:'m98',bias:{sansurcu:1.6},d:'Hicaz ve 9/8 sever; sansürcüler kalabalık'},
 {id:'berlin',n:'Berlin',scale:'minor',meter:'m44',bias:{kurye:1.6},d:'Minör ve 4/4; kuryeler hızlı ve çok'},
 {id:'tokyo',n:'Tokyo',scale:'major',meter:'m44',bias:{avukat:1.6},d:'Majör; kalkanlı avukatlar'},
 {id:'rio',n:'Rio',scale:'major',meter:'m44',bias:{stajyer:1.7},d:'Majör; stajyer sürüleri'},
 {id:'newyork',n:'New York',scale:'minor',meter:'m78',bias:{memur:1.4,avukat:1.3},d:'Minör ve 7/8; her tür biraz daha fazla'},
 {id:'lagos',n:'Lagos',scale:'kurdi',meter:'m58',bias:{kurye:1.3,stajyer:1.3},d:'Kürdi ve 5/8; hızlı ve kalabalık'},
 {id:'reykjavik',n:'Reykjavík',scale:'minor',meter:'m44',bias:{sansurcu:2.2},d:'Sessizlik en güçlü burada: sansürcü iki kat'},
 {id:'mumbai',n:'Mumbai',scale:'hicaz',meter:'m78',bias:{memur:1.6},d:'Hicaz ve 7/8; memur ordusu'}
];
const TOUR_AL=6;
const BOOK=[
 {id:'four',fx:{roleD:{darbe:1.2}},e:'Darbe silahları +%20',n:'Dört vuruş',m:'m44',s:[0,4,8,12],h:'Her vuruşa bir darbe',lore:'Disko ve house’un temeli.'},
 {id:'back',fx:{crit:0.15},e:'Keskin kritik şansı +%15',n:'Backbeat',m:'m44',s:[4,12],h:'İki darbe: 2 ve 4',lore:'Rock ve pop’ta 2. ve 4. vuruşa düşen trampet.'},
 {id:'half',fx:{row:2},e:'Bu halka ×2',n:'Yarım tempo',m:'m44',s:[8],h:'Tek darbe, ölçünün ortası',lore:'Şarkıyı ağır ve geniş hissettirir.'},
 {id:'off',fx:{roleD:{seri:1.25}},e:'Seri silahları +%25',n:'Ofbit',m:'m44',s:[2,6,10,14],h:'Dört darbe, tam aralarda',lore:'Ska gitarında ve house hi-hat’inde sık duyulur.'},
 {id:'eighth',fx:{nefes:4},e:'Bu halkanın nefesi +4',n:'Sekizlikler',m:'m44',s:[0,2,4,6,8,10,12,14],h:'Sekiz eşit darbe',lore:'Rock hi-hat’inin düz akışı.'},
 {id:'tres',fx:{row:1.5},e:'Bu halka ×1,5',n:'Tresillo',m:'m44',s:[0,6,12],h:'Üç darbe: 3+3+2',lore:'Afro-Küba müziğinden pop’a kadar yayılmış bölünme.'},
 {id:'haba',fx:{nota:1.25},e:'Tüm sahne nota +%25',n:'Habanera',m:'m44',s:[0,6,8,12],h:'Tresillo artı ortada bir darbe',lore:'Küba kökenli dans ritmi.'},
 {id:'son',fx:{dmg:1.1,clave:1},e:'Tüm hasar +%10; clave adımlarına uyanlar +%25',n:'Son clave',m:'m44',s:[0,3,6,10,12],h:'Beş darbe, 3-2 yönünde',lore:'Salsanın omurgası.'},
 {id:'rumba',fx:{nota:1.1,clave:1},e:'Tüm nota +%10; clave adımlarına uyanlar +%25',n:'Rumba clave',m:'m44',s:[0,3,7,10,12],h:'Son clave’in üçüncüsü bir adım geç',lore:'Son clave’den daha gergin bir his verir.'},
 {id:'bossa',fx:{slow:0.1,clave:1},e:'Düşmanlar %10 yavaş; clave adımlarına uyanlar +%25',n:'Bossa nova',m:'m44',s:[0,3,6,10,13],h:'Son clave’in sonuncusu bir adım kayar',lore:'Brezilya’dan, yumuşak ve kaygan.'},
 {id:'baladi',fx:{roleD:{darbe:1.2},wall:1.3},e:'Darbe +%20, ses duvarı ×1,3',n:'Baladi',m:'m44',s:[0,2,6,8,12],h:'Düm düm tek, düm tek',lore:'Darbukanın en bilinen kalıplarından.'},
 {id:'duyek',fx:{famD:{vur:1.15}},e:'Vurmalılar +%15',n:'Düyek',m:'m44',s:[0,4,6,8,12],h:'Düm tek-ke düm tek',lore:'Türk müziğinin sekiz zamanlı temel usulü.'},
 {id:'aksak',fx:{meter:0.2},e:'Ölçü bonusu +0,2',n:'Aksak',m:'m98',s:[0,4,8,12],h:'9/8’de grup başları',lore:'2+2+2+3; Roman havasının iskeleti.'},
 {id:'yedi',fx:{meter:0.2},e:'Ölçü bonusu +0,2',n:'Yedi zaman',m:'m78',s:[0,6,10],h:'7/8’de grup başları',lore:'3+2+2; Balkanlar’da ve Anadolu’da sık duyulur.'},
 {id:'bes',fx:{meter:0.2},e:'Ölçü bonusu +0,2',n:'Türk aksağı',m:'m58',s:[0,4],h:'5/8’de grup başları',lore:'2+3; beş zamanlı topal yürüyüş.'}
];
const ALB=['Gece vardiyası','Saat yönünde','Neon düm tek','Kırık metronom','Mor statik','Yörünge','Döngüde kal','Sıfır kilometre bas','Ay ışığı hi-hat','Son vagon','Elektrik kesintisi','Sessiz çatı'];
