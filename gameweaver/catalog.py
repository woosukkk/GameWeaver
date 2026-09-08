"""Game-domain data used by the dynamic harness."""

COMMON_RULES = [
    "팀원의 주당 가용 시간을 초과하지 않는다.",
    "모든 필수 태스크에 담당자를 배정한다.",
    "기피 역할은 가능한 한 배정하지 않는다.",
    "모든 배정에 계산 근거를 제공한다.",
]

GENRES = {
    "Roguelike": {
        "context": ["Core Loop", "Combat", "Enemy", "Item", "Progression", "Randomization", "Replayability"],
        "workflow": ["Project Analysis", "Core Loop Analysis", "System Task Generation", "Task Dependency Analysis", "Skill Matching", "Assignment", "Workload Validation"],
        "roles": ["Gameplay Programmer", "Game Designer", "UI Designer"],
        "tasks": [
            ("Player Controller", "Gameplay", {"ENGINE": 3, "Programming": 3}, 8, []),
            ("Core Combat", "Gameplay", {"ENGINE": 3, "Programming": 4}, 12, ["Player Controller"]),
            ("Enemy AI", "Enemy", {"Programming": 3, "AI": 3}, 10, ["Player Controller"]),
            ("Item & Progression", "System", {"Game Design": 3, "Programming": 2}, 8, ["Core Combat"]),
            ("HUD", "UI", {"UI": 3, "ENGINE": 2}, 6, ["Player Controller"]),
        ],
    },
    "Visual Novel": {
        "context": ["Dialogue", "Scenario", "Character", "Branching Narrative", "Save/Load", "UI", "Localization"],
        "workflow": ["Project Analysis", "Content Scale Analysis", "Scenario / Art / UI Task Generation", "Workload Estimation", "Role Matching", "Assignment"],
        "roles": ["Scenario Writer", "UI Designer", "Gameplay Programmer", "Artist"],
        "tasks": [
            ("Dialogue System", "System", {"ENGINE": 3, "Programming": 3}, 10, []),
            ("Branching Scenario", "Content", {"Writing": 4, "Game Design": 3}, 12, []),
            ("Character Art", "Art", {"Art": 4}, 12, []),
            ("Dialogue UI", "UI", {"UI": 4, "ENGINE": 2}, 8, ["Dialogue System"]),
            ("Save / Load", "System", {"Programming": 3, "ENGINE": 2}, 6, ["Dialogue System"]),
        ],
    },
}

DEFAULT_GENRE = {
    "context": ["Core Loop", "Gameplay", "Content", "UI", "Quality"],
    "workflow": ["Project Analysis", "Task Generation", "Task Requirement Analysis", "Member Analysis", "Matching", "Assignment", "Validation"],
    "roles": ["Gameplay Programmer", "Game Designer", "Artist", "UI Designer"],
    "tasks": [
        ("Core Prototype", "Gameplay", {"ENGINE": 3, "Programming": 3}, 10, []),
        ("Game Rules", "Design", {"Game Design": 3}, 7, []),
        ("Content Pass", "Content", {"Game Design": 2, "Art": 2}, 8, ["Core Prototype"]),
        ("Main UI", "UI", {"UI": 3, "ENGINE": 2}, 6, ["Core Prototype"]),
        ("Playtest & Polish", "Quality", {"Testing": 3, "ENGINE": 2}, 6, ["Content Pass", "Main UI"]),
    ],
}
