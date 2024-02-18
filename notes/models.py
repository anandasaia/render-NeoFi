from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Note(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Share(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='shared_notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_with')
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('note', 'user')

    def __str__(self):
        return f"{self.note.title} shared with {self.user.username}"


class NoteHistory(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='history')
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"History of {self.note.title} at {self.edited_at}"
