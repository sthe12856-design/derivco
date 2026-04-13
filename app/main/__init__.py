from flask import Blueprint, render_template
from app.models import Project, User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    recent = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    total_devs = User.query.count()
    total_projects = Project.query.count()
    completed = Project.query.filter_by(is_completed=True).count()
    return render_template('main/index.html', recent=recent,
                           total_devs=total_devs, total_projects=total_projects,
                           completed=completed, title='MzansiBuilds')


@main.route('/feed')
def feed():
    page = 1
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return render_template('main/feed.html', projects=projects, title='Live Feed')


@main.route('/celebration-wall')
def celebration_wall():
    completed_projects = Project.query.filter_by(is_completed=True)\
        .order_by(Project.updated_at.desc()).all()
    return render_template('main/celebration.html',
                           projects=completed_projects, title='Celebration Wall')
