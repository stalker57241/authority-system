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