Requisitos para instalação
--------------------------
Python 3.x

*Sugiro usar Anaconda e Python 3.6 ou superior


Instalação
----------
Depois de criar um `environment` com o conda, basta fazer:
```
pip install -r requirements.txt
```

Se for executar o servidor no windows, sugiro instalar o waitress também:
```
pip install waitress
```


Execução
--------
* Configure o valor da variável de ambiente FLASK_APP para o arquivo cadastro.py:
```
cd /path/de/instalação/do/cadastro-fornecedor/
export FLASK_APP=cadastro.py
```

No windows, ao invés de usar o export, faça:
```
SET FLASK_APP=cadastro.py
```

* Crie o banco de dados:
```
flask dp upgrade
```

* Inicie a aplicação:
```
python cadastro.py
```
Nesse caso, o serviço deverá começar a rodar na porta 5000. Basta abrir o browser e acessar localhost:5000.

Se estiver usando o waitress, faça:
```
waitress-serve --listen=*:8000 cadastro:app
```
Com este comando, a aplicação irá escutar na porta 8000.



Iniciar a aplicação em background durante o boot do windows
-----------------------------------------------------------
* Crie um arquivo cadatro.bat com o comando de execução de sua aplicação. Por exemplo:
```
cd \path\de\instalação\do\cadastro-fornecedor\
C:\diretório\do\environment\waitress-serve --listen=*:8000 cadastro:app
```
Salve o arquivo cadastro.bat dentro do diretório cadastro-fornecedor.

Crie um script com a extensão cadastro.vbs e cole as seguintes linhas:
```
Set WshShell = CreateObject("WScript.Shell" ) 
WshShell.Run chr(34) & "C:\caminho\para\o\arquivo\cadastro.bat" & Chr(34), 0 
Set WshShell = Nothing 
```

Digite CMD+R e entre com shell:startup. Salve o arquivo cadastro.vbs dentro do diretório que será aberto.
