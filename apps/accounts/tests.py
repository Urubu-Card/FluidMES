from django.test import TestCase, override_settings
from django.core import mail
from django.core.cache import cache
from rest_framework.test import APIClient
from .models import Usuarios, Empresa, PasswordResetToken
from apps.plantas.models import Planta, Clp
from apps.producao.models import Receita
from validate_docbr import CPF, CNPJ

PASSWORD = 'Strong-Fluid-Password-937!'

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ApplicationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.company = Empresa.objects.create(nome='A', cnpj=CNPJ().generate(mask=True))
        self.other_company = Empresa.objects.create(nome='B', cnpj=CNPJ().generate(mask=True))
        self.owner = Usuarios.objects.create_user(email='owner@example.com', password=PASSWORD, cpf=CPF().generate(mask=True), empresa=self.company, role=1)
        self.other = Usuarios.objects.create_user(email='other@example.com', password=PASSWORD, cpf=CPF().generate(mask=True), empresa=self.other_company, role=1)
        self.viewer = Usuarios.objects.create_user(email='viewer@example.com', password=PASSWORD, cpf=CPF().generate(mask=True), empresa=self.company, role=3)
        self.plant = Planta.objects.create(nome='P',localizacao='A',empresa=self.company)
        self.foreign_plant = Planta.objects.create(nome='Other',localizacao='B',empresa=self.other_company)
        self.recipe = Receita.objects.create(nome='R',empresa=self.company,ingrediente1=1,ingrediente2=2,ingrediente3=3,tempo1=2,tempo2=3)
        self.client = APIClient(enforce_csrf_checks=True)
        self.csrf = self.client.get('/api/csrf/').data['csrfToken']
        self.client.credentials(HTTP_X_CSRFTOKEN=self.csrf)

    def login(self, user=None):
        user = user or self.owner
        result = self.client.post('/api/login/', {'usuario':user.email,'password':PASSWORD})
        self.assertEqual(result.status_code, 200, result.data)
        return result

    def test_anonymous_routes_are_protected(self):
        for route in ('plantas','receitas','pedidos','clps','sensores','funcionarios','rendimentos','paradas','me'):
            self.assertEqual(self.client.get(f'/api/{route}/').status_code, 401)

    def test_csrf_required_even_on_login(self):
        self.client.credentials()
        self.assertEqual(self.client.post('/api/login/', {'usuario':self.owner.email,'password':PASSWORD}).status_code,403)

    def test_login_cookie_and_refresh(self):
        result = self.login()
        self.assertTrue(result.cookies['access_token']['httponly'])
        self.assertEqual(self.client.get('/api/me/').status_code,200)
        self.assertEqual(self.client.post('/api/token/refresh/').status_code,200)

    def test_inactive_user_cannot_refresh(self):
        self.login()
        self.owner.is_active=False; self.owner.save()
        self.assertEqual(self.client.post('/api/token/refresh/').status_code,401)

    def test_logout_revokes_refresh(self):
        self.login()
        old = self.client.cookies['refresh_token'].value
        self.assertEqual(self.client.post('/api/logout/').status_code,200)
        self.client.cookies['refresh_token']=old
        self.assertEqual(self.client.post('/api/token/refresh/').status_code,401)

    def test_cookie_mutation_requires_csrf(self):
        self.login(); self.client.credentials()
        self.assertEqual(self.client.post('/api/plantas/',{'nome':'X','localizacao':'Y'}).status_code,403)

    def test_tenant_read_and_update_isolation(self):
        self.login()
        self.assertEqual(len(self.client.get('/api/plantas/').data),1)
        self.assertEqual(self.client.patch(f'/api/plantas/{self.foreign_plant.pk}/',{'nome':'hack'}).status_code,404)
        self.assertEqual(self.client.delete(f'/api/plantas/{self.foreign_plant.pk}/').status_code,404)

    def test_viewer_cannot_edit_or_access_restricted_resources(self):
        self.login(self.viewer)
        for route in ('clps','sensores','funcionarios','paradas','rendimentos','atualizacoes'):
            self.assertEqual(self.client.get(f'/api/{route}/').status_code,403)
        self.assertEqual(self.client.patch(f'/api/plantas/{self.plant.pk}/',{'nome':'no'}).status_code,403)
        self.assertEqual(self.client.delete(f'/api/receitas/{self.recipe.pk}/').status_code,403)

    def test_clp_foreign_relationship_rejected(self):
        self.login()
        payload={'nome':'CLP','ip':'127.0.0.1','porta':'5020','ativo':True,'planta':self.foreign_plant.pk}
        self.assertEqual(self.client.post('/api/clps/',payload).status_code,400)
        payload['planta']=self.plant.pk
        self.assertEqual(self.client.post('/api/clps/',payload).status_code,201)

    def test_sensor_foreign_relationship_rejected(self):
        self.login()
        clp=Clp.objects.create(nome='C',ip='127.0.0.1',porta='5020',ativo=True,planta=self.foreign_plant)
        payload={'nome':'S','tipo':'volume','unidade':'litros','minimo':0,'maximo':100,'tipo_registro':'holding_register','endereco':0,'clp':clp.pk}
        self.assertEqual(self.client.post('/api/sensores/',payload).status_code,400)

    def test_order_lifecycle_and_simulated_completion(self):
        from apps.producao.models import Pedido
        from apps.producao.workflow import advance_plant
        from datetime import timedelta
        self.login(self.viewer)
        payload={'planta':self.plant.pk,'receita':self.recipe.pk,'prazo':'2027-01-01','quantidade':10,'aprovacao':'aprovado','status':'concluido'}
        result=self.client.post('/api/pedidos/',payload)
        self.assertEqual(result.status_code,201,result.data)
        self.assertEqual(result.data['aprovacao'],'aguardando')
        url=f"/api/pedidos/{result.data['idpedido']}/"
        self.assertEqual(self.client.post(url+'aprovar/').status_code,403)
        self.assertEqual(self.client.patch(url,{'status':'em_andamento'}).status_code,403)
        self.client.cookies.pop('access_token',None);self.client.cookies.pop('refresh_token',None);self.login()
        result=self.client.post(url+'aprovar/')
        self.assertEqual(result.status_code,200,result.data)
        self.assertEqual(result.data['status'],'em_andamento')
        order=Pedido.objects.get(pk=result.data['idpedido'])
        advance_plant(order.planta_id,order.lotes.latest('fim_previsto').fim_previsto+timedelta(seconds=1))
        order.refresh_from_db()
        self.assertEqual(order.status,'concluido')
        self.assertEqual(order.quantidade_boa,10)
        self.assertEqual(self.client.post(url+'aprovar/').status_code,400)

    def test_negative_and_foreign_order(self):
        self.login()
        payload={'planta':self.plant.pk,'receita':self.recipe.pk,'prazo':'2027-01-01','quantidade':-1}
        self.assertEqual(self.client.post('/api/pedidos/',payload).status_code,400)
        payload.update(quantidade=1,planta=self.foreign_plant.pk)
        self.assertEqual(self.client.post('/api/pedidos/',payload).status_code,400)

    def test_recipe_in_use_cannot_be_deleted(self):
        self.login()
        self.client.post('/api/pedidos/',{'planta':self.plant.pk,'receita':self.recipe.pk,'prazo':'2027-01-01','quantidade':1})
        self.assertEqual(self.client.delete(f'/api/receitas/{self.recipe.pk}/').status_code,400)
        self.assertEqual(self.client.delete(f'/api/plantas/{self.plant.pk}/').status_code,400)

    def test_employee_password_hashed_and_role_escalation_blocked(self):
        self.login()
        payload={'first_name':'Employee','last_name':'Test','email':'employee@example.com','cpf':CPF().generate(mask=True),'password':PASSWORD,'role':3}
        result=self.client.post('/api/funcionarios/',payload)
        self.assertEqual(result.status_code,201,result.data)
        user=Usuarios.objects.get(pk=result.data['id'])
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotIn('password',result.data)
        self.assertEqual(self.client.patch(f'/api/funcionarios/{user.pk}/',{'role':1}).status_code,400)

    def test_manager_reads_but_cannot_manage_employees(self):
        self.viewer.role=2;self.viewer.save();self.login(self.viewer)
        self.assertEqual(self.client.get('/api/funcionarios/').status_code,200)
        self.assertEqual(self.client.post('/api/funcionarios/',{}).status_code,403)

    def test_registration_creates_owner_and_rejects_duplicates_atomically(self):
        payload={'first_name':'New','last_name':'User','email':'new@example.com','cpf':CPF().generate(mask=True),'cnpj':CNPJ().generate(mask=True),'password':PASSWORD,'nomeEmpresa':'New company'}
        result=self.client.post('/api/cadastro/',payload)
        self.assertEqual(result.status_code,201,result.data)
        self.assertEqual(Usuarios.objects.get(email=payload['email']).role,1)
        count=Empresa.objects.count()
        self.assertEqual(self.client.post('/api/cadastro/',payload).status_code,400)
        self.assertEqual(Empresa.objects.count(),count)

    def test_password_reset_is_single_use_and_revokes_session(self):
        self.login()
        old_access=self.client.cookies['access_token'].value
        self.assertEqual(self.client.post('/api/password-reset/',{'email':self.owner.email}).status_code,200)
        reset=PasswordResetToken.objects.get(user=self.owner)
        self.assertIn('/auth/reset-password?token=',mail.outbox[0].body)
        payload={'token':str(reset.token),'nova_senha':'Another-Strong-Password-458!'}
        self.assertEqual(self.client.post('/api/password-reset/confirm/',payload).status_code,200)
        self.assertEqual(self.client.post('/api/password-reset/confirm/',payload).status_code,400)
        self.client.cookies['access_token']=old_access
        self.assertEqual(self.client.get('/api/me/').status_code,401)

    def test_unknown_email_reset_response_is_generic(self):
        response=self.client.post('/api/password-reset/',{'email':'nobody@example.com'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(mail.outbox),0)

    def test_csrf_bootstrap_does_not_exhaust_login_budget(self):
        for _ in range(15):
            self.assertEqual(self.client.get('/api/csrf/').status_code,200)
        self.login()

    def test_login_brute_force_is_still_throttled(self):
        for _ in range(10):
            self.assertEqual(self.client.post('/api/login/',{'usuario':'unknown@example.com','password':'Wrong-password'}).status_code,400)
        self.assertEqual(self.client.post('/api/login/',{'usuario':'unknown@example.com','password':'Wrong-password'}).status_code,429)


class PrepostoRegressionTests(TestCase):
    setUp = ApplicationTests.setUp
    login = ApplicationTests.login
    # Reuse only the fixture/helpers; inherited checks remain exercised by ApplicationTests.
    def test_signup_ignores_requested_employee_role(self):
        payload={'first_name':'Preposto','last_name':'Novo','email':'signup@example.com','cpf':CPF().generate(mask=True),'cnpj':CNPJ().generate(mask=True),'password':PASSWORD,'nomeEmpresa':'Empresa nova','role':3}
        response=self.client.post('/api/cadastro/',payload)
        self.assertEqual(response.status_code,201,response.data)
        self.assertEqual(response.data['role'],Usuarios.Role.PREPOSTO)
        self.assertIsNotNone(response.data['empresa'])
        user=Usuarios.objects.get(email=payload['email'])
        self.assertTrue(user.is_preposto)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_preposto_without_django_admin_flags_manages_recipe_and_plant(self):
        self.login()
        self.assertFalse(self.owner.is_staff)
        self.assertFalse(self.owner.is_superuser)
        recipe={'nome':'coca-cola','ingrediente1':2,'ingrediente2':2,'ingrediente3':2,'tempo1':2,'tempo2':2}
        response=self.client.post('/api/receitas/',recipe)
        self.assertEqual(response.status_code,201,response.data)
        url=f"/api/receitas/{response.data['idreceita']}/"
        self.assertEqual(self.client.patch(url,{'nome':'Receita editada'}).status_code,200)
        self.assertEqual(self.client.delete(url).status_code,204)
        response=self.client.post('/api/plantas/',{'nome':'Nova planta','localizacao':'A'})
        self.assertEqual(response.status_code,201,response.data)
        url=f"/api/plantas/{response.data['idplanta']}/"
        self.assertEqual(self.client.patch(url,{'nome':'Planta editada'}).status_code,200)
        self.assertEqual(self.client.delete(url).status_code,204)
        for route in ('rendimentos','funcionarios','atualizacoes','clps','sensores','paradas'):
            self.assertEqual(self.client.get(f'/api/{route}/').status_code,200)

    def test_orphan_account_creates_own_company_and_becomes_preposto(self):
        self.owner.empresa=None;self.owner.role=3;self.owner.save()
        self.login()
        response=self.client.get('/api/receitas/')
        self.assertEqual(response.status_code,403)
        self.assertIn('empresa',str(response.data['detail']))
        response=self.client.post('/api/configurar-empresa/',{'nome':'Minha empresa','cnpj':CNPJ().generate(mask=True)})
        self.assertEqual(response.status_code,201,response.data)
        self.assertEqual(response.data['role'],1)
        self.assertEqual(self.client.get('/api/receitas/').status_code,200)

    def test_company_setup_cannot_join_existing_company(self):
        self.owner.empresa=None;self.owner.save();self.login()
        result=self.client.post('/api/configurar-empresa/',{'nome':'Wrong','cnpj':self.other_company.cnpj})
        self.assertEqual(result.status_code,400)
        self.owner.refresh_from_db();self.assertIsNone(self.owner.empresa_id)

    def test_member_cannot_reassign_company_through_setup(self):
        self.login(self.viewer)
        before=Empresa.objects.count()
        self.assertEqual(self.client.post('/api/configurar-empresa/',{'nome':'Wrong','cnpj':CNPJ().generate(mask=True)}).status_code,400)
        self.viewer.refresh_from_db();self.assertEqual(self.viewer.role,3)
        self.assertEqual(Empresa.objects.count(),before)

    def test_local_command_repairs_legacy_role_without_deleting_data(self):
        from django.core.management import call_command
        self.owner.role=3;self.owner.save()
        previous_hash=self.owner.password
        call_command('definir_preposto',email=self.owner.email)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.is_preposto)
        self.assertEqual(self.owner.password,previous_hash)
        self.assertTrue(Planta.objects.filter(pk=self.plant.pk).exists())

    def test_superuser_default_role_is_preposto(self):
        user=Usuarios.objects.create_superuser(email='admin@example.com',password=PASSWORD,cpf=CPF().generate(mask=True))
        self.assertTrue(user.is_preposto)
