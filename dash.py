from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
    
    def __repr__(self):
        return '<User %r>' % self.name

class Task(db.Model):
    id_task = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False, unique=True)
    creator = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    subtasks = db.relationship('SubTask', backref='task', lazy=True)

    def __repr__(self):
        return '<Task %r>' % self.title

class SubTask(db.Model):
    id_subtask = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True) 
    status = db.Column(db.Integer, default=1) 
    id_task = db.Column(db.Integer, db.ForeignKey('task.id_task'), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Subtask %r>' % self.title

assignee = db.Table('assignee',
    db.Column('id_user', db.Integer, db.ForeignKey('user.id_user')),
    db.Column('id_task', db.Integer, db.ForeignKey('task.id_task'))
)

id_task = 0
@app.route('/', methods=['POST', 'GET'])
def add_task():
    id_user = 1
    global id_task
    tasks = Task.query.filter_by(creator=id_user).order_by(Task.date_created).all()
    subTasks = SubTask.query.filter_by(id_task=id_task).all()
    
     
    if request.method == 'POST':
        # Selection de la tache à afficher
        if 'taskList' in request.form:
            id_task = request.form['taskList']
            subTasks = SubTask.query.filter_by(id_task=id_task).all()
            task = Task.query.get(id_task)
            return render_template('test.html', task=task, subTasks=subTasks, tasks=tasks, id_task=id_task)
        # Ajout d'une tache        
        elif 'add_task' in request.form:
            try:
                task_content = request.form['add_task']
                new_task = Task(title=task_content, creator=id_user)
                db.session.add(new_task)
                db.session.commit()
                task = Task.query.order_by(Task.date_created.desc()).first()
                id_task = task.id_task
                tasks = Task.query.filter_by(creator=id_user).order_by(Task.date_created).all()
                return render_template('test.html', task=task, tasks=tasks, id_task=id_task)
            except:
                db.session.rollback()
                task = Task.query.get(id_task)
                subTasks = SubTask.query.filter_by(id_task=id_task).all()
                tasks = Task.query.filter_by(creator=id_user).order_by(Task.date_created).all()
                errorMessage = 'Cette tache existe déjà'
                return render_template('test.html', task=task, subTasks=subTasks, tasks=tasks, id_task=id_task, errorMessage=errorMessage)
        # Suppression d'une tache
        elif 'remove_task' in request.form:     
            Task.query.filter_by(id_task=id_task).delete()
            SubTask.query.filter_by(id_task=id_task).delete()
            db.session.commit()
            id_task=0
            return redirect('/')
        # Ajout d'une sous tache
        elif 'add_subTask' in request.form:
            subTask_content = request.form['add_subTask']
            new_subTask = SubTask(title=subTask_content, id_task=id_task)
            db.session.add(new_subTask)
            db.session.commit()
            task = Task.query.get(id_task)
            subTasks = SubTask.query.filter_by(id_task=id_task).all()
            return render_template('test.html', task=task, subTasks=subTasks, tasks=tasks, id_task=id_task)
        # Suppression de sous tache
        elif 'remove_subTask' in request.form:
            id_subTask = request.form['id_subTask']
            SubTask.query.filter_by(id_subtask=id_subTask).delete()
            db.session.commit()
            task = Task.query.get(id_task)
            subTasks = SubTask.query.filter_by(id_task=id_task).all()
            return render_template('test.html', task=task, subTasks=subTasks, tasks=tasks, id_task=id_task)
        # Modification de sous tache
        elif 'edit_subTask' in request.form:
            subTask_content = request.form['edit_subTask']
            id_subTask = request.form['id_subTask']
            SubTask.query.filter_by(id_subtask=id_subTask).update({SubTask.title: subTask_content})
            db.session.commit()
            task = Task.query.get(id_task)
            subTasks = SubTask.query.filter_by(id_task=id_task).all()
            return render_template('test.html', task=task, subTasks=subTasks, tasks=tasks, id_task=id_task)

    else: 
        task = Task.query.get(id_task)
        return render_template('test.html', task=task, subTasks=subTasks, tasks=tasks, id_task=id_task)


#         task_content = request.form['task_content']
#         new_task = Task(title=task_content, creator=1)

#         try:
#             db.session.add(new_task)
#             db.session.commit()
#             return redirect('/')
#         except:
#             return 'Il y a un soucis'
#     else:
#         tasks = Task.query.order_by(Task.date_created).all()
#         return render_template('test.html', tasks=tasks)

# def add_subTask():
#     if request.method == 'POST':
#         subTask_content = request.form['subtask_content']
#         new_subTask = SubTask(title=subTask_content, id_task=1)

#         try:
#             db.session.add(new_subTask)
#             db.session.commit()
#             return redirect('/')
#         except:
#             return 'Il y a un soucis'
#     else:
#         subTasks = SubTask.query.filter(id_task=1).all()
#         return render_template('test.html', subTasks=subTasks)
