from django.shortcuts import render, redirect, get_object_or_404
from .forms import DoctorRegistrationForm,PatientRegistrationForm,AppointmentForms,RescheduleAppointmentform,MedicalRecordForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.db.models import Count,Q
from django.contrib.auth import logout
from .models import User,Doctor,Patient,Appointment,MedicalRecord,Billing
from django.contrib import messages 
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.


def doctor_registration(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.role = 'doctor'  # Assign role
            user.save()  # Save user first

            # Add user to "Doctor" group
            doctor_group, _ = Group.objects.get_or_create(name='Doctor')
            user.groups.add(doctor_group)

            # Create associated Doctor profile
            Doctor.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                specialization=form.cleaned_data['specialization'],
                department=form.cleaned_data['department'],
                experience=form.cleaned_data['experience']
            )

            messages.success(request, "Doctor registered successfully! Please login.")
            return redirect('rolepage')
        else:
            messages.error(request,'error occured')

    else:
        form = DoctorRegistrationForm()

    return render(request, 'core/doctorRegistration.html', {'form': form})

# def doctor_registration(request):
#     if request.method == 'POST':
#         form = DoctorRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request,"Doctor registered Succesfully, Please login")
#             return redirect('rolepage')
#     else:
#         form =DoctorRegistrationForm()
#     return render(request, 'core/doctorRegistration.html',{'form':form})

def patient_registration(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()

            # Add user to "Doctor" group
            patient_group, _ = Group.objects.get_or_create(name='Patient')
            user.groups.add(patient_group)
        
            Patient.objects.create(
                user = user,
                phone = form.cleaned_data['phone'],
                dob = form.cleaned_data['dob'],
                gender = form.cleaned_data['gender'],
                address = form.cleaned_data['address'],
                medical_history = form.cleaned_data['medical_history']
            )
            
            
            messages.success(request, "Patient registered successfully. Please log in.")
            return redirect('rolepage')

    else:
        form = PatientRegistrationForm()
    return render(request, 'core/patientRegister.html', {'form': form})

def register(request):
    return render(request, 'core/register.html')


def rolepage(request):
    return render(request, 'core/rolepage.html')



class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.request.GET.get('role', '')  
        context['role'] = role  
        return context
    

    def form_valid(self, form):
        user = form.get_user()

        
        if user.groups.filter(name='Doctor').exists():
            try:
                doctor = Doctor.objects.get(user=user)
                if not doctor.is_approved:
                    logout(self.request)
                    return redirect(reverse_lazy('rolepage') + '?error=not_approved') 
            except Doctor.DoesNotExist:
                pass  

        return super().form_valid(form)
    
    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Doctor').exists():
            return reverse_lazy('doctor_dashboard')  
        elif user.groups.filter(name='Patient').exists():
            return reverse_lazy('patient_dashboard')
        elif user.is_superuser:  
            return reverse_lazy('admin_dashboard') 


def is_doctor(user):
    return user.groups.filter(name='Doctor').exists()

def is_patient(user):
    return user.groups.filter(name="Patient").exists()

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    return render(request, 'core/doctordashboard.html')


@login_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    return render(request, 'core/patientdashboard.html')


@login_required
@user_passes_test(is_patient)
def book_Appointment(request):
    if request.method == 'POST':
        form = AppointmentForms(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient_profile
            appointment.save()
            messages.success(request,"Your appointment has been booked Successfully")
            return redirect("patient_dashboard")
        else:
            messages.error(request, "Error Booking appointment, please Try again")
    else:
        form = AppointmentForms()
    return render(request, 'core/appointments/book_appointment.html',{'form':form})


@login_required
@user_passes_test(is_patient)
def myAppointments(request):
    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient)
    doctors = Doctor.objects.all()
    
    return render(request, 'core/appointments/myappointments.html',{"appointments":appointments,"doctors":doctors} )

@login_required
def rescheduleappointment(request, appointment_id):
    patient = Patient.objects.get(user=request.user)
    appointment = get_object_or_404(Appointment,id=appointment_id, patient=patient)

    if request.method == 'POST':
        form = RescheduleAppointmentform(request.POST, instance=appointment)
        if form.is_valid():
            new_date = form.cleaned_data['appointmentdate']
            new_time = form.cleaned_data['slot']

            # Check if the doctor is already booked at the new date & time
            conflict = Appointment.objects.filter(
                doctor=appointment.doctor.id,
                appointmentdate=new_date,
                slot=new_time
            ).exclude(id=appointment.id).exists()

            if conflict:
                messages.error(request, "This time slot is already booked. Please choose another.")
            else:
                form.save()
                messages.success(request, "Appointment rescheduled successfully.")
                return redirect('myappointments')
    else:
        form = RescheduleAppointmentform(instance=appointment)
    
    return render(request, 'core/appointments/rescheduleappointment.html',{'form':form})

@login_required
def deleteappointment(request, appointment_id):
    patient = Patient.objects.get(user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id,patient=patient)

    if request.method == 'POST':
        appointment.delete()
        return redirect('myappointments')
    
    return render(request, 'core/appointments/deleteappointments.html',{'appointment':appointment})


def doctorslist(request):
    doctors = Doctor.objects.filter(is_approved = True)
    return render(request, 'core/doctors/doctorslist.html', {'doctors':doctors})

def logoutuser(request):
    logout(request)
    return redirect('rolepage')


@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    return render(request, 'core/doctordasboard.html')

@login_required
def doctor_appointments(request):
    doctor = Doctor.objects.get(user=request.user)  
    date_filter = request.GET.get('date')

    if date_filter:
        appointments = Appointment.objects.filter(doctor=doctor, appointmentdate=date_filter)
    else:
        appointments = Appointment.objects.filter(doctor=doctor)

    return render(request, 'core/appointments/doctor_appointments.html', {'appointments': appointments})


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user == appointment.doctor.user:
        appointment.status = "Cancelled"
        appointment.save()
    return redirect('doctor_appointments')


@login_required
def reschedule_doctorappointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == "POST":
        new_date = request.POST.get('new_date')
        appointment.appointmentdate = new_date
        appointment.save()
        return redirect('doctor_appointments')

    return render(request, 'core/doctors/rescheduleappointmentd.html', {'appointment': appointment})

@login_required
@user_passes_test(is_doctor)
def attend_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user == appointment.doctor.user:
        appointment.status = "Completed"
        appointment.save()
        return redirect('medical_record', appointment_id=appointment.id)
    return redirect('doctor_appointments')


@login_required
def medical_record(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)


    medical_record, created = MedicalRecord.objects.get_or_create(
        appointment=appointment,
        patient = appointment.patient
    )

    if request.method == 'POST':
        form =MedicalRecordForm(request.POST,instance=medical_record)
        if form.is_valid():
            form.save()
            return redirect('doctor_appointments')
    else:
        form = MedicalRecordForm(instance=medical_record)
    
    return render(request, 'core/doctors/medical_record.html',{'form':form, 'appointment': appointment})



@login_required
@user_passes_test(is_doctor)
def doctor_medical_records(request):
    doctor = get_object_or_404(Doctor, user=request.user)  
    medical_records = MedicalRecord.objects.filter(doctor=doctor)
    
    return render(request, "core/doctors/medical_records.html", {"medical_records": medical_records})


@login_required
@user_passes_test(is_doctor)
def generate_bill(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    bill, created = Billing.objects.get_or_create(
        appointment=appointment,
        defaults={
            "patient": appointment.patient,
            "total_amount": 500.00, 
        },
    )

    if created:
        appointment.bill = True
        appointment.save()

    return redirect("doctor_appointments")


@login_required
def view_bill(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)
    return render(request, "core/billing/bill_details.html", {"bill": bill})


@login_required
def patientbills(request):
    patient = Patient.objects.get(user=request.user)
    bills = Billing.objects.filter(patient=patient)
    return render(request, 'core/patients/patientbills.html', {'bills': bills})

@login_required
def patientmedicalhistory(request):
    patient = Patient.objects.get(user=request.user)
    medicalhistory = MedicalRecord.objects.filter(patient=patient)

    return render(request,'core/patients/medicalhistory.html',{'records' : medicalhistory})

@login_required
@staff_member_required
def admin_dashboard_view(request):
    return render(request, 'core/admindashboard.html')


@login_required
@staff_member_required
def pending_doctor_approvals(request):
    pendingdoctors = Doctor.objects.filter(is_approved = False)
    return render(request, 'core/admin/pending_doctors.html', {'pending_doctors':pendingdoctors})


@login_required
@staff_member_required
def approve_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor,id=doctor_id)
    doctor.is_approved = True
    doctor.save()
    messages.success(request, f"Doctor {doctor.user.username} has been approved!")
    return redirect('pending_doctors')

@login_required
@staff_member_required
def reject_doctor(request, doctor_id):

    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.user.delete()  
    messages.warning(request, "Doctor has been rejected and removed.")
    return redirect('pending_doctors')



@login_required
@staff_member_required
def manage_doctors(request):
    doctors = Doctor.objects.filter(is_approved=True)  
    return render(request, 'core/admin/manage_doctors.html', {'doctors': doctors})


@login_required
@staff_member_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = doctor.user
    doctor.delete()
    user.delete()

    messages.success(request, "Doctor has been removed successfully.")
    return redirect('manage_doctors')


@login_required
@staff_member_required
def manage_patients(request):

    patients = Patient.objects.annotate(
        visit_count=Count('appointment', filter=Q(appointment__status="Completed")),
        appointmentsScheduled = Count('appointment',filter=Q(appointment__status="Scheduled")),
        appointmentsCancelled=Count('appointment', filter=Q(appointment__status = "Cancelled")),
    )  # Count completed appointments per patient

    return render(request, 'core/admin/manage_patients.html', {'patients': patients})



@login_required
@staff_member_required
def view_medical_records(request, patient_id):

    patient = get_object_or_404(Patient, id=patient_id)
    medical_records = MedicalRecord.objects.filter(patient=patient)

    return render(request, 'core/admin/view_medical_records.html', {'patient': patient, 'medical_records': medical_records})

@login_required
@staff_member_required
def admin_appointments(request):
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    appointments = Appointment.objects.all()

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        appointments = appointments.filter(appointmentdate=date_filter)

    return render(request, 'core/admin/admin_appointments.html', {'appointments': appointments})

@login_required
@staff_member_required
def cancelappointment_admin(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Cancelled"
    appointment.save()
    messages.success(request, "Appointment cancelled successfully.")
    return redirect('admin_appointments')


@login_required
@staff_member_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    
    if request.method == 'POST':
        form = RescheduleAppointmentform(request.POST, instance=appointment)
        if form.is_valid():
            new_date = form.cleaned_data['appointmentdate']
            new_time = form.cleaned_data['slot']
            conflict = Appointment.objects.filter(
                doctor=appointment.doctor.id,
                appointmentdate=new_date,
                slot=new_time
            ).exclude(id=appointment.id).exists()

            
            if conflict:
                messages.error(request, "This time slot is already booked. Please choose another.")
            else:
                form.save()
                messages.success(request, "Appointment rescheduled successfully.")
                return redirect('admin_appointments')
    else:
        form = RescheduleAppointmentform(instance=appointment)
    
    return render(request, 'core/admin/appresc.html',{'form':form})
    

@login_required
@staff_member_required
def admin_billing(request):
    bills = Billing.objects.all()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bills = bills.filter(payment_status=status_filter)

    return render(request, 'core/admin/billingadmin.html', {'bills': bills})

@login_required
@staff_member_required
def mark_bill_as_paid(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)
    bill.payment_status = "Paid"
    bill.save()
    messages.success(request, "Bill marked as Paid.")
    return redirect('admin_billing')


@login_required
@staff_member_required
def delete_bill(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)
    bill.delete()
    messages.success(request, "Bill deleted successfully.")
    return redirect('admin_billing')