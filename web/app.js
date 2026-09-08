const membersEl = document.querySelector('#members');
const form = document.querySelector('#planner-form');
const errorEl = document.querySelector('#error');
let lastInput = null;
let currentPlanId = null;
let currentProjectKey = null;

const defaults = [
  {name:'민수',skills:'Unity:4, Programming:4, AI:2, Git:3',preferred:'Gameplay Programmer',avoid:'UI',hours:12,learning:'Enemy AI'},
  {name:'지수',skills:'Unity:3, UI:5, Game Design:4, Art:3',preferred:'UI Designer',avoid:'',hours:10,learning:'Progression'}
];

function memberCard(data={}) {
  const el=document.createElement('article');
  el.className='member';
  el.innerHTML=`<h3>TEAM MEMBER</h3><button class="remove" type="button" aria-label="팀원 삭제">삭제</button><div class="grid three"><label>이름<input data-k="name" required value="${data.name||''}"></label><label>기술 스택 · 숙련도<input data-k="skills" required placeholder="Unity:4, UI:3" value="${data.skills||''}"></label><label>주당 가용 시간<input data-k="hours" type="number" min="1" max="80" required value="${data.hours||10}"></label><label>선호 역할<input data-k="preferred" placeholder="Gameplay Programmer" value="${data.preferred||''}"></label><label>기피 역할<input data-k="avoid" placeholder="UI" value="${data.avoid||''}"></label><label>학습 관심 분야<input data-k="learning" placeholder="Enemy AI" value="${data.learning||''}"></label><label>게임 개발 경험<input data-k="experience" placeholder="Unity 2D 프로젝트 1회" value="${data.experience||''}"></label><label>관련 프로젝트<input data-k="projects" placeholder="게임잼 액션 게임" value="${data.projects||''}"></label></div>`;
  el.querySelector('.remove').onclick=()=>membersEl.children.length>2?el.remove():showError('팀원은 최소 2명이어야 합니다.');
  membersEl.append(el);
}

defaults.forEach(memberCard);
document.querySelector('#add-member').onclick=()=>membersEl.children.length<6?memberCard():showError('팀원은 최대 6명까지 입력할 수 있습니다.');
const list=value=>(value||'').split(',').map(v=>v.trim()).filter(Boolean);
const skills=value=>Object.fromEntries(list(value).map(item=>{const [name,level='3']=item.split(':');return [name.trim(),Math.max(0,Math.min(5,Number(level)||0))]}));

function input() {
  const fd=new FormData(form);
  return {project:{name:fd.get('name'),genre:fd.get('genre'),engine:fd.get('engine'),dimension:fd.get('dimension'),platform:fd.get('platform'),duration_weeks:Number(fd.get('duration')),deadline:fd.get('deadline'),goal:fd.get('goal'),content_scale:fd.get('contentScale'),reference_games:list(fd.get('references')),mandatory_features:list(fd.get('features')),excluded_features:list(fd.get('excluded')),completed_features:list(fd.get('completed')),available_assets:list(fd.get('assets')),constraints:list(fd.get('constraints')),description:fd.get('description'),use_ai:fd.get('useAi')==='on'},members:[...membersEl.children].map((el,i)=>({id:`member_${String(i+1).padStart(2,'0')}`,name:el.querySelector('[data-k=name]').value,skills:skills(el.querySelector('[data-k=skills]').value),preferred_roles:list(el.querySelector('[data-k=preferred]').value),avoid_roles:list(el.querySelector('[data-k=avoid]').value),available_hours_per_week:Number(el.querySelector('[data-k=hours]').value),learning_interests:list(el.querySelector('[data-k=learning]').value),experience:el.querySelector('[data-k=experience]').value,related_projects:list(el.querySelector('[data-k=projects]').value)}))};
}

function fillForm(data) {
  const project=data.project||{};
  const fields={name:project.name,genre:project.genre,engine:project.engine,dimension:project.dimension,platform:project.platform,duration:project.duration_weeks,deadline:project.deadline,goal:project.goal,contentScale:project.content_scale,references:project.reference_games,features:project.mandatory_features,excluded:project.excluded_features,completed:project.completed_features,assets:project.available_assets,constraints:project.constraints,description:project.description};
  Object.entries(fields).forEach(([name,value])=>{const field=form.elements.namedItem(name);if(field)field.value=Array.isArray(value)?value.join(', '):(value??'')});
  form.elements.namedItem('useAi').checked=project.use_ai!==false;
  membersEl.replaceChildren();
  (data.members||[]).forEach(member=>memberCard({name:member.name,skills:Object.entries(member.skills||{}).map(([name,level])=>`${name}:${level}`).join(', '),hours:member.available_hours_per_week,preferred:(member.preferred_roles||[]).join(', '),avoid:(member.avoid_roles||[]).join(', '),learning:(member.learning_interests||[]).join(', '),experience:member.experience,projects:(member.related_projects||[]).join(', ')}));
}

async function request(path,payload,method) {
  errorEl.textContent='';
  const options={method:method||(payload?'POST':'GET')};
  if(payload){options.headers={'Content-Type':'application/json'};options.body=JSON.stringify(payload)}
  const res=await fetch(path,options),data=await res.json();
  if(!res.ok) throw new Error(data.error||'요청에 실패했습니다.');
  return data;
}

function showError(message){errorEl.textContent=message}
form.onsubmit=async event=>{event.preventDefault();await busy(form.querySelector('.primary'),async()=>{try{lastInput=input();render(await request('/api/plan',lastInput));loadSaved()}catch(error){showError(error.message)}})};
document.querySelector('#refine').onclick=async event=>{const revision=document.querySelector('#revision').value.trim();if(!revision)return;await busy(event.currentTarget,async()=>{try{render(await request('/api/refine',{input:lastInput,request:revision,parent_plan_id:currentPlanId}));loadSaved()}catch(error){showError(error.message)}})};

function render(data) {
  const results=document.querySelector('#results'),taskById=Object.fromEntries(data.tasks.map(t=>[t.id,t])),memberById=Object.fromEntries(lastInput.members.map(m=>[m.id,m]));
  currentPlanId=data.plan_id||data.id||currentPlanId;currentProjectKey=data.project_key||lastInput.project.id||currentProjectKey;if(currentProjectKey)lastInput.project.id=currentProjectKey;
  document.querySelector('#ai-mode').textContent=data.ai?.used?`AI · ${data.ai.model}`:'RULE ENGINE';
  document.querySelector('#plan-version').textContent=`PLAN v${data.version||1} · ${data.status||'draft'}`;
  document.querySelector('#result-name').textContent=`${data.project_analysis.name} 실행 계획`;
  document.querySelector('#result-summary').textContent=data.project_analysis.summary||`${data.project_analysis.genre} · ${data.project_analysis.engine} · ${data.project_analysis.development_priority}`;
  document.querySelector('#metrics').innerHTML=[['TASKS',data.tasks.length],['TEAM',data.project_analysis.team_size],['CONTEXT',data.harness.contexts.length],['TOOLS',data.harness.tools.length]].map(([k,v])=>`<div class="metric"><b>${v}</b><span>${k}</span></div>`).join('');
  const validation=document.querySelector('#validation');validation.textContent=data.validation.valid?'VALIDATED':'CHECK REQUIRED';validation.className=`badge ${data.validation.valid?'':'invalid'}`;
  document.querySelector('#core-loop').innerHTML=(data.project_analysis.core_loop?.length?data.project_analysis.core_loop:['입력 분석','핵심 구현','플레이테스트']).map(item=>`<span>${escapeHtml(item)}</span>`).join('');
  const notice=document.querySelector('#ai-notice');notice.hidden=!data.ai?.fallback_reason;notice.textContent=data.ai?.fallback_reason||'';
  document.querySelector('#tasks').innerHTML=data.assignments.map((a,i)=>{const t=taskById[a.task_id],m=memberById[a.member_id],skills=Object.entries(t.required_skills).map(([name,level])=>`${name} ${level}/5`).join(', ');return `<article class="task"><span class="task-num">${String(i+1).padStart(2,'0')}</span><div><h4>${escapeHtml(t.name)} <span class="badge">${escapeHtml(t.category)}</span></h4><p>${escapeHtml(m.name)} · ${escapeHtml(a.reason)}</p><p>요구 기술: ${escapeHtml(skills)}${t.dependencies.length?` · 선행: ${t.dependencies.map(id=>escapeHtml(taskById[id].name)).join(', ')}`:''}</p></div><div class="task-score"><b>${a.match_score}</b><span>match</span></div></article>`}).join('');
  document.querySelector('#harness').innerHTML=group('CONTEXT',data.harness.contexts)+group('RULES',data.harness.rules)+group('TOOLS',data.harness.tools)+`<div class="harness-group"><h4>WORKFLOW</h4><div class="flow">${data.harness.workflow.map(x=>`<span>${escapeHtml(x)}</span>`).join('')}</div></div>`;
  document.querySelector('#workloads').innerHTML=data.member_workload.map(w=>{const m=memberById[w.member_id],ratio=Math.min(100,Math.round(w.assigned_hours/w.available_hours*100));return `<div class="person"><b>${escapeHtml(m.name)}</b><div class="bar"><i style="width:${ratio}%"></i></div><small>${w.assigned_hours} / ${w.available_hours}h</small></div>`}).join('');
  const weeks=lastInput.project.duration_weeks;document.querySelector('#timeline').innerHTML=(data.schedule||[]).map(item=>{const task=taskById[item.task_id],left=item.start_week/weeks*100,width=Math.max(2,(item.end_week-item.start_week)/weeks*100);return `<div class="timeline-item"><b>${escapeHtml(task.name)}</b><div class="timeline-track"><i style="left:${left}%;width:${width}%"></i></div><small>${item.start_week}–${item.end_week}주</small></div>`}).join('');
  document.querySelector('#validation-errors').innerHTML=data.validation.valid?'<p class="validation-ok">모든 검증을 통과했습니다.</p>':data.validation.errors.map(error=>`<p class="validation-error">${escapeHtml(error)}</p>`).join('');
  results.hidden=false;results.scrollIntoView({behavior:'smooth'});
}

async function loadSaved() {
  try {
    const {projects}=await request('/api/projects'),container=document.querySelector('#saved'),listEl=document.querySelector('#saved-list');
    container.hidden=!projects.length;
    listEl.innerHTML=projects.map(item=>`<button data-id="${item.id}"><b>${escapeHtml(item.project_name)} · v${item.version||1}</b><small>${escapeHtml(item.status||'draft')} · ${escapeHtml(item.created_at)}</small></button>`).join('');
    listEl.querySelectorAll('button').forEach(button=>button.onclick=async()=>{const saved=await request(`/api/plans/${button.dataset.id}`);lastInput=saved.input;fillForm(lastInput);render({...saved.result,id:saved.id,project_key:saved.project_key,version:saved.version,status:saved.status})});
  } catch (_) {}
}

async function initialize(){const health=await request('/api/health');document.querySelector('#server-status').innerHTML=`<i></i> ${health.ai_configured?'AI READY':'RULE ENGINE'}`;loadSaved()}
async function busy(button,action){button.disabled=true;document.body.classList.add('loading');try{await action()}finally{button.disabled=false;document.body.classList.remove('loading')}}
document.querySelector('#confirm-plan').onclick=async event=>busy(event.currentTarget,async()=>{if(!currentPlanId)return;await request(`/api/plans/${currentPlanId}/confirm`,{});event.currentTarget.textContent='확정됨';loadSaved()});
document.querySelector('#delete-project').onclick=async()=>{if(!currentProjectKey||!confirm('이 프로젝트의 모든 계획 버전을 삭제할까요?'))return;await request(`/api/projects/${currentProjectKey}`,null,'DELETE');document.querySelector('#results').hidden=true;loadSaved()};
function group(title,items){return `<div class="harness-group"><h4>${title}</h4><div class="chips">${items.map(x=>`<span class="chip">${escapeHtml(x)}</span>`).join('')}</div></div>`}
function escapeHtml(value){const el=document.createElement('span');el.textContent=value;return el.innerHTML}
initialize().catch(error=>showError(error.message));
