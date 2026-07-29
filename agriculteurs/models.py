from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Agriculteur(models.Model):
    # 0. Identification unique pour éviter les doublons entre agents
    code_unique = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Code unique / Pièce d'identité")
    
    nom_prenom = models.CharField(max_length=255, verbose_name="Nom et prénom")
    
    SEXE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES, verbose_name="Sexe")
    
    age = models.IntegerField(verbose_name="Âge")
    localite = models.CharField(max_length=255, verbose_name="Localité")
    contact_telephonique = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact téléphonique")
    langue_principale = models.CharField(max_length=100, verbose_name="Langue principale parlée")
    niveau_instruction = models.CharField(max_length=100, verbose_name="Niveau d’instruction")
    activite_principale = models.CharField(max_length=255, verbose_name="Activité principale")
    experience = models.CharField(max_length=100, verbose_name="Expérience")
    principales_cultures = models.TextField(verbose_name="Principales cultures pratiquées")
    materiel_agricole = models.TextField(verbose_name="Matériel Agricole")
    ressources_disponibles = models.TextField(verbose_name="Ressources disponibles")
    methode_stockage = models.TextField(verbose_name="Méthode de stockage")
    source_eau = models.CharField(max_length=255, verbose_name="Source d’eau utilisée")
    periode_production = models.CharField(max_length=255, verbose_name="Période de production")
    total_production_an = models.CharField(max_length=255, verbose_name="Total de production/an")
    pertes_rencontrees = models.TextField(verbose_name="Les pertes rencontrées")
    problemes_rencontres = models.TextField(verbose_name="Problèmes/ difficultés rencontrés")

    # 1. Option de consentement pour la confidentialité (partage bailleurs)
    consentement_bailleur = models.BooleanField(default=False, verbose_name="Consentement accordé pour partager les données avec les bailleurs")

    # 2. Suivi des cas traités (ex: attribution d'un tracteur à Laila)
    STATUT_CHOICES = [
        ('en_attente', '⏳ En attente'),
        ('en_cours', '🔄 En cours de traitement'),
        ('traite', '✅ Traité / Résolu'),
    ]
    statut_traitement = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut du cas")
    notes_suivi = models.TextField(blank=True, null=True, verbose_name="Notes de suivi (ex: Tracteur attribué)")

    date_enregistrement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_prenom} - {self.localite}"


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('membre', 'Membre de l’ONG'),
        ('admin', 'Administrateur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre', verbose_name="Rôle / Profil")

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# Créer automatiquement un profil lorsqu'un utilisateur est créé
@receiver(post_save, sender=User)
def creer_profil_utilisateur(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)

@receiver(post_save, sender=User)
def sauvegarder_profil_utilisateur(sender, instance, **kwargs):
    instance.profil.save()