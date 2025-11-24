from django.db import models










# Create your models here.
class PersonalPermissions(models.Model):
    class Meta:
        verbose_name = "--BKO-Permission--"
        verbose_name_plural = "--BKO-Permissions--"
        permissions = [
            ("BKO", "permission BKO"),
            ("Importar", "importar"),
           
        ]

    def __str__(self):
        return "Personal Permissions"
