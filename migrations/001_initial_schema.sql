CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sessions (
    token_hash CHAR(64) NOT NULL PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_expiry (expires_at)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS plans (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    owner_user_id BIGINT UNSIGNED NULL,
    project_key CHAR(36) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    version INT UNSIGNED NOT NULL DEFAULT 1,
    parent_plan_id BIGINT UNSIGNED NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    input_json JSON NOT NULL,
    result_json JSON NOT NULL,
    revision_request VARCHAR(500) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plans_created_at (created_at)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS task_outcomes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    plan_id BIGINT UNSIGNED NOT NULL,
    task_id VARCHAR(50) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    engine VARCHAR(100) NOT NULL,
    estimated_hours DECIMAL(8,2) NOT NULL,
    actual_hours DECIMAL(8,2) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT TRUE,
    rework_hours DECIMAL(8,2) NOT NULL DEFAULT 0,
    blockers JSON NOT NULL,
    playtest_issues INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_task_outcome (plan_id, task_id),
    INDEX idx_outcome_context (genre, engine, task_name)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS project_retrospectives (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    plan_id BIGINT UNSIGNED NOT NULL,
    project_key CHAR(36) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    engine VARCHAR(100) NOT NULL,
    satisfaction TINYINT UNSIGNED NOT NULL,
    core_loop_achieved BOOLEAN NOT NULL,
    summary TEXT NOT NULL,
    went_well TEXT NOT NULL,
    problems TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_project_retrospective_plan (plan_id),
    INDEX idx_retrospective_context (genre, engine),
    FULLTEXT KEY ft_retrospective_text (summary, went_well, problems, recommendations)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
