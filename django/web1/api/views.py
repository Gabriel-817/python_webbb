from django.shortcuts import render
from django.http import HttpResponse

#insert1
from .models import Item

#select1
from .serializers import ItemSerializer
from rest_framework.renderers import JSONRenderer
import json


# 127.0.0.1:8000/api/insert1
def insert1(request):
    for i in range(1,31,1):
        obj = Item()
        obj.name = '신발'+str(i)
        obj.price = 100000+i
        obj.save()

    return HttpResponse("insert1")

# 127.0.0.1:8000/api/select1?key=abc
# {"id":"a"} => 물품 1개
# def select1(request):
#     key = request.GET.get("key","")
#     if key == 'abc':
#         obj = Item.objects.get(no=1)
#         serializer = ItemSerializer(obj)
#         data = JSONRenderer().render(serializer.data)
#         return HttpResponse(data)
#     else:
#         data = json.dumps({"ret":'key error'})
#         return HttpResponse(data)

def select1(request):
    key = request.GET.get("key","")
    no = request.GET.get("no","1")
    #DB에서 확인

    data = json.dumps({"ret":'key error'})
    if key == 'abc':
        obj = Item.objects.get(no=no)
        serializer = ItemSerializer(obj)
        print(serializer.data)
        data = JSONRenderer().render(serializer.data)
        
    return HttpResponse(data)

# [{"id":"a"} {"id":"b"}] => 물품 여러개
def select2(request):
    obj = Item.objects.all()
    serializer = ItemSerializer(obj, many=True)
    data = JSONRenderer().render(serializer.data)
    return HttpResponse(data)

def select_ex(request):
    key = request.GET.get("key","")
    num = int(request.GET.get("num","1"))
    search = request.GET.get("search","")
    #DB에서 확인

    data = json.dumps({"ret":'key error'})
    if key == 'abc':
        obj = Item.objects.filter(name__contains=search)[:num]
        # obj = Item.objects.all()
        serializer = ItemSerializer(obj, many=True)
        print(serializer.data)
        data = JSONRenderer().render(serializer.data)
        
    print(data)
    return HttpResponse(data)