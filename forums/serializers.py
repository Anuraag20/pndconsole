from rest_framework import serializers

from .models import Message, Forum
from django.contrib.contenttypes.models import ContentType



class ForumField(serializers.Field):

    
    def to_internal_value(self, data):
        
        if issubclass(data.__class__, Forum):
            return data

        elif not isinstance(data, dict):
            raise serializers.ValidationError('Field should be a \'dict\'')
                
        content_type = ContentType.objects.get(id = data.pop('content_type'))
        ForumClass = content_type.model_class()
        
        forum = ForumClass.objects.get_or_create(
                unique_identifier = data['unique_identifier'],
                defaults = {'name': data['name']}
                )[0]

        return forum

    def to_representation(self, value):
        return value.name

class MessageSerializer(serializers.ModelSerializer):
    
    forum = ForumField(required = True)
    
    
    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    class Meta:
        model = Message
        fields = ('content', 'sent_at', 'forum', 'db_added_at')