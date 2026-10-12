# Mejoras — lista ordenada simple → complejo
- [x] 3a. get_or_404 lote A (roles, user_roles, participant_tags, payments, delegations, festival_rulebooks)
- [x] 3b. get_or_404 lote B (chat, form_definitions, user_aliases, registration_forms, user_festival)
- [x] 4. paginate_filtered: 13 clones migrados (orden determinista)
- [x] 5. SyncQueue whitelist + paths estrictos (3 tests nuevos)
- [ ] 6. python-jose → PyJWT (CVE-2026-85394 CRIT 9.1, sin parche)
- [ ] 7. JWT iss/aud + ALGORITHM fijo + SECRET_KEY sin default
- [ ] 8. Deps majors frontend (connectivity_plus 6→7, flutter_map 7→8, file_picker 8→13, web 0.5→1.1)
