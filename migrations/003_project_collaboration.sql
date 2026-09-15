CREATE TABLE project_members (
    project_key CHAR(36) NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_key, user_id),
    CONSTRAINT fk_project_members_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE plans ADD INDEX idx_plans_owner (owner_user_id),
    DROP INDEX uq_plans_owner_project_version,
    ADD CONSTRAINT uq_plans_project_version UNIQUE (project_key, version);

INSERT IGNORE INTO project_members(project_key,user_id,role)
    SELECT DISTINCT project_key,owner_user_id,'owner' FROM plans WHERE owner_user_id IS NOT NULL;

CREATE TABLE project_invitations (
    token_hash CHAR(64) NOT NULL PRIMARY KEY,
    project_key CHAR(36) NOT NULL,
    email VARCHAR(254) NOT NULL,
    role VARCHAR(20) NOT NULL,
    invited_by BIGINT UNSIGNED NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_invitation_project (project_key),
    CONSTRAINT fk_invitations_inviter FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
