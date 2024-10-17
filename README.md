## Base Única / Banco e Api
_Com docker-compose para configuração de ambiente_

>Antes do comando:
> ```sudo docker-compose up --build```
>
>Certifique-se de configurar os arquivos .env, nas pastas: _app, flaskmigrate_
> ```
>URI=banco://user:senha@host/database
> ```
> .env para a pasta _script_
> ```
>URI=banco://user:senha@host/database
>HOST=
>PORT=
>DATABASE=
>USER=
>PASSWORD=
> ```
> .env para o arquivo _docker-compose.yml_
>```
>POSTGRES_DB=
>POSTGRES_USER=
>POSTGRES_PASSWORD=
>PGADMIN_DEFAULT_EMAIL=
>PGADMIN_DEFAULT_PASSWORD=
>```

> [!CAUTION]
> Crie dentro da pasta _app_ uma pasta vazia com o nome _uploads_.
