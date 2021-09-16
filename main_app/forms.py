from django.forms import ModelForm
from .models import Feeding
from django.urls import reverse
class FeedingForm(ModelForm):
    class Meta:
        model=Feeding
        fields=["date","meal"]
          
    def get_absolute_url(self):
        return reverse('detail', kwargs={'cat_id': self.id})    