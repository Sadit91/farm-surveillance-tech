from django import forms
from .models import Farm, SurveillanceSession, Observation
from django import forms
from pests.models import PlantPart
from .models import Pest, Disease

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['location', 'num_plants', 'stocking_rate']

class SurveillanceSessionForm(forms.ModelForm):
    farm = forms.ModelChoiceField(queryset=Farm.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['farm'].queryset = Farm.objects.filter(grower=user.grower)

    class Meta:
        model = SurveillanceSession
        fields = ['farm', 'plant_part', 'date', 'time_of_day']

class ObservationForm(forms.ModelForm):
    session = forms.ModelChoiceField(
        queryset=SurveillanceSession.objects.none(),
        label="Surveillance Session",
        required=True
    )
    pest = forms.ModelChoiceField(
        queryset=Pest.objects.all(),
        label="Pest",
        required=False,
        empty_label="(None)"
    )
    disease = forms.ModelChoiceField(
        queryset=Disease.objects.all(),
        label="Disease",
        required=False,
        empty_label="(None)"
    )

    class Meta:
        model = Observation
        fields = ['session', 'pest', 'disease', 'result']  # 'result' will be dropdown due to choices in model

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['session'].queryset = SurveillanceSession.objects.filter(farm__grower=user.grower)


class SurveillanceEffortForm(forms.Form):
    farm = forms.ModelChoiceField(
        queryset=Farm.objects.none(),
        label="Farm",
        required=True
    )
    plant_count = forms.IntegerField(
        label="Number of Plants",
        min_value=1
    )
    season = forms.ChoiceField(
        choices=[('dry', 'Dry Season'), ('wet', 'Wet Season')],
        label="Season"
    )
    plant_part = forms.ModelChoiceField(
        queryset=PlantPart.objects.all(),
        label="Plant part",
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['farm'].queryset = Farm.objects.filter(grower__user=user)

class PestForm(forms.ModelForm):
    class Meta:
        model = Pest
        fields = ['name', 'brief_description', 'image_url', 'details', 'control', 'impact', 'infestation_rate', 'sampling_multiplier']

class DiseaseForm(forms.ModelForm):
    class Meta:
        model = Disease
        fields = ['name', 'brief_description', 'image_url', 'details', 'control', 'impact', 'severity']