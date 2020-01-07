from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#DB 연결
from django.db import connection
cursor = connection.cursor()

# django에서 제공하는 User 모델
from django.contrib.auth.models import User
from django.contrib.auth import login as login1
from django.contrib.auth import logout as logout1
from django.contrib.auth import authenticate as auth1
from .models import Table2
from django.db.models import Sum, Max, Min, Count, Avg


def exam_result(request):
    # SELECT SUM(math) FROM MEMBER_TABLE2 WHERE CLASS_ROOM=101
    list = Table2.objects.aggregate(Sum('math'))

    # SELECT NO, NAME FROM MEMBER_TABLE2
    list = Table2.objects.all().values('no','name')

    # SELECT * FROM MEMBER_TABLE2 ORDER BY name ASC
    list = Table2.objects.all().order_by('name')
    #list = Table2.objects.raw("SELECT * FROM MEMBER_TABLE2 ORDER BY name ASC")

    # 반별 국어, 영어, 수학 합계
    # SELECT SUM(kor) AS kor, SUM(eng) AS eng, SUM(math) AS math FROM MEMBER_TABLE2 GROUP BY CLASSROOM
    list = Table2.objects.values('classroom').annotate(kor=Sum('kor'),eng=Sum('eng'),math=Sum('math'))   
    
    return render(request, 'member/exam_result.html',{"list":list})





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


def exam_select(request):
    if request.method=="GET":
        no= request.GET.get('no',0)
        #SELECT SUM(math) FROM MEMBER_TABLE2
        rows = Table2.objects.aggregate(Sum('math'))
        
        # SELECT NO, NAME FROM MEMBER_TABLE2
        rows = Table2.objects.all().values(['no','name'])
        
        # SELECT * FROM MEMBER_TABLE2 ORDER BY name ASC
        rows = Table2.objects.all().order_by('name')
        #rows = Table2.objects.raw(SELECT * FROM MEMBER_TABLE2 ORDER BY name ASC)

        # 반별 국어, 영어, 수학 합계
        # SELECT SUM(kor) AS kor, SUM(eng) AS eng, SUM(math) AS math FROM MEMBER_TABLE2 GROUP BY CLASSROOM
        list = Table2.objects.values('classroom').annotate(kor=Sum('kor'),eng=Sum('eng'),math=Sum('math'))   
 

        return render(request, "member/exam_select.html", {"rows": rows})
    





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

def list(request):
    # ID 기준으로 오름차순
    sql = "SELECT * FROM MEMBER ORDER BY ID ASC"
    cursor.execute(sql)
    data = cursor.fetchall();
    print(type(data))
    print(data)
    
    # list.html을 표시하기 전에
    # list 변수에 data값을, title변수에 "회원목록" 문자를
    # template에서는 최대한 상수 쓰지말라. view단에서 넘기는 것이 최선의 방법 !!
    return render(request, 'member/list.html', {"list":data, "title": "회원목록"})

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