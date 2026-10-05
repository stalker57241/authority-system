# Права доступа

Система прав доступа в данном проекте представлена с использованием древовидной структуры:

- OPERATOR
    - GUEST
        - REGISTER
        - LOGIN
    - ACCOUNTS
        - DELETE
            - EDIT
                - VIEW
    - REPOSITORIES
        - AUTHORITY_SYSTEM
            - DELETE
                - EDIT
                    - VIEW
            - ADD_MEMBER
            - REMOVE_MEMBER

Когда пользователь регистрируется, он генерирует аккаунт. На данный аккаунт создаются права: просмотр (`VIEW`), изменение (`EDIT`) и удаление (`DELETE`).

Тот кто может удалить аккаунт, наверняка должен иметь доступ к редактированию и просмотру, а тот кто может редактировать аккаунт, точно может его просматривать.

Пользователь с правами `OPERATOR.GUEST` имеет по умолчанию доступ `OPERATOR.GUEST.REGISTER`, `OPERATOR.GUEST.LOGIN` и `OPERATOR.USER.ACCOUNTS.DELETE.EDIT.VIEW`

## Сборка и запуск:

### А) В текущей среде

```sh
git clone https://github.com/stalker57241/authority-system authority_system
cd authority_system
python -m venv venv
# Для sh
source venv/bin/activate.sh
# Для fish
source venv/bin/activate.fish
# Для Powershell (Windows)
venv\bin\activate.ps1

pip install -r requirements.txt
# Напрямую через python
python -m app
# Через flask
flask run -h 0.0.0.0 -p 5000
# Или только на текущей машине
flask run -h 127.0.0.1 -p 5000
```
Затем открыть в браузере http://localhost:5000

### B) Через Docker

```sh
git clone https://github.com/stalker57241/authority-system authority_system
cd authority_system
docker build . -f DockerFile --tag authoritysystem:latest
docker run authoritysystem:latest
```
