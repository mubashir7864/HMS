from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .views import CustomLoginView,rolepage,doctor_registration,patient_registration,register
from .views import doctor_dashboard,patient_dashboard,book_Appointment,myAppointments,rescheduleappointment,deleteappointment,doctorslist,doctor_appointments
from .views import cancel_appointment,reschedule_doctorappointment,attend_appointment,medical_record,doctor_medical_records,generate_bill,view_bill,patientbills
from .views import patientmedicalhistory,pending_doctor_approvals,approve_doctor,reject_doctor,manage_doctors,delete_doctor,manage_patients,view_medical_records
from .views import admin_appointments,cancelappointment_admin,reschedule_appointment,admin_billing, mark_bill_as_paid, delete_bill
urlpatterns = [
    path('register/doctor/', doctor_registration, name='doctor_register'),
    path('register/patient/', patient_registration, name='patient_register'),
    path('register/',register,name='register'),
    path('', rolepage , name='rolepage'),
    path('login/', CustomLoginView.as_view(), name='login'),  
    path('logout/', auth_views.LogoutView.as_view(next_page = 'rolepage'), name='logout'),
    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    path('appointment/book', book_Appointment, name='book_appoinment'),
    path('appointment/scheduled',myAppointments, name='myappointments' ),
    path('appointment/reschedule/<int:appointment_id>/',rescheduleappointment, name='reschedule_appointment'),
    path('appointment/delete/<int:appointment_id>/', deleteappointment, name='delete_appointment'),
    path('appointment/doctorslist/',doctorslist,name='doctorslist'),
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('appointment/cancel/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('appointment/doreschedule/<int:appointment_id>/', reschedule_doctorappointment, name='reschedule_doappointment'),
    path('appointment/attend/<int:appointment_id>/', attend_appointment, name='attend_appointment'),
    path('medical-record/<int:appointment_id>/', medical_record, name='medical_record'),
    path('doctor/medical-records/', doctor_medical_records, name='doctor_medical_records'),
    path("generate-bill/<int:appointment_id>/", generate_bill, name="generate_bill"),
    path("bill/<int:bill_id>/", view_bill, name="view_bill"),
    path('bills/patients', patientbills,name='patientbills'),
    path('patient/medicalhistory', patientmedicalhistory, name="patientmedicalhistory"),
    path('staff/pending_doctors',pending_doctor_approvals,name='pending_doctors'),
    path('staff/approve_doctor/<int:doctor_id>/', approve_doctor, name='approve_doctor'),
    path('staff/reject-doctor/<int:doctor_id>/', reject_doctor, name='reject_doctor'),
    path('staff/manage-doctors/', manage_doctors, name='manage_doctors'),
    path('staff/delete-doctor/<int:doctor_id>/', delete_doctor, name='delete_doctor'),
    path('staff/manage-patients/', manage_patients, name='manage_patients'),
    path('staff/patient-records/<int:patient_id>/', view_medical_records, name='view_medical_records'),
    path('staff/appointments/', admin_appointments, name='admin_appointments'),
    path('staff/appointment/cancel/<int:appointment_id>/', cancelappointment_admin, name='admin_cancel_appointment'),
    path('staff/appointment/reschedule/<int:appointment_id>/', reschedule_appointment, name='admin_reschedule_appointment'),
    path('staff/billing/', admin_billing, name='admin_billing'),
    path('staff/billing/mark-paid/<int:bill_id>/', mark_bill_as_paid, name='mark_bill_as_paid'),
    path('staff/billing/delete/<int:bill_id>/', delete_bill, name='delete_bill'),






]