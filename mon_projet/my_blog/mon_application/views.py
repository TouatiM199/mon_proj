import os
import io
import re
import string
import docx    
import pandas as pd
from docxtpl import DocxTemplate, InlineImage
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
import zipfile
from .models import Instructeur,Cours
from .models import CertificateTemplatemodel 
from .forms import DateRangeForm
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files import File
from PIL import Image, ImageEnhance, ImageFilter
from django.templatetags.static import static
from PyPDF2 import PdfFileMerger, PdfFileReader
from docx2pdf import convert # ajouter cette ligne pour la conversion Word vers PDF
import docx2pdf
from django.conf import settings
import hashlib
from docx2python import docx2python
#from docx2html import convert
from django.shortcuts import redirect
def generate_certificates(request):
    
    
    
    instructeurs_file = os.path.join(os.path.dirname(__file__), 'data', 'instructeurs.txt')
    cours_file = os.path.join(os.path.dirname(__file__), 'data', 'cours.txt')
    instructeurs = Instructeur.objects.all()
    cours = Cours.objects.all()
    Instructeur.objects.exclude(nom__in=["Maha TOUATI", "Mohamed Ali RIAHI", "Mourad BEN AZZOUZ", "Mohamed Ramzi MAKNI", "Seifallah BENNOUR", "Moez RABOUDI", "Adnen HAMMADI"]).delete()
    
    # Charger les options existantes pour les instructeurs et les cours
    # Enregistrer les noms des instructeurs à partir du fichier texte dans le modèle Instructeur
 
    with open(instructeurs_file,  encoding="utf-8-sig") as f:
        for line in f.readlines():
        # Créez une instance de votre modèle et enregistrez-la dans la base de données
            nom_instructeur = line.strip()
            instructeur, created = Instructeur.objects.get_or_create(nom=str(nom_instructeur))
            if created:
                instructeur.save()  
                  

    
  
    with open(cours_file, 'r') as f:
        #cours = [ line.strip() for line in f.readlines()]
        for line in f.readlines():
            nom_cours = line.strip()
            cour, created = Cours.objects.get_or_create(nom=str(nom_cours))
            if created:
                cour.save()
    cours_vide = Cours.objects.filter(nom='').delete()
            
    templates_directory = os.path.join(settings.BASE_DIR, 'mon_application', 'static', 'certificates_templates')
    cert_templates = [name for name in os.listdir(templates_directory) if name.endswith('.docx')]
    # Supprimer les anciens modèles de certificat
    CertificateTemplatemodel.objects.all().delete()
    for template_name in cert_templates:
        template_path = os.path.join(templates_directory, template_name)
         # Vérifier si le modèle de certificat existe déjà dans la base de données
        if CertificateTemplatemodel.objects.filter(name=template_name).exists():
            continue

        with open(template_path, 'rb') as template_file:
            
            template_model,created = CertificateTemplatemodel.objects.get_or_create(name=template_name)
            
            template_model.save()

    cert_templates=CertificateTemplatemodel.objects.all()
    
    context = {                   
        'instructeurs': instructeurs,
        'cours': cours,
        'cert_templates': cert_templates
    }        
    
    if request.method == 'POST' and 'excel_file' in request.FILES  :
        
        template_name = request.POST.get('template_name') # Récupérer le nom du modèle sélectionné
        template_path = os.path.join(settings.BASE_DIR, 'mon_application', 'static', 'certificates_templates', template_name)            
        instructeur_id = request.POST.get('instructeur')
        if instructeur_id == 'new_instructeur':
            new_instructeur_name = request.POST.get('new_instructeur_name')
            instructeur = Instructeur.objects.create(nom=new_instructeur_name)
            instructeur.save()
            return redirect('generate_certificates')
        instructeur = Instructeur.objects.get(id=instructeur_id)

        SIGNATURES_directory = os.path.join(settings.BASE_DIR, 'mon_application', 'static', 'signatures')
        if instructeur:
            nom_signature = instructeur.nom.replace(' ', '_') + '.jpg'
            signature_path = os.path.join(SIGNATURES_directory, nom_signature)
           
            if os.path.exists(signature_path):
                (width_px, height_px)=(118, 36)
                max_size = (118, 36)
                signature_image = Image.open(signature_path)
                signature_image = signature_image.filter(ImageFilter.SHARPEN)
                # Augmenter le contraste de l'image pour améliorer les détails et la clarté
                enhancer = ImageEnhance.Contrast(signature_image)
                signature_image = enhancer.enhance(1.5)
               
                signature_image = signature_image.resize((width_px, height_px), resample=Image.LANCZOS)
                
            else:
                signature_image = None
        else:
            signature_image = None

        cour_id= request.POST.get('cour')
        if cour_id == 'new_cour':
            new_cour_name = request.POST.get('new_cour_name')
            cour = Cours.objects.create(nom=new_cour_name)
            cour.save()
            return redirect('generate_certificates')
        cour = Cours.objects.get(id=cour_id)
     
        excel_file = request.FILES['excel_file']
        
        date_form = DateRangeForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        
        # Charger le fichier Excel
        
        df = pd.read_excel(excel_file, header=0, nrows=None)

        # Extraire la colonne "Participant" et l'enregistrer dans un fichier texte
        df_selection = df.loc[:, "Participant"]
        df_selection.to_csv('nom_du_participant.txt', index=False)

        # Ouvrir le fichier texte contenant les noms des participants
        with open("nom_du_participant.txt", encoding="utf-8-sig") as f:
            nom_du_participant = [line.strip() for line in f.readlines() if " " in line]

        # Créer une liste de noms de participants
        liste_participants = [nom.strip() for nom in nom_du_participant if " " in nom]
         # Remplacer les occurrences de "{{date}}" par les dates sélectionnées par l'utilisateur
        if start_date.year == end_date.year and start_date.month == end_date.month and start_date.day !=end_date.day:
            date_str = f"From {start_date.day} to {end_date.day} of {end_date:%B %Y}"
        elif start_date.year == end_date.year and start_date.month != end_date.month:
            date_str = f"From {start_date.day} {start_date:%B} to {end_date.day} {end_date:%B} {end_date.year}"
        else:
                        #date_str = f"From {start_date.day} {start_date:%B} to {end_date.day} {end_date:%B} {end_date.year}"
            date_str = f" {start_date.day}th of {start_date:%B},  {end_date.year}"  

        
        certificates = []
        for participant in liste_participants:
            # Créer un objet DocxTemplate à partir du fichier Word
            document =DocxTemplate(template_path)
            image_descriptor = None
            if signature_image is not None:
                image_buffer = io.BytesIO()
                signature_image.save(image_buffer, 'png')
                image_buffer.seek(0)
                image_descriptor = InlineImage(document, image_buffer)
           
            # Créer un dictionnaire contenant les variables à remplacer pour ce participant
            FORM_instructeur_cour_date = {'Instructeur': str(instructeur), 'Cour': str(cour), 'Date': date_str, 'Participant': participant,  'Signature': image_descriptor }#'Signature':signatureInlineImage(document, signature_image,width = 118, height = 36
            # Ajouter l'objet InlineImage au dictionnaire de variables à remplacer
        
            temp_file = f"{participant}.docx"
            # Remplacer les variables du modèle par les valeurs correspondantes
            document.render(FORM_instructeur_cour_date)
            # Enregistrer le fichier Word modifié avec le nom du participant
            document.save(temp_file)
            certificates.append(temp_file)
       
        # Créer un fichier zip contenant tous les certificats
        zip_filename = "certificates.zip"
        with zipfile.ZipFile(zip_filename, "w") as myzip:
            for cert in certificates:
                myzip.write(cert)
                # Supprimer le fichier individuel après l'avoir ajouté au fichier zip
                os.remove(cert)

        # Envoi du fichier zip en réponse à la requête
        with open(zip_filename, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/zip")
            response["Content-Disposition"] = f"attachment; filename={zip_filename}"
            return response
              
    return render(request, 'generate_certificates.html',context)

