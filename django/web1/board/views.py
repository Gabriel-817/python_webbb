from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
#BLOB 읽기용
from base64 import b64encode # byte배열을 base64로 변경함.

cursor = connection.cursor()

@csrf_exempt
def write(request):
    if request.method=='GET':
        return render(request, 'board/write.html')
    if request.method=='POST':
        tmp =None
        if 'img' in request.FILES:
            img = request.FILES['img']
            tmp = img.read()

        ar = [
            request.POST['title'],
            request.POST['content'],
            request.POST['writer'],
            tmp
            # img.read() # 이미지를 byte[]로 변경
        ]
        # print(ar)

        try:
            sql="""
                INSERT INTO BOARD_TABLE1(TITLE, CONTENT, WRITER, IMG, HIT, REGDATE)
                VALUES(%s, %s, %s, %s, 0, SYSDATE)
            """
            cursor.execute(sql, ar)
        except Exception as e:
            print(e)
        return redirect("/board/list")

@csrf_exempt
def list(request):
    if request.method=='GET':
        request.session['hit'] = 1 # 세션에  hit=1

        sql = """
            SELECT NO, TITLE, WRITER, HIT, TO_CHAR(REGDATE, 'YYYY-MM-DD HH:MI:SS') 
            FROM BOARD_TABLE1
            ORDER BY NO DESC
        """
        cursor.execute(sql)
        data = cursor.fetchall()

        return render(request, 'board/list.html', {"list":data})


# http://127.0.0.1:8000/board/content?no=13     -> 정상 작동
# http://127.0.0.1:8000/board/content           -> 에러 발생, no=0으로 되게 default값을 잡아주는 것이 좋다.
#                                               -> no = request.GET.get('no', 0) -> default 값을 0으로 줘라!
@csrf_exempt
def content(request):
    if request.method=="GET":
        no = request.GET.get('no', 0)
        if no == 0:
            return redirect( "/board/list" )

        # 조회수 1증가 
        #       => 새로고침하면 안늘어나게 해야 함 - 세션을 통해 컨트롤
        if request.session['hit'] == 1:
            sql = """
                UPDATE BOARD_TABLE1 
                SET HIT=HIT+1
                WHERE no=%s
            """
            cursor.execute(sql, [no])
            request.session['hit'] = 0

        # 이전 글 번호
        sqlp = """
            SELECT NVL(max(no),0)
            FROM board_table1 
            where no<%s
        """
        cursor.execute(sqlp, [no])
        prev = cursor.fetchone()
        # 이전 글 없을 때 if로 처리
        # if prev[0] == 0:
        #     prev = (no,)

        # 다음 글 번호
        sqln = """
            SELECT NVL(min(no),0)
            FROM board_table1 
            where no>%s
        """
        cursor.execute(sqln, [no])
        nxt = cursor.fetchone()
        # 다음 글 없을 때 if로 처리
        # if nxt[0] == 0:
        #     nxt = (no,)
 
        # 가져오기
        sql = """
            SELECT NO, TITLE, CONTENT, WRITER, HIT, TO_CHAR(REGDATE, 'YYYY-MM-DD HH:MI:SS'), IMG 
            FROM BOARD_TABLE1
            WHERE NO=%s
        """
        cursor.execute(sql, [no])
        data = cursor.fetchone()
        print(data) 

        if data[6]:
            img = data[6].read() # 바이트 배열을 img에 넣음
            img64 = b64encode(img).decode("utf-8")
        else:
            file = open('./static/img/default.png', 'rb')
            img = file.read()
            img64 = b64encode(img).decode("utf-8")

        return render(request, 'board/content.html', {"one":data, "image":img64, "prev":prev[0], "next":nxt[0]})
        
@csrf_exempt
def edit(request):
    if request.method=="GET":
        no = request.GET.get('no', 0)
        if no == 0:
            return redirect("/board/list")

        sql = """
            SELECT NO, TITLE, CONTENT, WRITER
            FROM BOARD_TABLE1
            WHERE no=%s
        """
        cursor.execute(sql, [no])
        data = cursor.fetchone()

        return render(request, 'board/edit.html', {"one":data})
    if request.method=="POST":
        return redirect("/board/list")

@csrf_exempt
def delete(request):
    if request.method=="GET":
        pass