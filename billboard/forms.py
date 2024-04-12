from django import forms


class ImportBillboardForm(forms.Form):
    file = forms.FileField(label='فایل')


    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass