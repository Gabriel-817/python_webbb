from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from base64 import b64encode
import pandas as pd
# byte배열을 base64로 변경함.

cursor = connection.cursor() #sql문 수행위한 cursor객체

#########################################
from . models import Table2 # models.py 파일의 Table2클래스 불러옴

@csrf_exempt 
def t2_update_all(request):
    if request.method == 'GET':
        n = request.session['no'] # n = [8,3,5]
        print(n) 
        # SELECT * FROM BOARD_TABLE2 WHERE NO=8 OR NO=5 OR NO=3
        # SELECT * FROM BOARD_TABLE2 WHERE NO IN (8,5,3)
        rows = Table2.objects.filter(no__in=n)
        return render(request,'board/t2_update_all.html', {"list":rows})
    elif request.method == 'POST':
        menu = request.POST['menu']
        if menu == "1":
            no = request.POST.getlist("chk[]") # getlist -> 리스트로 가져온다
            request.session["no"] = no
            return redirect("/board/t2_update_all")
        elif menu == "2":
            no = request.POST.getlist("no[]")
            name = request.POST.getlist("name[]")
            kor = request.POST.getlist("kor[]")
            eng = request.POST.getlist("eng[]")
            math = request.POST.getlist("math[]")

            objs = []
            for i in range(0, len(no), 1):
                obj = Table2.objects.get(no=no[i])
                obj.name = name[i]
                obj.kor = kor[i]
                obj.eng = eng[i]
                obj.math = math[i]
                objs.append(obj)
            # 일괄 수정
            Table2.objects.bulk_update(objs, ["name", "kor", "eng", "math"])
            return redirect("/board/t2_list")


@csrf_exempt 
def t2_insert_all(request):
    if request.method == 'GET':
        return render(request,'board/t2_insert_all.html', {"cnt":range(5)})
    elif request.method == 'POST':
        na = request.POST.getlist('name[]')
        ko = request.POST.getlist('kor[]')
        en = request.POST.getlist('eng[]')
        ma = request.POST.getlist('math[]')

        objs = []

        for i in range(0, len(na),1):
            obj = Table2()
            obj.name = na[i]
            obj.kor = ko[i]
            obj.eng = en[i]
            obj.math = ma[i]
            objs.append(obj)

        # 일괄 추가
        Table2.objects.bulk_create(objs)
        return redirect("/board/t2_list")
    


@csrf_exempt 
def t2_update(request):
    if request.method == 'GET':
        n = request.GET.get("no",0)
        # SELECT * FROM BOARD_TABLE2 WHERE NO=%s
        row = Table2.objects.get(no=n)
        return render(request,'board/t2_update.html',{"one":row})
    elif request.method == 'POST':
        n = request.POST['no']

        obj = Table2.objects.get(no=n) # obj객체 가져옴
        obj.name = request.POST['name'] # 변수에 값
        obj.kor  = request.POST['kor']
        obj.eng  = request.POST['eng']
        obj.math = request.POST['math']
        obj.save() # 저장하기 수행
        # UPDATE BOARD_TABLE2 SET
        # NAME=%s, KOR-%s,ENG=%s,MATH=%s
        # WHERE NO = %s

        return redirect("/board/t2_list")


@csrf_exempt 
def t2_delete(request):
    if request.method == 'GET':
        n = request.GET.get("no",0)

        # SQL : SELECT * FROM BOARD_TABLE2 WHERE NO=%s
        row = Table2.objects.get(no=n)
        # DELETE FROM BOARD_TABLE2 WHERE NO=%s
        row.delete() # 삭제

        return redirect("/board/t2_list")


@csrf_exempt 
def t2_list(request):
    if request.method == 'GET':
            rows = Table2.objects.all()
            # SQL : SELECT * FROM BOARD_TABLE2
            print(rows) #결과 확인
            print(type(rows)) # 타입확인
            return render(request,'board/t2_list.html',{"list":rows}) # html표시

@csrf_exempt 
def t2_insert(request):
    if request.method == 'GET':
        return render(request,'board/t2_insert.html')
    elif request.method == 'POST':
        obj = Table2() # obj객체 생성
        obj.name = request.POST['name'] # 변수에 값
        obj.kor  = request.POST['kor']
        obj.eng  = request.POST['eng']
        obj.math = request.POST['math']
        obj.save() # 저장하기 수행

        return redirect("/board/t2_insert")



def dataframe(request):
    if request.method == 'GET':
        df = pd.read_sql(
            """
            SELECT NO, WRITER, HIT, REGDATE
            FROM BOARD_TABLE1
            """, con=connection)
        print(df)
        print(df['NO'])
        return render(request, 'board/dataframe.html', {"df":df.to_html(classes="table")})



@csrf_exempt  
def edit(request):
    if request.method == 'GET':
        no = request.GET.get("no", 0) 
       
        sql = """
            SELECT NO, TITLE, CONTENT  
            FROM  BOARD_TABLE1
            WHERE NO=%s
        """
        cursor.execute(sql, [no])
        data = cursor.fetchone()
        return render(request, 'board/edit.html',
             {"one":data}) 

    elif request.method == 'POST':         
        no = request.POST['no']
        ti = request.POST['title']
        co = request.POST['content']

        arr = [ti, co, no]
        sql = """
            UPDATE BOARD_TABLE1 SET TITLE=%s, 
            CONTENT=%s WHERE NO= %s
        """
        cursor.execute(sql, arr)
        return redirect("/board/content?no="+no)



@csrf_exempt  
def delete(request):
    if request.method == 'GET':
        no = request.GET.get("no",0)

        sql = """
            DELETE FROM BOARD_TABLE1
            WHERE NO = %s
        """
        cursor.execute(sql, [no])

        return redirect("/board/list")

# 127.0.0.1:8000/board/content?no=34
# 127.0.0.1:8000/board/content    ?no=0  => 오류발생
@csrf_exempt  
def content(request):
    if request.method == 'GET':
        no = request.GET.get('no', 0)  
        # request.GET['no']
        if no == 0 :
            return redirect("/board/list") # <a href와 같음

        if request.session['hit'] == 1:
            #조회수 1증가 시킴
            sql = """
                UPDATE BOARD_TABLE1 SET HIT=HIT+1
                WHERE NO = %s    
            """
            cursor.execute(sql, [no])
            request.session['hit'] = 0

        # 이전글 번호 가져오기
        sql = """
            SELECT NVL(MAX(NO), 0)
            FROM BOARD_TABLE1
            WHERE NO < %s
        """
        cursor.execute(sql, [no])
        prev = cursor.fetchone()

        # 다음글 번호 가져오기
        sql = """
            SELECT NVL(MIN(NO), 0)
            FROM BOARD_TABLE1
            WHERE NO > %s
        """
        cursor.execute(sql, [no])
        next = cursor.fetchone()

        # 게시물 내용 가져오기
        sql = """
            SELECT 
                NO, TITLE, CONTENT, WRITER, HIT,  
                TO_CHAR(REGDATE, 'YYYY-MM-DD HH:MI:SS'),
                IMG 
            FROM 
                BOARD_TABLE1
            WHERE
                NO = %s
        """
        cursor.execute(sql, [no])
        data = cursor.fetchone()  # (1,2,3,4,5,6)

        if data[6] : # DB에 BLOB로 있는 경우
            img = data[6].read() # 바이트배열을 img에 넣음
            img64 = b64encode(img).decode("utf-8")
        else : # 없는 경우
            file = open('./static/img/default.png', 'rb')
            img = file.read()
            img64 = b64encode(img).decode("utf-8")

        #print(no)
        return render(request, 'board/content.html',
             {"one":data, "image":img64, 
             "prev":prev[0], "next":next[0]}) 


@csrf_exempt  
def list(request):
    if request.method == 'GET':
        txt = request.GET.get("txt","")
        page = int(request.GET.get("page", 1))
        arr = ['%'+txt+'%', page*10-10+1, page*10]
        print(arr)

        request.session['hit'] = 1  #세션에 hit=1
        sql = """
            SELECT * FROM (
                SELECT
                    NO, TITLE, WRITER, 
                    HIT, TO_CHAR(REGDATE, 'YYYY-MM-DD HH:MI:SS'),
                    ROW_NUMBER() OVER (ORDER BY NO DESC) ROWN
            FROM
                BOARD_TABLE1
            WHERE TITLE LIKE %s    
        )
            WHERE ROWN BETWEEN %s AND %s
        """
        cursor.execute(sql, arr)
        data = cursor.fetchall()
        sql ="""
            SELECT COUNT(*) FROM BOARD_TABLE1 WHERE TITLE LIKE %s
            """
       
        arr1 = ['%'+txt+'%']
        cursor.execute(sql, arr1)
        cnt = cursor.fetchone()[0]
        tot = (cnt-1)//10+1

        
        print( type(data) ) 
        print( data )     
        return render(request, 'board/list.html', {"list":data , "pages":range(1,tot+1,1)})

        # sql = "SELECT COUNT(*) FROM BOARD_TABLE1"
        # cursor.execute(sql)
        # cnt = cursor.fetchone()[0]
        # tot = (cnt-1)//10+1 
        
        # txt  = request.GET.get("txt","")
        # page = int(request.GET.get("page", 1))

        # return render(request, 'board/list.html', {"list":data , "pages":range(1,tot+1,1)})


@csrf_exempt  
def write(request):
    if request.method == 'GET':
        return render(request, 'board/write.html') 
    elif request.method == 'POST':
        tmp = None
        if 'img' in request.FILES:
            img = request.FILES['img']        
            tmp = img.read()

        arr = [ 
            request.POST['title'],
            request.POST['content'],
            request.POST['writer'],
            tmp
        ]

        try :
            # print(arr)
            sql = """
                INSERT INTO BOARD_TABLE1
                (TITLE, CONTENT, WRITER, IMG, HIT, REGDATE)
                VALUES(%s, %s, %s, %s, 234, SYSDATE)
            """
            cursor.execute(sql, arr)
        except Exception as e:
            print(e)    
        
        return redirect("/board/list") # <a href와 같음


