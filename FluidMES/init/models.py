from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuarios(models.Model):
    """Model definition for MODELNAME."""


    # TODO: Define fields here

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'MODELNAME'
        verbose_name_plural = 'MODELNAMEs'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        pass
