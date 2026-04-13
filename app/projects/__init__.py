from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Project, Milestone, HandRaise
from app.forms import ProjectForm, MilestoneForm, CommentForm, HandRaiseForm

projects = Blueprint('projects', __name__)


@projects.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            stage=form.stage.data,
            support_needed=form.support_needed.data,
            user_id=current_user.id,
        )
        if form.stage.data == 'done':
            project.is_completed = True
        db.session.add(project)
        db.session.commit()
        flash('Project created!', 'success')
        return redirect(url_for('projects.project_detail', project_id=project.id))
    return render_template('projects/form.html', form=form, title='New Project', legend='New Project')


@projects.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    comment_form = CommentForm()
    hand_raise_form = HandRaiseForm()
    milestone_form = MilestoneForm()
    from app.models import Milestone, Comment
    milestones = project.milestones.order_by(Milestone.created_at.asc()).all()
    comments = project.comments.order_by(Comment.created_at.asc()).all()
    hand_raises = project.hand_raises.order_by(HandRaise.created_at.desc()).all()
    user_raised = False
    if current_user.is_authenticated:
        user_raised = HandRaise.query.filter_by(
            user_id=current_user.id, project_id=project_id).first() is not None
    return render_template(
        'projects/detail.html',
        project=project,
        comment_form=comment_form,
        hand_raise_form=hand_raise_form,
        milestone_form=milestone_form,
        milestones=milestones,
        comments=comments,
        hand_raises=hand_raises,
        user_raised=user_raised,
        title=project.title,
    )


@projects.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.stage = form.stage.data
        project.support_needed = form.support_needed.data
        project.updated_at = datetime.utcnow()
        project.is_completed = (form.stage.data == 'done')
        db.session.commit()
        flash('Project updated!', 'success')
        return redirect(url_for('projects.project_detail', project_id=project.id))
    return render_template('projects/form.html', form=form, title='Edit Project',
                           legend='Edit Project')


@projects.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('main.feed'))


@projects.route('/project/<int:project_id>/milestone', methods=['POST'])
@login_required
def add_milestone(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    form = MilestoneForm()
    if form.validate_on_submit():
        milestone = Milestone(
            title=form.title.data,
            description=form.description.data,
            project_id=project_id,
        )
        db.session.add(milestone)
        db.session.commit()
        flash('Milestone added!', 'success')
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects.route('/milestone/<int:milestone_id>/toggle', methods=['POST'])
@login_required
def toggle_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.project.user_id != current_user.id:
        abort(403)
    milestone.achieved = not milestone.achieved
    db.session.commit()
    return redirect(url_for('projects.project_detail', project_id=milestone.project_id))


@projects.route('/project/<int:project_id>/comment', methods=['POST'])
@login_required
def add_comment(project_id):
    from app.models import Comment
    project = Project.query.get_or_404(project_id)
    form = CommentForm()
    if form.validate_on_submit():
        from app.models import Comment
        comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            project_id=project_id,
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
    return redirect(url_for('projects.project_detail', project_id=project_id))


@projects.route('/project/<int:project_id>/raise-hand', methods=['POST'])
@login_required
def raise_hand(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id == current_user.id:
        flash("You can't raise a hand on your own project.", 'warning')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    existing = HandRaise.query.filter_by(
        user_id=current_user.id, project_id=project_id).first()
    if existing:
        flash('You have already raised your hand for this project.', 'info')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    form = HandRaiseForm()
    if form.validate_on_submit():
        hand_raise = HandRaise(
            message=form.message.data,
            user_id=current_user.id,
            project_id=project_id,
        )
        db.session.add(hand_raise)
        db.session.commit()
        flash('Hand raised! The developer will be notified.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project_id))
