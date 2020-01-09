from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

cursor = connection.cursor()

#django에서 제공하는 User 모델
from django.contrib.auth.models import User
from django.contrib.auth import login as login1
from django.contrib.auth import logout as logout1
from django.contrib.auth import authenticate as auth1

from .models import Table2
from django.db.models import Sum, Max, Min, Count, Avg

import pandas as pd # conda install pandas

import matplotlib.pyplot as plt
import io # byte로 변환
import base64 # byte를 base64로 변경
from matplotlib import font_manager, rc #한글 폰트 적용



def graph1(request):
   # SELECT SUM("kor") FROM MEMBER_TABLE2
    sum_kor = Table2.objects.aggregate(Sum("kor"))
    print(sum_kor) #"kor__sum"

    # SELECT SUM("kor") AS sum1 FROM MEMBER_TABLE2
    sum_kor = Table2.objects.aggregate(sum1=Sum("kor"))
    print(sum_kor) #"sum1"

    # SELECT SUM("kor") FROM MEMBER_TABLE2 
    # WHERE CLASSROOM=102
    sum_kor = Table2.objects.filter(classroom='102') \
        .aggregate(sum1=Sum("kor"))
    print(sum_kor)

    # SELECT SUM("kor") FROM MEMBER_TABLE2
    # WHERE KOR > 10
    # > gt, >= gte,  < lt,   <= lte
    sum_kor = Table2.objects.filter(kor__gt=10) \
        .aggregate(sum1=Sum("kor"))
    print(sum_kor)

    # 반별 합계
    # SELECT SUM("kor") sum1, SUM("eng") sum2, 
    #       SUM("math") sum3
    # FROM MEMBER_TABLE2
    # GROUP BY CLASSROOM
    sum_kor = Table2.objects.values("classroom") \
        .annotate(sum1=Sum("kor"), \
            sum2=Sum("eng"),sum3=Sum("math")).order_by("classroom")
    print(sum_kor) 
    print(sum_kor.query) #SQL문 확인  

    df = pd.DataFrame(sum_kor)
    print(df)
    print("-"*30,end="\n")
    df = df.set_index("classroom")
    print(df)
    df.plot(kind="bar")   



    # x = ['kor', 'eng', 'math']
    # y = [ 45,       3,      4]
    # # 폰트 읽기
    # font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/batang.ttc").get_name()
    # #폰트 적용
    # rc('font', family=font_name)
    
    # plt.bar(x,y)
    # plt.title("AGES & PERSON")
    # plt.xlabel("나이")
    # plt.ylabel("숫자")

    # plt.show() #표시
    plt.draw() # 안보이게 그림을 캡쳐
    img = io.BytesIO() # img에 byte배열로 보관
    plt.savefig(img, format='png') # png파일 포맷으로 저장
    img_url = base64.b64encode(img.getvalue()).decode()

    plt.close()  # 그래프 종료
    return render(request, 'member/graph1.html', {"graph1":'data:;base64,{}'.format(img_url)})
    # <img src="{{graph1}}" />  <= graph.html에서




def dataframe(request):
    # SELECT * FROM MEMBER_TABLE2
    rows = Table2.objects.all()

    # 1. QuerySet -> list로 변경 -> 위에 rows에 리스트로 변경
    # SELECT NO,NAME,KOR FROM MEMBER_TABLE2
    rows = list(Table2.objects.all().values("no", "name", "kor"))[0:10]
    print(rows)


    print(type(rows)) 

    # 2. list -> dataframe으로 변경
    df = pd.DataFrame(rows)
    print(df)

    # 3. dataframe -> list로 변경
    rows1 = df.values.toilst()

    return render(request, 'member/dataframe.html', {"df_table":df.to_html(), "list":rows})




def js_index(request):
    return render(request, 'member/js_index.html')

def js_chart(request):
    str = "100, 200, 300, 400, 200, 100"
    return render(request, 'member/js_chart.html',  {"str":str})

def exam_select(request):
    txt = request.GET.get("txt","")
    page = int(request.GET.get("page", 1))
    # 1 => 0, 10
    # 2 => 10, 20
    # 3 => 20, 30

    if txt == "":
        # SELECT * FROM MEMBER_TABLE2
        list1 = Table2.objects.all()[page*10-10:page*10]
    
        # SELECT COUNT(*) FROM MEMBER_TABLE2
        cnt = Table2.objects.all().count()
        tot = (cnt-1)//10+1
        # 10 => 1
        # 13 => 2
        # 20 => 2
        # 31 => 4
    else: # 검색어가 있는 경우
        # SELECT * FROM WHERE name LIKE '%가%'
        list1 = Table2.objects.filter(name__contains=txt)[page*10-10:page*10]
        
        #SELECT COUNT(*) FROM MT2 WHERE name LIKE '%가%'
        cnt = Table2.objects.filter(name__contains=txt).count()
        tot = (cnt-1)//10+1
    return render(request, 'member/exam_select.html',
        {"list1":list1, "pages":range(1,tot+1,1)})




def exam_result(request):
    # SELECT SUM(math) FROM MEMBER_TABLE2 WHERE CLASS_ROOM=101
    list1 = Table2.objects.aggregate(Sum('math'))

    # SELECT NO, NAME FROM MEMBER_TABLE2
    list1 = Table2.objects.all().values('no','name')

    # SELECT * FROM MEMBER_TABLE2 ORDER BY name ASC
    list1 = Table2.objects.all().order_by('name')
    #list1 = Table2.objects.raw("SELECT * FROM MEMBER_TABLE2 ORDER BY name ASC")

    # 반별 국어, 영어, 수학 합계
    # SELECT SUM(kor) AS kor, SUM(eng) AS eng, SUM(math) AS math FROM MEMBER_TABLE2 GROUP BY CLASSROOM
    list1 = Table2.objects.values('classroom').annotate(kor=Sum('kor'),eng=Sum('eng'),math=Sum('math'))   
    
    return render(request, 'member/exam_result.html',{"list1":list1})





def exam_delete(request):
    if request.method == 'GET':
        n = request.GET.get("no",0)
        
        #SELECT * FROM BOARD_TABLE2 WHRER NO=%s
        row = Table2.objects.get(no=n)
        # DELETE FROM BOARD_TABLE2 WHERE NO=%s
        row.delete() #삭제

        return redirect("/member/exam_select")


def exam_update(request):
    if request.method == 'GET':
        n = request.GET.get("no",0)
        row = Table2.objects.get(no=n)
        return render(request, 'member/exam_update.html',{"one":row})

    elif request.method == 'POST':
        n = request.POST['no']

        obj = Table2.objects.get(no=n) #obj객체 생성
        obj.name = request.POST['name'] # 변수에 값
        obj.kor = request.POST['kor']
        obj.eng = request.POST['eng']
        obj.math = request.POST['math']
        obj.classroom = request.POST['classroom']
        obj.save() #저장하기 수행
        # UPDATE BOARD_TABLE2 SET
        # NAME=%s, KOR=%s, ENG=%s, MATH=%s
        # WHRER NO = %s

        return redirect("/member/exam_select")


def exam_insert(request):
    if request.method=="GET":
        return render(request, "member/exam_insert.html")
    elif request.method == 'POST':
        na = request.POST['name']
        ko = request.POST['kor']
        en = request.POST['eng']
        ma = request.POST['math']
        cl = request.POST['classroom']

        obj = Table2()
        obj.name = na
        obj.kor  = ko
        obj.eng  = en
        obj.math  = ma
        obj.classroom  = cl
        obj.save()

        return redirect("/member/exam_select")






@csrf_exempt
def auth_join(request):
    if request.method=="GET":
        return render(request, "member/auth_join.html")
    elif request.method == 'POST':
        id = request.POST['username']
        pw = request.POST['password']
        na = request.POST['first_name']
        em = request.POST['email']
        
        #회원가입
        obj = User.objects.create_user(
            username=id,
            password=pw,
            first_name=na,
            email=em)
        obj.save()
        
        return redirect("/member/auth_index")

@csrf_exempt
def auth_index(request):
    if request.method=="GET":
        return render(request, "member/auth_index.html")

@csrf_exempt
def auth_login(request):
    if request.method=="GET":
        return render(request, "member/auth_login.html")
    elif request.method == 'POST':
        id = request.POST['username']
        pw = request.POST['password']

        #DB에 인증
        obj = auth1(request, username=id, password=pw)

        if obj is not None:
            login1(request, obj)  # 세션에 추가
            return redirect("/member/auth_index")
        return redirect("/member/auth_login")


def auth_logout(request):
    if request.method=="GET" or request.method == "POST":
        logout1(request) # 세션 초기화
        return redirect("/member/auth_index")


def auth_edit(request):
    if request.method=="GET":
        if not request.user.is_authenticated:
            return redirect("/member/auth_login")
        obj = User.objects.get(username=request.user)
        return render(request, "member/auth_edit.html", {"obj":obj})
    elif request.method == 'POST':
        id = request.POST['username']
        na = request.POST['first_name']
        em = request.POST['email']

        obj = User.objects.get(username=id)
        obj.first_name = na
        obj.email = em
        obj.save()
        return redirect("/member/auth_index")


def auth_pw(request):
    if request.method=="GET":
        if not request.user.is_authenticated:
            return redirect("/member/auth_login")

        return render(request, "member/auth_pw.html")
    elif request.method == 'POST':
        pw = request.POST['pw'] #기존 암호
        pw1 = request.POST['pw1'] #바꿀 암호
        obj = auth1(request, username=request.user, password=pw)
        if obj:
            obj.set_password(pw1) #pw1으로 암호변경
            obj.save()
            return redirect("/member/auth_index")

        return redirect("/member/auth_pw")



# Create your views here.
def index(request):
    # return HttpResponse("indexpagesssss")
    return render(request, 'member/index.html')

def list1(request):
    # ID 기준으로 오름차순
    sql = "SELECT * FROM MEMBER ORDER BY ID ASC"
    cursor.execute(sql)
    data = cursor.fetchall();
    print(type(data))
    print(data)
    
    # list.html을 표시하기 전에
    # list 변수에 data값을, title변수에 "회원목록" 문자를
    # template에서는 최대한 상수 쓰지말라. view단에서 넘기는 것이 최선의 방법 !!
    return render(request, 'member/list1.html', {"list1":data, "title": "회원목록"})

@csrf_exempt  # POST로 값을 전달받는 곳은 필수로!!, 보안정책의 하나
def join(request):
    if request.method == 'GET':
        return render(request, 'member/join.html')
    if request.method == 'POST':
        id = request.POST['id']
        na = request.POST['name']
        ag = request.POST['age']
        pw = request.POST['pw']
        
        ar = [id, na, ag, pw]

        # DB에 추가
        # SQLite 버전
        # sql = """
        # INSERT INTO MEMBER(ID,NAME,AGE,PW, JOINDATE) 
        # VALUES (%s, %s, %s, %s, datetime())
        # """

        # Oracle 버전
        sql = """
        INSERT INTO MEMBER(ID,NAME,AGE,PW, JOINDATE) 
        VALUES (%s, %s, %s, %s, SYSDATE)
        """
        cursor.execute(sql,ar)

        print(ar)

        return redirect("/member/index") # 절대경로로 줘라!!, /로 시작해야 한다..

@csrf_exempt
def login(request): 
    if request.method == 'GET':
        return render(request, 'member/login.html')
    if request.method == 'POST':
        ar = [request.POST['id'], request.POST['pw']]
        sql = """
            SELECT ID, NAME 
            FROM MEMBER 
            WHERE ID=%s AND PW=%s
        """

        cursor.execute(sql, ar)
        data = cursor.fetchone() # ID가 기본키이기 때문에 1개만 나오는게 정상
        print(type(data)) # (  ) 1개가 나오고  튜플로 온다.

        # session => 로그인한 데이터를 세이브해놓는다.
        if data:
            request.session['userid'] = data[0]
            request.session['username'] = data[1]
            return redirect('/member/index')

        return redirect("/member/index")

def logout(request):
    if request.method=="GET" or request.method == 'POST':
        del request.session['userid']
        del request.session['username']
        return redirect('/member/index')

@csrf_exempt
def edit(request):
    if request.method == 'GET':
        ar = [request.session['userid']]
        sql = """
            SELECT * 
            FROM MEMBER 
            WHERE ID=%s
        """
        cursor.execute(sql, ar)
        data = cursor.fetchone()
        return render(request, 'member/edit.html', {"one":data})

    if request.method == 'POST':
       pass     
        

@csrf_exempt
def delete(request):
    if request.method=="GET" or request.method == 'POST':
        ar = [request.session['userid']]
        sql ="""
            DELETE FROM MEMBER WHERE ID=%s
        """
        cursor.execute(sql, ar)
        return redirect("/member/logout")


@csrf_exempt
def join1(request):
    if request.method == 'GET':
        return render(request, 'member/join1.html')
    if request.method == 'POST':
        id = request.POST['id']
        name = request.POST['name']
        pw = request.POST['pw']
        email = request.POST['email']
        tel = request.POST['tel']
        img = request.POST['img']

        ar = [id, name, pw, email, tel, img]

        
        sql = """
        INSERT INTO MEMBER1(ID, NAME, PW, EMAIL, TEL, IMG, JOINDATE) 
        VALUES (%s, %s, %s, %s, %s, %s, SYSDATE)
        """
        cursor.execute(sql,ar)

        print(ar)

        return redirect("/member/index") # 절대경로로 줘라!!, /로 시작해야 한다..