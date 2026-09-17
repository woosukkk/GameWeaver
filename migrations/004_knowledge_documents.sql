CREATE TABLE IF NOT EXISTS knowledge_documents (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    project_key CHAR(36) NOT NULL,
    document_type ENUM('gdd','playtest') NOT NULL,
    title VARCHAR(255) NOT NULL,
    source_url VARCHAR(1000) NOT NULL DEFAULT '',
    content MEDIUMTEXT NOT NULL,
    created_by BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_knowledge_project (project_key, document_type),
    FULLTEXT KEY ft_knowledge_text (title, content),
    CONSTRAINT fk_knowledge_user FOREIGN KEY (created_by) REFERENCES users(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
