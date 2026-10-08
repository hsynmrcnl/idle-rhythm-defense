/* ================= canvas + WebGL ================= */
const view=$('cv');
let gl=null;try{gl=view.getContext('webgl',{premultipliedAlpha:false,antialias:false,alpha:false})}catch(e){gl=null}
let scene=gl?document.createElement('canvas'):view;
let ctx=scene.getContext('2d');
let L=600,DPR=1,W=600,phase=0,phase2=0,phase3=0,clock=0,dotRot=0,rot=0,dirS=1,hover=null,bgKey='',bgCv=null;
const flash=Array.from({length:MAXSLOTS},()=>new Float32Array(18));
const parts=[],waves=[],stars=[];
for(let k=0;k<64;k++)stars.push({x:Math.random()*2.2-1.1,y:Math.random()*2.2-1.1,vx:(Math.random()-0.5)*0.035,vy:(Math.random()-0.5)*0.035});
const CN=72,HALF=36,peaks=new Float32Array(CN),SK=48,skPeaks=new Float32Array(SK),crownCache={},wv=new Float32Array(201);
const VS='attribute vec2 p;varying vec2 vUv;void main(){vUv=p*0.5+0.5;gl_Position=vec4(p,0.0,1.0);}';
const PREC='#ifdef GL_FRAGMENT_PRECISION_HIGH\nprecision highp float;\n#else\nprecision mediump float;\n#endif\n';
const FS_BLUR=PREC+'varying vec2 vUv;uniform sampler2D t;uniform vec2 dir;uniform float th;vec3 S(vec2 uv){vec3 c=texture2D(t,uv).rgb;if(th>0.0){float l=max(c.r,max(c.g,c.b));c*=smoothstep(th,th+0.35,l);}return c;}void main(){vec3 c=S(vUv)*0.227;c+=(S(vUv+dir*1.385)+S(vUv-dir*1.385))*0.316;c+=(S(vUv+dir*3.231)+S(vUv-dir*3.231))*0.07;gl_FragColor=vec4(c,1.0);}';
const FS_TRAIL=PREC+'varying vec2 vUv;uniform sampler2D s;uniform sampler2D pv;uniform float k;void main(){vec3 a=texture2D(s,vUv).rgb;vec3 b=texture2D(pv,vUv).rgb*k;gl_FragColor=vec4(max(a,b),1.0);}';
const FS_COMP=PREC+[
'varying vec2 vUv;uniform sampler2D s;uniform sampler2D bl;',
'uniform float time,kick,bloomK,ca,scan,crt,glitch,grain,htone,mis,vign,dust,warm,sat,kaleid;',
'uniform vec3 paper,ink,dustCol;',
'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
'void main(){',
' vec2 uv=vUv;vec2 cc=uv-0.5;uv=0.5+cc*(1.0+crt*dot(cc,cc)*1.6);',
' float edge=step(0.0,uv.x)*step(uv.x,1.0)*step(0.0,uv.y)*step(uv.y,1.0);',
' float gsh=0.0;',
' if(glitch>0.0){float band=floor(uv.y*28.0);float tk=floor(time*14.0);float n=h(vec2(band,tk));float on=step(1.0-glitch*(0.05+kick*0.5),n);gsh=on*(h(vec2(band*3.1,tk))-0.5)*0.09*glitch;uv.x+=gsh;}',
' vec2 d=uv-0.5;float a=ca*(0.003+kick*0.009)+abs(gsh)*0.35;',
' vec3 col=vec3(texture2D(s,uv+d*a*2.0).r,texture2D(s,uv).g,texture2D(s,uv-d*a*2.0).b);',
' if(kaleid>0.0){vec2 k=uv-0.5;float ang=atan(k.y,k.x);float r=length(k);float n=floor(3.0+kaleid*5.0);float seg=6.2831853/n;ang=mod(ang+time*0.05,seg);ang=abs(ang-seg*0.5);vec2 ku=0.5+vec2(cos(ang),sin(ang))*r;vec3 kc=texture2D(s,ku).rgb;col=mix(col,max(col,kc),kaleid*0.6);}',
' col+=texture2D(bl,uv).rgb*bloomK*(1.0+kick*0.7);',
' if(htone>0.0){',
'  vec3 sm=texture2D(s,uv+vec2(mis*0.007,-mis*0.005)).rgb;',
'  float lum=dot(col,vec3(0.299,0.587,0.114));',
'  float sat0=max(col.r,max(col.g,col.b))-min(col.r,min(col.g,col.b));',
'  float satM=max(sm.r,max(sm.g,sm.b))-min(sm.r,min(sm.g,sm.b));',
'  float inkv=clamp((1.0-lum)*(1.0-sat0*1.5),0.0,1.0);',
'  float cell=mix(3.0,6.5,htone);',
'  vec2 q=vec2(gl_FragCoord.x+gl_FragCoord.y,gl_FragCoord.x-gl_FragCoord.y)*0.7071/cell;',
'  float dd=length(fract(q)-0.5);float rr=sqrt(inkv)*0.62;',
'  float dotm=1.0-smoothstep(rr-0.07,rr+0.07,dd);',
'  float kk=max(dotm,smoothstep(0.55,0.72,inkv));',
'  vec3 pap=paper*(0.93+0.07*h(floor(gl_FragCoord.xy/2.0)));',
'  vec3 outc=mix(pap,ink,kk);',
'  vec3 spot=clamp(floor(sm*3.0+0.5)/3.0,0.0,1.0);',
'  outc=mix(outc,outc*spot,smoothstep(0.22,0.42,satM));',
'  col=mix(col,outc,clamp(htone,0.0,1.0));',
' }',
' float l=dot(col,vec3(0.299,0.587,0.114));col=mix(vec3(l),col,sat);',
' col*=vec3(1.0+warm*0.14,1.0+warm*0.03,1.0-warm*0.18);',
' col*=1.0-scan*0.4*(0.5+0.5*sin(gl_FragCoord.y*2.6));',
' if(dust>0.0){float t2=floor(time*16.0);float sp=h(floor(gl_FragCoord.xy/3.0)+t2*7.13);col=mix(col,dustCol,step(1.0-0.0025*dust,sp)*0.8);',
'  float sx=h(vec2(t2,4.2));float sOn=step(0.82,h(vec2(t2,9.1)));float sy=h(vec2(t2,2.7));col=mix(col,dustCol,sOn*dust*0.5*(1.0-smoothstep(0.0,0.0015,abs(vUv.x-sx)))*(1.0-smoothstep(0.08,0.2,abs(vUv.y-sy))));}',
' col+=(h(gl_FragCoord.xy+fract(time)*91.7)-0.5)*grain*0.28;',
' col*=1.0-vign*smoothstep(0.3,0.95,length(vUv-0.5)*1.35);',
' gl_FragColor=vec4(col*edge,1.0);',
'}'].join('\n');
let GLX=null;
if(gl){try{GLX=(()=>{
 function sh(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s}
 function prog(fs){const p=gl.createProgram();gl.attachShader(p,sh(gl.VERTEX_SHADER,VS));gl.attachShader(p,sh(gl.FRAGMENT_SHADER,fs));gl.bindAttribLocation(p,0,'p');gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(p));const u={};const n=gl.getProgramParameter(p,gl.ACTIVE_UNIFORMS);for(let k=0;k<n;k++){const inf=gl.getActiveUniform(p,k);u[inf.name]=gl.getUniformLocation(p,inf.name)}return{p,u}}
 const pb=prog(FS_BLUR),pt=prog(FS_TRAIL),pc=prog(FS_COMP);
 const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,2,gl.FLOAT,false,0,0);
 function tex(w,h){const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);if(w)gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,null);return t}
 function fbo(w,h){const t=tex(w,h),f=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,f);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,t,0);gl.bindFramebuffer(gl.FRAMEBUFFER,null);return{t,f,w,h}}
 const sceneT=tex(0,0);let sz=0,tr=[],bA=null,bB=null,clearTrail=true;
 function ensure(w){if(w===sz)return;sz=w;[...tr,bA,bB].forEach(o=>{if(o){gl.deleteTexture(o.t);gl.deleteFramebuffer(o.f)}});tr=[fbo(w,w),fbo(w,w)];const q=Math.max(16,Math.round(w/4));bA=fbo(q,q);bB=fbo(q,q);clearTrail=true}
 function bind(unit,t){gl.activeTexture(gl.TEXTURE0+unit);gl.bindTexture(gl.TEXTURE_2D,t)}
 function pass(target,w){gl.bindFramebuffer(gl.FRAMEBUFFER,target?target.f:null);gl.viewport(0,0,w,w);gl.drawArrays(gl.TRIANGLES,0,6)}
 const v3=hx=>rgbOf(hx).map(x=>x/255);
 return{render(src,fx,time,kick,th){
  const w=src.width;ensure(w);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);bind(0,sceneT);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,src);
  let base=sceneT;
  if(fx.trail>0.01){
   if(clearTrail){tr.forEach(o=>{gl.bindFramebuffer(gl.FRAMEBUFFER,o.f);gl.clearColor(0,0,0,1);gl.clear(gl.COLOR_BUFFER_BIT)});clearTrail=false}
   gl.useProgram(pt.p);bind(0,sceneT);bind(1,tr[0].t);gl.uniform1i(pt.u.s,0);gl.uniform1i(pt.u.pv,1);gl.uniform1f(pt.u.k,fx.trail*0.92);pass(tr[1],w);tr.reverse();base=tr[0].t;
  }else clearTrail=true;
  let bloomT=base;
  if(fx.bloom>0.01){
   gl.useProgram(pb.p);gl.uniform1i(pb.u.t,0);const q=bA.w;
   bind(0,base);gl.uniform2f(pb.u.dir,1.6/q,0);gl.uniform1f(pb.u.th,th.light?0.9:0.42);pass(bA,q);
   bind(0,bA.t);gl.uniform2f(pb.u.dir,0,1.6/q);gl.uniform1f(pb.u.th,0);pass(bB,q);
   bind(0,bB.t);gl.uniform2f(pb.u.dir,3.4/q,0);pass(bA,q);
   bind(0,bA.t);gl.uniform2f(pb.u.dir,0,3.4/q);pass(bB,q);
   bloomT=bB.t;
  }
  gl.useProgram(pc.p);bind(0,base);bind(1,bloomT);const U=pc.u;
  gl.uniform1i(U.s,0);gl.uniform1i(U.bl,1);
  gl.uniform1f(U.time,time);gl.uniform1f(U.kick,kick);gl.uniform1f(U.bloomK,fx.bloom>0.01?fx.bloom:0);
  [['ca','ca'],['scan','scan'],['crt','crt'],['glitch','glitch'],['grain','grain'],['half','htone'],['mis','mis'],['vign','vign'],['dust','dust'],['warm','warm'],['sat','sat'],['kaleid','kaleid']].forEach(([k,u])=>{if(U[u])gl.uniform1f(U[u],fx[k]||0)});
  gl.uniform3fv(U.paper,v3(th.cv.bg));gl.uniform3fv(U.ink,v3(th.cv.ink));gl.uniform3fv(U.dustCol,v3(th.cv.ink));
  pass(null,view.width);
 }}
})()}catch(err){console.warn('WebGL kapalı:',err);GLX=null}}
if(gl&&!GLX){const c2=document.createElement('canvas');c2.id='cv';c2.setAttribute('aria-label',view.getAttribute('aria-label'));view.replaceWith(c2);scene=c2;ctx=c2.getContext('2d')}
const vis=()=>GLX?view:scene;
const PH=()=>L<480;let lowQ=false,slowT=0;
function resize(){const el=vis();const w=el.getBoundingClientRect().width||600;L=w;DPR=Math.min(GLX?(w<480?1.25:1.5):2,window.devicePixelRatio||1);W=Math.max(64,Math.round(w*DPR));el.width=W;el.height=W;if(scene!==el){scene.width=W;scene.height=W}bgKey=''}
if(window.ResizeObserver)new ResizeObserver(resize).observe(vis());else window.addEventListener('resize',resize);
resize();

function geom(){const R=L/2,ns=S.slots.length;if(S.layout==='strip'){const x0=0.17*L,x1=0.96*L,gridTop=0.6*L,rowH=Math.min(0.36*L/ns,0.05*L),colW=(x1-x0)/MI.N;return{layout:'strip',R,c:R,r0:0.15*R,x0,x1,gridTop,rowH,gridH:rowH*ns,colW,fieldTop:-0.04*L}}const ph=PH(),rIn=(ph?0.15:0.2)*R,rOut=0.74*R;return{layout:'circle',R,c:R,r0:(ph?0.13:0.15)*R,rIn,rOut,t:(rOut-rIn)/ns}}
const SEG=()=>TAU/MI.N;
function cellAng(s){const sg=SEG(),A0=-Math.PI/2+dirS*s*sg+rot,A1=A0+dirS*sg,gp=Math.min(0.022,sg*0.12);return[Math.min(A0,A1)+gp,Math.max(A0,A1)-gp]}
const midAng=s=>-Math.PI/2+dirS*(s+0.5)*SEG()+rot;
function cellPath(c,ri,ro,a0,a1){ctx.beginPath();ctx.arc(c,c,ro,a0,a1);ctx.arc(c,c,ri,a1,a0,true);ctx.closePath()}
function cellPos(si,s,g){if(g.layout==='strip')return[g.x0+(s+0.5)*g.colW,g.gridTop+(si+0.5)*g.rowH];const r=g.rIn+(si+0.5)*g.t,a=midAng(s);return[g.c+Math.cos(a)*r,g.c+Math.sin(a)*r]}
function enemyPos(e,g){if(g.layout==='strip')return[g.x0+e.a*(g.x1-g.x0),g.fieldTop+(1-e.d)*(g.gridTop-g.fieldTop)];const r=g.r0+e.d*(1.02*g.R-g.r0),a=e.a*TAU-Math.PI/2;return[g.c+Math.cos(a)*r,g.c+Math.sin(a)*r]}
function corePos(g){return g.layout==='strip'?[g.c,g.gridTop]:[g.c,g.c]}
function spawnPart(si,s){
 if(RM||parts.length>280)return;const th=dispTheme(),g=geom(),x=slotIns(si);if(!x)return;const [px,py]=cellPos(si,s,g);const ang=g.layout==='strip'?-Math.PI/2:midAng(s);
 const n=th.part==='splat'?4:th.part==='dust'?1:3,col=insColor(x,th);
 for(let k=0;k<n;k++){const sp=(th.part==='dust'?0.02:0.08+Math.random()*0.14)*L*0.5,a=ang+(Math.random()-0.5)*(th.part==='splat'?1.4:0.6);parts.push({x:px,y:py,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp-(th.part==='dust'?8:0),life:1,col:th.part==='splat'?(Math.random()<0.5?th.cv.ink:th.cv.acc):col,sz:th.part==='splat'?1.5+Math.random()*3.5:th.part==='dust'?1.2+Math.random()*1.5:1.1})}
}
function spawnDeath(e){if(RM||parts.length>280)return;const th=dispTheme(),g=geom(),[x,y]=enemyPos(e,g),col=e.boss?th.en.boss:th.en.body;const n=e.boss?24:8;for(let k=0;k<n;k++){const a=Math.random()*TAU,sp=(0.05+Math.random()*0.12)*L*0.5;parts.push({x,y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,life:1,col,sz:e.boss?2.5:1.6})}}

function paintBg(b,th,g){
 const {R,c}=g,r=rng(7);b.fillStyle=th.cv.bg;b.fillRect(0,0,L,L);
 if(th.id==='neon'){const gr=b.createRadialGradient(c,c,0,c,c,R*1.1);gr.addColorStop(0,'rgba(139,107,255,0.07)');gr.addColorStop(1,'rgba(139,107,255,0)');b.fillStyle=gr;b.fillRect(0,0,L,L)}
 else if(th.id==='cyber'){
  const s=L/24,hh=s*Math.sqrt(3)/2;b.strokeStyle='rgba(5,217,232,0.07)';b.lineWidth=1;
  for(let y=-1;y<L/hh+1;y++)for(let x=-1;x<L/(s*1.5)+1;x++){const cx=x*s*1.5,cy=y*hh*2+(x%2?hh:0);b.beginPath();for(let k=0;k<6;k++){const a=k*Math.PI/3;b.lineTo(cx+Math.cos(a)*s*0.5,cy+Math.sin(a)*s*0.5)}b.closePath();b.stroke()}
  b.strokeStyle='rgba(252,238,10,0.55)';b.lineWidth=1.5;const m=10,k=26;
  [[m,m,1,1],[L-m,m,-1,1],[m,L-m,1,-1],[L-m,L-m,-1,-1]].forEach(([x,y,sx,sy])=>{b.beginPath();b.moveTo(x,y+sy*k);b.lineTo(x,y);b.lineTo(x+sx*k,y);b.stroke()});
 }
 else if(th.id==='punk'){
  for(let i=0;i<900;i++){b.fillStyle='rgba(0,0,0,'+(r()*0.12)+')';b.fillRect(r()*L,r()*L,r()*1.6,r()*1.6)}
  const blocks=[['#ff2e88',0.06,0.08,0.3,0.18,-0.12],['#2b59ff',0.7,0.78,0.26,0.16,0.08],['#ff2e88',0.74,0.06,0.2,0.12,0.2],['#c9c1ad',0.04,0.74,0.3,0.2,0.05]];
  blocks.forEach(([col,x,y,w,h,a])=>{b.save();b.translate(x*L+w*L/2,y*L+h*L/2);b.rotate(a);b.fillStyle=col;b.globalAlpha=col==='#c9c1ad'?0.8:0.85;b.fillRect(-w*L/2,-h*L/2,w*L,h*L);if(col==='#c9c1ad'){b.fillStyle='rgba(17,17,17,0.55)';for(let l=0;l<6;l++)b.fillRect(-w*L/2+8,-h*L/2+8+l*h*L/7,w*L*(0.5+r()*0.4),2)}b.restore()});
  b.save();b.translate(L*0.5,L*0.53);b.rotate(-0.12);b.globalAlpha=0.08;b.fillStyle='#111';b.font=Math.round(L*0.24)+'px '+th.font.d;b.textAlign='center';b.textBaseline='middle';b.fillText('NABIZ',0,0);b.restore();
  b.globalAlpha=0.55;b.fillStyle='#d8cfb5';[[0.12,0.2,0.5],[0.82,0.66,-0.6]].forEach(([x,y,a])=>{b.save();b.translate(x*L,y*L);b.rotate(a);b.fillRect(-L*0.07,-L*0.018,L*0.14,L*0.036);b.restore()});b.globalAlpha=1;
 }
 else if(th.id==='lofi'){
  const gr=b.createRadialGradient(L*0.1,L*0.08,0,L*0.1,L*0.08,L*0.8);gr.addColorStop(0,'rgba(244,162,89,0.22)');gr.addColorStop(1,'rgba(244,162,89,0)');b.fillStyle=gr;b.fillRect(0,0,L,L);
  b.fillStyle='rgba(90,120,170,0.08)';b.fillRect(L*0.74,L*0.04,L*0.22,L*0.28);b.strokeStyle='rgba(243,227,201,0.12)';b.lineWidth=2;b.strokeRect(L*0.74,L*0.04,L*0.22,L*0.28);b.beginPath();b.moveTo(L*0.85,L*0.04);b.lineTo(L*0.85,L*0.32);b.moveTo(L*0.74,L*0.18);b.lineTo(L*0.96,L*0.18);b.stroke();
  b.fillStyle='rgba(0,0,0,0.25)';b.fillRect(0,L*0.93,L,L*0.07);
 }
 else if(th.id==='synth'){
  const sy=g.layout==='strip'?0.3*L:0.34*L,sr=0.26*L;const gr=b.createLinearGradient(0,sy-sr,0,sy+sr);gr.addColorStop(0,'#ffd166');gr.addColorStop(0.55,'#ff6ec7');gr.addColorStop(1,'#7b61ff');
  b.save();b.beginPath();b.arc(c,sy,sr,0,TAU);b.clip();b.fillStyle=gr;b.globalAlpha=0.38;b.fillRect(0,0,L,L);b.fillStyle=th.cv.bg;b.globalAlpha=0.9;for(let k=0;k<7;k++){const yy=sy+sr*0.1+k*sr*0.13;b.fillRect(0,yy,L,2+k*1.6)}b.restore();
  const hz=g.layout==='strip'?0.62*L:0.56*L;b.strokeStyle='rgba(0,229,255,0.18)';b.lineWidth=1;
  for(let k=-10;k<=10;k++){b.beginPath();b.moveTo(c+k*L*0.06,hz);b.lineTo(c+k*L*0.4,L);b.stroke()}
  for(let k=0;k<10;k++){const t=k/10,yy=hz+(L-hz)*t*t;b.beginPath();b.moveTo(0,yy);b.lineTo(L,yy);b.stroke()}
  b.fillStyle='rgba(18,10,42,0)';
 }
 else if(th.id==='anadolu'){
  const cols=['#ef476f','#ffb703','#06d6a0','#8338ec'];b.globalAlpha=0.18;
  for(let k=0;k<4;k++){const inset=12+k*14;b.strokeStyle=cols[k];b.lineWidth=6;b.setLineDash([14,10]);b.strokeRect(inset,inset,L-2*inset,L-2*inset)}b.setLineDash([]);
  b.globalAlpha=0.12;for(let y=0;y<L;y+=L/8)for(let x=0;x<L;x+=L/8){const d=L/16;b.fillStyle=cols[Math.floor(r()*4)];b.beginPath();b.moveTo(x+d,y);b.lineTo(x+2*d,y+d);b.lineTo(x+d,y+2*d);b.lineTo(x,y+d);b.closePath();b.fill()}
  b.globalAlpha=1;
 }
}
function drawBg(th,g){const key=th.id+':'+g.layout+':'+W+':'+S.slots.length;if(key!==bgKey||!bgCv){bgKey=key;bgCv=document.createElement('canvas');bgCv.width=W;bgCv.height=W;const b=bgCv.getContext('2d');b.setTransform(DPR,0,0,DPR,0,0);paintBg(b,th,g)}ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(bgCv,0,0);ctx.restore()}

function drawStars(dt,g,th){
 const {R,c}=g,thr=0.28*R,th2=thr*thr,k=1+bassP*0.035,col=th.light?th.cv.ink:th.cv.acc;
 const P=stars.map(p=>{if(!RM){p.x+=p.vx*dt;p.y+=p.vy*dt;if(p.x>1.1)p.x=-1.1;if(p.x<-1.1)p.x=1.1;if(p.y>1.1)p.y=-1.1;if(p.y<-1.1)p.y=1.1}return[c+p.x*R*k,c+p.y*R*k]});
 ctx.lineWidth=0.7;
 for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const dx=P[i][0]-P[j][0],dy=P[i][1]-P[j][1],d2=dx*dx+dy*dy;if(d2<th2){ctx.strokeStyle=hexA(col,((1-Math.sqrt(d2)/thr)*(0.14+0.24*bassP)).toFixed(3));ctx.beginPath();ctx.moveTo(P[i][0],P[i][1]);ctx.lineTo(P[j][0],P[j][1]);ctx.stroke()}}
 ctx.fillStyle=hexA(col,0.7);for(const p of P){ctx.beginPath();ctx.arc(p[0],p[1],1.3,0,TAU);ctx.fill()}
}
function drawTunnel(dt,g,th){
 const {R,c}=g;
 for(let w=waves.length-1;w>=0;w--){const o=waves[w];o.r+=dt*0.42*R;o.a-=dt*1.1;if(o.a<=0||o.r>R*1.05){waves.splice(w,1);continue}
  ctx.lineWidth=th.light?3:2;ctx.strokeStyle=hexA(th.cv.hot,(o.a*0.6).toFixed(3));
  if(g.layout==='strip'){const y=g.gridTop-o.r*0.9;ctx.beginPath();ctx.moveTo(g.x0,y);ctx.lineTo(g.x1,y);ctx.stroke();continue}
  const rr=g.rOut+4+o.r;
  for(let k=0;k<3;k++){const s=o.rot+k*TAU/3;ctx.beginPath();ctx.arc(c,c,rr,s,s+TAU/3*0.62);ctx.stroke()}
  ctx.fillStyle=hexA(th.light?th.cv.ink:th.cv.hot,(o.a*0.5).toFixed(3));
  for(let k=0;k<60;k++){const a=k*TAU/60;ctx.fillRect(c+Math.cos(a)*(rr+7)-1,c+Math.sin(a)*(rr+7)-1,2,2)}
 }
}
function crownCols(th){if(crownCache[th.id])return crownCache[th.id];const st=[rgbOf(th.fam.tel),rgbOf(th.fam.vur),rgbOf(th.fam.dun)],out=[];for(let k=0;k<HALF;k++){const t=k/(HALF-1),a=t<0.5?st[0]:st[1],b=t<0.5?st[1]:st[2],u=t<0.5?t*2:(t-0.5)*2;out.push('rgb('+a.map((v,j)=>Math.round(v+(b[j]-v)*u)).join(',')+')')}return crownCache[th.id]=out}
function drawWall(dt,g,th){
 const live=playing&&analyser;if(live)analyser.getByteFrequencyData(fData);
 const ca=rgbOf(th.cv.acc),cb=rgbOf(th.cv.hot),dots=96;
 ctx.lineCap='round';
 if(g.layout==='strip'){
  const {x0,x1,gridTop}=g,bw=(x1-x0)/WN,maxH=0.3*L;
  ctx.fillStyle=hexA(th.cv.ink,0.5);for(let k=0;k<dots;k++){const x=x0+(k+0.5)/dots*(x1-x0);ctx.fillRect(x-0.7,gridTop-12,1.4,1.4)}
  for(let k=0;k<WN;k++){const E=Math.min(1.6,wallE[k]),sh=live?fData[Math.floor(4+Math.pow(k<WN/2?k:WN-1-k,1.5))%fData.length]/255*0.08:0,h=(Math.min(1,E)*maxH)+sh*maxH;if(h<1)continue;const x=x0+(k+0.5)*bw,t=Math.min(1,E);ctx.strokeStyle='rgb('+ca.map((q,j)=>Math.round(q+(cb[j]-q)*t)).join(',')+')';ctx.lineWidth=1.3;ctx.globalAlpha=0.95;
   [[-0.32,0.62],[0,1],[0.32,0.62]].forEach(([o,f])=>{ctx.beginPath();ctx.moveTo(x+o*bw,gridTop-12);ctx.lineTo(x+o*bw,gridTop-12-h*f);ctx.stroke()})}
  ctx.globalAlpha=1;ctx.lineCap='butt';return;
 }
 const {R,c,rOut}=g,rb=rOut+0.012*R,maxL=0.27*R;
 ctx.fillStyle=hexA(th.cv.ink,0.5);for(let k=0;k<dots;k++){const a=k/dots*TAU;ctx.beginPath();ctx.arc(c+Math.cos(a)*rb,c+Math.sin(a)*rb,0.8,0,TAU);ctx.fill()}
 for(let k=0;k<WN;k++){const E=Math.min(1.6,wallE[k]),sh=live?fData[Math.floor(4+Math.pow(k<WN/2?k:WN-1-k,1.5))%fData.length]/255*0.08:0,len=Math.min(1,E)*maxL+sh*maxL;if(len<1)continue;const ang=(k+0.5)/WN*TAU-Math.PI/2,t=Math.min(1,E),da=TAU/WN*0.3;ctx.strokeStyle='rgb('+ca.map((q,j)=>Math.round(q+(cb[j]-q)*t)).join(',')+')';ctx.lineWidth=1.3;ctx.globalAlpha=0.95;
  [[-da,0.62],[0,1],[da,0.62]].forEach(([o,f])=>{const cs=Math.cos(ang+o),sn=Math.sin(ang+o);ctx.beginPath();ctx.moveTo(c+cs*rb,c+sn*rb);ctx.lineTo(c+cs*(rb+len*f),c+sn*(rb+len*f));ctx.stroke()})}
 ctx.globalAlpha=1;ctx.lineCap='butt';
}
function fillWv(live){const n=200;if(live)analyser.getFloatTimeDomainData(tData);for(let k=0;k<=n;k++){const w=Math.min(1,k/14,(n-k)/14),v=live?tData[Math.floor(k/n*(tData.length-1))]:0;wv[k]=clamp(v*2.4,-1,1)*w}}
function drawWave(g,th){
 const live=playing&&analyser,n=200;fillWv(live);
 let stroke=th.light?th.cv.ink:th.cv.acc;
 if(g.layout==='strip'){const y=0.3*L,amp=0.05*L;if(!th.light){const gr=ctx.createLinearGradient(g.x0,0,g.x1,0);gr.addColorStop(0,th.cv.hot);gr.addColorStop(0.5,th.cv.acc);gr.addColorStop(1,th.cv.hot);stroke=gr}ctx.strokeStyle=stroke;[[1,1,1.6],[-1,0.35,1]].forEach(([sg,al,lw])=>{ctx.globalAlpha=al;ctx.lineWidth=lw;ctx.beginPath();for(let k=0;k<=n;k++){const x=g.x0+k/n*(g.x1-g.x0),yy=y+sg*wv[k]*amp;if(k)ctx.lineTo(x,yy);else ctx.moveTo(x,yy)}ctx.stroke()});ctx.globalAlpha=1;return}
 const {R,c}=g,base=0.835*R,amp=0.055*R;
 if(!th.light&&ctx.createConicGradient){const gr=ctx.createConicGradient(-Math.PI/2,c,c);gr.addColorStop(0,th.cv.hot);gr.addColorStop(0.5,th.cv.acc);gr.addColorStop(1,th.cv.hot);stroke=gr}
 ctx.strokeStyle=stroke;
 [[1,1,th.light?2.2:1.6],[-1,0.35,1]].forEach(([sg,al,lw])=>{ctx.globalAlpha=al;ctx.lineWidth=lw;ctx.beginPath();for(let k=0;k<=n;k++){const ang=-Math.PI/2+k/n*TAU,rr=base+sg*wv[k]*amp,x=c+Math.cos(ang)*rr,y=c+Math.sin(ang)*rr;if(k)ctx.lineTo(x,y);else ctx.moveTo(x,y)}ctx.stroke()});
 ctx.globalAlpha=1;
}
function drawMirror(g,th){
 const live=playing&&analyser;if(live)analyser.getByteFrequencyData(fData);
 const n=40,cy=g.layout==='strip'?0.12*L:0.955*L,amp=g.layout==='strip'?0.07*L:0.04*L,x0=g.layout==='strip'?g.x0:0.1*L,x1=g.layout==='strip'?g.x1:0.9*L,bw=(x1-x0)/n;
 const ca=rgbOf(th.cv.hot),cb=rgbOf(th.cv.acc);
 for(let k=0;k<n;k++){const kk=k<n/2?k:n-1-k,bin=Math.floor(2+Math.pow(kk/(n/2),1.5)*160),v=live?fData[bin]/255:0,h=Math.max(1.5,Math.pow(v,1.4)*amp),t=k/(n-1);ctx.fillStyle='rgb('+ca.map((q,j)=>Math.round(q+(cb[j]-q)*t)).join(',')+')';ctx.globalAlpha=0.85;ctx.fillRect(x0+k*bw+1,cy-h,bw-2,h*2)}
 ctx.globalAlpha=1;
}
function drawTower(dt,g,th){
 const live=playing&&analyser;if(live)analyser.getByteFrequencyData(fData);
 const [cx,cy]=corePos(g),n=16,w=g.layout==='strip'?0.09*L:0.1*L,bw=w/n,top=g.layout==='strip'?0.06*L:0.08*L,maxH=cy-top;
 const ca=rgbOf(th.cv.hot),cb=rgbOf(th.cv.acc);
 ctx.strokeStyle=hexA(th.cv.acc,0.35);ctx.lineWidth=1;for(let k=1;k<=4;k++){ctx.beginPath();ctx.ellipse(cx,cy,w*0.5+k*w*0.35*(1+kickP*0.2),(w*0.5+k*w*0.35)*0.32,0,0,TAU);ctx.stroke()}
 for(let k=0;k<n;k++){const kk=k<n/2?k:n-1-k,bin=Math.floor(2+Math.pow(kk/(n/2),1.4)*120),v=live?fData[bin]/255:0,h=Math.pow(v,1.3)*maxH,t=1-h/maxH;ctx.fillStyle='rgb('+cb.map((q,j)=>Math.round(q+(ca[j]-q)*clamp(1-t,0,1))).join(',')+')';ctx.globalAlpha=0.6;ctx.fillRect(cx-w/2+k*bw+0.5,cy-h,bw-1,h);ctx.globalAlpha=0.9;ctx.fillRect(cx-w/2+k*bw+0.5,cy-h-2,bw-1,1.5)}
 ctx.globalAlpha=1;
}
function drawBeams(g,th){
 const [cx,cy]=corePos(g);ctx.save();ctx.globalCompositeOperation=th.light?'multiply':'lighter';
 for(let k=0;k<6;k++){const a=clock*0.5*(k%2?1:-1)+k*TAU/6+(g.layout==='strip'?-Math.PI/2:0),span=0.06+kickP*0.05;if(g.layout==='strip'&&(Math.sin(a)>0.2))continue;const gr=ctx.createLinearGradient(cx,cy,cx+Math.cos(a)*L,cy+Math.sin(a)*L);gr.addColorStop(0,hexA(k%2?th.cv.hot:th.cv.acc,0.25+kickP*0.25));gr.addColorStop(1,hexA(k%2?th.cv.hot:th.cv.acc,0));ctx.fillStyle=gr;ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,L,a-span,a+span);ctx.closePath();ctx.fill()}
 ctx.restore();
}
function drawDisk(g,th){
 const {R,c,rIn,rOut}=g,rd=rOut+0.035*R;
 ctx.fillStyle='#0d0a09';ctx.beginPath();ctx.arc(c,c,rd,0,TAU);ctx.fill();
 ctx.strokeStyle='rgba(255,240,220,0.04)';ctx.lineWidth=1;for(let r=rIn-0.03*R;r<rd-2;r+=2.6){ctx.beginPath();ctx.arc(c,c,r,0,TAU);ctx.stroke()}
 if(ctx.createConicGradient){const gr=ctx.createConicGradient(-0.6,c,c);gr.addColorStop(0,'rgba(255,230,200,0)');gr.addColorStop(0.06,'rgba(255,230,200,0.09)');gr.addColorStop(0.12,'rgba(255,230,200,0)');gr.addColorStop(0.5,'rgba(255,230,200,0)');gr.addColorStop(0.56,'rgba(255,230,200,0.07)');gr.addColorStop(0.62,'rgba(255,230,200,0)');gr.addColorStop(1,'rgba(255,230,200,0)');ctx.fillStyle=gr;ctx.beginPath();ctx.arc(c,c,rd,0,TAU);ctx.fill()}
 ctx.strokeStyle='rgba(243,227,201,0.18)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(c,c,rd,0,TAU);ctx.stroke();
}
function jitterPath(c,ri,ro,a0,a1,seed,amp){const r=rng(seed);ctx.beginPath();for(let k=0;k<=3;k++){const a=a0+(a1-a0)*k/3,rr=ro+(r()-0.5)*amp;ctx.lineTo(c+Math.cos(a)*rr,c+Math.sin(a)*rr)}for(let k=3;k>=0;k--){const a=a0+(a1-a0)*k/3,rr=ri+(r()-0.5)*amp;ctx.lineTo(c+Math.cos(a)*rr,c+Math.sin(a)*rr)}ctx.closePath()}
function drawRings(dt,g,th){
 const {R,c,rIn,t}=g,N=MI.N,pat=S.pat[S.edit],ns=S.slots.length,now=nowT();const curOf=si=>{const k=needleOf(si);return Math.floor((k===2?phase2:k===3?phase3:phase)*N)%N};
 const ghost=S.up.euclid&&performance.now()<eGhost?eucPattern(eK,eRot):null,boil=Math.floor(clock*7)%3;
 for(let i=0;i<ns;i++){
  const x=slotIns(i),ri=rIn+i*t+1.2,ro=rIn+(i+1)*t-1.2;
  if(!x){ctx.setLineDash(th.ring==='spray'?[5,4]:[2,5]);ctx.strokeStyle=hexA(th.light?th.cv.ink:th.cv.dim,th.light?0.35:0.6);ctx.lineWidth=1;ctx.beginPath();ctx.arc(c,c,(ri+ro)/2,0,TAU);ctx.stroke();ctx.setLineDash([]);continue}
  const col=insColor(x,th),muted=muteUntil[i]>now,over=(NF[S.edit][i]||1)<1,solo=isSolo(i),soloOn=solo&&soloNow===i,dimS=(S.edit==='S'&&!solo)||(S.edit==='F'&&x.fam!=='vur')||(playing&&!soloOn&&!allowed(planAt(curBar).sec,x,i));
  if(soloOn){ctx.strokeStyle=hexA(th.cv.hot,0.55+0.35*Math.sin(clock*9));ctx.lineWidth=3;ctx.beginPath();ctx.arc(c,c,ro+2.5,0,TAU);ctx.stroke();ctx.beginPath();ctx.arc(c,c,ri-2.5,0,TAU);ctx.stroke()}
  if(PH()&&i===eSel&&tab==='stage'){ctx.strokeStyle=hexA(th.cv.ink,0.45);ctx.lineWidth=1.2;ctx.setLineDash([4,3]);ctx.beginPath();ctx.arc(c,c,ro+1.5,0,TAU);ctx.stroke();ctx.setLineDash([])}
  if(th.ring==='hud'){ctx.strokeStyle=hexA(col,0.08);ctx.lineWidth=1;ctx.beginPath();ctx.arc(c,c,(ri+ro)/2,0,TAU);ctx.stroke()}
  if(th.ring==='kilim'){ctx.setLineDash([3,3]);ctx.strokeStyle=hexA(col,0.3);ctx.lineWidth=1;ctx.beginPath();ctx.arc(c,c,ri-0.6,0,TAU);ctx.stroke();ctx.setLineDash([])}
  for(let s=0;s<N;s++){
   const v=pat[i][s],f=flash[i][s]=Math.max(0,flash[i][s]-dt*3.5),[a0,a1]=cellAng(s),gsx=MI.gsSet.has(s),hl=playing&&s===curOf(i);
   if(th.ring==='neon'||th.ring==='vinyl'||th.ring==='kilim'){
    const ex=f*0.012*R;cellPath(c,Math.max(1,ri-ex*0.3),ro+ex,a0,a1);
    if(v){if(!GLX&&th.ring==='neon'){ctx.shadowColor=col;ctx.shadowBlur=6+16*f}ctx.fillStyle=hexA(col,muted||dimS?0.25:over?0.35+0.3*f:v===2?0.95:0.62+0.38*f);ctx.fill();ctx.shadowBlur=0;if(v===2){ctx.strokeStyle='rgba(255,255,255,0.85)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(c,c,ro-1.5,a0+0.01,a1-0.01);ctx.stroke()}if(th.ring==='kilim'){ctx.fillStyle=hexA(th.cv.ink,0.5);const m=midAng(s),rm=(ri+ro)/2;ctx.beginPath();ctx.arc(c+Math.cos(m)*rm,c+Math.sin(m)*rm,1.6,0,TAU);ctx.fill()}}
    else{ctx.fillStyle=hexA(col,(gsx?0.07:0.035)+(hl?0.07:0)+(S.edit==='F'&&x.fam==='vur'&&fillZone(s)?0.08:0));ctx.fill();ctx.strokeStyle=hexA(col,gsx?0.32:0.18);ctx.lineWidth=1;ctx.stroke()}
   }else if(th.ring==='hud'){
    if(v){cellPath(c,ri+1,ro-1,a0,a1);ctx.fillStyle=hexA(col,muted||dimS?0.25:0.78+0.22*f);ctx.fill();if(f>0.02){ctx.fillStyle='rgba(255,255,255,'+(f*0.6).toFixed(3)+')';ctx.fill()}if(v===2){ctx.strokeStyle=th.cv.warn;ctx.lineWidth=2;ctx.beginPath();ctx.arc(c,c,ro+1.5,a0,a1);ctx.stroke()}}
    else{if(hl){cellPath(c,ri+1,ro-1,a0,a1);ctx.fillStyle=hexA(col,0.12);ctx.fill()}ctx.strokeStyle=hexA(col,gsx?0.6:0.3);ctx.lineWidth=1;const L1=(ro-ri)*0.32;[a0,a1].forEach(a=>{const cs=Math.cos(a),sn=Math.sin(a);ctx.beginPath();ctx.moveTo(c+cs*(ri+1),c+sn*(ri+1));ctx.lineTo(c+cs*(ri+1+L1),c+sn*(ri+1+L1));ctx.moveTo(c+cs*(ro-1-L1),c+sn*(ro-1-L1));ctx.lineTo(c+cs*(ro-1),c+sn*(ro-1));ctx.stroke()});if(gsx){ctx.beginPath();ctx.arc(c,c,ro-1,a0,a1);ctx.stroke()}}
   }else{
    const amp=(ro-ri)*(0.22+f*0.5);jitterPath(c,ri,ro,a0,a1,i*131+s*7+boil*977,amp);
    if(v){ctx.fillStyle=muted||dimS?hexA(col,0.3):col;ctx.fill();ctx.strokeStyle=th.cv.ink;ctx.lineWidth=1.6;ctx.stroke();if(v===2){const m=midAng(s),rm=(ri+ro)/2,xx=c+Math.cos(m)*rm,yy=c+Math.sin(m)*rm,q=(ro-ri)*0.35;ctx.strokeStyle=th.cv.bg;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(xx-q,yy-q);ctx.lineTo(xx+q,yy+q);ctx.moveTo(xx+q,yy-q);ctx.lineTo(xx-q,yy+q);ctx.stroke()}}
    else{if(hl){ctx.fillStyle=hexA(th.cv.acc,0.25);ctx.fill()}ctx.strokeStyle=hexA(th.cv.ink,gsx?0.75:0.4);ctx.lineWidth=gsx?1.4:0.9;ctx.stroke()}
   }
   if(ghost&&eSel===i&&ghost[s]){ctx.setLineDash([3,3]);ctx.strokeStyle=hexA(th.cv.ink,0.8);ctx.lineWidth=1.2;cellPath(c,ri+1,ro-1,a0+0.01,a1-0.01);ctx.stroke();ctx.setLineDash([])}
   if(hover&&hover.i===i&&hover.s===s){ctx.strokeStyle=th.cv.ink;ctx.lineWidth=1.4;cellPath(c,ri,ro,a0,a1);ctx.stroke()}
  }
  if(muted||over||solo){ctx.fillStyle=soloOn?th.cv.hot:muted||over?th.cv.hot:hexA(th.cv.ink,0.5);ctx.font='600 10px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(muted?T('SUS'):over?T('NEFES'):soloOn?'SOLO!':'solo',c,c-(ri+ro)/2)}
 }
}
function drawMarks(g,th){
 const {R,c,rOut}=g,fs=Math.max(10,Math.round(R*0.034)),N=MI.N;
 ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.font=(th.id==='punk'?'':'600 ')+fs+'px '+(th.id==='punk'?th.font.d:th.font.m);
 ctx.strokeStyle=hexA(th.cv.ink,0.35);ctx.fillStyle=hexA(th.cv.ink,0.55);ctx.lineWidth=1;
 if(th.ring==='hud'){for(let s=0;s<N;s++){const a=-Math.PI/2+s*SEG(),cs=Math.cos(a),sn=Math.sin(a);ctx.beginPath();ctx.moveTo(c+cs*(rOut+3),c+sn*(rOut+3));ctx.lineTo(c+cs*(rOut+6),c+sn*(rOut+6));ctx.stroke()}}
 MI.gs.forEach(s=>{const a=-Math.PI/2+dirS*s*SEG()+rot,cs=Math.cos(a),sn=Math.sin(a),off=th.ring==='vinyl'?0.06*R:0.022*R;
  ctx.beginPath();ctx.moveTo(c+cs*(rOut+3),c+sn*(rOut+3));ctx.lineTo(c+cs*(rOut+off),c+sn*(rOut+off));ctx.stroke();
  const tr=rOut+(th.ring==='vinyl'?0.09:0.05)*R;ctx.fillText(String(s+1),c+cs*tr,c+sn*tr)});
 const rr=g.r0+range()*(1.02*R-g.r0);ctx.setLineDash([2,6]);ctx.strokeStyle=hexA(th.cv.hot,0.3);ctx.lineWidth=1;ctx.beginPath();ctx.arc(c,c,rr,0,TAU);ctx.stroke();ctx.setLineDash([]);
}
function drawNeedle(g,th){
 const {R,c,r0,rIn,rOut,t}=g;
 if(th.needle==='tonearm'){
  ctx.strokeStyle=hexA(th.cv.acc,0.6);ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(c,c-rIn+2);ctx.lineTo(c,c-rOut-2);ctx.stroke();
  const px=c+0.82*R,py=c-0.8*R,hx=c+0.012*R,hy=c-rOut+t*0.4;
  ctx.lineCap='round';ctx.strokeStyle='#2b211b';ctx.lineWidth=Math.max(5,R*0.03);ctx.beginPath();ctx.moveTo(px,py);ctx.quadraticCurveTo(c+0.45*R,c-0.86*R,hx+0.05*R,hy-0.05*R);ctx.lineTo(hx,hy);ctx.stroke();
  ctx.strokeStyle='#cfc6b8';ctx.lineWidth=Math.max(2.5,R*0.014);ctx.beginPath();ctx.moveTo(px,py);ctx.quadraticCurveTo(c+0.45*R,c-0.86*R,hx+0.05*R,hy-0.05*R);ctx.lineTo(hx,hy);ctx.stroke();
  ctx.save();ctx.translate(hx,hy);ctx.rotate(-0.75);ctx.fillStyle='#cfc6b8';ctx.fillRect(-0.025*R,-0.012*R,0.05*R,0.024*R);ctx.restore();
  ctx.fillStyle='#2e241e';ctx.strokeStyle='#cfc6b8';ctx.lineWidth=2;ctx.beginPath();ctx.arc(px,py,0.055*R,0,TAU);ctx.fill();ctx.stroke();
  ctx.fillStyle='#cfc6b8';ctx.beginPath();ctx.arc(px+0.05*R,py-0.05*R,0.03*R,0,TAU);ctx.fill();ctx.lineCap='butt';return;
 }
 const ang=-Math.PI/2+phase*TAU,cs=Math.cos(ang),sn=Math.sin(ang),x0=c+cs*r0*1.1,y0=c+sn*r0*1.1,x1=c+cs*(rOut+0.03*R),y1=c+sn*(rOut+0.03*R);
 if(th.needle!=='marker'&&ctx.createConicGradient){const span=0.9,p=span/TAU,gr=ctx.createConicGradient(ang-span,c,c);gr.addColorStop(0,hexA(th.cv.acc,0));gr.addColorStop(p,hexA(th.cv.acc,th.needle==='laser'?0.12:0.17));gr.addColorStop(Math.min(1,p+0.0005),hexA(th.cv.acc,0));gr.addColorStop(1,hexA(th.cv.acc,0));ctx.fillStyle=gr;ctx.beginPath();ctx.arc(c,c,rOut,0,TAU);ctx.arc(c,c,r0*1.08,0,TAU,true);ctx.fill('evenodd')}
 if(th.needle==='neon'){
  if(!GLX){ctx.shadowColor=th.cv.acc;ctx.shadowBlur=14}ctx.strokeStyle=th.id==='synth'?'#fff6fb':th.id==='anadolu'?'#fff3d6':'#e9fffb';ctx.lineWidth=1.6;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(x0,y0);ctx.lineTo(x1,y1);ctx.stroke();ctx.fillStyle=ctx.strokeStyle;ctx.beginPath();ctx.arc(x1,y1,2.6,0,TAU);ctx.fill();ctx.shadowBlur=0;
 }else if(th.needle==='laser'){
  [0.05,0.1].forEach((o,k)=>{const a=ang-o;ctx.strokeStyle=hexA(th.cv.acc,k?0.15:0.3);ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(c+Math.cos(a)*r0*1.1,c+Math.sin(a)*r0*1.1);ctx.lineTo(c+Math.cos(a)*rOut,c+Math.sin(a)*rOut);ctx.stroke()});
  ctx.strokeStyle=th.cv.warn;ctx.lineWidth=1.4;ctx.beginPath();ctx.moveTo(x0,y0);ctx.lineTo(x1,y1);ctx.stroke();
  ctx.strokeStyle=th.cv.acc;ctx.lineWidth=1.2;ctx.beginPath();ctx.arc(x1,y1,6,0,TAU);ctx.stroke();ctx.beginPath();ctx.moveTo(x1-10,y1);ctx.lineTo(x1-7,y1);ctx.moveTo(x1+7,y1);ctx.lineTo(x1+10,y1);ctx.moveTo(x1,y1-10);ctx.lineTo(x1,y1-7);ctx.moveTo(x1,y1+7);ctx.lineTo(x1,y1+10);ctx.stroke();
  ctx.fillStyle=th.cv.acc;ctx.font='600 11px '+th.font.m;ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText('S'+String(Math.floor(phase*MI.N)%MI.N+1).padStart(2,'0'),x1+13,y1);
 }else{
  const r=rng(Math.floor(clock*7));ctx.lineCap='round';
  ctx.strokeStyle=th.cv.acc;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(x0+3,y0+2);ctx.lineTo(x1+3,y1+2);ctx.stroke();
  ctx.strokeStyle=th.cv.ink;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(x0,y0);const mx=(x0+x1)/2+(r()-0.5)*4,my=(y0+y1)/2+(r()-0.5)*4;ctx.lineTo(mx,my);ctx.lineTo(x1,y1);ctx.stroke();
  const ah=ang+Math.PI;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x1+Math.cos(ah+0.5)*12,y1+Math.sin(ah+0.5)*12);ctx.moveTo(x1,y1);ctx.lineTo(x1+Math.cos(ah-0.5)*12,y1+Math.sin(ah-0.5)*12);ctx.stroke();ctx.lineCap='butt';
 }
}
function drawExtraNeedles(g,th){
 const {R,c,r0,rOut}=g;
 [[2,phase2,th.cv.hot,[]],[3,phase3,th.cv.warn,[4,4]]].forEach(([k,ph,col,dash])=>{if(!needleOn(k))return;const ang=-Math.PI/2+ph*TAU,cs=Math.cos(ang),sn=Math.sin(ang);ctx.setLineDash(dash);ctx.strokeStyle=hexA(col,0.9);ctx.lineWidth=1.2;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(c+cs*r0*1.1,c+sn*r0*1.1);ctx.lineTo(c+cs*(rOut+0.02*R),c+sn*(rOut+0.02*R));ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=col;ctx.beginPath();ctx.arc(c+cs*(rOut+0.02*R),c+sn*(rOut+0.02*R),2.2,0,TAU);ctx.fill();ctx.font='600 9px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(String(k),c+cs*(rOut+0.045*R),c+sn*(rOut+0.045*R));ctx.lineCap='butt'})
}
function drawCore(dt,g,th){
 const {R,c,r0}=g;
 if(!RM)dotRot+=dt*(0.25+kickP*0.6);
 if(S.stage.core){
  if(th.light){ctx.fillStyle=hexA(th.cv.acc,0.9);ctx.beginPath();ctx.arc(c,c,r0*(1.25+kickP*0.35),0,TAU);ctx.fill()}
  else{ctx.globalCompositeOperation='lighter';const rr=r0*(1.9+kickP*0.9),gr=ctx.createRadialGradient(c,c,r0*0.4,c,c,rr);gr.addColorStop(0,hexA(th.cv.hot,(0.32+0.4*kickP).toFixed(3)));gr.addColorStop(0.5,hexA(th.fam.tel,(0.14+0.2*kickP).toFixed(3)));gr.addColorStop(1,hexA(th.fam.tel,0));ctx.fillStyle=gr;ctx.beginPath();ctx.arc(c,c,rr,0,TAU);ctx.fill();ctx.globalCompositeOperation='source-over'}
  if(th.core==='neon'||th.core==='label'||th.core==='sun'){ctx.fillStyle=hexA(th.cv.ink,0.55);for(let k=0;k<48;k++){const a=dotRot+k*TAU/48;ctx.beginPath();ctx.arc(c+Math.cos(a)*r0*1.17,c+Math.sin(a)*r0*1.17,k%4===0?1.6:0.9,0,TAU);ctx.fill()}}
 }
 tapP=Math.max(0,tapP-dt*2.5);
 const fd=th.font.d,fmF=th.font.m;
 if(th.core==='hud'){
  ctx.fillStyle=th.cv.core;ctx.beginPath();for(let k=0;k<6;k++){const a=k*Math.PI/3+Math.PI/6;ctx.lineTo(c+Math.cos(a)*r0,c+Math.sin(a)*r0)}ctx.closePath();ctx.fill();
  ctx.strokeStyle=tapP>0&&tapFx?tapFx.c:th.cv.acc;ctx.lineWidth=1.2+tapP*2;ctx.stroke();
  ctx.strokeStyle=hexA(th.cv.warn,0.7);ctx.lineWidth=1.5;for(let k=0;k<4;k++){const a=dotRot*0.6+k*TAU/4;ctx.beginPath();ctx.arc(c,c,r0*1.22,a,a+0.5);ctx.stroke()}
 }else if(th.core==='paper'){
  const r=rng(Math.floor(clock*7)+3);ctx.fillStyle=th.cv.core;ctx.beginPath();for(let k=0;k<20;k++){const a=k*TAU/20,rr=r0*(1+(r()-0.5)*0.12);ctx.lineTo(c+Math.cos(a)*rr,c+Math.sin(a)*rr)}ctx.closePath();ctx.fill();ctx.strokeStyle=tapP>0&&tapFx?tapFx.c:th.cv.ink;ctx.lineWidth=2+tapP*2;ctx.stroke();
 }else if(th.core==='label'){
  ctx.save();ctx.translate(c,c);ctx.rotate(rot);ctx.fillStyle=th.cv.core;ctx.beginPath();ctx.arc(0,0,r0*1.02,0,TAU);ctx.fill();ctx.strokeStyle='rgba(243,227,201,0.6)';ctx.lineWidth=1;ctx.beginPath();ctx.arc(0,0,r0*0.86,0,TAU);ctx.stroke();
  ctx.fillStyle='rgba(42,22,8,0.8)';ctx.font='600 '+Math.max(10,Math.round(r0*0.16))+'px '+fmF;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('YAN '+playPk,0,-r0*0.6);ctx.restore();
  ctx.fillStyle='#120d0b';ctx.beginPath();ctx.arc(c,c,3,0,TAU);ctx.fill();
 }else if(th.core==='sun'){
  const gr=ctx.createLinearGradient(0,c-r0,0,c+r0);gr.addColorStop(0,'#ffd166');gr.addColorStop(0.5,'#ff6ec7');gr.addColorStop(1,'#7b61ff');ctx.fillStyle=gr;ctx.beginPath();ctx.arc(c,c,r0,0,TAU);ctx.fill();
  ctx.fillStyle=th.cv.core;for(let k=0;k<4;k++){ctx.fillRect(c-r0,c+r0*0.15+k*r0*0.2,r0*2,2+k*1.5)}ctx.strokeStyle=tapP>0&&tapFx?tapFx.c:hexA(th.cv.ink,0.7);ctx.lineWidth=1.5+tapP*2;ctx.beginPath();ctx.arc(c,c,r0,0,TAU);ctx.stroke();
 }else if(th.core==='eye'){
  ctx.fillStyle='#1b5fa8';ctx.beginPath();ctx.arc(c,c,r0,0,TAU);ctx.fill();ctx.fillStyle='#ffe8c8';ctx.beginPath();ctx.arc(c,c,r0*0.72,0,TAU);ctx.fill();ctx.fillStyle='#3a9bd9';ctx.beginPath();ctx.arc(c,c,r0*0.5,0,TAU);ctx.fill();ctx.fillStyle='#120d0b';ctx.beginPath();ctx.arc(c,c,r0*0.26,0,TAU);ctx.fill();
  ctx.strokeStyle=tapP>0&&tapFx?tapFx.c:th.cv.acc;ctx.lineWidth=2+tapP*2;ctx.beginPath();ctx.arc(c,c,r0,0,TAU);ctx.stroke();
 }else{
  ctx.beginPath();ctx.arc(c,c,r0,0,TAU);ctx.fillStyle=th.cv.core;ctx.fill();ctx.strokeStyle=tapP>0&&tapFx?tapFx.c:(S.stage.core?hexA(th.cv.hot,0.55):'#272148');ctx.lineWidth=1.2+tapP*2;ctx.stroke();
 }
 const hpf=clamp(core.hp/hpMax(),0,1);ctx.lineWidth=3;ctx.strokeStyle=hexA(th.cv.dim,0.6);ctx.beginPath();ctx.arc(c,c,r0*1.3,0,TAU);ctx.stroke();ctx.strokeStyle=hpf<0.35?th.cv.hot:th.cv.acc;ctx.beginPath();ctx.arc(c,c,r0*1.3,-Math.PI/2,-Math.PI/2+hpf*TAU);ctx.stroke();
 if(core.sh>0){ctx.strokeStyle=hexA(th.cv.ink,0.8);ctx.lineWidth=2;ctx.beginPath();ctx.arc(c,c,r0*1.38,-Math.PI/2,-Math.PI/2+clamp(core.sh/hpMax(),0,1)*TAU);ctx.stroke()}
 ctx.textAlign='center';ctx.textBaseline='middle';
 const dark=th.core==='eye'||th.core==='label';const ink=dark?'#120d0b':th.cv.ink,sub=dark?'rgba(18,13,11,0.75)':hexA(th.cv.ink,0.6);
 if(tapFx&&tapFx.life>0){
  tapFx.life-=dt*1.3;ctx.globalAlpha=clamp(tapFx.life*1.5,0,1);
  ctx.fillStyle=dark?'#120d0b':tapFx.c;ctx.font=(th.id==='punk'?'':'600 ')+Math.round(r0*0.36)+'px '+fd;ctx.fillText(tapFx.t,c,c-r0*0.12);
  ctx.fillStyle=sub;ctx.font='500 '+Math.max(10,Math.round(r0*0.15))+'px '+fmF;ctx.fillText(tapFx.sub,c,c+r0*0.3);ctx.globalAlpha=1;
 }else if(th.core!=='eye'){
  ctx.save();if(th.id==='punk'){ctx.translate(c,c);ctx.rotate(-0.1);ctx.translate(-c,-c)}
  ctx.fillStyle=ink;ctx.font=(th.id==='punk'||th.id==='synth'?'':'600 ')+Math.round(r0*(th.id==='punk'?0.62:th.id==='synth'?0.42:0.5))+'px '+fd;ctx.fillText(String(Math.round(curBpm(curBar))),c,c-r0*0.14);ctx.restore();
  ctx.font='500 '+Math.max(10,Math.round(r0*0.15))+'px '+fmF;ctx.fillStyle=sub;ctx.fillText('BPM'+(bActive()?' · '+playPk:''),c,c+r0*0.3);
  const es=effSeri();if(es>0){ctx.fillStyle=dark?'#120d0b':th.cv.acc;ctx.fillText('seri '+es,c,c+r0*0.56)}
 }
}
function drawStrip(dt,g,th){
 const {x0,x1,gridTop,rowH,colW}=g,N=MI.N,ns=S.slots.length,pat=S.pat[S.edit],now=nowT();const curOf=si=>{const k=needleOf(si);return Math.floor((k===2?phase2:k===3?phase3:phase)*N)%N};
 const ghost=S.up.euclid&&performance.now()<eGhost?eucPattern(eK,eRot):null;
 ctx.fillStyle=hexA(th.cv.bg,0.55);ctx.fillRect(0,gridTop,L,L-gridTop);
 const ry=g.fieldTop+(1-range())*(gridTop-g.fieldTop);ctx.setLineDash([2,6]);ctx.strokeStyle=hexA(th.cv.hot,0.3);ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(x0,ry);ctx.lineTo(x1,ry);ctx.stroke();ctx.setLineDash([]);
 for(let i=0;i<ns;i++){const x=slotIns(i),y=gridTop+i*rowH,col=x?insColor(x,th):th.cv.dim,muted=x&&muteUntil[i]>now,over=x&&(NF[S.edit][i]||1)<1,solo=x&&isSolo(i),soloOn=solo&&soloNow===i,dimS=(S.edit==='S'&&x&&!solo)||(x&&playing&&!soloOn&&!allowed(planAt(curBar).sec,x,i));
  if(soloOn){ctx.strokeStyle=hexA(th.cv.hot,0.55+0.35*Math.sin(clock*9));ctx.lineWidth=2;ctx.strokeRect(x0-2,y+0.5,x1-x0+4,rowH-1)}
  ctx.fillStyle=hexA(th.cv.ink,x?0.75:0.35);ctx.font='500 '+Math.max(9,Math.min(12,Math.round(rowH*0.42)))+'px '+th.font.m;ctx.textAlign='right';ctx.textBaseline='middle';ctx.fillText(muted?'SUS':over?'NEFES':soloOn?'SOLO!':solo?'solo':x?x.n:'boş',x0-8,y+rowH/2);
  if(muted){ctx.fillStyle=hexA(th.cv.hot,0.12);ctx.fillRect(x0,y,x1-x0,rowH)}
  for(let s=0;s<N;s++){const v=x?pat[i][s]:0,f=flash[i][s]=Math.max(0,flash[i][s]-dt*3.5),cx=x0+s*colW,gsx=MI.gsSet.has(s),hl=playing&&s===curOf(i),pad=1.5;
   if(!x){ctx.strokeStyle=hexA(th.cv.dim,0.5);ctx.setLineDash([2,4]);ctx.strokeRect(cx+pad,y+pad,colW-2*pad,rowH-2*pad);ctx.setLineDash([]);continue}
   if(v){ctx.fillStyle=hexA(col,muted||dimS?0.25:over?0.35+0.3*f:v===2?0.95:0.62+0.38*f);ctx.fillRect(cx+pad-f*2,y+pad-f*2,colW-2*pad+f*4,rowH-2*pad+f*4);if(v===2){ctx.strokeStyle=th.light?th.cv.bg:'rgba(255,255,255,0.85)';ctx.lineWidth=1.5;ctx.strokeRect(cx+pad+1.5,y+pad+1.5,colW-2*pad-3,rowH-2*pad-3)}}
   else{ctx.fillStyle=hexA(col,(gsx?0.1:0.05)+(hl?0.08:0));ctx.fillRect(cx+pad,y+pad,colW-2*pad,rowH-2*pad);ctx.strokeStyle=hexA(th.light?th.cv.ink:col,gsx?0.35:0.18);ctx.lineWidth=1;ctx.strokeRect(cx+pad,y+pad,colW-2*pad,rowH-2*pad)}
   if(ghost&&eSel===i&&ghost[s]){ctx.setLineDash([3,3]);ctx.strokeStyle=hexA(th.cv.ink,0.8);ctx.lineWidth=1.2;ctx.strokeRect(cx+pad+1,y+pad+1,colW-2*pad-2,rowH-2*pad-2);ctx.setLineDash([])}
   if(hover&&hover.i===i&&hover.s===s){ctx.strokeStyle=th.cv.ink;ctx.lineWidth=1.4;ctx.strokeRect(cx+pad,y+pad,colW-2*pad,rowH-2*pad)}
  }
 }
 ctx.fillStyle=hexA(th.cv.ink,0.5);ctx.font='600 10px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='top';MI.gs.forEach(s=>ctx.fillText(String(s+1),x0+(s+0.5)*colW,gridTop+ns*rowH+4));
 const px=x0+phase*(x1-x0);if(!GLX){ctx.shadowColor=th.cv.acc;ctx.shadowBlur=12}ctx.strokeStyle=th.light?th.cv.ink:th.cv.acc;ctx.lineWidth=th.needle==='marker'?4:1.6;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(px,gridTop-0.03*L);ctx.lineTo(px,gridTop+ns*rowH+2);ctx.stroke();ctx.shadowBlur=0;ctx.lineCap='butt';
 [[2,phase2,th.cv.hot,[]],[3,phase3,th.cv.warn,[4,4]]].forEach(([k,ph,col,dash])=>{if(!needleOn(k))return;const xx=x0+ph*(x1-x0);ctx.setLineDash(dash);ctx.strokeStyle=hexA(col,0.9);ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(xx,gridTop-0.02*L);ctx.lineTo(xx,gridTop+ns*rowH+2);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=col;ctx.font='600 9px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='bottom';ctx.fillText(String(k),xx,gridTop-0.022*L)});
 if(S.stage.core){ctx.globalCompositeOperation=th.light?'multiply':'lighter';const gr=ctx.createRadialGradient(px,gridTop,0,px,gridTop,0.12*L*(1+kickP*0.6));gr.addColorStop(0,hexA(th.cv.hot,0.35+0.35*kickP));gr.addColorStop(1,hexA(th.cv.hot,0));ctx.fillStyle=gr;ctx.beginPath();ctx.arc(px,gridTop,0.12*L*(1+kickP*0.6),0,TAU);ctx.fill();ctx.globalCompositeOperation='source-over'}
 const hpf=clamp(core.hp/hpMax(),0,1);ctx.fillStyle=hexA(th.cv.dim,0.7);ctx.fillRect(x0,gridTop-5,x1-x0,3);ctx.fillStyle=hpf<0.35?th.cv.hot:th.cv.acc;ctx.fillRect(x0,gridTop-5,(x1-x0)*hpf,3);if(core.sh>0){ctx.fillStyle=hexA(th.cv.ink,0.85);ctx.fillRect(x0,gridTop-9,(x1-x0)*clamp(core.sh/hpMax(),0,1),2)}
 ctx.fillStyle=hexA(th.cv.ink,0.7);ctx.font='600 11px '+th.font.m;ctx.textAlign='left';ctx.textBaseline='bottom';ctx.fillText(Math.round(curBpm(curBar))+' BPM'+(bActive()?' · '+playPk:'')+(effSeri()>0?' · seri '+effSeri():''),x0,gridTop-12);
 if(tapFx&&tapFx.life>0){tapFx.life-=dt*1.3;ctx.globalAlpha=clamp(tapFx.life*1.5,0,1);ctx.fillStyle=tapFx.c;ctx.font=(th.id==='punk'?'':'600 ')+Math.round(0.05*L)+'px '+th.font.d;ctx.textAlign='right';ctx.fillText(tapFx.t+' · '+tapFx.sub,x1,gridTop-12);ctx.globalAlpha=1}
 tapP=Math.max(0,tapP-dt*2.5);
}
function drawEnemy(e,th,g){
 const [x,y]=enemyPos(e,g),T=ETYPES[e.ty],sz=0.022*g.R*T.r*(e.boss?1.4:1),col=e.boss?th.en.boss:th.en.body,edge=th.en.edge,st=th.en.style,fl=e.flash>0.2;
 ctx.save();ctx.translate(x,y);if(st==='spray')ctx.rotate(Math.sin(clock*6+e.wob)*0.08);
 ctx.beginPath();switch(T.shape){case 'tri':ctx.moveTo(0,-sz);ctx.lineTo(sz*0.9,sz*0.7);ctx.lineTo(-sz*0.9,sz*0.7);ctx.closePath();break;case 'hex':for(let k=0;k<6;k++){const a=k*Math.PI/3;ctx.lineTo(Math.cos(a)*sz,Math.sin(a)*sz)}ctx.closePath();break;case 'dot':ctx.arc(0,0,sz*0.6,0,TAU);break;case 'square':ctx.rect(-sz*0.8,-sz*0.8,sz*1.6,sz*1.6);break;case 'boss':for(let k=0;k<10;k++){const a=k*TAU/10+clock*0.4,rr=k%2?sz*0.65:sz;ctx.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}ctx.closePath();break;default:ctx.arc(0,0,sz,0,TAU)}
 if(st==='wire'){ctx.strokeStyle=fl?'#ffffff':col;ctx.lineWidth=1.5;ctx.stroke();ctx.fillStyle=hexA(col,fl?0.6:0.15);ctx.fill()}
 else if(st==='hud'){ctx.fillStyle=fl?'#ffffff':hexA(col,0.85);ctx.fill();ctx.strokeStyle=edge;ctx.lineWidth=1;const b=sz*1.3;[[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([sx,sy])=>{ctx.beginPath();ctx.moveTo(sx*b,sy*b-sy*sz*0.5);ctx.lineTo(sx*b,sy*b);ctx.lineTo(sx*b-sx*sz*0.5,sy*b);ctx.stroke()})}
 else if(st==='spray'){ctx.fillStyle=fl?th.cv.acc:col;ctx.fill();ctx.strokeStyle=edge;ctx.lineWidth=1.8;ctx.stroke()}
 else if(st==='soft'){ctx.fillStyle=fl?'#ffffff':hexA(col,0.85);ctx.fill()}
 else if(st==='eye'){ctx.fillStyle=fl?'#ffffff':col;ctx.fill();ctx.strokeStyle=edge;ctx.lineWidth=1.2;ctx.stroke();ctx.fillStyle=edge;ctx.beginPath();ctx.arc(0,0,sz*0.45,0,TAU);ctx.fill();ctx.fillStyle='#1d0f0a';ctx.beginPath();ctx.arc(0,0,sz*0.2,0,TAU);ctx.fill()}
 else{if(!GLX){ctx.shadowColor=col;ctx.shadowBlur=8}ctx.fillStyle=fl?'#ffffff':col;ctx.fill();ctx.shadowBlur=0;ctx.strokeStyle=edge;ctx.lineWidth=1;ctx.stroke()}
 if(e.slowT>0||e.dotT>0){ctx.strokeStyle=e.dotT>0?th.cv.warn:th.cv.acc;ctx.lineWidth=1;ctx.setLineDash([2,3]);ctx.beginPath();ctx.arc(0,0,sz*1.5,0,TAU);ctx.stroke();ctx.setLineDash([])}
 if(e.stun>0){ctx.fillStyle=th.cv.warn;for(let k=0;k<3;k++){const a=clock*8+k*TAU/3;ctx.fillRect(Math.cos(a)*sz*1.6-1,Math.sin(a)*sz*1.6-1-sz*0.6,2,2)}}
 ctx.restore();
 if(e.boss){const w=sz*3;ctx.fillStyle=hexA(th.cv.ink,0.25);ctx.fillRect(x-w/2,y-sz*1.9,w,3);ctx.fillStyle=th.en.boss;ctx.fillRect(x-w/2,y-sz*1.9,w*clamp(e.hp/e.hpMax,0,1),3);ctx.fillStyle=hexA(th.cv.ink,0.8);ctx.font='600 10px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='bottom';ctx.fillText(T.n,x,y-sz*2.1)}
}
function drawVfx(dt,g,th){
 const [cx,cy]=corePos(g);ctx.lineCap='round';
 for(let k=vfx.length-1;k>=0;k--){const f=vfx[k];const rate_={tracer:4,homing:4,burst:3,crit:2,ring:2,beam:3,chain:3,shield:2,bolt:5,wallpush:4}[f.k]||3;f.life-=dt*rate_;if(f.life<=0){vfx.splice(k,1);continue}const a=f.life;
  if(f.k==='tracer'||f.k==='homing'){const [x0,y0]=cellPos(f.o.si,f.o.s,g),[x1,y1]=enemyPos(f.e,g);ctx.strokeStyle=hexA(f.col,a*0.9);ctx.lineWidth=1.4;ctx.beginPath();ctx.moveTo(x0,y0);if(f.k==='homing'){const mx=(x0+x1)/2+(y1-y0)*0.25,my=(y0+y1)/2-(x1-x0)*0.25;ctx.quadraticCurveTo(mx,my,x1,y1)}else ctx.lineTo(x1,y1);ctx.stroke();ctx.fillStyle=hexA(f.col,a);ctx.beginPath();ctx.arc(x1,y1,2.5,0,TAU);ctx.fill()}
  else if(f.k==='burst'){const [x,y]=enemyPos(f.e,g);ctx.strokeStyle=hexA(f.col,a*0.8);ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(x,y,(1-a)*0.05*L+3,0,TAU);ctx.stroke()}
  else if(f.k==='crit'){const [x,y]=enemyPos(f.e,g);ctx.strokeStyle=hexA(th.cv.warn,a);ctx.lineWidth=2;for(let q=0;q<4;q++){const an=q*Math.PI/4;const r1=0.012*L,r2=(0.03+(1-a)*0.02)*L;ctx.beginPath();ctx.moveTo(x+Math.cos(an)*r1,y+Math.sin(an)*r1);ctx.lineTo(x+Math.cos(an)*r2,y+Math.sin(an)*r2);ctx.moveTo(x-Math.cos(an)*r1,y-Math.sin(an)*r1);ctx.lineTo(x-Math.cos(an)*r2,y-Math.sin(an)*r2);ctx.stroke()}}
  else if(f.k==='ring'){ctx.strokeStyle=hexA(f.col,a*0.7);ctx.lineWidth=2+a*3;if(g.layout==='strip'){const y=g.gridTop-(1-a)*(g.gridTop-g.fieldTop);ctx.beginPath();ctx.moveTo(g.x0,y);ctx.lineTo(g.x1,y);ctx.stroke()}else{ctx.beginPath();ctx.arc(cx,cy,g.r0+(1-a)*(1.02*g.R-g.r0),0,TAU);ctx.stroke()}}
  else if(f.k==='beam'){ctx.strokeStyle=hexA(f.col,a*0.85);ctx.lineWidth=2+a*4;ctx.beginPath();if(g.layout==='strip'){const x=g.x0+f.a*(g.x1-g.x0);ctx.moveTo(x,g.gridTop);ctx.lineTo(x,g.fieldTop)}else{const an=f.a*TAU-Math.PI/2;ctx.moveTo(cx+Math.cos(an)*g.r0,cy+Math.sin(an)*g.r0);ctx.lineTo(cx+Math.cos(an)*1.05*g.R,cy+Math.sin(an)*1.05*g.R)}ctx.stroke()}
  else if(f.k==='chain'){const [x0,y0]=enemyPos(f.e1,g),[x1,y1]=enemyPos(f.e,g);ctx.strokeStyle=hexA(f.col,a);ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(x0,y0);const mx=(x0+x1)/2+(Math.random()-0.5)*8,my=(y0+y1)/2+(Math.random()-0.5)*8;ctx.lineTo(mx,my);ctx.lineTo(x1,y1);ctx.stroke()}
  else if(f.k==='bolt'){const [x1,y1]=enemyPos(f.e,g);ctx.strokeStyle=hexA(f.col,a);ctx.lineWidth=2.2;ctx.beginPath();ctx.moveTo(cx,cy);const segs=6;for(let q=1;q<=segs;q++){const t=q/segs,jx=(Math.random()-0.5)*14*(q<segs?1:0),jy=(Math.random()-0.5)*14*(q<segs?1:0);ctx.lineTo(cx+(x1-cx)*t+jx,cy+(y1-cy)*t+jy)}ctx.stroke()}
  else if(f.k==='wallpush'){ctx.strokeStyle=hexA(f.col,a*0.9);ctx.lineWidth=3;if(g.layout==='strip'){const x=g.x0+f.a*(g.x1-g.x0);ctx.beginPath();ctx.moveTo(x-10,g.gridTop-12);ctx.lineTo(x+10,g.gridTop-12);ctx.stroke()}else{const an=f.a*TAU-Math.PI/2,rb=g.rOut+0.012*g.R;ctx.beginPath();ctx.arc(cx,cy,rb+(1-a)*8,an-0.12,an+0.12);ctx.stroke()}}
  else if(f.k==='shield'){ctx.strokeStyle=hexA(f.col,a*0.8);ctx.lineWidth=2;if(g.layout==='strip'){ctx.beginPath();ctx.moveTo(g.x0,g.gridTop-9-(1-a)*20);ctx.lineTo(g.x1,g.gridTop-9-(1-a)*20);ctx.stroke()}else{ctx.beginPath();ctx.arc(cx,cy,g.r0*(1.4+(1-a)*0.8),0,TAU);ctx.stroke()}}
 }
 ctx.lineCap='butt';
}
function drawParts(dt,th){
 const lighter=!th.light&&th.part!=='dust';if(lighter)ctx.globalCompositeOperation='lighter';
 const decay=th.part==='dust'?0.5:th.part==='splat'?2.2:1.7;
 for(let k=parts.length-1;k>=0;k--){const p=parts[k];p.x+=p.vx*dt;p.y+=p.vy*dt;p.vx*=0.985;p.vy*=0.985;p.life-=dt*decay;if(p.life<=0){parts.splice(k,1);continue}
  ctx.globalAlpha=p.life*0.85;ctx.fillStyle=p.col;
  if(th.part==='line'){ctx.strokeStyle=p.col;ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(p.x-p.vx*0.06,p.y-p.vy*0.06);ctx.stroke()}
  else if(th.part==='spark')ctx.fillRect(p.x-1.1,p.y-1.1,2.2,2.2);
  else{ctx.beginPath();ctx.arc(p.x,p.y,p.sz,0,TAU);ctx.fill()}}
 ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';
}
function drawHud(g,th){
 ctx.fillStyle=hexA(th.cv.acc,0.55);ctx.font='600 11px '+th.font.m;ctx.textBaseline='middle';
 ctx.textAlign='left';ctx.fillText('SEQ//NABIZ-03',18,22);ctx.fillText('DÖNGÜ '+String(bar).padStart(4,'0'),18,L-22);
 ctx.textAlign='right';ctx.fillText('BPM '+S.bpm,L-18,22);ctx.fillText('DALGA '+S.wave+' · '+enemies.length+' HEDEF',L-18,L-22);
 if(!RM){const y=((clock*0.12)%1)*L;ctx.fillStyle=hexA(th.cv.acc,0.07);ctx.fillRect(0,y,L,3);ctx.fillStyle=hexA(th.cv.acc,0.03);ctx.fillRect(0,y-14,L,14)}
 if(g.layout==='circle'){ctx.strokeStyle=hexA(th.cv.acc,0.4);ctx.lineWidth=1.5;for(let k=0;k<4;k++){const a=-dotRot*0.35+k*TAU/4;ctx.beginPath();ctx.arc(g.c,g.c,0.975*g.R,a,a+0.3);ctx.stroke()}}
}
function drawOverlay(dt,g,th){
 if(waveFlash>0){waveFlash=Math.max(0,waveFlash-dt*0.6);const a=Math.min(1,waveFlash*1.6);ctx.globalAlpha=a*0.9;ctx.fillStyle=th.cv.ink;ctx.font=(th.id==='punk'||th.id==='synth'?'':'600 ')+Math.round(0.07*L)+'px '+th.font.d;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(waveText,g.c,g.layout==='strip'?0.5*L:0.08*L);if(wave&&wave.boss){ctx.font='500 '+Math.round(0.022*L)+'px '+th.font.m;ctx.fillStyle=th.en.boss;ctx.fillText(ETYPES[wave.boss.ty].n+' sahnede',g.c,(g.layout==='strip'?0.5*L:0.08*L)+0.055*L)}ctx.globalAlpha=1}
 if(secFlash>0){secFlash=Math.max(0,secFlash-dt*0.45);const a=Math.min(1,secFlash*1.5);ctx.globalAlpha=a*0.85;ctx.fillStyle=th.cv.ink;ctx.font='500 '+Math.round(0.026*L)+'px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(secName.toLocaleUpperCase('tr-TR'),g.c,g.layout==='strip'?0.56*L:0.955*L);ctx.globalAlpha=1}
 if(transFlash>0){transFlash=Math.max(0,transFlash-dt*0.8);ctx.globalAlpha=Math.min(1,transFlash*1.5);ctx.fillStyle=th.cv.warn||'#ffb13f';ctx.font='600 '+Math.round(0.04*L)+'px '+th.font.d;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(transText,g.c,g.layout==='strip'?0.36*L:0.08*L);ctx.globalAlpha=1}
 if(soloFlash>0&&soloNow>=0){soloFlash=Math.max(0,soloFlash-dt*0.5);const a=Math.min(1,soloFlash*1.6),x=slotIns(soloNow);ctx.globalAlpha=a;ctx.fillStyle=th.cv.hot;ctx.font=(th.id==='punk'||th.id==='synth'?'':'600 ')+Math.round(0.05*L)+'px '+th.font.d;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('Solo · '+(x?x.n:''),g.c,g.layout==='strip'?0.42*L:0.92*L);ctx.globalAlpha=1}
 if(retreatFlash>0){retreatFlash=Math.max(0,retreatFlash-dt*1.2);const gr=ctx.createRadialGradient(g.c,g.c,0.4*L,g.c,g.c,0.75*L);gr.addColorStop(0,hexA(th.cv.hot,0));gr.addColorStop(1,hexA(th.cv.hot,Math.min(0.6,retreatFlash*0.5)));ctx.fillStyle=gr;ctx.fillRect(0,0,L,L)}
}
function drawScene(dt){
 const th=dispTheme(),g=geom();
 ctx.setTransform(DPR,0,0,DPR,0,0);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.shadowBlur=0;
 const shk=fxVal(th,'shake')*kickP;if(shk>0&&!RM)ctx.translate((Math.random()-0.5)*shk*0.02*L,(Math.random()-0.5)*shk*0.02*L);
 drawBg(th,g);
 rot=th.ring==='vinyl'&&g.layout==='circle'?phase*TAU:0;dirS=th.ring==='vinyl'&&g.layout==='circle'?-1:1;
 kickP=Math.max(0,kickP-dt*3.2);bassP=Math.max(0,bassP-dt*2.5);
 if(S.stage.stars)drawStars(dt,g,th);
 if(S.stage.beams)drawBeams(g,th);
 if(S.stage.tunnel)drawTunnel(dt,g,th);
 if(S.stage.wall)drawWall(dt,g,th);
 if(S.stage.tower)drawTower(dt,g,th);
 if(S.stage.mirror)drawMirror(g,th);
 if(th.ring==='vinyl'&&g.layout==='circle')drawDisk(g,th);
 if(S.stage.wave)drawWave(g,th);
 if(playing&&S.up.dolgu&&fillBar(curBar)&&g.layout==='circle'){ctx.strokeStyle=hexA(th.cv.warn||'#ffb13f',0.35+0.3*Math.sin(clock*12));ctx.lineWidth=3;ctx.beginPath();ctx.arc(g.c,g.c,g.rOut+5,0,TAU);ctx.stroke()}
 const sv=soloView();
 if(sv>=0){drawSoloStage(dt,sgeom(),th,sv);if(g.layout!=='strip')drawCore(dt,g,th)}
 else if(g.layout==='strip'){drawStrip(dt,g,th)}
 else{drawRings(dt,g,th);drawMarks(g,th);drawNeedle(g,th);drawExtraNeedles(g,th);drawCore(dt,g,th)}
 if(S.up.akor&&sv<0&&g.layout==='circle'){const ch=curChord(curBar,Math.floor(phase*MI.N)%MI.N);ctx.fillStyle=hexA(th.cv.acc,0.85);ctx.font='600 '+Math.max(9,Math.round(g.r0*0.3))+'px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(chordName(ch),g.c,g.c+g.r0*0.55)}
 if(crashFlash>0){crashFlash=Math.max(0,crashFlash-dt*2.5);ctx.fillStyle='rgba(255,255,255,'+(crashFlash*0.18).toFixed(3)+')';ctx.fillRect(0,0,L,L)}
 enemies.forEach(e=>drawEnemy(e,th,g));
 drawVfx(dt,g,th);
 drawParts(dt,th);
 if(th.ring==='hud')drawHud(g,th);
 drawOverlay(dt,g,th);
}

/* ================= solo stage takeover ================= */
function soloView(){if(!S.up.sdevir)return -1;if(S.edit==='S'){const ss=soloEdSlots();if(ss.length){if(!ss.includes(soloEdSlot))soloEdSlot=ss[0];return soloEdSlot}}if(playing&&soloNow>=0){const x=slotIns(soloNow);if(x&&x.fam!=='vur'&&hasSoloNotes(soloNow))return soloNow}return -1}
function sgeom(){const R=L/2,K=soloRows(),T=soloSteps();if(S.layout==='strip'){const x0=0.1*L,x1=0.97*L,gridTop=0.4*L,rowH=Math.min(0.52*L/K,0.05*L);return{layout:'strip',R,c:R,K,T,x0,x1,gridTop,rowH,colW:(x1-x0)/T,r0:0.13*R}}const ph=PH(),rIn=(ph?0.13:0.16)*R,rOut=0.74*R;return{layout:'circle',R,c:R,K,T,r0:(ph?0.1:0.12)*R,rIn,rOut,t:(rOut-rIn)/K}}
const sAng=t=>-Math.PI/2+t/soloSteps()*TAU;
function soloPhase(){if(!playing)return -1;const pa=planAt(curBar);return ((pa.barIn%2)+phase)/2}
function soloStageHit(e){const b=vis().getBoundingClientRect(),x=(e.clientX-b.left)/b.width*L,y=(e.clientY-b.top)/b.height*L,g=sgeom();
 if(g.layout==='strip'){if(y<g.gridTop||y>g.gridTop+g.rowH*g.K)return y<g.gridTop-6?{core:true}:null;const t=Math.floor((x-g.x0)/g.colW);if(t<0||t>=g.T)return null;return{t,r:clamp(g.K-1-Math.floor((y-g.gridTop)/g.rowH),0,g.K-1)}}
 const dx=x-g.c,dy=y-g.c,r=Math.hypot(dx,dy);if(r<g.r0*1.05)return{core:true};if(r<g.rIn-4||r>g.rOut+4)return null;let a=Math.atan2(dy,dx)+Math.PI/2;a=((a%TAU)+TAU)%TAU;return{t:Math.floor(a/TAU*g.T),r:clamp(Math.floor((r-g.rIn)/g.t),0,g.K-1)}}
function drawSoloStage(dt,g,th,si){const x=slotIns(si),col=insColor(x,th),ink=th.cv.ink,so=S.solos[si]||{notes:[]},n=(SOLO_SCALE[S.scale]||SOLO_SCALE.minor).length,edit=S.edit==='S',ph=soloPhase(),off=ph>=0?Math.floor(ph*g.T):-1,circ=g.layout==='circle';
 const {c}=g;
 /* bir nota tek sürekli bar: adım parçaları boşluksuz (hafif bindirmeli, opak renk → dikiş yok), kenar payı yalnızca notanın iki ucunda */
 const bgv=rgbOf(th.cv.bg),opq=(colr,a)=>{const v=rgbOf(colr);return 'rgb('+Math.round(bgv[0]+(v[0]-bgv[0])*a)+','+Math.round(bgv[1]+(v[1]-bgv[1])*a)+','+Math.round(bgv[2]+(v[2]-bgv[2])*a)+')'};
 const span=(t0,t1,r,style,dash,e0,e1)=>{ctx.setLineDash(dash||[]);ctx.strokeStyle=style;if(circ){ctx.lineWidth=g.t*0.64;ctx.beginPath();ctx.arc(c,c,g.rIn+r*g.t+g.t/2,sAng(t0)+(e0?0.012:-0.004),sAng(t1)-(e1?0.012:-0.004));ctx.stroke()}else{const y=g.gridTop+(g.K-1-r)*g.rowH+g.rowH/2;ctx.lineWidth=g.rowH*0.64;ctx.beginPath();ctx.moveTo(g.x0+t0*g.colW+(e0?1:-0.5),y);ctx.lineTo(g.x0+t1*g.colW-(e1?1:-0.5),y);ctx.stroke()}ctx.setLineDash([])};
 const pt=(t,r,frac)=>{if(circ){const rr=g.rIn+r*g.t+g.t/2,a=sAng(t+frac);return[c+Math.cos(a)*rr,c+Math.sin(a)*rr]}return[g.x0+(t+frac)*g.colW,g.gridTop+(g.K-1-r)*g.rowH+g.rowH/2]};
 const th1=circ?g.t:g.rowH;
 /* rows */
 for(let r=0;r<g.K;r++){const root=r%n===0;if(circ){ctx.beginPath();ctx.arc(c,c,g.rIn+r*g.t+g.t/2,0,TAU);ctx.strokeStyle=hexA(col,root?0.16:0.07);ctx.lineWidth=g.t-1.5;ctx.stroke()}else{ctx.fillStyle=hexA(col,root?0.14:0.06);ctx.fillRect(g.x0,g.gridTop+(g.K-1-r)*g.rowH+0.75,g.x1-g.x0,g.rowH-1.5)}}
 /* steps */
 for(let s=0;s<=g.T;s++){const bar=s%MI.N===0,beat=MI.gsSet.has(s%MI.N);ctx.strokeStyle=hexA(ink,bar?0.5:beat?0.25:0.08);ctx.lineWidth=bar?1.5:1;ctx.beginPath();if(circ){if(s===g.T)continue;const a=sAng(s),ex=bar?8:beat?5:2;ctx.moveTo(c+Math.cos(a)*(g.rIn-2),c+Math.sin(a)*(g.rIn-2));ctx.lineTo(c+Math.cos(a)*(g.rOut+ex),c+Math.sin(a)*(g.rOut+ex))}else{const xx=g.x0+s*g.colW;ctx.moveTo(xx,g.gridTop-(bar?8:beat?4:0));ctx.lineTo(xx,g.gridTop+g.K*g.rowH)}ctx.stroke()}
 const drawNotes=(notes,colr,alphaM,selIdx,xx)=>notes.forEach((nt,i)=>{const row=nr(nt),a=artEff(xx,nt.art),L=noteLenEff(nt),isSel=i===selIdx,cc=isSel?th.cv.hot:colr;
  for(let k=0;k<L;k++){const p=k?tickPow(xx,k,a):1,t0=nt.t+k;if(p>0)span(t0,t0+1,row,opq(cc,(0.22+0.78*Math.min(1,p))*alphaM),null,k===0,k===L-1);else span(t0,t0+1,row,hexA(p<0?th.cv.hot:cc,0.45*alphaM),[3,4],k===0,k===L-1)}
  const [px,py]=pt(nt.t,row,0.5);ctx.beginPath();ctx.arc(px,py,th1*0.3,0,TAU);ctx.fillStyle=hexA(cc,alphaM);ctx.fill();
  if(a!=='none'&&L>1){const [qx,qy]=pt(nt.t,row,Math.min(L,3)-0.5+0.5);ctx.fillStyle=hexA(ink,0.9*alphaM);ctx.font='600 '+Math.max(8,Math.round(th1*0.55))+'px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(SOLO_ART[a].g,qx,qy)}
  if(isSel&&edit){const [hx,hy]=pt(nt.t+L-1,row,0.5);ctx.beginPath();ctx.arc(hx,hy,th1*0.42,0,TAU);ctx.fillStyle=th.cv.bg;ctx.fill();ctx.lineWidth=2;ctx.strokeStyle=th.cv.hot;ctx.stroke()}});
 const dp=duetPart(si);if(dp>=0){const ss=soloSlots().filter(s=>{const y=slotIns(s);return y&&y.fam!=='vur'});const other=ss[1-dp];if(other!=null&&other!==si){const y=slotIns(other);drawNotes(soloNotesOf(other),insColor(y,th),0.4,-1,y)}}
 drawNotes(so.notes,col,1,edit?soloSel:-1,x);
 /* labels */
 for(let r=0;r<g.K;r++){const root=r%n===0,fs=Math.max(8,Math.min(11,Math.round(th1*0.6)));let lx,ly;if(circ){const rr=g.rIn+r*g.t+g.t/2;lx=r%2?c+rr:c-rr;ly=c}else{lx=g.x0-fs*1.4;ly=g.gridTop+(g.K-1-r)*g.rowH+g.rowH/2}ctx.beginPath();ctx.arc(lx,ly,fs*0.8,0,TAU);ctx.fillStyle=hexA(th.cv.bg,0.85);ctx.fill();ctx.fillStyle=hexA(ink,root?0.95:0.6);ctx.font=(root?'600 ':'500 ')+fs+'px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(soloNoteName(r),lx,ly)}
 ctx.fillStyle=hexA(ink,0.5);ctx.font='500 10px '+th.font.m;ctx.textAlign='center';if(circ){ctx.textBaseline='bottom';ctx.fillText(T('1. ölçü'),c,c-g.rOut-11);ctx.textBaseline='top';ctx.fillText(T('2. ölçü'),c,c+g.rOut+11)}else{ctx.textBaseline='bottom';ctx.textAlign='left';ctx.fillText(T('1. ölçü'),g.x0+3,g.gridTop-10);ctx.fillText(T('2. ölçü'),g.x0+MI.N*g.colW+3,g.gridTop-10)}
 /* needle + sounding glow */
 if(ph>=0){ctx.strokeStyle=hexA(th.cv.acc,0.9);ctx.lineWidth=1.5;ctx.beginPath();if(circ){const a=sAng(ph*g.T);ctx.moveTo(c+Math.cos(a)*g.r0*1.1,c+Math.sin(a)*g.r0*1.1);ctx.lineTo(c+Math.cos(a)*(g.rOut+3),c+Math.sin(a)*(g.rOut+3))}else{const xx=g.x0+ph*(g.x1-g.x0);ctx.moveTo(xx,g.gridTop-12);ctx.lineTo(xx,g.gridTop+g.K*g.rowH+2)}ctx.stroke();
  if(soloNow===si)so.notes.forEach(nt=>{const L=noteLenEff(nt);if(off>=nt.t&&off<nt.t+L){const k=off-nt.t,p=k?tickPow(x,k,artEff(x,nt.art)):1;if(p<=0)return;const [qx,qy]=pt(off,nr(nt),0.5);ctx.beginPath();ctx.arc(qx,qy,th1*(0.5+0.6*Math.min(1.2,p)),0,TAU);ctx.fillStyle=hexA(col,0.35);ctx.fill()}})}
 /* badges */
 if(S.up.sseyir){const A=analyzeSolo(si);const items=[[A.karar,T('KARAR')],[A.doruk,T('DORUK')],[A.sc,T('SORU-CEVAP')]];ctx.font='600 9px '+th.font.m;ctx.textAlign='center';ctx.textBaseline='middle';const y=circ?c+g.r0*1.9:g.gridTop-24;const ws=items.map(([,l])=>ctx.measureText(l).width),gap=circ?Math.max(8,g.r0*0.35):14;let bx=c-(ws[0]+ws[1]+ws[2]+gap*2)/2;items.forEach(([on,l],i)=>{ctx.fillStyle=hexA(on?th.cv.acc:ink,on?0.95:0.3);ctx.fillText(l,bx+ws[i]/2,y);bx+=ws[i]+gap});if(A.mg){ctx.fillStyle=hexA(th.cv.hot,0.9);ctx.fillText(T('MAKİNELİ')+' −'+A.mg,c,y+12)}}
 if(dorukFlash>0){dorukFlash=Math.max(0,dorukFlash-dt*0.8);ctx.globalAlpha=Math.min(1,dorukFlash);ctx.fillStyle=col;ctx.font='600 '+Math.round(0.07*L)+'px '+th.font.d;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(T('DORUK'),c,circ?c-g.rOut*0.5:0.2*L);ctx.globalAlpha=1}
}
function hitTest(e){
 const b=vis().getBoundingClientRect(),x=(e.clientX-b.left)/b.width*L,y=(e.clientY-b.top)/b.height*L,g=geom();
 if(g.layout==='strip'){if(y<g.gridTop-6)return{core:true};const i=Math.floor((y-g.gridTop)/g.rowH),s=Math.floor((x-g.x0)/g.colW);if(i<0||i>=S.slots.length||s<0||s>=MI.N)return null;return{i,s}}
 const dx=x-g.c,dy=y-g.c,r=Math.hypot(dx,dy);
 if(r<g.r0*1.05)return{core:true};if(r<g.rIn||r>g.rOut)return null;
 let a=(Math.atan2(dy,dx)+Math.PI/2-rot)*dirS;a=((a%TAU)+TAU)%TAU;
 return{i:Math.min(S.slots.length-1,Math.floor((r-g.rIn)/g.t)),s:Math.floor(a/SEG())%MI.N};
}
(function bindCanvas(){const el=vis();
 let sDrag=null;
 el.addEventListener('pointerdown',e=>{const si=soloView();if(si<0||S.edit!=='S')return;const h=soloStageHit(e);if(!h||h.core)return;e.preventDefault();if(el.setPointerCapture)try{el.setPointerCapture(e.pointerId)}catch(err){}const so=S.solos[si]||(S.solos[si]={notes:[],style:'hendrix'});
  const j=so.notes.findIndex(m=>nr(m)===h.r&&h.t>=m.t&&h.t<m.t+noteLenEff(m));
  if(j>=0){soloSel=j;const m=so.notes[j];const tail=h.t===m.t+noteLenEff(m)-1;sDrag=tail&&S.up.suzun?{mode:'len',j}:{mode:'move',j,dt:h.t-m.t}}
  else{if(so.notes.length>=SOLO_MAX){msg('En fazla '+SOLO_MAX+' solo notası');return}so.notes.push({t:h.t,len:1,r:h.r,art:'none'});so.notes.sort((a,b)=>a.t-b.t);soloSel=so.notes.findIndex(m=>m.t===h.t&&m.r===h.r);sDrag={mode:S.up.suzun?'len':'move',j:soloSel,dt:0};if(!playing){ensureAudio();soloVoice(slotIns(si),ac.currentTime+0.01,h.r,0.35,'none',1)}}
  renderSoloTb()});
 el.addEventListener('pointermove',e=>{if(sDrag){const si=soloView();if(si<0)return;const h=soloStageHit(e);if(!h||h.core)return;const so=S.solos[si];const m=so&&so.notes[sDrag.j];if(!m)return;const T=soloSteps(),sus=!!S.up.suzun;let ch=false;
   /* uzun nota açıkken çakışma engel değil: sürüklenen bar değdiği barları yutar (soloMerge); kapalıyken eski davranış, üst üste binme yok */
   const ov=(t,len,r,j)=>!sus&&so.notes.some((q,k)=>k!==j&&nr(q)===r&&t<q.t+noteLenEff(q)&&q.t<t+len);
   if(sDrag.mode==='len'){if(h.r!==nr(m)&&!ov(m.t,m.len,h.r,sDrag.j)){m.r=h.r;ch=true}const len=clamp(h.t-m.t+1,1,T-m.t);if(len!==m.len&&!ov(m.t,len,nr(m),sDrag.j)){m.len=len;ch=true}}
   else{const t=clamp(h.t-sDrag.dt,0,T-noteLenEff(m));if((t!==m.t||h.r!==nr(m))&&!ov(t,noteLenEff(m),h.r,sDrag.j)){m.t=t;m.r=h.r;ch=true}}
   if(ch){if(sus){const n0=so.notes.length;sDrag.j=soloMerge(so,m);soloSel=sDrag.j;sDrag.dt=h.t-m.t;if(so.notes.length<n0)msg('Barlar birleşti · '+soloNoteName(nr(m))+' · '+m.len+' adım')}renderSoloTb()}return}
  if(soloView()>=0){hover=null;el.style.cursor=S.edit==='S'?'crosshair':'default';return}const h=hitTest(e);hover=h&&!h.core?h:null;el.style.cursor=h?'pointer':'default';hintFor(hover)});
 const sUp=()=>{if(!sDrag)return;sDrag=null;const si=soloView();const so=si>=0&&S.solos[si];if(so){const selN=so.notes[soloSel];so.notes.sort((a,b)=>a.t-b.t);soloSel=selN?so.notes.indexOf(selN):-1}recalc();updUI();renderSoloBox();renderPads()};
 el.addEventListener('pointerup',sUp);el.addEventListener('pointercancel',sUp);
 el.addEventListener('pointerleave',()=>{hover=null;hintFor(null)});
 el.addEventListener('click',e=>{if(soloView()>=0){const hs=soloStageHit(e);if(hs&&hs.core)tap();return}const h=hitTest(e);if(!h||h.core){tap();return}if(PH()){eSel=h.i}cellClick(h.i,h.s);if(PH())renderPads()});
 document.addEventListener('pointerdown',()=>{if(ac&&ac.state==='suspended')ac.resume()},{passive:true});
})();
let lastF=performance.now();
function frame(ms){
 const dt=Math.min(0.05,Math.max(0,(ms-lastF)/1000));lastF=ms;clock+=dt;
 if(previewId&&ms>=previewUntil){previewId=null;applyTheme();msg('Önizleme bitti')}
 if(playing&&ac){const now=ac.currentTime;
  while(queue.length&&queue[0].t<=now)onStep(queue.shift());
  while(grid.length>1&&grid[1].t<=now)grid.shift();
  if(grid.length&&grid[0].t<=now){const e=grid[0];phase=(e.s+Math.min(1,(now-e.t)/e.sd))/e.N}
  for(let k=2;k<=3;k++){const nd=NS[k-1];while(nd.grid.length>1&&nd.grid[1].t<=now)nd.grid.shift();if(nd.grid.length&&nd.grid[0].t<=now){const e=nd.grid[0];const fr=Math.min(1,(now-e.t)/e.sd);const ph=(e.dir>0?(e.s+fr):(e.s+1-fr))/e.N;if(k===2)phase2=ph;else phase3=ph}}
  logic(now);
 }
 drawScene(dt);
 {const ta=(soloView()>=0&&S.edit==='S')?'none':'manipulation';const el=vis();if(el.style.touchAction!==ta)el.style.touchAction=ta}
 if(GLX&&!lowQ&&PH()&&clock>3){slowT=dt>0.034?slowT+dt:0;if(slowT>2){lowQ=true;msg('Telefon için hafif çizim moduna geçildi: iz ve parlama kapalı')}}
 if(GLX){const th=dispTheme(),fx={};FXK.forEach(([k])=>fx[k]=fxVal(th,k));if(RM){fx.glitch=0;fx.trail=0}if(lowQ){fx.trail=0;fx.bloom=0;fx.glitch=0;fx.kaleid=0}try{GLX.render(scene,fx,clock,kickP,th)}catch(err){console.warn(err)}}
 requestAnimationFrame(frame);
}

/* ================= boot ================= */
recalc();core.hp=hpMax();ensureOrders();applyTheme();setTab(isPhone()?'stage':'studio');hintFor(null);tutShow();if(S.lang==='en'){document.documentElement.lang='en';$('app').lang='en';i18n(document.body);$('langBtn').textContent='TR'}
const away=Math.min((Date.now()-(S.last||Date.now()))/1000,8*3600);
if(away>30){const g=rate()*away*0.5;if(g>=1){earn(g);setTimeout(()=>msg('Sen yokken döngün ♪ '+fmt(g)+' kazandırdı · kuşatma seni bekledi'),300)}}
updUI();
setInterval(updUI,150);
setInterval(()=>{if(S.orders.some(o=>!o.tpl&&o.ready&&Date.now()>=o.ready)){renderDef();i18n($('p-def'))}else if(S.orders.some(o=>!o.tpl)){renderDef();i18n($('p-def'))}},1000);
setInterval(save,5000);setInterval(()=>{try{autoTick()}catch(e){console.warn(e)}},2000);
document.addEventListener('visibilitychange',()=>{if(document.hidden)save()});
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{bgKey=''});
window.__nb={get S(){return S},ff:ffSim,rate,dps,recalc,renderPanels,setWave,get enemies(){return enemies},get wave(){return wave},get core(){return core},IDX,INS,get playing(){return playing},get soloNow(){return soloNow},get curBar(){return curBar},soloVoice:(id,row,hold,art)=>{ensureAudio();soloVoice(IDX[id],ac.currentTime+0.01,row,hold,art,1);return true},genSolo,testVoice:(id,s)=>{ensureAudio();const x=IDX[id];SOLO_F=0;GEN[x.v.g](ac.currentTime+0.01,1,x.v,s||0);return true},soloFreq,tickPow,analyzeSolo,artOk,noteSus,soloView:()=>soloView(),sgeom:()=>sgeom(),get soloEdSlot(){return soloEdSlot},set soloEdSlot(v){soloEdSlot=v},get soloSel(){return soloSel},get L(){return L},setEdit(v){S.edit=v;renderPanels();updUI()},renderPads,get lowQ(){return lowQ},parseCode,exportCode,curChord,chordName,kadansAt,contrastM,transM,fillHits,fillBar,cellClick,get crashFlash(){return crashFlash},get transText(){return transText},planAvg,autoTick,autoReset:()=>{autoT=0},sfLoad,SF,sfReady:id=>sfReady(IDX[id]),sfVoice:(id,s)=>{ensureAudio();return sfVoice(IDX[id],ac.currentTime+0.02,1,s||0)},get sfDir(){return SF_DIR},set sfDir(v){SF_DIR=v},get sfVol(){return SF_VOL},set sfVol(v){SF_VOL=v},sfDrum:(id,t,a,s)=>{ensureAudio();return sfDrum(IDX[id],t||ac.currentTime+0.02,a||1,s||0)},sfSolo:(id,t,row,hold,art,a)=>{ensureAudio();return sfSolo(IDX[id],t||ac.currentTime+0.02,row||0,hold||1,art||'none',a||1)},soloVoice:(id,t,row,hold,art,a)=>{ensureAudio();soloVoice(IDX[id],t||ac.currentTime+0.02,row||0,hold||1,art||'none',a||1)},voice:(id,t,v,s)=>{ensureAudio();voice(IDX[id],t||ac.currentTime+0.02,v||1,s||0)},get ac(){return ac},get analyser(){return analyser},get playingNow(){return playing},goTour,tourM,cityOf,albUnl,waveComp,get demoMode(){return demoMode},get demoIdx(){return demoIdx},DEMOS,enterDemo,exitDemo,soloMerge,sAng,get scene(){return scene},get dorukFlash(){return dorukFlash}};
requestAnimationFrame(frame);
})();
</script>
