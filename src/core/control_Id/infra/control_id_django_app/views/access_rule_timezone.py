from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.access_rule_timezone import AccessRuleTimeZone
from ..serializers.access_rule_timezone import AccessRuleTimeZoneSerializer
from ..sync_mixins.access_rule_timezone import AccessRuleTimeZoneSyncMixin
from ..models.access_rule import AccessRule
from ..models.timezone import TimeZone

class AccessRuleTimeZoneViewSet(AccessRuleTimeZoneSyncMixin, viewsets.ModelViewSet):
    queryset = AccessRuleTimeZone.objects.all()
    serializer_class = AccessRuleTimeZoneSerializer
    filterset_fields = ['access_rule_id', 'time_zone_id']
    search_fields = ['access_rule_id', 'time_zone_id']
    ordering_fields = ['access_rule_id', 'time_zone_id']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Criar na catraca
        response = self.create_objects("access_rule_time_zones", [{
            "access_rule_id": instance.access_rule_id_id,
            "time_zone_id": instance.time_zone_id_id
        }])

        if response.status_code != status.HTTP_201_CREATED:
            instance.delete()  # Reverte se falhar na catraca
            return response

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Atualizar na catraca
        response = self.update_objects(
            "access_rule_time_zones",
            {
                "access_rule_id": instance.access_rule_id_id,
                "time_zone_id": instance.time_zone_id_id
            },
            {"access_rule_time_zones": {"access_rule_id": instance.access_rule_id_id, "time_zone_id": instance.time_zone_id_id}}
        )

        if response.status_code != status.HTTP_200_OK:
            return response

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Deletar na catraca
        response = self.destroy_objects(
            "access_rule_time_zones",
            {"access_rule_time_zones": {"access_rule_id": instance.access_rule_id_id, "time_zone_id": instance.time_zone_id_id}}
        )

        if response.status_code != status.HTTP_204_NO_CONTENT:
            return response

        # Deletar no banco local
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
