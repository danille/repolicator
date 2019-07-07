from django import forms


class ReplicationForm(forms.Form):
    repository_name = forms.CharField(
        label='Repository where to replicate',
        max_length=100,
    )
