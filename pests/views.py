from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Pest, Disease
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .forms import FarmForm, SurveillanceSessionForm, ObservationForm
from .models import Farm, SurveillanceSession, Observation
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .models import Grower
from django.utils.timezone import now, timedelta
from django.db.models import Count
import json
import csv
from django.http import HttpResponse
from math import ceil
from .forms import SurveillanceEffortForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from .forms import PestForm, DiseaseForm
from django.db.models import Q


def custom_404(request, exception):
    return render(request, "pests/404.html", status=404)

def home(request):
    query = request.GET.get('q', '')
    items = []

    if query:
        pest_results = Pest.objects.filter(name__icontains=query) | Pest.objects.filter(brief_description__icontains=query)
        disease_results = Disease.objects.filter(name__icontains=query) | Disease.objects.filter(brief_description__icontains=query)
        items = list(pest_results) + list(disease_results)

    ctx = {
        'items': items,
        'query': query,
    }
    return render(request, 'pests/home.html', ctx)

class pro_list(ListView):
    template_name = "pests/proj_list.html"
    context_object_name = "itms"

    def get_queryset(self):
        ftype = self.request.GET.get("type", "")
        if ftype == "pest":
            return Pest.objects.all()
        elif ftype == "disease":
            return Disease.objects.all()
        return list(Pest.objects.all()) + list(Disease.objects.all())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ftype"] = self.request.GET.get("type", "")
        return ctx

class pro_det(DetailView):
    template_name = "pests/project_detail.html"
    context_object_name = "itm"

    def get_object(self):
        pid = self.kwargs.get("pid")
        itype = self.kwargs.get("itype")
        if itype == "pest":
            return get_object_or_404(Pest, id=pid)
        elif itype == "disease":
            return get_object_or_404(Disease, id=pid)
        raise Http404("Invalid type")

def about(request):
    tm = [
        {'n': 'Sadit Khan.', 'student_id': 'S379452'},
        {'n': 'Nguyen Hao Vo.', 'student_id': 'S377196'},
        {'n': 'Fabiha Sultana Anushe.', 'student_id': 'S372205'},
        {'n': 'Roshan Karki.', 'student_id': 'S365632'},
    ]
    ctx = {'tm': tm}
    return render(request, 'pests/about.html', ctx)

# -------- FARM VIEWS --------
class FarmListView(ListView):
    model = Farm
    template_name = 'pests/portal/farm_list.html'
    context_object_name = 'farms'

    def get_queryset(self):
        return Farm.objects.filter(grower=self.request.user.grower)

class FarmCreateView(CreateView):
    model = Farm
    form_class = FarmForm
    template_name = 'pests/portal/farm_form.html'
    success_url = reverse_lazy('farm_list')

    def form_valid(self, form):
        form.instance.grower = self.request.user.grower
        return super().form_valid(form)

class FarmUpdateView(UpdateView):
    model = Farm
    form_class = FarmForm
    template_name = 'pests/portal/farm_form.html'
    success_url = reverse_lazy('farm_list')

class FarmDeleteView(DeleteView):
    model = Farm
    template_name = 'pests/portal/farm_confirm_delete.html'
    success_url = reverse_lazy('farm_list')

# -------- SESSION VIEWS --------
class SessionListView(ListView):
    model = SurveillanceSession
    template_name = 'pests/portal/session_list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return SurveillanceSession.objects.filter(farm__grower=self.request.user.grower)

class SessionCreateView(CreateView):
    model = SurveillanceSession
    form_class = SurveillanceSessionForm
    template_name = 'pests/portal/session_form.html'
    success_url = reverse_lazy('session_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass user for farm dropdown
        return kwargs

class SessionUpdateView(UpdateView):
    model = SurveillanceSession
    form_class = SurveillanceSessionForm
    template_name = 'pests/portal/session_form.html'
    success_url = reverse_lazy('session_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass user to form
        return kwargs

class SessionDeleteView(DeleteView):
    model = SurveillanceSession
    template_name = 'pests/portal/session_confirm_delete.html'
    success_url = reverse_lazy('session_list')

# -------- OBSERVATION VIEWS --------
class ObservationListView(ListView):
    model = Observation
    template_name = 'pests/portal/observation_list.html'
    context_object_name = 'observations'

    def get_queryset(self):
        return Observation.objects.filter(session__farm__grower=self.request.user.grower)

class ObservationCreateView(CreateView):
    model = Observation
    form_class = ObservationForm
    template_name = 'pests/portal/observation_form.html'
    success_url = reverse_lazy('observation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ObservationUpdateView(UpdateView):
    model = Observation
    form_class = ObservationForm
    template_name = 'pests/portal/observation_form.html'
    success_url = reverse_lazy('observation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        return kwargs

class ObservationDeleteView(DeleteView):
    model = Observation
    template_name = 'pests/portal/observation_confirm_delete.html'
    success_url = reverse_lazy('observation_list')

@login_required
def grower_portal(request):
    grower = request.user.grower
    today = now().date()
    past_30_days = today - timedelta(days=30)

    farm_count = Farm.objects.filter(grower=grower).count()
    session_count = SurveillanceSession.objects.filter(farm__grower=grower).count()
    observation_count = Observation.objects.filter(session__farm__grower=grower).count()

    # New: Filtered by date
    recent_sessions = SurveillanceSession.objects.filter(
        farm__grower=grower,
        date__gte=past_30_days
    ).count()

    recent_observations = Observation.objects.filter(
        session__farm__grower=grower,
        session__date__gte=past_30_days
    ).count()

    return render(request, "pests/portal.html", {
        "farm_count": farm_count,
        "session_count": session_count,
        "observation_count": observation_count,
        "recent_sessions": recent_sessions,
        "recent_observations": recent_observations
    })


# -------- REGISTRATION VIEW --------
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-create linked Grower profile
            Grower.objects.create(user=user, name=user.username, age=0, email=user.email)
            login(request, user)
            return redirect('grower_portal')
    else:
        form = UserCreationForm()
    return render(request, 'pests/registration/register.html', {'form': form})

# -------- LOGOUT VIEW --------
def logout_view(request):
    logout(request)
    return redirect('home')

# -------- DASHBOARD --------
@login_required
def grower_portal(request):
    grower = request.user.grower
    today = now().date()
    past_30_days = today - timedelta(days=30)

    # Summary counts
    farm_count = Farm.objects.filter(grower=grower).count()
    session_count = SurveillanceSession.objects.filter(farm__grower=grower).count()
    observation_count = Observation.objects.filter(session__farm__grower=grower).count()

    # Recent 30-day counts
    recent_sessions = SurveillanceSession.objects.filter(
        farm__grower=grower,
        date__gte=past_30_days
    ).count()

    recent_observations = Observation.objects.filter(
        session__farm__grower=grower,
        session__date__gte=past_30_days
    ).count()

    # Sessions by plant part (for chart)
    session_data = SurveillanceSession.objects.filter(farm__grower=grower).values(
    'plant_part__name'
).annotate(count=Count('id'))

    plant_labels = [item['plant_part__name'] for item in session_data]
    plant_counts = [item['count'] for item in session_data]

    return render(request, "pests/portal.html", {
        "farm_count": farm_count,
        "session_count": session_count,
        "observation_count": observation_count,
        "recent_sessions": recent_sessions,
        "recent_observations": recent_observations,
        "plant_labels": json.dumps(plant_labels),
        "plant_counts": json.dumps(plant_counts)
    })

# -------- SURVEILLANCE EFFORT FORM --------

def effort_calculator(request):
    user = request.user
    result = None
    plant_count = season = plant_part = location = stocking_rate = None

    if request.method == "POST":
        form = SurveillanceEffortForm(request.POST, user=user)
        if form.is_valid():
            farm = form.cleaned_data['farm']
            plant_count = form.cleaned_data['plant_count']
            season = form.cleaned_data['season']
            plant_part = form.cleaned_data['plant_part']
            location = farm.location
            stocking_rate = farm.stocking_rate

            # Calculation logic (customize if needed)
            multiplier = 1.5 if season == "wet" else 1.0
            result = ceil((plant_count ** 0.5) * multiplier)
    else:
        initial = {}
        farm_id = request.GET.get('farm')
        if farm_id:
            try:
                farm = Farm.objects.get(id=farm_id, grower__user=user)
                initial['farm'] = farm
                initial['plant_count'] = farm.num_plants
            except Farm.DoesNotExist:
                pass
        form = SurveillanceEffortForm(user=user, initial=initial)

    return render(request, "pests/portal/effort_calculator.html", {
        "form": form,
        "result": result,
        "plant_count": plant_count,
        "season": season,
        "plant_part": plant_part,
        "location": location,
        "stocking_rate": stocking_rate,
    })

@login_required
def get_farm_plants(request):
    farm_id = request.GET.get('farm_id')
    try:
        farm = Farm.objects.get(id=farm_id, grower__user=request.user)
        return JsonResponse({'num_plants': farm.num_plants})
    except Farm.DoesNotExist:
        return JsonResponse({'num_plants': None}, status=404)

# -------- EXPORT DATA FEATURE --------

def export_all_data_json(request):
    grower = request.user.grower
    data = []

    for farm in Farm.objects.filter(grower=grower):
        farm_data = {
            "location": farm.location,
            "num_plants": farm.num_plants,
            "stocking_rate": float(farm.stocking_rate),
            "sessions": [],
        }

        for session in farm.sessions.all():
            session_data = {
                "date": str(session.date),
                "time_of_day": session.time_of_day,
                "plant_part": session.plant_part.name if session.plant_part else None,
                "observations": []
            }

            for obs in session.observations.all():
                session_data["observations"].append({
                    "pest": obs.pest.name if obs.pest else None,
                    "disease": obs.disease.name if obs.disease else None,
                    "result": obs.result,
                })

            farm_data["sessions"].append(session_data)

        data.append(farm_data)

    return JsonResponse(data, safe=False, json_dumps_params={"indent": 2})

def export_all_data_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="surveillance_data.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Farm Location", "Number of Plants", "Stocking Rate",
        "Session Date", "Time of Day", "Plant Part",
        "Pest", "Disease", "Result"
    ])

    for farm in Farm.objects.filter(grower=request.user.grower):
        for session in farm.sessions.all():
            for obs in session.observations.all():
                writer.writerow([
                    farm.location,
                    farm.num_plants,
                    float(farm.stocking_rate),
                    session.date,
                    session.time_of_day,
                    session.plant_part.name if session.plant_part else None,
                    obs.pest.name if obs.pest else None,
                    obs.disease.name if obs.disease else None,
                    obs.result
                ])
            if not session.observations.exists():
                writer.writerow([
                    farm.location,
                    farm.num_plants,
                    float(farm.stocking_rate),
                    session.date,
                    session.time_of_day,
                    session.plant_part.name if session.plant_part else None,
                    None, None, None
                ])
        if not farm.sessions.exists():
            writer.writerow([
                farm.location,
                farm.num_plants,
                float(farm.stocking_rate),
                None, None, None, None, None, None
            ])

    return response

def global_index_table(request):
    observations = Observation.objects.select_related(
        'session', 'session__farm', 'session__plant_part', 'pest', 'disease'
    ).all()

    context = {'observations': observations}
    return render(request, 'pests/global_index_table.html', context)

# -------- Add Custom Pest or Disease --------

@method_decorator(login_required, name='dispatch')
class PestCreateView(CreateView):
    model = Pest
    form_class = PestForm
    template_name = 'pests/portal/pest_form.html'
    success_url = reverse_lazy('project_list')

@method_decorator(login_required, name='dispatch')
class DiseaseCreateView(CreateView):
    model = Disease
    form_class = DiseaseForm
    template_name = 'pests/portal/disease_form.html'
    success_url = reverse_lazy('project_list')

@login_required
def add_item_choice(request):
    return render(request, 'pests/portal/add_item_choice.html')


# -------- Delete Custom Pest or Disease --------

@login_required
def delete_item_choice(request):
    return render(request, 'pests/portal/delete_item_choice.html')

@method_decorator(login_required, name='dispatch')
class PestDeleteListView(ListView):
    model = Pest
    template_name = 'pests/portal/pest_delete_list.html'
    context_object_name = 'pests'

@method_decorator(login_required, name='dispatch')
class DiseaseDeleteListView(ListView):
    model = Disease
    template_name = 'pests/portal/disease_delete_list.html'
    context_object_name = 'diseases'

@method_decorator(login_required, name='dispatch')
class PestDeleteView(DeleteView):
    model = Pest
    template_name = 'pests/portal/pest_confirm_delete.html'
    success_url = reverse_lazy('pest_delete_list')

@method_decorator(login_required, name='dispatch')
class DiseaseDeleteView(DeleteView):
    model = Disease
    template_name = 'pests/portal/disease_confirm_delete.html'
    success_url = reverse_lazy('disease_delete_list')