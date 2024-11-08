from django.db import models
class Subscribe(models.Model):
    email=models.EmailField()
    status=models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
