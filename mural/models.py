from django.db import models


class MuralPermissions(models.Model):
    class Meta:
        verbose_name = "--Mural Permission--"
        verbose_name_plural = "--Mural Permissions--"
        permissions = [
            ("ger_mural", "Gerenciar Mural"),
        ]

    def __str__(self):
        return "Permissões personalizadas"
