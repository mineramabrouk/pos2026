from django import forms
from django.contrib.auth.models import User, Group

class UserForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('Admin', 'Administrador'),
        ('Salesperson', 'Vendedor'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Rol', required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Dejar en blanco para mantener la contraseña actual (al editar).")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'password']
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # If editing, set initial role based on group
            if self.instance.groups.filter(name='Admin').exists():
                self.fields['role'].initial = 'Admin'
            elif self.instance.groups.filter(name='Salesperson').exists():
                self.fields['role'].initial = 'Salesperson'
            
            # Password is not required when editing
            self.fields['password'].required = False
        else:
            # Password is required when creating
            self.fields['password'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            # Assign role
            role = self.cleaned_data.get('role')
            group = Group.objects.get(name=role)
            user.groups.clear()
            user.groups.add(group)
            # Set is_staff/is_superuser for Admin
            if role == 'Admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False
            user.save()
        return user
