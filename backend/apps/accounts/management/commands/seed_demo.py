import secrets
from django.core.management.base import BaseCommand
from django.db import transaction
from validate_docbr import CPF, CNPJ
from apps.accounts.models import Empresa, Usuarios
from apps.plantas.models import Planta
from apps.producao.models import Receita

class Command(BaseCommand):
    help = 'Cria empresa, três contas de demonstração e cadastros fictícios; exibe senhas aleatórias apenas para contas novas.'
    @transaction.atomic
    def handle(self, *args, **options):
        company = Empresa.objects.filter(nome='FluidMES Demonstração').first()
        if not company:
            company = Empresa.objects.create(nome='FluidMES Demonstração',cnpj=CNPJ().generate(mask=True))
        for role, name, email in [(1,'Alex','preposto@fluidmes.demo'),(2,'Marina','chefe@fluidmes.demo'),(3,'Rafael','funcionario@fluidmes.demo')]:
            if Usuarios.objects.filter(email=email).exists():
                self.stdout.write(f'{email}: já existe, senha preservada.')
                continue
            password = secrets.token_urlsafe(14)+'!Aa1'
            Usuarios.objects.create_user(email=email,password=password,first_name=name,last_name='Demo',cpf=CPF().generate(mask=True),empresa=company,role=role)
            self.stdout.write(f'{email} | senha: {password}')
        for name, location in [('Planta 01','Setor A · Linha 01'),('Planta 02','Setor A · Linha 02'),('Planta 03','Setor B · Linha 01')]:
            Planta.objects.get_or_create(empresa=company,nome=name,defaults={'localizacao':location})
        for name in ['Cítrico tropical','Mix de frutas','Limonada suave']:
            Receita.objects.get_or_create(empresa=company,nome=name,defaults={'ingrediente1':1,'ingrediente2':2,'ingrediente3':1,'tempo1':2,'tempo2':3})
        self.stdout.write('Cadastros fictícios criados. Guarde as senhas exibidas; nenhum equipamento foi conectado.')
