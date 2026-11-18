"use strict";

const desktop = document.getElementById("desktop");
const launcher = document.getElementById("launcher");
const appsContainer = document.getElementById("apps");
const toastElement = document.getElementById("toast");

document.getElementById("app-window").remove();

const catalog = [
  ["files","Files","▣"],
  ["notes","Notes","▤"],
  ["settings","Appearance","⚙"],
  ["calendar","Calendar","▦"],
  ["calculator","Calculator","⌗"],
  ["gallery","Gallery","▧"],
  ["music","Music","♫"],
  ["terminal","Terminal","⌘"],
  ["monitor","System Monitor","◉"],
  ["about","About LIFE","◈"]
];

const names = Object.fromEntries(catalog.map(a=>[a[0],a[1]]));
const windows = new Map();
const filesState = new Map();
let topZ = 20;
let toastTimer;
let calendarOffset = 0;

const folders = {
  Home:["Desktop","Documents","Downloads","Pictures","Music","Videos","Projects"],
  Desktop:["Welcome to LIFE OS.txt","LIFE Appearance.desktop"],
  Documents:["Welcome.txt","Study Notes.txt"],
  Downloads:["Downloads are empty"],
  Pictures:["Wallpapers","Memories"],
  Music:["Albums","Playlists"],
  Videos:["Video Library"],
  Projects:["LIFE OS","My Projects"],
  Wallpapers:["LIFE Flow","Mountain Mist"],
  Memories:[],
  Albums:[],
  Playlists:[],
  "LIFE OS":["README.md"],
  "My Projects":[]
};

function safeText(value){
  return String(value).replace(/[&<>"']/g,c=>({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  })[c]);
}

function showToast(message){
  toastElement.textContent=message;
  toastElement.style.display="block";
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>toastElement.style.display="none",2600);
}

function refreshClock(){
  document.getElementById("clock").textContent=
    new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"});
}
refreshClock();
setInterval(refreshClock,30000);

function toggleLauncher(){
  launcher.classList.toggle("show");
  if(launcher.classList.contains("show")){
    document.getElementById("search").focus();
  }
}

function filterApps(value){
  for(const button of appsContainer.querySelectorAll("button")){
    button.hidden=!button.dataset.name.toLowerCase().includes(value.toLowerCase());
  }
}

function focusApp(id){
  const record=windows.get(id);
  if(!record)return;
  record.element.style.zIndex=String(++topZ);
  record.element.style.display="flex";
  record.minimized=false;
  updateDock();
}

function updateDock(){
  for(const button of document.querySelectorAll(".dock button[data-app]")){
    const record=windows.get(button.dataset.app);
    button.classList.toggle("on",Boolean(record&&!record.minimized));
  }
}

function closeWindow(id){
  const record=windows.get(id);
  if(!record)return;
  record.element.remove();
  windows.delete(id);
  updateDock();
}

function minimizeWindow(id){
  const record=windows.get(id);
  if(!record)return;
  record.element.style.display="none";
  record.minimized=true;
  updateDock();
}

function toggleMaximize(id){
  const record=windows.get(id);
  if(!record)return;
  record.element.classList.toggle("maximized");
  focusApp(id);
}

function makeWindow(id){
  const section=document.createElement("section");
  section.className="window";
  section.style.display="flex";
  section.style.left=(21+(windows.size%5)*4)+"%";
  section.style.top=(12+(windows.size%5)*5)+"%";
  section.style.zIndex=String(++topZ);

  section.innerHTML=`
    <div class="window-head">
      <div class="dots">
        <button class="dot red" title="Close"></button>
        <button class="dot yellow" title="Minimize"></button>
        <button class="dot green" title="Maximize"></button>
      </div>
      <strong>${safeText(names[id])}</strong>
    </div>
    <div class="window-content"></div>
  `;

  section.querySelector(".red").onclick=()=>closeWindow(id);
  section.querySelector(".yellow").onclick=()=>minimizeWindow(id);
  section.querySelector(".green").onclick=()=>toggleMaximize(id);

  const head=section.querySelector(".window-head");
  let drag=null;
  head.addEventListener("pointerdown",e=>{
    if(e.target.closest("button")||section.classList.contains("maximized"))return;
    focusApp(id);
    const box=section.getBoundingClientRect();
    drag={x:e.clientX-box.left,y:e.clientY-box.top};
    head.setPointerCapture(e.pointerId);
  });
  head.addEventListener("pointermove",e=>{
    if(!drag)return;
    section.style.left=Math.max(0,Math.min(innerWidth-section.offsetWidth,e.clientX-drag.x))+"px";
    section.style.top=Math.max(43,Math.min(innerHeight-section.offsetHeight,e.clientY-drag.y))+"px";
  });
  head.addEventListener("pointerup",()=>drag=null);
  head.addEventListener("pointercancel",()=>drag=null);
  section.addEventListener("pointerdown",()=>focusApp(id));

  desktop.appendChild(section);
  windows.set(id,{element:section,minimized:false});
  updateDock();
  return section.querySelector(".window-content");
}

function openApp(id){
  if(!names[id])return;
  launcher.classList.remove("show");
  if(windows.has(id)){focusApp(id);return;}
  const content=makeWindow(id);
  renderApp(id,content);
}

function appContent(id){
  return windows.get(id)?.element.querySelector(".window-content");
}

function setLayout(id){
  if(!["flow","center","classic","minimal"].includes(id))return;
  document.body.dataset.layout=id;
  localStorage.setItem("life-layout",id);
  if(windows.has("settings"))renderSettings(appContent("settings"));
  showToast("LIFE "+id[0].toUpperCase()+id.slice(1)+" layout selected");
}

function setTheme(id){
  if(!["light","dark"].includes(id))return;
  document.body.dataset.theme=id;
  localStorage.setItem("life-theme",id);
  if(windows.has("settings"))renderSettings(appContent("settings"));
  showToast(id==="dark"?"Deep Night enabled":"Warm Light enabled");
}

function renderSettings(content){
  const currentLayout=document.body.dataset.layout;
  const currentTheme=document.body.dataset.theme;
  content.innerHTML=`
    <div class="app-main">
      <h2>LIFE Appearance</h2>
      <p>Make your workspace feel like yours.</p>
    </div>
    <div class="setting-group">
      <h3>Desktop layouts</h3>
      <p class="hint">Four interactive preview arrangements.</p>
      <div class="option-grid" id="layout-options"></div>
    </div>
    <div class="setting-group">
      <h3>Color appearance</h3>
      <div class="option-grid" id="theme-options"></div>
    </div>
    <div class="setting-group">
      <h3>Desktop edition</h3>
      <p class="hint">LIFE Lite — XFCE · LIFE Standard — KDE Plasma</p>
      <p class="hint">This web preview doesn't yet alter the real Linux panels.</p>
    </div>`;

  const layouts={flow:"◈ LIFE Flow",center:"▦ LIFE Center",classic:"▤ LIFE Classic",minimal:"◇ LIFE Minimal"};
  for(const [id,name] of Object.entries(layouts)){
    const button=document.createElement("button");
    button.className="choice"+(currentLayout===id?" active":"");
    button.textContent=name;
    button.onclick=()=>setLayout(id);
    content.querySelector("#layout-options").append(button);
  }
  for(const [id,name] of [["light","☀ Warm Light"],["dark","☾ Deep Night"]]){
    const button=document.createElement("button");
    button.className="choice"+(currentTheme===id?" active":"");
    button.textContent=name;
    button.onclick=()=>setTheme(id);
    content.querySelector("#theme-options").append(button);
  }
}

function renderFiles(content,id){
  const selected=filesState.get(id)||"Home";
  const entries=folders[selected]||[];
  content.innerHTML=`
    <div class="toolbar">
      <button id="files-home">⌂ Home</button>
      <button id="files-back">←</button>
      <div class="address" id="files-address"></div>
    </div>
    <div class="app-shell">
      <aside class="app-sidebar" id="file-sidebar"></aside>
      <main class="app-main">
        <h2 id="folder-heading"></h2>
        <p>Browse your LIFE OS workspace.</p>
        <div class="folder-grid" id="folder-grid"></div>
        <div class="hint">Demo folders only — no access to your real files.</div>
      </main>
    </div>`;
  content.querySelector("#files-address").textContent="Home"+(selected==="Home"?"":"/"+selected);
  content.querySelector("#folder-heading").textContent=selected;
  content.querySelector("#files-home").onclick=()=>goFolder(id,"Home");
  content.querySelector("#files-back").onclick=()=>goFolder(id,"Home");

  const sidebar=content.querySelector("#file-sidebar");
  for(const folder of folders.Home){
    const button=document.createElement("button");
    button.textContent=({Desktop:"▧",Documents:"▤",Downloads:"↓",Pictures:"▣",Music:"♫",Videos:"▷",Projects:"◇"}[folder]||"▣")+"  "+folder;
    button.className=selected===folder?"selected":"";
    button.onclick=()=>goFolder(id,folder);
    sidebar.append(button);
  }

  const grid=content.querySelector("#folder-grid");
  if(!entries.length){
    const empty=document.createElement("p");
    empty.textContent="Nothing here yet.";
    grid.append(empty);
  }
  for(const entry of entries){
    const isFolder=Object.hasOwn(folders,entry);
    const button=document.createElement("button");
    button.className="folder-tile";
    const symbol=document.createElement("span");
    symbol.className="symbol";
    symbol.textContent=isFolder?"📁":entry.endsWith(".md")?"▤":"▧";
    const name=document.createElement("b");
    name.textContent=entry;
    const meta=document.createElement("small");
    meta.textContent=isFolder?"Folder":"Sample file";
    button.append(symbol,name,meta);
    button.onclick=()=>isFolder?goFolder(id,entry):showToast("Sample file: "+entry);
    grid.append(button);
  }
}

function goFolder(id,folder){
  filesState.set(id,folder);
  renderFiles(appContent(id),id);
}

function renderNotes(content){
  content.innerHTML=`
    <div class="app-main">
      <h2>A little space to think.</h2>
      <p>Write down ideas, plans, and the things worth keeping.</p>
      <input class="app-input" id="life-note-title" placeholder="Note title">
      <div style="height:12px"></div>
      <textarea class="app-input app-textarea" id="life-note-body" placeholder="Start writing..."></textarea>
      <p>Saved locally in this browser preview, separate from the LIFE OS SQLite notes database.</p>
    </div>`;
  const title=content.querySelector("#life-note-title");
  const body=content.querySelector("#life-note-body");
  title.value=localStorage.getItem("life-preview-title")||"";
  body.value=localStorage.getItem("life-preview-note")||"";
  title.addEventListener("input",()=>localStorage.setItem("life-preview-title",title.value));
  body.addEventListener("input",()=>localStorage.setItem("life-preview-note",body.value));
}

function renderCalendar(content){
  content.innerHTML=`
    <div class="app-main">
      <h2 id="calendar-heading">Calendar</h2>
      <p>One day at a time.</p>
      <div class="option-grid">
        <button class="choice" id="month-prev">← Previous</button>
        <button class="choice" id="month-today">Today</button>
        <button class="choice" id="month-next">Next →</button>
      </div>
      <div class="calendar-grid" id="days"></div>
    </div>`;
  const now=new Date();
  const date=new Date(now.getFullYear(),now.getMonth()+calendarOffset,1);
  content.querySelector("#calendar-heading").textContent=date.toLocaleDateString([], {month:"long",year:"numeric"});
  const grid=content.querySelector("#days");
  for(const day of ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]){
    const div=document.createElement("div");div.textContent=day;grid.append(div);
  }
  for(let i=0;i<date.getDay();i++)grid.append(document.createElement("div"));
  const total=new Date(date.getFullYear(),date.getMonth()+1,0).getDate();
  for(let n=1;n<=total;n++){
    const div=document.createElement("div");div.textContent=String(n);
    if(n===now.getDate()&&date.getMonth()===now.getMonth()&&date.getFullYear()===now.getFullYear())div.className="today";
    grid.append(div);
  }
  for(const [selector,change] of [["#month-prev",-1],["#month-next",1],["#month-today",null]]){
    content.querySelector(selector).onclick=()=>{
      calendarOffset=change===null?0:calendarOffset+change;
      renderCalendar(content);
    };
  }
}

function renderCalculator(content){
  content.innerHTML='<div class="app-main"><h2>Calculator</h2><p>Simple, useful, always nearby.</p><div class="calc" id="calc"><div class="calc-display" id="calc-value">0</div></div></div>';
  const grid=content.querySelector("#calc");
  const display=content.querySelector("#calc-value");
  let expression="";
  for(const key of ["C","(",")","÷","7","8","9","×","4","5","6","−","1","2","3","+","0",".","⌫","="]){
    const button=document.createElement("button");
    button.textContent=key;
    button.onclick=()=>{
      if(key==="C")expression="";
      else if(key==="⌫")expression=expression.slice(0,-1);
      else if(key==="="){
        const normalized=expression.replaceAll("×","*").replaceAll("÷","/").replaceAll("−","-");
        try{
          if(!/^[\d+\-*/().\s]+$/.test(normalized)||!normalized.trim())throw Error();
          // A small expression parser is safer than evaluating arbitrary JS.
          const tokens=normalized.match(/\d+(?:\.\d+)?|[()+\-*/]/g);
          if(!tokens||tokens.join("")!==normalized.replace(/\s/g,""))throw Error();
          let pos=0;
          function factor(){
            const t=tokens[pos++];
            if(t==="+")return factor();
            if(t==="-")return -factor();
            if(t==="("){const v=sum();if(tokens[pos++]!==")")throw Error();return v;}
            const n=Number(t);if(!Number.isFinite(n))throw Error();return n;
          }
          function product(){
            let v=factor();
            while(tokens[pos]==="*"||tokens[pos]==="/"){
              const op=tokens[pos++],rhs=factor();
              v=op==="*"?v*rhs:v/rhs;
            }
            return v;
          }
          function sum(){
            let v=product();
            while(tokens[pos]==="+"||tokens[pos]==="-"){
              const op=tokens[pos++],rhs=product();
              v=op==="+"?v+rhs:v-rhs;
            }
            return v;
          }
          const result=sum();
          if(pos!==tokens.length||!Number.isFinite(result))throw Error();
          expression=String(Number(result.toPrecision(12)));
        }catch{expression="Error";}
      }else expression=(expression==="Error"?"":expression)+key;
      display.textContent=expression||"0";
    };
    grid.append(button);
  }
}

function renderGallery(content){
  content.innerHTML=`
    <div class="app-main">
      <h2>Gallery</h2><p>Spaces, colors, and moments.</p>
      <div class="folder-grid">
        <div class="folder-tile" style="background:linear-gradient(145deg,#e5d7cd,#9bbbc5);height:145px"><span class="symbol">☀</span><b>Morning Haze</b></div>
        <div class="folder-tile" style="background:linear-gradient(145deg,#263e58,#7995af);height:145px;color:white"><span class="symbol">☾</span><b>Deep Night</b></div>
        <div class="folder-tile" style="background:linear-gradient(145deg,#e9d9e2,#a9c8da);height:145px"><span class="symbol">✿</span><b>Soft Sky</b></div>
      </div><p>Sample wallpaper collection. Actual image-library integration comes later.</p>
    </div>`;
}

function renderMusic(content){
  content.innerHTML=`
    <div class="app-main">
      <h2>Music</h2><p>Your sound. Your space.</p>
      <div id="track-list"></div>
      <p>Sample library — audio playback and file scanning aren't implemented in this preview.</p>
    </div>`;
  for(const [title,detail] of [["Quiet Horizon","Ambient collection"],["Morning Light","Focus playlist"],["After Hours","Night playlist"]]){
    const row=document.createElement("div");row.className="music-track";
    row.innerHTML='<div class="music-cover">♫</div><div><strong></strong><small></small></div>';
    row.querySelector("strong").textContent=title;
    row.querySelector("small").textContent=detail;
    content.querySelector("#track-list").append(row);
  }
}

function renderTerminal(content){
  content.innerHTML=`
    <div class="app-main">
      <h2>Terminal Preview</h2>
      <p>A simulated terminal. No real system commands are executed.</p>
      <div class="terminal" id="terminal-output">LIFE OS — Preview Terminal
Type help, about, date, whoami, or clear.
</div>
      <input class="app-input" id="terminal-input" placeholder="life@lifeos:~$" style="margin-top:12px">
    </div>`;
  const input=content.querySelector("#terminal-input");
  const output=content.querySelector("#terminal-output");
  input.addEventListener("keydown",e=>{
    if(e.key!=="Enter")return;
    const cmd=input.value.trim();input.value="";
    if(cmd==="clear"){output.textContent="";return;}
    const answers={
      help:"Available preview commands: help, about, date, whoami, clear",
      about:"LIFE OS — a student-focused Linux desktop project",
      date:new Date().toString(),
      whoami:"life (simulated)"
    };
    output.textContent+="\nlife@lifeos:~$ "+cmd+"\n"+(answers[cmd]||"Not supported in preview")+"\n";
    output.scrollTop=output.scrollHeight;
  });
}

function renderMonitor(content){
  content.innerHTML=`
    <div class="app-main">
      <h2>System Monitor</h2>
      <p>Preview metrics, not live hardware telemetry.</p>
      <div class="tile"><b>CPU — Demo 24%</b><div class="statbar"><div style="width:24%"></div></div></div>
      <div style="height:12px"></div>
      <div class="tile"><b>Memory — Demo 43%</b><div class="statbar"><div style="width:43%"></div></div></div>
      <div style="height:12px"></div>
      <div class="tile"><b>Disk — Demo 28%</b><div class="statbar"><div style="width:28%"></div></div></div>
      <p>Native system monitoring will use Linux process and hardware data.</p>
    </div>`;
}

function renderApp(id,content){
  if(id==="files")renderFiles(content,id);
  else if(id==="notes")renderNotes(content);
  else if(id==="settings")renderSettings(content);
  else if(id==="calendar")renderCalendar(content);
  else if(id==="calculator")renderCalculator(content);
  else if(id==="gallery")renderGallery(content);
  else if(id==="music")renderMusic(content);
  else if(id==="terminal")renderTerminal(content);
  else if(id==="monitor")renderMonitor(content);
  else content.innerHTML='<div class="app-main"><h2>LIFE OS</h2><p>Live Intuitively. Focus Effortlessly.</p><div class="tile"><b>Milestone 7 — Visual Preview 2.0</b><p>A calm desktop experience designed for LIFE Lite and LIFE Standard.</p></div></div>';
}

appsContainer.replaceChildren();
for(const [id,name,symbol] of catalog){
  const button=document.createElement("button");
  button.dataset.name=name;
  button.innerHTML='<span class="app-launch-icon"></span><small></small>';
  button.querySelector("span").textContent=symbol;
  button.querySelector("small").textContent=name;
  button.onclick=()=>openApp(id);
  appsContainer.append(button);
}

const dock=document.querySelector(".dock");
dock.replaceChildren();
const launcherButton=document.createElement("button");
launcherButton.textContent="◈";
launcherButton.title="App Launcher";
launcherButton.onclick=toggleLauncher;
dock.append(launcherButton);
const separator=document.createElement("div");separator.className="sep";dock.append(separator);
for(const id of ["files","notes","calendar","music","settings"]){
  const app=catalog.find(a=>a[0]===id);
  const button=document.createElement("button");
  button.dataset.app=id;
  button.textContent=app[2];
  button.title=app[1];
  button.onclick=()=>openApp(id);
  dock.append(button);
}

for(const [key,storage] of [["layout","life-layout"],["theme","life-theme"]]){
  const saved=localStorage.getItem(storage);
  if((key==="layout"?["flow","center","classic","minimal"]:["light","dark"]).includes(saved)){
    document.body.dataset[key]=saved;
  }
}

document.addEventListener("keydown",e=>{
  if(e.key==="Escape")launcher.classList.remove("show");
});
