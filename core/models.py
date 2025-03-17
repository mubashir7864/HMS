from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    Role_Choices = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]



    role = models.CharField(max_length=10,choices=Role_Choices, default='')

    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="core_users",  # Unique related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="core_users_permissions",  # Unique related_name
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    

    

class Patient(models.Model):
    Gender_choices = [
        ('Male','Male'),
        ('Female','Female'),
        ('Other','Other')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone = models.CharField(max_length=15,unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=50,choices=Gender_choices,default=None)
    address = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user



class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('General Physician', 'General Physician'),
        ('ENT', 'ENT'),
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Neurologist', 'Neurologist'),
        ('Pediatrician', 'Pediatrician'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    phone = models.CharField(max_length=15, unique=True)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    department = models.CharField(max_length=100)
    experience = models.IntegerField(help_text="years of experience")
    joining_date = models.DateField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} ({self.specialization})"


class Appointment(models.Model):
    slot_choices = [
        ('Morning','Morning'),
        ('Afternoon','Afternoon'),
        ('Evening','Evening')
    ]

    Appointment_status = [ 
        ("Scheduled",'Scheduled'),
        ("Completed","Completed"),
        ("Cancelled","Cancelled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointmentdate = models.DateField()
    slot = models.CharField(max_length=20, choices=slot_choices)
    status = models.CharField(max_length=20, choices= Appointment_status, default="Scheduled")
    notes = models.TextField(blank=True,null=True)
    bill = models.BooleanField(default=False)


    class Meta:
         unique_together = ('doctor', 'appointmentdate', 'slot')


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    prescription = models.TextField()
    visit_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Medical Record of {self.patient.name} - {self.visit_date}"

    


class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')], default='Pending')
    bill_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Billing for {self.patient.name} - {self.total_amount}"




