from forums.models import Message
from forums.serializers import MessageSerializer

from .viewsets import CreateListRetrieveViewset




class MessageAPI(CreateListRetrieveViewset):

    queryset = Message.objects.all()
    serializer_class = MessageSerializer 
    

