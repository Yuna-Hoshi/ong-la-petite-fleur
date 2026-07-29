from django import forms
from .models import Agriculteur

class AgriculteurForm(forms.ModelForm):
    class Meta:
        model = Agriculteur
        fields = [
            'code_unique',
            'nom_prenom',
            'sexe',
            'age',
            'localite',
            'contact_telephonique',
            'langue_principale',
            'niveau_instruction',
            'activite_principale',
            'experience',
            'principales_cultures',
            'materiel_agricole',
            'ressources_disponibles',
            'methode_stockage',
            'source_eau',
            'periode_production',
            'total_production_an',
            'pertes_rencontrees',
            'problemes_rencontres',
            # Nouveaux champs de suivi et confidentialité
            'statut_traitement',
            'notes_suivi',
            'consentement_bailleur',  # Placé en bas
        ]
        widgets = {
            'problemes_rencontres': forms.Textarea(attrs={'rows': 3}),
            'materiel_agricole': forms.Textarea(attrs={'rows': 2}),
            'ressources_disponibles': forms.Textarea(attrs={'rows': 2}),
            'methode_stockage': forms.Textarea(attrs={'rows': 2}),
            'pertes_rencontrees': forms.Textarea(attrs={'rows': 2}),
            'notes_suivi': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Matériel ou tracteur attribué, suivi en cours...'}),
            'consentement_bailleur': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'}),
        }

    # Empêcher les doublons en vérifiant si le code unique existe déjà
    def clean_code_unique(self):
        code = self.cleaned_data.get('code_unique')
        if code:
            qs = Agriculteur.objects.filter(code_unique=code)
            # Si on est en train de modifier une fiche existante, on l'exclut de la vérification
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("⚠️ Un agriculteur avec ce code unique ou cette pièce d'identité existe déjà dans la base !")
        return code