from django.test import TestCase
from django.urls import reverse
from .models import Usuarios
from .admin import AccountCreationForm

class AdminDeploymentTests(TestCase):
    def test_public_preposto_cannot_open_database_admin(self):
        user=Usuarios.objects.create_user(email='owner@admin.test',cpf='owner-admin',password='Strong-Admin-419!',role=1)
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/').status_code,302)
    def test_superuser_sees_records_and_can_open_account_editor(self):
        user=Usuarios.objects.create_superuser(email='admin@admin.test',cpf='super-admin',password='Strong-Admin-419!',first_name='Admin')
        self.client.force_login(user)
        response=self.client.get('/admin/')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Receitas')
        self.assertEqual(self.client.get(reverse('admin:accounts_usuarios_change',args=[user.pk])).status_code,200)
    def test_admin_account_creation_hashes_password(self):
        form=AccountCreationForm(data={'email':'created@admin.test','first_name':'New','cpf':'created-admin','role':1,'password1':'Strong-Admin-419!','password2':'Strong-Admin-419!'})
        self.assertTrue(form.is_valid(),form.errors)
        user=form.save()
        self.assertTrue(user.check_password('Strong-Admin-419!'))
        self.assertNotEqual(user.password,'Strong-Admin-419!')
    def test_health_endpoint(self):
        response=self.client.get('/api/health/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(),{'status':'ok'})
