from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from .models import User,Doctor,Patient,Appointment,MedicalRecord

class DoctorRegistrationForm(UserCreationForm):
    specialization = forms.ChoiceField(choices=Doctor.SPECIALIZATION_CHOICES)
    phone = forms.CharField(max_length=15)
    department = forms.CharField(max_length=100)
    experience = forms.IntegerField()

    class Meta:
        model = User
        fields =  ['username', 'email', 'password1', 'password2', 'specialization', 'phone', 'department', 'experience']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        if commit:
            user.save()
            doctor = Doctor.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                phone=self.cleaned_data['phone'],
                specialization=self.cleaned_data['specialization'],
                department=self.cleaned_data['department'],
                experience=self.cleaned_data['experience']
            )
            doctor.save()
            group, _ = Group.objects.get_or_create(name='doctor')
            user.groups.add(group)
        return user



class PatientRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2100)))
    gender = forms.ChoiceField(choices=Patient.Gender_choices)
    address = forms.CharField(widget=forms.Textarea)
    medical_history = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'dob', 'gender', 'address', 'medical_history']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
            patient = Patient.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                phone=self.cleaned_data['phone'],
                dob=self.cleaned_data['dob'],
                gender=self.cleaned_data['gender'],
                address=self.cleaned_data['address'],
                medical_history=self.cleaned_data['medical_history']
            )
            patient.save()
            group, _ = Group.objects.get_or_create(name='patient')
            user.groups.add(group)
        return user







class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Enter your password'})
    )



class AppointmentForms(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor','appointmentdate','slot']
        widgets = {
            'appointmentdate':forms.DateInput(attrs={'type':'date'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_approved=True) 

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointmentdate = cleaned_data.get('appointmentdate')
        slot = cleaned_data.get('slot')

        if doctor and appointmentdate and slot:
            if Appointment.objects.filter(doctor=doctor, appointmentdate=appointmentdate, slot=slot).exists():
                raise forms.ValidationError("This slot is already booked. Please choose another.")
        return cleaned_data
    
class RescheduleAppointmentform(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointmentdate' , 'slot']
        widgets = {
            'appointmentdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }



class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'prescription', ]