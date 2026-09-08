"""Deterministic planning tools controlled by a project-specific harness."""

from __future__ import annotations

import copy
from collections import defaultdict

from .catalog import common, engine, genre


def _require(data, key, kind):
    value = data.get(key)
    if not isinstance(value, kind) or (kind in (str, list) and not value):
        raise ValueError(f"'{key}' 값이 필요합니다.")
    return value


def _normalize(payload):
    normalized = copy.deepcopy(payload)
    project = _require(normalized, "project", dict)
    members = _require(normalized, "members", list)
    for key in ("name", "genre", "engine", "dimension", "goal"):
        _require(project, key, str)
    project.setdefault("platform", "PC")
    project.setdefault("reference_games", [])
    project.setdefault("content_scale", "소규모")
    project.setdefault("excluded_features", [])
    project.setdefault("completed_features", [])
    project.setdefault("available_assets", [])
    project.setdefault("constraints", [])
    weeks = project.get("duration_weeks")
    if not isinstance(weeks, int) or not 1 <= weeks <= 52:
        raise ValueError("'duration_weeks'는 1~52 사이의 정수여야 합니다.")
    if not 2 <= len(members) <= 6:
        raise ValueError("팀원은 2~6명이어야 합니다.")
    for index, member in enumerate(members, 1):
        member.setdefault("id", f"member_{index:02d}")
        _require(member, "name", str)
        member.setdefault("skills", {})
        member.setdefault("preferred_roles", [])
        member.setdefault("avoid_roles", [])
        member.setdefault("learning_interests", [])
        member.setdefault("experience", "")
        member.setdefault("related_projects", [])
        hours = member.get("available_hours_per_week")
        if not isinstance(hours, (int, float)) or hours <= 0:
            raise ValueError(f"{member['name']}의 주당 가용 시간을 확인해 주세요.")
        if any(not isinstance(level, (int, float)) or not 0 <= level <= 5 for level in member["skills"].values()):
            raise ValueError(f"{member['name']}의 숙련도는 0~5여야 합니다.")
    return normalized


def build_harness(project):
    genre_data = genre(project["genre"])
    common_data = common()
    engine_data = engine(project["engine"])
    weeks = project["duration_weeks"]
    contexts = [engine_data["context"], f"{project['dimension']} Game", f"{project['platform']} Platform", f"{project['genre']} Context"]
    contexts += ["Small Team", f"{weeks}-Week Development", f"{project['goal']} Context", f"{project['content_scale']} Content"] + genre_data["context"]
    rules = list(common_data["rules"])
    if weeks <= 6:
        rules.append("짧은 일정에서는 구현·완료 가능성을 우선하고 낮은 우선순위 기능을 축소한다.")
    if project["goal"] == "학습":
        rules.append("학습 관심사를 일부 반영하되 핵심 기능을 한 사람에게 집중하지 않는다.")
    rules.extend(project["constraints"])
    tools = list(common_data["tools"])
    if weeks > 6:
        tools.append("check_role_balance")
    return {"contexts": list(dict.fromkeys(contexts)), "rules": rules, "tools": tools, "workflow": genre_data["workflow"], "role_candidates": genre_data["roles"], "validation_conditions": common_data["validation_conditions"], "permissions": ["read_project_input", "use_registered_tools", "propose_assignments"]}


def _tasks(project):
    catalog = genre(project["genre"])["tasks"]
    names, result = {}, []
    excluded = {name.casefold() for name in project["excluded_features"]}
    completed = {name.casefold() for name in project["completed_features"]}
    catalog = [item for item in catalog if item["name"].casefold() not in excluded | completed]
    for index, item in enumerate(catalog, 1):
        name, category = item["name"], item["category"]
        task_id = f"task_{index:02d}"
        names[name] = task_id
        resolved = {project["engine"] if skill == "ENGINE" else skill: level for skill, level in item["required_skills"].items()}
        result.append({"id": task_id, "name": name, "category": category, "required_skills": resolved, "estimated_hours": item["estimated_hours"], "dependencies": item["dependencies"], "mandatory": True})
    for task in result:
        task["dependencies"] = [names[name] for name in task["dependencies"] if name in names]
    existing = {task["name"].casefold() for task in result}
    for feature in project.get("mandatory_features", []):
        if feature.strip() and feature.casefold() not in existing:
            result.append({"id": f"task_{len(result)+1:02d}", "name": feature.strip(), "category": "Required", "required_skills": {project["engine"]: 2}, "estimated_hours": 6, "dependencies": [], "mandatory": True})
    return result


def _score(task, member, remaining, constraints):
    required = task["required_skills"]
    skill = sum(min(member["skills"].get(name, 0), level) / level for name, level in required.items()) / max(len(required), 1)
    text = f"{task['name']} {task['category']}".casefold()
    preference = 1 if any(role.casefold() in text or task["category"].casefold() in role.casefold() for role in member["preferred_roles"]) else 0
    learning = 1 if any(topic.casefold() in text for topic in member["learning_interests"]) else 0
    avoided = any(role.casefold() in text or task["category"].casefold() in role.casefold() for role in member["avoid_roles"])
    blocked = member["id"] in constraints.get("avoid", {}).get(task["name"], set())
    enough_time = min(remaining / max(task["estimated_hours"], 1), 1)
    score = 55 * skill + 15 * preference + 10 * learning + 20 * enough_time - (50 if avoided or blocked else 0)
    return max(0, min(100, round(score)))


def _constraints(request, members, tasks):
    result = {"avoid": defaultdict(set), "prefer": defaultdict(set), "balance": False}
    lowered = request.casefold()
    result["balance"] = any(word in lowered for word in ("균등", "고르게", "balance"))
    for member in members:
        if member["name"].casefold() not in lowered:
            continue
        for task in tasks:
            if task["name"].casefold() not in lowered:
                continue
            if any(word in lowered for word in ("않", "빼", "제외", "avoid", "not")):
                result["avoid"][task["name"]].add(member["id"])
            elif any(word in lowered for word in ("맡", "배정", "학습", "give", "assign")):
                result["prefer"][task["name"]].add(member["id"])
    return result


def _assign(tasks, members, weeks, constraints):
    capacity = {member["id"]: member["available_hours_per_week"] * weeks for member in members}
    assigned = defaultdict(float)
    assignments = []
    for task in tasks:
        ranked = []
        for member in members:
            remaining = capacity[member["id"]] - assigned[member["id"]]
            score = _score(task, member, remaining, constraints)
            allowed = member["id"] not in constraints["avoid"].get(task["name"], set())
            if member["id"] in constraints["prefer"].get(task["name"], set()):
                score = min(100, score + 30)
            load_ratio = assigned[member["id"]] / capacity[member["id"]]
            rank = score - load_ratio * (30 if constraints["balance"] else 12)
            ranked.append((allowed, remaining >= task["estimated_hours"], rank, score, member))
        _, fits, _, score, chosen = max(ranked, key=lambda item: (item[0], item[1], item[2]))
        assigned[chosen["id"]] += task["estimated_hours"]
        strongest = max(task["required_skills"], key=lambda skill: chosen["skills"].get(skill, 0))
        reason = f"{strongest} 숙련도 {chosen['skills'].get(strongest, 0)}/5, 일정 {'적합' if fits else '초과(대체 인력 부족)'}"
        assignments.append({"task_id": task["id"], "member_id": chosen["id"], "match_score": score, "reason": reason})
    workload = [{"member_id": member["id"], "assigned_hours": assigned[member["id"]], "available_hours": capacity[member["id"]]} for member in members]
    return assignments, workload


def _validate(tasks, assignments, workload, members):
    errors, task_ids = [], {task["id"] for task in tasks}
    member_ids = {member["id"] for member in members}
    assigned_ids = {item["task_id"] for item in assignments}
    names = [task["name"].strip().casefold() for task in tasks]
    if len(names) != len(set(names)):
        errors.append("중복된 태스크가 있습니다.")
    for task in tasks:
        if task["mandatory"] and task["id"] not in assigned_ids:
            errors.append(f"필수 태스크 '{task['name']}'에 담당자가 없습니다.")
        missing = set(task["dependencies"]) - task_ids
        if missing:
            errors.append(f"'{task['name']}'의 의존성 {sorted(missing)}이 존재하지 않습니다.")
        if task["id"] in task["dependencies"]:
            errors.append(f"'{task['name']}'이 자기 자신을 의존합니다.")
    graph = {task["id"]: task["dependencies"] for task in tasks}
    visiting, visited = set(), set()

    def cyclic(task_id):
        if task_id in visiting:
            return True
        if task_id in visited:
            return False
        visiting.add(task_id)
        found = any(cyclic(dependency) for dependency in graph.get(task_id, []))
        visiting.remove(task_id)
        visited.add(task_id)
        return found

    if any(cyclic(task_id) for task_id in graph):
        errors.append("태스크 의존성이 순환합니다.")
    for item in assignments:
        if item["member_id"] not in member_ids:
            errors.append(f"존재하지 않는 팀원 '{item['member_id']}'이 배정되었습니다.")
    for item in workload:
        if item["assigned_hours"] > item["available_hours"]:
            errors.append(f"{item['member_id']} 작업량이 {item['assigned_hours']}h로 가용 {item['available_hours']}h를 초과합니다.")
    total_hours = sum(item["assigned_hours"] for item in workload)
    if total_hours and any(item["assigned_hours"] / total_hours > 0.7 for item in workload) and len(workload) > 1:
        errors.append("전체 작업의 70%를 초과하여 한 팀원에게 집중되었습니다.")
    return {"valid": not errors, "errors": errors}


def create_plan(payload, revision_request=""):
    data = _normalize(payload)
    project, members = data["project"], data["members"]
    tasks = _tasks(project)
    assignments, workload = _assign(tasks, members, project["duration_weeks"], _constraints(revision_request, members, tasks))
    return {"project_analysis": {"name": project["name"], "genre": project["genre"], "engine": project["engine"], "dimension": project["dimension"], "platform": project["platform"], "content_scale": project["content_scale"], "development_priority": project["goal"], "team_size": len(members), "summary": project.get("description", "")}, "harness": build_harness(project), "tasks": tasks, "assignments": assignments, "member_workload": workload, "validation": _validate(tasks, assignments, workload, members), "revision_request": revision_request}


def refine_plan(payload):
    original = _require(payload, "input", dict)
    request = _require(payload, "request", str)
    if len(request) > 500:
        raise ValueError("수정 요청은 500자 이하여야 합니다.")
    return create_plan(original, request)
