from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import User
from .serializers import UserSerializer
from src.core.__seedwork__.infra import ControlIDSyncMixin
from src.core.control_Id.infra.control_id_django_app.models.device import Device

class UserViewSet(ControlIDSyncMixin, viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = ['id', 'name', 'registration', 'user_type_id']
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'registration', 'user_type_id']
    ordering = ['id']
    depth = 1

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Primeiro salvamos o usuário no banco
            instance = serializer.save()
            
            # Pega todas as catracas ativas
            devices = Device.objects.filter(is_active=True)
            
            # Para cada catraca ativa
            for device in devices:
                self.set_device(device)
                
                # Criar na catraca
                response = self.create_objects("users", [{
                    "id": instance.id,
                    "name": instance.name,
                    "registration": instance.registration,
                    "user_type_id": instance.user_type_id
                }])
                
                if response.status_code != status.HTTP_201_CREATED:
                    # Se falhar em alguma catraca, reverte tudo
                    instance.delete()
                    return Response({
                        "error": f"Erro ao criar usuário na catraca {device.name}",
                        "details": response.data
                    }, status=response.status_code)
                
                # Adiciona a relação com a catraca
                device.users.add(instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Atualiza o usuário no banco
            instance = serializer.save()
            
            # Atualiza em todas as catracas ativas
            devices = Device.objects.filter(is_active=True)
            
            for device in devices:
                self.set_device(device)
                response = self.update_objects(
                    "users",
                    [{
                        "id": instance.id,
                        "name": instance.name,
                        "registration": instance.registration,
                        "user_type_id": instance.user_type_id
                    }],
                    {"users": {"id": instance.id}}
                )
                if response.status_code != status.HTTP_200_OK:
                    return Response({
                        "error": f"Erro ao atualizar usuário na catraca {device.name}",
                        "details": response.data
                    }, status=response.status_code)
                
                # Atualiza a relação com a catraca
                device.users.add(instance)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        with transaction.atomic():
            # Remove o usuário de todas as catracas ativas
            devices = Device.objects.filter(is_active=True)
            
            for device in devices:
                self.set_device(device)
                response = self.destroy_objects(
                    "users",
                    {"users": {"id": instance.id}}
                )
                if response.status_code != status.HTTP_204_NO_CONTENT:
                    return Response({
                        "error": f"Erro ao deletar usuário da catraca {device.name}",
                        "details": response.data
                    }, status=response.status_code)
            
            # Se removeu de todas as catracas, remove do banco
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def sync(self, request):
        """Sincroniza usuários de todas as catracas ativas"""
        try:
            with transaction.atomic():
                # Sincroniza com todas as catracas ativas
                devices = Device.objects.filter(is_active=True)
                
                for device in devices:
                    self.set_device(device)
                    catraca_objects = self.load_objects(
                        "users",
                        fields=["id", "name", "registration", "user_type_id"],
                        order_by=["id"]
                    )
                    
                    # Atualiza/cria usuários no banco
                    for data in catraca_objects:
                        user, created = User.objects.update_or_create(
                            id=data["id"],
                            defaults={
                                "name": data["name"],
                                "registration": data.get("registration", ""),
                                "user_type_id": data.get("user_type_id")
                            }
                        )
                        # Adiciona a relação com a catraca
                        user.devices.add(device)

                return Response({
                    "success": True,
                    "message": f"Sincronizados usuários de {len(devices)} catraca(s)"
                })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        