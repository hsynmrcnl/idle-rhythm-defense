/* ================= audio ================= */
let ac=null,drum,dShaper,music,musicLP,mShaper,side,comp,masterLP,analyser,master,send,delay,lfoG,crackleG,noise,fData,tData;
const DIST={};
function curve(k){const key=String(k);if(DIST[key])return DIST[key];const n=1024,c=new Float32Array(n);for(let i=0;i<n;i++){const x=i*2/n-1;c[i]=k==='crush'?Math.round(x*8)/8:k===0?x:(1+k)*x/(1+k*Math.abs(x))}return DIST[key]=c}
function initAudio(){
 ac=new(window.AudioContext||window.webkitAudioContext)();
 comp=ac.createDynamicsCompressor();comp.threshold.value=-14;comp.ratio.value=4;comp.attack.value=0.003;comp.release.value=0.15;
 masterLP=ac.createBiquadFilter();masterLP.type='lowpass';masterLP.frequency.value=20000;
 analyser=ac.createAnalyser();analyser.fftSize=1024;analyser.smoothingTimeConstant=0.78;
 fData=new Uint8Array(analyser.frequencyBinCount);tData=new Float32Array(analyser.fftSize);
 master=ac.createGain();master.gain.value=S.muted?0:0.7;
 drum=ac.createGain();dShaper=ac.createWaveShaper();dShaper.curve=curve(0);
 music=ac.createGain();musicLP=ac.createBiquadFilter();musicLP.type='lowpass';musicLP.frequency.value=20000;mShaper=ac.createWaveShaper();mShaper.curve=curve(0);side=ac.createGain();
 drum.connect(dShaper);dShaper.connect(comp);music.connect(musicLP);musicLP.connect(mShaper);mShaper.connect(side);side.connect(comp);
 comp.connect(masterLP);masterLP.connect(analyser);analyser.connect(master);master.connect(ac.destination);
 send=ac.createGain();send.gain.value=0;delay=ac.createDelay(2);delay.delayTime.value=60/S.bpm*0.75;
 const fb=ac.createGain();fb.gain.value=0.38;const dlp=ac.createBiquadFilter();dlp.type='lowpass';dlp.frequency.value=2600;
 send.connect(delay);delay.connect(dlp);dlp.connect(fb);fb.connect(delay);const wet=ac.createGain();wet.gain.value=0.55;dlp.connect(wet);wet.connect(comp);
 const lfo=ac.createOscillator();lfo.frequency.value=0.06;lfoG=ac.createGain();lfoG.gain.value=0;lfo.connect(lfoG);lfoG.connect(musicLP.frequency);lfo.start();
 noise=ac.createBuffer(1,ac.sampleRate,ac.sampleRate);const d=noise.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;
 const cb=ac.createBuffer(1,ac.sampleRate*2,ac.sampleRate);const cd=cb.getChannelData(0);for(let i=0;i<cd.length;i++)cd[i]=Math.random()<0.0007?(Math.random()*2-1):(Math.random()*2-1)*0.015;
 const cs=ac.createBufferSource();cs.buffer=cb;cs.loop=true;crackleG=ac.createGain();crackleG.gain.value=0;cs.connect(crackleG);crackleG.connect(masterLP);cs.start();
 syncFx();
}
function ensureAudio(){if(!ac){initAudio();sfLoadStage()}if(ac.state==='suspended')ac.resume()}
function syncFx(){
 if(!ac)return;const t=ac.currentTime,th=dispTheme(),k=th.kit;
 send.gain.setTargetAtTime(S.up.echo?0.4:0,t,0.05);
 delay.delayTime.setTargetAtTime(60/S.bpm*0.75,t,0.05);
 master.gain.setTargetAtTime(S.muted?0:0.7,t,0.02);
 masterLP.frequency.setTargetAtTime(k.lp,t,0.1);
 crackleG.gain.setTargetAtTime(k.crackle?0.05:0,t,0.1);
 dShaper.curve=curve(k.crush?'crush':k.drive);mShaper.curve=curve(k.drive*0.5);
 if(S.up.filter){musicLP.frequency.setTargetAtTime(5200,t,0.1);lfoG.gain.setTargetAtTime(4200,t,0.1)}
 else{lfoG.gain.setTargetAtTime(0,t,0.1);musicLP.frequency.setTargetAtTime(20000,t,0.1)}
}
function env(g,t,a,dur,att){g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(Math.max(a,0.0002),t+(att||0.004));g.gain.exponentialRampToValueAtTime(0.0001,t+dur)}
function O(type,f,t,dur,a,dest,f2,fT,att){const o=ac.createOscillator(),g=ac.createGain();o.type=type;o.frequency.setValueAtTime(f,t);if(f2)o.frequency.exponentialRampToValueAtTime(f2,t+(fT||dur));env(g,t,a,dur,att);o.connect(g);g.connect(dest);o.start(t);o.stop(t+dur+0.05);return g}
function Nz(t,type,f,q,a,dur,dest,gate){const s=ac.createBufferSource();s.buffer=noise;const fl=ac.createBiquadFilter();fl.type=type;fl.frequency.value=f;if(q)fl.Q.value=q;const g=ac.createGain();if(gate){g.gain.setValueAtTime(a,t);g.gain.setValueAtTime(a,t+dur-0.02);g.gain.linearRampToValueAtTime(0.0001,t+dur)}else env(g,t,a,dur);s.connect(fl);fl.connect(g);g.connect(dest);s.start(t,Math.random()*0.4);s.stop(t+dur+0.05);return g}
function synth(t,f,a,dur,f0,f1,q,dest,type,det,att){const lp=ac.createBiquadFilter();lp.type='lowpass';lp.Q.value=q;lp.frequency.setValueAtTime(f0,t);lp.frequency.exponentialRampToValueAtTime(f1,t+dur*0.8);const g=ac.createGain();env(g,t,a,dur,att);lp.connect(g);g.connect(dest);(det||[0]).forEach(dv=>{const o=ac.createOscillator();o.type=type||'sawtooth';o.frequency.value=f;o.detune.value=dv;o.connect(lp);o.start(t);o.stop(t+dur+0.05)});return g}
function dirty(t,freqs,type,det,k,lpf,a,dur,dest){const sh=ac.createWaveShaper();sh.curve=curve(k);const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=lpf;const g=ac.createGain();env(g,t,a,dur);sh.connect(lp);lp.connect(g);g.connect(dest);freqs.forEach(f=>(det||[0]).forEach(dv=>{const o=ac.createOscillator();o.type=type;o.frequency.value=f;o.detune.value=dv;o.connect(sh);o.start(t);o.stop(t+dur+0.05)}));return g}
function metalCluster(t,base,dur,a,hp){const bp=ac.createBiquadFilter();bp.type='bandpass';bp.frequency.value=Math.min(16000,10000*base);const h=ac.createBiquadFilter();h.type='highpass';h.frequency.value=hp;const g=ac.createGain();env(g,t,a,dur);bp.connect(h);h.connect(g);g.connect(drum);[205.3,304.4,369.6,522.7,540,800].forEach(f=>{const o=ac.createOscillator();o.type='square';o.frequency.value=f*base;o.connect(bp);o.start(t);o.stop(t+dur+0.05)})}
function fmTone(t,f,ratio,index,dur,a){const c=ac.createOscillator(),m=ac.createOscillator(),mg=ac.createGain(),g=ac.createGain();c.frequency.value=f;m.frequency.value=f*ratio;mg.gain.setValueAtTime(f*index,t);mg.gain.exponentialRampToValueAtTime(f*index*0.05+0.01,t+dur);m.connect(mg);mg.connect(c.frequency);env(g,t,a,dur,0.004);c.connect(g);g.connect(music);c.start(t);m.start(t);c.stop(t+dur+0.05);m.stop(t+dur+0.05);return g}
function leadTone(t,f,p,a){const dur=p.dur||0.4;const o=ac.createOscillator();o.type=p.type||'sawtooth';o.frequency.setValueAtTime(p.gliss?f*0.94:f,t);if(p.gliss)o.frequency.exponentialRampToValueAtTime(f,t+0.12);const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=p.lp||4000;const g=ac.createGain();env(g,t,(p.a||0.15)*a,dur,p.att||0.005);o.connect(lp);lp.connect(g);g.connect(music);g.connect(send);if(p.vib){const l=ac.createOscillator(),lg=ac.createGain();l.frequency.value=p.vib;lg.gain.value=f*0.012;l.connect(lg);lg.connect(o.frequency);l.start(t);l.stop(t+dur+0.1)}o.start(t);o.stop(t+dur+0.1);return g}
function brassTone(t,f,p,a){const dur=p.dur||0.3;const o=ac.createOscillator();o.type='sawtooth';o.frequency.value=f;const fl=ac.createBiquadFilter();fl.type=p.nasal?'bandpass':'lowpass';if(p.nasal)fl.Q.value=4;fl.frequency.setValueAtTime(p.nasal?f*3:300,t);fl.frequency.exponentialRampToValueAtTime(p.lp||3000,t+0.08);const g=ac.createGain();env(g,t,(p.a||0.15)*a,dur,0.02);o.connect(fl);fl.connect(g);g.connect(music);g.connect(send);if(p.growl){const o2=ac.createOscillator();o2.type='sawtooth';o2.frequency.value=f*1.01;o2.connect(fl);o2.start(t);o2.stop(t+dur+0.1)}o.start(t);o.stop(t+dur+0.1);return g}
let SOLO_F=0;
let CUR_B=0;
const chordAt=s=>SOLO_F?[SOLO_F,SOLO_F*1.25,SOLO_F*1.5]:chordFreqs(curChord(CUR_B,s));
const rootAt=s=>rootFreq(curChord(CUR_B,s));
function crashVoice(t,a){try{GEN.metal(t,a||1,IDX.zil.v,0)}catch(e){}}
const arpF=s=>chordAt(s)[[0,1,2,1][MI.pos[s]%4]]*2;
function pitchOf(p,s){if(SOLO_F)return SOLO_F*Math.pow(2,p.oct||0);let f;switch(p.pitch){case 'root':f=rootAt(s);break;case 'arp':f=arpF(s);break;case 'high':f=arpF(s)*2;break;case 'low':f=rootAt(s)/2;break;default:f=p.f||220}return f*Math.pow(2,p.oct||0)}
const KSC={};
function ksBuf(f,dur,bright){const key=Math.round(f*4)+':'+dur+':'+bright;if(KSC[key])return KSC[key];const sr=ac.sampleRate,N=Math.max(2,Math.round(sr/f)),len=Math.floor(sr*dur),buf=ac.createBuffer(1,len,sr),d=buf.getChannelData(0);const r=rng(Math.round(f*7)+11);let x=0;for(let i=0;i<N;i++){x=x*(1-bright)+(r()*2-1)*bright;d[i]=x}const g=Math.pow(0.001,N/(sr*dur*1.6));for(let i=N;i<len;i++){d[i]=g*0.5*(d[i-N]+d[i-N+1])}return KSC[key]=buf}
const soloSeqs={};
function soloDeg(win,k){let seq=soloSeqs[win];if(!seq){seq=[];const r=rng(win*131+7);let deg=3;for(let i=0;i<40;i++){deg=clamp(deg+[-2,-1,-1,0,1,1,2][Math.floor(r()*7)],0,6);seq.push(deg)}soloSeqs[win]=seq}return seq[k%seq.length]}
function soloFreq(win,pos,s){const ch=SCALES[S.scale].ch[MI.grp[s]%4],pool=[ch[0],ch[1],ch[2],ch[0]*2,ch[1]*2,ch[2]*2,ch[0]*4];return pool[soloDeg(win,pos*MI.N+s)]}
function ksBuf2(f,dur,bright,pick){const key='n'+Math.round(f*4)+':'+Math.round(dur*10)+':'+bright+':'+pick;if(KSC[key])return KSC[key];const sr=ac.sampleRate,N=Math.max(2,Math.round(sr/f)),len=Math.floor(sr*dur),buf=ac.createBuffer(1,len,sr),d=buf.getChannelData(0);const r=rng(Math.round(f*7)+11);let x=0;const ex=new Float32Array(N);for(let i=0;i<N;i++){x=x*(1-bright)+(r()*2-1)*bright;ex[i]=x}const pp=Math.max(1,Math.round(N*pick));for(let i=0;i<N;i++)d[i]=ex[i]-(i>=pp?ex[i-pp]*0.9:0);const g=Math.pow(0.001,N/(sr*dur*1.6));for(let i=N;i<len;i++)d[i]=g*(0.5*(d[i-N]+d[i-N+1]));return KSC[key]=buf}
function body(dest,peaks,wet){const inp=ac.createGain(),dry=ac.createGain(),wetG=ac.createGain();dry.gain.value=1-wet;wetG.gain.value=wet;inp.connect(dry);dry.connect(dest);peaks.forEach(([fr,q,gn])=>{const b=ac.createBiquadFilter();b.type='bandpass';b.frequency.value=fr;b.Q.value=q;const g=ac.createGain();g.gain.value=gn;inp.connect(b);b.connect(g);g.connect(wetG)});wetG.connect(dest);return inp}
function artRate(src,t,dur,art){const pr=src.playbackRate;pr.setValueAtTime(art==='slide'?Math.pow(2,-5/12):1.008,t);if(art==='slide')pr.exponentialRampToValueAtTime(1,t+Math.min(0.18,dur*0.5));else pr.exponentialRampToValueAtTime(1,t+0.07);if(art==='bend'){const t1=t+Math.min(0.25,dur*0.3),t2=t+Math.min(0.6,dur*0.65);pr.setValueAtTime(1,t1);pr.exponentialRampToValueAtTime(Math.pow(2,2/12),t2)}if(art==='vib'||art==='fb'||(art==='none'&&dur>1.2)){const l=ac.createOscillator(),lg=ac.createGain();l.frequency.value=art==='fb'?5.2:5.6;lg.gain.setValueAtTime(0,t);lg.gain.linearRampToValueAtTime(art==='none'?0.006:0.012,t+Math.min(0.5,dur*0.4));l.connect(lg);lg.connect(pr);l.start(t);l.stop(t+dur+0.1)}}
function artFreq(o,f,t,dur,art){const fr=o.frequency;fr.setValueAtTime(art==='slide'?f*Math.pow(2,-5/12):f,t);if(art==='slide')fr.exponentialRampToValueAtTime(f,t+Math.min(0.2,dur*0.5));if(art==='bend'){fr.setValueAtTime(f,t+Math.min(0.25,dur*0.3));fr.exponentialRampToValueAtTime(f*Math.pow(2,2/12),t+Math.min(0.6,dur*0.65))}if(art==='vib'||art==='fb'||(art==='none'&&dur>1)){const l=ac.createOscillator(),lg=ac.createGain();l.frequency.value=5.4;lg.gain.setValueAtTime(0,t);lg.gain.linearRampToValueAtTime(f*(art==='none'?0.006:0.013),t+Math.min(0.5,dur*0.4));l.connect(lg);lg.connect(fr);l.start(t);l.stop(t+dur+0.1)}}
function pluckNote(t,f,p,a,hold,art){const dur=hold?hold+0.45:(p.dur||1)*Math.pow(220/f,0.35);const out=body(music,p.body||[[108,2,0.9],[214,3,0.7],[425,4,0.45]],p.wet==null?0.42:p.wet);const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=p.lp||5500;lp.connect(out);
 (p.course||[[1,1]]).forEach(([ratio,gn],k)=>{const g=ac.createGain();const amp=(p.a||0.24)*gn*a;g.gain.setValueAtTime(amp,t);if(hold){g.gain.setValueAtTime(amp,t+hold-0.2);g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.3)}else g.gain.exponentialRampToValueAtTime(0.0001,t+dur*(k?0.85:1));g.connect(lp);const s=ac.createBufferSource();s.buffer=ksBuf2(f*ratio,dur,p.bright||0.55,p.pick||0.22);artRate(s,t,hold||dur,art||'none');s.connect(g);s.start(t+k*0.004);s.stop(t+dur+0.1)});
 Nz(t,'bandpass',p.pickF||3200,1.5,(p.pickA||0.12)*a,0.012,out);if(p.gitar)out.connect(send);}
function sazNote(t,f,a,dur,hold,art){const out=body(music,[[190,3,0.8],[380,4,0.6],[760,5,0.4],[3400,2,0.35]],0.32);const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=7500;lp.connect(out);out.connect(send);
 const D=hold?hold+0.4:dur*Math.pow(220/f,0.3);
 [[1,1,0.85,1],[1.003,0.85,0.85,1],[2,0.42,0.95,0.6]].forEach(([ratio,gn,br,dk],k)=>{const g=ac.createGain();const amp=0.22*gn*a;g.gain.setValueAtTime(amp,t);if(hold){g.gain.setValueAtTime(amp*0.9,t+hold-0.15);g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.25)}else g.gain.exponentialRampToValueAtTime(0.0001,t+D*dk);g.connect(lp);const s=ac.createBufferSource();s.buffer=ksBuf2(f*ratio,D,br,0.12);artRate(s,t,hold||D,art||'none');s.connect(g);s.start(t+k*0.003);s.stop(t+D+0.1)});
 Nz(t,'bandpass',4200,1.5,0.16*a,0.010,out);Nz(t,'highpass',6000,0,0.05*a,0.004,out);
 const dg=ac.createGain();dg.gain.setValueAtTime(0.05*a,t);dg.gain.exponentialRampToValueAtTime(0.0001,t+D*1.3);dg.connect(lp);const ds=ac.createBufferSource();ds.buffer=ksBuf2(SCALES[S.scale].root[0],D*1.4,0.5,0.2);ds.connect(dg);ds.start(t+0.002);ds.stop(t+D*1.4+0.1);
 if(a>1.2){setTimeout(()=>{},0);const t2=t+0.045;[[1,0.6],[2,0.25]].forEach(([ratio,gn])=>{const g=ac.createGain();g.gain.setValueAtTime(0.22*gn*a,t2);g.gain.exponentialRampToValueAtTime(0.0001,t2+D*0.8);g.connect(lp);const s=ac.createBufferSource();s.buffer=ksBuf2(f*ratio*1.002,D,0.9,0.12);s.connect(g);s.start(t2);s.stop(t2+D+0.1)});Nz(t2,'bandpass',4600,1.5,0.1*a,0.008,out)}}
function bowNote(t,f,p,a,hold,art){const dur=hold||p.dur||0.8;const out=body(music,p.body||[[280,2,0.9],[600,3,0.7],[1100,4,0.5],[2800,5,0.3]],0.55);out.connect(send);const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime((p.lp||3400)*0.6,t);lp.frequency.linearRampToValueAtTime(p.lp||3400,t+0.25);lp.Q.value=0.8;const g=ac.createGain();g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime((p.a||0.16)*a,t+(p.att||0.09));g.gain.setValueAtTime((p.a||0.16)*a,t+Math.max(p.att||0.09,dur-0.14));g.gain.exponentialRampToValueAtTime(0.0001,t+dur);lp.connect(g);g.connect(out);
 [0,-7].forEach(dv=>{const o=ac.createOscillator();o.type='sawtooth';o.detune.value=dv;artFreq(o,f,t,dur,art||'none');if(!art||art==='none'){const vib=ac.createOscillator(),vg=ac.createGain();vib.frequency.value=p.vib||5.6;vg.gain.setValueAtTime(0,t);vg.gain.linearRampToValueAtTime(f*0.009,t+0.35);vib.connect(vg);vg.connect(o.frequency);vib.start(t);vib.stop(t+dur+0.1)}o.connect(lp);o.start(t);o.stop(t+dur+0.1)});
 Nz(t,'highpass',1800,0,0.035*a,0.12,out);}
const GEN={
 pluck2(t,a,p,s){const fs=p.pitch==='chord'?chordAt(s).map(f=>f*Math.pow(2,p.oct||0)):[pitchOf(p,s)];fs.forEach((f,k)=>pluckNote(t+(p.strum||0)*k,f,p,a))},
 saz(t,a,p,s){sazNote(t,pitchOf(p,s),a,p.dur||1.1)},
 bow(t,a,p,s){bowNote(t,pitchOf(p,s),p,a)},
 ks(t,a,p,s){const fs=p.pitch==='chord'?chordAt(s).map(f=>f*Math.pow(2,p.oct||0)):[pitchOf(p,s)];const dur=p.dur||1;fs.forEach((f,k)=>{const t0=t+(p.strum||0)*k,g=ac.createGain();g.gain.setValueAtTime((p.a||0.3)*a,t0);g.gain.exponentialRampToValueAtTime(0.0001,t0+dur);g.connect(music);g.connect(send);const src=ac.createBufferSource();src.buffer=ksBuf(f,dur,p.bright||0.5);src.connect(g);src.start(t0);src.stop(t0+dur+0.02);if(p.double){const s2=ac.createBufferSource();s2.buffer=ksBuf(f*1.004,dur,p.bright||0.5);s2.connect(g);s2.start(t0+0.005);s2.stop(t0+dur+0.02)}})},
 kick(t,a,p){const f0=p.f0||165,f1=p.f1||44;O('sine',f0,t,p.dur||0.4,(p.a||0.95)*a,drum,f1,0.13);if(p.click)Nz(t,'highpass',3000,0,0.06*a,0.012,drum);if(p.noise)Nz(t,'lowpass',p.big?600:900,0,0.2*a,0.05,drum);if(p.big)Nz(t,'bandpass',200,1,0.3*a,0.3,drum);if(a>1)O('sine',f1*1.2,t,0.5,0.3*a,drum)},
 tkick(t,a,p,s){const f=pitchOf(p,s);O('sine',f*2.2,t,p.dur||0.7,(p.a||0.9)*a,drum,f,0.08);if(p.sub)O('triangle',f,t,(p.dur||0.7)*0.8,0.25*a,drum)},
 noise(t,a,p){const dur=(p.open&&a>1)?p.open:(p.dur||0.1);Nz(t,p.ft||'highpass',p.f||1400,p.q||0,(p.a||0.4)*a,dur,drum);if(p.tone)O('triangle',p.tone,t,p.toneDur||0.1,0.28*a,drum,p.tone*0.72);if(p.gate&&dispTheme().kit.gate)Nz(t+0.02,'highpass',900,0,0.3*a,0.24,drum,true)},
 clap(t,a){for(let k=0;k<3;k++)Nz(t+k*0.011,'bandpass',1350,0.9,0.42*a,0.028,drum);Nz(t+0.033,'bandpass',1250,0.8,0.32*a,0.17,drum).connect(send)},
 darb(t,a,p,s){const doum=MI.pos[s]===0||MI.pos[s]===2;if(doum){O('sine',118,t,0.34,0.75*a,drum,78,0.2);Nz(t,'lowpass',400,0,0.12*a,0.05,drum)}else{O('triangle',820,t,0.07,0.2*a,drum,700);Nz(t,'bandpass',3600,1.2,0.34*a,0.05,drum)}},
 tabla(t,a,p,s){if(MI.pos[s]%2===0)O('sine',180,t,0.25,0.5*a,drum,120,0.2);else{O('sine',720,t,0.3,0.3*a,drum,700);Nz(t,'bandpass',3000,2,0.2*a,0.03,drum)}},
 metal(t,a,p){metalCluster(t,p.f||1,p.dur||0.9,(p.a||0.12)*a,p.hp||5000)},
 bass(t,a,p,s){const f=pitchOf(p,s);synth(t,f,0.3*a,0.26,1100,180,6,music);O('sine',f,t,0.26,0.22*a,music)},
 power(t,a,p,s){const f=pitchOf(p,s);dirty(t,[f,f*1.5,f*2],'sawtooth',[-9,9],60,3400,0.075*a,0.34,music);O('sine',f/2,t,0.3,0.06*a,music)},
 pluck(t,a,p,s){const f=pitchOf(p,s);synth(t,f,(p.a||0.2)*a,p.dur||0.3,p.lp0||2500,p.lp1||300,p.q||4,music,p.type||'sawtooth',p.det).connect(send)},
 pad(t,a,p,s){chordAt(s).forEach(f=>synth(t,f*Math.pow(2,p.oct||0),(p.a||0.05)*a,p.dur||0.35,p.lp0||2400,p.lp1||500,1,music,'sawtooth',[-7,7],p.att).connect(send))},
 fm(t,a,p,s){const fs=p.chord?chordAt(s).map(f=>f*Math.pow(2,p.oct||0)):[pitchOf(p,s)];fs.forEach(f=>fmTone(t,f,p.ratio||2,p.index||1,p.dur||0.6,(p.a||0.1)*a).connect(send))},
 organ(t,a,p,s){chordAt(s).forEach(f=>{[1,2,3,4].forEach((h,k)=>O('sine',f*h,t,p.dur||0.4,(p.a||0.04)*a/(k+1),music,0,0,0.01))})},
 lead(t,a,p,s){leadTone(t,pitchOf(p,s),p,a)},
 brass(t,a,p,s){brassTone(t,pitchOf(p,s),p,a)},
 flute(t,a,p,s){const f=pitchOf(p,s),dur=p.dur||0.4;O('sine',f,t,dur,(p.a||0.16)*a,music,0,0,p.att||0.03).connect(send);O('sine',f*2,t,dur*0.8,0.03*a,music,0,0,p.att||0.03);Nz(t,'bandpass',Math.min(12000,f*2),8,(p.breath||0.05)*a,dur,music)},
 drone(t,a,p,s){const f=pitchOf(p,s),dur=p.dur||0.9;synth(t,f,(p.a||0.2)*a,dur,600,250,8,music,'sawtooth',[-5,5],0.05);O('sine',f,t,dur,0.15*a,music)},
 riser(t,a){const src=ac.createBufferSource();src.buffer=noise;const bp=ac.createBiquadFilter();bp.type='bandpass';bp.Q.value=3;bp.frequency.setValueAtTime(300,t);bp.frequency.exponentialRampToValueAtTime(6000,t+0.3);const g=ac.createGain();env(g,t,0.3*a,0.35);src.connect(bp);bp.connect(g);g.connect(drum);src.start(t);src.stop(t+0.4)},
 vox(t,a,p,s){chordAt(s).forEach(f=>{const o=ac.createOscillator();o.type='sawtooth';o.frequency.value=f;[700,1800].forEach(fc=>{const bp=ac.createBiquadFilter();bp.type='bandpass';bp.frequency.value=fc;bp.Q.value=6;const g=ac.createGain();env(g,t,0.06*a,0.35,0.02);o.connect(bp);bp.connect(g);g.connect(music);g.connect(send)});o.start(t);o.stop(t+0.4)})}
};
function driveNode(k){const sh=ac.createWaveShaper();sh.curve=curve(k);return sh}
function soloFreq2(x,row){const sc=SOLO_SCALE[S.scale]||SOLO_SCALE.minor,n=sc.length,oct=Math.floor(row/n),semi=sc[row%n]+12*oct;let base=SCALES[S.scale].root[0]*2;const fl=x.v.solo;if(fl==='bass')base/=2;if(x.v.pitch==='high'||fl==='wind')base*=1;return base*Math.pow(2,semi/12)}
function soloVoice(x,t,row,hold,art,a){const f=soloFreq2(x,row),fl=x.v.solo||'lead';a=a||1;if(sfSolo(x,t,row,hold,art,a))return;
 if(fl==='saz'){sazNote(t,f,a*1.1,1.1,hold,art);return}
 if(fl==='tel'){pluckNote(t,f,x.v,a*1.1,hold,art);return}
 if(fl==='bow'){bowNote(t,f,x.v,a,hold,art);return}
 if(fl==='edrive'){const sh=driveNode(25),lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=3200;const g=ac.createGain();const amp=0.2*a;g.gain.setValueAtTime(amp,t);g.gain.setValueAtTime(amp,t+Math.max(0.05,hold-0.3));g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.1);sh.connect(lp);lp.connect(g);g.connect(music);g.connect(send);const s=ac.createBufferSource();s.buffer=ksBuf2(f,hold+0.6,0.7,0.18);artRate(s,t,hold,art);s.connect(sh);s.start(t);s.stop(t+hold+0.2);if(art==='fb'||hold>1.5){const fb=ac.createOscillator(),fg=ac.createGain();fb.type='sine';fb.frequency.value=f*2;fg.gain.setValueAtTime(0.0001,t);fg.gain.exponentialRampToValueAtTime(0.12*a,t+hold*0.7);fg.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.1);fb.connect(fg);fg.connect(sh);fb.start(t);fb.stop(t+hold+0.2)}Nz(t,'bandpass',3000,1.5,0.1*a,0.01,music);return}
 if(fl==='bass'){const pop=art==='pop',slap=art==='slap';const s=ac.createBufferSource();s.buffer=ksBuf2(f*(pop?2:1),hold+0.5,pop?0.95:0.8,0.1);const g=ac.createGain();const amp=(pop?0.32:0.4)*a;g.gain.setValueAtTime(amp,t);g.gain.setValueAtTime(amp,t+Math.max(0.03,hold-0.15));g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.1);const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(pop?6000:slap?4000:2600,t);lp.frequency.exponentialRampToValueAtTime(600,t+0.3);artRate(s,t,hold,pop||slap?'none':art);s.connect(lp);lp.connect(g);g.connect(music);s.start(t);s.stop(t+hold+0.2);if(slap||pop)Nz(t,'bandpass',pop?3800:1800,1,(pop?0.2:0.14)*a,0.01,music);O('sine',f,t,Math.min(0.35,hold+0.1),0.22*a,music,f*0.75,0.3);return}
 if(fl==='wind'){const o=ac.createOscillator(),o2=ac.createOscillator(),g=ac.createGain();o.type='sine';o2.type='triangle';artFreq(o,f,t,hold,art);artFreq(o2,f*2,t,hold,art);const amp=0.18*a;g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(amp,t+0.06);g.gain.setValueAtTime(amp,t+Math.max(0.06,hold-0.12));g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.05);o.connect(g);const g2=ac.createGain();g2.gain.value=0.12;o2.connect(g2);g2.connect(g);g.connect(music);g.connect(send);o.start(t);o2.start(t);o.stop(t+hold+0.1);o2.stop(t+hold+0.1);Nz(t,'bandpass',Math.min(12000,f*2),8,0.06*a,Math.min(0.5,hold),music);return}
 if(fl==='brass'){const o=ac.createOscillator(),fl2=ac.createBiquadFilter(),g=ac.createGain();o.type='sawtooth';artFreq(o,f,t,hold,art);fl2.type='lowpass';fl2.frequency.setValueAtTime(300,t);fl2.frequency.exponentialRampToValueAtTime(3000,t+0.1);const amp=0.15*a;g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(amp,t+0.03);g.gain.setValueAtTime(amp,t+Math.max(0.03,hold-0.1));g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.05);o.connect(fl2);fl2.connect(g);g.connect(music);g.connect(send);o.start(t);o.stop(t+hold+0.1);return}
 if(fl==='keys'){const c=ac.createOscillator(),m=ac.createOscillator(),mg=ac.createGain(),g=ac.createGain();artFreq(c,f,t,hold,art);m.frequency.value=f*2;mg.gain.setValueAtTime(f*1.6,t);mg.gain.exponentialRampToValueAtTime(f*0.1,t+Math.max(0.3,hold));m.connect(mg);mg.connect(c.frequency);const amp=0.12*a;g.gain.setValueAtTime(amp,t);g.gain.exponentialRampToValueAtTime(amp*0.35,t+Math.max(0.2,hold));g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.4);c.connect(g);g.connect(music);g.connect(send);c.start(t);m.start(t);c.stop(t+hold+0.5);m.stop(t+hold+0.5);return}
 const o=ac.createOscillator(),lp=ac.createBiquadFilter(),g=ac.createGain();o.type='sawtooth';artFreq(o,f,t,hold,art);lp.type='lowpass';lp.frequency.setValueAtTime(4500,t);lp.frequency.exponentialRampToValueAtTime(1800,t+Math.max(0.3,hold));lp.Q.value=4;const amp=0.16*a;g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(amp,t+0.01);g.gain.setValueAtTime(amp,t+Math.max(0.02,hold-0.08));g.gain.exponentialRampToValueAtTime(0.0001,t+hold+0.05);o.connect(lp);lp.connect(g);g.connect(music);g.connect(send);o.start(t);o.stop(t+hold+0.1);}
/* plays one solo note with the sustain gene: decay kinds ring naturally and get cut when dead, hold/breath kinds follow the power curve, tremolo/arp re-trigger per step, feedback grows then squeals */
function soloPlay(x,t,nt,sd,dyn){const a=artEff(x,nt.art),L=noteLenEff(nt),row=nr(nt);dyn=dyn||1;
 if(a==='trem'||a==='arp'){for(let k=0;k<L;k++){const p=k?tickPow(x,k,a):1;if(p<=0)break;const rr=a==='arp'?Math.min(soloRows()-1,row+k):row;soloVoice(x,t+k*sd,rr,Math.max(0.12,sd*0.9),'none',dyn*(k?0.45+0.55*p:1))}return}
 const prof=susOf(x);let alive=L;for(let k=1;k<L;k++){if(tickPow(x,k,a)<=0){alive=k;break}}
 const hold=Math.max(0.12,alive*sd*0.95),bus=ac.createGain();bus.connect(music);const bm=music;music=bus;try{soloVoice(x,t,row,hold,a,dyn)}finally{music=bm}
 bus.gain.setValueAtTime(1,t);let last=1;if(prof.k!=='decay'||a==='fb'){for(let k=1;k<alive;k++){last=clamp(tickPow(x,k,a),0.05,1.2);bus.gain.linearRampToValueAtTime(last,t+k*sd)}}
 if(alive<L){bus.gain.setValueAtTime(last,t+alive*sd-0.01);bus.gain.linearRampToValueAtTime(0.0001,t+alive*sd+0.05);if(prof.k==='breath')Nz(t+alive*sd-0.06,'highpass',1500,0,0.07*dyn,0.1,music);
  if(a==='fb'){const f=soloFreq2(x,row),t16=t+16*sd,e2=t+L*sd+0.2,sq=ac.createOscillator(),sg=ac.createGain();sq.type='sine';sq.frequency.setValueAtTime(f*4,t16);sq.frequency.exponentialRampToValueAtTime(f*7,e2);sg.gain.setValueAtTime(0.0001,t16);sg.gain.exponentialRampToValueAtTime(0.09*dyn,t16+0.3);sg.gain.setValueAtTime(0.09*dyn,e2-0.15);sg.gain.exponentialRampToValueAtTime(0.0001,e2);sq.connect(sg);sg.connect(music);sq.start(t16);sq.stop(e2+0.05);Nz(t16,'highpass',3000,0,0.05*dyn,e2-t16,music)}}}
function duck(t){side.gain.setValueAtTime(1,t);side.gain.linearRampToValueAtTime(0.45,t+0.012);side.gain.linearRampToValueAtTime(1,t+0.22)}
/* ---- sampled instruments: General MIDI soundfonts (gleitz/midi-js-soundfonts, FluidR3_GM) loaded per instrument; any failure falls back to synthesis ---- */
function voice(x,t,v,s,solo,dyn){const a=(v===2?1.5:1)*(lvOf(x.id)>=25?1.1:1)*(solo?1.3:1)*(dyn||1);if(solo&&x.fam!=='vur')SOLO_F=soloFreq(solo.win,solo.pos,s);if(!solo&&sfVoice(x,t,a,s)){SOLO_F=0;return}try{GEN[x.v.g](t,a,x.v,s)}catch(e){}SOLO_F=0;if(lvOf(x.id)>=25&&x.fam==='vur'&&x.v.g==='kick')O('sine',55,t,0.4,0.2*a,drum)}
function playStep(s,pk,t,b,k){const p=S.pat[pk],sa=soloActive(b),pa=planAt(b),dyn=dynAt(b);k=k||1;CUR_B=b;const fb=k===1&&fillBar(b);if(k===1&&s===0&&pa.barIn===0&&b>0&&fillBar(b-1)&&fillHits()>=4)crashVoice(t,0.9*dyn);for(let i=0;i<S.slots.length;i++){const x=slotIns(i);if(!x)continue;if(needleOf(i)!==k)continue;if(muteUntil[i]>t)continue;if(pa.sec.solo&&isSolo(i)){const dp=duetPart(i);if(dp<0&&sa!==i)continue;if(x.fam!=='vur'&&hasSoloNotes(i)){const sd=60/curBpm(b)/4,off=(pa.barIn%2)*MI.N+s;if(!duetPlays(i,off))continue;soloNotesOf(i).forEach(nt=>{if(nt.t!==off)return;soloPlay(x,t,nt,sd,dyn*(dp>=0?1.1:1))});continue}const vs=S.pat.S[i][s];if(!vs)continue;voice(x,t,vs,s,{win:Math.floor(b/SEC_BARS),pos:pa.barIn},dyn);continue}const v=(fb&&fillZone(s)&&x.fam==='vur')?S.pat.F[i][s]:p[i][s];if(!v)continue;if(!allowed(pa.sec,x,i))continue;voice(x,t,v,s,null,dyn);if(x.id==='davul'&&S.up.side)duck(t)}}

let playing=false,timer=0,nextT=0,step=0,bar=0,queue=[],grid=[],beats=[],hitBar=false,playPk='A',lastLogic=0;
const NS=[null,{nextT:0,step:0,grid:[]},{nextT:0,step:0,grid:[]}];
const muteUntil=Array(MAXSLOTS).fill(0);
const nowT=()=>ac?ac.currentTime:0;
function sched(){
 const sd0=60/S.bpm/4,now=ac.currentTime;const sd=sd0;
 if(now-nextT>0.25){const miss=Math.floor((now-nextT)/sd);earn(rate()*miss*sd);const tot=step+miss;bar+=Math.floor(tot/MI.N);step=tot%MI.N;nextT+=miss*sd}
 while(nextT<now+0.12){
  if(step>=MI.N){step=0;bar++}
  const sdb=60/curBpm(bar)/4;const s=step,pk=pkFor(bar),tp=nextT+((s%2===1&&S.up.swing)?sdb*0.2:0);
  playStep(s,pk,tp,bar);queue.push({s,pk,t:tp,b:bar});grid.push({s,t:nextT,sd:sdb,N:MI.N});
  if(MI.gsSet.has(s)){beats.push(nextT);if(beats.length>10)beats.shift()}
  nextT+=sdb;step++;if(step>=MI.N){step=0;bar++}
 }
 for(let k=2;k<=3;k++){if(!needleOn(k))continue;const nd=NS[k-1],spec=NEEDLES[k-1];if(now-nd.nextT>0.25){nd.nextT=now+0.02}
  while(nd.nextT<now+0.12){const sdk=60/curBpm(bar)/4/spec.speed;const cell=spec.dir>0?nd.step%MI.N:(MI.N-1-nd.step%MI.N);const pk=pkFor(bar);playStep(cell,pk,nd.nextT,bar,k);queue.push({s:cell,pk,t:nd.nextT,b:bar,k});nd.grid.push({s:cell,t:nd.nextT,sd:sdk,N:MI.N,dir:spec.dir});nd.nextT+=sdk;nd.step++}}
 logic(now);
}
/* şarkıyı başa sar: örnek şarkı, albüm, turne, kayıt yükleme ve sıfırlamada */
function songRewind(){step=0;bar=0;NS[1].step=0;NS[2].step=0}
function startStop(){
 ensureAudio();
 if(playing){playing=false;clearInterval(timer);queue=[];msg('Ateşkes: kuşatma durdu, döngü sustu')}
 else{playing=true;const now=ac.currentTime;nextT=now+0.06;step=step%MI.N;queue=[];grid=[];beats=[];lastLogic=now;NS[1].nextT=now+0.06;NS[1].grid=[];NS[2].nextT=now+0.06;NS[2].grid=[];if(!wave||wave.n!==S.wave||wave.stale)startWave(S.wave,now);else{const pa=wave.pausedAt||now,sh=now-pa;wave.startT+=sh;if(wave.done)wave.nextAt+=sh;enemies.forEach(e=>{if(e.lastSp)e.lastSp+=sh})}timer=setInterval(sched,25);sched()}
 if(!playing&&wave){wave.pausedAt=ac.currentTime}
 $('play').textContent=T(playing?'Durdur':'Başlat');
}
let tapFx=null,tapP=0,kickP=0,bassP=0;
function tap(){
 if(!playing){msg('Önce ortadaki ▶ ile müziği başlat');return}
 const now=ac.currentTime-(ac.outputLatency||ac.baseLatency||0);
 let best=null;for(const b of beats)if(best===null||Math.abs(now-b)<Math.abs(now-best))best=b;
 if(best===null)return;const d=now-best;
 if(Math.abs(d)<0.085){S.seri++;hitBar=true;const g=Math.max(5,rate()*0.6);earn(g);tapFx={t:'Tam',c:dispTheme().cv.acc,life:1,sub:'+♪ '+fmt(g)};tapP=1}
 else{S.seri=0;tapFx={t:d<0?'Erken':'Geç',c:dispTheme().cv.hot,life:1,sub:'seri sıfırlandı'};tapP=0.6}
 updUI();
}
