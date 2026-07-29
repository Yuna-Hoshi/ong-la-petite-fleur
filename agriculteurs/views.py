from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse

# Imports pour la génération de PDF avec ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .models import Agriculteur, Profil
from .forms import AgriculteurForm

def page_connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Utiliser update_or_create pour forcer le rôle 'admin' si le compte est superuser
            role_attribue = 'admin' if user.is_superuser else 'agent'
            Profil.objects.update_or_create(
                user=user, 
                defaults={'role': role_attribue}
            )
            
            login(request, user)
            return redirect('dashboard_analyse')
    else:
        form = AuthenticationForm()
    return render(request, 'agriculteurs/connexion.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('connexion')

@login_required
def tableau_de_bord_analyse(request):
    qs = Agriculteur.objects.all()
    
    # Barre de recherche globale
    query = request.GET.get('q')
    if query:
        qs = qs.filter(
            Q(nom_prenom__icontains=query) |
            Q(localite__icontains=query) |
            Q(sexe__icontains=query) |
            Q(principales_cultures__icontains=query) |
            Q(age__icontains=query) |
            Q(code_unique__icontains=query)
        )
    
    total_agriculteurs = Agriculteur.objects.count()
    total_hommes = Agriculteur.objects.filter(sexe='Homme').count()
    total_femmes = Agriculteur.objects.filter(sexe='Femme').count()
    
    # Statistiques des cas traités
    total_cas = qs.count()
    cas_traites = qs.filter(statut_traitement='traite').count()
    cas_en_cours = qs.filter(statut_traitement='en_cours').count()
    cas_attente = qs.filter(statut_traitement='en_attente').count()
    
    # Statistiques basées sur l'ensemble de la base pour les graphiques/analyses
    qs_all = Agriculteur.objects.all()
    if qs_all.exists():
        data = list(qs_all.values())
        df = pd.DataFrame(data)
        
        top_localites = df['localite'].value_counts().head(5).to_dict() if 'localite' in df else {}
        top_cultures = df['principales_cultures'].value_counts().head(5).to_dict() if 'principales_cultures' in df else {}
        problemes_frequents = df['problemes_rencontres'].value_counts().head(5).to_dict() if 'problemes_rencontres' in df else {}
        sources_eau = df['source_eau'].value_counts().head(5).to_dict() if 'source_eau' in df else {}
        niveaux_instruction = df['niveau_instruction'].value_counts().head(5).to_dict() if 'niveau_instruction' in df else {}
        materiels = df['materiel_agricole'].value_counts().head(5).to_dict() if 'materiel_agricole' in df else {}
        methodes_stockage = df['methode_stockage'].value_counts().head(5).to_dict() if 'methode_stockage' in df else {}
        
        jeunes = qs_all.filter(age__lte=35).count()
        adultes = qs_all.filter(age__gt=35, age__lte=60).count()
        seniors = qs_all.filter(age__gt=60).count()
        tranches_ages = {
            'Moins de 35 ans': jeunes, 
            '35 - 60 ans': adultes, 
            'Plus de 60 ans': seniors
        }
    else:
        top_localites = top_cultures = problemes_frequents = sources_eau = niveaux_instruction = materiels = methodes_stockage = tranches_ages = {}

    contexte = {
        'total_agriculteurs': total_agriculteurs,
        'total_hommes': total_hommes,
        'total_femmes': total_femmes,
        'total_cas': total_cas,
        'cas_traites': cas_traites,
        'cas_en_cours': cas_en_cours,
        'cas_attente': cas_attente,
        'tranches_ages': tranches_ages,
        'top_localites': top_localites,
        'top_cultures': top_cultures,
        'problemes_frequents': problemes_frequents,
        'sources_eau': sources_eau,
        'niveaux_instruction': niveaux_instruction,
        'materiels': materiels,
        'methodes_stockage': methodes_stockage,
        'agriculteurs_list': qs,
        'search_query': query or '',
    }
    
    return render(request, 'agriculteurs/dashboard.html', contexte)

@login_required
def liste_agriculteurs(request):
    qs = Agriculteur.objects.all()
    
    query = request.GET.get('q')
    if query:
        qs = qs.filter(
            Q(nom_prenom__icontains=query) |
            Q(localite__icontains=query) |
            Q(sexe__icontains=query) |
            Q(principales_cultures__icontains=query) |
            Q(age__icontains=query) |
            Q(code_unique__icontains=query)
        )
        
    context = {
        'agriculteurs': qs,
        'search_query': query or '',
    }
    return render(request, 'agriculteurs/liste_agriculteurs.html', context)

@login_required
def detail_agriculteur(request, pk):
    agriculteur = get_object_or_404(Agriculteur, pk=pk)
    return render(request, 'agriculteurs/detail_agriculteur.html', {'agriculteur': agriculteur})

@login_required
def ajouter_agriculteur(request):
    if request.method == 'POST':
        form = AgriculteurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_analyse')
    else:
        form = AgriculteurForm()
    return render(request, 'agriculteurs/ajouter_agriculteur.html', {'form': form})

@login_required
def modifier_agriculteur(request, pk):
    agriculteur = get_object_or_404(Agriculteur, pk=pk)
    if request.method == 'POST':
        form = AgriculteurForm(request.POST, instance=agriculteur)
        if form.is_valid():
            form.save()
            return redirect('liste_agriculteurs')
    else:
        form = AgriculteurForm(instance=agriculteur)
    return render(request, 'agriculteurs/modifier_agriculteur.html', {'form': form, 'agriculteur': agriculteur})

@login_required
def supprimer_agriculteur(request, pk):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profil') and request.user.profil.role == 'admin')
    if not is_admin:
        return redirect('liste_agriculteurs')
        
    agriculteur = get_object_or_404(Agriculteur, pk=pk)
    agriculteur.delete()
    return redirect('dashboard_analyse')

@login_required
def rapport_analyse_imprimable(request):
    # Restriction : Seul l'administrateur peut voir et imprimer le rapport d'analyse
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profil') and request.user.profil.role == 'admin')
    if not is_admin:
        return redirect('dashboard_analyse')

    qs = Agriculteur.objects.all()
    
    total_agriculteurs = qs.count()
    total_hommes = qs.filter(sexe='Homme').count()
    total_femmes = qs.filter(sexe='Femme').count()
    
    if qs.exists():
        data = list(qs.values())
        df = pd.DataFrame(data)
        top_localites = df['localite'].value_counts().head(5).to_dict() if 'localite' in df else {}
        top_cultures = df['principales_cultures'].value_counts().head(5).to_dict() if 'principales_cultures' in df else {}
        problemes_frequents = df['problemes_rencontres'].value_counts().head(5).to_dict() if 'problemes_rencontres' in df else {}
        sources_eau = df['source_eau'].value_counts().head(5).to_dict() if 'source_eau' in df else {}
        niveaux_instruction = df['niveau_instruction'].value_counts().head(5).to_dict() if 'niveau_instruction' in df else {}
        materiels = df['materiel_agricole'].value_counts().head(5).to_dict() if 'materiel_agricole' in df else {}
        methodes_stockage = df['methode_stockage'].value_counts().head(5).to_dict() if 'methode_stockage' in df else {}
        
        jeunes = qs.filter(age__lte=35).count()
        adultes = qs.filter(age__gt=35, age__lte=60).count()
        seniors = qs.filter(age__gt=60).count()
        tranches_ages = {
            'Moins de 35 ans': jeunes, 
            '35 - 60 ans': adultes, 
            'Plus de 60 ans': seniors
        }
    else:
        top_localites = top_cultures = problemes_frequents = sources_eau = niveaux_instruction = materiels = methodes_stockage = tranches_ages = {}

    contexte = {
        'total_agriculteurs': total_agriculteurs,
        'total_hommes': total_hommes,
        'total_femmes': total_femmes,
        'tranches_ages': tranches_ages,
        'top_localites': top_localites,
        'top_cultures': top_cultures,
        'problemes_frequents': problemes_frequents,
        'sources_eau': sources_eau,
        'niveaux_instruction': niveaux_instruction,
        'materiels': materiels,
        'methodes_stockage': methodes_stockage,
    }
    return render(request, 'agriculteurs/rapport_analyse.html', contexte)

@login_required
def exporter_donnees_pdf(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profil') and request.user.profil.role == 'admin')
    if not is_admin:
        return redirect('liste_agriculteurs')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_agriculteurs.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=15,
        alignment=1
    )
    
    elements.append(Paragraph("Rapport des Agriculteurs - ONG La Petite Fleur", title_style))
    elements.append(Spacer(1, 10))

    qs = Agriculteur.objects.filter(consentement_bailleur=True)
    
    data = [["Nom & Prénom", "Sexe", "Âge", "Localité", "Statut"]]
    for ag in qs:
        data.append([
            ag.nom_prenom,
            ag.sexe,
            str(ag.age),
            ag.localite,
            ag.get_statut_traitement_display()
        ])

    table = Table(data, colWidths=[150, 60, 40, 130, 160])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9F9F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    elements.append(table)
    doc.build(elements)
    return response

@login_required
def exporter_donnees_excel(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profil') and request.user.profil.role == 'admin')
    if not is_admin:
        return redirect('liste_agriculteurs')
    
    qs = Agriculteur.objects.filter(consentement_bailleur=True)
    data = list(qs.values())
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="rapport_bailleurs_consentants.xlsx"'
    
    df.to_excel(response, index=False, engine='openpyxl')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser or (hasattr(u, 'profil') and u.profil.role == 'admin'))
def supprimer_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.delete()
    return redirect('gestion_utilisateurs')

@login_required
@user_passes_test(lambda u: u.is_superuser or (hasattr(u, 'profil') and u.profil.role == 'admin'))
def modifier_utilisateur(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    profil_to_edit, created = Profil.objects.get_or_create(user=user_to_edit)
    
    ROLES_CHOICES = [
        ('agent', 'Agent'),
        ('admin', 'Administrateur'),
    ]

    if request.method == 'POST':
        nouveau_role = request.POST.get('role', 'agent')
        profil_to_edit.role = nouveau_role
        profil_to_edit.save()
        
        # Mettre à jour is_superuser si nécessaire
        if nouveau_role == 'admin' and not user_to_edit.is_superuser:
            user_to_edit.is_superuser = False # Conserver le contrôle fin via Profil
        
        return redirect('gestion_utilisateurs')

    context = {
        'user_to_edit': user_to_edit,
        'profil_to_edit': profil_to_edit,
        'roles': ROLES_CHOICES
    }
    return render(request, 'agriculteurs/modifier_utilisateur.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser or (hasattr(u, 'profil') and u.profil.role == 'admin'))
def gestion_utilisateurs(request):
    ROLES_CHOICES = [
        ('agent', 'Agent'),
        ('admin', 'Administrateur'),
    ]

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'agent')
        
        if form.is_valid():
            user = form.save()
            Profil.objects.update_or_create(
                user=user,
                defaults={'role': role}
            )
            return redirect('gestion_utilisateurs')
    else:
        form = UserCreationForm()
    
    utilisateurs = User.objects.all()
    return render(request, 'agriculteurs/gestion_utilisateurs.html', {
        'form': form,
        'utilisateurs': utilisateurs,
        'roles': ROLES_CHOICES
    })