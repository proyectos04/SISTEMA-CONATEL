from rest_framework import serializers
from ..models.ubicacion_models import  *



class RegionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'region']
    

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id', 'estado']

class MunicipioSerializer(serializers.ModelSerializer):
    estado = serializers.CharField(source='estadoid.estado', read_only=True)
    
    class Meta:
        model = Municipio
        fields = ['id', 'municipio', 'estadoid', 'estado']

class ParroquiaSerializer(serializers.ModelSerializer):
    municipio = serializers.CharField(source='municipioid.municipio', read_only=True)
    
    class Meta:
        model = Parroquia
        fields = ['id', 'parroquia', 'municipioid', 'municipio']
