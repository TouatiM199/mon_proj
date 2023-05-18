import os
import tempfile
import zipfile
from django.test import TestCase, RequestFactory
from django.urls import reverse
from .models import Instructeur, Cours, CertificateTemplatemodel
from .views import generate_certificates
from .forms import DateRangeForm


class GenerateCertificatesTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Créer des objets Instructeur et Cours pour les tests
        self.instructeur = Instructeur.objects.create(nom="Test Instructeur")
        self.cours = Cours.objects.create(nom="Test Cours")

        # Créer des fichiers temporaires pour les modèles de certificat
        self.template_file = tempfile.NamedTemporaryFile(suffix='.docx')
        self.template_path = self.template_file.name
        self.template_name = os.path.basename(self.template_path)
        self.template_model = CertificateTemplatemodel.objects.create(name=self.template_name)
        self.template_model.file.save(self.template_name, self.template_file)

    def tearDown(self):
        # Supprimer les objets Instructeur, Cours et les fichiers temporaires
        self.instructeur.delete()
        self.cours.delete()
        self.template_model.file.delete()
        self.template_file.close()

    def test_generate_certificates(self):
        # Créer un fichier Excel temporaire
        excel_file = tempfile.NamedTemporaryFile(suffix='.xlsx')

        # Créer une requête POST avec le fichier Excel
        data = {
            'template_name': self.template_name,
            'instructeur': str(self.instructeur.id),
            'cour': str(self.cours.id),
            'excel_file': excel_file,
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
        }
        url = reverse('generate_certificates')
        request = self.factory.post(url, data, format='multipart')

        # Appeler la vue generate_certificates
        response = generate_certificates(request)
        self.assertEqual(response.status_code, 200)

        # Vérifier que la réponse est un fichier zip
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename='))

        # Extraire le fichier zip dans un répertoire temporaire
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(response.content, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Vérifier que tous les certificats ont été créés
        certificates = [filename for filename in os.listdir(temp_dir) if filename.endswith('.docx')]
        self.assertGreater(len(certificates), 0)

        # Supprimer les fichiers temporaires
        excel_file.close()
        os.remove(excel_file.name)
        os.remove(self.template_path)

