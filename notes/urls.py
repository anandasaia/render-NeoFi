from django.urls import path
from .views import create_note, get_note, update_note, delete_note, share_note, get_note_history

urlpatterns = [
    path('create', create_note, name='create-note'),
    path('share', share_note, name='share-note'),
    path('<int:id>', get_note, name='get-note'),
    path('<int:id>/update', update_note, name='update-note'),
    path('<int:id>/delete', delete_note, name='delete-note'),
    path('version-history/<int:id>', get_note_history, name='note-history'),
]
