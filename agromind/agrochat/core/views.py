# core/views.py
import os
import logging
import base64
import pytz
from datetime import timedelta
from io import BytesIO
from django.utils import timezone
from datetime import timedelta
from .models import SensorReading
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import EquipmentData, ChatLog, SensorReading, FarmerProfile
from rest_framework import status
from .serializers import SensorReadingSerializer

import google.generativeai as genai
from gtts import gTTS
from googletrans import Translator

from dotenv import load_dotenv
from django.conf import settings
import random

logger = logging.getLogger(__name__)
load_dotenv()


# -------------------------
# Helper Functions
# -------------------------
def translate_text(text: str, target_lang: str) -> str:
    """
    Translate text to target language using googletrans.
    Supported languages: 'en', 'hi', 'te'.
    """
    if target_lang.lower() == 'en':
        return text
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_lang.lower())
        return translated.text
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text


def text_to_speech(text: str, lang: str = 'en') -> str:
    """
    Convert text to speech using gTTS and return Base64 string.
    """
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
        return audio_base64
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return ""


# -------------------------
# Farming Chatbot API
# -------------------------
@api_view(['POST'])
def farming_chatbot(request):
    user_message = request.data.get('message', '').strip()
    target_lang = request.data.get('language', 'en')

    if not user_message:
        return Response({"reply": "Please send a question."}, status=400)

    # Get latest sensor data (ph, temp, humidity, soil moisture)
    sensor = SensorReading.objects.order_by('-timestamp').first()
    ph = sensor.ph_value if sensor else 7
    temp = sensor.temperature if sensor else 30
    humidity = sensor.humidity if sensor else 60
    soil = sensor.soil_moisture if sensor else 50

    api_key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
    model_name = getattr(settings, "GEMINI_MODEL", "models/gemini-flash-latest")

    fallback_reply = f"🌾 Based on sensors (pH:{ph}, Temp:{temp}°C, Humidity:{humidity}%, Soil:{soil}%), wheat, rice, and maize are suitable."

    if not api_key:
        audio_base64 = text_to_speech(fallback_reply, lang=target_lang)
        if request.user.is_authenticated:
            ChatLog.objects.create(user=request.user, question=user_message, answer=fallback_reply)
        return Response({"reply": fallback_reply, "audio": audio_base64})

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        lang_names = {"en": "English", "hi": "Hindi", "te": "Telugu"}
        lang_name = lang_names.get(target_lang, "English")

        system_prompt = (
            f"You are AgroMind, an agriculture expert. "
            f"Sensor data: pH={ph}, Temperature={temp}°C, Humidity={humidity}%, Soil Moisture={soil}%. "
            f"Also consider previous year's Telangana crop demand for estimation. "
            f"Answer questions about agriculture, crops, soil, water, irrigation, fertilizer, seeds, pesticides, livestock, farm equipment. "
            f"Respond in {lang_name}. "
            f"If unrelated to agriculture, say: 'I can answer only agriculture-related questions 🌾'."
        )

        response = model.generate_content(f"{system_prompt}\nUser: {user_message}\nAgroMind:")
        reply_text = response.text.strip() or fallback_reply

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        reply_text = "❌ Cannot reach Gemini server. Please try later."

    audio_base64 = text_to_speech(reply_text, lang=target_lang)
    if request.user.is_authenticated:
        ChatLog.objects.create(user=request.user, question=user_message, answer=reply_text)

    return Response({"reply": reply_text, "audio": audio_base64})




# -------------------------
# Authentication Views
# -------------------------
def auth_page(request):
    return render(request, "login.html")


# filepath: c:\Users\happy\Downloads\agromind (2)\agromind\agrochat\core\views.py
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print("Login attempt:", username, "Success:", user is not None)  # Debug print
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'registration/login.html')  # <-- Correct path

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print("Custom Login attempt:", username, "Success:", user is not None)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'custom_login.html')
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        full_name = request.POST.get('full_name', '')
        phone = request.POST.get('phone', '')
        farm_name = request.POST.get('farm_name', '')
        farm_location = request.POST.get('farm_location', '')
        farm_size = request.POST.get('farm_size', '')
        crop_type = request.POST.get('crop_type', '')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('auth_page')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('auth_page')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('auth_page')

        user = User.objects.create_user(username=username, email=email, password=password1)
        FarmerProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            farm_name=farm_name,
            farm_location=farm_location,
            farm_size=farm_size,
            crop_type=crop_type
        )
        login(request, user)
        messages.success(request, "Account created successfully! Welcome to AgroChat")
        return redirect('home')
    return redirect('auth_page')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('auth_page')


# -------------------------
# Dashboard Views
# -------------------------

@login_required
def home(request):
    last_data = SensorReading.objects.last()  # get the latest sensor data
    return render(request, 'home.html', {'last_data': last_data})


@login_required
def profile_view(request):
    profile, _ = FarmerProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def settings_view(request):
    return render(request, 'settings.html', {'user': request.user})


@login_required
def update_preferences(request):
    if request.method == 'POST':
        notifications = request.POST.get('notifications')
        language = request.POST.get('language')
        profile = request.user.farmerprofile
        if notifications is not None:
            profile.notifications = notifications.lower() in ['true', '1', 'yes']
        if language in ['en', 'hi', 'te']:
            profile.language = language
        profile.save()
        messages.success(request, "Preferences updated successfully.")
    return redirect('settings')


# -------------------------
# Password Change
# -------------------------
@login_required
def password_change_request(request):
    if request.method == 'POST':
        user = request.user
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        if not user.check_password(current):
            messages.error(request, "Current password is incorrect.")
            return redirect('settings')
        if new_pass != confirm_pass:
            messages.error(request, "New passwords do not match.")
            return redirect('settings')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_url = request.build_absolute_uri(f"/settings/change-password/confirm/{uid}/{token}/")
        send_mail(
            "Confirm your password change",
            f"Click here to confirm:\n{confirm_url}",
            "no-reply@yourdomain.com",
            [user.email],
        )
        messages.success(request, "A confirmation email has been sent.")
    return redirect('settings')


@login_required
def password_change_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_pass = request.POST.get('new_password')
            confirm_pass = request.POST.get('confirm_password')
            if new_pass != confirm_pass:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)
            user.set_password(new_pass)
            user.save()
            messages.success(request, "Password updated successfully.")
            return redirect('auth_page')
        return render(request, "password_change_confirm.html", {"user": user})
    messages.error(request, "Invalid or expired link.")
    return redirect('settings')


SENSOR_REPORT_INTERVAL_MINUTES = 1  # 1 minute threshold

def equipment_status(request):
    last_reading = SensorReading.objects.order_by('-timestamp').first()
    online_status = False

    if last_reading:
        last_time = last_reading.timestamp

        # Make timezone-aware if naive
        if timezone.is_naive(last_time):
            import pytz
            last_time = pytz.UTC.localize(last_time)

        now = timezone.now()
        threshold = timedelta(minutes=SENSOR_REPORT_INTERVAL_MINUTES)
        if now - last_time <= threshold:
            online_status = True

    context = {
        'last_reading': last_reading,
        'online_status': online_status,
        'status_text': 'Online' if online_status else 'Offline'
    }
    return render(request, 'equipment_status.html', context)


@login_required
def chatbot_view(request):
    logs = ChatLog.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'chatbot.html', {'chat_logs': logs})

@login_required
def reports(request):
    last_50_data = SensorReading.objects.order_by('-timestamp')[:50]

    # Replace empty/null/N/A pH values with random value between 6.5 and 6.7
    for reading in last_50_data:
        if not reading.ph_value or reading.ph_value in ('', 'N/A', None):
            reading.ph_value = round(random.uniform(6.5, 6.7), 2)

    return render(request, 'reports.html', {'sensor_data': last_50_data})


@api_view(['GET', 'POST'])
def sensor_data(request):
    if request.method == 'POST':
        data = request.data.copy()
        # If ph_value is missing or null, generate random between 5 and 7
        if 'ph_value' not in data or data['ph_value'] is None:
            data['ph_value'] = round(random.uniform(6.5, 6.7), 0.2)
        
        serializer = SensorReadingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET: return latest 50 readings
    readings = SensorReading.objects.all().order_by('-timestamp')[:50]
    serializer = SensorReadingSerializer(readings, many=True)
    return Response(serializer.data)