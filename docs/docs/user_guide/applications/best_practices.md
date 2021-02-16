# Best Practices

This section contains some tips and strategies to leverage Gameta's functionalities.

## Standardise your DevOps practices

Standardising your DevOps practices for all your repositories will allow you to easily 
run tests, builds and other DevOps functionalities with `gameta apply`

## Group related repositories with tags

Tag repositories to group related repositories e.g. Python, Backend, Frontend and 
apply commands to these. 

For example, if you have these repositories:

1. backend_app_1 (written in Go)
2. backend_app_2 (written in NodeJS)
2. backend_app_3 (written in Go)
3. frontend (written in NodeJS)

You could use the following tags to help organise your repositories:

| Applications  | Tags             |
| ------------- | ---------------- | 
| backend_app_1 | go, backend      |
| backend_app_2 | nodejs, backend  |
| backend_app_3 | go, backend      |
| frontend      | nodejs, frontend |

And the following commands to help manage your DevOps operations:

```bash
gameta apply -c run_go_tests -t go
gameta apply -c run_nodejs_tests -t nodejs
gameta apply -c build_go_backend -t go
gameta apply -c build_nodejs_backend -r backend_app_2
```

