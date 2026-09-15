ALTER TABLE sessions
    ADD CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE plans
    ADD CONSTRAINT uq_plans_owner_project_version UNIQUE (owner_user_id, project_key, version),
    ADD CONSTRAINT fk_plans_owner FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_plans_parent FOREIGN KEY (parent_plan_id) REFERENCES plans(id) ON DELETE SET NULL;

ALTER TABLE task_outcomes
    ADD CONSTRAINT fk_task_outcomes_plan FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE;

ALTER TABLE project_retrospectives
    ADD CONSTRAINT fk_retrospectives_plan FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE;
