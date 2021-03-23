# Dashboard DP World

Integração dos dashboards em Python com o Portal de conferência requisitado pela DP

Esta aplicação será rodada como serviço no servidor da DP World

#Passos para deixar o app como serviço no servidor: 

1. Verifique se virtualenv está instalado no servidor. Caso esteja, execute dentro da pasta deste projeto após o git clone `virtualenv venv`
2. Feito isso, execute `source /venv/bin/activate` para ativar o ambiente virtual python
3. Com o ambiente virtual ativado, execute `pip install -r requirements.txt`
4. Assim que as instalações forem feitas, vamos configurar o serviço!
5. Primeiramente verifique se não há nada rodando na porta 5000 do servidor, porta padrão do Flask quando startado, caso tenha, `app.run()` de app.py deverá ser alterado.
6. Criaremos a configuração pro serviço: `nano /etc/init/<nome da aplicação>.conf`
>description "<nome da aplicação>"
>start on stopped rc RUNLEVEL=[2345]
>respawn
>exec python /<caminho onde o gitclone foi dado>/app.py
7. Agora criaremos o serviço em si: `nano /lib/systemd/system/<nome da aplicação>.service`
>[Unit]
>Description=<descrição da aplicação>
>[Install]
>WantedBy=multi-user.target
>[Service]
>User=<usuario>
>PermissionsStartOnly=true
>ExecStart=<caminho do git clone>/venv/bin/python3.7 <caminho do git clone>/app.py
>TimeoutSec=600
>Restart=on-failure
>RuntimeDirectoryMode=755
8. Alteramos a permissão da aplicação: `chown <usuario> app.py` e `chmod +x app.py`
9. Para concluir, executamos `sudo systemctl <nome da aplicação> start` para startar e `sudo systemctl <nome da aplicação> status` para verificar o status.
