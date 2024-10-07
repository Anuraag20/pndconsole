from rest_framework import viewsets, mixins


class CreateListRetrieveViewset(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):

    pass 
