import json
import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login as user_login
from django.contrib.auth import logout as user_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.utils import IntegrityError

from .forms import LoginForm
from .models import Room, RoomBooking


# Create your views here.
@login_required(login_url='/users/login/')
def index(request):
    choices = RoomBooking.time_choices
    return render(request, 'index.html', {'choices': choices})


@login_required(login_url='/users/login/')
def get_booking_info(request):
    """
    预定会议室
    :param request:
    :return:
    """
    result = {'status': 'success', 'message': '', 'data': ''}
    current_date = datetime.datetime.now().date()
    # 获取前端传过来的日期数据
    fetch_date = request.GET.get('date') if request.GET.get('date') else request.POST.get('date')
    fetch_date = datetime.datetime.strptime(fetch_date, '%Y-%m-%d').date()
    # 再次确认前端传递过来的日期数据是否正确
    if fetch_date < current_date:
        result['message'] = '查询时间不能为以前时间'
        return HttpResponse(json.dumps(result))
    if request.method == 'GET':
        try:
            # 通过主动连表操作  将三张表连接起来 减少查询消耗
            # booking_list = RoomBooking.objects.filter(booking_date=fetch_date).select_related('user',
            #                                                                                     'room').order_by(
            #     'booking_time')

            # 通过三次独立查询获取三表数据  减少连表的耗时
            booking_list = RoomBooking.objects.filter(booking_date=fetch_date).prefetch_related('user',
                                                                                                'room').order_by(
                'booking_time')
            # 获取预定信息，因为字典更便于查询
            booking_dict = {}
            for item in booking_list:
                if item.room_id not in booking_dict:
                    booking_dict[item.room_id] = {item.booking_time: {'name': item.user.username, 'id': item.user_id}}
                else:
                    booking_dict[item.room_id][item.booking_time] = {'name': item.user.username, 'id': item.user_id}
            # 查找到所有的预定消息
            room_list = Room.objects.all()
            booking_info = []
            for room in room_list:
                temp = [{'text': room.name, 'attr': {'rid': room.id}, 'class': ''}]
                for choice in RoomBooking.time_choices:
                    v = {'text': '', 'attr': {'time-id': choice[0], 'room-id': room.id}, 'class': ''}
                    if room.id in booking_dict and choice[0] in booking_dict[room.id]:
                        # 已经被预定
                        v['text'] = booking_dict[room.id][choice[0]]['name']
                        if booking_dict[room.id][choice[0]]['id'] != request.user.id:
                            v['attr']['disable'] = 'true'
                            v['class'] = 'danger'
                        else:
                            v['class'] = 'success'
                    temp.append(v)
                booking_info.append(temp)
            result['data'] = booking_info
        except Exception as e:
            result['message'] = '预定失败' + str(e)

        return HttpResponse(json.dumps(result))

    elif request.method == 'POST':
        try:
            booking_info = json.loads(request.POST.get('data'))

            for room_id, time_id_list in booking_info['del'].items():
                if room_id not in booking_info['add']:
                    continue
                for time_id in list(time_id_list):
                    if time_id in booking_info['add'][room_id]:
                        booking_info['add'][room_id].remove(time_id)
                        booking_info['del'][room_id].remove(time_id)

            # 删除
            remove_booking = Q()
            for room_id, time_id_list in booking_info['del'].items():
                for time_id in time_id_list:
                    temp = Q()
                    temp.connector = 'AND'
                    temp.children.append(('user_id', request.user.id,))
                    temp.children.append(('booking_date', fetch_date,))
                    temp.children.append(('room_id', room_id,))
                    temp.children.append(('booking_time', time_id,))
                    remove_booking.add(temp, 'OR')
            if remove_booking:
                RoomBooking.objects.filter(remove_booking).delete()
            # 添加
            add_obj_list = []
            for room_id, time_id_list in booking_info['add'].items():
                for time_id in time_id_list:
                    obj = RoomBooking(
                        user_id=request.user.id,
                        room_id=room_id,
                        booking_time=time_id,
                        booking_date=fetch_date
                    )
                    add_obj_list.append(obj)
            RoomBooking.objects.bulk_create(add_obj_list)
        except IntegrityError as e:
            # 已经被预定
            result['message'] = '会议室已经被预定'
        except Exception as e:
            # 预定失败
            result['message'] = '预定失败' + str(e)
        return HttpResponse(json.dumps(result))

    return HttpResponse('error')


def login(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                user_login(request, user)
                return redirect('/index/')
        else:
            return render(request, 'index.html', {'form': form})
    return HttpResponse('error')


@login_required(login_url='/users/login/')
def logout(request):
    """
    用户登出
    :param request:
    :return:
    """
    user_logout(request)
    return redirect('/users/login/')
