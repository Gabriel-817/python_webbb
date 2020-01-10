#파일명 : seriealizers.py => 직렬화

from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('no', 'name', 'price', 'regdate')
        # 아이템이라는 오브젝트가 들어오면 필드로 내용을 바꾸겠다는 의미
# class Member ........