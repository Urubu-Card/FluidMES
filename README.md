# FluidMES - backend
Aqui fica a parte do backend do codigo caso queira testar utilize alguns comandos


## Instalar Projeto
Clonar o repositorio via local

```git 
git clone https://github.com/Urubu-Card/FluidMES.git
```

## Amibente virutal e bibliotecas
Segue o tutorial para instalar o venv e as bibliotecas necessarias

```python 
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt #Se tiver a interface 'uv' pode utilizar 
py manage.py makemigrations
py manage.py migrate
py manage.py read_plants # Em outro terminal
py manage.py runserver 


```

## Instalar Docker e Redis
Para a utilização base ira precisar baixar o Redis via docker

```docker 
docker run -d --name my-redis -p 6379:6379 redis:latest
```


Celery worker 
```celery
celery -A config worker -l info -P solo
```
Celery
```celery
beat celery -A config beat -l info
```