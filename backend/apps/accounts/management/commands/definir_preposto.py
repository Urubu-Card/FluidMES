from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from validate_docbr import CNPJ
from apps.accounts.models import Usuarios, Empresa
from apps.accounts.audit import record

class Command(BaseCommand):
    help = 'Ajusta uma conta existente para Preposto, sem alterar senha ou apagar dados. Executar apenas pelo administrador local.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--cnpj', help='Opcional: vincula explicitamente à empresa existente deste CNPJ.')

    @transaction.atomic
    def handle(self, *args, **options):
        user = Usuarios.objects.select_for_update().filter(email__iexact=options['email'].strip()).first()
        if not user:
            raise CommandError('Conta não encontrada. Confira o e-mail cadastrado.')
        company = user.empresa
        if options['cnpj']:
            if not CNPJ().validate(options['cnpj']):
                raise CommandError('CNPJ inválido.')
            digits = ''.join(c for c in options['cnpj'] if c.isdigit())
            company = Empresa.objects.filter(cnpj__in=[digits, CNPJ().mask(digits)]).first()
            if not company:
                raise CommandError('Empresa não encontrada. Cadastre-a primeiro.')
        if not company:
            raise CommandError('Conta sem empresa. Informe --cnpj de uma empresa existente para estabelecer o vínculo administrativo.')
        user.empresa = company
        user.role = Usuarios.Role.PREPOSTO
        user.save(update_fields=['empresa','role'])
        record(None, company.pk, 'ajustou', 'permissão de conta', f'{user.get_full_name() or user.email}: Preposto (ajuste administrativo local)')
        self.stdout.write(self.style.SUCCESS(f'{user.email} agora é Preposto de {company.nome}. Saia e entre novamente no site.'))
