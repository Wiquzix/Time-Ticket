import os
#from pdf import pdf
from flask import flash, Flask, render_template, redirect
from flask import session as ses
# from api import app_api
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from sqlalchemy.sql.expression import func
from flask_restful import Api, Resource, reqparse, request
from instance.DataBase import Users, Events, db, Types, Tickets, Discounts, Event_users


app = Flask(__name__)
app.secret_key = 'a3951e50d6e90d5f173e522e3e623731'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)  # инициализация
# app.register_blueprint(app_api)
manager = LoginManager(app)


@manager.user_loader
def load_user(id):
    return db.session.get(Users, id)


@app.route('/')
def index():
    events = Events.query.all()[:3]
    if len(events) != 0:
        return render_template("index.html", events=events)
    return render_template("index.html", events=0)
#Events.query.order_by(Events.start_datetime).limit(6))


@app.route('/events')
def events():
    return render_template("events.html", events=Events.query.all())
    
#создать profile_edit

@app.route('/profile/<id>')
def profile(id):
    events = []
    if current_user.is_authenticated:
        balance = Users.query.filter(Users.id == current_user.id).first().balance
        user = Users.query.filter(Users.id == id).first()
        events_user = Event_users.query.filter(Event_users.id_user == user.id).all()
        org = Events.query.filter(Events.organizer == user.id).all()
        for i in events_user:
            print(i)
            # print(Events.query.filter(Events.id == i.id_event).first().id, Events.query.filter(Events.id == i.id_event).first().name)
            events.append(Events.query.filter(Events.id == i.id_event).first())
        events.append(0)
        org.append(0)

        if len(org)>len(events):
            while len(org)>len(events):
                events.append(0)
        if len(org)<len(events):
            while len(org)<len(events):
                org.append(0)
        # print(events)
        # (org[0].name, org[0].id)
        # if len(org) == 0:
        #     if len(events) == 0:
        #         return render_template("profile.html", user=user, events=[None], organizer=[None])
        #     return render_template("profile.html", user=user, events=events, organizer=[None])
        # if len(events) == 0:
        #     if len(org) == 0:
        #         return render_template("profile.html", user=user, events=[None], organizer=[None])
        #     return render_template("profile.html", user=user, events=events[None], organizer=org)

        # a = RequestEvent.event_user(user.id)
        return render_template("profile.html", user=user, events=events, organizer=org, balance=balance)


@app.route('/event/<int:id>')
def event(id):
    a=[]
    balance = Users.query.filter(Users.id == current_user.id).first().balance
    event = Events.query.filter(Events.id == id).first()
    type = Types.query.filter_by(id_event=id).all()
    organizer = Users.query.filter(Users.id == event.organizer).first()
    event_users = Event_users.query.filter_by(id_event=id).all()
    for i in event_users:
        a.append(Users.query.filter_by(id=i.id).first())
    return render_template("event.html", event=event, organizer=organizer,type=type, balance=balance, event_users=a)


@app.route('/events/<int:id>/del')
def event_del(id):
    event = Events.query.filter(Events.id == id).first()
    db.session.delete(event)
    db.session.commit()
    return redirect("/")


@app.route('/add_event/<int:id>', methods=["POST", "GET"])
def add_event(id):
    event = Events(name="", adress="", description="", start_datetime="",
                   end_datetime="", organizer=current_user.id)
    types = [Types(type="", price="", id_event=""),#, ticket_count=""
             Types(type="", price="", id_event=""),#, ticket_count=""
             Types(type="", price="", id_event="")]#, ticket_count="")]
    if request.method == "GET":
        if id != 0:
            event = Events.query.filter(Events.id == id).first()
            types = Types.query.all()
        return render_template("add_event.html", event=event, types=types)

    if current_user.is_authenticated:
        name = request.form.get('name')
        description = request.form.get('about')
        organizer = current_user.id
        adress = request.form.get('adress')
        file = request.files['file']

        time1 = request.form.get('time1')
        time2 = request.form.get('time2')
        forma = '%M:%H %d.%m.%Y'

        type1 = request.form.get("type")
        price = request.form.get("price")
        #count = request.form.get("count")
        type2 = request.form.get("type2")
        price2 = request.form.get("price2")
        #count2 = request.form.get("count2")
        type3 = request.form.get("type3")
        price3 = request.form.get("price3")
        #count3 = request.form.get("count3")
        try:
            date_time_obj1 = datetime.datetime.strptime(time1, forma)
            date_time_obj2 = datetime.datetime.strptime(time2, forma)
        except ValueError:
            flash("Неверный формат даты")
            return render_template("add_event.html", event=event, types=types)

        try:
            if id != 0:
                event = Events.query.filter(Events.id == id).first()
                if event is not None:
                    event.name, event.description, event.organizer = name, description, organizer
                    event.adress, event.start_datetime, event.end_datetime = adress, time1, time2
                    event.filename = file.filename

                    db.session.commit()
                    return redirect("/")
                else:
                    flash("Нет такого событи")
                    return render_template("add_event.html", event=event, types=types)
            else:
                db.session.add(
                    Events(name=name, adress=adress, description=description, start_datetime=date_time_obj1,
                           end_datetime=date_time_obj2, filename=file.filename, organizer=organizer))
                event_id = db.session.query(func.max(Events.id)).one()[0]
                file.save(os.path.join('static/img', file.filename))
                db.session.add(Types(id_event=event_id, type=type1, price=price))
                db.session.add(Types(id_event=event_id, type=type2, price=price2))
                db.session.add(Types(id_event=event_id, type=type3, price=price3))#, ticket_count=count3))
                db.session.commit()
                return redirect("/")
        except:
            db.session.rollback()
            flash("Ошибка при добавлении данных")
            return render_template("add_event.html", event=event, types=types)
    flash("Зарегистрируйся для добавления мероприятей")
    return render_template("sign-up.html")


@app.route('/plus')
def plus():
    idlog = ses.get("idlog")
    col = Events.query.filter(Events.idlog == idlog).first()
    if idlog is not None:
        if col.ticket_types_count < 17:
            col.ticket_types_count = col.ticket_types_count + 1
            db.session.commit()
            return redirect("/add_event2")
        else:
            flash("Типов билетов не может быть больше 20")
            return render_template("add_event2.html", col=col.ticket_types_count)
    else:
        flash("Некоректный запрос")
        return render_template("index.html")


@app.route('/minus')
def minus():
    idlog = ses.get("idlog")
    col = Events.query.filter(Events.idlog == idlog).first()
    if idlog is not None:
        if col.ticket_types_count > 0:
            col.ticket_types_count = col.ticket_types_count - 1
            db.session.commit()
            return redirect("/add_event2")
        else:
            flash("Кол-во доп билетов не может быть меньше 0")
            return render_template("add_event2.html", col=col.ticket_types_count)
    else:
        flash("Некоректный запрос")
        return render_template("index.html")


@app.route('/sign-up', methods=["POST", "GET"])
def sign_up():
    if request.method == "GET":
        return render_template("sign-up.html")

    mail = request.form.get('mail')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    description = request.form.get('description')
    fio = request.form.get('F') + " " + request.form.get('I') + " " + request.form.get('O')
    age = request.form.get('age')
    user = Users.query.filter_by(mail=mail).first()

    if len(mail) > 50:
        flash("Слишком длинный логин")
        return render_template("sign-up.html")

    if user is not None:
        flash('Имя пользователя занято!')
        return render_template("sign-up.html")

    if password != password2:
        flash("Пароли не совпадают!")
        return render_template("sign-up.html")

    try:
        hash_pwd = generate_password_hash(password)
        new_user = Users(mail=mail, password=hash_pwd, fio=fio, description=description, age=age)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    except:
        flash("Возникла ошибка при регистрации")
        return render_template("sign-up.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        mail = request.form.get('mail')
        password = request.form.get('password')
        user = Users.query.filter_by(mail=mail).first()

        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash('Неверный логин или пароль')
        else:
            flash('Такого пользователя не существует')

    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/admin_status_p', methods=["POST", "GET"])
def admin_status_p():
    if request.method == "POST":
        email = request.form.get('username_give')
        user = Users.query.filter_by(mail=email).first()
        if current_user.admin == 2:
            try:
                if 0 <= user.admin <= 2:
                    if user.admin == 2:
                        flash("Пользователь уже является главный администратором")
                        return render_template("admin_status_p.html")
                    elif user.admin == 1:
                        user.admin = 2
                        db.session.commit()
                        flash("Вы сделали пользователя админом второго уровня")
                        return render_template("admin_status_p.html")
                    elif user.admin == 0:
                        user.admin = 1
                        db.session.commit()
                        flash("Вы сделали пользователя админом первого уровня")
                        return render_template("admin_status_p.html")
                else:
                    flash("Error1")
                    return render_template("admin_status_p.html")
            except:
                flash("Error2")
                return render_template("admin_status_p.html")
        return redirect("/")
    return render_template("admin_status_p.html")


@app.route('/admin_status_m', methods=["POST", "GET"])
def admin_status_m():
    if request.method == "POST":
        email = request.form.get('username_give')
        user = Users.query.filter_by(mail=email).first()

        if current_user.admin == 2:
            try:
                if 0 <= user.admin <= 2:
                    if user.admin == 2:
                        user.admin = 1
                        db.session.commit()
                        flash("Вы сделали пользователя админом первого уровня")
                        return render_template("admin_status_m.html")
                    elif user.admin == 1:
                        user.admin = 0
                        db.session.commit()
                        flash("Вы забрали статус админа у данного пользователя")
                        return render_template("admin_status_m.html")
                    elif user.admin == 0:
                        flash("пользователь уже не имеет статус администратора")
                        return render_template("admin_status_m.html")
                else:
                    flash("Error1")
                    return render_template("admin_status_m.html")
            except:
                flash("Error2")
                return render_template("admin_status_m.html")
        return redirect("/")
    return render_template("admin_status_m.html")


@app.route('/buy_ticket/<int:id>/<int:type>', methods=['POST','GET']) #баланс
def buy1(id, type):
    print(current_user.balance)
    event = Events.query.filter_by(id=id).first()
    tickets = Tickets.query.filter_by(id_user=current_user.id).all()
    balance = Users.query.filter(Users.id==current_user.id).first().balance
    user = current_user
    if request.method == "GET":
        if event is not None:
            if len(tickets) != 0:
                for i in tickets:
                    if i.id_event == id:
                        flash('вы уже купили билет на данное мероприятие')
                        print(current_user.balance)
                        return render_template("buy.html")
                else:
                    a = Types.query.filter(Types.id==type).first().price
                    if balance>=a:
                        user.balance -= a
                        db.session.add(Tickets(id_user=current_user.id, type=type, id_event=id))
                        db.session.add(Event_users(id_event=id,id_user=current_user.id))
                        db.session.commit()
                        flash(f'вы успешно купили билет ваш баланс: {current_user.balance}')
                        print(current_user.balance)
                # else:
                #     flash('вы уже купили билет на данное мероприятие')
                #     return render_template("buy.html")
            else:
                a = Types.query.filter(Types.id == type).first().price
                if balance >= a:
                    user.balance -= a
                    db.session.add(Tickets(id_user=current_user.id, type=type, id_event=id))
                    db.session.add(Event_users(id_event=id, id_user=current_user.id))
                    db.session.commit()
                    flash(f'вы успешно купили билет ваш баланс: {current_user.balance}')
                    print(current_user.balance)

        else:
            flash('этого мероприятия не существует')
            #n = pdf(t)
            return render_template("buy.html")
    return render_template("buy.html")

@app.route('/buy_ticket/<int:id>',methods=['POST', 'GET'])
def buy(id):
    user = current_user
    event = Events.query.filter(Events.id==id).first()
    type = Types.query.filter(Types.id_event==event.id).all()
    if request.method == "POST":
        # ticket1 = request.form.get("ticket1")
        # db.session.add(Tickets(id_user=user.id, type=ticket1))
        # try:
        #     ticket2 = request.form.get("ticket2")
        #     ticket3 = request.form.get("ticket3")
        #     db.session.add(Tickets(id_user=user.id, type=ticket2))
        #     db.session.add(Tickets(id_user=user.id, type=ticket3))
        # except:
        #     try:
        #         ticket2 = request.form.get("ticket2")
        #         db.session.add(Tickets(id_user=user.id, type=ticket2))
        #     except:
        #         ticket3 = request.form.get("ticket3")
        #         db.session.add(Tickets(id_user=user.id, type=ticket3))
        if request.form.get("submit") is not None:
            ticket = request.form.get("type1")

            try:
                ticket = request.form.get("type1")
            except:
                try:
                    ticket = request.form.get("type2")
                except:
                    try:
                        ticket = request.form.get("type3")
                    except:
                        flash('выберите тип билета')
                        return redirect(f'/buy_ticket/{id}')

        db.session.add(Tickets(id_user=user.id,type=ticket))
        db.session.add(Event_users(id_event=event.id, id_user=user.id))
        db.session.commit()
        #t = Tickets(id_user=id, id_event=user.Events.id, type=type, on=True)  # данные из формы должны быть    db.session.add(t)
        #n = pdf(t)
        return render_template("buy.html",type=type,user=user,event=event)
    elif request.method == "GET":
        return render_template("buy.html",type=type,user=user,event=event)



@app.route('/chess_event')
def chess_event():
    return render_template("chess_event.html")


@app.route('/buy_tickets', methods=["POST", "GET"])
def buy_tickets():
    user = Users.query.filter(Users.id == current_user.id).first()
    if request.method == "POST":
        if user.balance >= 200 or user.balance >= 100 or user.balance >= 50:
            if 50 <= user.balance < 100:
                user.balance -= 50
                db.session.commit()
                flash("Вы купили билет за 50")
                return redirect("/")
            elif 100 <= user.balance < 200:
                user.balance -= 100
                db.session.commit()
                flash("Вы купили билет за 100")
                return redirect("/")
            elif 200 <= user.balance:
                user.balance -= 200
                db.session.commit()
                flash("Вы купили билет за 200")
                return redirect("/")
            elif 50 > user.balance:
                flash("Недастаточно средств")
                return redirect("/")
            else:
                flash("Error1")
                return redirect("/")
        else:
            flash("Недастаточно средств")
            return redirect("/")
    return render_template("buy_tickets.html",user=user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="localhost", port=3000)
