from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db.models.fields.files import ImageFieldFile

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ImageFieldFile):
            return obj.url  # Convert the ImageFieldFile to its URL representation
        return super().default(obj)
