from django.db import models
from django.conf import settings

import os
class CertificateTemplatemodel(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(max_length=255)
    
    def __str__(self):
        return self.name

    
class Instructeur(models.Model):
    nom = models.CharField(max_length=255)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    
    def __str__(self):
        return self.nom
    
class Cours(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom


class Signature(models.Model):
    name = models.CharField(max_length=255,default='1')
    image = models.ImageField(upload_to='signatures',default='default_signature.jpg')
    image_type = models.CharField(max_length=5,default='3')

    def __str__(self):
        return self.name
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

   