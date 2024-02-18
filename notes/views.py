from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import Note, Share
from .serializers import NoteSerializer
from .models import NoteHistory
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

# Create your views here.


@api_view(['POST'])
def register_user(request):
    try:
        # Extract password from the request
        password = request.data['password']

        # Validate the password
        validate_password(password)

        # Proceed with user creation if the password is valid
        user = User.objects.create(
            username=request.data['username'],
            email=request.data['email'],
            password=make_password(password)
        )
        user.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        # Return a 400 Bad Request response if password validation fails
        return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Handle other exceptions
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    user = authenticate(
        username=request.data['username'], password=request.data['password'])
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_note(request):
    serializer = NoteSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_note(request, id):
    try:
        note = Note.objects.get(id=id, owner=request.user)
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_note(request, id):
    try:
        note = Note.objects.get(id=id, owner=request.user)
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Save history
            NoteHistory.objects.create(
                note=note, content=request.data['content'], edited_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_note(request, id):
    try:
        note = Note.objects.get(id=id, owner=request.user)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# Share Notes

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_note(request):
    note_id = request.data.get('note_id')
    usernames = request.data.get('usernames', [])

    # Check if the note exists and belongs to the authenticated user
    try:
        note = Note.objects.get(id=note_id, owner=request.user)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found or you do not have permission to share it.'}, status=status.HTTP_404_NOT_FOUND)

    # Check that all usernames exist
    users = User.objects.filter(username__in=usernames)
    if len(usernames) != users.count():
        return Response({'error': 'One or more specified users do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    # Share the note with each user
    for user in users:
        Share.objects.get_or_create(note=note, user=user)

    return Response({'message': 'Note shared successfully'}, status=status.HTTP_200_OK)


# Retrieve version history

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_note_history(request, id):
    try:
        note = Note.objects.get(id=id, owner=request.user)
        history = NoteHistory.objects.filter(note=note).order_by('-edited_at')
        history_data = [{"content": h.content, "edited_at": h.edited_at,
                         "edited_by": h.edited_by.username} for h in history]
        return Response(history_data)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
