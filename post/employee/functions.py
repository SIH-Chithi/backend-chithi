
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta , datetime
import threading
import vonage
import pytz
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError
import jwt
from django.conf import settings
import requests
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.http import JsonResponse

