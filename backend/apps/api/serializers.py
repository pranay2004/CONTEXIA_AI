from rest_framework import serializers
from apps.ingest.models import UploadedFile, GeneratedContent
from apps.trends.models import TrendArticle


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file_type', 'original_filename', 'url', 'extracted_text', 
                  'word_count', 'detected_topic', 'uploaded_at', 'processed_at']
        read_only_fields = ['id', 'extracted_text', 'word_count', 'detected_topic', 
                           'uploaded_at', 'processed_at']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    url = serializers.URLField(required=False)
    text = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if not any([data.get('file'), data.get('url'), data.get('text')]):
            raise serializers.ValidationError(
                "At least one of 'file', 'url', or 'text' must be provided"
            )
        return data


class GeneratedContentSerializer(serializers.ModelSerializer):
    uploaded_file = UploadedFileSerializer(read_only=True)
    
    class Meta:
        model = GeneratedContent
        fields = ['id', 'uploaded_file', 'content_json', 'model_used', 
                  'trends_used', 'created_at']
        read_only_fields = ['id', 'created_at']


class GenerateRequestSerializer(serializers.Serializer):
    uploaded_file_id = serializers.IntegerField()
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['linkedin', 'x_thread', 'threads', 'short_blog', 'long_blog']
    )
    trend_count = serializers.IntegerField(default=10, min_value=1, max_value=20)
    has_images = serializers.BooleanField(default=False, required=False)
    generate_images = serializers.BooleanField(default=False, required=False)


class TrendArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendArticle
        fields = ['id', 'source', 'title', 'url', 'snippet', 'published_date', 
                  'tags', 'scraped_at']
