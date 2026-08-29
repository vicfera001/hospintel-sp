-- Execute como ADMIN. Não registre senhas ou usuários pessoais no repositório.
CREATE ROLE enterprise_challenge_collab;

GRANT SELECT, INSERT, UPDATE ON internacoes_sp
TO enterprise_challenge_collab;

GRANT SELECT ON vw_internacoes_mensais
TO enterprise_challenge_collab;

GRANT SELECT ON vw_ranking_municipios
TO enterprise_challenge_collab;

GRANT SELECT ON vw_internacoes_dashboard
TO enterprise_challenge_collab;

-- Para cada conta criada pela interface do Oracle:
-- GRANT CREATE SESSION TO <USUARIO>;
-- GRANT enterprise_challenge_collab TO <USUARIO>;
